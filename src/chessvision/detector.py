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

        threshold_mode = (
            cv2.THRESH_BINARY if gray.mean() < 128 else cv2.THRESH_BINARY_INV
        )
        _, binary = cv2.threshold(gray, 160, 255, threshold_mode)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
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
                    and self._is_8x8_board(gray[y : y + h, x : x + w])
                ):
                    candidates.append((x, y, x + w, y + h))

        # Sort into reading order (top-to-bottom, left-to-right)
        candidates.sort(key=lambda box: (box[1] // ((box[3] - box[1]) // 2), box[0]))

        return [img.crop(bbox) for bbox in candidates]

    @staticmethod
    def _is_8x8_board(crop: np.ndarray) -> bool:
        resized_crop = cv2.resize(crop, (64, 64), interpolation=cv2.INTER_AREA)
        squares = resized_crop.reshape(8, 8, 8, 8).swapaxes(1, 2)

        medians = np.median(squares, axis=(2, 3))
        parity = (np.arange(8)[:, None] + np.arange(8)) % 2 == 0
        contrast = abs(np.median(medians[parity]) - np.median(medians[~parity]))

        dx = np.diff(resized_crop, axis=1).mean(axis=0)
        dy = np.diff(resized_crop, axis=0).mean(axis=1)
        grid_index = np.arange(7, 63, 8)
        mid_index = np.arange(3, 63, 8)

        ratio_x = dx[grid_index].mean() / (dx[mid_index].mean() + 1e-5)
        ratio_y = dy[grid_index].mean() / (dy[mid_index].mean() + 1e-5)

        return contrast > 20 and min(ratio_x, ratio_y) > 1.5
