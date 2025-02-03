from audio_handling.audio_load_handler import AudioLoadHandler
from audio_analysis.note_predictor import NotePredictor
import matplotlib.pyplot as plt


# ---------------------- NOTE_PREDICTOR TESTING ----------------------

test_audio = AudioLoadHandler()

note_pred = NotePredictor()

test_predictions = note_pred.predict(test_audio)

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

plt.plot(times, freqs)
plt.yticks(freqs, labels=notes)
plt.show()