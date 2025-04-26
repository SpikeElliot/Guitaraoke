"""Provides a GUI setup window QWidget subclass."""

import os
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSignal # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import ( # pylint: disable=no-name-in-module
    QWidget, QVBoxLayout, QPushButton, QFileDialog
)
from guitaraoke.audio_streaming import LoadedAudio, AudioStreamHandler
from guitaraoke.utils import read_config

gui_config = read_config("GUI")
audio_config = read_config("Audio")

class SetupWindow(QWidget):
    """The user setup window of the GUI application."""
    send_set_practice_window_signal = pyqtSignal(AudioStreamHandler)

    def __init__(self) -> None:
        """The constructor for the SetupWindow class."""
        super().__init__()

        os.makedirs("./assets/audio", exist_ok=True)

        self.setWindowTitle("Guitaraoke")

        self.setFixedSize(gui_config["width"], gui_config["height"])

        self.widgets = self.set_components()

        self.set_connections()

        self.set_styles()

    def set_components(self) -> dict[str]:
        """Initialises all widgets and adds them to the main window."""
        # Song Information Labels
        file_browser_button = QPushButton()
        file_browser_button.setText("Select Song")

        layout = QVBoxLayout()
        layout.addWidget(
            file_browser_button,
            alignment=Qt.AlignCenter
        )
        self.setLayout(layout)

        # Container for main layout
        # container = QWidget()
        # container.setLayout(layout)
        # self.setCentralWidget(container)

        return {
            "file_browser_button": file_browser_button
        }

    def set_styles(self) -> dict[str]:
        """Sets the CSS styling of the main window and widgets."""
        with open("./assets/stylesheets/main.qss", "r", encoding="utf-8") as f:
            # Read main stylesheet and set main window style
            _style = f.read()
            self.setStyleSheet(_style)

    def set_connections(self) -> None:
        """
        Sets the connections between QObjects and their connected
        functions.
        """
        self.widgets["file_browser_button"].clicked.connect(
            self.open_file_browser
        )

    def open_file_browser(self) -> None:
        file_path = Path(QFileDialog.getOpenFileName(
            parent=self,
            caption="Select Audio File",
            directory="./assets/audio",
            filter="WAV files (*.wav)"
        )[0])
        if file_path.exists():
            self.load_audio(file_path)

    def load_audio(self, audio_path: Path) -> None:
        print(f"Loading '{audio_path}'...")
        audio = AudioStreamHandler(
            LoadedAudio(
                path=audio_path,
                title="temp",
                artist="temp"
            )
        )
        self.send_set_practice_window_signal.emit(audio)
