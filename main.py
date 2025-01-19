import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from audio_handler import AudioHandler
from waveform_plot import WaveformPlot
from utils import timeFormat

a = AudioHandler()

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.WIDTH = 1440
        self.HEIGHT = 400

        # CSS Styling of main window
        self.setStyleSheet(
        '''
        background-color: black;
        color: white;
        font-size: 20px;
        '''
        )

        self.setWindowTitle("Test App")

        self.setGeometry(0, 0, self.WIDTH, self.HEIGHT)

        self.UiComponents()

        self.show()

    # Create and add widgets to window
    def UiComponents(self):
        self.songpos_timer = QTimer()
        self.songpos_timer.setInterval(10)
        self.songpos_timer.timeout.connect(self.update_songpos)
        
        self.song_artist = QLabel()
        self.song_artist.setText(a.artist)

        self.song_title = QLabel()
        self.song_title.setText(a.title)

        self.song_duration = QLabel()
        self.song_duration.setText(f"00:00.00 / {timeFormat(a.duration)}")

        self.play_button = QPushButton()
        self.play_button.setText("Play")
        self.play_button.clicked.connect(self.play_button_pressed)

        self.pause_button = QPushButton()
        self.pause_button.setText("Pause")
        self.pause_button.clicked.connect(self.pause_button_pressed)
        self.pause_button.hide()

        self.waveform = WaveformPlot(a).plot
        self.waveform.setMaximumHeight(100)
        
        layout = QVBoxLayout()
        layout.addWidget(self.song_artist, alignment=Qt.AlignCenter)
        layout.addWidget(self.song_title, alignment=Qt.AlignCenter)
        layout.addWidget(self.song_duration, alignment=Qt.AlignCenter)
        layout.addWidget(self.waveform)
        layout.addWidget(self.play_button)
        layout.addWidget(self.pause_button)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # Updates current song time label every 10ms
    def update_songpos(self):
        songpos = a.getPos()
        if songpos > 0:
            self.song_duration.setText(f"{timeFormat(songpos)} / {timeFormat(a.duration)}")
        else: # Stop time progressing when song ends
            self.pause_button_pressed()
            self.song_duration.setText(f"00:00.00 / {timeFormat(a.duration)}")
            a.ended = True

    # Play button action
    def play_button_pressed(self):
        self.play_button.hide()
        self.pause_button.show()
        a.play()
        self.songpos_timer.start()
    
    # Pause button action
    def pause_button_pressed(self):
        self.pause_button.hide()
        self.play_button.show()
        a.pause()
        self.songpos_timer.stop()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()