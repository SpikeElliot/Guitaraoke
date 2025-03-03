import librosa
from tinytag import TinyTag
import sounddevice as sd
import numpy as np
from pitch_detection import save_pitches


class AudioLoadHandler():
    """
    Handles operations relating to audio loading and playback.

    Attributes
    ----------
    CHANNELS : int
        Specifies whether the audio channel is mono (1) or stereo (2).
    RATE : int
        The sample rate of the audio.
    metronome_data : ndarray
        The loaded metronome sound's audio time series.
    paused : bool
        Whether audio playback is paused or not.
    ended : bool
        Whether audio playback has finished or not.
    stream : OutputStream
        The song's sounddevice output stream for audio playback.
    position : int
        The current position of audio playback in frames.
    title : str
        The title found in metadata from a loaded audio file.
    artist : str
        The artist found in metadata from a loaded audio file.
    guitar_data : ndarray
        The song's separated guitar audio time series.
    no_guitar_data : ndarray
        The song's separated no_guitar audio time series.
    duration : float
        The length of the loaded song in seconds.
    bpm : float
        The estimated tempo of the song found using Librosa's beat_track.
    first_beat : float
        The first detected beat of the song found using Librosa's beat_track.
    guitar_volume : float
        The volume to scale the separated guitar track's amplitudes by (0-1).
    user_score : int
        The performance score derived from comparing the user's recorded pitch
        to the guitar track's.

    Methods
    -------
    load(path)
        Load the frame data from an audio file.
    play()
        Play or unpause audio playback.
    play_metronome()
        Play a metronome sound effect.
    pause()
        Pause audio playback.
    get_pos()
        Return the audio playback's current time position in seconds.
    set_pos(pos):
        Set the audio playback's time position to a new time in seconds.
    """
    def __init__(self, path):
        """
        The constructor for the AudioLoadHandler class.

        Parameters
        ----------
        path : str
            The file path of the audio file to load.
        """
        self.CHANNELS = 1
        self.RATE = 44100
        self.stream = None
        sd.default.samplerate = self.RATE
        self.metronome_data = librosa.load( # Load metronome sound effect
            path="./assets/Perc_MetronomeQuartz_lo.wav",
            sr=self.RATE
        )[0]
        self.load(path)

    def load(self, path):
        """
        Get information from an audio file such as an audio time series,
        metadata, song length, tempo, and the position of the first detected
        beat. This function also initialises attributes related to the song's
        playback status, such as stream and position.

        Parameters
        ----------
        path : str
            The file path of the audio file to load.
        """
        # When loading a new song, immediately terminate audio processing of
        # previous song's stream
        if self.stream:
            self.stream.abort()
        self.path = path
        self.paused = True
        self.ended = True
        self.stream = sd.OutputStream(
            samplerate=self.RATE,
            channels=self.CHANNELS,
            callback=self._callback
        )
        self.position = 0
        self.guitar_volume = 1
        self.user_score = 0

        # Get song metadata
        metadata = TinyTag.get(self.path)
        self.title = metadata.title or "Unknown"
        self.artist = metadata.artist or "Unknown"
        fn_split = metadata.filename.split(".")
        self.filename, self.filetype = fn_split[1].split("/")[-1], fn_split[2]
        self.filedir = fn_split[1].split("/")[-2]

        # TODO Check if song has already been separated. If so, load in guitar
        # and no_guitar files to play concurrently. Otherwise, run the
        # separate_guitar function on the file first.

        # Get audio frames from guitar no_guitar separated tracks
        self.guitar_data = librosa.load(
            f"./separated_tracks/htdemucs_6s/{self.filename}/guitar.wav",
            sr=self.RATE
        )[0]
        self.no_guitar_data = librosa.load(
            f"./separated_tracks/htdemucs_6s/{self.filename}/no_guitar.wav",
            sr=self.RATE
        )[0]
        
        self.duration = len(self.guitar_data) / float(self.RATE) # In seconds

        # Get song tempo and position of first detected beat
        tempo, beats = librosa.beat.beat_track(
            y=self.guitar_data + self.no_guitar_data, # Full mix
            sr=self.RATE
        )
        self.bpm = tempo[0]
        self.first_beat = librosa.frames_to_time(beats[0]) * 1000 # In ms

    # TODO Move all playback logic to a separate audio_playback_handler file

    def play(self):
        """Play or unpause audio playback."""
        if self.ended:
            self.position = 0
        self.paused, self.ended = False, False
        self.stream.start()
    
    def play_metronome(self):
        """Use sounddevice to play a metronome sound effect."""
        sd.play(self.metronome_data)
        sd.wait()

    def _callback(self, outdata, frames, time, status):
        """
        The callback function called by the sounddevice output stream. 
        Generates output audio data.
        """
        new_pos = self.position + frames
        frames_per_buffer = new_pos - self.position

        # Set outdata to zeros if audio should not be playing
        if self.paused or self.ended:
            outdata[:frames_per_buffer] = np.zeros((frames_per_buffer,1))
            return
        
        # Set ended bool to True if end reached
        if new_pos >= len(self.guitar_data):
            new_pos = len(self.guitar_data)
            self.ended = True

        # Set outdata to next frames of loaded audio
        try:
            guitar_batch = self.guitar_data[self.position:new_pos].copy()
            no_guitar_batch = self.no_guitar_data[self.position:new_pos].copy()
            guitar_batch *= self.guitar_volume
            # Sum the amplitudes of the two tracks to get full mix values
            audio_batch = np.add(guitar_batch,no_guitar_batch).reshape(-1,1)
            outdata[:frames_per_buffer] = audio_batch
        # Case: not enough frames from audio data compared to buffer size
        except ValueError as e:
            # Set outdata to zeros
            outdata[:frames_per_buffer] = np.zeros((frames_per_buffer,1))

        self.position = new_pos # Update song position

    def pause(self):
        """Pause audio playback."""
        if not self.paused:
            self.paused = True

    def get_pos(self):
        """Return the audio playback's current time position in seconds."""
        pos = self.position / self.RATE
        return pos
    
    def set_pos(self, pos):
        """Set the audio playback's time position to a new time in seconds."""
        if self.ended:
            self.ended = False
        self.position = int(pos * self.RATE)