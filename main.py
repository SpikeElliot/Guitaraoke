"""The main file of the application."""

import os
import sys
import time
import multiprocessing
from PyQt6.QtWidgets import ( # pylint: disable=no-name-in-module
    QApplication, QMainWindow, QStackedWidget, QWidget, QLabel, QVBoxLayout
)
from PyQt6.QtGui import QFontDatabase, QIcon, QPixmap # pylint: disable=no-name-in-module
from PyQt6.QtCore import QDir, QThread, pyqtSignal, QObject # pylint: disable=no-name-in-module
from guitaraoke.scoring_system import ScoringSystem
from guitaraoke.practice_window import PracticeWindow
from guitaraoke.setup_window import SetupWindow
from guitaraoke.audio_streaming import AudioStreamHandler, LoadedAudio
from guitaraoke.utils import read_config
from guitaraoke.preload import preload_directories


class LoadingWindow(QWidget):
    """A loading screen shown during the song loading process."""
    def __init__(self) -> None:
        """The constructor for the LoadingWindow class."""
        super().__init__()

        self.gui_config = read_config("GUI")

        self.setWindowTitle("Guitaraoke")

        self.setFixedSize(self.gui_config["min_width"], self.gui_config["min_height"])

        self.loading_image = QLabel()
        self.loading_image.setFixedSize(
            self.gui_config["min_width"], self.gui_config["min_height"]
        )
        self.loading_pixmap = QPixmap(f"{os.environ['assets_dir']}\\images\\loading_screen.png")
        self.loading_image.setPixmap(self.loading_pixmap)

        layout = QVBoxLayout()
        layout.addWidget(self.loading_image)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    """The main window of the GUI application."""
    def __init__(self) -> None:
        """The constructor for the MainWindow class."""
        super().__init__()

        self.gui_config = read_config("GUI")

        self.scorer = ScoringSystem()

        self.setWindowIcon(QIcon(f"{os.environ['assets_dir']}\\images\\guitar_pick.png"))

        self.setWindowTitle("Guitaraoke")

        self.setFixedSize(self.gui_config["min_width"], self.gui_config["min_height"])

        self.setup_window = SetupWindow()
        self.practice_window = None
        self.loading_window = None
        self.loading_thread = None
        self.worker = None

        self.window_stack = QStackedWidget()
        self.window_stack.addWidget(self.setup_window)
        self.setup_window.load_song_signal.connect(
            self.launch_practice_mode
        )
        self.setCentralWidget(self.window_stack)

        self.set_styles()

    def set_styles(self) -> dict[str, str]:
        """Sets the CSS styling of the window and widgets."""
        with open(
            f"{os.environ['assets_dir']}\\stylesheets\\main.qss", "r", encoding="utf-8"
        ) as f:
            # Read main stylesheet and set main window style
            _style = f.read()
            self.setStyleSheet(_style)

    def launch_practice_mode(self, song_data: tuple[str, str, str]) -> None:
        """
        Displays a loading screen before loading data from the selected
        song and creating a PracticeWindow.
        """
        # Set current window to loading screen
        self.loading_window = LoadingWindow()
        self.window_stack.addWidget(self.loading_window)
        self.window_stack.setCurrentWidget(self.loading_window)
        try:
            # Start song loading thread
            self.loading_thread = QThread()
            self.worker = SongLoader(song_data)
            self.worker.moveToThread(self.loading_thread)
            self.loading_thread.started.connect(self.worker.run)
            self.worker.loaded.connect(self.song_loaded)
            self.worker.loaded.connect(self.loading_thread.quit)
            self.worker.loaded.connect(self.worker.deleteLater)
            self.loading_thread.finished.connect(self.loading_thread.deleteLater)
            self.loading_thread.start()
        except RuntimeError:
            self.window_stack.removeWidget(self.loading_window)

    def song_loaded(self, song: AudioStreamHandler) -> None:
        """
        Instantiate PracticeWindow using loaded song and update
        current window.
        """
        self.practice_window = PracticeWindow(song, self.scorer)
        self.practice_window.back_button_pressed_signal.connect(self.show_setup_window)
        # Add practice window to window stack and remove loading screen
        self.window_stack.addWidget(self.practice_window)
        self.window_stack.setCurrentWidget(self.practice_window)
        self.window_stack.removeWidget(self.loading_window)

    def show_setup_window(self) -> None:
        """
        Destroy current PracticeWindow instance and set current window
        to SetupWindow when back button pressed in practice screen.
        """
        self.destroy_practice_window()
        self.scorer.zero_score_data()
        self.window_stack.setCurrentWidget(self.setup_window)

    def destroy_practice_window(self) -> None:
        """
        End all running processes of the current PracticeWindow
        instance before deleting it.
        """
        if not hasattr(self, "practice_window"):
            return
        if self.practice_window is None:
            return
        self.practice_window.audio.abort_stream()
        # Wait for current scoring process to end
        while self.scorer.executor_future is not None:
            time.sleep(0.01)
        # Delete practice window
        self.window_stack.removeWidget(self.practice_window)
        del self.practice_window


class SongLoader(QObject):
    """Worker object that performs song loading."""
    loaded = pyqtSignal(AudioStreamHandler)

    def __init__(self, song_data: tuple[str, str, str]) -> None:
        """The constructor for the SongLoader class."""
        super().__init__()

        self.song_data = song_data

    def run(self) -> None:
        """Perform song loading."""
        path, title, artist = self.song_data
        audio = AudioStreamHandler(
            LoadedAudio(
                path=path,
                title=title,
                artist=artist
            )
        )
        self.loaded.emit(audio)


def main() -> None:
    """Run the application."""

    # Add path to find images in stylesheet
    QDir.addSearchPath("images", f"{os.environ['assets_dir']}\\images")

    # Initialise the application and add the font
    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont(f"{os.environ['assets_dir']}\\fonts\\Roboto-Regular.ttf")

    main_window = MainWindow()
    main_window.show()

    # If running as an executable, close splash screen when GUI loaded
    try:
        import pyi_splash # pylint: disable=import-outside-toplevel
        pyi_splash.close()
    except ImportError:
        pass

    sys.exit(app_exec(app, main_window))


def app_exec(app: QApplication, window: MainWindow) -> None:
    """End all processes when the application's window is closed."""
    app.exec()
    window.destroy_practice_window()
    window.scorer.shutdown_processes()


if __name__ == "__main__":
    multiprocessing.freeze_support() # Pyinstaller fix

    try:
        preload_directories() # Perform preloading
    except IOError:
        pass

    main()
