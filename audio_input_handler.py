from PyQt5.QtCore import QThread, pyqtSignal
import threading
import time
import os
import sounddevice as sd
import tempfile
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
    record()
        Save a WAV file recording of the audio input stream.
    """
    score_processed = pyqtSignal(int)

    def __init__(self):
        """The constructor for the AudioInputHandler class."""
        super().__init__()
        self.CHANNELS = 1
        self.RATE = 44100
        self.DTYPE = "float32" # Datatype used by audio processing libraries
        self.input_devices = self._find_input_devices()
        self.input_device_index = 0
        self.record_duration = 5
        self.recording = False

    def _find_input_devices(self):
        """Return a list of available audio input devices."""
        devices = sd.query_devices()
        input_devs = []
        for d in devices:
            if d["max_input_channels"] > 0 and d["hostapi"] == 0:
                input_devs.append(d)
        return input_devs

    def _record(self):
        """
        Record an audio input stream for a given duration in seconds using a
        given input device's index, saving the data to a temporary WAV file.

        Returns
        -------
        recording_path : str
            The file path to the newly-created temp file.
        """
        print(f"Recording {self.record_duration:.1f}s of input audio...")
        self.recording = True

        audio_data = sd.rec(
            int(self.record_duration * self.RATE),
            samplerate=self.RATE,
            device=self.input_device_index,
            channels=self.CHANNELS,
            dtype=self.DTYPE
        )
        sd.wait()

        # Save recorded audio as a temp WAV file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        write(temp_file.name, self.RATE, audio_data)
        return temp_file.name

    def _process_recorded_audio(self, path):
        pitches_path = save_pitches(path)

        # TODO Call comparison logic function here to get a score
        score = 0

        os.remove(pitches_path) # Delete file when processing complete
        self.score_processed.emit(score)

    def run(self):
        while self.recording:
            recording = self._record()

            threading.Thread(
                target=self._process_recorded_audio,
                args=(recording,)
            ).start()

            time.sleep(self.record_duration)
    
    def stop(self):
        print("Recording stopped.")
        self.recording = False
        self.quit()
        self.wait()