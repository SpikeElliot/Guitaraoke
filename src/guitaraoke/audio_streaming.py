"""
Module providing AudioInput, AudioOutput, and AudioStreamHandlers classes.
"""

from pathlib import Path
import librosa
import numpy as np
import pandas as pd
import sounddevice as sd
from PyQt5.QtCore import QObject, pyqtSignal, QTimer # pylint: disable=no-name-in-module
from config import CHANNELS, RATE, DTYPE, SEP_TRACKS_DIR, REC_BUFFER_SIZE
from guitaraoke.save_pitches import save_pitches
from guitaraoke.separate_guitar import separate_guitar
from guitaraoke.utils import csv_to_pitches_dataframe, preprocess_pitch_data


class AudioInput():
    """
    Handles operations relating to audio input such as streaming and recording.

    Attributes
    ----------
    audio_blocks : ndarray
        An ndarray that holds recorded input audio data to be added to a
        buffer once it meets the necessary size required.
    input_device_index : int
        The index of the input device used.
    """
    def __init__(self) -> None:
        """The constructor for the AudioInput class."""
        self.audio_blocks = np.ndarray(0)
        self.device_index = 2

    def find_devices(self) -> None:
        """Return a list of available audio input devices."""
        devices = sd.query_devices()
        input_devs = []
        for d in devices:
            if d["max_input_channels"] > 0 and d["hostapi"] == 0:
                input_devs.append(d)
        return input_devs


class AudioOutput():
    """
    Contains all necessary data received from an audio file such as its audio
    time series, tempo, and duration.

    Attributes
    ----------
    metadata : dict[str, str]
        The song's title, artist, and filename stored in a dictionary.
    guitar_data, no_guitar_data : ndarray
        The song's separated guitar and no_guitar track audio time series.
    pitches : DataFrame
        The guitar note events predicted from the song in a DataFrame.
    bpm : float
        The song's tempo.
    first_beat : float
        The estimated time position of the onset of the song's first beat.
    duration : float
        The length of the song in seconds.
    """
    def __init__(
        self,
        path: str | Path,
        title: str = "Unknown",
        artist: str = "Unknown"
    ) -> None:
        """
        The constructor for the LoadedAudio class.

        Parameters
        ----------
        path : str | Path
            The file path of the audio file to load.
        title : str, default="Unknown"
            The title given to the loaded audio file.
        artist : str, default="Unknown"
            The artist attributed to the loaded audio file.
        """
        assert isinstance(path, (Path, str)), "File path should be a string or pathlib Path"
        path = Path(path)
        assert path.exists(), "File does not exist"
        self.metadata = {
            "title": title,
            "artist": artist,
            "filename": path.stem
        }
        (self.pitches, self.guitar_data,
         self.no_guitar_data) = self._get_audio_data(path)
        self.bpm, self.first_beat = self._get_tempo_data()
        self.duration = len(self.guitar_data) / RATE # In secs

    def _get_audio_data(
        self,
        path: Path
    ) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
        """
        Load a song's predicted pitches DataFrame and its guitar-separated
        audio time series (guitar_data and no_guitar_data).
        """
        audio_dir = SEP_TRACKS_DIR / self.metadata["filename"]
        guitar_path = audio_dir / "guitar.wav"
        no_guitar_path = audio_dir / "no_guitar.wav"

        # Perform guitar separation and pitch detection
        guitar_path, no_guitar_data = separate_guitar(path)
        pitches_path = save_pitches(guitar_path)[0]

        # Convert pitches CSV to a pandas DataFrame
        pitches = csv_to_pitches_dataframe(pitches_path)

        # Get guitar and no_guitar tracks' audio time series
        guitar_data = librosa.load(guitar_path, sr=RATE)[0]
        no_guitar_data = librosa.load(no_guitar_path, sr=RATE)[0]

        return pitches, guitar_data, no_guitar_data

    def _get_tempo_data(self) -> tuple[float, float]:
        """
        Find a song's predicted BPM and the estimated time position of its
        first beat.
        """
        tempo, beats = librosa.beat.beat_track(
            y=self.guitar_data + self.no_guitar_data, # Full mix
            sr=RATE
        )
        bpm = tempo[0]
        first_beat = librosa.frames_to_time(beats[0]) * 1000 # In ms

        return bpm, first_beat


class AudioStreamHandler(QObject):
    """
    Handle audio I/O streaming and playback functionality.

    Attributes
    ----------
    paused, ended : bool
        The current state of audio playback's paused and ended status.
    stream : OutputStream
        The song's sounddevice output stream for audio playback.
    position : int
        The current position of audio playback in frames.
    guitar_volume : float
        The volume to linearly scale the separated guitar track's amplitudes
        by. Should be kept between 0 and 1.
    metronome : dict[str, Any]
        Information relating to the metronome such as its audio time series
        and count-in status.
    score_data : dict[str, int]
        The user's performance data: score, notes hit, total notes, and
        accuracy.
    """
    input_audio_buffer = pyqtSignal(tuple)

    def __init__(self, audio_in: AudioInput, audio_out: AudioOutput) -> None:
        super().__init__()
        self.audio_in = audio_in
        self.audio_out = audio_out

        # Playback data
        self._paused = True
        self._ended = True
        self._position = 0
        self._guitar_volume = 1.0
        self.loop_markers = [None,None]
        self.looping = False

        # Metronome data
        self.metronome = {
            "audio_data": librosa.load("./assets/audio/metronome.wav", sr=RATE)[0],
            "count_in_enabled": True,
            "count": 0,
            "interval": int(1000 / (self.audio_out.bpm / 60))
        }

        # I/O Stream
        self._stream = sd.Stream(
            samplerate=RATE,
            device=(self.audio_in.device_index, None),
            channels=CHANNELS,
            callback=self._callback,
            dtype=DTYPE,
            latency="low",
        )

    @property
    def position(self) -> int:
        """Getter for the song position in frames."""
        return self._position

    @property
    def guitar_volume(self) -> float:
        """Getter for the guitar track volume."""
        return self._guitar_volume

    @property
    def paused(self) -> bool:
        """Getter for the paused value."""
        return self._paused

    @property
    def ended(self) -> bool:
        """Getter for the ended value."""
        return self._ended

    @guitar_volume.setter
    def guitar_volume(self, value):
        """Setter for the guitar track volume"""
        if not 0 <= value <= 1.0:
            raise ValueError("Guitar volume must be between 0 and 1.")
        self._guitar_volume = value

    def seek(self, position: float) -> None:
        """Set the position to a new time in seconds."""
        if not 0 <= int(position * RATE) <= int(self.audio_out.duration * RATE):
            raise ValueError("Position must be between 0 and song duration.")
        if self._ended:
            self._ended = False
        self._position = int(position * RATE)

    def start(self) -> None:
        """Play or unpause audio stream."""
        print("\nStream started...")
        if self._ended: # Reset position to start of song
            self._position = 0
            self._ended = False
        self._paused = False
        self._stream.start()

    def stop(self) -> None:
        """Pause audio stream."""
        print("\nStream stopped.")
        if not self._paused:
            self._paused = True
        self._stream.stop()
        # Reset buffer when streaming ends
        self.audio_in.buffer = np.zeros(REC_BUFFER_SIZE)

    def _callback(self, indata, outdata, frames, time, status) -> None: # pylint: disable=unused-argument,too-many-arguments,too-many-positional-arguments
        if status: # Print callback flags if any
            print(f"Stream callback flags: {status}", flush=True)

        # INPUT HANDLING

        self.audio_in.audio_blocks = np.append(self.audio_in.audio_blocks, indata.copy())

        if self.audio_in.audio_blocks.size >= REC_BUFFER_SIZE:
            # Send buffered audio to connected function in main file
            buffer = self.audio_in.audio_blocks[:REC_BUFFER_SIZE].copy()
            pitches = preprocess_pitch_data(
                self.audio_out.pitches,
                slice_start=(self._position-REC_BUFFER_SIZE)/RATE,
                slice_end=self._position/RATE
            )
            self.input_audio_buffer.emit((buffer, self._position, pitches))
            self.audio_in.audio_blocks = self.audio_in.audio_blocks[REC_BUFFER_SIZE:]

        # OUTPUT HANDLING

        new_pos = self._position + frames

        # Case: audio should not be playing
        if self._paused or self._ended:
            # Set outdata to zeros
            outdata[:frames] = np.zeros((frames,1))
            return

        # Case: song looping and end of loop is reached in this batch
        if self.in_loop_bounds() and new_pos >= self.loop_markers[1]:
            overflow_frames = new_pos - self.loop_markers[1]
            # Set new pos to correct position after loop
            new_pos = self.loop_markers[0] + overflow_frames

            # Get all frames before right loop marker, and concatenate with
            # all frames needed after loop
            guitar_batch = np.concatenate((
                self.audio_out.guitar_data[self._position:self.loop_markers[1]],
                self.audio_out.guitar_data[self.loop_markers[0]:new_pos]
            ))
            no_guitar_batch = np.concatenate((
                self.audio_out.no_guitar_data[self._position:self.loop_markers[1]],
                self.audio_out.no_guitar_data[self.loop_markers[0]:new_pos]
            ))
        else:
            # Case: no looping and end of song is reached in this batch
            if new_pos >= len(self.audio_out.guitar_data):
                new_pos = len(self.audio_out.guitar_data)
                frames = new_pos - self._position
                self._ended = True

            # No looping, load guitar and no_guitar batches as normal
            guitar_batch = self.audio_out.guitar_data[self._position:new_pos]
            no_guitar_batch = self.audio_out.no_guitar_data[self._position:new_pos]

        # Sum the amplitudes of the two tracks to get full mix values
        audio_batch = (guitar_batch * self._guitar_volume) + no_guitar_batch
        outdata[:frames] = audio_batch.reshape(-1,1)

        self._position = new_pos # Update song position

    def play_count_in_metronome(self, count_in_timer: QTimer) -> None:
        """
        Play the count-in metronome sound and increment the metronome's count
        value, starting song playback after the fourth count.

        Parameters
        ----------
        count_in_timer : QTimer
            The QTimer whose interval will be updated after 4 counts.
        """
        self.metronome["count"] += 1

        # Stop counting when metronome aligned to song position
        if self.metronome["count"] > 4:
            count_in_timer.stop()
            self.metronome["count"] = 0
            return True # Start song

        sd.play(self.metronome["audio_data"], samplerate=RATE)
        return False # Keep counting

    def in_loop_bounds(self) -> bool:
        """Check playback is looping and within the loop marker bounds."""
        if (self.looping
            and (self._position > self.loop_markers[0]
            and self._position < self.loop_markers[1])):
            return True
        return False
