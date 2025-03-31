import pytest
from guitaraoke.compare_pitches import compare_pitches


@pytest.fixture
def pitches() -> tuple[dict[int, list], dict[int, list]]:
    user_pitches = {k: [] for k in range(128)}
    song_pitches = {k: [] for k in range(128)}
    user_pitches[60] = [0.1, 0.2, 0.3, 0.4, 0.52, 0.54, 0.61, 0.62, 0.63,
        0.78, 0.863, 0.91, 1.2, 1.31]
    song_pitches[60] = [0.05, 0.1, 0.2, 0.3, 0.46, 0.5, 0.511, 0.563, 0.57,
        0.58, 0.6, 0.624, 0.63, 1.0]
    return user_pitches, song_pitches

def test_compare_pitches(
    pitches: tuple[dict[int, list], dict[int, list]]
) -> None:
    result = compare_pitches(*pitches)

    assert result == (950, 9.5, 14)