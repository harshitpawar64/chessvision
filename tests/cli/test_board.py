from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from chessvision.cli import app


def test_board(runner: CliRunner) -> None:
    result = runner.invoke(app, ["board", "assets/chessboard.png"])
    assert result.exit_code == 0
    assert "FEN:" in result.stdout
    assert "2b1k2r/pp2P3/2p3RQ/8/5P2/7P/Pq1r2PK/4R3 w k - 0 1" in result.stdout
    assert "Confidence:" in result.stdout


def test_board_castling_valid(runner: CliRunner) -> None:
    result = runner.invoke(app, ["board", "assets/chessboard.png", "-c", "qK"])
    assert result.exit_code == 0
    assert "2b1k2r/pp2P3/2p3RQ/8/5P2/7P/Pq1r2PK/4R3 w Kq - 0 1" in result.stdout


def test_board_castling_invalid(runner: CliRunner) -> None:
    result = runner.invoke(app, ["board", "assets/chessboard.png", "-c", "invalid"])
    assert result.exit_code == 2


def test_board_no_board_detected(runner: CliRunner) -> None:
    result = runner.invoke(app, ["board", "assets/square.png"])
    assert result.exit_code == 1
    assert "No chessboard detected in the image." in result.stderr


def test_board_illegal_warning(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_prediction = MagicMock(
        fen="8/8/8/8/8/8/8/8 w - - 0 1",
        confidence=0.5,
        is_valid=False,
        validation_errors=[
            "Missing white king",
            "Missing black king",
            "Board is empty",
        ],
    )
    monkeypatch.setattr(
        "chessvision.cli.board.BoardPredictor.predict",
        lambda *args, **kwargs: mock_prediction,
    )

    result = runner.invoke(app, ["board", "assets/chessboard.png"])
    assert result.exit_code == 0
    assert (
        "Illegal position detected: Missing white king, Missing black king, Board is empty."
        in result.stderr
    )


def test_board_multiple_boards_illegal(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_prediction_valid = MagicMock(
        fen="8/8/8/8/8/8/8/8 w - - 0 1", confidence=0.9, is_valid=True
    )
    mock_prediction_invalid = MagicMock(
        fen="8/8/8/8/8/8/8/8 w - - 0 1",
        confidence=0.5,
        is_valid=False,
        validation_errors=["Board is empty"],
    )
    monkeypatch.setattr(
        "chessvision.cli.board.BoardDetector.detect",
        lambda *args, **kwargs: ["assets/chessboard.png", "assets/chessboard.png"],
    )
    monkeypatch.setattr(
        "chessvision.cli.board.BoardPredictor.predict",
        MagicMock(side_effect=[mock_prediction_valid, mock_prediction_invalid]),
    )

    result = runner.invoke(app, ["board", "assets/chessboard.png"])
    assert result.exit_code == 0
    assert "Illegal position detected:" in result.stderr
    assert "- Board #2: Board is empty" in result.stderr


def test_board_multiple_boards(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "chessvision.cli.board.BoardDetector.detect",
        lambda *args, **kwargs: ["assets/chessboard.png", "assets/chessboard.png"],
    )

    result = runner.invoke(app, ["board", "assets/chessboard.png"])
    assert result.exit_code == 0
    assert "Board #1" in result.stdout
    assert "Board #2" in result.stdout


def test_board_open_in_browser(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_launch = MagicMock()
    monkeypatch.setattr("chessvision.cli.board.typer.launch", mock_launch)

    result = runner.invoke(app, ["board", "assets/chessboard.png", "--open"])
    assert result.exit_code == 0
    mock_launch.assert_called_once()
