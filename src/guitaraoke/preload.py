"""
Preloads the Basic Pitch model and updates config directory values.
"""

import os
import sys
from pathlib import Path
from configparser import ConfigParser
from basic_pitch.inference import Model
from basic_pitch import ICASSP_2022_MODEL_PATH

# Preload the Basic Pitch model
PITCH_MODEL = Model(ICASSP_2022_MODEL_PATH)

def preload():
    """Perform necessary preloading steps for the application."""

    # Update config file
    parser = ConfigParser()
    parser.read("config.ini")

    # Write directory paths
    parser.set("Directories", "sep_tracks_dir",
            (str(Path(os.getcwd()) / "data" / "separated_tracks" / "htdemucs_6s"))
    )

    parser.set("Directories", "saved_pitches_dir",
            (str(Path(os.getcwd()) / "data" / "pitch_predictions"))
    )

    parser.set("Directories", "data_dir",
            (str(Path(os.getcwd()) / "data"))
    )

    # Set assets path to temp directory if being run as an executable
    if getattr(sys, "frozen", False):
        assets_path = Path(sys._MEIPASS) # pylint: disable=protected-access
    else:
        assets_path = Path(os.getcwd())
    parser.set("Directories", "assets_dir",
            (str(assets_path / "assets"))
    )

    with open("config.ini", "w", encoding="utf-8") as configfile:
        parser.write(configfile)
