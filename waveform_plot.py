import pyqtgraph as pg
import numpy as np
import librosa


class WaveformPlot():
    """
    A waveform representation of audio data plotted using PyQtGraph.

    Attributes
    ----------
    plot : PlotWidget
        The PyQt widget containing the plot to be shown in the GUI.
    
    """
    def __init__(self, audio):
        """
        The constructor for the WaveformPlot class.

        Parameters
        ----------
        audio : AudioLoadHandler
            The AudioLoadHandler object whose path property will be used to
            access the audio file.
        """
        self.plot = pg.PlotWidget()

        # Set plot properties
        self.plot.showAxes(False)
        self.plot.hideButtons()
        self.plot.setMouseEnabled(False, False)
        self.plot.setBackground((255,255,255))

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
        self.plot.setYRange(-1, 1, padding=0)
        self.plot.setXRange(0, num_points, padding=0)

        self._draw_plot(x_vals, min_windows, max_windows)

    def _draw_plot(self, x_vals, min_windows, max_windows, colour=(0,0,0)):
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
        colour : tuple of int, default=(0,0,0)
            The RGB values to use for the plot's fill colour.
        """
        pen=pg.mkPen(colour)
        brush=pg.mkBrush(colour)

        max_line = pg.PlotCurveItem(x_vals, max_windows, pen=pen)
        min_line = pg.PlotCurveItem(x_vals, min_windows, pen=pen)
        fill = pg.FillBetweenItem(max_line, min_line, brush=brush)

        self.plot.addItem(max_line)
        self.plot.addItem(min_line)
        self.plot.addItem(fill)
