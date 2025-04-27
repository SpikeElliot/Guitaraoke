"""Performs unit testing of the compare_pitches function."""

import pytest
from guitaraoke.scoring_system import compare_pitches


@pytest.fixture(name="pitch_dicts")
def pitch_dicts_fixture() -> tuple[dict[int, list], dict[int, list]]:
    """Create empty song and user pitch dictionaries for testing."""
    user_pitches = {k: [] for k in range(128)}
    song_pitches = {k: [] for k in range(128)}
    return (user_pitches, song_pitches)

def test_compare_pitches(
    pitch_dicts: tuple[dict[int, list], dict[int, list]]
) -> None:
    """Assert compare_pitches method returns correct score results."""
    user_pitches, song_pitches = pitch_dicts

    user_pitches[60] = [0.1, 0.2, 0.3, 0.4, 0.52, 0.54, 0.61, 0.62, 0.63,
        0.78, 0.863, 0.91, 1.2, 1.31]
    song_pitches[60] = [0.05, 0.1, 0.2, 0.3, 0.46, 0.5, 0.511, 0.563,
        0.57, 0.58, 0.6, 0.624, 0.63, 1.0]

    result = compare_pitches(user_pitches, song_pitches)
    assert result == (1000, 10, 14)
