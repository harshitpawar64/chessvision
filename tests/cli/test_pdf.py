from pathlib import Path
from unittest.mock import MagicMock

import pypdfium2 as pdfium
import pytest
from typer.testing import CliRunner

from chessvision.cli import app


def test_pdf_invalid_file(runner: CliRunner, tmp_path: Path) -> None:
    bad_pdf = tmp_path / "bad.pdf"
    bad_pdf.write_bytes(b"not a valid pdf")

    result = runner.invoke(app, ["pdf", str(bad_pdf)])
    assert result.exit_code == 1
    assert "Failed to open PDF file:" in result.stderr


def test_pdf_no_board_detected(runner: CliRunner, tmp_path: Path) -> None:
    blank_pdf = tmp_path / "blank.pdf"
    doc = pdfium.PdfDocument.new()
    doc.new_page(100, 100)
    doc.save(blank_pdf)
    doc.close()

    result = runner.invoke(app, ["pdf", str(blank_pdf)])
    assert result.exit_code == 1
    assert "No chessboard detected in the PDF." in result.stderr


def test_pdf_multiple_boards(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pdf_path = tmp_path / "multi.pdf"
    doc = pdfium.PdfDocument.new()
    doc.new_page(200, 200)
    doc.new_page(200, 200)
    doc.save(pdf_path)
    doc.close()

    mock_valid = MagicMock(
        fen="8/8/8/8/8/8/8/8 w - - 0 1", confidence=0.95, is_valid=True
    )
    mock_invalid = MagicMock(
        fen="8/8/8/8/8/8/8/8 w - - 0 1",
        confidence=0.85,
        is_valid=False,
        validation_errors=["Board is empty"],
    )

    monkeypatch.setattr(
        "chessvision.pdf.BoardDetector.detect",
        MagicMock(side_effect=[[], ["board_1", "board_2"]]),
    )
    monkeypatch.setattr(
        "chessvision.pdf.BoardPredictor.predict",
        MagicMock(side_effect=[mock_valid, mock_invalid]),
    )

    result = runner.invoke(app, ["pdf", str(pdf_path)])
    assert result.exit_code == 0
    assert "Page 2 - Board #1" in result.stdout
    assert "Page 2 - Board #2" in result.stdout
    assert "Illegal position detected:" in result.stderr
    assert "Page 2 - Board #2: Board is empty" in result.stderr


def test_pdf_output(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pdf_path = tmp_path / "test.pdf"
    doc = pdfium.PdfDocument.new()
    doc.new_page(200, 200)
    doc.save(pdf_path)
    doc.close()

    mock_valid = MagicMock(
        fen="8/8/8/8/8/8/8/8 w - - 0 1",
        confidence=0.95,
        is_valid=True,
        pgn='[Event "?"]\n[SetUp "1"]\n[FEN "8/8/8/8/8/8/8/8 w - - 0 1"]\n\n*',
    )

    monkeypatch.setattr(
        "chessvision.pdf.BoardDetector.detect", MagicMock(return_value=["board_1"])
    )
    monkeypatch.setattr(
        "chessvision.pdf.BoardPredictor.predict", MagicMock(return_value=mock_valid)
    )

    out_file = tmp_path / "sub" / "output.pgn"
    result = runner.invoke(app, ["pdf", str(pdf_path), "-o", str(out_file)])
    assert result.exit_code == 0
    assert result.stdout == ""
    assert out_file.exists()
    assert '[FEN "8/8/8/8/8/8/8/8 w - - 0 1"]' in out_file.read_text(encoding="utf-8")


def test_pdf_output_write_error(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pdf_path = tmp_path / "test.pdf"
    doc = pdfium.PdfDocument.new()
    doc.new_page(200, 200)
    doc.save(pdf_path)
    doc.close()

    mock_valid = MagicMock(
        fen="8/8/8/8/8/8/8/8 w - - 0 1",
        confidence=0.95,
        is_valid=True,
        pgn='[Event "?"]\n[SetUp "1"]\n[FEN "8/8/8/8/8/8/8/8 w - - 0 1"]\n\n*',
    )

    monkeypatch.setattr(
        "chessvision.pdf.BoardDetector.detect", MagicMock(return_value=["board_1"])
    )
    monkeypatch.setattr(
        "chessvision.pdf.BoardPredictor.predict", MagicMock(return_value=mock_valid)
    )
    monkeypatch.setattr(
        Path, "write_text", MagicMock(side_effect=OSError("Permission Error"))
    )

    out_file = tmp_path / "output.pgn"
    result = runner.invoke(app, ["pdf", str(pdf_path), "-o", str(out_file)])
    assert result.exit_code == 1
    assert "Failed to write output file: Permission Error" in result.stderr
