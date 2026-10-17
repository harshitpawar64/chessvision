from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from chessvision._utils import get_model_path, to_pil_image


def test_to_pil_image(tmp_path: Path) -> None:
    img_path = tmp_path / "test.png"
    Image.new("RGB", (10, 10)).save(img_path)

    assert to_pil_image(img_path).mode == "RGB"
    assert to_pil_image(str(img_path)).mode == "RGB"
    assert to_pil_image(np.zeros((10, 10, 3), dtype=np.uint8)).mode == "RGB"

    rgba = Image.new("RGBA", (10, 10))
    assert to_pil_image(rgba).mode == "RGB"

    rgb = Image.new("RGB", (10, 10))
    assert to_pil_image(rgb) is rgb


def test_get_model_path_exists() -> None:
    model_path = get_model_path()
    assert model_path.is_file()
    assert model_path.suffix == ".onnx"


def test_get_model_path_not_found(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        "chessvision._utils.files", lambda pkg: tmp_path / "missing.onnx"
    )

    with pytest.raises(
        FileNotFoundError, match="Bundled piece classifier model was not found"
    ):
        get_model_path()
