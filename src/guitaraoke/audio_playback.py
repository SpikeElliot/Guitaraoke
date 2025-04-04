"""Module providing an AudioPlayback class."""

import os
import librosa
import numpy as np
import sounddevice as sd
from PyQt5.QtCore import QThread, QTimer # pylint: disable=no-name-in-module
from config import CHANNELS, RATE, DTYPE
from guitaraoke.save_pitches import save_pitches
from guitaraoke.separate_guitar import separate_guitar
from guitaraoke.utils import csv_to_pitches_dataframe


class LoadedAudio():
    """
    Contains all necessary data received from an audio file such as its audio
    time series, tempo, and duration.

    Attributes
    ----------
    filename : str
        The song's filename.
    guitar_data, no_guitar_data : ndarray
        The song's separated guitar and no_guitar track audio time series.
    pitches : DataFrame
        The guitar note events predicted from the song in a DataFrame.
    bpm : int
        The song's tempo.
    duration : float
        The length of the song in seconds.

    Parameters
    ----------
    path : str
        The file path of the song to load.
    title : str, default="Unknown"
        The title given to the loaded song.
    artist : str, default="Unknown"
        The artist attributed to the loaded song.
    """
    def __init__(
        self,
        path: str,
        title: str = "Unknown",
        artist: str = "Unknown"
    ) -> None:
        """
        The constructor for the LoadedAudio class.

        Parameters
        ----------
        path : str
            The file path of the audio file to load.
        title : str, default="Unknown"
            The title given to the loaded audio file.
        artist : str, default="Unknown"
            The artist attributed to the loaded audio file.
        """
        self.path = path
        self.title = title
        self.artist = artist

        self.filename = path.split(".")[1].split("/")[-1]
        separated_tracks_dir = f"./assets/separated_tracks/htdemucs_6s/{self.filename}/"
        guitar_pitches_path = ""

        # If song has not been processed, perform guitar separation and pitch detection
        if not os.path.isdir(separated_tracks_dir):
            guitar_track_path, no_guitar_track_path = separate_guitar(self.path)
            guitar_pitches_path = save_pitches(guitar_track_path)[0]
        else: # Otherwise, load tracks and pitches
            guitar_track_path = separated_tracks_dir + "guitar.wav"
            no_guitar_track_path = separated_tracks_dir + "no_guitar.wav"
            guitar_pitches_path = ("./assets/pitch_predictions/songs/"
            f"{self.filename}/guitar_basic_pitch.csv")

        # Convert pitches CSV to a pandas DataFrame
        self.pitches = csv_to_pitches_dataframe(guitar_pitches_path)

        # Get guitar and no_guitar tracks' audio time series
        self.guitar_data = librosa.load(guitar_track_path, sr=RATE)[0]
        self.no_guitar_data = librosa.load(no_guitar_track_path, sr=RATE)[0]

        # Get tempo information
        tempo, beats = librosa.beat.beat_track(
            y=self.guitar_data + self.no_guitar_data, # Full mix
            sr=RATE
        )
        self.bpm = tempo[0]
        self.first_beat = librosa.frames_to_time(beats[0]) * 1000 # In ms
        self.duration = len(self.guitar_data) / float(RATE) # In secs

class AudioPlayback(QThread):
    """
    Provides audio playback methods for a currently-loaded song.

    Attributes
    ----------
    paused, ended : bool
        The current state of audio playback's paused and ended status.
    stream : OutputStream
        The song's sounddevice output stream for audio playback.
    position : int
        The current position of audio playback in frames.
    guitar_volume : float
        The volume to scale the separated guitar track's amplitudes by. Should
        be kept between 0 and 1.
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
    def __init__(self) -> None:
        """The constructor for the AudioPlayback class."""
        super().__init__()

        self.song = None
        self.paused = None
        self.ended = None
        self.position = None
        self.metronome_count = None
        self.count_interval = None
        self.guitar_volume = None
        self.loop_markers = None
        self.looping = None
        self.count_in = None
        self.score_data = None

        # Open output stream
        self.stream = sd.OutputStream(
            samplerate=RATE,
            blocksize=1024,
            channels=CHANNELS,
            callback=self._callback,
            dtype=DTYPE
        )

        # Load metronome sound effect
        metronome_path = "./assets/audio/Perc_MetronomeQuartz_lo.wav"
        self.metronome_data = librosa.load(metronome_path, sr=RATE)[0]

        # Initialise playback attributes
        self._reset_playback()

    def load_song(self, song: LoadedAudio) -> None:
        """Load a song's data to be used for playback."""
        self.song = song
        self._reset_playback()
        self.count_interval = int(1000 / (self.song.bpm / 60))

    def _reset_playback(self):
        """Set all playback attributes to their initial values."""
        self.paused = True
        self.ended = True
        self.position = 0
        self.metronome_count = 0
        self.guitar_volume = 1
        self.loop_markers = [None,None]
        self.looping = False
        self.count_in = True
        self.score_data = self._zero_score_data()

    def _zero_score_data(self):
        """Return a score data dictionary with values set to zero."""
        return {
            "score": 0,
            "notes_hit": 0,
            "total_notes": 0,
            "accuracy": 0
        }

    def run(self) -> None:
        """Play or unpause audio playback."""
        print("\nPlayback started...")
        if self.ended:
            # Reset song pos to start of song
            self.position = 0
            self.score_data = self._zero_score_data()

        self.paused, self.ended = False, False
        self.stream.start()

    def stop(self) -> None:
        """Pause audio playback."""
        print("\nPlayback stopped.")
        if not self.paused:
            self.paused = True
        self.quit()
        self.wait()

    def play_count_in_metronome(self, count_in_timer: QTimer) -> None:
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

        sd.play(self.metronome_data, samplerate=RATE)
        return False # Keep counting

    def get_pos(self) -> None:
        """Return the audio playback's current time position in seconds."""
        pos = self.position / RATE
        return pos

    def set_pos(self, pos: float) -> None:
        """Set the audio playback's time position to a new time in seconds."""
        if self.ended:
            self.ended = False
        self.position = int(pos * RATE)

    def _callback(self, outdata, frames, t, s) -> None: # pylint: disable=unused-argument
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

        # Case: song looping and end of loop is reached in this batch
        if self.in_loop_bounds() and new_pos >= self.loop_markers[1]:
            overflow_frames = new_pos - self.loop_markers[1]
            # Set new pos to correct position after loop
            new_pos = self.loop_markers[0] + overflow_frames

            # Get all frames before right loop marker, and concatenate with
            # all frames needed after loop
            guitar_batch = np.concatenate((
                self.song.guitar_data[self.position:self.loop_markers[1]],
                self.song.guitar_data[self.loop_markers[0]:new_pos]
            ))
            no_guitar_batch = np.concatenate((
                self.song.no_guitar_data[self.position:self.loop_markers[1]],
                self.song.no_guitar_data[self.loop_markers[0]:new_pos]
            ))
        else:
            # Case: no looping and end of song is reached in this batch
            if new_pos >= len(self.song.guitar_data):
                new_pos = len(self.song.guitar_data)
                frames = new_pos - self.position
                self.ended = True

            # No looping, load guitar and no_guitar batches as normal
            guitar_batch = self.song.guitar_data[self.position:new_pos]
            no_guitar_batch = self.song.no_guitar_data[self.position:new_pos]

        # Sum the amplitudes of the two tracks to get full mix values
        audio_batch = (guitar_batch * self.guitar_volume) + no_guitar_batch
        outdata[:frames] = audio_batch.reshape(-1,1)

        self.position = new_pos # Update song position

    def in_loop_bounds(self) -> bool:
        """Check playback is currently looping and within the loop marker bounds."""
        if (self.looping
            and (self.position > self.loop_markers[0]
            and self.position < self.loop_markers[1])):
            return True
        return False
