from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH
import os


class NotePredictor():

    def __init__(self):
        pass
    

    def predict(self, audio):
        # Make subdirectory for audio file in note_predictions
        os.makedirs(f"./note_predictions/{audio.filename}", exist_ok=True)

        # Save audio file's predicted MIDI data and note events
        predict_and_save(
            audio_path_list=[audio.path],
            output_directory=f"./note_predictions/{audio.filename}",
            save_midi=True,
            sonify_midi=True,
            save_model_outputs=False,
            save_notes=True,
            model_or_model_path=ICASSP_2022_MODEL_PATH,
            sonification_samplerate=audio.RATE
        )