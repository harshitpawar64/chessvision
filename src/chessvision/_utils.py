from pathlib import Path

import numpy as np
from PIL import Image


def to_pil_image(image: Image.Image | Path | str | np.ndarray) -> Image.Image:
    if isinstance(image, (Path, str)):
        with Image.open(image) as img:
            return img.convert("RGB")
    if isinstance(image, np.ndarray):
        return Image.fromarray(image).convert("RGB")

    return image.convert("RGB")
