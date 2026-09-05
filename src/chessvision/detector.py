from pathlib import Path

import cv2
import numpy as np
from PIL import Image


class BoardDetector:
    def __init__(
        self, min_size_ratio: float = 0.10, max_size_ratio: float = 1.05
    ) -> None:
        self.min_size_ratio = min_size_ratio
        self.max_size_ratio = max_size_ratio

    def detect(self, image: Image.Image | Path | str | np.ndarray) -> list[Image.Image]:
        if isinstance(image, (Path, str)):
            img = Image.open(image).convert("RGB")
        elif isinstance(image, np.ndarray):
            img = Image.fromarray(image).convert("RGB")
        else:
            img = image.convert("RGB")

        gray = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2GRAY)

        height, width = gray.shape
        min_size = min(height, width) * self.min_size_ratio
        max_size = min(height, width) * self.max_size_ratio

        _, binary = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        candidates = []
        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                if (
                    min_size <= w <= max_size
                    and min_size <= h <= max_size
                    and 0.95 <= w / h <= 1.05
                    and gray[y : y + h, x : x + w].std() > 15
                ):
                    candidates.append((x, y, x + w, y + h))

        # Sort into reading order (top-to-bottom, left-to-right)
        candidates.sort(key=lambda b: (b[1] // ((b[3] - b[1]) // 2), b[0]))

        return [img.crop(bbox) for bbox in candidates]
