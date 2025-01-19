import librosa
import matplotlib.pyplot as plt
from audio_handler import AudioHandler
import numpy as np

a = AudioHandler()

class SpectogramPlot():

    def __init__(self, audio):
        super().__init__()

        # Get song frequency data for spectrogram plot
        C = librosa.cqt(y=audio.frames, sr=audio.RATE)
        C_db = librosa.amplitude_to_db(np.abs(C), ref=np.max)

        # Matplotlib Constant-Q spectrogram that shows frequencies as note names
        fig, ax = plt.subplots()
        img = librosa.display.specshow(C_db, sr=audio.RATE, x_axis='time', y_axis='cqt_note', ax=ax)
        fig.colorbar(img, ax=ax, format="%+2.f dB")
        plt.show()

spec = SpectogramPlot(a)