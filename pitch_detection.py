from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH
import os

# Saves the midi file and note events predicted from
# an audio file using Spotify's Basic Pitch model
def save_song_pitches(audio):
    # Make subdirectory for audio file in note_predictions
    os.makedirs(f"./pitch_predictions/songs/{audio.filedir}", exist_ok=True)

    # Save audio file's predicted MIDI data and note events
    predict_and_save(
        [audio.path], # Input file path
        f"./pitch_predictions/songs/{audio.filedir}", # Output folder
        save_midi=True, # Save MIDI file of predicted notes
        sonify_midi=True, # Save wav file of sonified MIDI for testing
        save_model_outputs=False, # Model outputs are not necessary
        save_notes=True, # Save note events in CSV file
        model_or_model_path=ICASSP_2022_MODEL_PATH, # Default model
        minimum_note_length=68, # A note every 68ms is ~16th notes at 220bpm
        multiple_pitch_bends=True, # More accurate to bending of guitar notes
        sonification_samplerate=audio.RATE # Match sample rate of input
    )

# TODO Real-time pitch detection of user's audio input stream
def predict_input_pitches(audio):
    pass