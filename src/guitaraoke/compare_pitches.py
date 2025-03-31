import numpy as np
from collections import defaultdict

# TODO: Testing and improvement. Many notes aren't being accurately detected,
# there may be significant input latency offsetting all user notes by varying
# degree, and algorithm needs to be reworked in general to better capture user
# performance.
#
# Potential improvement is to consider note off events as well as notes on,
# to better gauge timing and how well the user is holding the notes.
#
# Due to overlapping recordings, duplicate notes are being counted every loop.
# A method of filtering duplicates from score calculations needs to be found.
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
    note_hit_window = 0.05 # 50 ms tolerance for timing of note

    # Iterate over user and song note events for all 128 MIDI pitches
    for note in range(128):
        song_note_times, user_note_times = song_pitches[note], user_pitches[note]

        # Case: No notes in song
        if len(song_note_times) == 0: continue

        total_notes += len(song_note_times)
        
        # TODO: At some point the issue of the user not being able to play
        # the rhythm and lead notes concurrently needs to be addressed 
        # somehow to make scoring fairer
        if len(user_note_times) == 0: continue

        # Take the shortest distances between note sequences: this allows
        # every song note to match with its nearest unique user note, as
        # opposed to simply pairing notes by index order.

        # nearest_times is a 2D array whose first dimension indexes correspond
        # to the song_note_times array, and its second dimension contains a
        # given song note time's distances from all user note times.
        nearest_times = []
        for time in song_note_times:
            # Get a list of user time indexes sorted by distance from song time
            sorted_dist_idxs = np.argsort(
                np.abs(np.array(user_note_times) - time)
            )
            # Add user note times in sorted order to nearest_times 2D array
            nearest_times.append(
                [user_note_times[d] for d in sorted_dist_idxs]
            )
        
        # Ensure all user notes are paired to a unique song note by iterating
        # over song notes nearest times and checking for duplicates.
        unique_pairs = False
        while not unique_pairs:
            for i in range(len(nearest_times)-1):
                for j in range(i+1, len(nearest_times)):
                    # First song note has been removed
                    if not nearest_times[i]:
                        break 
                    # Second song note removed or nearest user notes are dissimilar
                    if (not nearest_times[j]
                        or nearest_times[i][0] != nearest_times[j][0]):
                        continue

                    i_dist = np.abs(song_note_times[i] - nearest_times[i][0])
                    j_dist = np.abs(song_note_times[j] - nearest_times[j][0])

                    # The song note time with the larger distance has the user
                    # note time deleted from its corresponding array, updating 
                    # index 0 to the next closest user note time. 
                    if i_dist > j_dist:
                        del nearest_times[i][0]
                    else:
                        del nearest_times[j][0]

            # Check for duplicates
            freq = defaultdict(int)
            for t in nearest_times:
                if t: freq[t[0]] += 1

            # End loop if no song notes are sharing the same nearest user note
            if not [t for t in freq if freq[t] > 1]: unique_pairs = True
                
        # Append all note distances that will be scored to a new array. Any song
        # notes with no unique neighbour user notes were eliminated by the
        # above algorithm, and will automatically be considered a miss.
        distances = []
        for i, times in enumerate(nearest_times):
            if times: distances.append(np.abs(times[0] - song_note_times[i]))
        
        # Perform scoring logic
        for dist in distances:
            if dist <= note_hit_window:
                notes_hit += 1
            elif dist <= note_hit_window * 2:
                score_penalty = 0.5 * ((dist - note_hit_window) / note_hit_window)
                notes_hit += 1 - score_penalty

    score = round(notes_hit * 100)
    return (score, notes_hit, total_notes)