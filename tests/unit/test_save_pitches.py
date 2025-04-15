"""Performs unit testing of the save_pitches function."""

import pytest
from guitaraoke.save_pitches import save_pitches


def test_nonexistent_file_error_raised() -> None:
    """Assert exception is raised when given a non-existent file path."""
    with pytest.raises(AssertionError):
        save_pitches(path="   ")

def test_path_type_error_raised() -> None:
    """Assert exception is raised when given path value of the wrong type."""
    with pytest.raises(AssertionError):
        save_pitches(path=42)
