from pathlib import Path
from typing import Annotated

import pypdfium2 as pdfium
import typer

from chessvision import BoardDetector, BoardPredictor
from chessvision.cli.utils import report_validation_errors

TARGET_PAGE_DIM = 1800


def pdf(
    pdf: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to PDF file.",
        ),
    ],
) -> None:
    """Predicts chess positions from a PDF document."""
    try:
        doc = pdfium.PdfDocument(pdf)
    except pdfium.PdfiumError as e:
        typer.secho(f"Failed to open PDF file: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    with doc:
        detector = BoardDetector()
        predictor = BoardPredictor()

        total_boards = 0
        invalid_boards = {}

        for page_num, page in enumerate(doc, 1):
            width, height = page.get_size()
            scale = TARGET_PAGE_DIM / max(width, height, 1)
            image = page.render(scale=scale).to_pil()

            boards = detector.detect(image)

            if not boards:
                continue

            for i, board_img in enumerate(boards, 1):
                total_boards += 1

                if total_boards > 1:
                    print()

                if len(boards) > 1:
                    header = f"Page {page_num} - Board #{i}"
                else:
                    header = f"Page {page_num}"
                typer.secho(header.center(21), bold=True)

                prediction = predictor.predict(board_img)

                print(prediction.render_board + "\n")
                print(f"FEN: {prediction.fen}")
                print(f"Confidence: {prediction.confidence:.2%}")

                if not prediction.is_valid:
                    invalid_boards[header] = prediction.validation_errors

        if total_boards == 0:
            typer.secho(
                "No chessboard detected in the PDF.", fg=typer.colors.RED, err=True
            )
            raise typer.Exit(1)

        report_validation_errors(invalid_boards, total_boards=total_boards)
