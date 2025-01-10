import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import numpy as np
import audio_handling

a = audio_handling.AudioInput()


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Test App")

        self.setGeometry(0, 0, 960, 490)

        self.UiComponents()

        self.show()

    # Create widgets
    def UiComponents(self):
        waveform = self.initialisePlot()
        
        # Dropdown list of input devices
        input_cbox = QComboBox()
        for i in range(len(a.input_devices)):
            input_cbox.addItem(a.input_devices[i])

        # Record method uses device selected from combo box
        input_cbox.activated.connect(self.changeInputDevice)

        layout = QVBoxLayout()
        layout.addWidget(waveform)
        layout.addWidget(input_cbox)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # Create audio input waveform plot
    def initialisePlot(self):
        wf_plot = pg.PlotWidget()

        wf_plot.setXRange(0, a.CHUNK, padding=0)
        wf_plot.setYRange(-2**15, 2**15, padding=0)
        self.x_vals = np.arange(0, a.CHUNK, 1)

        self.stream = a.openStream(0)
        data = self.stream.read(a.CHUNK)
        data_np = np.frombuffer(data, dtype=np.int16)

        self.wf_line = wf_plot.plot(
            self.x_vals,
            data_np,
            pen=pg.mkPen(color=(255, 0, 0))
        )

        # Update waveform every 10 ms
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateWaveform)
        self.timer.start(10)

        return wf_plot

    # Update input device index
    def changeInputDevice(self, idx):
        # Close current stream before opening new one
        self.stream.stop_stream()
        self.stream.close()
        self.stream = a.openStream(idx)
    
    # Update waveform plot with new data 
    def updateWaveform(self):
        data = self.stream.read(a.CHUNK)
        data_np = np.frombuffer(data, dtype=np.int16)
        self.wf_line.setData(self.x_vals, data_np)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()