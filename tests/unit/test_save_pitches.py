"""Module performing unit testing of the compare_pitches function."""

import pytest
from guitaraoke.save_pitches import save_pitches


def test_file_does_not_exist() -> None:
    """
    Assert exception is raised when save_pitches function is given a
    non-existent filepath.
    """
    with pytest.raises(AssertionError):
        save_pitches(path="i_do_not_exist")
