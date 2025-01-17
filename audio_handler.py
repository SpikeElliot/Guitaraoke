import pyaudio
import numpy as np
import librosa


class AudioHandler():
    
    def __init__(self):
        self.CHUNK = 1024 * 2
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100

        self.frames = librosa.load(path='Rift.mp3', sr=self.RATE)[0]
        self.duration = len(self.frames) / float(self.RATE) # Song length in seconds