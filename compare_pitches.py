import numpy as np

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
def compare_pitches(user_pitches, song_pitches):
    """
    Take two dicts containing note event sequences for all possible MIDI pitches
    and compare note appearances and timings for each pitch, returning a score
    value and note accuracy information.

    Parameters
    ----------
    user_pitches, song_pitches : dict
        A dictionary converted from a pandas DataFrame containing a list of note
        event times for each possible MIDI pitch predicted from an audio file.
    
    Returns
    -------
    score_info : tuple of int
        The user score, number of notes hit by the user, and total number
        of notes.
    """
    total_notes = 0
    notes_hit = 0
    note_hit_window = 0.05 # 50 ms tolerance for timing of note

    for note in range(128): # 128 possible MIDI pitches
        user_note_events = user_pitches[note]
        song_note_events = song_pitches[note]
        total_notes += len(song_note_events)

        # Case: No notes in song
        if len(song_note_events) == 0:
            continue
        
        if len(user_note_events) == 0:
            # TODO: At some point the issue of the user not being able to play
            # the rhythm and lead notes concurrently needs to be addressed 
            # somehow to make scoring fairer
            continue

        # Case: Note events found in both sources
        for note_time in song_note_events:
            # Find difference in time between user notes and current song note
            compared_note_events = np.abs(np.array(user_note_events) - note_time)
            nearest_note_distance = np.min(compared_note_events) # Get nearest note

            if nearest_note_distance <= note_hit_window:
                notes_hit += 1
            elif nearest_note_distance <= note_hit_window * 2:
                score_penalty = 0.5 * ((nearest_note_distance - note_hit_window) / note_hit_window)
                notes_hit += 1 - score_penalty

    score = int(notes_hit * 100)
    score_info = (score, notes_hit, total_notes)
    return score_info