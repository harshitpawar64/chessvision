import pytest

from chessvision.cli.utils import report_illegal_positions


def test_report_illegal_positions_max_display(
    capsys: pytest.CaptureFixture[str],
) -> None:
    errors = {i: ["Invalid position"] for i in range(1, 15)}
    report_illegal_positions(errors, total_boards=len(errors))
    captured = capsys.readouterr()

    assert "Illegal positions detected:" in captured.err
    assert "- Board #10: Invalid position" in captured.err
    assert "- Board #11:" not in captured.err
    assert "... and 4 more." in captured.err
