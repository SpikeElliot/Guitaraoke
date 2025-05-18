"""Provides a GUI practice mode window QWidget subclass."""

import time
import numpy as np
from PyQt6.QtCore import Qt, QTimer, pyqtSignal # pylint: disable=no-name-in-module
from PyQt6.QtWidgets import ( # pylint: disable=no-name-in-module
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QSlider
)
from guitaraoke.waveform_plot import WaveformPlot
from guitaraoke.playback_controls import PlaybackControls
from guitaraoke.audio_streaming import AudioStreamHandler
from guitaraoke.scoring_system import ScoringSystem
from guitaraoke.utils import time_format, hex_to_rgb, read_config


class PracticeWindow(QWidget):
    """The main window of the GUI application."""
    back_button_pressed_signal = pyqtSignal()

    def __init__(
        self,
        audio: AudioStreamHandler,
        scorer: ScoringSystem
    ) -> None:
        """The constructor for the PracticeWindow class."""
        super().__init__()

        self.gui_config = read_config("GUI")

        self.audio = audio
        self.scorer = scorer
        self.perf_time_start = None

        self.widgets = self.set_components()

        self.styles = self.set_styles()

        self.controls = PlaybackControls(self.audio, self.widgets, self.styles)

        self.set_connections()

    def set_components(self) -> dict[str]:
        """Initialises all widgets and adds them to the window."""
        # Song Information Labels

        song_info_layout = QHBoxLayout()
        song_info_col1 = QVBoxLayout()
        song_info_col2 = QVBoxLayout()
        song_info_col3 = QVBoxLayout()
        song_info_col4 = QVBoxLayout()

        # Column 1

        prev_accuracy_label = QLabel()
        prev_accuracy_label.setFixedWidth(int(self.gui_config["min_width"]*0.2))
        prev_accuracy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prev_accuracy_label.setText(
            f"Prev. Accuracy <font color='{self.gui_config['theme_colour']}'>N/A</font>"
        )

        prev_score_label = QLabel()
        prev_score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prev_score_label.setText(
            f"Prev. Score <font color='{self.gui_config['theme_colour']}'>N/A</font>"
        )

        swing_label = QLabel()
        swing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Layout

        song_info_col1.addWidget(
            prev_accuracy_label,
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        song_info_col1.addStretch()
        song_info_col1.addWidget(
            prev_score_label,
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        song_info_col1.addStretch()
        song_info_col1.addWidget(
            swing_label,
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        song_info_col1.addSpacing(int(self.gui_config["min_height"]*0.05))

        # Column 2

        accuracy_label = QLabel()
        accuracy_label.setFixedWidth(int(self.gui_config["min_width"]*0.3))
        accuracy_label.setObjectName("accuracy_label")
        accuracy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        accuracy_label.setText(
            f"Accuracy <font color='{self.gui_config['theme_colour']}'>0.0%    </font>"
        )

        score_label = QLabel()
        score_label.setObjectName("score_label")
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_label.setText(
            f"Score <font color='{self.gui_config['theme_colour']}'>0</font>"
        )

        duration_label = QLabel()
        duration_label.setObjectName("duration_label")
        duration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        duration_label.setText(
            f"<font color='{self.gui_config['theme_colour']}'>00:00.00</font>"
            f" / {time_format(self.audio.song.duration)}"
        )

        # Layout

        song_info_col2.addWidget(
            accuracy_label,
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        song_info_col2.addStretch()
        song_info_col2.addWidget(
            score_label,
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        song_info_col2.addStretch()
        song_info_col2.addWidget(
            duration_label,
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        song_info_col2.addSpacing(int(self.gui_config["min_height"]*0.05))

        # Column 3

        gamemode_label = QLabel()
        gamemode_label.setFixedWidth(int(self.gui_config["min_width"]*0.25))
        gamemode_label.setObjectName("gamemode_label")
        gamemode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gamemode_label.setText("Practice Mode")

        artist_label = QLabel()
        artist_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        artist_label.setText(
            f"<font color='{self.gui_config['theme_colour']}'>{self.audio.song.metadata['artist']}"
        )

        title_label = QLabel()
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setText(
            f"<font color='{self.gui_config['theme_colour']}'>{self.audio.song.metadata['title']}"
        )

        # Layout

        song_info_col3.addWidget(
            gamemode_label,
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        song_info_col3.addStretch()
        song_info_col3.addWidget(
            artist_label,
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        song_info_col3.addStretch()
        song_info_col3.addWidget(
            title_label,
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        song_info_col3.addSpacing(int(self.gui_config["min_height"]*0.05))

        # Column 4

        back_button = QPushButton()
        back_button.setObjectName("back_button")
        back_button.setToolTip("Back to song select menu")
        back_button.setFixedSize(
            int(self.gui_config["min_width"]*0.022),
            int(self.gui_config["min_width"]*0.022)
        )

        col4_positioner_element = QWidget()
        col4_positioner_element.setFixedSize(int(self.gui_config["min_width"]*0.05), 0)

        # Layout

        song_info_col4.addWidget(
            back_button,
            alignment=Qt.AlignmentFlag.AlignRight
        )
        song_info_col4.addWidget(
            col4_positioner_element,
            alignment=Qt.AlignmentFlag.AlignTop
        )
        song_info_col4.addStretch()

        # All Columns Layout

        song_info_layout.addSpacing(int(self.gui_config["min_width"]*0.15))
        song_info_layout.addLayout(song_info_col1)
        song_info_layout.addStretch()
        song_info_layout.addLayout(song_info_col2)
        song_info_layout.addStretch()
        song_info_layout.addLayout(song_info_col3)
        song_info_layout.addStretch()
        song_info_layout.addLayout(song_info_col4)
        song_info_layout.addSpacing(int(self.gui_config["min_width"]*0.05))

        # Waveform Plot

        waveform = WaveformPlot(
            width=int(self.gui_config["min_width"]*0.9),
            height=int(self.gui_config["min_height"]*0.2),
            colour=hex_to_rgb(self.gui_config["theme_colour"])
        )
        waveform.setObjectName("waveform")
        waveform.draw_plot(self.audio.song)

        # Song playhead
        playhead = QWidget(waveform)
        playhead.setObjectName("playhead")
        playhead.setFixedSize(3, waveform.height-4)
        playhead.move(0, 2)
        playhead.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )

        # Loop overlay
        loop_overlay = QWidget(waveform)
        loop_overlay.setObjectName("loop_overlay")
        loop_overlay.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )
        loop_overlay.hide()

        # Left loop marker
        left_marker_img = QWidget(waveform)
        left_marker_img.setObjectName("left_marker_img")
        left_marker_img.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )
        left_marker_img.resize(
            int(self.gui_config["min_width"]*0.017),
            int(self.gui_config["min_width"]*0.017)
        )
        left_marker_img.hide()

        # Right loop marker
        right_marker_img = QWidget(waveform)
        right_marker_img.setObjectName("right_marker_img")
        right_marker_img.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )
        right_marker_img.resize(
            int(self.gui_config["min_width"]*0.017),
            int(self.gui_config["min_width"]*0.017)
        )
        right_marker_img.hide()

        # Song time position timer
        audiopos_timer = QTimer()
        audiopos_timer.setInterval(10)

        # Audio Playback Controls

        # Guitar volume label
        guitar_vol_label = QLabel()
        guitar_vol_label.setObjectName("guitar_vol_label")
        guitar_vol_label.setText("Guitar Track")

        # Volume symbol
        volume_image = QWidget()
        volume_image.setObjectName("volume_image")
        volume_image.setFixedSize(
            int(self.gui_config["min_width"]*0.017),
            int(self.gui_config["min_width"]*0.017)
        )

        # Guitar volume slider
        guitar_vol_slider = QSlider(orientation=Qt.Orientation.Horizontal)
        guitar_vol_slider.setObjectName("guitar_vol_slider")
        guitar_vol_slider.setToolTip("Change guitar track volume in mix.")
        guitar_vol_slider.setFixedWidth(int(self.gui_config["min_width"]*0.278))
        guitar_vol_slider.setRange(0, 100)
        guitar_vol_slider.setPageStep(5)
        guitar_vol_slider.setSliderPosition(100)

        # Guitar volume value label
        guitar_vol_val_label = QLabel()
        guitar_vol_val_label.setObjectName("guitar_vol_val_label")
        guitar_vol_val_label.setText("100%")

        # Buttons
        button_width = int(self.gui_config["min_width"]*0.05)
        button_height = int(self.gui_config["min_height"]*0.11)

        # Count-in toggle button
        count_in_button = QPushButton()
        count_in_button.setObjectName("count_in_button")
        count_in_button.setToolTip("Toggle metronome count-in.")
        count_in_button.setFixedSize(button_width, button_height)

        # Song count-in timer
        count_in_timer = QTimer()

        # Skip back button
        skip_back_button = QPushButton()
        skip_back_button.setObjectName("skip_back_button")
        skip_back_button.setToolTip("Skip back 5 seconds.")
        skip_back_button.setFixedSize(button_width, button_height)

        # Play button
        play_button = QPushButton()
        play_button.setObjectName("play_button")
        play_button.setToolTip("Start or resume song playback.")
        play_button.setFixedSize(button_width, button_height)

        # Pause button
        pause_button = QPushButton()
        pause_button.setObjectName("pause_button")
        pause_button.setToolTip("Pause song playback.")
        pause_button.hide()
        pause_button.setFixedSize(button_width, button_height)

        # Skip forward button
        skip_forward_button = QPushButton()
        skip_forward_button.setObjectName("skip_forward_button")
        skip_forward_button.setToolTip("Skip forward 5 seconds.")
        skip_forward_button.setFixedSize(button_width, button_height)

        # Loop toggle button
        loop_button = QPushButton()
        loop_button.setObjectName("loop_button")
        loop_button.setToolTip(
            "Toggle section looping.<br><br> \
            <b>shift+mouse1</b> sets the left loop marker.<br> \
            <b>shift+mouse2</b> sets the right loop marker."
        )
        loop_button.setFixedSize(button_width, button_height)

        # Layouts
        controls_layout = QVBoxLayout()
        controls_layout_top_row = QHBoxLayout()
        controls_layout_bottom_row = QGridLayout()

        # Top row

        controls_layout_top_row.addWidget( # "Guitar Volume" text label
            guitar_vol_label,
            alignment=Qt.AlignmentFlag.AlignRight
        )

        controls_layout_top_row.addWidget(volume_image) # Volume symbol

        controls_layout_top_row.addWidget( # Guitar volume slider
            guitar_vol_slider,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        controls_layout_top_row.addWidget( # Guitar volume value label
            guitar_vol_val_label,
            alignment=Qt.AlignmentFlag.AlignLeft
        )

        controls_layout_top_row.addSpacing(int(self.gui_config["min_width"]*0.021))

        # Bottom row

        controls_layout_bottom_row.addWidget( # Count-in button
            count_in_button,
            0, 0,
            alignment=Qt.AlignmentFlag.AlignRight
        )

        controls_layout_bottom_row.addWidget( # Skip back button
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

        controls_layout_bottom_row.addWidget( # Skip forward button
            skip_forward_button,
            0, 3
        )

        controls_layout_bottom_row.addWidget( # Loop button
            loop_button,
            0, 4,
            alignment=Qt.AlignmentFlag.AlignLeft
        )

        controls_layout_bottom_row.setHorizontalSpacing(0)
        controls_layout_bottom_row.setContentsMargins(
            int(self.gui_config["min_width"]*0.05), int(self.gui_config["min_height"]*0.05),
            int(self.gui_config["min_width"]*0.05), int(self.gui_config["min_height"]*0.05)
        )

        controls_layout.addLayout(controls_layout_top_row)
        controls_layout.addLayout(controls_layout_bottom_row)

        # Main Layout

        layout = QVBoxLayout()
        layout.addSpacing(int(self.gui_config["min_height"]*0.05))
        layout.addLayout(song_info_layout)
        layout.addWidget(
            waveform,
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        layout.addSpacing(int(self.gui_config["min_height"]*0.05))
        layout.addLayout(controls_layout)
        self.setLayout(layout)

        return {
            "prev_accuracy_label": prev_accuracy_label,
            "prev_score_label": prev_score_label,
            "swing_label": swing_label,
            "artist_label": artist_label, 
            "title_label": title_label,
            "duration_label": duration_label, 
            "score_label": score_label,
            "accuracy_label": accuracy_label,
            "gamemode_label": gamemode_label,
            "back_button": back_button,
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
        """Create active and inactive styles for widgets."""

        active_loop_button_style = """
            border-image: url('images:loop_button.png');
            background-color: transparent;
            """
        inactive_loop_button_style = """
            border-image: url('images:loop_button_inactive.png');
            background-color: transparent;
            """

        active_count_in_button_style = """
            border-image: url('images:count_in_button.png');
            background-color: transparent;
            """
        inactive_count_in_button_style = """
            border-image: url('images:count_in_button_inactive.png');
            background-color: transparent;
            """

        active_marker_style = """
            border-image: url('images:loop_marker.png');
            background-color: transparent;
            """
        inactive_marker_style = """
            border-image: url('images:loop_marker_inactive.png');
            background-color: transparent;
            """

        return {
            "active_loop_button": active_loop_button_style,
            "inactive_loop_button": inactive_loop_button_style,
            "active_count_in_button": active_count_in_button_style,
            "inactive_count_in_button": inactive_count_in_button_style,
            "active_marker": active_marker_style,
            "inactive_marker": inactive_marker_style
        }

    def set_connections(self) -> None:
        """
        Sets the connections between QObjects and their connected
        functions.
        """
        self.audio.new_input_buffer_signal.connect(
            self.receive_new_input_audio
        )
        self.scorer.new_score_data_signal.connect(
            self.receive_new_score_data
        )
        self.controls.reset_score_signal.connect(
            self.receive_reset_score_signal
        )
        self.widgets["back_button"].clicked.connect(
            self.back_button_pressed_signal.emit
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
        Resets user score data to zero when a signal is sent from the
        PlaybackControls object indicating song position has been 
        manually changed.
        """
        # Set accuracy and score labels to zero
        self.widgets["accuracy_label"].setText(
            f"Accuracy <font color='{self.gui_config['theme_colour']}'>0.0%    </font>"
        )
        self.widgets["score_label"].setText(
            f"Score <font color='{self.gui_config['theme_colour']}'>0</font>"
        )
        # Set prev. labels to current vals before resetting
        if self.scorer.score > 0:
            self.widgets["prev_accuracy_label"].setText(
                (f"Prev. Accuracy <font color='{self.gui_config['theme_colour']}'>"
                + f"{self.scorer.accuracy:.1f}%</font>")
            )
            self.widgets["prev_score_label"].setText(
                (f"Prev. Score <font color='{self.gui_config['theme_colour']}'>"
                + f"{self.scorer.score}</font>")
            )
        self.widgets["swing_label"].setText("")
        self.scorer.zero_score_data()

    def receive_new_input_audio(
        self,
        data: tuple[np.ndarray, int, dict[int, list], float]
    ) -> None:
        """
        Schedule the process_recording method to be called when a new
        audio input buffer is received.
        """
        buffer, position, notes, self.perf_time_start = data
        self.scorer.submit_process_recording(buffer, position, notes)

    def receive_new_score_data(
        self,
        data: tuple[int, float, float]
    ) -> None:
        """Update GUI score information with new score data."""
        score, accuracy, swing = data

        perf_time_end = time.perf_counter()
        print(f"\033[92mElapsed scoring time: {perf_time_end-self.perf_time_start}\033[0m")

        self.widgets["score_label"].setText(
            f"Score <font color='{self.gui_config['theme_colour']}'>{score}</font>"
        )
        self.widgets["accuracy_label"].setText(
            f"Accuracy <font color='{self.gui_config['theme_colour']}'>{accuracy:.1f}%    </font>"
        )

        swing *= 1000 # In ms
        swing_label_text = ""
        if -10 <= swing <= 10:
            if self.scorer.score > 0:
                swing_label_text = "<font color='#0da000'>On time!</font>"
        elif swing < -10:
            swing_label_text = f"Rushing by <font color='#ff0000'>~{round(-swing)}ms</font>"
        else:
            swing_label_text = f"Dragging by <font color='#ff0000'>~{round(swing)}ms</font>"
        self.widgets["swing_label"].setText(swing_label_text)
        self.widgets["swing_label"].show()
