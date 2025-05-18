"""Performs unit testing of the compare_notes function."""

import pytest
from guitaraoke.scoring_system import compare_notes


@pytest.fixture(name="note_dicts")
def note_dicts_fixture() -> tuple[dict[int, list], dict[int, list]]:
    """Create empty song and user note dictionaries for testing."""
    user_notes = {k: [] for k in range(128)}
    song_notes = {k: [] for k in range(128)}
    return (user_notes, song_notes)


def test_compare_notes(
    note_dicts: tuple[dict[int, list], dict[int, list]]
) -> None:
    """Assert compare_notes method returns correct score results."""
    user_notes, song_notes = note_dicts

    user_notes[60] = [0.1, 0.2, 0.3, 0.4, 0.52, 0.54, 0.61, 0.62, 0.63,
        0.78, 0.863, 0.91, 1.2, 1.31]
    song_notes[60] = [0.05, 0.1, 0.2, 0.3, 0.46, 0.5, 0.511, 0.563,
        0.57, 0.58, 0.6, 0.624, 0.63, 1.0]

    result = compare_notes(user_notes, song_notes)
    assert (result[0], result[1], result[2]) == (1000, 10, 14)
