from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import pypdfium2 as pdfium

from chessvision.board import BoardPrediction, BoardPredictor
from chessvision.detector import BoardDetector

_TARGET_PAGE_DIM = 1800


@dataclass(frozen=True, slots=True)
class PDFBoardPrediction:
    page_number: int
    board_index: int
    total_boards_on_page: int
    prediction: BoardPrediction

    @property
    def label(self) -> str:
        if self.total_boards_on_page > 1:
            return f"Page {self.page_number} - Board #{self.board_index}"
        return f"Page {self.page_number}"


class PDFPredictor:
    def __init__(
        self,
        detector: BoardDetector | None = None,
        predictor: BoardPredictor | None = None,
        target_page_dim: int = _TARGET_PAGE_DIM,
    ) -> None:
        self.detector = detector or BoardDetector()
        self.predictor = predictor or BoardPredictor()
        self.target_page_dim = target_page_dim

    def predict(self, pdf: Path | str | bytes) -> Iterator[PDFBoardPrediction]:
        with pdfium.PdfDocument(pdf) as doc:
            for page_number, page in enumerate(doc, 1):
                width, height = page.get_size()
                scale = self.target_page_dim / max(width, height, 1)
                image = page.render(scale=scale).to_pil()

                boards = self.detector.detect(image)
                if not boards:
                    continue

                for i, board_img in enumerate(boards, 1):
                    prediction = self.predictor.predict(board_img)
                    yield PDFBoardPrediction(
                        page_number=page_number,
                        board_index=i,
                        total_boards_on_page=len(boards),
                        prediction=prediction,
                    )
