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
        fen="8/8/8/8/8/8/8/8 w - - 0 1", confidence=0.5, is_valid=False
    )
    monkeypatch.setattr(
        "chessvision.cli.BoardPredictor.predict",
        lambda *args, **kwargs: mock_prediction,
    )

    result = runner.invoke(app, ["board", "assets/chessboard.png"])
    assert result.exit_code == 0
    assert "Illegal position detected." in result.stderr


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
