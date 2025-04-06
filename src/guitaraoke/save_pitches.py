"""
Module providing a function to perform pitch detection using a model from
Spotify's Basic Pitch library.
"""

import os
from pathlib import Path
from basic_pitch import ICASSP_2022_MODEL_PATH
from basic_pitch.inference import predict_and_save
from config import SAVED_PITCHES_DIR


def save_pitches(
    path: str,
    sonify: bool = False,
    temp: bool = False
) -> list[str]:
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
    paths : list[Path]
        The file paths to the note events CSV file [0] and the sonified
        MIDI file [1] if sonify=True.
    """
    path = Path(path)
    assert path.exists(), "File does not exist"

    parent = path.parent.stem
    out_folder = SAVED_PITCHES_DIR

    if temp:
        # Directory for input recording predicted pitches
        out_folder = out_folder / "temp"
    else:
        # Directory for song predicted pitches
        out_folder = out_folder / "songs" / parent

    os.makedirs(out_folder, exist_ok=True)

    filename = path.stem
    paths = [out_folder / f"{filename}_basic_pitch.csv"]

    # Check pitches file does not already exist
    if not paths[0].exists():
        predict_and_save(
            [str(path)], # Input file path
            str(out_folder), # Directory pitch files will be saved to
            save_midi=False, # Saving the actual MIDI file is not necessary
            sonify_midi=sonify, # Save rendered MIDI as WAV file for testing
            save_model_outputs=False, # Model outputs are not necessary
            save_notes=True, # Save note events in CSV file
            model_or_model_path=ICASSP_2022_MODEL_PATH, # Default model
            minimum_note_length=68, # A note every 68ms is ~16th notes at 220bpm
            multiple_pitch_bends=True, # More accurate to bending of guitar notes
        )

    if sonify:
        paths.append(out_folder / f"{filename}_basic_pitch.wav")

    return paths
