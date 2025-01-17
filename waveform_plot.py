import pyqtgraph as pg
import numpy as np
import librosa

class WaveformPlot():

    def __init__(self, audio):
        super().__init__()

        self.plot = pg.PlotWidget()

        # One point represents a window of ~100 ms
        self.num_points = int(audio.duration*10)

        # Downsampling for better performance when plotting waveform
        plot_frames = librosa.resample(y=audio.frames,
                                       orig_sr=audio.RATE,
                                       target_sr=audio.RATE/64
        )
        w_size = int(len(plot_frames) / self.num_points)
        self.x_vals = np.arange(0, self.num_points)

        # Get max and min values for each window
        w_maxes, w_mins = [], []
        for i in range(self.num_points):
            w = plot_frames[i*w_size:i*w_size+w_size]
            w_maxes.append(np.max(w))
            w_mins.append(np.min([0, np.min(w)]))
        
        # Convert lists to np arrays for data processing
        self.max_windows = np.array(w_maxes)
        self.min_windows = np.array(w_mins)

        # Get y-axis limits based on range of amplitudes from windows
        self.max_ylim = np.max(self.max_windows)
        self.min_ylim = np.min(self.min_windows)

        # Scale the data (0 to 1 for pos vals, 0 to -1 for neg vals)
        self.max_windows /= self.max_ylim
        self.min_windows /= abs(self.min_ylim)

        # Set axis ranges for plot
        self.plot.setYRange(-1, 1, padding=0)
        self.plot.setXRange(0, self.num_points, padding=0)

        self.drawPlot()

    # Draw plot of max and min waveform lines, filling between points.  
    def drawPlot(self, c=(0, 187, 255)):
        self.pen=pg.mkPen(color=c)
        self.brush=pg.mkBrush(color=c)

        # Initial plot of waveform
        self.max_line = pg.PlotCurveItem(self.x_vals,
                                         self.max_windows,
                                         pen=self.pen
        )

        self.min_line = pg.PlotCurveItem(self.x_vals,
                                         self.min_windows,
                                         pen=self.pen
        )

        self.plot.addItem(self.max_line)
        self.plot.addItem(self.min_line)
        fill = pg.FillBetweenItem(self.max_line,
                                  self.min_line,
                                  brush=self.brush)
        self.plot.addItem(fill)
