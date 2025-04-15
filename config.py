"""Provides config variables used across the codebase."""

from pathlib import Path

# Audio
CHANNELS = 1
RATE = 44100
DTYPE = "float32" # Datatype preferred by audio processing libraries
SEP_TRACKS_DIR = Path("./assets/separated_tracks/htdemucs_6s")
SAVED_PITCHES_DIR = Path("./assets/pitch_predictions")
REC_BUFFER_SIZE = int(3 * RATE)
INPUT_DEVICE_INDEX = 2

# GUI
WIDTH, HEIGHT = 1440, 500
THEME_COLOUR = "#0070df"
INACTIVE_COLOUR = "#4e759c"
