import pyqtgraph as pg
import numpy as np
import librosa


class PitchPlot():

    def __init__(self, audio):
        super().__init__()

        self.plot = pg.PlotWidget()

        # Set plot properties
        self.plot.hideButtons()
        self.plot.setMouseEnabled(False, False)

        time_length = len(audio.pitches[0, :])
        self.x_vals = np.arange(0, time_length)
        
        self.y_vals = []
        for i in range(time_length):
            index = audio.magnitudes[:,i].argmax()
            pitch = audio.pitches[index, i]
            self.y_vals.append(pitch)

        self.y_vals = np.array(self.y_vals)

        # Set axis ranges for plot
        self.plot.setYRange(np.min(self.y_vals), np.max(self.y_vals), padding=0)
        self.plot.setXRange(0, time_length, padding=0)

        self.drawPlot()

    # Draw plot of max and min waveform lines, filling between points.  
    def drawPlot(self, c=(255, 0, 0)):
        self.plot.clear()

        self.pen=pg.mkPen(color=c)
        self.brush=pg.mkBrush(color=c)

        self.pitch_line = pg.PlotCurveItem(self.x_vals,
                                           self.y_vals,
                                           pen=self.pen
        )

        self.plot.addItem(self.pitch_line)