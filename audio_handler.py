import pyaudio
import numpy as np
import librosa
from tinytag import TinyTag
import pygame


class AudioHandler():
    
    def __init__(self):
        pygame.mixer.init()
        
        self.CHUNK = 1024 * 2
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100
        self.PATH = 'Rift.mp3'
        self.paused = False
        self.ended = True

        # Load song for playback
        pygame.mixer.music.load(self.PATH)

        # Get song metadata
        metadata = TinyTag.get(self.PATH)
        self.title = metadata.title
        self.artist = metadata.artist

        # Get song frames and length
        self.frames = librosa.load(path=self.PATH, sr=self.RATE)[0]
        self.duration = len(self.frames) / float(self.RATE) # In seconds

        # Get song frequency data for spectrogram plot
        C = librosa.cqt(y=self.frames, sr=self.RATE)
        self.C_db = librosa.amplitude_to_db(np.abs(C), ref=np.max)

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
    def getPos(self):
        pos = pygame.mixer.music.get_pos() / 1000
        return pos
    
    # Set time position of song (converts from seconds to milliseconds)
    def setPos(self, pos):
        pygame.mixer.music.set_pos(pos * 1000)