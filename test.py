from audio_handling.audio_load_handler import AudioLoadHandler
from audio_analysis.note_predictor import NotePredictor
import matplotlib.pyplot as plt

from audio_separation.guitar_separator import GuitarSeparator

test_audio = AudioLoadHandler()


# ---------------------- PITCH DETECTION TESTING ----------------------

def notePredictorTest():
    note_pred = NotePredictor()

    preds = note_pred.predict(test_audio, save_data=True)

    # Temporary way to check note predictions
    for p in preds:
        print(f"Time: {p['time']:.2f} | Pitch: {p['pitch']:.2f} | Note: {p['note']} | Periodicity: {p['periodicity']:.2f}")

    # plt.plot(times, freqs, linewidth=3)
    # plt.yticks(freqs, labels=notes)
    # plt.show()

notePredictorTest()

# ---------------------- GUITAR SEPARATION TESTING ----------------------

def guitarSeparatorTest():
    guitar_sep = GuitarSeparator()
    guitar_sep.separate(test_audio)

# guitarSeparatorTest()