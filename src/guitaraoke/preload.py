"""
Preloads the Basic Pitch model and provides a function for preloading
the paths of necessary directories.
"""

import os
import sys
from basic_pitch.inference import Model
from basic_pitch import ICASSP_2022_MODEL_PATH

# Preload the Basic Pitch model
PITCH_MODEL = Model(ICASSP_2022_MODEL_PATH)

def preload_directories() -> None:
    """Perform necessary preloading steps for the application."""

    os.environ["sep_tracks_dir"] = "data\\separated_tracks\\htdemucs_6s"
    os.environ["saved_notes_dir"] = "data\\note_predictions"

    # Set paths to _internal directory if being run as an executable
    if getattr(sys, "frozen", False):
        os.environ["assets_dir"] = f"{sys._MEIPASS}\\assets" # pylint: disable=protected-access
        os.environ["model_repo"] = f"{sys._MEIPASS}\\demucs_models" # pylint: disable=protected-access
        os.environ["PATH"] = f"{sys._MEIPASS}\\ffmpeg" + os.pathsep + os.environ["PATH"] # pylint: disable=protected-access
    else:
        os.environ["assets_dir"] = "assets"
        os.environ["model_repo"] = "demucs_models"
