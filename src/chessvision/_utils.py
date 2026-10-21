from importlib.resources import files
from pathlib import Path

import numpy as np
from PIL import Image


def to_pil_image(image: Image.Image | Path | str | np.ndarray) -> Image.Image:
    if isinstance(image, (Path, str)):
        with Image.open(image) as img:
            return img.convert("RGB")
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)

    return image if image.mode == "RGB" else image.convert("RGB")


def get_model_path() -> Path:
    resource = files("chessvision.models") / "chess_piece_classifier.onnx"
    if isinstance(resource, Path) and resource.is_file():
        return resource

    raise FileNotFoundError(
        f"Bundled piece classifier model was not found at {resource}."
    )
