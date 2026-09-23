import pytest

import chessvision


def test_unknown_attribute_raises_attribute_error() -> None:
    with pytest.raises(
        AttributeError,
        match="module 'chessvision' has no attribute 'non_existent_attribute'",
    ):
        _ = chessvision.non_existent_attribute
