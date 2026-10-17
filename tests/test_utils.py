import hashlib
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest
from PIL import Image

from chessvision._utils import (
    MODEL_NAME,
    _verify_checksum,
    download_model,
    to_pil_image,
)

DUMMY_MODEL = b"dummy model"
DUMMY_SHA = hashlib.sha256(DUMMY_MODEL).hexdigest()


@pytest.fixture
def isolated_cache(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    cache_dir = tmp_path / "cache"
    monkeypatch.setattr("chessvision._utils.user_cache_path", lambda *a, **k: cache_dir)
    monkeypatch.setattr("chessvision._utils.MODEL_SHA256", DUMMY_SHA)
    return cache_dir


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


def test_verify_checksum(tmp_path: Path) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_bytes(DUMMY_MODEL)

    assert _verify_checksum(sample, DUMMY_SHA) is True
    assert _verify_checksum(sample, "invalid_hash") is False


def test_download_model_success(
    isolated_cache: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "chessvision._utils.urllib.request.urlretrieve",
        lambda url, filename: Path(filename).write_bytes(DUMMY_MODEL),
    )
    model_path = download_model(target_dir=tmp_path)
    assert model_path == tmp_path / MODEL_NAME
    assert model_path.read_bytes() == DUMMY_MODEL


def test_download_model_copy_from_cache(
    isolated_cache: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    isolated_cache.mkdir(parents=True, exist_ok=True)
    (isolated_cache / MODEL_NAME).write_bytes(DUMMY_MODEL)

    mock_retrieve = MagicMock()
    monkeypatch.setattr("chessvision._utils.urllib.request.urlretrieve", mock_retrieve)

    target_dir = tmp_path / "target"
    model_path = download_model(target_dir=target_dir)

    assert model_path == target_dir / MODEL_NAME
    assert model_path.read_bytes() == DUMMY_MODEL
    mock_retrieve.assert_not_called()


def test_download_model_already_exists(
    isolated_cache: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    model_path = tmp_path / MODEL_NAME
    model_path.write_bytes(DUMMY_MODEL)

    mock_retrieve = MagicMock()
    monkeypatch.setattr("chessvision._utils.urllib.request.urlretrieve", mock_retrieve)

    assert download_model(target_dir=tmp_path) == model_path
    mock_retrieve.assert_not_called()


def test_download_model_failure(
    isolated_cache: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "chessvision._utils.urllib.request.urlretrieve",
        MagicMock(side_effect=urllib.error.URLError("Network error")),
    )
    with pytest.raises(RuntimeError, match="Failed to download model"):
        download_model(target_dir=tmp_path)

    assert not (tmp_path / f"{MODEL_NAME}.tmp").exists()


def test_download_model_checksum_mismatch(
    isolated_cache: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "chessvision._utils.urllib.request.urlretrieve",
        lambda url, filename: Path(filename).write_text("corrupted content"),
    )
    with pytest.raises(RuntimeError, match="Checksum mismatch"):
        download_model(target_dir=tmp_path)

    assert not (tmp_path / f"{MODEL_NAME}.tmp").exists()
