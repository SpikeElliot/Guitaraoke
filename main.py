import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QWidget, QVBoxLayout
import pyaudio


class MainWindow(QMainWindow):
    def __init__(self, inputDevices):
        super().__init__()
        self.inputDevices = inputDevices

        self.setWindowTitle("Test App")
        self.setGeometry(0, 0, 960, 490)

        # Create a dropdown list that contains all input devices
        comboBox = QComboBox()
        for i in range(len(self.inputDevices)):
            comboBox.addItem(self.inputDevices[i])

        layout = QVBoxLayout()
        layout.addWidget(comboBox)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)


def main():
    # AUDIO PROCESSING

    # Get number of connected audio devices, then populate an array
    # with the names of every input device.
    p = pyaudio.PyAudio()
    numDevices = p.get_host_api_info_by_index(0).get('deviceCount') 
    inputDevices = []
    for i in range(numDevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            inputDevices.append(p.get_device_info_by_host_api_device_index(0, i).get('name'))

    # GRAPHICS

    app = QApplication(sys.argv)
    window = MainWindow(inputDevices)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()