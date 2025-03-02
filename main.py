import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from audio_load_handler import AudioLoadHandler
from audio_input_handler import AudioInputHandler
from waveform_plot import WaveformPlot
from utils import time_format


class MainWindow(QMainWindow):
    """The main window of the GUI application."""
    def __init__(self):
        """The constructor for the MainWindow class."""
        super().__init__()

        self.WIDTH = 1440
        self.HEIGHT = 500

        self.song = AudioLoadHandler(path="./separated_tracks/htdemucs_6s/sweetchildomine/guitar.wav")
        self.input = AudioInputHandler()
        self.input.score_processed.connect(self._on_score_processed)

        self.setWindowTitle("Guitaraoke")

        # self.setGeometry(0, 0, self.WIDTH, self.HEIGHT)
        self.setFixedSize(self.WIDTH, self.HEIGHT)

        self._set_components()

        self._set_styles()

    def _set_components(self):
        """Initialise all widgets and add them to the main window."""
        # Song Information Labels

        song_info_layout = QVBoxLayout()
        song_info_top_row, song_info_middle_row, song_info_bottom_row = QHBoxLayout(), QHBoxLayout(), QHBoxLayout()

        self.artist_label = QLabel()
        self.artist_label.setText(self.song.artist)

        self.title_label = QLabel()
        self.title_label.setText(self.song.title)

        self.duration_label = QLabel()
        self.duration_label.text_colour = "#462aff"
        self.duration_label.setText(f"<font color='{self.duration_label.text_colour}'>00:00.00</font> / {time_format(self.song.duration)}")

        self.score_label = QLabel()
        self.score_label.setText("Score: ?")

        self.accuracy_label = QLabel()
        self.accuracy_label.setText("Accuracy: ?%")

        self.gamemode_label = QLabel()
        self.gamemode_label.setText("PRACTICE")

        song_info_top_row.addSpacing(int(self.WIDTH*0.05))
        song_info_top_row.addWidget(self.gamemode_label, alignment=Qt.AlignLeft)
        song_info_top_row.addWidget(self.artist_label, alignment=Qt.AlignCenter)
        song_info_top_row.addWidget(self.score_label, alignment=Qt.AlignRight)
        song_info_top_row.addSpacing(int(self.WIDTH*0.05))
        
        song_info_middle_row.addSpacing(int(self.WIDTH*0.05))
        song_info_middle_row.addWidget(QLabel()) # Temporary
        song_info_middle_row.addWidget(self.title_label, alignment=Qt.AlignCenter)
        song_info_middle_row.addWidget(self.accuracy_label, alignment=Qt.AlignRight)
        song_info_middle_row.addSpacing(int(self.WIDTH*0.05))

        song_info_bottom_row.addStretch(1)
        song_info_bottom_row.addWidget(self.duration_label, alignment=Qt.AlignCenter)
        song_info_bottom_row.addStretch(1)

        song_info_layout.addLayout(song_info_top_row)
        song_info_layout.addLayout(song_info_middle_row)
        song_info_layout.addLayout(song_info_bottom_row)

        # Waveform Plot

        self.waveform = WaveformPlot(
            width=int(self.WIDTH*0.9),
            height=100,
            colour=(70,42,255)
        )
        self.waveform.draw_plot(self.song)
        self.waveform.clicked_connect(self._waveform_pressed)

        # Song playhead
        self.playhead = QWidget(self.waveform) 
        self.playhead.setFixedSize(3, self.waveform.height)
        self.playhead.hide()

        # Song time position timer
        self.songpos_timer = QTimer() 
        self.songpos_timer.setInterval(10)
        self.songpos_timer.timeout.connect(self._update_songpos)

        # Overlay playhead on waveform
        waveform_layout = QHBoxLayout(self.waveform) 
        waveform_layout.addWidget(self.playhead, alignment=Qt.AlignLeft)
        
        # Audio Playback Controls

        button_width = 100

        # Play button
        self.play_button = QPushButton() 
        self.play_button.setText("Play")
        self.play_button.setFixedWidth(button_width)
        self.play_button.clicked.connect(self._play_button_pressed)

        # Song count-in before playing
        self.count_in_timer = QTimer()
        self.count_in_timer.count_interval = int(1000 / (self.song.bpm / 60))
        # Don't set count-in timer interval yet
        self.count_in_timer.timeout.connect(self._play_count_in_metronome)
        self.count_in_timer.count = 0
        
        # Pause button
        self.pause_button = QPushButton() 
        self.pause_button.setText("Pause")
        self.pause_button.hide()
        self.pause_button.setFixedWidth(button_width)
        self.pause_button.clicked.connect(self._pause_button_pressed)
        
        # Record button (TESTING)
        self.record_button = QPushButton() 
        self.record_button.setText("Record")
        self.record_button.setFixedWidth(button_width)
        self.record_button.clicked.connect(self._record_button_pressed)
        
        # Playback controls layout
        controls_layout = QGridLayout()
        controls_layout.addWidget(self.play_button, 0, 0)
        controls_layout.addWidget(self.pause_button, 0, 0)
        controls_layout.addWidget(self.record_button, 1, 0)

        # Main Layout
        
        layout = QVBoxLayout()
        layout.addLayout(song_info_layout)
        layout.addWidget(self.waveform, alignment=Qt.AlignCenter)
        layout.addLayout(controls_layout)
        
        # Container for main layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)    

    def _set_styles(self):
        """Set the CSS styling of window and widgets."""
        # Main Window
        self.setStyleSheet(
            """
            background-color: rgb(255,255,255);
            color: rgb(0,0,0);
            font-size: 20px;
            """
        )
        # Waveform Plot
        self.waveform.setStyleSheet(
            """
            border: 2px solid rgb(0,0,0);
            border-radius: 4px;
            """
        )
        # Song Playhead
        self.playhead.setStyleSheet(
            """
            background-color: rgba(255,0,0,0.9);
            border: none;
            """
        )
        # Audio Playback Controls
        button_stylesheet = """
            background-color: rgb(70,42,255);
            color: rgb(255,255,255);
            border-radius: 16px;
            padding: 8px 0px;
            """
        self.play_button.setStyleSheet(button_stylesheet)
        self.pause_button.setStyleSheet(button_stylesheet)
        self.record_button.setStyleSheet(button_stylesheet)

    def _update_songpos(self):
        """Update song_duration label and playhead every 10ms."""
        song_pos = self.song.get_pos()
        
        if self.song.ended: # Stop time progressing when song ends
            self._pause_button_pressed()
            self.duration_label.setText(f"<font color='{self.duration_label.text_colour}'>00:00.00</font> / {time_format(self.song.duration)}")
        else:
            self.duration_label.setText(f"<font color='{self.duration_label.text_colour}'>{time_format(song_pos)}</font> / {time_format(self.song.duration)}")

        playhead_pos = int((song_pos / self.song.duration) * self.waveform.width)
        self.playhead.move(playhead_pos, 0)

        # Show playhead first time play button is clicked
        if self.playhead.isHidden():
            self.playhead.show()

    def _play_button_pressed(self):
        """Start songpos_timer when play button clicked."""
        self.play_button.hide()
        self.pause_button.show()
        self._start_count_in()
        
    def _start_count_in(self):
        """Start count-in timer before playing the song."""
        # Set an initial offset interval to align count-in with current songpos
        self.count_in_timer.offset = int(((self.song.position/self.song.RATE)*1000 + self.song.first_beat) % self.count_in_timer.count_interval)
        print("offset " + str(self.count_in_timer.offset) + "ms")
        print("normal interval " + str(self.count_in_timer.count_interval) + "ms")
        self.count_in_timer.setInterval(self.count_in_timer.count_interval)
        self.count_in_timer.count = 0
        self.count_in_timer.start()

    def _play_count_in_metronome(self):
        """
        Play the count-in metronome sound and increment self.count_in_timer.count, playing
        the song after the fourth count.
        """
        self.count_in_timer.count += 1

        # Stop timer and play song when metronome aligned to song position
        if self.count_in_timer.count > 4:
            self.count_in_timer.stop()
            self.count_in_timer.count = 0

            self.song.play()
            self.songpos_timer.start()
            return
        elif self.count_in_timer.count == 4:
            # After 4 counts, wait for metronome time alignment with song position
            self.count_in_timer.setInterval(self.count_in_timer.offset)

        self.song.play_metronome()
    
    def _pause_button_pressed(self):
        """Pause songpos_timer when pause button clicked."""
        self.pause_button.hide()
        self.play_button.show()

        # Reset in case pause button pressed during count-in
        if self.count_in_timer.isActive():
            self.count_in_timer.stop()
            self.count_in_timer.count = 0

        self.song.pause()
        self.songpos_timer.stop()

    def _record_button_pressed(self):
        """Start an audio input stream recording when record button clicked."""
        # TODO Learn to use QThreads instead
        self.input.recording = True
        self.input.start()

    def _waveform_pressed(self, mouseClickEvent):
        """Skip to song position relative to mouse x position in waveform plot when clicked."""
        mouse_x_pos = int(mouseClickEvent.scenePos()[0])
        mouse_button = mouseClickEvent.button()

        if mouse_button != 1: # Left click
            return
        
        if mouse_x_pos < 0: # Prevent negative pos value
            mouse_x_pos = 0
        new_song_pos = (mouse_x_pos / self.waveform.width) * self.song.duration
        
        # Show playhead when song is skipped if play button isn't pressed
        if self.playhead.isHidden():
            self.playhead.show()

        self.song.set_pos(new_song_pos)

        # Print song skip and mouse information to console (testing)
        print(f"\nSong skipped to: {time_format(new_song_pos)}")
        print("mouse_x_pos: {} | mouse_button: {}".format(mouse_x_pos, mouse_button))

        # Update playhead and time display to skipped position
        playhead_pos = int(mouse_x_pos)
        self.playhead.move(playhead_pos, 0)
        self.duration_label.setText(f"<font color='{self.duration_label.text_colour}'>{time_format(new_song_pos)}</font> / {time_format(self.song.duration)}")

        # Reset timer count in case song skipped during count-in
        if self.count_in_timer.isActive():
            self.count_in_timer.stop()
            self.count_in_timer.count = 0
        elif self.song.paused:
            return
        
        # Pause song and start a count-in
        self.song.pause()
        self.songpos_timer.stop()
        self._start_count_in()
    
    def _on_score_processed(self, score):
        """
        Called when a new pitch detection of user input is received.
        Currently adds the returned value from the input's process_recorded_audio
        function to the song's user score and updates the score label.

        Parameters
        ----------
        score : int
            The returned pitch accuracy score from the AudioInputHandler
            object's audio processing loop.
        """
        self.song.user_score += score
        self.score_label.setText(f"Score: {self.song.user_score}")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()