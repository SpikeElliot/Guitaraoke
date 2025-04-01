"""Module providing an AudioInput class."""

import os
import time
import tempfile
import threading
import numpy as np
import pandas as pd
import sounddevice as sd
from PyQt5.QtCore import QThread, pyqtSignal # pylint: disable=no-name-in-module
from scipy.io.wavfile import write as write_wav
import config
from guitaraoke.save_pitches import save_pitches
from guitaraoke.compare_pitches import compare_pitches
from guitaraoke.utils import preprocess_pitch_data, csv_to_pitches_dataframe


class AudioInput(QThread):
    """
    Handles operations relating to audio input such as streaming and recording.

    Attributes
    ----------
    BUFFER_SIZE : int
        The size of the audio input buffer in frames.
    OVERLAP_SIZE : int
        The size of the audio input overlapping window in frames.
    input_devices : list of dicts
        A list of available audio input devices.
    input_device_index : int
        The index of the input device used.
    song_pitches : AudioPlayback
        The song pitch data needed to compare against for score calculation.
    streaming : bool
        Whether the user's audio input is currently being recorded or not.

    Methods
    -------
    set_input_device(input_dev_idx)
        Sets the input device to use for the sounddevice input stream by index
        in input_devices list.
    """
    score_processed = pyqtSignal(int, float, int) # Connects the QThread to the GUI
    # Audio input stream is saved in 2 second windows to prevent notes from
    # being cut off, as is the case when using sounddevice's rec function.
    BUFFER_SIZE = int(6 * config.RATE)
    OVERLAP_SIZE = int(2 * config.RATE)

    def __init__(self, song_pitches: pd.DataFrame) -> None:
        """
        The constructor for the AudioInput class.
        
        Parameters
        ----------
        song : AudioPlayback
            The currently-playing song whose current time position and pitch data
            is needed.
        """
        super().__init__()
        self.song_pitches = song_pitches

        self.stream = None
        self.streaming = False
        self.stream_start = {}

        self.buffer = np.zeros(self.BUFFER_SIZE)
        self.audio_blocks = np.ndarray(0)

        self.input_devices = self._find_input_devices()
        self.input_device_index = 0
        self.set_input_device(self.input_device_index)

    def _find_input_devices(self) -> None:
        """Return a list of available audio input devices."""
        devices = sd.query_devices()
        input_devs = []
        for d in devices:
            if d["max_input_channels"] > 0 and d["hostapi"] == 0:
                input_devs.append(d)
        return input_devs

    def set_input_device(self, input_dev_idx: int) -> None:
        """
        Sets the input device to use for the sounddevice input stream by index
        in input_devices list. Starts a new input stream using the desired input device.

        Parameters
        ----------
        input_dev_idx : int
            The input_devices list index of the desired input device.
        """
        # Terminate previous input stream
        if self.stream:

        self.input_device_index = input_dev_idx
        # Create new stream using this input device
        self.stream = sd.InputStream(
            samplerate=self.RATE,
            device=self.input_device_index,
            channels=config.CHANNELS,
            dtype=config.DTYPE,
            callback=self._callback,
            latency="low",
        )
        self.streaming = False

    def _callback(self, indata, f, t, s) -> None: # pylint: disable=W0613
        """
        The callback function called by the sounddevice input stream. 
        Generates input audio data.
        """
        self.audio_blocks = np.append(self.audio_blocks, indata)

    def _process_recording(self) -> None:
        """
        Convert the user input recording into a MIDI file, and compare the
        user's predicted pitches to the audio file's aligned at the correct
        time. The resultant score data is sent to the GUI.
        """
        while self.streaming:
            if self.audio_blocks.size >= self.OVERLAP_SIZE:
                # Add new window to buffer and shift to the left by overlap duration
                self.buffer = np.append(
                    self.buffer,
                    self.audio_blocks[:self.OVERLAP_SIZE]
                )
                self.buffer = self.buffer[self.OVERLAP_SIZE:]
                self.audio_blocks = self.audio_blocks[self.OVERLAP_SIZE:]

                # Save recorded audio as a temp WAV file
                with tempfile.TemporaryFile(delete=False, suffix=".wav") as temp_recording:

                buffer_size_s = self.BUFFER_SIZE / self.RATE # In seconds

                user_pitches_path = save_pitches(temp_recording.name, temp=True)[0]
                user_pitches = csv_to_pitches_dataframe(user_pitches_path)
                current_time = ( # Get current time in song

                # Align user note event times to current song position
                user_pitches = csv_to_pitches_dataframe(user_pitches_path)
                user_pitches["start_time_s"] += current_time - (self.BUFFER_SIZE/config.RATE)

                # Convert user and song pitches to dicts of note event sequences
                user_pitches = preprocess_pitch_data(user_pitches)
                song_pitches = preprocess_pitch_data(
                    self.song_pitches,
                    slice_start=current_time - (self.BUFFER_SIZE/config.RATE),
                    slice_end=current_time
                )

                # TESTING
                # print("user pitches:",user_pitches)
                # print("song pitches:",song_pitches)

                # Perform scoring
                score_results = compare_pitches(user_pitches, song_pitches)
                self.score_processed.emit(*score_results) # Send score to GUI

                # Clean up
                os.remove(user_pitches_path)

            time.sleep(0.01) # Reduce CPU load

    def run(self) -> None:
        """Starts the user input recording-processing loop."""
        print("\nRecording...")
        self.stream.start()
        self.streaming = True
        audio_processing_thread = threading.Thread(
            target=self._process_recording,
        )
        audio_processing_thread.daemon = True
        audio_processing_thread.start()

    def stop(self) -> None:
        """Stops the user input recording-processing loop."""
        print("\nRecording stopped.")
        self.stream.stop()
        self.buffer = np.zeros(self.BUFFER_SIZE) # Reset buffer when streaming ends
        self.streaming = False
        self.quit()
        self.wait()
