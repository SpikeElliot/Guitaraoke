"""The main file of the application."""

import sys
from PyQt6.QtWidgets import ( # pylint: disable=no-name-in-module
    QApplication, QMainWindow, QStackedWidget
)
from PyQt6.QtGui import QFontDatabase # pylint: disable=no-name-in-module
from guitaraoke.scoring_system import ScoringSystem
from guitaraoke.practice_window import PracticeWindow
from guitaraoke.setup_window import SetupWindow
from guitaraoke.audio_streaming import AudioStreamHandler
from guitaraoke.utils import read_config

gui_config = read_config("GUI")
audio_config = read_config("Audio")

class MainWindow(QMainWindow):
    """The main window of the GUI application."""
    def __init__(self) -> None:
        """The constructor for the MainWindow class."""
        super().__init__()

        self.scorer = ScoringSystem()

        self.setWindowTitle("Guitaraoke")

        self.setFixedSize(gui_config["width"], gui_config["height"])

        self.setup_window = SetupWindow()
        self.practice_window = None

        self.window_stack = QStackedWidget()
        self.window_stack.addWidget(self.setup_window)
        self.setup_window.send_set_practice_window_signal.connect(
            self.create_practice_window
        )
        self.setCentralWidget(self.window_stack)

        self.set_styles()

    def set_styles(self) -> dict[str]:
        """Sets the CSS styling of the window and widgets."""
        with open("./assets/stylesheets/main.qss", "r", encoding="utf-8") as f:
            # Read main stylesheet and set main window style
            _style = f.read()
            self.setStyleSheet(_style)

    def create_practice_window(self, audio: AudioStreamHandler) -> None:
        """
        Initialises the PracticeWindow when selected song received from
        the SetupWindow.
        """
        self.practice_window = PracticeWindow(audio, self.scorer)
        self.window_stack.addWidget(self.practice_window)
        self.window_stack.setCurrentWidget(self.practice_window)


def main() -> None:
    """Run the application."""
    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont("./assets/fonts/Roboto-Regular.ttf")
    main_window = MainWindow()
    main_window.show()
    sys.exit(app_exec(app, main_window))


def app_exec(app: QApplication, window: MainWindow) -> None:
    """End all processes when the application's window is closed."""
    if window.practice_window:
        window.practice_window.audio.abort_stream()
    app.exec()
    window.scorer.shutdown_processes()


if __name__ == "__main__":
    main()
