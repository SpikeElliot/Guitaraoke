"""
Preloads the Basic Pitch model and updates config latency variables.
"""

import os
import sys
from pathlib import Path
from configparser import ConfigParser
from basic_pitch.inference import Model
from basic_pitch import ICASSP_2022_MODEL_PATH
import sounddevice as sd

# Preload the Basic Pitch model
PITCH_MODEL = Model(ICASSP_2022_MODEL_PATH)

def preload():
    """Perform necessary preloading steps for the application."""

    # Update config file
    parser = ConfigParser()
    parser.read("config.ini")

    # Write current device latency values
    in_latency = sd.query_devices(
        device=parser.getint("Audio", "input_device_index")
    )["default_low_output_latency"]
    parser.set("Audio", "in_latency", str(in_latency))

    out_latency = sd.query_devices(
        kind="output"
    )["default_low_output_latency"]
    parser.set("Audio", "out_latency", str(out_latency))

    # Set root path to temp directory if being run as an executable
    if getattr(sys, "frozen", False):
        path = Path(sys._MEIPASS) # pylint: disable=protected-access
    else:
        path = Path(os.getcwd())

    # Write directory paths
    parser.set("Directories", "sep_tracks_dir",
            (str(path / "data" / "separated_tracks" / "htdemucs_6s"))
    )

    parser.set("Directories", "saved_pitches_dir",
            (str(path / "data" / "pitch_predictions"))
    )

    parser.set("Directories", "assets_dir",
            (str(path / "assets"))
    )

    parser.set("Directories", "data_dir",
            (str(path / "data"))
    )

    with open("config.ini", "w", encoding="utf-8") as configfile:
        parser.write(configfile)
