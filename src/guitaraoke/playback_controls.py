"""Provides a class for GUI audio playback control functionality."""

import numpy as np
from PyQt6.QtCore import Qt, pyqtSignal, QObject # pylint: disable=no-name-in-module
from guitaraoke.audio_streaming import AudioStreamHandler
from guitaraoke.utils import time_format, read_config


class PlaybackControls(QObject):
    """
    Provides functions connected to GUI audio playback controls and
    necessary for control functionality.

    Attributes
    ----------
    send_reset_score_signal : pyqtSignal
        A signal sent to the GUI when playback position is changed
        by the user, indicating that the score should be reset.
    audio : AudioStreamHandler
        The AudioStreamHandler object containing currently-played song
        data.
    widgets : dict[str]
        The GUI widgets stored in a dictionary.
    styles : dict[str]
        The GUI widget styles stored in a dictionary.
    """
    send_reset_score_signal = pyqtSignal()

    def __init__(
        self,
        audio: AudioStreamHandler,
        widgets: dict[str],
        styles: dict[str]
    ) -> None:
        super().__init__()

        self.gui_config = read_config("GUI")
        self.audio_config = read_config("Audio")

        self.audio = audio
        self.widgets = widgets
        self.styles = styles

    def update_songpos(self) -> None:
        """Updates song_duration label and moves playhead every 10ms."""
        if self.audio.ended:
            # Stop time progressing when song ends
            self.pause_button_pressed()

            # Reset song time display to 0
            self.widgets["duration_label"].setText(
                f"<font color='{self.gui_config['theme_colour']}'>00:00.00</font>"
                f" / {time_format(self.audio.song.duration)}"
            )
        else:
            # Update the song duration label with new time
            self.widgets["duration_label"].setText(
                f"<font color='{self.gui_config['theme_colour']}'>"
                f"{time_format(self.audio.position/self.audio_config['rate'])}</font>"
                f" / {time_format(self.audio.song.duration)}"
            )
        self.update_playhead_pos()

    def update_playhead_pos(self) -> None:
        """
        Set playhead position relative to current song playback 
        position.
        """
        song_pos_in_s = self.audio.position/self.audio_config["rate"]
        head_pos = int((song_pos_in_s/self.audio.song.duration)
                        * self.widgets["waveform"].width)
        self.widgets["playhead"].move(head_pos, 2)

    def play_button_pressed(self) -> None:
        """Starts count-in timer when play button pressed."""
        self.widgets["play_button"].hide()
        self.widgets["pause_button"].show()

        # Case: song count-in is disabled
        if not self.audio.metronome["count_in_enabled"]:
            self.start_song_processes()
            return

        # Set count-in timer interval to estimated beat interval of song
        self.widgets["count_in_timer"].setInterval(self.audio.metronome["interval"])
        self.audio.metronome["count"] = 0
        self.widgets["count_in_timer"].start()

    def count_in_button_pressed(self) -> None:
        """Toggles metronome count-in when count-in button pressed."""
        self.audio.metronome["count_in_enabled"] = (
            not self.audio.metronome["count_in_enabled"])
        if self.audio.metronome["count_in_enabled"]:
            self.widgets["count_in_button"].setStyleSheet(self.styles["active_count_in_button"])
        else:
            self.widgets["count_in_button"].setStyleSheet(self.styles["inactive_count_in_button"])

    def count_in(self) -> None:
        """Starts audio processes when count-in timer finished."""
        if self.audio.play_count_in_metronome(self.widgets["count_in_timer"]):
            # Start playback and recording
            self.start_song_processes()

    def start_song_processes(self) -> None:
        "Start all I/O streaming processes."
        self.send_reset_score_signal.emit() # Send signal to GUI to reset score
        self.audio.start()
        self.widgets["audiopos_timer"].start()

    def pause_song_processes(self) -> None:
        """Stop all I/O streaming processes."""
        self.audio.stop()
        self.widgets["audiopos_timer"].stop()

    def pause_button_pressed(self) -> None:
        """Stops audio processes when pause button pressed."""
        self.widgets["pause_button"].hide()
        self.widgets["play_button"].show()

        # Case: pause button pressed during count-in timer
        if self.widgets["count_in_timer"].isActive():
            self.widgets["count_in_timer"].stop()
            self.audio.metronome["count"] = 0

        # Pause playback and recording
        self.pause_song_processes()

    def skip_forward_button_pressed(self) -> None:
        """Skips playback position a maximum of 5 seconds back."""
        # Prevent position from running over end of loop or end of song
        end = self.audio.song.duration
        if self.audio.in_loop_bounds():
            end = self.audio.loop_markers[1]/self.audio_config["rate"]
        pos_in_s = self.audio.position/self.audio_config["rate"]

        if pos_in_s + 5 < end:
            self.audio.seek(pos_in_s + 5)
        else:
            self.audio.seek(end-0.1)

        self.send_reset_score_signal.emit() # Send signal to GUI to reset score
        self.update_songpos()

    def skip_back_button_pressed(self) -> None:
        """Skips playback position a maximum of 5 seconds forward."""
        # Prevent position from falling behind start of loop or start of song
        start = 0
        if self.audio.in_loop_bounds():
            start = self.audio.loop_markers[0]/self.audio_config["rate"]
        pos_in_s = self.audio.position/self.audio_config["rate"]

        if pos_in_s - 5 > start:
            self.audio.seek(pos_in_s - 5)
        else:
            self.audio.seek(start)

        self.send_reset_score_signal.emit() # Send signal to GUI to reset score
        self.update_songpos()

    def loop_button_pressed(self) -> None:
        """
        Toggles song section looping when loop button pressed if both
        loop markers are set.
        """
        if None in self.audio.loop_markers:
            return

        self.audio.looping = not self.audio.looping
        if self.audio.looping:
            self.widgets["loop_overlay"].show()
            self.widgets["loop_button"].setStyleSheet(self.styles["active_loop_button"])
            self.widgets["left_marker_img"].setStyleSheet(self.styles["active_marker"])
            self.widgets["right_marker_img"].setStyleSheet(self.styles["active_marker"])
        else:
            self.widgets["loop_overlay"].hide()
            self.widgets["loop_button"].setStyleSheet(self.styles["inactive_loop_button"])
            self.widgets["left_marker_img"].setStyleSheet(self.styles["inactive_marker"])
            self.widgets["right_marker_img"].setStyleSheet(self.styles["inactive_marker"])

    def waveform_pressed(self, mouse_event) -> None:
        """
        Called when mouse click event signal sent by waveform plot.
        Sets a loop marker if shift button held. Otherwise, if left
        mouse pressed, skip to song position based on x pos clicked.
        """
        x_pos = np.max(int(mouse_event.scenePos()[0]), 0)
        button = mouse_event.button()
        mods = mouse_event.modifiers()

        # Case: shift button held
        if mods == Qt.KeyboardModifier.ShiftModifier:
            self.loop_marker_set(x_pos, button)
            return

        # Case: only left mouse button pressed
        if button == Qt.MouseButton.LeftButton:
            self.skip_song_position(x_pos)

    def loop_marker_set(self, x_pos: int, button) -> None:
        """
        Sets a new time position (in frames) for the left or right loop
        marker. When both markers have values set, song looping
        logic is actuated.
        """
        left_marker = self.audio.loop_markers[0]
        right_marker = self.audio.loop_markers[1]

        marker_pos = round(( # Marker time position in frames
            (x_pos/self.widgets["waveform"].width)
            * self.audio.song.duration
            * self.audio_config["rate"]
        ))
        time_constraint = 1 * self.audio_config["rate"] # Minimum loop time of 1 sec

        # Update left marker when left mouse pressed
        if button == Qt.MouseButton.LeftButton:
            if right_marker is None:
                left_marker = marker_pos
                self.widgets["left_marker_img"].move(x_pos-9, 2)
            elif np.abs(right_marker - marker_pos) >= time_constraint:
                # Invert markers if new left marker > right marker
                if marker_pos > right_marker:
                    left_marker = right_marker
                    self.widgets["left_marker_img"].move(
                        self.widgets["right_marker_img"].x(), 2
                    )

                    right_marker = marker_pos
                    self.widgets["right_marker_img"].move(x_pos-9, 2)
                else: # Otherwise, set left marker to new position
                    left_marker = marker_pos
                    self.widgets["left_marker_img"].move(x_pos-9, 2)
                self.display_looping()
            self.widgets["left_marker_img"].show() # Show marker when set

        # Update right marker when right mouse pressed
        elif button == Qt.MouseButton.RightButton:
            if left_marker is None:
                right_marker = marker_pos
                self.widgets["right_marker_img"].move(x_pos-9, 2)
            elif np.abs(marker_pos - left_marker) >= time_constraint:
                # Invert markers if new right marker < left marker
                if marker_pos < left_marker:
                    right_marker = left_marker
                    self.widgets["right_marker_img"].move(
                        self.widgets["left_marker_img"].x(), 2
                    )

                    left_marker = marker_pos
                    self.widgets["left_marker_img"].move(x_pos-9, 2)
                else: # Otherwise, set right marker to new position
                    right_marker = marker_pos
                    self.widgets["right_marker_img"].move(x_pos-9, 2)
                self.display_looping()
            self.widgets["right_marker_img"].show() # Show marker when set

        # Update playback loop markers (in frames)
        self.audio.loop_markers[0] = left_marker
        self.audio.loop_markers[1] = right_marker

        if (not None in (self.audio.loop_markers[0], self.audio.loop_markers[1])
            and not self.audio.looping):
            # Looping set to true when both markers set
            self.audio.looping = True

    def display_looping(self) -> None:
        """
        Set looping elements to active styles and display loop
        overlay.
        """
        # Set active styles for loop markers and button
        self.widgets["left_marker_img"].setStyleSheet(self.styles["active_marker"])
        self.widgets["right_marker_img"].setStyleSheet(self.styles["active_marker"])
        self.widgets["loop_button"].setStyleSheet(self.styles["active_loop_button"])

        # Show the loop overlay widget when its area has been created by
        # the left and right markers
        left_x = self.widgets["left_marker_img"].x() + 9
        right_x = self.widgets["right_marker_img"].x() + 9
        self.widgets["loop_overlay"].move(left_x, 2)
        self.widgets["loop_overlay"].resize(
            np.abs(right_x - left_x), self.widgets["waveform"].height - 3
        )
        self.widgets["loop_overlay"].show()

    def skip_song_position(self, x_pos: int) -> None:
        """
        Skips to song position based on x position of left-click
        on waveform plot.
        """
        self.widgets["playhead"].move(x_pos, 2) # Update playhead x position

        song_pos = (x_pos/self.widgets["waveform"].width) * self.audio.song.duration
        self.audio.seek(song_pos) # Update song time position
        self.send_reset_score_signal.emit() # Send signal to GUI to reset score

        self.widgets["duration_label"].setText( # Update song time display
            f"<font color='{self.gui_config['theme_colour']}'>{time_format(song_pos)}</font>"
            f" / {time_format(self.audio.song.duration)}"
        )

        print(f"\nSong skipped to: {time_format(song_pos)}") # Testing

        # Case: song count-in is disabled
        if not self.audio.metronome["count_in_enabled"]:
            return

        # Case: song skipped during count-in
        if self.widgets["count_in_timer"].isActive():
            # Restart count
            self.widgets["count_in_timer"].stop()
            self.audio.metronome["count"] = 0
            self.widgets["count_in_timer"].start()
            return
        if self.audio.paused:
            return

        # Case: song skipped mid-playback
        self.pause_song_processes()
        self.widgets["count_in_timer"].start()

    def guitar_vol_slider_moved(self, value: int) -> None:
        """Updates the song's guitar_volume from new slider value."""
        self.audio.guitar_volume = value/100
        self.widgets["guitar_vol_val_label"].setText(f"{value}%")
