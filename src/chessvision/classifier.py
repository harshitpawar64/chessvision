import hashlib
import logging
import urllib.error
import urllib.request
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image
from platformdirs import user_cache_path

from chessvision._utils import to_pil_image
from chessvision.constants import IMAGE_SIZE, PIECE_CLASSES, PIECE_NAMES

logger = logging.getLogger(__name__)

MODEL_NAME = "chess_piece_classifier.onnx"
MODEL_SHA256 = "66de5d17f07b822fbb5957615c0880ce02a0cab977c83dafa033f3b71eb4a7fc"


@dataclass(frozen=True, slots=True)
class SquarePrediction:
    label: str
    confidence: float

    @property
    def name(self) -> str:
        return PIECE_NAMES[self.label]


class PieceClassifier:
    def __init__(self, model_path: Path | str | None = None) -> None:
        self.model_path = Path(model_path) if model_path else self.get_model_path()
        logger.debug("Initializing PieceClassifier with model: %s", self.model_path)

        self.session = ort.InferenceSession(self.model_path)
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

        self.classes = PIECE_CLASSES
        self.image_size = IMAGE_SIZE

    def predict_square(
        self, image: Image.Image | Path | str | np.ndarray
    ) -> SquarePrediction:
        tensor = np.expand_dims(self._preprocess_single(image), axis=0)
        raw_output = self.session.run([self.output_name], {self.input_name: tensor})[0]
        probs = np.asarray(raw_output, dtype=np.float32)[0]

        prediction_index = np.argmax(probs)

        label = self.classes[prediction_index]

        return SquarePrediction(label=label, confidence=probs[prediction_index])

    def predict_squares(
        self, images: Sequence[Image.Image | Path | str | np.ndarray]
    ) -> list[SquarePrediction]:
        if not images:
            return []
        logger.debug("Predicting batch of %d square(s)", len(images))
        batch = self._preprocess_batch(images)
        raw_output = self.session.run([self.output_name], {self.input_name: batch})[0]
        probs = np.asarray(raw_output, dtype=np.float32)
        prediction_indices = np.argmax(probs, axis=1)

        return [
            SquarePrediction(label=self.classes[index], confidence=probs[i, index])
            for i, index in enumerate(prediction_indices)
        ]

    @staticmethod
    def get_model_path(cache_dir: Path | str | None = None) -> Path:
        model_path = (
            Path(cache_dir)
            if cache_dir
            else user_cache_path("chessvision", appauthor=False, ensure_exists=True)
        ) / MODEL_NAME
        logger.debug("Checking model path: %s", model_path)

        if model_path.exists() and _verify_checksum(model_path, MODEL_SHA256):
            logger.debug("Model found in cache and SHA-256 verified (%s)", model_path)
            return model_path

        url = f"https://huggingface.co/harshitpawar64/chessvision/resolve/main/{MODEL_NAME}"
        logger.info("Downloading piece classifier model from %s", url)

        temp_path = model_path.with_suffix(".tmp")

        try:
            urllib.request.urlretrieve(url, temp_path)

            if not _verify_checksum(temp_path, MODEL_SHA256):
                raise ValueError("Checksum mismatch")

            temp_path.replace(model_path)
            logger.info("Successfully downloaded and verified model at %s", model_path)
        except (urllib.error.URLError, ValueError) as e:
            temp_path.unlink(missing_ok=True)
            raise RuntimeError(f"Failed to download model from {url}: {e}") from e

        return model_path

    def _preprocess_single(
        self, image: Image.Image | Path | str | np.ndarray
    ) -> np.ndarray:
        img = to_pil_image(image).resize(
            (self.image_size, self.image_size), Image.Resampling.BICUBIC
        )
        arr = np.asarray(img, dtype=np.float32) / 255.0
        return np.transpose(arr, (2, 0, 1))

    def _preprocess_batch(
        self, images: Sequence[Image.Image | Path | str | np.ndarray]
    ) -> np.ndarray:
        return np.stack([self._preprocess_single(img) for img in images], axis=0)


def _verify_checksum(path: Path, expected_sha256: str) -> bool:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest() == expected_sha256
