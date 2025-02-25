# Allow importing modules from parent directory
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from audio_load_handler import AudioLoadHandler
from pitch_detection import save_song_pitches

# -------------------------- TESTING --------------------------

test_audio = AudioLoadHandler(path="./separated_tracks/htdemucs_6s/sweetchildomine/guitar.wav")

save_song_pitches(test_audio)