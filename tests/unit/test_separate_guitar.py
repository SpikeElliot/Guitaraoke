"""Module performing unit testing of the separate_guitar function."""

import pytest
from guitaraoke.separate_guitar import separate_guitar


def test_file_does_not_exist() -> None:
    """
    Assert exception is raised when separate_guitar function is given a
    non-existent filepath.
    """
    with pytest.raises(AssertionError):
        separate_guitar(path="i_do_not_exist")
