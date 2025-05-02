"""Provides a GUI setup window QWidget subclass."""

import os
from configparser import ConfigParser
from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal # pylint: disable=no-name-in-module
from PyQt6.QtWidgets import ( # pylint: disable=no-name-in-module
    QWidget, QVBoxLayout, QPushButton, QFileDialog, QComboBox, QLabel
)
from guitaraoke.audio_streaming import LoadedAudio, AudioStreamHandler
from guitaraoke.utils import read_config, find_audio_devices

gui_config = read_config("GUI")
audio_config = read_config("Audio")

class SetupWindow(QWidget):
    """The user setup window of the GUI application."""
    send_set_practice_window_signal = pyqtSignal(AudioStreamHandler)

    def __init__(self) -> None:
        """The constructor for the SetupWindow class."""
        super().__init__()

        os.makedirs("./assets/audio", exist_ok=True)

        self.in_devices = find_audio_devices()[0]

        self.widgets = self.set_components()

        self.set_connections()

        self.set_styles()

    def set_components(self) -> dict[str]:
        """Initialises all widgets and adds them to the window."""
        title_label = QLabel("Guitaraoke")
        title_label.setObjectName("app_title")

        combobox_label = QLabel("Input Device:")

        input_devices_combobox = QComboBox()
        input_devices_combobox.setFixedSize(int(gui_config["width"]*0.25), 26)
        for dev in self.in_devices:
            input_devices_combobox.addItem(dev["name"])
        input_devices_combobox.setCurrentIndex(
            audio_config["input_device_index"]
        )

        select_song_button = QPushButton()
        select_song_button.setObjectName("select_song")
        select_song_button.setText("Select Song")

        layout = QVBoxLayout()

        layout.addSpacing(int(gui_config["height"] * 0.1))

        layout.addWidget(
            title_label,
            alignment=Qt.AlignmentFlag.AlignCenter
            )

        layout.addStretch(1)

        layout.addWidget(
            combobox_label,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout.addSpacing(int(gui_config["height"] * 0.02))

        layout.addWidget(
            input_devices_combobox,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout.addStretch(2)

        layout.addWidget(
            select_song_button,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout.addSpacing(int(gui_config["height"] * 0.1))

        self.setLayout(layout)

        return {
            "title_label": title_label,
            "combobox_label": combobox_label,
            "input_devices_combobox": input_devices_combobox,
            "select_song_button": select_song_button,
        }

    def set_styles(self) -> dict[str]:
        """Sets the CSS styling of the window and widgets."""
        with open("./assets/stylesheets/main.qss", "r", encoding="utf-8") as f:
            # Read main stylesheet and set main window style
            _style = f.read()
            self.setStyleSheet(_style)

    def set_connections(self) -> None:
        """
        Sets the connections between QObjects and their connected
        functions.
        """
        self.widgets["select_song_button"].clicked.connect(
            self.open_file_browser
        )
        self.widgets["input_devices_combobox"].activated.connect(
            self.set_input_device
        )

    def open_file_browser(self) -> None:
        """
        Open the file browser when the select song button is pressed.
        """
        file_path = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select Audio File",
            directory="./assets/audio",
            filter="WAV files (*.wav)"
        )[0]
        if file_path:
            self.load_audio(Path(file_path))

    def load_audio(self, audio_path: Path) -> None:
        """
        Initialise the AudioStreamHandler used in the practice mode
        from the selected audio file path.
        """
        print(f"Loading '{audio_path}'...")
        audio = AudioStreamHandler(
            LoadedAudio(
                path=audio_path,
                title="temp",
                artist="temp"
            )
        )
        self.send_set_practice_window_signal.emit(audio)

    def set_input_device(self, idx) -> None:
        """Update config file with new input device index."""
        parser = ConfigParser()
        parser.read("config.ini")
        parser.set("Audio", "input_device_index", str(idx))
        with open("config.ini", "w", encoding="utf-8") as configfile:
            parser.write(configfile)
