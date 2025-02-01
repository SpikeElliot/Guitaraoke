import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from audio_handling.audio_load_handler import AudioLoadHandler
from audio_handling.audio_stream_handler import AudioStreamHandler
from plotting.waveform_plot import WaveformPlot
from utils import timeFormat

song = AudioLoadHandler()
input = AudioStreamHandler()

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

        # Create timer for song time position
        self.songpos_timer = QTimer()
        self.songpos_timer.setInterval(10)
        self.songpos_timer.timeout.connect(self.update_songpos)

    # Create and add widgets to window
    def UiComponents(self):
        
        # SONG METADATA DISPLAY

        self.song_artist = QLabel()
        self.song_artist.setText(song.artist)

        self.song_title = QLabel()
        self.song_title.setText(song.title)

        self.song_duration = QLabel()
        self.song_duration.setText(f"00:00.00 / {timeFormat(song.duration)}")

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
        self.play_button.clicked.connect(self.play_button_pressed)

        self.pause_button = QPushButton()
        self.pause_button.setText("Pause")
        self.pause_button.clicked.connect(self.pause_button_pressed)
        self.pause_button.hide()

        # MAIN LAYOUT
        
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

    # Updates current song time label and playhead every 10ms
    def update_songpos(self):
        songpos = song.getPos()
        
        if songpos > 0:
            self.song_duration.setText(f"{timeFormat(songpos)} / {timeFormat(song.duration)}")
        else: # Stop time progressing when song ends
            self.pause_button_pressed()
            self.song_duration.setText(f"00:00.00 / {timeFormat(song.duration)}")
            song.ended = True

        playhead_pos = int((songpos / song.duration) * self.waveform_width)
        self.playhead.move(playhead_pos, 0)

        # Show playhead first time play button is clicked (temporary solution)
        if self.playhead.isHidden():
            self.playhead.show()

    # Play button action
    def play_button_pressed(self):
        self.play_button.hide()
        self.pause_button.show()
        song.play()
        self.songpos_timer.start()
    
    # Pause button action
    def pause_button_pressed(self):
        self.pause_button.hide()
        self.play_button.show()
        song.pause()
        self.songpos_timer.stop()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()