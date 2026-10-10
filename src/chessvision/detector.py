import logging
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from chessvision._utils import to_pil_image
from chessvision.constants import BOARD_SIZE

logger = logging.getLogger(__name__)

__all__ = ["BoardDetector", "DetectedBoard"]

_KERNEL_3X3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
_CHECKERBOARD_MASK = (np.arange(8)[:, None] + np.arange(8)) % 2 == 0
_GRID_INDICES = np.arange(7, 63, 8)
_MID_INDICES = np.arange(3, 63, 8)

_ASPECT_RATIO_MIN = 0.75
_ASPECT_RATIO_MAX = 1.35
_FILL_RATIO_THRESHOLD = 0.95
_POLYGON_EPSILONS = (0.015, 0.02, 0.03)
_NMS_THRESHOLD = 0.3
_MARGIN_RATIO = 0.15
_DARK_PIXEL_THRESHOLD = 120
_LINE_DENSITY_THRESHOLD = 0.45
_FULL_IMAGE_ASPECT_RATIO_MIN = 0.95
_FULL_IMAGE_ASPECT_RATIO_MAX = 1.05


@dataclass(frozen=True, slots=True)
class DetectedBoard:
    image: Image.Image
    box: tuple[int, int, int, int]
    score: float = 0.0


class BoardDetector:
    def __init__(
        self, min_size_ratio: float = 0.10, max_size_ratio: float = 1.05
    ) -> None:
        self.min_size_ratio = min_size_ratio
        self.max_size_ratio = max_size_ratio

    def detect(
        self, image: Image.Image | Path | str | np.ndarray
    ) -> list[DetectedBoard]:
        img = to_pil_image(image)
        arr = np.asarray(img)
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

        height, width = gray.shape
        logger.debug("Starting board detection on image (%dx%d)", width, height)

        min_dim = min(height, width)
        min_size = min_dim * self.min_size_ratio
        max_size = min_dim * self.max_size_ratio

        threshold_mode = (
            cv2.THRESH_BINARY if gray.mean() < 128 else cv2.THRESH_BINARY_INV
        )
        _, binary = cv2.threshold(gray, 0, 255, threshold_mode | cv2.THRESH_OTSU)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, _KERNEL_3X3)
        contours_otsu, _ = cv2.findContours(
            binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )

        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 40, 150)
        dilated = cv2.dilate(edges, _KERNEL_3X3, iterations=2)
        contours_canny, _ = cv2.findContours(
            dilated, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )

        candidates = []

        for contour in (*contours_otsu, *contours_canny):
            bx, by, bw, bh = cv2.boundingRect(contour)
            if not (min_size <= bw <= max_size and min_size <= bh <= max_size):
                continue
            if not (_ASPECT_RATIO_MIN <= bw / bh <= _ASPECT_RATIO_MAX):
                continue

            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            fill_ratio = hull_area / (bw * bh + 1e-5)

            if fill_ratio >= _FILL_RATIO_THRESHOLD:
                sub_gray = gray[by : by + bh, bx : bx + bw]
                x1, y1, x2, y2 = self._snap_to_board(sub_gray)
                cropped_gray = sub_gray[y1:y2, x1:x2]
                if score := self._is_8x8_board(cropped_gray):
                    crop_pil = img.crop((bx + x1, by + y1, bx + x2, by + y2))
                    candidates.append(
                        DetectedBoard(
                            image=crop_pil,
                            box=(bx + x1, by + y1, x2 - x1, y2 - y1),
                            score=score,
                        )
                    )
            elif fill_ratio >= 0.5:
                peri = cv2.arcLength(hull, True)
                for eps in _POLYGON_EPSILONS:
                    approx = cv2.approxPolyDP(hull, eps * peri, True)
                    if len(approx) == 4 and cv2.isContourConvex(approx):
                        pts = approx.reshape(4, 2).astype(np.float32)
                        dewarped = self._dewarp_quad(arr, pts, BOARD_SIZE)
                        if score := self._is_8x8_board(dewarped):
                            candidates.append(
                                DetectedBoard(
                                    image=Image.fromarray(dewarped),
                                    box=(bx, by, bw, bh),
                                    score=score,
                                )
                            )
                            break

        if candidates:
            boxes = [c.box for c in candidates]
            scores = [c.score for c in candidates]
            indices = cv2.dnn.NMSBoxes(
                boxes, scores, score_threshold=0.0, nms_threshold=_NMS_THRESHOLD
            )
            selected = [candidates[i] for i in indices]
            logger.debug(
                "NMS selected %d chessboard candidate(s) from %d",
                len(selected),
                len(candidates),
            )
            selected.sort(key=lambda b: (b.box[1] // max(b.box[3] // 2, 1), b.box[0]))
            return selected

        logger.debug("No candidates found via contours; evaluating full-image fallback")
        if (
            _FULL_IMAGE_ASPECT_RATIO_MIN
            <= width / height
            <= _FULL_IMAGE_ASPECT_RATIO_MAX
            and (score := self._is_8x8_board(gray))
        ):
            logger.debug("Full image verified as 8x8 chessboard")
            return [DetectedBoard(image=img, box=(0, 0, width, height), score=score)]

        logger.debug("No chessboard detected in image")
        return []

    @staticmethod
    def _is_8x8_board(crop: np.ndarray) -> float | None:
        if min(crop.shape[:2]) < 64:
            return None

        if crop.ndim == 3:
            crop = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)

        resized_crop = cv2.resize(crop, (64, 64), interpolation=cv2.INTER_AREA)
        squares = resized_crop.reshape(8, 8, 8, 8).swapaxes(1, 2)

        medians = np.median(squares, axis=(2, 3))
        contrast = float(
            abs(
                np.median(medians[_CHECKERBOARD_MASK])
                - np.median(medians[~_CHECKERBOARD_MASK])
            )
        )

        if contrast <= 20:
            return None

        if contrast > 40:
            logger.debug("8x8 board check passed: contrast=%.2f", contrast)
            return contrast

        dx, dy = cv2.spatialGradient(resized_crop)
        gx = np.abs(dx).mean(axis=0)
        gy = np.abs(dy).mean(axis=1)

        ratio_x = gx[_GRID_INDICES].mean() / (gx[_MID_INDICES].mean() + 1e-5)
        ratio_y = gy[_GRID_INDICES].mean() / (gy[_MID_INDICES].mean() + 1e-5)

        if min(ratio_x, ratio_y) > 1.3:
            logger.debug(
                "8x8 board check passed: contrast=%.2f, ratio_x=%.2f, ratio_y=%.2f",
                contrast,
                ratio_x,
                ratio_y,
            )
            return contrast

        return None

    @staticmethod
    def _dewarp_quad(
        img: np.ndarray, quad_pts: np.ndarray, target_size: int = BOARD_SIZE
    ) -> np.ndarray:
        s = quad_pts.sum(axis=1)
        diff = np.diff(quad_pts, axis=1)
        src = np.array(
            [
                quad_pts[np.argmin(s)],
                quad_pts[np.argmin(diff)],
                quad_pts[np.argmax(s)],
                quad_pts[np.argmax(diff)],
            ],
            dtype=np.float32,
        )
        dst = np.array(
            [[0, 0], [target_size, 0], [target_size, target_size], [0, target_size]],
            dtype=np.float32,
        )
        matrix = cv2.getPerspectiveTransform(src, dst)
        return cv2.warpPerspective(
            img, matrix, (target_size, target_size), flags=cv2.INTER_CUBIC
        )

    @staticmethod
    def _snap_to_board(gray: np.ndarray) -> tuple[int, int, int, int]:
        h, w = gray.shape[:2]
        margin_x = int(w * _MARGIN_RATIO)
        margin_y = int(h * _MARGIN_RATIO)
        if margin_x <= 0 or margin_y <= 0:
            return (0, 0, w, h)

        dark = gray < _DARK_PIXEL_THRESHOLD

        top_matches = np.flatnonzero(
            dark[:margin_y, margin_x:-margin_x].mean(axis=1) > _LINE_DENSITY_THRESHOLD
        )
        top = int(top_matches[0]) if top_matches.size > 0 else 0

        bottom_matches = np.flatnonzero(
            dark[h - margin_y :, margin_x:-margin_x].mean(axis=1)
            > _LINE_DENSITY_THRESHOLD
        )
        bottom = (
            int(h - margin_y + bottom_matches[-1]) if bottom_matches.size > 0 else h - 1
        )

        left_matches = np.flatnonzero(
            dark[margin_y:-margin_y, :margin_x].mean(axis=0) > _LINE_DENSITY_THRESHOLD
        )
        left = int(left_matches[0]) if left_matches.size > 0 else 0

        right_matches = np.flatnonzero(
            dark[margin_y:-margin_y, w - margin_x :].mean(axis=0)
            > _LINE_DENSITY_THRESHOLD
        )
        right = (
            int(w - margin_x + right_matches[-1]) if right_matches.size > 0 else w - 1
        )

        return (left, top, right + 1, bottom + 1)
