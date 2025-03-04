from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import sounddevice as sd
import numpy as np
from audio_load_handler import AudioLoadHandler

class AudioPlayback(QThread):
    """
    Provides an interface for playback of a loaded audio file.

    Parameters
    ----------
    audio : AudioLoadHandler
        An object that holds relevant information about the loaded audio file.
    paused : bool
        Whether audio playback is paused or not.
    ended : bool
        Whether audio playback has finished or not.
    stream : OutputStream
        The song's sounddevice output stream for audio playback.
    position : int
        The current position of audio playback in frames.
    guitar_volume : float
        The volume to scale the separated guitar track's amplitudes by (0-1).
    user_score : int
        The performance score derived from comparing the user's recorded pitch
        to the guitar track's.
    metronome_count : int
        The current count of the count-in metronome sound that play four times
        before audio playback starts.
    count_interval : int
        The time in ms between each metronome sound based on the loaded audio
        file's tempo.

    Methods
    -------
    load(path)
        Instantiate a new AudioLoadHandler object that loads the necessary data
        from an audio file given its path.
    play()
        Play or unpause audio playback.
    play_metronome()
        Play a count-in metronome sound, starting audio playback after the
        fourth count.
    pause()
        Pause audio playback.
    get_pos()
        Return the audio playback's current time position in seconds.
    set_pos(pos):
        Set the audio playback's time position to a new time in seconds.
    """

    def __init__(self, path):
        """The constructor for the AudioPlayBack class.

        Parameters
        ----------
        path : str
            The file path of the audio file to load.
        """
        super().__init__()
        self.stream = None
        self.load(path)
        
    def load(self, path):
        """
        Instantiate a new AudioLoadHandler object that loads the necessary data
        from an audio file given its path.

        Parameters
        ----------
        path : str
            The file path of the audio file to load.
        """
        # When loading a new song, immediately terminate audio processing of
        # previous song's stream
        if self.stream:
            self.stream.abort()

        self.audio = AudioLoadHandler(path)
        sd.default.samplerate = self.audio.RATE
        self.stream = sd.OutputStream(
            samplerate=self.audio.RATE,
            channels=self.audio.CHANNELS,
            callback=self._callback
        )
        self.paused, self.ended = True, True
        self.position, self.user_score, self.metronome_count = 0, 0, 0
        self.guitar_volume = 1
        self.count_interval = int(1000 / (self.audio.bpm / 60))

    def run(self):
        """Play or unpause audio playback."""
        print("Playback started...")
        if self.ended:
            self.position = 0
        self.paused, self.ended = False, False
        self.stream.start()

    def stop(self):
        """Pause audio playback."""
        print("Playback stopped.")
        if not self.paused:
            self.paused = True
        self.quit()
        self.wait()
    
    def play_count_in_metronome(self, count_in_timer : QTimer):
        """
        Use sounddevice to play the count-in metronome sound and increment the
        metronome_count attribute, playing the song after the fourth count.

        Parameters
        ----------
        count_in_timer : QTimer
            The QTimer whose interval will be updated after 4 counts.
        """
        self.metronome_count += 1

        # Stop counting when metronome aligned to song position
        if self.metronome_count > 4:
            count_in_timer.stop()
            self.metronome_count = 0
            return True # Start song

        sd.play(self.audio.metronome_data)
        sd.wait()
        return False # Keep counting
    
    def get_pos(self):
        """Return the audio playback's current time position in seconds."""
        pos = self.position / self.audio.RATE
        return pos
    
    def set_pos(self, pos):
        """Set the audio playback's time position to a new time in seconds."""
        if self.ended:
            self.ended = False
        self.position = int(pos * self.audio.RATE)

    def _callback(self, outdata, frames, time, status):
        """
        The callback function called by the sounddevice output stream. 
        Generates output audio data.
        """
        new_pos = self.position + frames
        frames_per_buffer = new_pos - self.position

        # Set outdata to zeros if audio should not be playing
        if self.paused or self.ended:
            outdata[:frames_per_buffer] = np.zeros((frames_per_buffer,1))
            return
        
        # Set ended bool to True if end reached
        if new_pos >= len(self.audio.guitar_data):
            new_pos = len(self.audio.guitar_data)
            self.ended = True

        # Set outdata to next frames of loaded audio
        try:
            guitar_batch = self.audio.guitar_data[self.position:new_pos].copy()
            no_guitar_batch = self.audio.no_guitar_data[self.position:new_pos].copy()
            guitar_batch *= self.guitar_volume
            # Sum the amplitudes of the two tracks to get full mix values
            audio_batch = np.add(guitar_batch,no_guitar_batch).reshape(-1,1)
            outdata[:frames_per_buffer] = audio_batch
        # Case: not enough frames from audio data compared to buffer size
        except ValueError as e:
            # Set outdata to zeros
            outdata[:frames_per_buffer] = np.zeros((frames_per_buffer,1))

        self.position = new_pos # Update song position

    # def _get_offset(self):
    #     """Return the current time position's distance from the previous beat in ms."""
    #     offset = int(((self.position/self.audio.RATE)*1000 + self.audio.first_beat) % self.count_interval)
    #     return offset