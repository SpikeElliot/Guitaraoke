import os
import sys
# Allow importing modules from parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
import sounddevice as sd
from audio_load_handler import AudioLoadHandler


test_audio = AudioLoadHandler(path="./assets/backinblack.wav")
sd.play(test_audio.guitar_data, samplerate=test_audio.RATE)
print("Playing separated guitar track...")
sd.wait()