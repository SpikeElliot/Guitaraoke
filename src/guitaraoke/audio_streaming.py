"""
Provides classes for audio streaming and playback functionality.

Classes
-------
LoadedAudio()
    Contains all needed data from an audio file.

AudioStreamHandler()
    Handle audio I/O streaming and playback functionality.
"""

import os
import time
from configparser import ConfigParser
from pathlib import Path
import librosa
import numpy as np
import pandas as pd
import sounddevice as sd
from PyQt6.QtCore import QObject, pyqtSignal, QTimer # pylint: disable=no-name-in-module
from guitaraoke.save_notes import save_notes
from guitaraoke.separate_guitar import separate_guitar
from guitaraoke.utils import (
    csv_to_notes_dataframe, preprocess_note_data, read_config
)

class LoadedAudio():
    """
    Contains all necessary data received from an audio file such as its
    audio time series, tempo, and duration.

    Attributes
    ----------
    metadata : dict[str, str]
        The song's title, artist, and filename stored in a dictionary.
    guitar_data, no_guitar_data : ndarray
        The song's separated tracks' audio time series.
    notes : DataFrame
        The guitar note events predicted from the song in a DataFrame.
    bpm : float
        The song's tempo.
    first_beat : float
        The estimated time position of the song's first beat onset.
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

        self.audio_config = read_config("Audio")

        self.metadata = {
            "title": title,
            "artist": artist,
            "filename": path.stem
        }
        self.notes, self.guitar_data, self.no_guitar_data = self._get_audio_data(path)
        self.bpm, self.first_beat = self._get_tempo_data()
        self.duration = len(self.guitar_data) / self.audio_config["rate"] # In secs

    def _get_audio_data(
        self,
        path: Path
    ) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
        """
        Load a song's predicted notes DataFrame and its separated
        audio time series (guitar_data and no_guitar_data).
        """
        audio_dir = Path(f"{os.environ['sep_tracks_dir']}\\{self.metadata['filename']}")
        guitar_path = audio_dir / "guitar.wav"
        no_guitar_path = audio_dir / "no_guitar.wav"

        # Perform guitar separation and note detection
        guitar_path, no_guitar_data = separate_guitar(path)
        notes_path = save_notes(guitar_path)[0]

        # Convert notes CSV to a pandas DataFrame
        notes = csv_to_notes_dataframe(notes_path)

        # Get guitar and no_guitar tracks' audio time series
        guitar_data = librosa.load(guitar_path, sr=self.audio_config["rate"])[0]
        no_guitar_data = librosa.load(no_guitar_path, sr=self.audio_config["rate"])[0]

        return notes, guitar_data, no_guitar_data

    def _get_tempo_data(self) -> tuple[float, float]:
        """
        Find a song's predicted BPM and the estimated time position of 
        its first beat.
        """
        tempo, beats = librosa.beat.beat_track(
            y=self.guitar_data + self.no_guitar_data, # Full mix
            sr=self.audio_config["rate"]
        )
        bpm = tempo[0]
        first_beat = librosa.frames_to_time(beats[0]) * 1000 # In ms

        return bpm, first_beat


class AudioStreamHandler(QObject):
    """
    Handle audio I/O streaming and playback functionality.

    Attributes
    ----------
    song : LoadedAudio
        A LoadedAudio instance containing song data such as its audio
        time series and notes DataFrame.
    rec_buffer : ndarray
        An ndarray that acts as a circular buffer containing 2 seconds
        of user audio data sent to the practice window for scoring.
    rec_overlap_window : ndarray
        An ndarray that containing recorded input audio data pushed to
        the rec_buffer when a full second of audio has been added.
    paused, ended : bool
        The current state of audio playback's paused and ended status.
    stream : Stream
        The sounddevice I/O stream.
    position : int
        The current position of audio playback in frames.
    guitar_volume : float
        The volume to linearly scale the separated guitar track's
        amplitudes by. Should be kept between 0 and 1.
    metronome : dict[str, Any]
        Information relating to the metronome such as its audio time
        series and count-in status.
    score_data : dict[str, int]
        The user's performance data: score, notes hit, total notes, and
        accuracy.
    """
    new_input_buffer_signal = pyqtSignal(tuple)

    def __init__(self, song: LoadedAudio) -> None:
        super().__init__()
        # Audio data
        self.song = song

        self.audio_config = read_config("Audio")

        # Input variables
        self._rec_buffer = np.zeros(self.audio_config["rec_buffer_size"]) # Input audio buffer
        self._rec_overlap_window = np.ndarray(0) # Input audio overlap window

        # Playback data
        self._paused = True
        self._ended = True
        self._position = 0
        self._guitar_volume = 1.0
        self.loop_markers = [None,None]
        self.looping = False

        # Metronome data
        self.metronome = {
            "audio_data": librosa.load(
                f"{os.environ['assets_dir']}\\audio\\metronome.wav",
                sr=self.audio_config["rate"]
            )[0],
            "count_in_enabled": True,
            "count": 0,
            "interval": int(1000 / (self.song.bpm / 60))
        }

        # I/O Stream
        self._stream = sd.Stream(
            samplerate=self.audio_config["rate"],
            device=(self.audio_config["input_device_index"], None),
            channels=(self.audio_config["channels"], self.audio_config["channels"]),
            callback=self._callback,
            dtype=self.audio_config["dtype"],
            latency="low",
        )

        in_lat, out_lat = self._stream.latency
        print(
            f"Input Latency: {in_lat*1000:.1f}ms\n"
            f"Output Latency: {out_lat*1000:.1f}ms"
        )

        # Update config file
        parser = ConfigParser()
        parser.read("data\\config.ini")

        # Write current stream latency values to config
        parser.set("Audio", "in_latency", str(in_lat))
        parser.set("Audio", "out_latency", str(out_lat))

        with open("data\\config.ini", "w", encoding="utf-8") as configfile:
            parser.write(configfile)

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
        if not (0 <= int(position * self.audio_config["rate"])
                <= int(self.song.duration * self.audio_config["rate"])):
            raise ValueError("Position must be between 0 and song duration.")
        if self._ended:
            self._ended = False
        self._position = int(position * self.audio_config["rate"])
        # Reset buffers when audio skipped
        self.zero_buffers()

    def start(self) -> None:
        """Play or unpause audio stream."""
        print("\nStream started...")
        if self._ended: # Reset position to start of song
            self._position = 0
            self._ended = False
        self._paused = False
        self._stream.start()
        # Reset buffers when audio started
        self.zero_buffers()

    def stop(self) -> None:
        """Pause audio stream."""
        print("\nStream stopped.")
        if not self._paused:
            self._paused = True
        self._stream.stop()

    def abort_stream(self) -> None:
        """Immediately terminate audio processing."""
        self._stream.abort()

    def _callback(self, indata, outdata, frames, t, status) -> None: # pylint: disable=unused-argument,too-many-arguments,too-many-positional-arguments
        """Callback function for the sounddevice Stream."""
        if status: # Print callback flags if any
            print(f"Stream callback flags: {status}", flush=True)

        # INPUT HANDLING

        self._rec_overlap_window = np.append(
            self._rec_overlap_window, indata.copy()
        )

        if self._rec_overlap_window.size >= self.audio_config["rec_overlap_window_size"]:
            perf_time_start = time.perf_counter()
            overlap_size = self.audio_config["rec_overlap_window_size"]
            # Add new overlap buffered data to main buffer, and push main
            # buffer to the left by rec_overlap_window_size
            self._rec_buffer = np.append(
                self._rec_buffer,
                self._rec_overlap_window[:overlap_size]
            )
            self._rec_buffer = self._rec_buffer[overlap_size:]

            # Remove data added to main buffer from overlap window buffer
            self._rec_overlap_window = self._rec_overlap_window[overlap_size:]

            # Only take note data from song time-slice equal to size
            # of data currently in the buffer to avoid negatively
            # impacting user accuracy
            if not np.any(self._rec_buffer[:overlap_size]):
                slice_start = (self._position-overlap_size)/self.audio_config["rate"]
            else:
                slice_start = ((self._position-self.audio_config["rec_buffer_size"])
                               /self.audio_config["rate"])

            # Send audio buffer data, position, and song notes
            # to connected function in main file for scoring
            notes = preprocess_note_data(
                self.song.notes,
                slice_start=slice_start,
                slice_end=self._position/self.audio_config["rate"],
            )
            self.new_input_buffer_signal.emit(
                (self._rec_buffer.copy(), self._position, notes, perf_time_start)
            )

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

            # Get all frames before right loop marker, and concatenate
            # with all frames needed after loop
            guitar_batch = np.concatenate((
                self.song.guitar_data[self._position:self.loop_markers[1]],
                self.song.guitar_data[self.loop_markers[0]:new_pos]
            ))
            no_guitar_batch = np.concatenate((
                self.song.no_guitar_data[self._position:self.loop_markers[1]],
                self.song.no_guitar_data[self.loop_markers[0]:new_pos]
            ))
        else:
            # Case: no looping and end of song is reached in this batch
            if new_pos >= len(self.song.guitar_data):
                new_pos = len(self.song.guitar_data)
                frames = new_pos - self._position
                self._ended = True

            # No looping, load guitar and no_guitar batches as normal
            guitar_batch = self.song.guitar_data[self._position:new_pos]
            no_guitar_batch = self.song.no_guitar_data[self._position:new_pos]

        # Sum the amplitudes of the two tracks to get full mix values
        audio_batch = (guitar_batch * self._guitar_volume) + no_guitar_batch
        outdata[:frames] = audio_batch.reshape(-1,1)

        self._position = new_pos # Update song position

    def play_count_in_metronome(self, count_in_timer: QTimer) -> None:
        """
        Play the count-in metronome sound and increment the metronome's
        count value, starting song playback after the fourth count.

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

        sd.play(self.metronome["audio_data"], samplerate=self.audio_config["rate"])
        return False # Keep counting

    def in_loop_bounds(self) -> bool:
        """Check playback is looping and within loop marker bounds."""
        if self.looping:
            if (self._position > self.loop_markers[0]
            and self._position < self.loop_markers[1]):
                return True
        return False

    def zero_buffers(self) -> None:
        """Reset buffers when audio is restarted or skipped."""
        self._rec_buffer = np.zeros(self.audio_config["rec_buffer_size"])
        self._rec_overlap_window = np.ndarray(0)
