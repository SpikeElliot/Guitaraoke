"""Performs a performance test of the compare_notes function."""

import time
from guitaraoke.scoring_system import compare_notes

user_notes = {k: [] for k in range(128)}
song_notes = {k: [] for k in range(128)}
for i in range(29):
    user_notes[20+i].append(i*0.068)

    song_notes[20+i].append(i*0.068)
    song_notes[25+i].append(i*0.068)

time1 = time.perf_counter()
result = compare_notes(user_notes,song_notes)
time2 = time.perf_counter()
print("Worst Case Execution Time:", time2-time1)
