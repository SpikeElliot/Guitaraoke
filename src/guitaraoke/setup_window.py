"""Provides a GUI setup window QWidget subclass."""

import os
import csv
from configparser import ConfigParser
from PyQt6.QtCore import Qt, pyqtSignal # pylint: disable=no-name-in-module
from PyQt6.QtWidgets import ( # pylint: disable=no-name-in-module
    QWidget, QDialog, QDialogButtonBox, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QComboBox, QFormLayout, QLineEdit, QGroupBox, QHBoxLayout
)
from guitaraoke.audio_streaming import LoadedAudio, AudioStreamHandler # pylint: disable=no-name-in-module
from guitaraoke.utils import read_config, find_audio_devices

gui_config = read_config("GUI")
audio_config = read_config("Audio")
dir_config = read_config("Directories")

class PopupWindow(QDialog):
    """
    A popup window that appears if a selected song does not have any
    saved data.
    """
    send_set_song_data = pyqtSignal(tuple)
    def __init__(self):
        """The constructor for the PopupWindow class."""
        super().__init__()

        self.setWindowTitle("Guitaraoke")
        self.setFixedSize(400, 200)

        self.widgets = self.set_components()

        self.set_styles()

    def set_components(self) -> None:
        """Initialises all widgets and adds them to the window."""
        form_group_box = QGroupBox("Set a song title and artist:")
        artist_line_edit = QLineEdit()
        title_line_edit = QLineEdit()

        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addRow(QLabel("Title"), title_line_edit)
        form_layout.addRow(QLabel("Artist"), artist_line_edit)
        form_group_box.setLayout(form_layout)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.form_accepted)
        button_box.rejected.connect(self.form_rejected)

        layout = QVBoxLayout()
        layout.addWidget(form_group_box, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(button_box, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        return {
            "form_group_box": form_group_box,
            "title_line_edit": title_line_edit,
            "artist_line_edit": artist_line_edit,
            "button_box": button_box
        }

    def set_styles(self) -> dict[str]:
        """Sets the CSS styling of the window and widgets."""
        with open(f"{dir_config['assets_dir']}/stylesheets/main.qss", "r", encoding="utf-8") as f:
            # Read main stylesheet and set main window style
            _style = f.read()
            self.setStyleSheet(_style)

    def form_accepted(self) -> None:
        """Send new title and artist to the setup window."""
        title = self.widgets["title_line_edit"].text()
        artist = self.widgets["artist_line_edit"].text()
        self.close()
        self.send_set_song_data.emit((title, artist))

    def form_rejected(self) -> None:
        """Close popup window."""
        self.close()


class SetupWindow(QWidget):
    """The user setup window of the GUI application."""
    send_set_practice_window_signal = pyqtSignal(AudioStreamHandler)

    def __init__(self) -> None:
        """The constructor for the SetupWindow class."""
        super().__init__()
        self.popup_window = None
        self.song_filepath = None

        os.makedirs("songs", exist_ok=True)

        self.in_devices = find_audio_devices()[0]

        self.widgets = self.set_components()

        self.set_connections()

    def set_components(self) -> dict[str]:
        """Initialises all widgets and adds them to the window."""
        title_label = QLabel("Guitaraoke")
        title_label.setObjectName("setupscreen_title")

        logo = QWidget()
        logo.setObjectName("setupscreen_icon")
        logo.setFixedSize(36, 36)

        combobox_label = QLabel("Input Device:")

        input_devices_combobox = QComboBox()
        input_devices_combobox.setFixedSize(int(gui_config["min_width"]*0.25), 30)
        for dev in self.in_devices:
            input_devices_combobox.addItem(dev["name"])
        input_devices_combobox.setCurrentIndex(
            audio_config["input_device_index"]
        )

        select_song_button = QPushButton()
        select_song_button.setObjectName("select_song")
        select_song_button.setText("Select Song")

        layout = QVBoxLayout()

        layout.addSpacing(int(gui_config["min_height"] * 0.1))

        logo_layout = QHBoxLayout()

        logo_layout.addStretch()

        logo_layout.addWidget(
            logo,
            alignment=Qt.AlignmentFlag.AlignRight
        )

        logo_layout.addWidget(
            title_label,
            alignment=Qt.AlignmentFlag.AlignLeft
            )

        logo_layout.addStretch()

        layout.addLayout(logo_layout)

        layout.addStretch(1)

        layout.addWidget(
            combobox_label,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout.addSpacing(int(gui_config["min_height"] * 0.02))

        layout.addWidget(
            input_devices_combobox,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout.addStretch(2)

        layout.addWidget(
            select_song_button,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout.addSpacing(int(gui_config["min_height"] * 0.1))

        self.setLayout(layout)

        return {
            "title_label": title_label,
            "combobox_label": combobox_label,
            "input_devices_combobox": input_devices_combobox,
            "select_song_button": select_song_button,
        }

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
            directory="songs",
            filter="WAV files (*.wav)"
        )[0]
        if not file_path:
            return

        title, artist = None, None
        self.song_filepath = file_path
        with open(f"{dir_config['data_dir']}/saved_songs.csv", "r", encoding="utf-8") as data:
            for song in csv.DictReader(data):
                if song["path"] == self.song_filepath:
                    title, artist = song["title"], song["artist"]
                    break

        # Check the song's artist and title already saved
        if not None in (title, artist):
            self.load_audio(title, artist)
        else:
            # Open popup window that allows the user to set the values
            self.create_popup_window()

    def create_popup_window(self) -> None:
        """
        Spawn a popup window when the user selects a song that has
        no saved data.
        """
        self.popup_window = PopupWindow()
        self.popup_window.show()
        self.popup_window.send_set_song_data.connect(self.save_song_data)

    def save_song_data(self, data: tuple[str, str]) -> None:
        """
        Write the submitted song title and artist from the popup
        window to the saved_songs CSV file.
        """
        title, artist = data
        with open(f"{dir_config['data_dir']}/saved_songs.csv", "a", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["path", "title", "artist"])
            writer.writerow(
                {"path": self.song_filepath, "title": title, "artist": artist}
            )
        self.load_audio(title, artist)

    def load_audio(self, title: str, artist: str) -> None:
        """
        Initialise the AudioStreamHandler used in the practice mode
        from the selected audio file path.
        """
        print(f"Loading '{self.song_filepath}'...")
        audio = AudioStreamHandler(
            LoadedAudio(
                path=self.song_filepath,
                title=title,
                artist=artist
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
