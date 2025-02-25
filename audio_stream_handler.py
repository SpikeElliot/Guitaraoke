import sounddevice as sd
import tempfile
from scipy.io.wavfile import write

class AudioStreamHandler():
    
    def __init__(self):
        self.CHANNELS = 1 # Mono channel
        self.RATE = 44100 # Default sample rate of 44.1k
        self.RECORD_DURATION = 5 # 5 second audio chunk for recording
        self.DTYPE = "float32" # Datatype used by audio processing libraries

        # Create a list of all connected input devices
        devices = sd.query_devices()
        self.input_devices = []
        for d in devices:
            if d["max_input_channels"] > 0 and d["hostapi"] == 0:
                self.input_devices.append(d)

    # Open an input stream and record 5 seconds of audio, saving as a WAV file
    # Returns: temporary input audio recording file path
    def record(self, input_device_idx=0):
        print(f"Recording {self.RECORD_DURATION}s of input audio...")
        audio_data = sd.rec(
            int(self.RECORD_DURATION * self.RATE),
            samplerate=self.RATE,
            device=input_device_idx,
            channels=self.CHANNELS,
            dtype=self.DTYPE
        )
        sd.wait()

        # Save recorded audio as a temp WAV file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        write(temp_file.name, self.RATE, audio_data)

        return temp_file.name