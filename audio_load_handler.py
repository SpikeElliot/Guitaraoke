import librosa
from tinytag import TinyTag
import pygame

class AudioLoadHandler():
    
    def __init__(self, path='./assets/elecguitar_chromatic_scale.wav'):
        pygame.mixer.init()
        
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 2048
        self.path = path
        
        self.load(self.path)
        
    # Load song data from a given path
    def load(self, path):
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

    # Play or unpause song
    def play(self):
        if self.ended or not self.paused:
            pygame.mixer.music.play()
            self.ended = False
        else:
            pygame.mixer.music.unpause()
        self.paused = False

    # Pause song playback
    def pause(self):
        if not self.paused:
            pygame.mixer.music.pause()
            self.paused = True

    # Return current time position of song in seconds
    def get_pos(self):
        pos = pygame.mixer.music.get_pos() / 1000
        return pos
    
    # Set time position of song (converts from seconds to milliseconds)
    def set_pos(self, pos):
        pygame.mixer.music.set_pos(pos * 1000)