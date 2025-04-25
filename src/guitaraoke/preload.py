"""
Preloads the Basic Pitch model and updates config latency variables.
"""

from configparser import ConfigParser
from basic_pitch.inference import Model
from basic_pitch import ICASSP_2022_MODEL_PATH
import sounddevice as sd

# Preload the Basic Pitch model
PITCH_MODEL = Model(ICASSP_2022_MODEL_PATH)

# Update config file with current devices' latency values
parser = ConfigParser()
parser.read("config.ini")

in_latency = sd.query_devices(
    device=parser.getint("Audio", "input_device_index")
)["default_low_output_latency"]
parser.set("Audio", "in_latency", str(in_latency))

out_latency = sd.query_devices(
    kind="output"
)["default_low_output_latency"]
parser.set("Audio", "out_latency", str(out_latency))

with open("config.ini", "w", encoding="utf-8") as configfile:
    parser.write(configfile)
