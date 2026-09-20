from pathlib import Path
from unittest.mock import MagicMock

import pypdfium2 as pdfium

from chessvision.pdf import PDFBoardPrediction, PDFPredictor


def test_pdf_board_prediction_label_single() -> None:
    prediction = PDFBoardPrediction(
        page_number=1, board_index=1, total_boards_on_page=1, prediction=MagicMock()
    )
    assert prediction.label == "Page 1"


def test_pdf_board_prediction_label_multiple() -> None:
    prediction = PDFBoardPrediction(
        page_number=2, board_index=3, total_boards_on_page=4, prediction=MagicMock()
    )
    assert prediction.label == "Page 2 - Board #3"


def test_pdf_predictor_predict(tmp_path: Path) -> None:
    pdf_path = tmp_path / "test.pdf"
    doc = pdfium.PdfDocument.new()
    doc.new_page(100, 100)
    doc.new_page(100, 100)
    doc.save(pdf_path)
    doc.close()

    mock_detector = MagicMock()
    mock_detector.detect.side_effect = [[], ["board1", "board2"]]
    mock_predictor = MagicMock()

    pdf_predictor = PDFPredictor(detector=mock_detector, predictor=mock_predictor)
    results = list(pdf_predictor.predict(pdf_path))

    assert len(results) == 2
    assert results[0].page_number == 2
    assert results[0].board_index == 1
    assert results[0].total_boards_on_page == 2
    assert results[0].prediction is mock_predictor.predict.return_value
    assert results[1].page_number == 2
    assert results[1].board_index == 2
