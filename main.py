import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from audio_load_handler import AudioLoadHandler
from audio_stream_handler import AudioStreamHandler
from waveform_plot import WaveformPlot
from utils import time_format


song = AudioLoadHandler()
input = AudioStreamHandler()

class MainWindow(QMainWindow):
    """
    The main window of the GUI application.

    Attributes
    ----------
    WIDTH : int
        The fixed width of the window.
    HEIGHT : int
        The fixed height of the window.
    songpos_timer : QTimer
        A timer with an interval of 10ms that updates the song position
        graphics during audio playback.
    """
    def __init__(self):
        """The constructor for the MainWindow class."""
        super().__init__()

        self.WIDTH = 1440
        self.HEIGHT = 400

        # CSS Styling of main window
        self.setStyleSheet(
        """
        background-color: black;
        color: white;
        font-size: 20px;
        """
        )

        self.setWindowTitle("Test App")

        self.setGeometry(0, 0, self.WIDTH, self.HEIGHT)

        self._UI_components()

        # Create timer for song time position
        self.songpos_timer = QTimer()
        self.songpos_timer.setInterval(10)
        self.songpos_timer.timeout.connect(self._update_songpos)

    def _UI_components(self):
        """Initialise all widgets add them to the main window."""
        # SONG METADATA DISPLAY

        self.song_artist = QLabel()
        self.song_artist.setText(song.artist)

        self.song_title = QLabel()
        self.song_title.setText(song.title)

        self.song_duration = QLabel()
        self.song_duration.setText(f"00:00.00 / {time_format(song.duration)}")

        # WAVEFORM DISPLAY

        self.waveform = WaveformPlot(song).plot
        self.waveform.setMaximumHeight(100)
        self.waveform.setMinimumWidth(self.WIDTH)
        self.waveform_width = self.waveform.geometry().width()

        # Song playhead
        self.playhead = QWidget(self.waveform)
        self.playhead.setStyleSheet("background-color:red")
        self.playhead.setFixedSize(3, 100)
        self.playhead.hide()

        # Waveform layout containing song playhead
        waveform_layout = QHBoxLayout(self.waveform)
        waveform_layout.addWidget(self.playhead, alignment=Qt.AlignLeft)
        
        # AUDIO PLAYBACK CONTROLS

        self.play_button = QPushButton()
        self.play_button.setText("Play")
        self.play_button.clicked.connect(self._play_button_pressed)

        self.pause_button = QPushButton()
        self.pause_button.setText("Pause")
        self.pause_button.clicked.connect(self._pause_button_pressed)
        self.pause_button.hide()

        # RECORD BUTTON (TESTING)

        self.record_button = QPushButton()
        self.record_button.setText("Record")
        self.record_button.clicked.connect(self._record_button_pressed)

        # MAIN LAYOUT
        
        layout = QVBoxLayout()
        layout.addWidget(self.song_artist, alignment=Qt.AlignCenter)
        layout.addWidget(self.song_title, alignment=Qt.AlignCenter)
        layout.addWidget(self.song_duration, alignment=Qt.AlignCenter)
        layout.addWidget(self.waveform)
        layout.addWidget(self.play_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.record_button)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _update_songpos(self):
        """Update song_duration label and playhead every 10ms."""
        songpos = song.get_pos()
        
        if songpos > 0:
            self.song_duration.setText(f"{time_format(songpos)} / {time_format(song.duration)}")
        else: # Stop time progressing when song ends
            self.pause_button_pressed()
            self.song_duration.setText(f"00:00.00 / {time_format(song.duration)}")
            song.ended = True

        playhead_pos = int((songpos / song.duration) * self.waveform_width)
        self.playhead.move(playhead_pos, 0)

        # Show playhead first time play button is clicked (temporary solution)
        if self.playhead.isHidden():
            self.playhead.show()

    def _play_button_pressed(self):
        """Start songpos_timer when play button clicked."""
        self.play_button.hide()
        self.pause_button.show()
        song.play()
        self.songpos_timer.start()
    
    def _pause_button_pressed(self):
        """Pause songpos_timer when pause button clicked."""
        self.pause_button.hide()
        self.play_button.show()
        song.pause()
        self.songpos_timer.stop()

    def _record_button_pressed(self):
        """Start an audio input stream recording when record button clicked."""
        name = input.record()
        print(name)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()