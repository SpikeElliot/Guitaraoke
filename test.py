from audio_handling.audio_load_handler import AudioLoadHandler
from audio_analysis.note_predictor import NotePredictor


# ---------------------- NOTE_PREDICTOR TESTING ----------------------

test_audio = AudioLoadHandler()

note_pred = NotePredictor(confidence_threshold=0.7)

note_pred.predict(test_audio)