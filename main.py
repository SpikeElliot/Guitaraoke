import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QWidget, QVBoxLayout, QPushButton
import pyaudio
import matplotlib.pyplot as plt
import numpy as np
import time

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
p = pyaudio.PyAudio()

# AUDIO PROCESSING

# Get number of connected audio devices, then populate an array
# with the names of every input device.
NUM_DEVICES = p.get_host_api_info_by_index(0).get('deviceCount') 
input_devices = []
for i in range(NUM_DEVICES):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        input_devices.append(p.get_device_info_by_host_api_device_index(0, i).get('name'))


class MainWindow(QMainWindow):
    in_dev_idx = 0

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Test App")

        self.setGeometry(0, 0, 960, 490)

        self.UiComponents()

        self.show()

    # Create widgets
    def UiComponents(self):
        # Dropdown list of input devices
        input_cbox = QComboBox()
        for i in range(len(input_devices)):
            input_cbox.addItem(input_devices[i])
        
        record_button = QPushButton()
        record_button.setText("Record")

        # Record method uses device selected from combo box
        input_cbox.activated.connect(self.changeInputDevice)
        record_button.clicked.connect(self.record)

        layout = QVBoxLayout()
        layout.addWidget(input_cbox)
        layout.addWidget(record_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # Update input device index
    def changeInputDevice(self, idx):
        self.in_dev_idx = idx
    
    # Record 5 seconds of audio from input device
    def record(self):
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            output=True,
            frames_per_buffer=CHUNK,
            input_device_index=self.in_dev_idx
        )

        # Plot the waveform

        fig, ax = plt.subplots()
        x = np.arange(0, CHUNK, 1)
        line, = ax.plot(x, np.random.rand(CHUNK))
        ax.set_ylim(-2**15, 2**15)
        ax.set_xlim(0, CHUNK)
        plt.show()

        endTime = time.time() + 5
        
        print("Recording started...")

        while time.time() < endTime:
            data = stream.read(CHUNK)
            data_np = np.frombuffer(data, dtype=np.int16)
            line.set_ydata(data_np)
            fig.canvas.draw()
            fig.canvas.flush_events()

        print("Recording stopped")

        stream.stop_stream()
        stream.close()


def main():

    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()