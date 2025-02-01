import pyaudio
import librosa
import numpy as np


class AudioStreamHandler():
    
    def __init__(self):
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = int(self.RATE * 0.02) # 20 ms buffer size
        self.FORMAT = pyaudio.paFloat32

        self.p = None
        self.stream = None
        self.data_np = None
        self.openStream(1)

        self.input_devices = []
        self.getNumDevices()

    # Get number of connected audio devices, then populate an array
    # with the names of every input device.
    def getNumDevices(self):
        num_devices = self.p.get_host_api_info_by_index(0).get('deviceCount') 
        for i in range(num_devices):
            if (self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                self.input_devices.append(self.p.get_device_info_by_host_api_device_index(0, i).get('name'))

    # Open audio stream with input device index parameter
    def openStream(self, idx):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=False,
            frames_per_buffer=self.CHUNK,
            stream_callback=self.callback,
            input_device_index=idx
        )

    # Callback function for audio stream
    def callback(self, data_in, frame_count, time_info, status):
        self.frames = np.frombuffer(data_in, dtype=np.float32)
        
        return None, pyaudio.paContinue
    
    # Close current audio stream
    def closeStream(self):
        self.stream.stop_stream()
        self.stream.close()