"""
Provides miscellaneous utility functions used across the application.

Functions
---------
read_config(section)
    Get Audio or GUI variables from the config file.

find_audio_devices()
    Get lists of user audio input and output devices.

time_format(time)
    Return a time in MM:SS.CC format.

hex_to_rgb(hex_string)
    Get an RGB equivalent from a hex triplet.

csv_to_pitches_dataframe(path)
    Return sorted Pandas DataFrame converted from a pitches CSV file.

preprocess_pitch_data(
    pitches, 
    slice_start=None, slice_end=None, 
    offset_latency=False
)
    Return a dict of note events for 128 pitches from a pitches 
    Dataframe.
"""

import math
from pathlib import Path
from configparser import ConfigParser
import pandas as pd
import sounddevice as sd


def read_config(section: str) -> dict[str]:
    """Get Audio or GUI config variables."""
    if section not in ("Audio", "GUI"):
        raise ValueError("Only config sections are: Audio, GUI")

    parser = ConfigParser()
    parser.read("./config.ini")

    if section == "Audio":
        config_vals = {
            "channels": parser.getint(section, "channels"),
            "rate": parser.getint(section, "rate"),
            "dtype": parser.get(section, "dtype"),
            "sep_tracks_dir": parser.get(section, "sep_tracks_dir"),
            "saved_pitches_dir": parser.get(section, "saved_pitches_dir"),
            "rec_buffer_size": parser.getint(section, "rec_buffer_size"),
            "rec_overlap_window_size": parser.getint(section, "rec_overlap_window_size"),
            "input_device_index": parser.getint(section, "input_device_index"),
            "in_latency": parser.getfloat(section, "in_latency"),
            "out_latency": parser.getfloat(section, "out_latency")
        }
    else:
        config_vals = {
            "width": parser.getint(section, "width"),
            "height": parser.getint(section, "height"),
            "theme_colour": parser.get(section, "theme_colour"),
            "inactive_colour": parser.get(section, "inactive_colour")
        }
    return config_vals

def find_audio_devices() -> tuple[list, list]:
    """Return two lists of user audio input and output devices."""
    devices = sd.query_devices()
    input_devs = []
    output_devs = []
    for d in devices:
        if d["hostapi"] == 0:
            if d["max_input_channels"] > 0:
                input_devs.append(d)
            if d["max_output_channels"] > 0:
                output_devs.append(d)
    return input_devs, output_devs

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

config = read_config("Audio")

def preprocess_pitch_data(
    pitches: pd.DataFrame,
    slice_start: float | None = None,
    slice_end: float | None = None,
    offset_latency: bool = False
) -> dict[int, list]:
    """
    Take a pitches DataFrame and perform pre-processing, returning a
    2D array containing note onset times for all 128 MIDI pitches.

    Parameters
    ----------
    pitches : DataFrame
        The pandas DataFrame containing note event information.
    slice_start, slice_end : float, optional
        The times in seconds to start and end time-slice.
    offset_latency : bool
        Offset the note onset times by the user's round-trip latency.

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

    if offset_latency:
        latency = config["in_latency"] + config["out_latency"] + 0.15
        new_pitches["start_time_s"] -= latency

    pitch_sequences = {k: [] for k in range(128)}
    for row in new_pitches.itertuples():
        pitch_sequences[row.pitch_midi].append(row.start_time_s)

    return pitch_sequences
