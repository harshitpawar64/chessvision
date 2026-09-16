import importlib
import runpy
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from chessvision import __version__
from chessvision.cli import app


def test_version(runner: CliRunner) -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert f"chessvision {__version__}" in result.stdout


def test_square(runner: CliRunner) -> None:
    result = runner.invoke(app, ["square", "assets/square.png"])
    assert result.exit_code == 0
    assert "bN" in result.stdout


def test_board(runner: CliRunner) -> None:
    result = runner.invoke(app, ["board", "assets/chessboard.png"])
    assert result.exit_code == 0
    assert "FEN:" in result.stdout
    assert "2b1k2r/pp2P3/2p3RQ/8/5P2/7P/Pq1r2PK/4R3 w - - 0 1" in result.stdout
    assert "Confidence:" in result.stdout


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
        "chessvision.cli.BoardPredictor.predict",
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
        "chessvision.cli.BoardDetector.detect",
        lambda *args, **kwargs: ["assets/chessboard.png", "assets/chessboard.png"],
    )
    monkeypatch.setattr(
        "chessvision.cli.BoardPredictor.predict",
        MagicMock(side_effect=[mock_prediction_valid, mock_prediction_invalid]),
    )

    result = runner.invoke(app, ["board", "assets/chessboard.png"])
    assert result.exit_code == 0
    assert "Illegal position detected:" in result.stderr
    assert "- Board #2: Board is empty" in result.stderr


def test_report_illegal_positions_max_display(
    capsys: pytest.CaptureFixture[str],
) -> None:
    from chessvision.cli import _report_illegal_positions

    errors = {i: ["Invalid position"] for i in range(1, 15)}
    _report_illegal_positions(errors, total_boards=len(errors))
    captured = capsys.readouterr()
    assert "Illegal positions detected:" in captured.err
    assert "- Board #10: Invalid position" in captured.err
    assert "- Board #11:" not in captured.err
    assert "... and 4 more." in captured.err


def test_board_multiple_boards(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "chessvision.cli.BoardDetector.detect",
        lambda *args, **kwargs: ["assets/chessboard.png", "assets/chessboard.png"],
    )

    result = runner.invoke(app, ["board", "assets/chessboard.png"])
    assert result.exit_code == 0
    assert "--- Board #1 ---" in result.stdout
    assert "--- Board #2 ---" in result.stdout


def test_board_open_in_browser(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_launch = MagicMock()
    monkeypatch.setattr("chessvision.cli.typer.launch", mock_launch)

    result = runner.invoke(app, ["board", "assets/chessboard.png", "--open"])
    assert result.exit_code == 0
    mock_launch.assert_called_once()


def test_main_module_entrypoint(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_app = MagicMock()
    monkeypatch.setattr("chessvision.cli.app", mock_app)
    runpy.run_module("chessvision.__main__", run_name="__main__")
    mock_app.assert_called_once()


def test_main_module_import(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_app = MagicMock()
    monkeypatch.setattr("chessvision.cli.app", mock_app)
    import chessvision.__main__

    importlib.reload(chessvision.__main__)
    mock_app.assert_not_called()
