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


if __name__=="__main__":
    unittest.main()