import os
import sys
import sounddevice as sd
from audio_playback import AudioPlayback
# Hack to import modules from parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)


test_audio = AudioPlayback(path="./assets/backinblack.wav")
sd.play(test_audio.guitar_data, samplerate=test_audio.RATE)
print("Playing separated guitar track...")
sd.wait()