"""
Module providing a function to compare user and song pitches and return
resultant scoring data (score, notes hit, total notes).
"""

from collections import defaultdict
import numpy as np

NOTE_HIT_WINDOW = 0.05 # 50 ms tolerance for timing of note

def compare_pitches(
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
        nearest_times = []
        for time in song_note_times: # O(n*m*log(m))
            # Get a list of user time indexes sorted by distance from song time
            sorted_dist_idxs = np.argsort(
                np.abs(np.array(user_note_times) - time)
            )
            # Add user note times in sorted order to nearest_times 2D array
            nearest_times.append(
                [user_note_times[d] for d in sorted_dist_idxs]
            )

        # Match all nearest unique pairs of user and song notes
        nearest_times = unique_nearest_notes(
            nearest_times,
            song_note_times
        )

        # Append all note distances that will be scored to a new array. Any song
        # notes with no unique neighbour user notes were eliminated by the
        # above algorithm, and will automatically be considered a miss.
        distances = []
        for i, times in enumerate(nearest_times):
            if times:
                distances.append(np.abs(times[0] - song_note_times[i]))

        # Perform scoring logic
        for dist in distances:
            if dist <= NOTE_HIT_WINDOW:
                notes_hit += 1
            elif dist <= NOTE_HIT_WINDOW * 2:
                score_penalty = 0.5 * ((dist - NOTE_HIT_WINDOW) / NOTE_HIT_WINDOW)
                notes_hit += 1 - score_penalty

    return (round(notes_hit * 100), notes_hit, total_notes)

def unique_nearest_notes(
    sorted_user_times: list,
    song_times: list
) -> list:
    """
    Get all unique nearest song note - user note pairs by iterating
    over song notes' nearest user note times and checking for duplicates.
    """
    unique_pairs = False
    while not unique_pairs: # O(n^2*m)
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
