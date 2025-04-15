"""
Provides miscellaneous utility functions used across the application.

Functions
---------
time_format(time)
    Return a time in MM:SS.CC format.

hex_to_rgb(hex_string)
    Get an RGB equivalent from a hex triplet.

csv_to_pitches_dataframe(path)
    Return sorted Pandas DataFrame converted from a pitches CSV file.

preprocess_pitch_data(pitches, slice_start=None, slice_end=None)
    Return a dict of note events for 128 pitches from a pitches Dataframe.
"""

import math
from pathlib import Path
import pandas as pd


def time_format(time: float) -> str:
    """Take a time in seconds and return it in MM:SS.CC format."""
    mins = math.floor(time / 60)
    secs = math.floor(time % 60)
    cents = int((time - math.floor(time)) * 100)

    return f"{mins:02d}:{secs:02d}.{cents:02d}"


def hex_to_rgb(hex_string: str) -> tuple:
    """Take a hex triplet and convert it to RGB values."""
    return tuple(int(hex_string.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))


def csv_to_pitches_dataframe(path: Path) -> pd.DataFrame:
    """
    Return a Pandas DataFrame from a pitches CSV file, dropping
    unnecessary columns and sorting by note onset times.
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
    Take a pitches DataFrame and perform pre-processing, returning a
    2D array containg note onset times for all 128 MIDI pitches.

    Parameters
    ----------
    pitches : DataFrame
        The pandas DataFrame containing note event information.
    slice_start, slice_end : float, optional
        The times in seconds to start and end time-slice.

    Returns
    -------
    pitch_sequences : dict[int, list]
        A dictionary containing lists of the times in seconds of note
        onsets for every possible MIDI pitch (0-127).
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
