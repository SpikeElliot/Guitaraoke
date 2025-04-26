"""Provides a GUI practice mode window QWidget subclass."""

import numpy as np
from PyQt5.QtCore import Qt, QTimer # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import ( # pylint: disable=no-name-in-module
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QSlider
)
from guitaraoke.waveform_plot import WaveformPlot
from guitaraoke.playback_controls import PlaybackControls
from guitaraoke.audio_streaming import AudioStreamHandler
from guitaraoke.scoring_system import ScoringSystem
from guitaraoke.utils import time_format, hex_to_rgb, read_config

gui_config = read_config("GUI")
audio_config = read_config("Audio")

class PracticeWindow(QWidget):
    """The main window of the GUI application."""
    def __init__(
        self,
        audio: AudioStreamHandler,
        scorer: ScoringSystem
    ) -> None:
        """The constructor for the MainWindow class."""
        super().__init__()

        self.audio = audio
        self.scorer = scorer

        self.setWindowTitle("Guitaraoke")

        self.setFixedSize(gui_config["width"], gui_config["height"])

        self.widgets = self.set_components()

        self.styles = self.set_styles()

        self.controls = PlaybackControls(self.audio, self.widgets, self.styles)

        self.set_connections()

    def set_components(self) -> dict[str]:
        """Initialises all widgets and adds them to the main window."""
        # Song Information Labels

        song_info_layout = QVBoxLayout()
        song_info_top_row = QHBoxLayout()
        song_info_middle_row = QHBoxLayout()
        song_info_bottom_row = QHBoxLayout()

        artist_label = QLabel()
        artist_label.setText(
            self.audio.song.metadata["artist"]
        )

        title_label = QLabel()
        title_label.setText(
            self.audio.song.metadata["title"]
            )

        duration_label = QLabel()
        duration_label.setText(
            f"<font color='{gui_config['theme_colour']}'>00:00.00</font>"
            f" / {time_format(self.audio.song.duration)}"
        )

        score_label = QLabel()
        score_label.setText("Score: 0")

        accuracy_label = QLabel()
        accuracy_label.setText("Accuracy: 0%")

        gamemode_label = QLabel()
        gamemode_label.setText("PRACTICE")

        # Top row

        song_info_top_row.addSpacing(int(gui_config["width"]*0.05))

        song_info_top_row.addWidget(
            gamemode_label,
            alignment=Qt.AlignLeft
        )

        song_info_top_row.addWidget(
            artist_label,
            alignment=Qt.AlignCenter
        )

        song_info_top_row.addWidget(
            score_label,
            alignment=Qt.AlignRight
        )

        song_info_top_row.addSpacing(int(gui_config["width"]*0.05))

        # Middle row

        song_info_middle_row.addSpacing(int(gui_config["width"]*0.05))

        song_info_middle_row.addWidget(QLabel()) # Temporary

        song_info_middle_row.addWidget(
            title_label,
            alignment=Qt.AlignCenter
        )

        song_info_middle_row.addWidget(
            accuracy_label,
            alignment=Qt.AlignRight
        )

        song_info_middle_row.addSpacing(int(gui_config["width"]*0.05))

        # Bottom row

        song_info_bottom_row.addStretch(1)

        song_info_bottom_row.addWidget(
            duration_label,
            alignment=Qt.AlignCenter
        )

        song_info_bottom_row.addStretch(1)

        song_info_layout.addLayout(song_info_top_row)
        song_info_layout.addLayout(song_info_middle_row)
        song_info_layout.addLayout(song_info_bottom_row)

        # Waveform Plot

        waveform = WaveformPlot(
            width=int(gui_config["width"]*0.9),
            height=100,
            colour=hex_to_rgb(gui_config["theme_colour"])
        )
        waveform.setObjectName("waveform")
        waveform.draw_plot(self.audio.song)

        # Song playhead
        playhead = QWidget(waveform)
        playhead.setObjectName("playhead")
        playhead.setFixedSize(3, waveform.height-4)
        playhead.move(0, 2)
        playhead.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        # Loop overlay
        loop_overlay = QWidget(waveform)
        loop_overlay.setObjectName("loop_overlay")
        loop_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        loop_overlay.hide()

        # Left loop marker
        left_marker_img = QWidget(waveform)
        left_marker_img.setObjectName("left_marker_img")
        left_marker_img.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        left_marker_img.resize(24, 24)
        left_marker_img.hide()

        # Right loop marker
        right_marker_img = QWidget(waveform)
        right_marker_img.setObjectName("right_marker_img")
        right_marker_img.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        right_marker_img.resize(24, 24)
        right_marker_img.hide()

        # Song time position timer
        audiopos_timer = QTimer()
        audiopos_timer.setInterval(10)

        # Audio Playback Controls

        # Layouts
        controls_layout = QVBoxLayout()
        controls_layout_top_row = QHBoxLayout()
        controls_layout_bottom_row = QGridLayout()

        # Guitar volume label
        guitar_vol_label = QLabel()
        guitar_vol_label.setText("Guitar Volume")

        # Guitar volume slider
        guitar_vol_slider = QSlider(orientation=Qt.Horizontal)
        guitar_vol_slider.setToolTip("Change guitar track volume in mix.")
        guitar_vol_slider.setFixedWidth(int(waveform.width/2))
        guitar_vol_slider.setRange(0, 100)
        guitar_vol_slider.setPageStep(5)
        guitar_vol_slider.setSliderPosition(100)

        # Guitar volume value label
        guitar_vol_val_label = QLabel()
        guitar_vol_val_label.setText("100%")

        # Buttons
        button_width = 100

        # Count-in toggle button
        count_in_button = QPushButton()
        count_in_button.setObjectName("count_in_button")
        count_in_button.setText("Count-in")
        count_in_button.setToolTip("Toggle metronome count-in.")
        count_in_button.setFixedWidth(button_width)

        # Song count-in timer
        count_in_timer = QTimer()

        # Skip back button
        skip_back_button = QPushButton()
        skip_back_button.setObjectName("skip_back_button")
        skip_back_button.setText("Skip back")
        skip_back_button.setToolTip("Skip back 5 seconds.")
        skip_back_button.setFixedWidth(button_width)

        # Play button
        play_button = QPushButton()
        play_button.setObjectName("play_button")
        play_button.setText("Play")
        play_button.setToolTip("Start or resume song playback.")
        play_button.setFixedWidth(button_width)

        # Pause button
        pause_button = QPushButton()
        pause_button.setObjectName("pause_button")
        pause_button.setText("Pause")
        pause_button.setToolTip("Pause song playback.")
        pause_button.hide()
        pause_button.setFixedWidth(button_width)

        # Skip forward button
        skip_forward_button = QPushButton()
        skip_forward_button.setObjectName("skip_forward_button")
        skip_forward_button.setText("Skip forward")
        skip_forward_button.setToolTip("Skip forward 5 seconds.")
        skip_forward_button.setFixedWidth(button_width)

        # Loop toggle button
        loop_button = QPushButton()
        loop_button.setObjectName("loop_button")
        loop_button.setText("Loop")
        loop_button.setToolTip(
            "Toggle section looping.<br><br> \
            <b>shift+mouse1</b> sets the left loop marker.<br> \
            <b>shift+mouse2</b> sets the right loop marker."
        )
        loop_button.setFixedWidth(button_width)

        # Top row

        controls_layout_top_row.addWidget( # "Guitar Volume" text label
            guitar_vol_label,
            alignment=Qt.AlignRight
        )

        controls_layout_top_row.addSpacing(10)

        controls_layout_top_row.addWidget( # Guitar volume slider
            guitar_vol_slider,
            alignment=Qt.AlignCenter
        )

        controls_layout_top_row.addSpacing(10)

        controls_layout_top_row.addWidget( # Guitar volume value label
            guitar_vol_val_label,
            alignment=Qt.AlignLeft
        )

        # Bottom row

        controls_layout_bottom_row.addWidget( # Count-in button
            count_in_button,
            0, 0,
            alignment=Qt.AlignRight
        )

        controls_layout_bottom_row.addWidget( # Count-in button
            skip_back_button,
            0, 1
        )

        controls_layout_bottom_row.addWidget( # Play button
            play_button,
            0, 2
        )

        controls_layout_bottom_row.addWidget( # Pause button
            pause_button,
            0, 2
        )

        controls_layout_bottom_row.addWidget( # Count-in button
            skip_forward_button,
            0, 3
        )

        controls_layout_bottom_row.addWidget( # Loop button
            loop_button,
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
            waveform,
            alignment=Qt.AlignCenter
        )
        layout.addLayout(controls_layout)
        self.setLayout(layout)

        return {
            "artist_label": artist_label, 
            "title_label": title_label,
            "duration_label": duration_label, 
            "score_label": score_label,
            "accuracy_label": accuracy_label, 
            "gamemode_label": gamemode_label,
            "waveform": waveform, 
            "playhead": playhead,
            "loop_overlay": loop_overlay, 
            "left_marker_img": left_marker_img,
            "right_marker_img": right_marker_img, 
            "audiopos_timer": audiopos_timer,
            "guitar_vol_label": guitar_vol_label, 
            "guitar_vol_slider": guitar_vol_slider,
            "guitar_vol_val_label": guitar_vol_val_label, 
            "count_in_button": count_in_button,
            "count_in_timer": count_in_timer, 
            "skip_back_button": skip_back_button,
            "play_button": play_button, 
            "pause_button": pause_button,
            "skip_forward_button": skip_forward_button, 
            "loop_button": loop_button
        }

    def set_styles(self) -> dict[str]:
        """Sets the CSS styling of window and widgets."""
        with open("./assets/stylesheets/main.qss", "r", encoding="utf-8") as f:
            # Read main stylesheet and set main window style
            _style = f.read()
            self.setStyleSheet(_style)

        active_button_style = f"background-color: {gui_config['theme_colour']};"
        inactive_button_style = f"background-color: {gui_config['inactive_colour']};"

        active_marker_style = """
            border-image: url('./assets/images/loop_marker.png');
            background-color: transparent;
            """
        inactive_marker_style = """
            border-image: url('./assets/images/loop_marker_inactive.png');
            background-color: transparent;
            """

        return {
            "active_button": active_button_style,
            "inactive_button": inactive_button_style,
            "active_marker": active_marker_style,
            "inactive_marker": inactive_marker_style
        }

    def set_connections(self) -> None:
        """
        Sets the connections between QObjects and their connected
        functions.
        """
        self.audio.send_buffer.connect(
            self.receive_new_input_audio
        )
        self.scorer.sent_score_data.connect(
            self.receive_new_score_data
        )
        self.controls.send_reset_score_signal.connect(
            self.receive_reset_score_signal
        )
        self.widgets["waveform"].clicked_connect(
            self.controls.waveform_pressed
        )
        self.widgets["audiopos_timer"].timeout.connect(
            self.controls.update_songpos
        )
        self.widgets["guitar_vol_slider"].valueChanged.connect(
            self.controls.guitar_vol_slider_moved
        )
        self.widgets["count_in_button"].clicked.connect(
            self.controls.count_in_button_pressed
        )
        self.widgets["count_in_timer"].timeout.connect(
            self.controls.count_in
        )
        self.widgets["skip_back_button"].clicked.connect(
            self.controls.skip_back_button_pressed
        )
        self.widgets["play_button"].clicked.connect(
            self.controls.play_button_pressed
        )
        self.widgets["pause_button"].clicked.connect(
            self.controls.pause_button_pressed
        )
        self.widgets["skip_forward_button"].clicked.connect(
            self.controls.skip_forward_button_pressed
        )
        self.widgets["loop_button"].clicked.connect(
            self.controls.loop_button_pressed
        )

    def receive_reset_score_signal(self) -> None:
        """
        Resets the user score to zero when a signal is sent from the
        PlaybackControls object indicating song position has been 
        manually changed.
        """
        self.scorer.zero_score_data()

    def receive_new_input_audio(
        self,
        data: tuple[np.ndarray, int, dict[int, list]]
    ) -> None:
        """
        Schedule the process_recording method to be called when a new
        audio input buffer received.
        """
        buffer, position, pitches = data
        self.scorer.submit_process_recording(buffer, position, pitches)

    def receive_new_score_data(
        self,
        data: tuple[int, float]
    ) -> None:
        """Update GUI score information with new score data."""
        score, accuracy = data
        self.widgets["score_label"].setText(f"Score: {score}")
        self.widgets["accuracy_label"].setText(f"Accuracy: {accuracy:.1f}%")
