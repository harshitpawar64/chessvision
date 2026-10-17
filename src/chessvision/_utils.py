import hashlib
import logging
import shutil
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image
from platformdirs import user_cache_path

logger = logging.getLogger(__name__)

MODEL_NAME = "chess_piece_classifier.onnx"
MODEL_SHA256 = "66de5d17f07b822fbb5957615c0880ce02a0cab977c83dafa033f3b71eb4a7fc"


def to_pil_image(image: Image.Image | Path | str | np.ndarray) -> Image.Image:
    if isinstance(image, (Path, str)):
        with Image.open(image) as img:
            return img.convert("RGB")
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)

    return image if image.mode == "RGB" else image.convert("RGB")


def download_model(target_dir: Path | str | None = None) -> Path:
    cached_path = (
        user_cache_path("chessvision", appauthor=False, ensure_exists=True) / MODEL_NAME
    )
    model_path = Path(target_dir) / MODEL_NAME if target_dir else cached_path
    model_path.parent.mkdir(parents=True, exist_ok=True)

    if model_path.exists() and _verify_checksum(model_path, MODEL_SHA256):
        logger.debug("Model found in cache and SHA-256 verified (%s)", model_path)
        return model_path

    if (
        model_path != cached_path
        and cached_path.exists()
        and _verify_checksum(cached_path, MODEL_SHA256)
    ):
        logger.debug(
            "Model found in cache (%s) and SHA-256 verified. Copying to %s",
            cached_path,
            model_path,
        )
        shutil.copy2(cached_path, model_path)
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


def _verify_checksum(path: Path, expected_sha256: str) -> bool:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest() == expected_sha256
