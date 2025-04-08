"""
Module providing a ScoringSystem class that performs karaoke-style user
scoring.
"""

import os
import tempfile
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy.io.wavfile import write as write_wav
from config import RATE, REC_BUFFER_SIZE
from guitaraoke.save_pitches import save_pitches
from guitaraoke.utils import preprocess_pitch_data, csv_to_pitches_dataframe


class ScoringSystem():
    """
    Performs user scoring logic by comparing user and song predicted notes.
    """
    NOTE_HIT_WINDOW = 0.05 # 50 ms tolerance for timing of note

    def __init__(self, song_pitches: pd.DataFrame) -> None:
        """
        The constructor for the ScoringSystem class.
        """
        self.song_pitches = song_pitches

    def compare_pitches(
        self,
        user_pitches: dict[int, list],
        song_pitches: dict[int, list]
    ) -> tuple[int, float, int]:
        """
        Take two dictionaries containing 128 arrays (one for each MIDI pitch), 
        find the shortest unique distances between each user and song note, 
        and return the resultant score information.

        Parameters
        ----------
        user_pitches, song_pitches : dict[int, list]
            A dictionary converted from a pandas DataFrame containing a list of note
            event times for each possible MIDI pitch predicted from an audio file.
        
        Returns
        -------
        tuple[int, float, int]
            The user score, number of notes hit by the user, and total number
            of notes.
        """
        total_notes = 0
        notes_hit = 0

        # Iterate over user and song note events for all 128 MIDI pitches
        for note in range(128):
            song_note_times, user_note_times = song_pitches[note], user_pitches[note]

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
            nearest_notes = self.unique_nearest_notes( # O(n^2*m)
                nearest_notes,
                song_note_times
            )

            for i, notes, in enumerate(nearest_notes):
                # Song notes with no unique nearest user note are passed
                # and automatically considered a miss
                if not notes:
                    pass

                dist = np.abs(notes[0] - song_note_times[i])

                # Perform scoring logic
                if dist <= self.NOTE_HIT_WINDOW:
                    notes_hit += 1
                elif dist <= self.NOTE_HIT_WINDOW * 2:
                    score_penalty = (
                        0.5 * ((dist - self.NOTE_HIT_WINDOW)
                        / self.NOTE_HIT_WINDOW)
                    )
                    notes_hit += 1 - score_penalty

        return (round(notes_hit * 100), notes_hit, total_notes)

    def unique_nearest_notes(
        self,
        sorted_user_times: list,
        song_times: list
    ) -> list:
        """
        Get all unique nearest song note - user note pairs by iterating
        over song notes' nearest user note times and checking for duplicates.
        """
        unique_pairs = False
        while not unique_pairs:
            for i in range(len(sorted_user_times)-1):
                for j in range(i+1, len(sorted_user_times)):
                    # First song note has been removed
                    if not sorted_user_times[i]:
                        break
                    # Second song note removed or nearest user notes are dissimilar
                    if (not sorted_user_times[j]
                        or sorted_user_times[i][0] != sorted_user_times[j][0]):
                        continue

                    i_dist = np.abs(song_times[i] - sorted_user_times[i][0])
                    j_dist = np.abs(song_times[j] - sorted_user_times[j][0])

                    # The song note time with the larger distance has the user
                    # note time deleted from its corresponding array, updating
                    # index 0 to the next closest user note time.
                    if i_dist > j_dist:
                        del sorted_user_times[i][0]
                    else:
                        del sorted_user_times[j][0]

            # Check for duplicates
            freq = defaultdict(int)
            for t in sorted_user_times:
                if t:
                    freq[t[0]] += 1

            # End loop if no song notes are sharing the same nearest user note
            if not [t for t in freq if freq[t] > 1]:
                unique_pairs = True
        return sorted_user_times

    def _process_recording(self, buffer: np.ndarray, position: int) -> None:
        """
        Converts the user input recording into a MIDI file and compares the
        user's predicted pitches to the audio file's aligned at the correct
        time. The resultant score data is sent to the GUI.
        """
        # Save recorded audio as a temp WAV file
        with tempfile.TemporaryFile(delete=False, suffix=".wav") as temp_recording:
            write_wav(temp_recording.name, RATE, buffer)
            print(f"\nCreated temp file: {temp_recording.name}")

            # Save predicted user pitches to a temp CSV file
            user_pitches_path = save_pitches(temp_recording.name, temp=True)[0]

        try:
            # Align user note event times to current song position
            user_pitches = csv_to_pitches_dataframe(user_pitches_path)
            user_pitches["start_time_s"] += position/RATE - (REC_BUFFER_SIZE/RATE)

            # Convert user and song pitches to dicts of note event sequences
            user_pitches = preprocess_pitch_data(user_pitches)
            song_pitches = preprocess_pitch_data(
                self.song_pitches,
                slice_start=position-(REC_BUFFER_SIZE/RATE),
                slice_end=position
            )

            # TESTING
            # print("user pitches:",user_pitches)
            # print("song pitches:",song_pitches)

            # Perform scoring
            score_results = self.compare_pitches(user_pitches, song_pitches)
            print(score_results)
        finally:
            # Clean up
            os.remove(user_pitches_path)
