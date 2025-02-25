import pyaudio

class AudioStreamHandler():
    
    def __init__(self):
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 2048
        self.FORMAT = pyaudio.paFloat32

        self.p = pyaudio.PyAudio()
        self.stream = None
        self.open_stream(0)

        self.input_devices = []
        self.get_num_devices()

    # Get number of connected audio devices, then populate an array
    # with the names of every input device.
    def get_num_devices(self):
        num_devices = self.p.get_host_api_info_by_index(0).get('deviceCount') 
        for i in range(num_devices):
            if self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
                self.input_devices.append(self.p.get_device_info_by_host_api_device_index(0, i).get('name'))

    # Open audio stream with input device index parameter
    def open_stream(self, idx):
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=False,
            frames_per_buffer=self.CHUNK,
            input_device_index=idx
        )
    
    # Close current audio stream
    def close_stream(self):
        self.stream.stop_stream()
        self.stream.close()
