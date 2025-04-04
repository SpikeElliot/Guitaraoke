"""Module providing a waveform plot class."""

import librosa
import numpy as np
import pyqtgraph as pg
from config import RATE
from guitaraoke.audio_playback import LoadedAudio


class WaveformPlot(pg.PlotWidget):
    """
    A waveform representation of audio data plotted using PyQtGraph. Inherits from PlotWidget class.

    Parameters
    ----------
    width : int
        The fixed width of the PlotWidget.
    height : int
        The fixed height of the PlotWidget.
    background_colour : tuple[int,int,int], default=(255,255,255)
        The RGB values to use for the plot's background colour.
    colour : tuple[int,int,int], default=(0,0,0)
        The RGB values to use for the plot's fill colour.
    """
    def __init__(
        self,
        width: int,
        height: int,
        bg_colour: tuple[int,int,int] = (255,255,255),
        colour: tuple[int,int,int] = (0,0,0)
    ) -> None:
        """
        The constructor for the WaveformPlot class.

        Parameters
        ----------
        width : int
            The fixed width of the PlotWidget.
        height : int
            The fixed height of the PlotWidget.
        background_colour : tuple[int,int,int], default=(255,255,255)
            The RGB values to use for the plot's background colour.
        colour : tuple[int,int,int], default=(0,0,0)
            The RGB values to use for the plot's fill colour.
        """
        super().__init__()

        self.width, self.height = width, height
        self.bg_colour, self.colour = bg_colour, colour
        self.setBackground(self.bg_colour)
        self.setFixedSize(self.width, self.height)

        # Set plot properties
        self.showAxes(False)
        self.hideButtons()
        self.setMouseEnabled(False, False)
        self.setMenuEnabled(False) # Disable context menu blocking right click

    def draw_plot(self, song: LoadedAudio) -> None:
        """
        Draw the plot of an audio file's maximum and minimum window amplitudes
        as two lines, filling between the points to create a waveform.

        Parameters
        ----------
        song : LoadedAudio
            The LoadedAudio object whose audio time series data (frames) 
            will be used.
        """
        # Preserves a minimum number of 1000 points on the graph if audio file
        # is too short, otherwise one point represents a window of ~100 ms
        num_points = np.max([1000, int(song.duration * 10)])

        # Downsampling for better performance when plotting waveform
        plot_frames = librosa.resample(
            y=song.guitar_data + song.no_guitar_data, # Sum to get full mix
            orig_sr=RATE,
            target_sr=RATE/16
        )
        w_size = int(len(plot_frames) / num_points)
        x_vals = np.arange(0, num_points)

        # Get max and min values for each window
        max_windows, min_windows = [], []
        for i in range(num_points):
            w = plot_frames[i*w_size : i*w_size + w_size]
            max_windows.append(np.max(w))
            min_windows.append(np.min([0, np.min(w)]))

        # Convert lists to np arrays for data processing
        max_windows = np.array(max_windows)
        min_windows = np.array(min_windows)

        # Scale the data (0 to 1 for pos vals, 0 to -1 for neg vals)
        max_windows /= np.max(max_windows)
        min_windows /= np.abs(np.min(min_windows))

        # Set axis ranges for plot
        self.setYRange(-1, 1, padding=0) # pylint: disable=redundant-keyword-arg
        self.setXRange(0, num_points, padding=0) # pylint: disable=redundant-keyword-arg

        # Set line colour
        pen = pg.mkPen(self.colour)
        brush = pg.mkBrush(self.colour)

        # Initialise plot items
        max_line = pg.PlotCurveItem(x_vals, max_windows, pen=pen)
        min_line = pg.PlotCurveItem(x_vals, min_windows, pen=pen)
        fill = pg.FillBetweenItem(max_line, min_line, brush=brush)

        # Add items to the plot
        self.addItem(max_line)
        self.addItem(min_line)
        self.addItem(fill)

    def clicked_connect(self, function):
        """Add a mouse click connection to the waveform plot widget."""
        self.scene().sigMouseClicked.connect(function)
