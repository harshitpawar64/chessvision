import numpy as np
import pytest

from chessvision.constants import BOARD_SIZE
from chessvision.detector import BoardDetector, DetectedBoard

detector = BoardDetector()


def test_detect_board() -> None:
    boards = detector.detect("tests/assets/chessboard.png")
    assert len(boards) == 1
    assert isinstance(boards[0], DetectedBoard)


def test_detect_no_board() -> None:
    assert detector.detect("tests/assets/square.png") == []


def test_detect_crop_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("cv2.findContours", lambda *args, **kwargs: ([], None))
    boards = detector.detect("tests/assets/chessboard.png")
    assert len(boards) == 1


def test_detect_rotated_board() -> None:
    boards = detector.detect("tests/assets/rotated_board.png")
    assert len(boards) == 1
    assert isinstance(boards[0], DetectedBoard)
    assert boards[0].image.size == (BOARD_SIZE, BOARD_SIZE)


def test_detect_low_contrast_board() -> None:
    boards = detector.detect("tests/assets/low_contrast_board.png")
    assert len(boards) == 1
    assert isinstance(boards[0], DetectedBoard)


def test_is_8x8_board_too_small() -> None:
    small_crop = np.zeros((32, 32), dtype=np.uint8)
    assert BoardDetector._is_8x8_board(small_crop) is None


def test_snap_to_board_small() -> None:
    assert BoardDetector._snap_to_board(np.zeros((5, 5), dtype=np.uint8)) == (
        0,
        0,
        5,
        5,
    )
