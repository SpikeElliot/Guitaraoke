from PyQt5.QtCore import QThread, pyqtSignal
import pandas as pd
import threading
import os
import sounddevice as sd
import tempfile
import numpy as np
import time
from scipy.io.wavfile import write
from pitch_detection import save_pitches
from utils import preprocess_pitch_data
from score_system import compare_pitches


class AudioInputHandler(QThread):
    """
    Handles operations relating to audio input such as streaming and recording.
    Inherits from PyQt5 QThread.

    Attributes
    ----------
    CHANNELS : int
        Specifies whether the audio channel is mono (1) or stereo (2).
    RATE : int
        The sample rate of the audio.
    DTYPE : str
        Specifies the audio's datatype.
    input_devices : list of dicts
        A list of available audio input devices.
    input_device_index : int
        The index of the input device used.
    BUFFER_SIZE : int
        The size of the audio input buffer in frames.
    OVERLAP_SIZE : int
        The size of the audio input overlapping window in frames.
    score_processed : pyqtSignal
        Connects the _process_recorded_audio method to the main application,
        sending the returned "score" value to a different function.
    song_pitch_data : DataFrame
        The pandas DataFrame containing the loaded song's guitar track
        predicted pitches.
    song : AudioPlayback
        The song loaded for playback whose current time position and pitch data
        is needed.
    streaming : bool
        Whether the user's audio input is currently being recorded or not.

    Methods
    -------
    set_input_device(input_dev_idx)
        Sets the input device to use for the sounddevice input stream by index
        in input_devices list.
    """
    score_processed = pyqtSignal(tuple)

    def __init__(self, song):
        """
        The constructor for the AudioInputHandler class.
        
        Parameters
        ----------
        song : AudioPlayback
            The currently-playing song whose current time position and pitch data
            is needed.
        """
        super().__init__()
        self.CHANNELS = 1
        self.RATE = 44100
        self.DTYPE = "float32" # Datatype used by audio processing libraries
        
        # Audio input stream is saved in 1 second windows to prevent notes from
        # being cut off, as is the case when using sounddevice's rec function.
        self.BUFFER_SIZE = int(self.RATE * 5)
        self.OVERLAP_SIZE = int(self.RATE * 1)
        self.buffer = np.zeros(self.BUFFER_SIZE)
        self.audio_blocks = np.ndarray(0)

        self.input_devices = self._find_input_devices()
        self.input_device_index = 0
        self.song = song
        self.streaming = False
        self.set_input_device(self.input_device_index)

    def _find_input_devices(self):
        """Return a list of available audio input devices."""
        devices = sd.query_devices()
        input_devs = []
        for d in devices:
            if d["max_input_channels"] > 0 and d["hostapi"] == 0:
                input_devs.append(d)
        return input_devs
    
    def set_input_device(self, input_dev_idx):
        """
        Sets the input device to use for the sounddevice input stream by index
        in input_devices list. Starts a new input stream using the desired input device.

        Parameters
        ----------
        input_dev_idx : int
            The input_devices list index of the desired input device.
        """
        self.input_device_index = input_dev_idx
        # Create new stream using this input device
        self.stream = sd.InputStream(
            samplerate=self.RATE,
            device=self.input_device_index,
            channels=self.CHANNELS,
            dtype=self.DTYPE,
            callback=self._callback,
        )

    # TODO: Move input streaming logic and record-processing loop to a dedicated
    # streaming class?
    
    def _callback(self, indata, frames, time, status):
        """
        The callback function called by the sounddevice input stream. 
        Generates input audio data.
        """
        self.audio_blocks = np.append(self.audio_blocks, indata)

    def _process_recorded_audio(self):
        """
        Convert the user input recording into a MIDI file, and compare the
        user's predicted pitches to the audio file's aligned at the correct
        time. The resultant score information is sent to the GUI.
        """
        while self.streaming:
            current_time = self.song.position / self.RATE # Update time

            if self.audio_blocks.size >= self.OVERLAP_SIZE:
                # Add new window to buffer and shift to the left by overlap duration
                self.buffer = np.append(self.buffer, self.audio_blocks[:self.OVERLAP_SIZE])
                self.buffer = self.buffer[self.OVERLAP_SIZE:]
                self.audio_blocks = self.audio_blocks[self.OVERLAP_SIZE:]
                
                # Save recorded audio as a temp WAV file
                temp_recording = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                write(temp_recording.name, self.RATE, self.buffer)
                print(f"\nCreated temp file: {temp_recording.name}")

                buffer_size_s = self.BUFFER_SIZE / self.RATE # In seconds
            
                # Save predicted user pitches to a temp CSV file
                user_pitches_path = save_pitches(temp_recording.name, input_recording=True)
                user_pitches = pd.read_csv( # Convert pitches CSV to a pandas DataFrame
                    user_pitches_path,
                    sep=None,
                    engine="python",
                    index_col=False
                ).drop(columns=["end_time_s", "velocity", "pitch_bend"]).sort_values("start_time_s")
                
                # Align user note event times to current song position
                user_pitches["start_time_s"] = user_pitches["start_time_s"] + (current_time - buffer_size_s)

                # Convert user and song pitches to dicts of note event sequences
                user_pitches = preprocess_pitch_data(user_pitches)
                song_pitches = preprocess_pitch_data(
                    self.song.audio.pitches,
                    slice_start=current_time - (self.BUFFER_SIZE / self.RATE),
                    slice_end=current_time
                )

                # TESTING
                # print("user pitches:",user_pitches)
                # print("song pitches:",song_pitches)

                score_information = compare_pitches(
                    user_pitches, 
                    song_pitches
                )

                # Delete temp files when processing complete
                os.remove(user_pitches_path)
                temp_recording.close()
                os.unlink(temp_recording.name)

                # Send score information to GUI
                self.score_processed.emit(score_information)

            time.sleep(0.01) # Reduce CPU load
        
    def run(self):
        """Starts the user input recording-processing loop."""
        print(f"\nRecording...")
        self.stream.start()
        self.streaming = True
        audio_processing_thread = threading.Thread(
            target=self._process_recorded_audio,
        )
        audio_processing_thread.daemon = True
        audio_processing_thread.start()
    
    def stop(self):
        """Stops the user input recording-processing loop."""
        print("\nRecording stopped.")
        self.stream.stop()
        self.streaming = False
        self.quit()
        self.wait()