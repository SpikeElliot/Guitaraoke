import os
from basic_pitch import ICASSP_2022_MODEL_PATH
from basic_pitch.inference import predict_and_save


def save_pitches(path : str, sonify=False, temp=False):
    """
    Saves the note events CSV file from Spotify's Basic Pitch model prediction
    run on a given audio file.

    Parameters
    ----------
    path : str
        The path of the audio file to make pitch predictions for.
    sonify : bool, default=False
        Whether to render audio from predicted MIDI and save to an audio file.
    temp : bool, default=False
        Whether the audio file is a saved song or a temporary recording.
        
    Returns
    -------
    paths : list of str
        The file paths to the note events CSV file [0] and the sonified
        MIDI file [1] if sonify=True.
    """
    assert os.path.isfile(path), "File does not exist"
    output_folder = "./assets/pitch_predictions"
    filename = ""
    
    # Case: path is to a temp audio input recording file
    if temp:
        filename = path.split(".")[-2].split("\\")[-1]

        # Make directory for audio input predictions if not exists
        os.makedirs( f"./assets/pitch_predictions/temp", exist_ok=True)
        output_folder += "/temp"
    else: # Case: path is to a loaded audio file
        filedir = path.split("/")[-2]
        filename = path.split(".")[-2].split("/")[-1]
        
        # Make directory for song pitch predictions
        os.makedirs( f"./assets/pitch_predictions/songs/{filedir}", exist_ok=True)
        output_folder += f"/songs/{filedir}"

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

    paths = [f"{output_folder}/{filename}_basic_pitch.csv"]
    if sonify : paths.append(f"{output_folder}/{filename}_basic_pitch.wav")
    return paths