from PyQt5.QtCore import QThread, pyqtSignal
import threading
import os
import sounddevice as sd
import tempfile
import numpy as np
from scipy.io.wavfile import write
from pitch_detection import save_pitches


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
    record_duration : int
        The length of time of the recording in seconds.
    recording : bool
        Whether the audio input is currently being recorded or not.
    score_processed : pyqtSignal
        Connects the _process_record_audio method to the main application,
        sending the returned "score" value to a different function.

    Methods
    -------
    set_input_device(input_dev_idx)
        Sets the input device to use for the sounddevice input stream by index
        in input_devices list.
    """
    score_processed = pyqtSignal(int)

    def __init__(self):
        """The constructor for the AudioInputHandler class."""
        super().__init__()
        self.CHANNELS = 1
        self.RATE = 44100
        self.DTYPE = "float32" # Datatype used by audio processing libraries
        
        # Audio input stream is saved in 1 second windows to prevent notes from
        # being cut off, as is the case when using sounddevice's rec function.
        self.BUFFER_SIZE = int(self.RATE * 5)
        self.OVERLAP_SIZE = int(self.RATE * 1)
        self.buffer = np.zeros(self.BUFFER_SIZE)
        self.input_devices = self._find_input_devices()
        self.input_device_index = 0
        self.set_input_device(self.input_device_index)

    def _find_input_devices(self):
        """Return a list of available audio input devices."""
        devices = sd.query_devices()
        input_devs = []
        for d in devices:
            if d["max_input_channels"] > 0 and d["hostapi"] == 0:
                input_devs.append(d)
        return input_devs
    
    def set_input_device(self, input_dev_idx : int):
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
            blocksize=self.OVERLAP_SIZE,
            device=self.input_device_index,
            channels=self.CHANNELS,
            dtype=self.DTYPE,
            callback=self._callback
        )
    
    def _callback(self, indata, frames, time, status):
        """
        The callback function called by the sounddevice input stream. 
        Generates input audio data.
        """
        # Add new window to buffer and shift to the left by overlap duration
        self.buffer = np.append(self.buffer, indata)
        self.buffer = self.buffer[self.OVERLAP_SIZE:]

        # Save recorded audio as a temp WAV file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        write(temp_file.name, self.RATE, self.buffer)
        print(str(temp_file.name))

        # Process saved audio
        threading.Thread(
            target=self._process_recorded_audio,
            args=(temp_file.name,)
        ).start()

    def _process_recorded_audio(self, path : str):
        """
        Convert the user input recording into a MIDI file, and compare the
        user's predicted pitches to the audio file's aligned at the same time.

        Parameters
        ----------
        path : str
            The path of the temporary user recording audio file.
        """
        pitches_path = save_pitches(path)

        # TODO Call comparison logic function here to get a score
        score = 0

        os.remove(pitches_path) # Delete file when processing complete
        self.score_processed.emit(score)

    def run(self):
        """Starts the user input recording-processing loop."""
        print(f"Recording...")
        self.stream.start()
    
    def stop(self):
        """Stops the user input recording-processing loop."""
        print("Recording stopped.")
        self.stream.stop()
        self.quit()
        self.wait()