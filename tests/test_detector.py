import numpy as np
from PIL import Image

from chessvision.detector import BoardDetector

detector = BoardDetector()


def test_detect_board() -> None:
    boards = detector.detect("assets/chessboard.png")
    assert len(boards) == 1
    assert isinstance(boards[0], Image.Image)


def test_detect_pil() -> None:
    img = Image.open("assets/chessboard.png")
    boards = detector.detect(img)
    assert len(boards) == 1


def test_detect_numpy() -> None:
    arr = np.array(Image.open("assets/chessboard.png"))
    boards = detector.detect(arr)
    assert len(boards) == 1


def test_detect_no_board() -> None:
    assert detector.detect("assets/square.png") == []
