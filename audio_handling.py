import pyaudio


class AudioInput():
    p = pyaudio.PyAudio()
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    input_devices = []
    
    def __init__(self):
        super().__init__()
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
            stream = self.p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                output=True,
                frames_per_buffer=self.CHUNK,
                input_device_index=idx
            )
            return stream