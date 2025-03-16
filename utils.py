import math
import pandas as pd


def time_format(time: float) -> str:
    """Takes time in seconds and returns a time string converted to MM:SS.CC format."""
    mins = math.floor(time / 60)
    secs = math.floor(time % 60)
    cents = int((time - math.floor(time)) * 100)
    
    formatted_time = '{:02d}'.format(mins) + ":"
    formatted_time +='{:02d}'.format(secs) + "."
    formatted_time += '{:02d}'.format(cents)

    return formatted_time

def hex_to_rgb(hex_string: str) -> tuple:
    """Takes a hex triplet and converts it to RGB values."""
    return tuple(int(hex_string.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

def csv_to_pitches_dataframe(path):
    """
    Use pandas read_csv function to read a CSV file as a DataFrame, dropping
    unwanted columns and sorting by note onset times.
    """
    pitches = pd.read_csv(
        path, 
        sep=None,
        engine="python",
        index_col=False
    ).drop(columns=["end_time_s", "velocity", "pitch_bend"]).sort_values("start_time_s")
    return pitches

def preprocess_pitch_data(pitches, slice_start=None, slice_end=None):
    """
    Takes a pandas DataFrame read from a Basic Pitch note events CSV file
    and performs pre-processing, returning a 2D array of note sequences.

    Parameters
    ----------
    pitches : DataFrame
        The pandas DataFrame containing note event information.
    slice_start, slice_end : float, optional
        The times in seconds to start and end time-slice.

    Returns
    -------
    pitch_sequences : dict
        A dictionary containing lists of the times in seconds of note on events
        for every possible MIDI pitch (0-127).
    """
    if slice_start and slice_end:
        pitches = pitches[(pitches["start_time_s"] >= slice_start)
                        & (pitches["start_time_s"] < slice_end)]
        
    pitch_sequences = {}
    for i in range(128):
        pitch_sequences[i] = []
    for row in pitches.itertuples():
        pitch_sequences[row.pitch_midi].append(row.start_time_s)

    return pitch_sequences
