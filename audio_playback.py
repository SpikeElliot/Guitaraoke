import os
import librosa
import numpy as np
import pandas as pd
import sounddevice as sd
# import matplotlib.pyplot as plt
from PyQt5.QtCore import QThread, QTimer
from pitch_detection import save_pitches
from guitar_separation import separate_guitar


class AudioPlayback(QThread):
    """
    Handles loading of new data from an audio file and provides playback
    methods for the currently-loaded song.

    Parameters
    ----------
    path : str
        The file path of the audio file to load.
    CHANNELS : int
        Specifies whether the audio channel is mono (1) or stereo (2).
    RATE : int
        The sample rate of the audio.
    BLOCK_SIZE : int
        The number of frames per buffer of streamed audio.
    paused, ended : bool
        The current state of audio playback's paused and ended status.
    stream : OutputStream
        The song's sounddevice output stream for audio playback.
    position : int
        The current position of audio playback in frames.
    guitar_data, no_guitar_data : ndarray
        The song's separated guitar and no_guitar track audio time series.
    guitar_volume : float
        The volume to scale the separated guitar track's amplitudes by. Should
        be kept between 0 and 1.
    duration : float
        The length of the loaded song in seconds.
    score_data : dict
        The performance score derived from comparing the user's recorded pitch
        to the guitar track's.

    Methods
    -------
    load(path, title="Unknown", artist="Unknown")
        Load important data from an audio file and prepare it for playback.
    play()
        Play or unpause audio playback.
    play_metronome()
        Initiate a metronome count-in, starting audio playback after the fourth count.
    pause()
        Pause audio playback.
    get_pos()
        Return the audio playback's current time position in seconds.
    set_pos(pos):
        Set the audio playback's time position to a new time in seconds.
    """
    def __init__(self, path, title="Unknown", artist="Unknown"):
        """The constructor for the AudioPlayBack class.

        Parameters
        ----------
        path : str
            The file path of the audio file to load.
        title : str, default="Unknown"
            The title to be given to the loaded audio.
        artist : str, default="Unknown"
            The artist to be attributed to the loaded audio.
        """
        super().__init__()
        self.stream = None
        self.CHANNELS = 1
        self.RATE = 44100
        sd.default.samplerate = self.RATE
        self.DTYPE = "float32" # Datatype used by audio processing libraries
        self.BLOCK_SIZE = 4096 # Increases latency but stops glitching/freezing
        self.load(path, title, artist)
        
    def load(self, path, title="Unknown", artist="Unknown"):
        """
        Load important data from an audio file and prepare it for playback.

        Parameters
        ----------
        path : str
            The file path of the audio file to load.
        title : str, default="Unknown"
            The title given to the loaded audio file.
        artist : str, default="Unknown"
            The artist attributed to the loaded audio file.
        """
        # When loading a new song, immediately terminate audio processing of
        # previous song's stream
        if self.stream:
            self.stream.abort()

        self.path = path
        self.title = title
        self.artist = artist

        # Load metronome sound effect
        metronome_path = "./assets/Perc_MetronomeQuartz_lo.wav"
        self.metronome_data = librosa.load(metronome_path, sr=self.RATE)[0]

        self.filename = path.split(".")[1].split("/")[-1]
        separated_tracks_dir = f"./separated_tracks/htdemucs_6s/{self.filename}/"
        guitar_pitches_path = ""

        # If song has not been processed, perform guitar separation and pitch detection
        if not os.path.isdir(separated_tracks_dir):
            guitar_track_path, no_guitar_track_path = separate_guitar(self.path)
            guitar_pitches_path = save_pitches(guitar_track_path)
        else: # Otherwise, load tracks and pitches
            guitar_track_path = separated_tracks_dir + "guitar.wav"
            no_guitar_track_path = separated_tracks_dir + "no_guitar.wav"
            guitar_pitches_path = f"./pitch_predictions/songs/{self.filename}/guitar_basic_pitch.csv"

        # Convert pitches CSV to a pandas DataFrame
        self.pitches = pd.read_csv(
            guitar_pitches_path, 
            sep=None,
            engine="python",
            index_col=False
        ).drop(columns=["end_time_s", "velocity", "pitch_bend"]).sort_values("start_time_s")
        
        # print(self.pitches.head())
        # plt.scatter(self.pitches.start_time_s, self.pitches.pitch_midi)
        # plt.show()
        
        # Get guitar and no_guitar tracks' audio time series
        self.guitar_data = librosa.load(guitar_track_path, sr=self.RATE)[0]
        self.no_guitar_data = librosa.load(no_guitar_track_path, sr=self.RATE)[0]
        
        # Get tempo information
        tempo, beats = librosa.beat.beat_track(
            y=self.guitar_data + self.no_guitar_data, # Full mix
            sr=self.RATE
        )
        self.bpm = tempo[0]
        self.count_interval = int(1000 / (self.bpm / 60))
        self.first_beat = librosa.frames_to_time(beats[0]) * 1000 # In ms

        # Playback variables
        self.paused, self.ended = True, True
        self.duration = len(self.guitar_data) / float(self.RATE) # In secs
        self.position = 0
        self.metronome_count = 0
        self.guitar_volume = 1

        # Score information
        self.score_data = {
            "score": 0,
            "notes_hit" : 0,
            "total_notes" : 0,
            "accuracy" : 0
        }

        # Open output stream
        self.stream = sd.OutputStream(
            samplerate=self.RATE,
            blocksize=self.BLOCK_SIZE,
            channels=self.CHANNELS,
            callback=self._callback,
            dtype=self.DTYPE
        )

    def run(self):
        """Play or unpause audio playback."""
        print("\nPlayback started...")
        if self.ended:
            self.position = 0
            self.user_score, self.notes_hit, self.total_notes = 0, 0, 0

        self.paused, self.ended = False, False
        self.stream.start()

    def stop(self):
        """Pause audio playback."""
        print("\nPlayback stopped.")
        if not self.paused:
            self.paused = True
        self.quit()
        self.wait()
    
    def play_count_in_metronome(self, count_in_timer : QTimer):
        """
        Use sounddevice to play the count-in metronome sound and increment the
        metronome_count attribute, playing the song after the fourth count.

        Parameters
        ----------
        count_in_timer : QTimer
            The QTimer whose interval will be updated after 4 counts.
        """
        self.metronome_count += 1

        # Stop counting when metronome aligned to song position
        if self.metronome_count > 4:
            count_in_timer.stop()
            self.metronome_count = 0
            return True # Start song

        sd.play(self.metronome_data)
        return False # Keep counting
    
    def get_pos(self):
        """Return the audio playback's current time position in seconds."""
        pos = self.position / self.RATE
        return pos
    
    def set_pos(self, pos):
        """Set the audio playback's time position to a new time in seconds."""
        if self.ended:
            self.ended = False

        self.position = int(pos * self.RATE)
        self.user_score, self.notes_hit, self.total_notes = 0, 0, 0

    def _callback(self, outdata, frames, time, status):
        """
        The callback function called by the sounddevice output stream. 
        Generates output audio data.
        """
        new_pos = self.position + frames

        # Case: audio should not be playing
        if self.paused or self.ended:
            # Set outdata to zeros
            outdata[:frames] = np.zeros((frames,1))
            return
        
        # Case: end of song is reached in this batch
        if new_pos >= len(self.guitar_data):
            new_pos = len(self.guitar_data)
            frames = new_pos - self.position
            self.ended = True

        # Load guitar and no_guitar batches for current position
        guitar_batch = self.guitar_data[self.position:new_pos]
        no_guitar_batch = self.no_guitar_data[self.position:new_pos]

        # Sum the amplitudes of the two tracks to get full mix values
        audio_batch = (guitar_batch * self.guitar_volume) + no_guitar_batch
        outdata[:frames] = audio_batch.reshape(-1,1)

        self.position = new_pos # Update song position