"""Performs integration testing of pitch saving and reading functionality."""

import os
import tempfile
import pytest
import numpy as np
import pandas as pd
from scipy.io.wavfile import write as write_wav
from guitaraoke.save_pitches import save_pitches
from guitaraoke.utils import csv_to_pitches_dataframe, read_config

config = read_config("Audio")

@pytest.fixture(name="silent_audio")
def silent_audio_fixture() -> np.ndarray:
    """Create mock silent audio for testing."""
    return np.zeros(shape=(2*config["rate"],)) # 2 seconds of silence


def test_no_notes_predicted_from_silent_audio(silent_audio: np.ndarray) -> None:
    """Assert there are zero predicted notes from silent audio"""
    # Create temporary silent audio file
    with tempfile.TemporaryFile(delete=False, suffix=".wav") as temp_recording:
        write_wav(temp_recording.name, config["rate"], silent_audio)
        print(f"\nCreated temp file: {temp_recording.name}")

        # Save predicted note events
        test_pitches_path = save_pitches(
            temp_recording.name,
            temp=True,
        )[0]
        test_note_events = pd.read_csv(test_pitches_path)

    # Clean up
    os.remove(test_pitches_path)

    note_count = test_note_events.shape[0]
    assert note_count == 0


def test_one_note_predicted_from_monotone_audio() -> None:
    """
    Assert only one pitch is predicted audio file playing a pure sine
    tone of C3.
    """
    # Save predicted note events
    test_pitches_path = save_pitches(
        ".\\assets\\audio\\test\\C3_sine_test.wav", 
        temp=True,
    )[0]
    test_notes_events = csv_to_pitches_dataframe(test_pitches_path)

    # Clean up
    os.remove(test_pitches_path)

    unique_pitches = test_notes_events["pitch_midi"].unique()
    assert unique_pitches == [60]


def test_predicted_note_times_are_accurate() -> None:
    """
    Assert all predicted note onset times are accurate within 20ms from test
    audio file in which notes are played at an interval of one second.
    """
    # Save predicted note events
    test_pitches_path = save_pitches(
        ".\\assets\\audio\\test\\1s_interval_test.wav",
        temp=True,
    )[0]
    test_notes_events = csv_to_pitches_dataframe(test_pitches_path)

    # Clean up
    os.remove(test_pitches_path)

    note_start_times = test_notes_events["start_time_s"]
    tolerance = 0.02
    for time in note_start_times:
        difference = np.abs(time - round(time))
        assert difference <= tolerance
