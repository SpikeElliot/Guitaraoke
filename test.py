from audio_handling.audio_load_handler import AudioLoadHandler
from audio_analysis.note_predictor import NotePredictor
from audio_separation.guitar_separator import GuitarSeparator

test_audio = AudioLoadHandler()


# ---------------------- PITCH DETECTION TESTING ----------------------

def notePredictorTest():
    note_pred = NotePredictor()
    note_pred.predict(test_audio)

notePredictorTest()

# ---------------------- GUITAR SEPARATION TESTING ----------------------

def guitarSeparatorTest():
    guitar_sep = GuitarSeparator()
    guitar_sep.separate(test_audio)

# guitarSeparatorTest()