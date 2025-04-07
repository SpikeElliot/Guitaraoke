"""Module performing unit testing of the compare_pitches function."""

import pytest
from guitaraoke.save_pitches import save_pitches


def test_nonexistent_file_error_raised() -> None:
    """Assert exception is raised when given a non-existent file path."""
    with pytest.raises(AssertionError):
        save_pitches(path="i_do_not_exist")
