import pytest
from guitaraoke.save_pitches import save_pitches


def test_file_does_not_exist() -> None:
    with pytest.raises(AssertionError):
        save_pitches(path="i_do_not_exist")