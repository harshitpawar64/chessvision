import urllib.error
import urllib.request
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image
from platformdirs import user_cache_path

from chessvision.constants import PIECE_CLASSES


@dataclass(frozen=True, slots=True)
class SquarePrediction:
    label: str
    confidence: float


class PieceClassifier:
    def __init__(self) -> None:
        self.model_path = self._get_model_path()

        self.session = ort.InferenceSession(str(self.model_path))
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

        metadata = self.session.get_modelmeta().custom_metadata_map

        self.image_size = int(metadata["image_size"])

        self.mean = np.array(
            [float(x) for x in metadata["mean"].split(",")], dtype=np.float32
        )
        self.std = np.array(
            [float(x) for x in metadata["std"].split(",")], dtype=np.float32
        )

    def predict_square(
        self, image: Image.Image | Path | str | np.ndarray
    ) -> SquarePrediction:
        tensor = np.expand_dims(self._preprocess_single(image), axis=0)
        raw_output = self.session.run([self.output_name], {self.input_name: tensor})[0]
        logits = np.asarray(raw_output, dtype=np.float32)
        probs = self._softmax(logits)[0]
        prediction_index = np.argmax(probs)

        label = PIECE_CLASSES[prediction_index]

        return SquarePrediction(label=label, confidence=float(probs[prediction_index]))

    def predict_squares(
        self, images: Sequence[Image.Image | Path | str | np.ndarray]
    ) -> list[SquarePrediction]:
        if not images:
            return []
        batch = self._preprocess_batch(images)
        raw_output = self.session.run([self.output_name], {self.input_name: batch})[0]
        logits = np.asarray(raw_output, dtype=np.float32)
        probs = self._softmax(logits)
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
        if isinstance(image, (Path, str)):
            img = Image.open(image).convert("RGB")
        elif isinstance(image, np.ndarray):
            img = Image.fromarray(image).convert("RGB")
        else:
            img = image.convert("RGB")

        img = img.resize((self.image_size, self.image_size), Image.Resampling.BICUBIC)
        arr = (np.asarray(img, dtype=np.float32) / 255.0 - self.mean) / self.std
        return np.transpose(arr, (2, 0, 1))

    def _preprocess_batch(
        self, images: Sequence[Image.Image | Path | str | np.ndarray]
    ) -> np.ndarray:
        return np.stack([self._preprocess_single(img) for img in images], axis=0)

    @staticmethod
    def _softmax(logits: np.ndarray) -> np.ndarray:
        shifted = logits - np.max(logits, axis=-1, keepdims=True)
        exp_vals = np.exp(shifted)
        return exp_vals / np.sum(exp_vals, axis=-1, keepdims=True)

    @staticmethod
    def _get_model_path() -> Path:
        MODEL_NAME = "chess_piece_classifier.onnx"

        model_path = user_cache_path("chessvision", ensure_exists=True) / MODEL_NAME

        if model_path.exists():
            return model_path

        url = f"https://huggingface.co/harshitpawar64/chessvision/resolve/main/{MODEL_NAME}"

        temp_path = model_path.with_suffix(".tmp")

        try:
            urllib.request.urlretrieve(url, temp_path)
            temp_path.replace(model_path)
        except urllib.error.URLError as e:
            temp_path.unlink(missing_ok=True)
            raise RuntimeError(f"Failed to download model from {url}: {e}") from e

        return model_path
