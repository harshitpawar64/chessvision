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
