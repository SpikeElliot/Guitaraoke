"""Module performing unit testing of the compare_pitches function."""

import pytest
from guitaraoke.save_pitches import save_pitches


def test_file_does_not_exist() -> None:
    """Assert exception is raised when given a non-existent file path."""
    with pytest.raises(AssertionError):
        save_pitches(path="i_do_not_exist")
