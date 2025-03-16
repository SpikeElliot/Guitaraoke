import os
import sys
import tempfile
import unittest
import numpy as np
import pandas as pd
from scipy.io.wavfile import write
# Hack to import modules from parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from save_pitches import save_pitches
from utils import csv_to_pitches_dataframe


class TestSavePitches(unittest.TestCase):
    def test_invalid_file(self):
        with self.assertRaises(AssertionError):
            save_pitches(path="i_do_not_exist")

    def test_silent_audio(self):
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
        self.assertEqual(note_count, 0)

    def test_monotone_audio(self):
        # Save predicted notes from C3 sine test audio file
        test_pitches_path = save_pitches(".\\tests\\test_audio\\C3_sine_test.wav", temp=True)[0]
        test_notes_events = csv_to_pitches_dataframe(test_pitches_path)
        os.remove(test_pitches_path)

        # Assert there is only one correct pitch detected (C3 = 60)
        unique_pitches = test_notes_events["pitch_midi"].unique()
        self.assertEqual(unique_pitches, [60])

    def test_note_start_times(self):
        # Save predicted notes from test audio file where note start times have
        # an interval of exactly one second
        test_pitches_path = save_pitches(".\\tests\\test_audio\\1s_interval_test.wav", temp=True)[0]
        test_notes_events = csv_to_pitches_dataframe(test_pitches_path)
        os.remove(test_pitches_path)

        # Assert all predicted note onset times are accurate within 20ms
        note_start_times = test_notes_events["start_time_s"]
        for time in note_start_times:
            self.assertAlmostEqual(time, round(time), delta=0.02)


if __name__=="__main__":
    unittest.main()