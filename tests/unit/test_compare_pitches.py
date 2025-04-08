"""Module performing unit testing of the compare_pitches function."""

import pytest
from guitaraoke.scoring_system import ScoringSystem


@pytest.fixture(name="scorer")
def scorer_fixture() -> ScoringSystem:
    """Create ScoringSystem class instance for testing compare_pitches method."""
    return ScoringSystem({k: [] for k in range(128)})

def test_compare_pitches(scorer: ScoringSystem) -> None:
    """Assert compare_pitches method returns correct score results."""
    scorer.song_pitches[60] = [0.05, 0.1, 0.2, 0.3, 0.46, 0.5, 0.511, 0.563,
        0.57, 0.58, 0.6, 0.624, 0.63, 1.0]

    user_pitches = {k: [] for k in range(128)}
    user_pitches[60] = [0.1, 0.2, 0.3, 0.4, 0.52, 0.54, 0.61, 0.62, 0.63,
        0.78, 0.863, 0.91, 1.2, 1.31]

    result = scorer.compare_pitches(
        user_pitches,
        scorer.song_pitches
    )

    assert result == (950, 9.5, 14)
