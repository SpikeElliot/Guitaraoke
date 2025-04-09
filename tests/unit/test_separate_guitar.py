"""Module performing unit testing of the separate_guitar function."""

import pytest
from guitaraoke.separate_guitar import separate_guitar


def test_nonexistent_file_error_raised() -> None:
    """Assert exception is raised when given a non-existent file path."""
    with pytest.raises(AssertionError):
        separate_guitar(path="   ")

def test_path_type_error_raised() -> None:
    """Assert exception is raised when given path value of the wrong type."""
    with pytest.raises(AssertionError):
        separate_guitar(path=42)
