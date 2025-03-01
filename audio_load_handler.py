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
    data : ndarray
        The loaded song's audio time series.
    duration : float
        The length of the loaded song in seconds.
    bpm : float
        The estimated tempo of the song found using Librosa's beat_track.
    first_beat : float
        The first detected beat of the song found using Librosa's beat_track.

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
    def __init__(self, path='./assets/elecguitar_chromatic_scale.wav'):
        """
        The constructor for the AudioLoadHandler class.

        Parameters
        ----------
        path : str
            The file path of the audio file to load.
        """
        self.CHANNELS = 1
        self.RATE = 44100
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
        self.path = path
        self.paused = True
        self.ended = True
        self.stream = None
        self.position = 0

        # Get song metadata
        metadata = TinyTag.get(self.path)
        self.title = metadata.title or "Unknown"
        self.artist = metadata.artist or "Unknown"
        fn_split = metadata.filename.split(".")
        self.filename, self.filetype = fn_split[1].split("/")[-1], fn_split[2]
        self.filedir = fn_split[1].split("/")[-2]
            
        # Get song frames and length
        self.data = librosa.load(path=self.path, sr=self.RATE)[0]
        self.duration = len(self.data) / float(self.RATE) # In seconds

        # Get song tempo and position of first detected beat
        tempo, beats = librosa.beat.beat_track(y=self.data, sr=self.RATE)
        self.bpm = tempo[0]
        self.first_beat = librosa.frames_to_time(beats[0]) * 1000 # In ms

    def play(self):
        """Play or unpause audio playback."""
        if self.ended:
            self.position = 0
        self.paused, self.ended = False, False
        self.stream.start()
    
    def play_metronome(self):
        """Use sounddevice to play a metronome sound effect once."""
        # Open an output stream for song if played for the first time
        if not self.stream:
            self.stream = sd.OutputStream(
                samplerate=self.RATE,
                channels=self.CHANNELS,
                callback=self._callback
            )
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
        if new_pos >= len(self.data):
            new_pos = len(self.data)
            self.ended = True

        # Set outdata to next frames of loaded audio
        try:
            audio_data = self.data[self.position:new_pos].reshape(-1,1)
            outdata[:frames_per_buffer] = audio_data
        # Case: not enough frames from data compared to buffer size
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