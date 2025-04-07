"""Module performing unit testing of the separate_guitar function."""

import pytest
from guitaraoke.separate_guitar import separate_guitar


def test_nonexistent_file_error_raised() -> None:
    """Assert exception is raised when given a non-existent file path."""
    with pytest.raises(AssertionError):
        separate_guitar(path="i_do_not_exist")
