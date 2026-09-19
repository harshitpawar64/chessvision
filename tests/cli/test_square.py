from typer.testing import CliRunner

from chessvision.cli import app


def test_square(runner: CliRunner) -> None:
    result = runner.invoke(app, ["square", "assets/square.png"])
    assert result.exit_code == 0
    assert "Black Knight" in result.stdout
