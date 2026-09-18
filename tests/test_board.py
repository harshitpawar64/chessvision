import chess
import numpy as np
import pytest
from PIL import Image

from chessvision.board import BoardPrediction, BoardPredictor, slice_board
from chessvision.classifier import SquarePrediction
from chessvision.constants import Orientation


def test_board_prediction_valid() -> None:
    prediction = BoardPrediction(
        fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        squares={},
        confidence=1.0,
        orientation=Orientation.WHITE,
    )
    assert prediction.is_valid is True
    assert isinstance(prediction.board, chess.Board)
    assert prediction.validation_errors == []


def test_board_prediction_illegal() -> None:
    prediction = BoardPrediction(
        fen="8/8/8/8/8/8/8/8 w - - 0 1",
        squares={},
        confidence=0.5,
        orientation=Orientation.WHITE,
    )
    assert prediction.is_valid is False
    assert prediction.validation_errors == [
        "Board is empty",
        "Missing white king",
        "Missing black king",
    ]


def test_board_prediction_invalid() -> None:
    prediction = BoardPrediction(
        fen="invalid_fen_syntax",
        squares={},
        confidence=0.5,
        orientation=Orientation.WHITE,
    )
    assert prediction.is_valid is False
    assert prediction.validation_errors == ["Invalid FEN syntax"]


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


@pytest.mark.parametrize(
    ("squares", "castling_rights"),
    [
        ({"e1": "wK", "h1": "wR", "a1": "wR"}, "KQ"),
        ({"e8": "bK", "h8": "bR"}, "k"),
        ({"e8": "bK", "a8": "bR"}, "q"),
        ({"e1": "wK"}, "-"),
    ],
)
def test_board_predictor_auto_castling(
    squares: dict[str, str], castling_rights: str
) -> None:
    square_map = {
        coord: SquarePrediction(label=squares.get(coord, "empty"), confidence=1.0)
        for coord in Orientation.WHITE.grid_coordinates
    }
    fen = BoardPredictor.fen(square_map)
    assert f" w {castling_rights} - 0 1" in fen
