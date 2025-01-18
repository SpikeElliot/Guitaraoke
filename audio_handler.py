import pyaudio
import numpy as np
import librosa


class AudioHandler():
    
    def __init__(self):
        self.CHUNK = 1024 * 2
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100

        self.frames = librosa.load(path='elecguitar_chromatic_scale.wav', sr=self.RATE)[0]
        self.duration = len(self.frames) / float(self.RATE) # Song length in seconds

        C = librosa.cqt(y=self.frames, sr=self.RATE)
        self.C_db = librosa.amplitude_to_db(np.abs(C), ref=np.max)