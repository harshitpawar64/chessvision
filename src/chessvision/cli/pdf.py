from pathlib import Path
from typing import Annotated

import pypdfium2 as pdfium
import typer

from chessvision import PDFPredictor
from chessvision.cli.utils import report_validation_errors


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
    output: Annotated[
        Path | None, typer.Option("--output", "-o", help="Path to output file (.pgn).")
    ] = None,
) -> None:
    """Predicts chess positions from a PDF document."""
    pdf_predictor = PDFPredictor()

    total_boards = 0
    invalid_boards = {}
    results = []

    try:
        for result in pdf_predictor.predict(pdf):
            total_boards += 1

            if output:
                results.append(result.prediction.pgn)
            else:
                if total_boards > 1:
                    print()

                header = result.label
                typer.secho(header.center(21), bold=True)

                print(result.prediction.render_board + "\n")
                print(f"FEN: {result.prediction.fen}")
                print(f"Confidence: {result.prediction.confidence:.2%}")

            if not result.prediction.is_valid:
                invalid_boards[result.label] = result.prediction.validation_errors
    except pdfium.PdfiumError as e:
        typer.secho(f"Failed to open PDF file: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    if total_boards == 0:
        typer.secho("No chessboard detected in the PDF.", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    if output:
        try:
            content = "\n\n".join(results)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(content + "\n", encoding="utf-8")
        except OSError as e:
            typer.secho(
                f"Failed to write output file: {e}", fg=typer.colors.RED, err=True
            )
            raise typer.Exit(1)

    report_validation_errors(invalid_boards, total_boards=total_boards)
