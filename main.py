import sys
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer, QThread
from audio_load_handler import AudioLoadHandler
from audio_input_handler import AudioInputHandler
from waveform_plot import WaveformPlot
from utils import time_format


song = AudioLoadHandler(path="./assets/sweetchildomine.wav")
input = AudioInputHandler()

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
        self.HEIGHT = 500

        # CSS Styling of main window
        self.setStyleSheet(
        """
        background-color: rgb(255,255,255);
        color: rgb(0,0,0);
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
        # SONG INFORMATION DISPLAY

        song_info_layout = QGridLayout()

        self.song_artist = QLabel()
        self.song_artist.setText(song.artist)

        self.song_title = QLabel()
        self.song_title.setText(song.title)

        self.song_duration = QLabel()
        self.song_duration_color = "#462aff"
        self.song_duration.setText(f"<font color='{self.song_duration_color}'>00:00.00</font> / {time_format(song.duration)}")

        song_info_layout.addWidget(self.song_artist, 0, 0, alignment=Qt.AlignCenter)
        song_info_layout.addWidget(self.song_title, 1, 0, alignment=Qt.AlignCenter)
        song_info_layout.addWidget(self.song_duration, 2, 0, alignment=Qt.AlignCenter)

        # WAVEFORM DISPLAY

        self.waveform = WaveformPlot(
            audio=song,
            width=int(self.WIDTH*0.9),
            height=100
        )
        # Allow detection of mouse click events
        self.waveform.clicked_connect(self._waveform_pressed)
        self.waveform.setStyleSheet(
            """
            border: 2px solid rgb(0,0,0);
            border-radius: 4px;
            """
        )

        # Song playhead
        self.playhead = QWidget(self.waveform)
        self.playhead.setFixedSize(3, self.waveform.height)
        self.playhead.hide()
        self.playhead.setStyleSheet(
            """
            background-color: rgb(255,0,0);
            border: none;
            """
        )

        # Waveform layout containing song playhead
        waveform_layout = QHBoxLayout(self.waveform)
        waveform_layout.addWidget(self.playhead, alignment=Qt.AlignLeft)
        
        # AUDIO PLAYBACK CONTROLS

        button_stylesheet = """
        background-color: rgb(70,42,255);
        color: rgb(255,255,255);
        border-radius: 16px;
        padding: 8px 0px;
        """

        button_width = 100
        self.play_button = QPushButton()
        self.play_button.setText("Play")
        self.play_button.clicked.connect(self._play_button_pressed)
        self.play_button.setFixedWidth(button_width)
        self.play_button.setStyleSheet(button_stylesheet)

        self.pause_button = QPushButton()
        self.pause_button.setText("Pause")
        self.pause_button.clicked.connect(self._pause_button_pressed)
        self.pause_button.hide()
        self.pause_button.setFixedWidth(button_width)
        self.pause_button.setStyleSheet(button_stylesheet)

        # Record button (TESTING)
        self.record_button = QPushButton()
        self.record_button.setText("Record")
        self.record_button.clicked.connect(self._record_button_pressed)
        self.record_button.setFixedWidth(button_width)
        self.record_button.setStyleSheet(button_stylesheet)

        controls_layout = QGridLayout()
        controls_layout.addWidget(self.play_button, 0, 0)
        controls_layout.addWidget(self.pause_button, 0, 0)
        controls_layout.addWidget(self.record_button, 1, 0)

        # MAIN LAYOUT
        
        layout = QVBoxLayout()
        layout.addLayout(song_info_layout)
        layout.addWidget(self.waveform, alignment=Qt.AlignCenter)
        layout.addLayout(controls_layout)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _update_songpos(self):
        """Update song_duration label and playhead every 10ms."""
        song_pos = song.get_pos()
        
        if song.ended: # Stop time progressing when song ends
            self._pause_button_pressed()
            self.song_duration.setText(f"<font color='{self.song_duration_color}'>00:00.00</font> / {time_format(song.duration)}")
        else:
            self.song_duration.setText(f"<font color='{self.song_duration_color}'>{time_format(song_pos)}</font> / {time_format(song.duration)}")

        playhead_pos = int((song_pos / song.duration) * self.waveform.width)
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
        # TODO Learn to use QThreads instead
        threading.Thread(target=input.record_process_loop).start()

    def _waveform_pressed(self, mouseClickEvent):
        """Skip to song position relative to mouse x position in waveform plot when clicked."""
        mouse_x_pos = int(mouseClickEvent.scenePos()[0])
        mouse_button = mouseClickEvent.button()

        if mouse_button != 1 or mouse_x_pos > self.waveform.width:
            return
        
        if mouse_x_pos < 0: # Prevent negative pos value
            mouse_x_pos = 0
        new_song_pos = (mouse_x_pos / self.waveform.width) * song.duration
        
        song.set_pos(new_song_pos)
        print(f"Song skipped to: {time_format(new_song_pos)}")
        print("x pos: {} button: {}".format(mouse_x_pos, mouse_button))

        # Update playhead and time display to skipped position
        playhead_pos = int(mouse_x_pos)
        self.playhead.move(playhead_pos, 0)
        self.song_duration.setText(f"<font color='{self.song_duration_color}'>{time_format(new_song_pos)}</font> / {time_format(song.duration)}")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()