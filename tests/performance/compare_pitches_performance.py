"""Performs a performance test of the compare_pitches function."""

import time
from guitaraoke.scoring_system import compare_pitches

user_pitches = {k: [] for k in range(128)}
song_pitches = {k: [] for k in range(128)}
for i in range(29):
    user_pitches[20+i].append(i*0.068)

    song_pitches[20+i].append(i*0.068)
    song_pitches[25+i].append(i*0.068)

time1 = time.perf_counter()
result = compare_pitches(user_pitches,song_pitches)
time2 = time.perf_counter()
print("Worst Case Execution Time:", time2-time1)
