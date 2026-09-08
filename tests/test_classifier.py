import urllib.error
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest
from PIL import Image

from chessvision.classifier import PieceClassifier

classifier = PieceClassifier()


def test_predict_square() -> None:
    prediction = classifier.predict_square("assets/square.png")
    assert prediction.label == "bN"


def test_predict_square_pil() -> None:
    img = Image.open("assets/square.png")
    prediction = classifier.predict_square(img)
    assert prediction.label == "bN"


def test_predict_square_arr() -> None:
    img = Image.open("assets/square.png")
    arr = np.array(img)
    prediction_arr = classifier.predict_square(arr)
    assert prediction_arr.label == "bN"


def test_predict_squares_batch() -> None:
    predictions = classifier.predict_squares(["assets/square.png", "assets/square.png"])
    assert len(predictions) == 2
    assert all(prediction.label == "bN" for prediction in predictions)


def test_predict_squares_empty() -> None:
    assert classifier.predict_squares([]) == []


def test_classifier_download_success(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        "chessvision.classifier.urllib.request.urlretrieve",
        MagicMock(side_effect=lambda url, filename: filename.write_text("dummy model")),
    )

    model_path = PieceClassifier.get_model_path(cache_dir=tmp_path)
    assert model_path == tmp_path / "chess_piece_classifier.onnx"
    assert model_path.exists()


def test_classifier_download_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:

    monkeypatch.setattr(
        "chessvision.classifier.urllib.request.urlretrieve",
        MagicMock(side_effect=urllib.error.URLError("Network error")),
    )

    with pytest.raises(RuntimeError, match="Failed to download model"):
        PieceClassifier.get_model_path(cache_dir=tmp_path)

    assert not (tmp_path / "chess_piece_classifier.tmp").exists()
