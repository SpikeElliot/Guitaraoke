import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import numpy as np
import audio_handling

a = audio_handling.AudioInputHandler()


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

        # Set plot axes
        wf_plot.setXRange(0, a.CHUNK, padding=0)
        wf_plot.setYRange(-1.0, 1.0, padding=0)
        self.x_vals = np.arange(0, a.CHUNK, 1)
        self.plot_data = a.data_np

        # Initial plot of waveform
        self.wf_line = wf_plot.plot(
            self.x_vals,
            self.plot_data,
            pen=pg.mkPen(color=(255, 0, 0))
        )

        # Update waveform every 10 ms
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateWaveform)
        self.timer.start(10)

        return wf_plot

    # Open new stream with updated input device index
    def changeInputDevice(self, idx):
        a.closeStream() # Close current stream before opening new one
        a.openStream(idx)
    
    # Refresh waveform plot with new data 
    def updateWaveform(self):
        self.plot_data = a.data_np # Get data from AudioInputHandler
        self.wf_line.setData(self.x_vals, self.plot_data)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()