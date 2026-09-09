import numpy as np
from PIL import Image

from chessvision.board import BoardPrediction, slice_board
from chessvision.constants import Orientation


def test_board_prediction_valid() -> None:
    prediction = BoardPrediction(
        fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        squares={},
        confidence=1.0,
        orientation=Orientation.WHITE,
    )
    assert prediction.is_valid is True


def test_board_prediction_illegal() -> None:
    prediction = BoardPrediction(
        fen="8/8/8/8/8/8/8/8 w - - 0 1",
        squares={},
        confidence=0.5,
        orientation=Orientation.WHITE,
    )
    assert prediction.is_valid is False


def test_board_prediction_invalid() -> None:
    prediction = BoardPrediction(
        fen="invalid_fen_syntax",
        squares={},
        confidence=0.5,
        orientation=Orientation.WHITE,
    )
    assert prediction.is_valid is False


def test_board_prediction_url() -> None:
    prediction = BoardPrediction(
        fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        squares={},
        confidence=1.0,
        orientation=Orientation.WHITE,
    )
    assert (
        prediction.url
        == "https://lichess.org/editor/rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR_w_KQkq_-_0_1?color=white"
    )


def test_slice_board() -> None:
    crops, _ = slice_board("assets/chessboard.png")
    assert len(crops) == 64


def test_slice_board_pil() -> None:
    img = Image.open("assets/chessboard.png")
    crops, _ = slice_board(img)
    assert len(crops) == 64


def test_slice_board_arr() -> None:
    img = Image.open("assets/chessboard.png")
    arr = np.array(img)

    crops, _ = slice_board(arr)
    assert len(crops) == 64
