import pyqtgraph as pg
import numpy as np
import librosa


class WaveformPlot(pg.PlotWidget):
    """
    A waveform representation of audio data plotted using PyQtGraph. Inherits from PlotWidget class.

    Methods
    -------
    clicked_connect(function)
        Add a mouse click connection to the plot widget.
    """
    def __init__(
            self, 
            audio, 
            width,
            height,
            background_colour=(255,255,255),
            colour=(70,42,255)
        ):
        """
        The constructor for the WaveformPlot class.

        Parameters
        ----------
        audio : AudioLoadHandler
            The AudioLoadHandler object whose path property will be used to
            access the audio file.
        width : int
            The fixed width of the PlotWidget.
        height : int
            The fixed height of the PlotWidget.
        background_colour : tuple of int, default=(255,255,255)
            The RGB values to use for the plot's background colour.
        colour : tuple of int, default=(70,42,255)
            The RGB values to use for the plot's fill colour.
        """
        super().__init__()

        self.width = width
        self.height = height
        self.background_colour = background_colour
        self.colour = colour
        self.setBackground(self.background_colour)
        self.setFixedHeight(self.height)
        self.setFixedWidth(self.width)

        # Set plot properties
        self.showAxes(False)
        self.hideButtons()
        self.setMouseEnabled(False, False)

        # Preserves a minimum number of 1000 points on the graph if audio file
        # is too short, otherwise one point represents a window of ~100 ms
        num_points = np.max([1000, int(audio.duration * 10)])

        # Downsampling for better performance when plotting waveform
        plot_frames = librosa.resample(
            y=audio.frames,
            orig_sr=audio.RATE,
            target_sr=audio.RATE/16
        )
        w_size = int(len(plot_frames) / num_points)
        x_vals = np.arange(0, num_points)

        # Get max and min values for each window
        w_maxes, w_mins = [], []
        for i in range(num_points):
            w = plot_frames[i*w_size : i*w_size + w_size]
            w_maxes.append(np.max(w))
            w_mins.append(np.min([0, np.min(w)]))
        
        # Convert lists to np arrays for data processing
        max_windows = np.array(w_maxes)
        min_windows = np.array(w_mins)

        # Get y-axis limits based on range of amplitudes from windows
        max_ylim = np.max(max_windows)
        min_ylim = np.min(min_windows)

        # Scale the data (0 to 1 for pos vals, 0 to -1 for neg vals)
        max_windows /= max_ylim
        min_windows /= abs(min_ylim)

        # Set axis ranges for plot
        self.setYRange(-1, 1, padding=0)
        self.setXRange(0, num_points, padding=0)

        self._draw_plot(x_vals, min_windows, max_windows)

    def _draw_plot(self, x_vals, min_windows, max_windows):
        """
        Draw the plot of max and min waveform lines, filling between the points.

        Parameters
        ----------
        x_vals : ndarray
            The values to plot along the x-axis.
        min_windows : ndarray
            The minimum amplitude of each window from the audio data, used as
            y-coordinates for the min waveform line.
        max_windows: ndarray
            The maximum amplitude of each window from the audio data, used as
            y-coordinates for the max waveform line.
        """
        pen=pg.mkPen(self.colour)
        brush=pg.mkBrush(self.colour)

        max_line = pg.PlotCurveItem(x_vals, max_windows, pen=pen)
        min_line = pg.PlotCurveItem(x_vals, min_windows, pen=pen)
        fill = pg.FillBetweenItem(max_line, min_line, brush=brush)

        self.addItem(max_line)
        self.addItem(min_line)
        self.addItem(fill)
        
    def clicked_connect(self, function):
        self.scene().sigMouseClicked.connect(function)