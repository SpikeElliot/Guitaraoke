"""
Module providing various utility functions.

Functions
---------
time_format(time)
hex_to_rgb(hex_string)
csv_to_pitches_dataframe(path)
preprocess_pitch_data(pitches, slice_start=None, slice_end=None)
"""

import math
import pandas as pd


def time_format(time: float) -> str:
    """Takes time in seconds and returns a time string converted to MM:SS.CC format."""
    mins = math.floor(time / 60)
    secs = math.floor(time % 60)
    cents = int((time - math.floor(time)) * 100)

    return f"{mins:02d}:{secs:02d}.{cents:02d}"


def hex_to_rgb(hex_string: str) -> tuple:
    """Takes a hex triplet and converts it to RGB values."""
    return tuple(int(hex_string.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))


def csv_to_pitches_dataframe(path: str) -> pd.DataFrame:
    """
    Use pandas read_csv function to read a CSV file as a DataFrame, dropping
    unwanted columns and sorting by note onset times.
    """
    return pd.read_csv(
        path,
        sep=None,
        engine="python",
        index_col=False
    ).drop(
        columns=["end_time_s", "velocity", "pitch_bend"]
    ).sort_values("start_time_s")


def preprocess_pitch_data(
    pitches: pd.DataFrame,
    slice_start: float | None = None,
    slice_end: float | None = None
) -> dict[int, list]:
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
    pitch_sequences : dict[int, list]
        A dictionary containing lists of the times in seconds of note on events
        for every possible MIDI pitch (0-127).
    """
    new_pitches = pitches.copy()

    if slice_start and slice_end:
        new_pitches = pitches[
            (pitches["start_time_s"] >= slice_start)
            & (pitches["start_time_s"] < slice_end)
        ]

    pitch_sequences = {k: [] for k in range(128)}
    for row in new_pitches.itertuples():
        pitch_sequences[row.pitch_midi].append(row.start_time_s)

    return pitch_sequences
