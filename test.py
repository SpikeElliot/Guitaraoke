from audio_handling.audio_load_handler import AudioLoadHandler
from audio_analysis.note_predictor import NotePredictor
import matplotlib.pyplot as plt

from audio_separation.guitar_separator import GuitarSeparator

test_audio = AudioLoadHandler(path="./assets/nerv.wav")


# ---------------------- PITCH DETECTION TESTING ----------------------

def notePredictorTest():
    note_pred = NotePredictor()

    test_predictions = note_pred.predict(test_audio, save_data=True)

    # Temporary way to check note predictions
    for pred in test_predictions:
        print(f"Time: {pred['time']:.2f} | Mean Conf.: {pred['confidence']:.2f} | Median Freq.: {pred['frequency']:.2f} | Pred. Note: {pred['note']}")

    times = []
    freqs = []
    notes = []
    for pred in test_predictions:
        times.append(pred["time"])
        freqs.append(pred["frequency"])
        notes.append(pred["note"])

    plt.plot(times, freqs, linewidth=3)
    plt.yticks(freqs, labels=notes)
    plt.show()

# notePredictorTest()

# ---------------------- GUITAR SEPARATION TESTING ----------------------

def guitarSeparatorTest():
    guitar_sep = GuitarSeparator()
    guitar_sep.separate(test_audio)

guitarSeparatorTest()