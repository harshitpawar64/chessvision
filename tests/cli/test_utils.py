import pytest

from chessvision.cli.utils import report_validation_errors


def test_report_validation_errors_max_display(
    capsys: pytest.CaptureFixture[str],
) -> None:
    errors = {f"Board #{i}": ["Invalid position"] for i in range(1, 15)}
    report_validation_errors(errors, total_boards=len(errors))
    captured = capsys.readouterr()

    assert "Illegal positions detected:" in captured.err
    assert "- Board #10: Invalid position" in captured.err
    assert "- Board #11:" not in captured.err
    assert "... and 4 more." in captured.err
