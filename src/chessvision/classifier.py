import logging
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from chessvision._utils import get_model_path, to_pil_image
from chessvision.constants import PIECE_CLASSES, PIECE_NAMES, SQUARE_SIZE

logger = logging.getLogger(__name__)

__all__ = ["PieceClassifier", "SquarePrediction"]


@dataclass(frozen=True, slots=True)
class SquarePrediction:
    label: str
    confidence: float

    @property
    def name(self) -> str:
        return PIECE_NAMES[self.label]


class PieceClassifier:
    def __init__(self, model_path: Path | str | None = None) -> None:
        self.model_path = model_path or get_model_path()
        logger.debug("Initializing PieceClassifier with model: %s", self.model_path)

        self.net = cv2.dnn.readNetFromONNX(self.model_path)

    def predict_square(
        self, image: Image.Image | Path | str | np.ndarray
    ) -> SquarePrediction:
        return self.predict_squares([image])[0]

    def predict_squares(
        self, images: Sequence[Image.Image | Path | str | np.ndarray]
    ) -> list[SquarePrediction]:
        if not images:
            return []
        logger.debug("Predicting batch of %d square(s)", len(images))
        batch = self._preprocess_batch(images)
        self.net.setInput(batch)
        probs = self.net.forward()
        prediction_indices = np.argmax(probs, axis=1)

        return [
            SquarePrediction(
                label=PIECE_CLASSES[index], confidence=float(probs[i, index])
            )
            for i, index in enumerate(prediction_indices)
        ]

    def _preprocess_single(
        self, image: Image.Image | Path | str | np.ndarray
    ) -> np.ndarray:
        img = to_pil_image(image).resize(
            (SQUARE_SIZE, SQUARE_SIZE), Image.Resampling.BICUBIC
        )
        arr = np.asarray(img, dtype=np.float32) / 255.0
        return np.transpose(arr, (2, 0, 1))

    def _preprocess_batch(
        self, images: Sequence[Image.Image | Path | str | np.ndarray]
    ) -> np.ndarray:
        return np.stack([self._preprocess_single(img) for img in images], axis=0)
