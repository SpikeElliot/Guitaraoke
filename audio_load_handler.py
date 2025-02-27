import librosa
from tinytag import TinyTag
import pygame


class AudioLoadHandler():
    """
    Handles operations relating to audio loading and playback.

    Attributes
    ----------
    CHANNELS : int
        Specifies whether the audio channel is mono (1) or stereo (2).
    RATE : int
        The sample rate of the audio.
    CHUNK : int
        The number of frames per buffer of audio.

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
        pygame.mixer.init()
        
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 2048
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

        # Load song for playback
        pygame.mixer.music.load(self.path)

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
        if self.ended or not self.paused:
            pygame.mixer.music.play()
            self.ended = False
        else:
            pygame.mixer.music.unpause()
        self.paused = False

    def pause(self):
        """Pause audio playback."""
        if not self.paused:
            pygame.mixer.music.pause()
            self.paused = True

    def get_pos(self):
        """Return the audio playback's current time position in seconds."""
        pos = pygame.mixer.music.get_pos() / 1000
        return pos
    
    def set_pos(self, pos):
        """Set the audio playback's time position to a new time in seconds."""
        pygame.mixer.music.set_pos(pos * 1000) # Convert from s to ms