"""
Provides a class and functions for karaoke-style scoring system 
functionality.

Classes
-------
ScoringSystem(QObject)
    Contains score data and performs multiprocessing for real-time
    scoring.

Functions
---------
compare_notes
    Take two note dictionaries (user and song) and return user scores.

unique_nearest_notes
    Get all unique nearest song-user note pairs (used in 
    compare_notes).

process_recording
    Compare the user input recording's notes against the song's,
    returning the resultant score data.
"""

import os
from collections import deque, defaultdict
import tempfile
import concurrent.futures
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal # pylint: disable=no-name-in-module
from scipy.io.wavfile import write as write_wav
from guitaraoke.save_notes import save_notes
from guitaraoke.utils import (
    preprocess_note_data, csv_to_notes_dataframe, read_config
)

config = read_config("Audio")

class ScoringSystem(QObject):
    """
    Contains the current score data, provides functionality for 
    real-time scoring during user performance.

    Attributes
    ----------
    executor: ProcessPoolExecutor
        The process pool executor that creates futures for scoring
        processes.
    score: int
        The user's current score.
    notes_hit : float
        The number of notes the user has correctly played.
    total_notes : int
        The total number of song notes up to the current point of
        playback.
    accuracy : float
        The percentage out of total song notes hit by the user.
    """
    new_score_data_signal = pyqtSignal(tuple)

    def __init__(self) -> None:
        """The constructor for the ScoringSystem class."""
        super().__init__()
        self._executor = concurrent.futures.ProcessPoolExecutor(max_workers=1)
        self._executor.submit(preload_basic_pitch_model)
        self._executor_future = None

        self._score = 0
        self._notes_hit = 0
        self._total_notes = 0
        self._accuracy = 0
        self._swing_times = deque(maxlen=5)

    @property
    def executor(self):
        """Getter for the process pool executor."""
        return self._executor

    @property
    def executor_future(self):
        """The current future of the process pool executor."""
        return self._executor_future

    def shutdown_processes(self) -> None:
        """Shut down all worker processes."""
        self._executor.shutdown(wait=False)

    def submit_process_recording(
        self,
        buffer: np.ndarray,
        position: int,
        notes: dict[int, list]
    ) -> None:
        """
        Schedule the process_recording function to be executed by a 
        process, providing a callback function that updates score
        attributes with new data when the future is complete.
        """
        self._executor_future = self._executor.submit(
            process_recording,
            buffer, position, notes,
        )
        self._executor_future.add_done_callback(self._internal_done_callback)

    def _internal_done_callback(
        self,
        future: concurrent.futures.Future[tuple[int, float, int, list]]
    ) -> None:
        """
        Called when the future is complete, emits the resultant score
        data to the connected function in the main file.
        """
        score, notes_hit, total_notes, swing_times = future.result()
        self._executor_future = None
        # Scores currently divided by 2 as workaround to user notes
        # being counted twice
        self._score += int(round(score/2, ndigits=-1))
        self._notes_hit += round(notes_hit/2)
        self._total_notes += round(total_notes/2)

        # Find average note swing (median taken as times distribution
        # likely skewed, and to be robust to outliers)
        self._swing_times.append(swing_times)
        swing_times_list = [time for i in self._swing_times for time in i]
        if not swing_times_list:
            average_swing = 0
        else:
            average_swing = np.median(swing_times_list)

        # Print swing times for testing
        for i, times in enumerate(self._swing_times):
            print(f"{i+1}: {times}")

        if self._total_notes != 0: # Avoid divide by zero error
            self._accuracy = (self._notes_hit / self.total_notes) * 100

        self.new_score_data_signal.emit((self._score, self._accuracy, average_swing))

    @property
    def score(self) -> int:
        """Getter for the score value."""
        return self._score

    @property
    def notes_hit(self) -> float:
        """Getter for the notes_hit value."""
        return self._notes_hit

    @property
    def total_notes(self) -> int:
        """Getter for the total_notes value."""
        return self._total_notes

    @property
    def accuracy(self) -> int:
        """Getter for the accuracy value."""
        return self._accuracy

    @property
    def swing_times(self) -> int:
        """Getter for the note swing times array."""
        return self._swing_times

    def zero_score_data(self) -> None:
        """Reset score data (called when song skipped/restarted)."""
        (self._score, self._notes_hit, self._total_notes,
        self._accuracy, self._swing_times) = (0,0,0,0,deque(maxlen=5))


def preload_basic_pitch_model() -> None:
    """Load the Basic Pitch model when a worker process is created."""
    from guitaraoke.preload import PITCH_MODEL # pylint: disable=import-outside-toplevel,unused-import


def compare_notes(
    user_notes: dict[int, list],
    song_notes: dict[int, list]
) -> tuple[int, float, int, list]:
    """
    Take two note dictionaries (user and song), find the shortest 
    unique distances between each user and song note, and return the
    resultant performance information.

    Parameters
    ----------
    user_notes, song_notes : dict[int, list]
        Dictionaries containing lists of the times in seconds of note
        onsets for every possible MIDI pitch (0-127).
    
    Returns
    -------
    tuple[int, float, int, list]
        The user score, number of notes hit by the user, total number
        of notes, and average swing.
    """
    total_notes = 0
    notes_hit = 0
    note_swing_times = []

    # Iterate over user and song note events for all 128 MIDI pitches
    for pitch in range(128):
        song_note_times, user_note_times = song_notes[pitch], user_notes[pitch]

        # Case: No notes in song at this pitch
        if len(song_note_times) == 0:
            continue

        total_notes += len(song_note_times)

        # Case: User played no notes at this pitch
        if len(user_note_times) == 0:
            continue

        # nearest_times is a 2D array whose first dimension indexes correspond
        # to the song_note_times array, and its second dimension contains a
        # given song note time's sorted distances from all user note times.
        nearest_notes = []
        for note_time in song_note_times: # O(n*m*log(m))
            # Get a list of user time indexes sorted by distance from song time
            sorted_dist_idxs = np.argsort(
                np.abs(np.array(user_note_times) - note_time)
            )
            # Add user note times in sorted order to nearest_times 2D array
            nearest_notes.append(
                [user_note_times[d] for d in sorted_dist_idxs]
            )

        # Match all nearest unique pairs of user and song notes
        nearest_notes = unique_nearest_notes( # O(n^2*m)
            nearest_notes,
            song_note_times
        )

        for i, notes in enumerate(nearest_notes):
            # Song notes with no unique nearest user note are skipped
            # and automatically considered a miss
            if not notes:
                continue

            # Absolute distance from note for scoring
            dist = np.abs(notes[0] - song_note_times[i])

            # Perform scoring logic

            # Tolerance to account for swing and variance in preds
            if dist <= config["note_hit_window"]:
                notes_hit += 1
            elif dist <= config["note_hit_window"] * 2:
                # Deduct from note score for inaccurate timing
                notes_hit += 1 - config["close_hit_penalty"]
            else: # If note time outside of tolerance window
                continue

            # Positive means dragging, negative means rushing
            swing_amt = notes[0] - song_note_times[i]
            note_swing_times.append(swing_amt)

    return notes_hit*100, notes_hit, total_notes, note_swing_times


def unique_nearest_notes(
    nearest_notes: list,
    song_notes: list
) -> list:
    """
    Get all unique nearest song note - user note pairs by iterating
    over song notes' nearest user note times and checking for 
    duplicates.
    """
    unique_pairs = False
    while not unique_pairs:
        for i in range(len(nearest_notes)-1):
            for j in range(i+1, len(nearest_notes)):
                # First song note has been removed
                if not nearest_notes[i]:
                    break
                # Second song note removed or nearest user notes are dissimilar
                if (not nearest_notes[j]
                    or nearest_notes[i][0] != nearest_notes[j][0]):
                    continue

                i_dist = np.abs(song_notes[i] - nearest_notes[i][0])
                j_dist = np.abs(song_notes[j] - nearest_notes[j][0])

                # The song note time with the larger distance has the user
                # note time deleted from its corresponding array, updating
                # index 0 to the next closest user note time.
                if i_dist > j_dist:
                    del nearest_notes[i][0]
                else:
                    del nearest_notes[j][0]

        # Check for duplicates
        freq = defaultdict(int)
        for t in nearest_notes:
            if t:
                freq[t[0]] += 1

        # End loop if no song notes are sharing the same nearest user note
        if not [t for t in freq if freq[t] > 1]:
            unique_pairs = True
    return nearest_notes

def process_recording(
    buffer: np.ndarray,
    position: int,
    preprocessed_song_notes: dict[int, list]
) -> tuple[int, float, int, list]:
    """
    Compare the user input recording's notes against the song's,
    returning the resultant score data.
    """
    assert isinstance(buffer, np.ndarray), "Audio buffer must be an ndarray."
    assert isinstance(position, int), "Position must be an int."
    assert isinstance(preprocessed_song_notes, dict), "Song notes must be a dictionary."

    # Offset user note times by size of data currently in the buffer
    time_offset = config["rec_buffer_size"]
    if not np.any(buffer[:config["rec_overlap_window_size"]]):
        buffer = buffer[config["rec_overlap_window_size"]:]
        time_offset = config["rec_overlap_window_size"]

    # Save recorded audio as a temp WAV file
    with tempfile.TemporaryFile(delete=False, suffix=".wav") as temp_recording:
        write_wav(temp_recording.name, config["rate"], buffer)
        print(f"\nCreated temp file: {temp_recording.name}")

        # Save predicted user notes to a temp CSV file
        user_notes_path = save_notes(temp_recording.name, temp=True)[0]

    score_data = (0,0,0)
    try:
        # Align user note event times to song position
        user_notes = csv_to_notes_dataframe(user_notes_path)
        user_notes["start_time_s"] += (
            (position/config["rate"]) - (time_offset/config["rate"])
        )

        # Convert user notes to dict of note-onset time lists
        user_notes = preprocess_note_data(
            user_notes,
            offset_latency=True,
        )

        # TESTING
        # print("USER notes:\n")
        # for k, v in user_notes.items():
        #     if v:
        #         print(f"{k}: {v}")

        # print("\nSONG notes:\n")
        # for k, v in preprocessed_song_notes.items():
        #     if v:
        #         print(f"{k}: {v}")

        # Perform scoring
        score_data = compare_notes(
            user_notes,
            preprocessed_song_notes
        )
    finally:
        # Clean up
        os.remove(user_notes_path)
    return score_data
