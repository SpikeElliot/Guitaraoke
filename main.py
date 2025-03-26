import sys
import numpy as np
from PyQt5.QtCore import Qt, QTimer
from guitaraoke.audio_input import AudioInput
from guitaraoke.waveform_plot import WaveformPlot
from guitaraoke.audio_playback import AudioPlayback
from guitaraoke.utils import time_format, hex_to_rgb
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QSlider


class MainWindow(QMainWindow):
    """The main window of the GUI application."""
    def __init__(self) -> None:
        """The constructor for the MainWindow class."""
        super().__init__()

        self.WIDTH, self.HEIGHT = 1440, 500
        self.theme_colour = "#0070df"
        self.inactive_colour = "#4e759c"

        # Hard-coded for now
        self.playback = AudioPlayback()
        self.playback.load(
            path="./assets/audio/sweetchildomine_intro_riff.wav",
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

    def _set_components(self) -> None:
        """Initialises all widgets and adds them to the main window."""
        # Song Information Labels

        song_info_layout = QVBoxLayout()
        song_info_top_row = QHBoxLayout()
        song_info_middle_row = QHBoxLayout()
        song_info_bottom_row = QHBoxLayout()

        self.artist_label = QLabel()
        self.artist_label.setText(self.playback.artist)

        self.title_label = QLabel()
        self.title_label.setText(self.playback.title)

        self.duration_label = QLabel()
        self.duration_label.setText(
            f"<font color='{self.theme_colour}'>00:00.00</font>"
            f" / {time_format(self.playback.duration)}"
        )

        self.score_label = QLabel()
        self.score_label.setText("Score: 0")

        self.accuracy_label = QLabel()
        self.accuracy_label.setText("Accuracy: 0%")

        self.gamemode_label = QLabel()
        self.gamemode_label.setText("PRACTICE")

        # Top row

        song_info_top_row.addSpacing(int(self.WIDTH*0.05))

        song_info_top_row.addWidget(
            self.gamemode_label, 
            alignment=Qt.AlignLeft
        )

        song_info_top_row.addWidget(
            self.artist_label, 
            alignment=Qt.AlignCenter
        )

        song_info_top_row.addWidget(
            self.score_label, 
            alignment=Qt.AlignRight
        )

        song_info_top_row.addSpacing(int(self.WIDTH*0.05))

        # Middle row
        
        song_info_middle_row.addSpacing(int(self.WIDTH*0.05))

        song_info_middle_row.addWidget(QLabel()) # Temporary

        song_info_middle_row.addWidget(
            self.title_label, 
            alignment=Qt.AlignCenter
        )

        song_info_middle_row.addWidget(
            self.accuracy_label, 
            alignment=Qt.AlignRight
        )

        song_info_middle_row.addSpacing(int(self.WIDTH*0.05))

        # Bottom row

        song_info_bottom_row.addStretch(1)

        song_info_bottom_row.addWidget(
            self.duration_label, 
            alignment=Qt.AlignCenter
        )

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
        self.waveform.setObjectName("waveform")
        self.waveform.draw_plot(self.playback)
        self.waveform.clicked_connect(self._waveform_pressed)

        # Song playhead
        self.playhead = QWidget(self.waveform)
        self.playhead.setObjectName("playhead")
        self.playhead.setFixedSize(3, self.waveform.height)
        self.playhead.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.playhead.hide()

        self.loop_window = QWidget(self.waveform)
        self.loop_window.setObjectName("loop_window")
        self.loop_window.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.loop_window.hide()

        # Song time position timer
        self.songpos_timer = QTimer() 
        self.songpos_timer.setInterval(10)
        self.songpos_timer.timeout.connect(self._update_songpos)

        # Overlay playhead on waveform
        waveform_layout = QHBoxLayout(self.waveform) 
        waveform_layout.addWidget(
            self.playhead, 
            alignment=Qt.AlignLeft
        )
        
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
        self.guitar_vol_slider.valueChanged.connect(
            self._guitar_vol_slider_moved
        )

        # Guitar volume value label
        self.guitar_vol_val_label = QLabel()
        self.guitar_vol_val_label.setText("100%")

        # Buttons
        button_width = 100

        # Count-in toggle button
        self.count_in_button = QPushButton()
        self.count_in_button.setObjectName("count_in_button")
        self.count_in_button.setText("Count-in")
        self.count_in_button.setFixedWidth(button_width)
        self.count_in_button.clicked.connect(self._count_in_button_pressed)

        # Song count-in timer
        self.count_in_timer = QTimer()
        self.count_in_timer.timeout.connect(self._count_in)

        # Skip back button
        self.skip_back_button = QPushButton() 
        self.skip_back_button.setObjectName("skip_back_button")
        self.skip_back_button.setText("Skip back")
        self.skip_back_button.setFixedWidth(button_width)
        self.skip_back_button.clicked.connect(self._skip_back_button_pressed)

        # Play button
        self.play_button = QPushButton() 
        self.play_button.setObjectName("play_button")
        self.play_button.setText("Play")
        self.play_button.setFixedWidth(button_width)
        self.play_button.clicked.connect(self._play_button_pressed)
        
        # Pause button
        self.pause_button = QPushButton() 
        self.pause_button.setObjectName("pause_button")
        self.pause_button.setText("Pause")
        self.pause_button.hide()
        self.pause_button.setFixedWidth(button_width)
        self.pause_button.clicked.connect(self._pause_button_pressed)

        # Skip forward button
        self.skip_forward_button = QPushButton() 
        self.skip_forward_button.setObjectName("skip_forward_button")
        self.skip_forward_button.setText("Skip forward")
        self.skip_forward_button.setFixedWidth(button_width)
        self.skip_forward_button.clicked.connect(self._skip_forward_button_pressed)

        # Loop toggle button
        self.loop_button = QPushButton()
        self.loop_button.setObjectName("loop_button")
        self.loop_button.setText("Loop")
        self.loop_button.setFixedWidth(button_width)
        self.loop_button.clicked.connect(self._loop_button_pressed)
        
        # Top row

        controls_layout_top_row.addWidget( # "Guitar Volume" text label
            self.guitar_vol_label, 
            alignment=Qt.AlignRight
        )

        controls_layout_top_row.addSpacing(10)

        controls_layout_top_row.addWidget( # Guitar volume slider
            self.guitar_vol_slider, 
            alignment=Qt.AlignCenter
        )

        controls_layout_top_row.addSpacing(10)

        controls_layout_top_row.addWidget( # Guitar volume value label
            self.guitar_vol_val_label, 
            alignment=Qt.AlignLeft
        )

        # Bottom row

        controls_layout_bottom_row.addWidget( # Count-in button
            self.count_in_button, 
            0, 0, 
            alignment=Qt.AlignRight
        )

        controls_layout_bottom_row.addWidget( # Count-in button
            self.skip_back_button, 
            0, 1
        )

        controls_layout_bottom_row.addWidget( # Play button
            self.play_button, 
            0, 2
        )

        controls_layout_bottom_row.addWidget( # Pause button
            self.pause_button, 
            0, 2
        )

        controls_layout_bottom_row.addWidget( # Count-in button
            self.skip_forward_button, 
            0, 3
        )

        controls_layout_bottom_row.addWidget( # Loop button
            self.loop_button, 
            0, 4, 
            alignment=Qt.AlignLeft
        )

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
        layout.addWidget(
            self.waveform, 
            alignment=Qt.AlignCenter
        )
        layout.addLayout(controls_layout)
        
        # Container for main layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)    

    def _set_styles(self) -> None:
        """Sets the CSS styling of window and widgets."""
        with open("./assets/stylesheets/main.qss", "r") as f:
            # Read main stylesheet and set main window style
            _style = f.read()
            self.setStyleSheet(_style)

        self.active_button_style = f"background-color: {self.theme_colour};"
        self.inactive_button_style = f"background-color: {self.inactive_colour};"

    def _update_songpos(self) -> None:
        """Updates song_duration label and moves playhead every 10ms."""
        # Show playhead first time play button is clicked
        if self.playhead.isHidden(): self.playhead.show()

        if self.playback.ended: 
            # Stop time progressing when song ends
            self._pause_button_pressed()

            # Reset song time display to 0
            self.duration_label.setText( 
                f"<font color='{self.theme_colour}'>00:00.00</font>"
                f" / {time_format(self.playback.duration)}"
            ) 
        else:
            # Update the song duration label with new time
            self.duration_label.setText( 
                f"<font color='{self.theme_colour}'>"
                f"{time_format(self.playback.get_pos())}</font>"
                f" / {time_format(self.playback.duration)}"
            )

        self._update_playhead_pos()
    
    def _update_playhead_pos(self) -> None:
        song_pos = self.playback.get_pos()
        head_pos = int((song_pos/self.playback.duration)
                        * self.waveform.width)
        self.playhead.move(head_pos, 0)

    def _play_button_pressed(self) -> None:
        """Starts count-in timer when play button pressed."""
        self.play_button.hide()
        self.pause_button.show()

        # Case: song count-in is disabled
        if not self.playback.count_in: return self._start_song_processes()

        # Set count-in timer interval to estimated beat interval of song
        self.count_in_timer.setInterval(self.playback.count_interval)
        self.playback.metronome_count = 0
        self.count_in_timer.start()
    
    def _count_in_button_pressed(self) -> None:
        self.playback.count_in = not self.playback.count_in
        if self.playback.count_in:
            self.count_in_button.setStyleSheet(self.active_button_style)
        else:
            self.count_in_button.setStyleSheet(self.inactive_button_style)
        
    def _count_in(self) -> None:
        """Starts audio playback and recording when count-in timer finished."""
        if self.playback.play_count_in_metronome(self.count_in_timer):
            # Start playback and recording
            self._start_song_processes()
            
    def _start_song_processes(self) -> None:
        self.playback.start()
        self.input.start()
        self.songpos_timer.start()

    def _pause_song_processes(self) -> None:
        self.playback.stop()
        self.input.stop()
        self.songpos_timer.stop()
    
    def _pause_button_pressed(self) -> None:
        """Stops audio playback and recording when pause button pressed."""
        self.pause_button.hide()
        self.play_button.show()

        # Case: pause button pressed during count-in timer
        if self.count_in_timer.isActive():
            self.count_in_timer.stop()
            self.playback.metronome_count = 0

        # Pause playback and recording
        self._pause_song_processes()

    def _skip_forward_button_pressed(self) -> None:
        # Prevent position from running over end of loop or end of song
        end = self.playback.duration
        if self.playback.in_loop_bounds():
            end = self.playback.loop_markers[1]/self.playback.RATE
        pos_in_s = self.playback.position/self.playback.RATE

        if pos_in_s + 5 < end:
            self.playback.set_pos(pos_in_s + 5)
        else:
            self.playback.set_pos(end-0.1)

        if self.playhead.isHidden(): self.playhead.show()
        self._update_songpos()

    def _skip_back_button_pressed(self) -> None:
        # Prevent position from falling behind start of loop or start of song
        start = 0
        if self.playback.in_loop_bounds():
            start = self.playback.loop_markers[0]/self.playback.RATE
        pos_in_s = self.playback.position/self.playback.RATE

        if pos_in_s - 5 > start:
            self.playback.set_pos(pos_in_s - 5)
        else:
            self.playback.set_pos(start)

        if self.playhead.isHidden(): self.playhead.show()
        self._update_songpos()

    def _loop_button_pressed(self) -> None:
        """
        Toggles song section looping when loop button pressed if both loop
        markers are set.
        """
        if None in self.playback.loop_markers: return
        
        self.playback.looping = not self.playback.looping
        if self.playback.looping:
            self.loop_window.show()
            self.loop_button.setStyleSheet(self.active_button_style)
        else:
            self.loop_window.hide()
            self.loop_button.setStyleSheet(self.inactive_button_style)

    def _waveform_pressed(self, mouseClickEvent) -> None:
        """
        Method called when mouse click event signal sent by waveform plot.
        Sets a loop marker if shift button held, otherwise if left mouse button
        pressed, skip to song position based on x position clicked.
        """
        x_pos = np.max(int(mouseClickEvent.scenePos()[0]), 0)
        button = mouseClickEvent.button()
        mods = mouseClickEvent.modifiers()

        # Case: shift button held
        if mods == Qt.ShiftModifier: return self._loop_marker_set(x_pos, button)

        # Case: only left mouse button pressed
        if button == 1: self._skip_song_position(x_pos) 

    def _loop_marker_set(self, x_pos: int, button: int) -> None:
        """
        Sets a new time position (in frames) for the left or right loop marker.
        When both markers have values set, song looping logic is actuated.
        """
        left_marker = self.playback.loop_markers[0]
        right_marker = self.playback.loop_markers[1]

        marker_pos = int(( # Marker time position in frames
            (x_pos/self.waveform.width)
            * self.playback.RATE
            * self.playback.duration
        ))
        time_constraint = 2 * self.playback.RATE # Minimum loop time of 2 secs

        # Update left marker when left mouse pressed
        if button == 1:
            if right_marker is None : left_marker = marker_pos
            elif np.abs(right_marker - marker_pos) >= time_constraint:
                # Invert markers if new left marker > right marker
                if marker_pos > right_marker:
                    left_marker = right_marker
                    right_marker = marker_pos
                # Otherwise, set left marker to new position
                else:
                    left_marker = marker_pos
                self.playback.looping = True
                self.loop_button.setStyleSheet(self.active_button_style)
        # Update right marker when right mouse pressed
        elif button == 2:
            if left_marker is None : right_marker = marker_pos
            elif np.abs(marker_pos - left_marker) >= time_constraint:
                # Invert markers if new right marker < left marker
                if marker_pos < left_marker:
                    right_marker = left_marker
                    left_marker = marker_pos
                # Otherwise, set right marker to new position
                else:
                    right_marker = marker_pos
                self.playback.looping = True
                self.loop_button.setStyleSheet(self.active_button_style)

        if left_marker is not None:
            left_marker_in_s = left_marker/self.playback.RATE
        if right_marker is not None:
            right_marker_in_s = right_marker/self.playback.RATE

        if self.playback.looping:
            # Get loop marker x positions
            left_x_pos = int(((left_marker_in_s/self.playback.duration)
                                * self.waveform.width))
            right_x_pos = int(((right_marker_in_s/self.playback.duration)
                                * self.waveform.width))
            
            # Show the loop window widget when its area has been created by
            # the left and right markers
            self.loop_window.move(left_x_pos, 0)
            loop_window_width = np.abs(right_x_pos - left_x_pos)
            self.loop_window.resize(loop_window_width, 100)
            self.loop_window.show()
            
        # Update playback loop markers (in frames)
        self.playback.loop_markers[0] = left_marker
        self.playback.loop_markers[1] = right_marker

        # Print song loop markers to console (testing)
        if left_marker is not None:
            print(f"\nLeft marker: {time_format(left_marker_in_s)}")
        if right_marker is not None:
            print(f"Right marker: {time_format(right_marker_in_s)}")

    def _skip_song_position(self, x_pos: int) -> None:
        """Skips to song position based on x-pos of left-click on waveform plot."""
        if self.playhead.isHidden(): self.playhead.show()

        self.playhead.move(x_pos, 0) # Update playhead x position

        song_pos = ((x_pos/self.waveform.width) * self.playback.duration)
        self.playback.set_pos(song_pos) # Update song time position

        self.duration_label.setText( # Update song time display
            f"<font color='{self.theme_colour}'>{time_format(song_pos)}</font>"
            f" / {time_format(self.playback.duration)}"
        ) 

        print(f"\nSong skipped to: {time_format(song_pos)}") # Testing

        # Case: song count-in is disabled
        if not self.playback.count_in: return

        # Case: song skipped during count-in
        if self.count_in_timer.isActive():
            # Restart count
            self.count_in_timer.stop()
            self.playback.metronome_count = 0
            self.count_in_timer.start()
            return
        elif self.playback.paused : return

        # Case: song skipped mid-playback
        self._pause_song_processes()
        self.count_in_timer.start()
    
    def _on_score_processed(self, score_info: tuple[int, int]) -> None:
        """
        Method called when the next input recording has been processed. Updates
        the AudioPlayback's score_data and the GUI's labels with new values.
        """
        score, notes_hit, total_notes = score_info
        
        self.playback.score_data["score"] += score
        self.playback.score_data["notes_hit"] += notes_hit
        self.playback.score_data["total_notes"] += total_notes

        if self.playback.score_data["total_notes"] != 0: # Avoid div by 0 error
            accuracy = (self.playback.score_data["notes_hit"]
                        /self.playback.score_data["total_notes"]) * 100
            new_acc = self.playback.score_data["accuracy"] = accuracy

        self.score_label.setText(f"Score: {self.playback.score_data['score']}")
        self.accuracy_label.setText(f"Accuracy: {round(new_acc, 1)}%")

    def _guitar_vol_slider_moved(self, value: int) -> None:
        """Updates the AudioPlayback's guitar_volume based on new slider value."""
        self.playback.guitar_volume = value / 100
        self.guitar_vol_val_label.setText(f"{value}%")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()