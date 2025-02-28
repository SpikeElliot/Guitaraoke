# Allow importing modules from parent directory
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from audio_load_handler import AudioLoadHandler
from guitar_separation import separate_guitar


test_audio = AudioLoadHandler(path="./assets/sweetchildomine.wav")
separate_guitar(test_audio)