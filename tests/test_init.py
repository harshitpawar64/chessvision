import pytest

import chessvision


def test_unknown_attribute_raises_attribute_error() -> None:
    with pytest.raises(
        AttributeError,
        match="module 'chessvision' has no attribute 'non_existent_attribute'",
    ):
        _ = chessvision.non_existent_attribute


def test_dir() -> None:
    dir_attrs = set(dir(chessvision))

    assert set(chessvision.__all__) < dir_attrs
    assert {"__all__", "__file__", "__name__"} < dir_attrs
