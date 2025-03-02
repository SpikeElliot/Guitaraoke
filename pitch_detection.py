from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH
import os


def save_pitches(audio):
    """
    Saves the note events CSV file from Spotify's Basic Pitch model prediction
    run on a given audio file.

    Parameters
    ----------
    audio : AudioLoadHandler or str
        The AudioLoadHandler object whose path property will be used to
        access the audio file, or a path to the audio file in the case
        the user's audio input recording is being predicted.

    Returns
    -------
    pitches_path : str
        The file path to the note events CSV file resultant from the pitch
        prediction.
    """
    output_folder = "./pitch_predictions"
    audio_path = ""
    audio_filename = ""

    # Case: audio is the user's audio input recording file path string
    if type(audio) == str:
        os.makedirs( # Make directory for audio input predictions if not exists
            f"./pitch_predictions/temp",
            exist_ok=True
        )
        output_folder += "/temp"
        audio_path = audio
        audio_filename = audio.split(".")[0].split("\\")[-1]
    # Case: audio is an AudioLoadHandler object
    else:
        os.makedirs( # Make directory for song pitch predictions
            f"./pitch_predictions/songs/{audio.filedir}",
            exist_ok=True
        )
        output_folder += f"/songs/{audio.filedir}"
        audio_path = audio.path
        audio_filename = audio.filename

    predict_and_save(
        [audio_path], # Input file path
        output_folder, # Directory resultant files will be saved to
        save_midi=False, # Save MIDI file of predicted notes
        sonify_midi=False, # Save wav file of sonified MIDI for testing
        save_model_outputs=False, # Model outputs are not necessary
        save_notes=True, # Save note events in CSV file
        model_or_model_path=ICASSP_2022_MODEL_PATH, # Default model
        minimum_note_length=68, # A note every 68ms is ~16th notes at 220bpm
        multiple_pitch_bends=True, # More accurate to bending of guitar notes
    )
    return f"{output_folder}/{audio_filename}_basic_pitch.csv"