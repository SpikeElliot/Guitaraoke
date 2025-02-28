import librosa
from tinytag import TinyTag
import sounddevice as sd
import numpy as np


class AudioLoadHandler():
    """
    Handles operations relating to audio loading and playback.

    Attributes
    ----------
    CHANNELS : int
        Specifies whether the audio channel is mono (1) or stereo (2).
    RATE : int
        The sample rate of the audio.

    Methods
    -------
    load(path)
        Load the frame data from an audio file.
    play()
        Play or unpause audio playback.
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
        self.load(path)

    def load(self, path):
        """
        Get an audio file's frame data, metadata, song length, as well as
        preparing it for playback by loading into the Pygame.mixer.music module.

        Parameters
        ----------
        path : str
            The file path of the audio file to load.
        """
        self.path = path
        self.paused = False
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
        self.frames = librosa.load(path=self.path, sr=self.RATE)[0]
        self.duration = len(self.frames) / float(self.RATE) # In seconds

    def play(self):
        """Play or unpause audio playback."""
        if self.ended:
            self.position = 0

        self.paused, self.ended = False, False

        if not self.stream:
            self.stream = sd.OutputStream(
                samplerate=self.RATE,
                channels=self.CHANNELS,
                callback=self.callback
            )
        self.stream.start()

    def callback(self, outdata, frames, time, status):
        """
        The callback function called by the sounddevice output stream. 
        Generates output audio data.
        """
        new_pos = self.position + frames
        frames_per_buffer = new_pos - self.position

        # Set outdata to zeros if audio should not be playing
        if self.paused or self.ended:
            outdata[:frames_per_buffer] = np.zeros(
                outdata[:frames_per_buffer].shape
            )
            return
        
        # Set ended bool to True if end reached
        if new_pos >= len(self.frames):
            new_pos = len(self.frames)
            self.ended = True

        # Set outdata to next frames of loaded audio
        try:
            data = self.frames[self.position:new_pos].reshape(-1,1)
            outdata[:frames_per_buffer] = data
        # Case: not enough frames from data compared to buffer size
        except ValueError as e:
            # Add padded zeros to data to match expected shape
            zero_padded_data = data.copy().resize(frames_per_buffer,1)
            outdata[:frames_per_buffer] = zero_padded_data

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