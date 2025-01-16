import pyaudio
import numpy as np
import librosa


class AudioHandler():
    
    def __init__(self):
        self.CHUNK = 1024 * 2
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100

        self.frames, sr = librosa.load(path='Rift.mp3', sr=self.RATE)
        self.duration = len(self.frames) / float(sr)

        # New rate to resample loaded song to for 11025 plotted points.
        # In the Librosa documentation, this is the default maximum number
        # of points for the display.waveshow function.
        plot_sr = int(11025/self.duration)

        self.plot_frames = librosa.resample(y=self.frames, orig_sr=self.RATE, target_sr=plot_sr)
        
        # self.p = None
        # self.stream = None
        # self.data_np = None
        # self.openStream(0)

        self.input_devices = []
        # self.getNumDevices()

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
        self.data_np = np.frombuffer(data_in, dtype=np.float32)
        
        # TODO ADD AUDIO ANALYSIS FUNCTIONALITY HERE IN FUTURE
        
        return None, pyaudio.paContinue

    # Close current audio stream
    def closeStream(self):
        self.stream.stop_stream()
        self.stream.close()