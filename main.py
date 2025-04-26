"""The main file of the application."""

import sys
from PyQt5.QtWidgets import ( # pylint: disable=no-name-in-module
    QApplication, QMainWindow, QStackedWidget
)
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
        self.window_stack.setCurrentWidget(self.setup_window)
        self.setCentralWidget(self.window_stack)

    def create_practice_window(self, audio: AudioStreamHandler) -> None:
        """Called when signal received from SetupWindow indicating a
        song has been selected"""
        self.practice_window = PracticeWindow(audio, self.scorer)
        self.window_stack.addWidget(self.practice_window)
        self.window_stack.setCurrentWidget(self.practice_window)


def main() -> None:
    """Run the application."""
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app_exec(app, main_window))


def app_exec(app: QApplication, window: MainWindow) -> None:
    """End all processes when the application's window is closed."""
    app.exec()
    window.scorer.shutdown_processes()


if __name__ == "__main__":
    main()
