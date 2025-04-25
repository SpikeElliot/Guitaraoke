"""The main file of the application."""

import sys
import numpy as np
from PyQt5.QtCore import Qt, QTimer # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import ( # pylint: disable=no-name-in-module
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QSlider
)
from guitaraoke.waveform_plot import WaveformPlot
from guitaraoke.audio_streaming import AudioStreamHandler, LoadedAudio
from guitaraoke.scoring_system import ScoringSystem
from guitaraoke.utils import time_format, hex_to_rgb, read_config

gui_config = read_config("GUI")
audio_config = read_config("Audio")

class MainWindow(QMainWindow):
    """The main window of the GUI application."""
    def __init__(self) -> None:
        """The constructor for the MainWindow class."""
        super().__init__()

        # Hard-coded for now
        self.audio = AudioStreamHandler(
            LoadedAudio(
                path="./assets/audio/sweetchildomine_intro_riff.wav",
                title="Sweet Child O' Mine (Intro Riff)",
                artist="Guns N' Roses"
            )
        )
        self.audio.send_buffer.connect(self._receive_new_input_audio)

        self.scorer = ScoringSystem()
        self.scorer.sent_score_data.connect(self._receive_new_score_data)

        self.setWindowTitle("Guitaraoke")

        self.setFixedSize(gui_config["width"], gui_config["height"])

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
        self.artist_label.setText(
            self.audio.song.metadata["artist"]
        )

        self.title_label = QLabel()
        self.title_label.setText(
            self.audio.song.metadata["title"]
            )

        self.duration_label = QLabel()
        self.duration_label.setText(
            f"<font color='{gui_config['theme_colour']}'>00:00.00</font>"
            f" / {time_format(self.audio.song.duration)}"
        )

        self.score_label = QLabel()
        self.score_label.setText("Score: 0")

        self.accuracy_label = QLabel()
        self.accuracy_label.setText("Accuracy: 0%")

        self.gamemode_label = QLabel()
        self.gamemode_label.setText("PRACTICE")

        # Top row

        song_info_top_row.addSpacing(int(gui_config["width"]*0.05))

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

        song_info_top_row.addSpacing(int(gui_config["width"]*0.05))

        # Middle row

        song_info_middle_row.addSpacing(int(gui_config["width"]*0.05))

        song_info_middle_row.addWidget(QLabel()) # Temporary

        song_info_middle_row.addWidget(
            self.title_label,
            alignment=Qt.AlignCenter
        )

        song_info_middle_row.addWidget(
            self.accuracy_label,
            alignment=Qt.AlignRight
        )

        song_info_middle_row.addSpacing(int(gui_config["width"]*0.05))

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
            width=int(gui_config["width"]*0.9),
            height=100,
            colour=hex_to_rgb(gui_config["theme_colour"])
        )
        self.waveform.setObjectName("waveform")
        self.waveform.draw_plot(self.audio.song)
        self.waveform.clicked_connect(self._waveform_pressed)

        # Song playhead
        self.playhead = QWidget(self.waveform)
        self.playhead.setObjectName("playhead")
        self.playhead.setFixedSize(3, self.waveform.height-4)
        self.playhead.move(0, 2)
        self.playhead.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        # Loop overlay
        self.loop_overlay = QWidget(self.waveform)
        self.loop_overlay.setObjectName("loop_overlay")
        self.loop_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.loop_overlay.hide()

        # Left loop marker
        self.left_marker_img = QWidget(self.waveform)
        self.left_marker_img.setObjectName("left_marker_img")
        self.left_marker_img.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.left_marker_img.resize(24, 24)
        self.left_marker_img.hide()

        # Right loop marker
        self.right_marker_img = QWidget(self.waveform)
        self.right_marker_img.setObjectName("right_marker_img")
        self.right_marker_img.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.right_marker_img.resize(24, 24)
        self.right_marker_img.hide()

        # Song time position timer
        self.audiopos_timer = QTimer()
        self.audiopos_timer.setInterval(10)
        self.audiopos_timer.timeout.connect(self._update_songpos)

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
        self.guitar_vol_slider.setToolTip("Change guitar track volume in mix.")
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
        self.count_in_button.setToolTip("Toggle metronome count-in.")
        self.count_in_button.setFixedWidth(button_width)
        self.count_in_button.clicked.connect(self._count_in_button_pressed)

        # Song count-in timer
        self.count_in_timer = QTimer()
        self.count_in_timer.timeout.connect(self._count_in)

        # Skip back button
        self.skip_back_button = QPushButton()
        self.skip_back_button.setObjectName("skip_back_button")
        self.skip_back_button.setText("Skip back")
        self.skip_back_button.setToolTip("Skip back 5 seconds.")
        self.skip_back_button.setFixedWidth(button_width)
        self.skip_back_button.clicked.connect(self._skip_back_button_pressed)

        # Play button
        self.play_button = QPushButton()
        self.play_button.setObjectName("play_button")
        self.play_button.setText("Play")
        self.play_button.setToolTip("Start or resume song playback.")
        self.play_button.setFixedWidth(button_width)
        self.play_button.clicked.connect(self._play_button_pressed)

        # Pause button
        self.pause_button = QPushButton()
        self.pause_button.setObjectName("pause_button")
        self.pause_button.setText("Pause")
        self.pause_button.setToolTip("Pause song playback.")
        self.pause_button.hide()
        self.pause_button.setFixedWidth(button_width)
        self.pause_button.clicked.connect(self._pause_button_pressed)

        # Skip forward button
        self.skip_forward_button = QPushButton()
        self.skip_forward_button.setObjectName("skip_forward_button")
        self.skip_forward_button.setText("Skip forward")
        self.skip_forward_button.setToolTip("Skip forward 5 seconds.")
        self.skip_forward_button.setFixedWidth(button_width)
        self.skip_forward_button.clicked.connect(self._skip_forward_button_pressed)

        # Loop toggle button
        self.loop_button = QPushButton()
        self.loop_button.setObjectName("loop_button")
        self.loop_button.setText("Loop")
        self.loop_button.setToolTip(
            "Toggle section looping.<br><br> \
            <b>shift+mouse1</b> sets the left loop marker.<br> \
            <b>shift+mouse2</b> sets the right loop marker."
        )
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
            int(gui_config["width"]*0.05), int(gui_config["height"]*0.05),
            int(gui_config["width"]*0.05), int(gui_config["height"]*0.05)
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
        with open("./assets/stylesheets/main.qss", "r", encoding="utf-8") as f:
            # Read main stylesheet and set main window style
            _style = f.read()
            self.setStyleSheet(_style)

        self.active_button_style = f"background-color: {gui_config['theme_colour']};"
        self.inactive_button_style = f"background-color: {gui_config['inactive_colour']};"

        self.active_marker_style = """
            border-image: url('./assets/images/loop_marker.png');
            background-color: transparent;
            """
        self.inactive_marker_style = """
            border-image: url('./assets/images/loop_marker_inactive.png');
            background-color: transparent;
            """

    def _update_songpos(self) -> None:
        """Updates song_duration label and moves playhead every 10ms."""
        if self.audio.ended:
            # Stop time progressing when song ends
            self._pause_button_pressed()

            # Reset song time display to 0
            self.duration_label.setText(
                f"<font color='{gui_config['theme_colour']}'>00:00.00</font>"
                f" / {time_format(self.audio.song.duration)}"
            )
        else:
            # Update the song duration label with new time
            self.duration_label.setText(
                f"<font color='{gui_config['theme_colour']}'>"
                f"{time_format(self.audio.position/audio_config['rate'])}</font>"
                f" / {time_format(self.audio.song.duration)}"
            )
        self._update_playhead_pos()

    def _update_playhead_pos(self) -> None:
        """
        Set playhead position relative to current song playback 
        position.
        """
        song_pos_in_s = self.audio.position/audio_config["rate"]
        head_pos = int((song_pos_in_s/self.audio.song.duration)
                        * self.waveform.width)
        self.playhead.move(head_pos, 2)

    def _play_button_pressed(self) -> None:
        """Starts count-in timer when play button pressed."""
        self.play_button.hide()
        self.pause_button.show()

        # Case: song count-in is disabled
        if not self.audio.metronome["count_in_enabled"]:
            self._start_song_processes()
            return

        # Set count-in timer interval to estimated beat interval of song
        self.count_in_timer.setInterval(self.audio.metronome["interval"])
        self.audio.metronome["count"] = 0
        self.count_in_timer.start()

    def _count_in_button_pressed(self) -> None:
        """Toggles metronome count-in when count-in button pressed."""
        self.audio.metronome["count_in_enabled"] = (
            not self.audio.metronome["count_in_enabled"])
        if self.audio.metronome["count_in_enabled"]:
            self.count_in_button.setStyleSheet(self.active_button_style)
        else:
            self.count_in_button.setStyleSheet(self.inactive_button_style)

    def _count_in(self) -> None:
        """Starts audio processes when count-in timer finished."""
        if self.audio.play_count_in_metronome(self.count_in_timer):
            # Start playback and recording
            self._start_song_processes()

    def _start_song_processes(self) -> None:
        "Start all I/O streaming processes."
        self.scorer.zero_score_data()
        self.audio.start()
        self.audiopos_timer.start()

    def _pause_song_processes(self) -> None:
        """Stop all I/O streaming processes."""
        self.audio.stop()
        self.audiopos_timer.stop()

    def _pause_button_pressed(self) -> None:
        """Stops audio processes when pause button pressed."""
        self.pause_button.hide()
        self.play_button.show()

        # Case: pause button pressed during count-in timer
        if self.count_in_timer.isActive():
            self.count_in_timer.stop()
            self.audio.metronome["count"] = 0

        # Pause playback and recording
        self._pause_song_processes()

    def _skip_forward_button_pressed(self) -> None:
        """Skips playback position a maximum of 5 seconds back."""
        # Prevent position from running over end of loop or end of song
        end = self.audio.song.duration
        if self.audio.in_loop_bounds():
            end = self.audio.loop_markers[1]/audio_config["rate"]
        pos_in_s = self.audio.position/audio_config["rate"]

        if pos_in_s + 5 < end:
            self.audio.seek(pos_in_s + 5)
        else:
            self.audio.seek(end-0.1)

        self._update_songpos()

    def _skip_back_button_pressed(self) -> None:
        """Skips playback position a maximum of 5 seconds forward."""
        # Prevent position from falling behind start of loop or start of song
        start = 0
        if self.audio.in_loop_bounds():
            start = self.audio.loop_markers[0]/audio_config["rate"]
        pos_in_s = self.audio.position/audio_config["rate"]

        if pos_in_s - 5 > start:
            self.audio.seek(pos_in_s - 5)
        else:
            self.audio.seek(start)

        self._update_songpos()

    def _loop_button_pressed(self) -> None:
        """
        Toggles song section looping when loop button pressed if both
        loop markers are set.
        """
        if None in self.audio.loop_markers:
            return

        self.audio.looping = not self.audio.looping
        if self.audio.looping:
            self.loop_overlay.show()
            self.loop_button.setStyleSheet(self.active_button_style)
            self.left_marker_img.setStyleSheet(self.active_marker_style)
            self.right_marker_img.setStyleSheet(self.active_marker_style)
        else:
            self.loop_overlay.hide()
            self.loop_button.setStyleSheet(self.inactive_button_style)
            self.left_marker_img.setStyleSheet(self.inactive_marker_style)
            self.right_marker_img.setStyleSheet(self.inactive_marker_style)

    def _waveform_pressed(self, mouse_event) -> None:
        """
        Called when mouse click event signal sent by waveform plot.
        Sets a loop marker if shift button held. Otherwise, if left
        mouse pressed, skip to song position based on x pos clicked.
        """
        x_pos = np.max(int(mouse_event.scenePos()[0]), 0)
        button = mouse_event.button()
        mods = mouse_event.modifiers()

        # Case: shift button held
        if mods == Qt.ShiftModifier:
            self._loop_marker_set(x_pos, button)
            return

        # Case: only left mouse button pressed
        if button == 1:
            self._skip_song_position(x_pos)

    def _loop_marker_set(self, x_pos: int, button: int) -> None:
        """
        Sets a new time position (in frames) for the left or right loop
        marker. When both markers have values set, song looping
        logic is actuated.
        """
        left_marker = self.audio.loop_markers[0]
        right_marker = self.audio.loop_markers[1]

        marker_pos = round(( # Marker time position in frames
            (x_pos/self.waveform.width)
            * self.audio.song.duration
            * audio_config["rate"]
        ))
        time_constraint = 2 * audio_config["rate"] # Minimum loop time of 2 secs

        # Update left marker when left mouse pressed
        if button == 1:
            if right_marker is None:
                left_marker = marker_pos
                self.left_marker_img.move(x_pos-12, 2)
            elif np.abs(right_marker - marker_pos) >= time_constraint:
                # Looping set to true when both markers set
                self.audio.looping = True
                # Invert markers if new left marker > right marker
                if marker_pos > right_marker:
                    left_marker = right_marker
                    self.left_marker_img.move(self.right_marker_img.x(), 2)

                    right_marker = marker_pos
                    self.right_marker_img.move(x_pos-12, 2)
                else: # Otherwise, set left marker to new position
                    left_marker = marker_pos
                    self.left_marker_img.move(x_pos-12, 2)
            self.left_marker_img.show() # Show marker when set

        # Update right marker when right mouse pressed
        elif button == 2:
            if left_marker is None:
                right_marker = marker_pos
                self.right_marker_img.move(x_pos-12, 2)
            elif np.abs(marker_pos - left_marker) >= time_constraint:
                # Looping set to true when both markers set
                self.audio.looping = True
                # Invert markers if new right marker < left marker
                if marker_pos < left_marker:
                    right_marker = left_marker
                    self.right_marker_img.move(self.left_marker_img.x(), 2)

                    left_marker = marker_pos
                    self.left_marker_img.move(x_pos-12, 2)
                else: # Otherwise, set right marker to new position
                    right_marker = marker_pos
                    self.right_marker_img.move(x_pos-12, 2)
            self.right_marker_img.show() # Show marker when set

        if self.audio.looping:
            self._display_looping()

        # Update playback loop markers (in frames)
        self.audio.loop_markers[0] = left_marker
        self.audio.loop_markers[1] = right_marker

    def _display_looping(self) -> None:
        """
        Set looping elements to active styles and display loop
        overlay.
        """
        # Set active styles for loop markers and button
        self.left_marker_img.setStyleSheet(self.active_marker_style)
        self.right_marker_img.setStyleSheet(self.active_marker_style)
        self.loop_button.setStyleSheet(self.active_button_style)

        # Show the loop overlay widget when its area has been created by
        # the left and right markers
        left_x, right_x = self.left_marker_img.x()+12, self.right_marker_img.x()+12
        self.loop_overlay.move(left_x, 2)
        self.loop_overlay.resize(np.abs(right_x - left_x), self.waveform.height-4)
        self.loop_overlay.show()

    def _skip_song_position(self, x_pos: int) -> None:
        """
        Skips to song position based on x position of left-click
        on waveform plot.
        """
        self.playhead.move(x_pos, 2) # Update playhead x position

        song_pos = (x_pos/self.waveform.width) * self.audio.song.duration
        self.audio.seek(song_pos) # Update song time position
        self.scorer.zero_score_data()

        self.duration_label.setText( # Update song time display
            f"<font color='{gui_config['theme_colour']}'>{time_format(song_pos)}</font>"
            f" / {time_format(self.audio.song.duration)}"
        )

        print(f"\nSong skipped to: {time_format(song_pos)}") # Testing

        # Case: song count-in is disabled
        if not self.audio.metronome["count_in_enabled"]:
            return

        # Case: song skipped during count-in
        if self.count_in_timer.isActive():
            # Restart count
            self.count_in_timer.stop()
            self.audio.metronome["count"] = 0
            self.count_in_timer.start()
            return
        if self.audio.paused:
            return

        # Case: song skipped mid-playback
        self._pause_song_processes()
        self.count_in_timer.start()

    def _guitar_vol_slider_moved(self, value: int) -> None:
        """Updates the song's guitar_volume from new slider value."""
        self.audio.guitar_volume = value/100
        self.guitar_vol_val_label.setText(f"{value}%")

    def _receive_new_input_audio(
        self,
        data: tuple[np.ndarray, int, dict[int, list]]
    ) -> None:
        """
        Schedule the process_recording method to be called when a new
        audio input buffer received.
        """
        buffer, position, pitches = data
        self.scorer.submit_process_recording(buffer, position, pitches)

    def _receive_new_score_data(
        self,
        data: tuple[int, float]
    ) -> None:
        """Update GUI score information with new score data."""
        score, accuracy = data
        self.score_label.setText(f"Score: {score}")
        self.accuracy_label.setText(f"Accuracy: {accuracy:.1f}%")


def main() -> None:
    """Run the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app_exec(app, window))


def app_exec(app: QApplication, window: MainWindow) -> None:
    """End all processes when the application's window is closed."""
    app.exec()
    window.scorer.shutdown_processes()


if __name__ == "__main__":
    main()
