import os
import sys
# Allow importing modules from parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
import librosa
import sounddevice as sd
from audio_load_handler import AudioLoadHandler


test_audio = AudioLoadHandler(path="./assets/sweetchildomine_intro_riff.wav")
sonified_midi_path = f"./pitch_predictions/songs/{test_audio.filename}/guitar_basic_pitch.wav"
midi = librosa.load(sonified_midi_path, sr=test_audio.RATE)[0]
sd.play(midi, samplerate=test_audio.RATE)
print("Playing sonified MIDI...")
sd.wait()