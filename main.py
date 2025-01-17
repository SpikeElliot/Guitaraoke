import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from audio_handler import AudioHandler
from waveform_plot import WaveformPlot

a = AudioHandler()


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Test App")

        self.setGeometry(0, 0, 960, 490)

        self.UiComponents()

        self.show()

    # Create widgets
    def UiComponents(self):
        waveform = WaveformPlot(a).plot

        layout = QVBoxLayout()
        layout.addWidget(waveform)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()