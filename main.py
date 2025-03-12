import sys
from audio_input import AudioInput
from PyQt5.QtCore import Qt, QTimer
from waveform_plot import WaveformPlot
from audio_playback import AudioPlayback
from utils import time_format, hex_to_rgb
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QSlider


class MainWindow(QMainWindow):
    """The main window of the GUI application."""
    def __init__(self):
        """The constructor for the MainWindow class."""
        super().__init__()

        self.WIDTH = 1440
        self.HEIGHT = 500
        self.theme_colour = "#0070DF"

        # Hard-coded for now
        self.playback = AudioPlayback( 
            path="./assets/sweetchildomine_intro_riff.wav",
            title="Sweet Child O' Mine (Intro Riff)",
            artist="Guns N' Roses"
        )
        self.input = AudioInput(self.playback)
        self.input.set_input_device(2)
        self.input.score_processed.connect(self._on_score_processed)

        self.setWindowTitle("Guitaraoke")

        self.setFixedSize(self.WIDTH, self.HEIGHT)

        self._set_components()

        self._set_styles()

    def _set_components(self):
        """Initialise all widgets and add them to the main window."""
        # Song Information Labels

        song_info_layout = QVBoxLayout()
        song_info_top_row, song_info_middle_row, song_info_bottom_row = QHBoxLayout(), QHBoxLayout(), QHBoxLayout()

        self.artist_label = QLabel()
        self.artist_label.setText(self.playback.artist)

        self.title_label = QLabel()
        self.title_label.setText(self.playback.title)

        self.duration_label = QLabel()
        self.duration_label.setText(f"<font color='{self.theme_colour}'>00:00.00</font> / {time_format(self.playback.duration)}")

        self.score_label = QLabel()
        self.score_label.setText("Score: 0")

        self.accuracy_label = QLabel()
        self.accuracy_label.setText("Accuracy: 0%")

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
            colour=hex_to_rgb(self.theme_colour)
        )
        self.waveform.draw_plot(self.playback)
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

        # Layouts
        controls_layout = QVBoxLayout()
        controls_layout_top_row = QHBoxLayout()
        controls_layout_bottom_row = QGridLayout()

        # Guitar volume label
        self.guitar_vol_label = QLabel()
        self.guitar_vol_label.setText("Guitar Volume")

        # Guitar volume slider
        self.guitar_vol_slider = QSlider(orientation=Qt.Horizontal)
        self.guitar_vol_slider.setFixedWidth(int(self.waveform.width/2))
        self.guitar_vol_slider.setRange(0, 100)
        self.guitar_vol_slider.setPageStep(5)
        self.guitar_vol_slider.setSliderPosition(100)
        self.guitar_vol_slider.valueChanged.connect(self._guitar_vol_slider_moved)

        # Guitar volume value label
        self.guitar_vol_val_label = QLabel()
        self.guitar_vol_val_label.setText("100%")

        #Buttons
        button_width = 100

        # Play button
        self.play_button = QPushButton() 
        self.play_button.setText("Play")
        self.play_button.setFixedWidth(button_width)
        self.play_button.clicked.connect(self._play_button_pressed)

        # Song count-in before playing
        self.count_in_timer = QTimer()
        self.count_in_timer.timeout.connect(self._count_in)
        
        # Pause button
        self.pause_button = QPushButton() 
        self.pause_button.setText("Pause")
        self.pause_button.hide()
        self.pause_button.setFixedWidth(button_width)
        self.pause_button.clicked.connect(self._pause_button_pressed)
        
        controls_layout_top_row.addWidget(self.guitar_vol_label, alignment=Qt.AlignRight)
        controls_layout_top_row.addSpacing(10)
        controls_layout_top_row.addWidget(self.guitar_vol_slider, alignment=Qt.AlignCenter)
        controls_layout_top_row.addSpacing(10)
        controls_layout_top_row.addWidget(self.guitar_vol_val_label, alignment=Qt.AlignLeft)

        controls_layout_bottom_row.addWidget(self.play_button, 0, 0, alignment=Qt.AlignCenter)
        controls_layout_bottom_row.addWidget(self.pause_button, 0, 0, alignment=Qt.AlignCenter)
        controls_layout_bottom_row.setHorizontalSpacing(20)
        controls_layout_bottom_row.setContentsMargins(
            int(self.WIDTH*0.05), int(self.HEIGHT*0.05),
            int(self.WIDTH*0.05), int(self.HEIGHT*0.05)
        )

        controls_layout.addLayout(controls_layout_top_row)
        controls_layout.addLayout(controls_layout_bottom_row)

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
        self.css = f"""
            QWidget {{
                background-color: rgb(255,255,255);
                color: rgb(0,0,0);
                font-size: 20px;
            }}

            QSlider::groove::horizontal {{
                background: rgb(0,0,0);
                height: 22px;
                border-radius: 10px;
            }}

            QSlider::handle::horizontal {{
                background: rgb(255,255,255);
                width: 20px;
                height: 20px;
                border-radius: 10px;
                border: 1px solid rgb(0,0,0);
            }}
            """
        self.setStyleSheet(self.css)
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
        button_stylesheet = f"""
            background-color: {self.theme_colour};
            color: rgb(255,255,255);
            border-radius: 16px;
            padding: 8px 0px;
            """
        self.play_button.setStyleSheet(button_stylesheet)
        self.pause_button.setStyleSheet(button_stylesheet)

    def _update_songpos(self):
        """Update song_duration label and playhead every 10ms."""
        # Show playhead first time play button is clicked
        if self.playhead.isHidden():
            self.playhead.show()
        
        song_pos = self.playback.get_pos()

        if self.playback.ended: # Stop time progressing when song ends
            self._pause_button_pressed()
            self.duration_label.setText(f"<font color='{self.theme_colour}'>00:00.00</font> / {time_format(self.playback.duration)}")
        else:
            self.duration_label.setText(f"<font color='{self.theme_colour}'>{time_format(song_pos)}</font> / {time_format(self.playback.duration)}")

        playhead_pos = int((song_pos / self.playback.duration) * self.waveform.width)
        self.playhead.move(playhead_pos, 0)

    def _play_button_pressed(self):
        """Start count-in timer when play button clicked."""
        self.play_button.hide()
        self.pause_button.show()
        # Set count-in timer interval to estimated beat interval of song
        self.count_in_timer.setInterval(self.playback.count_interval)
        self.playback.metronome_count = 0
        self.count_in_timer.start()
        
    def _count_in(self):
        """When count-in timer finished, start audio playback, input recording, and songpos timer."""
        if self.playback.play_count_in_metronome(self.count_in_timer):
            # Start audio playback
            self.playback.start()
            self.songpos_timer.start()
            # Start recording user input
            self.input.start()
            return
    
    def _pause_button_pressed(self):
        """Pause songpos_timer when pause button clicked."""
        self.pause_button.hide()
        self.play_button.show()

        # Reset in case pause button pressed during count-in
        if self.count_in_timer.isActive():
            self.count_in_timer.stop()
            self.playback.metronome_count = 0

        # Pause playback
        self.playback.stop()
        self.songpos_timer.stop()
        # Stop recording
        self.input.stop()

    def _waveform_pressed(self, mouseClickEvent):
        """Skip to song position relative to mouse x position in waveform plot when clicked."""
        mouse_x_pos = int(mouseClickEvent.scenePos()[0])
        mouse_button = mouseClickEvent.button()

        if mouse_button != 1: # Left click
            return
        
        if mouse_x_pos < 0: # Prevent negative pos value
            mouse_x_pos = 0
        new_song_pos = (mouse_x_pos / self.waveform.width) * self.playback.duration
        
        # Show playhead when song is skipped if play button isn't pressed
        if self.playhead.isHidden():
            self.playhead.show()

        self.playback.set_pos(new_song_pos) # Update song pos

        # Print song skip and mouse information to console (testing)
        print(f"\nSong skipped to: {time_format(new_song_pos)}")
        print("mouse_x_pos: {} | mouse_button: {}".format(mouse_x_pos, mouse_button))

        # Update playhead and time display to skipped position
        playhead_pos = int(mouse_x_pos)
        self.playhead.move(playhead_pos, 0)
        self.duration_label.setText(f"<font color='{self.theme_colour}'>{time_format(new_song_pos)}</font> / {time_format(self.playback.duration)}")

        # Case: song skipped during count-in
        if self.count_in_timer.isActive():
            # Restart count
            self.count_in_timer.stop()
            self.playback.metronome_count = 0
            self.count_in_timer.start()
            return
        elif self.playback.paused:
            return
        
        # Pause playback and recording, start a count-in
        self.playback.stop()
        self.input.stop()
        # TODO: RESET INPUT BUFFER WHEN SONG SKIPPED
        # self.input.buffer = np.zeros(self.BUFFER_SIZE)
        self.songpos_timer.stop()
        self.count_in_timer.start()
    
    def _on_score_processed(self, score_info):
        """
        Called when a new batch of recorded user input has been processed.
        Currently updates the song's score and accuracy labels with values
        received from the AudioInput's _process_recording function.

        Parameters
        ----------
        score_info : tuple of int
            The user score, number of notes hit by the user, and total number
            of notes for the current batch of compared audio.
        """
        score, notes_hit, total_notes = score_info
        
        self.playback.score_data["score"] += score
        self.playback.score_data["notes_hit"] += notes_hit
        self.playback.score_data["total_notes"] += total_notes

        if self.playback.total_notes != 0: # Avoid divide by zero error
            accuracy = (self.playback.score_data["notes_hit"]
                        /self.playback.score_data["total_notes"]) * 100
            self.playback.score_data["accuracy"] = accuracy

        self.score_label.setText(f"Score: {int(self.playback.user_score)}")
        self.accuracy_label.setText(f"Accuracy: {round(self.playback.score_data['accuracy'], 1)}%")

    def _guitar_vol_slider_moved(self, value):
        """Updates the guitar track's volume when slider moved."""
        self.playback.guitar_volume = value / 100
        self.guitar_vol_val_label.setText(f"{value}%")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()