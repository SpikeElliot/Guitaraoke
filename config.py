"""Provides config variables used across the codebase."""

from pathlib import Path
from basic_pitch.inference import Model
from basic_pitch import ICASSP_2022_MODEL_PATH
import sounddevice as sd

# Audio
CHANNELS = 1
RATE = 44100
DTYPE = "float32" # Datatype preferred by audio processing libraries
SEP_TRACKS_DIR = Path("./assets/separated_tracks/htdemucs_6s")
SAVED_PITCHES_DIR = Path("./assets/pitch_predictions")
REC_BUFFER_SIZE = int(3 * RATE)
PITCH_MODEL = Model(ICASSP_2022_MODEL_PATH) # Preload the Basic Pitch model
INPUT_DEVICE_INDEX = 2
INPUT_LATENCY = sd.query_devices(
    device=INPUT_DEVICE_INDEX
)["default_low_output_latency"]
OUTPUT_LATENCY = sd.query_devices(
    kind="output"
)["default_low_output_latency"]

# GUI
WIDTH, HEIGHT = 1440, 500
THEME_COLOUR = "#0070df"
INACTIVE_COLOUR = "#4e759c"
