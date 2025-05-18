"""Performs unit testing of the separate_guitar function."""

import pytest
from guitaraoke.separate_guitar import separate_guitar
from guitaraoke.preload import preload_directories

preload_directories()

def test_nonexistent_file_error_raised() -> None:
    """Assert exception raised when given a non-existent file path."""
    with pytest.raises(AssertionError):
        separate_guitar(path="   ")


def test_path_type_error_raised() -> None:
    """Assert exception raised when given path value of wrong type."""
    with pytest.raises(AssertionError):
        separate_guitar(path=42)
