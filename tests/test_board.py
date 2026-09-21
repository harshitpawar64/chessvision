import chess
import numpy as np
import pytest
from PIL import Image

from chessvision.board import BoardPrediction, BoardPredictor, slice_board
from chessvision.classifier import PieceClassifier, SquarePrediction
from chessvision.constants import Orientation, Turn

predictor = BoardPredictor()


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


def test_board_prediction_pgn() -> None:
    prediction = BoardPrediction(
        fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        squares={},
        confidence=1.0,
        orientation=Orientation.WHITE,
    )
    assert '[SetUp "1"]' in prediction.pgn
    assert (
        '[FEN "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"]'
        in prediction.pgn
    )


def test_slice_board() -> None:
    crops = slice_board("assets/chessboard.png")
    assert len(crops) == 64


def test_slice_board_pil() -> None:
    img = Image.open("assets/chessboard.png")
    crops = slice_board(img)
    assert len(crops) == 64


def test_slice_board_arr() -> None:
    img = Image.open("assets/chessboard.png")
    arr = np.array(img)

    crops = slice_board(arr)
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


def test_board_predictor_explicit_orientation() -> None:
    prediction = predictor.predict(
        "assets/chessboard.png", orientation=Orientation.WHITE
    )
    assert prediction.orientation is Orientation.WHITE


def test_board_predictor_auto_orientation_black(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_predictions = [
        SquarePrediction(label="empty", confidence=1.0) for _ in range(64)
    ]
    mock_predictions[0] = SquarePrediction(label="wK", confidence=1.0)
    mock_predictions[63] = SquarePrediction(label="bK", confidence=1.0)
    monkeypatch.setattr(
        PieceClassifier, "predict_squares", lambda *args, **kwargs: mock_predictions
    )

    prediction = predictor.predict("assets/chessboard.png")
    assert prediction.orientation is Orientation.BLACK


def test_board_predictor_auto_orientation_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_predictions = [
        SquarePrediction(label="empty", confidence=1.0) for _ in range(64)
    ]
    monkeypatch.setattr(
        PieceClassifier, "predict_squares", lambda *args, **kwargs: mock_predictions
    )

    prediction = predictor.predict("assets/chessboard.png")
    assert prediction.orientation is Orientation.WHITE


def test_board_predictor_explicit_turn() -> None:
    prediction = predictor.predict("assets/chessboard.png", turn=Turn.BLACK)
    assert " b " in prediction.fen


def test_board_predictor_auto_turn_white_under_check(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_predictions = [
        SquarePrediction(label="empty", confidence=1.0) for _ in range(64)
    ]
    mock_predictions[60] = SquarePrediction(label="wK", confidence=1.0)
    mock_predictions[4] = SquarePrediction(label="bK", confidence=1.0)
    mock_predictions[52] = SquarePrediction(label="bR", confidence=1.0)
    monkeypatch.setattr(
        PieceClassifier, "predict_squares", lambda *args, **kwargs: mock_predictions
    )

    prediction = predictor.predict("assets/chessboard.png")
    assert " w " in prediction.fen


def test_board_predictor_auto_turn_black_under_check(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_predictions = [
        SquarePrediction(label="empty", confidence=1.0) for _ in range(64)
    ]
    mock_predictions[60] = SquarePrediction(label="wK", confidence=1.0)
    mock_predictions[4] = SquarePrediction(label="bK", confidence=1.0)
    mock_predictions[12] = SquarePrediction(label="wR", confidence=1.0)
    monkeypatch.setattr(
        PieceClassifier, "predict_squares", lambda *args, **kwargs: mock_predictions
    )
    prediction = predictor.predict("assets/chessboard.png")
    assert " b " in prediction.fen
