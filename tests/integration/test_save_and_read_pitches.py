import os
import pytest
import tempfile
import numpy as np
import pandas as pd
from scipy.io.wavfile import write
from guitaraoke.save_pitches import save_pitches
from guitaraoke.utils import csv_to_pitches_dataframe


def test_no_notes_predicted_from_silent_audio():
    # Create temporary silent audio file
    dummy_silent_audio = np.zeros(shape=(44100*2,)) # 2 seconds of silence
    temp_test_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    write(temp_test_file.name, 44100, dummy_silent_audio)

    # Save predicted note events
    test_pitches_path = save_pitches(temp_test_file.name, temp=True)[0]
    test_note_events = pd.read_csv(test_pitches_path)

    # Delete temp files when processing complete
    os.remove(test_pitches_path)
    temp_test_file.close()
    os.unlink(temp_test_file.name)

    # Assert there are zero predicted notes from silent audio
    note_count = test_note_events.shape[0]
    assert note_count == 0


def test_one_note_predicted_from_monotone_audio():
    # Save predicted notes from audio file featuring a pure sine tone of C3
    test_pitches_path = save_pitches(".\\assets\\audio\\test\\C3_sine_test.wav", temp=True)[0]
    test_notes_events = csv_to_pitches_dataframe(test_pitches_path)
    os.remove(test_pitches_path)

    # Assert only one pitch (C3 = 60) is predicted
    unique_pitches = test_notes_events["pitch_midi"].unique()
    assert unique_pitches == [60]


def test_predicted_note_times_are_accurate():
    # Save predicted notes from test audio file where note start times have
    # an interval of exactly one second
    test_pitches_path = save_pitches(".\\assets\\audio\\test\\1s_interval_test.wav", temp=True)[0]
    test_notes_events = csv_to_pitches_dataframe(test_pitches_path)
    os.remove(test_pitches_path)

    # Assert all predicted note onset times are accurate within 20ms
    note_start_times = test_notes_events["start_time_s"]
    tolerance = 0.02
    for time in note_start_times:
        difference = np.abs(time - round(time))
        assert difference <= tolerance