"""Performs unit testing of the compare_notes function."""

import pytest
from guitaraoke.scoring_system import compare_notes
from guitaraoke.utils import read_config

config = read_config("Audio")

@pytest.fixture(name="note_dicts")
def note_dicts_fixture() -> tuple[dict[int, list], dict[int, list]]:
    """Create empty song and user note dictionaries for testing."""
    user_notes = {k: [] for k in range(128)}
    song_notes = {k: [] for k in range(128)}
    return (user_notes, song_notes)


def test_perfect_accuracy(
    note_dicts: tuple[dict[int, list], dict[int, list]]
) -> None:
    """
    Assert perfectly matching song notes and user notes result in
    100% accuracy.
    """
    user_notes, song_notes = note_dicts

    user_notes[60] = [0.7]
    user_notes[61] = [0.75, 0.8]

    song_notes[60] = [0.7]
    song_notes[61] = [0.75, 0.8]

    results = compare_notes(user_notes, song_notes)
    notes_hit, total_notes = results[1], results[2]
    assert notes_hit/total_notes == 1


def test_nearest_user_note_matched(
    note_dicts: tuple[dict[int, list], dict[int, list]]
) -> None:
    """
    Assert nearest user note to song note is matched, while the
    rest are discounted.
    """
    user_notes, song_notes = note_dicts

    user_notes[57] = [0.65, 0.698, 0.702, 0.71, 0.72, 0.75]

    song_notes[57] = [0.7]

    results = compare_notes(user_notes, song_notes)
    notes_hit, total_notes = results[1], results[2]
    assert notes_hit == 1 and total_notes == 1


def test_inside_note_hit_window(
    note_dicts: tuple[dict[int, list], dict[int, list]]
) -> None:
    """Assert notes within tolerance window are correctly counted."""
    user_notes, song_notes = note_dicts

    user_notes[45] = [0.701, 0.839 + config["note_hit_window"]]
    user_notes[50] = [0.881]

    song_notes[45] = [0.7 + config["note_hit_window"], 0.84]
    song_notes[50] = [0.88 + config["note_hit_window"]]

    results = compare_notes(user_notes, song_notes)
    notes_hit, total_notes = results[1], results[2]
    assert notes_hit/total_notes == 1


def test_outside_note_hit_window(
    note_dicts: tuple[dict[int, list], dict[int, list]]
) -> None:
    """Assert notes outside tolerance window are correctly missed."""
    user_notes, song_notes = note_dicts

    user_notes[45] = [0.699, 0.94 + (config["note_hit_window"]*2)]
    user_notes[50] = [0.879]

    song_notes[45] = [0.7 + (config["note_hit_window"]*2), 0.939]
    song_notes[50] = [0.88 + (config["note_hit_window"]*2)]

    results = compare_notes(user_notes, song_notes)
    notes_hit, total_notes = results[1], results[2]
    assert notes_hit/total_notes == 0
