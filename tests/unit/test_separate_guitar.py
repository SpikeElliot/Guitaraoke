import pytest
from guitaraoke.separate_guitar import separate_guitar


def test_file_does_not_exist() -> None:
    with pytest.raises(AssertionError):
        separate_guitar(path="i_do_not_exist")