from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH
import os


def save_pitches(path, input_recording=False):
    """
    Saves the note events CSV file from Spotify's Basic Pitch model prediction
    run on a given audio file.

    Parameters
    ----------
    path : str
        The path of the audio file to make pitch predictions for.
    input_recording : bool, default=False
        Whether the audio file is a loaded song (False) or a temporary
        user input recording (True).
    Returns
    -------
    pitches_path : str
        The file path to the note events CSV file resultant from the pitch
        prediction.
    """
    output_folder = "./pitch_predictions"
    filename = ""
    sonify = False

    # Case: path is for a temporary audio input recording file
    if input_recording:
        filename = path.split(".")[0].split("\\")[-1]
        # Make directory for audio input predictions if not exists
        os.makedirs( f"./pitch_predictions/temp", exist_ok=True)
        output_folder += "/temp"
    # Case: path is for a loaded audio file that will be played
    else:
        filedir = path.split("/")[-2]
        filename = path.split(".")[-2].split("/")[-1]
        # Make directory for song pitch predictions
        os.makedirs( f"./pitch_predictions/songs/{filedir}", exist_ok=True)
        output_folder += f"/songs/{filedir}"
        sonify = True

    predict_and_save(
        [path], # Input file path
        output_folder, # Directory resultant files will be saved to
        save_midi=False, # Save MIDI file of predicted notes
        sonify_midi=sonify, # Save wav file of sonified MIDI for testing
        save_model_outputs=False, # Model outputs are not necessary
        save_notes=True, # Save note events in CSV file
        model_or_model_path=ICASSP_2022_MODEL_PATH, # Default model
        minimum_note_length=68, # A note every 68ms is ~16th notes at 220bpm
        multiple_pitch_bends=True, # More accurate to bending of guitar notes
    )
    return f"{output_folder}/{filename}_basic_pitch.csv"