"""Performs unit testing of the save_notes function."""

import pytest
from guitaraoke.save_notes import save_notes
from guitaraoke.preload import preload_directories

preload_directories()

def test_nonexistent_file_error_raised() -> None:
    """Assert exception raised when given a non-existent file path."""
    with pytest.raises(AssertionError):
        save_notes(path="   ")


def test_path_type_error_raised() -> None:
    """Assert exception raised when given path value of wrong type."""
    with pytest.raises(AssertionError):
        save_notes(path=42)
