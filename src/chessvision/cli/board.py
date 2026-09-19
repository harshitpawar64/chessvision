from pathlib import Path
from typing import Annotated

import typer

from chessvision import BoardDetector, BoardPredictor, Orientation, Turn
from chessvision.cli.utils import report_validation_errors


def castling_callback(value: str) -> str:
    if value in ("auto", "-"):
        return value

    if (
        (chars := set(value))
        and chars <= {"K", "Q", "k", "q"}
        and len(chars) == len(value)
    ):
        return "".join(char for char in "KQkq" if char in chars)

    raise typer.BadParameter("Expected 'auto', '-', or combination of K, Q, k, q.")


def board(
    image: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to image.",
        ),
    ],
    orientation: Annotated[
        Orientation, typer.Option("--orientation", "-o", help="Board perspective.")
    ] = Orientation.AUTO,
    turn: Annotated[
        Turn, typer.Option("--turn", "-t", help="Side to move.")
    ] = Turn.AUTO,
    castling: Annotated[
        str,
        typer.Option(
            "--castling",
            "-c",
            callback=castling_callback,
            help="Castling availability.",
        ),
    ] = "auto",
    open_in_browser: Annotated[
        bool, typer.Option("--open", help="Open position in Lichess editor.")
    ] = False,
) -> None:
    """Predicts chess positions from a chessboard image."""
    detector = BoardDetector()
    boards = detector.detect(image)

    if not boards:
        typer.secho(
            "No chessboard detected in the image.", fg=typer.colors.RED, err=True
        )
        raise typer.Exit(1)

    predictor = BoardPredictor()

    invalid_boards = {}
    for i, board_img in enumerate(boards, 1):
        if len(boards) > 1:
            typer.secho(f"Board #{i}".center(21), bold=True)

        prediction = predictor.predict(board_img, orientation, turn, castling)

        print(prediction.render_board + "\n")
        print(f"FEN: {prediction.fen}")
        print(f"Confidence: {prediction.confidence:.2%}")

        if not prediction.is_valid:
            invalid_boards[f"Board #{i}"] = prediction.validation_errors

        if len(boards) > 1 and i < len(boards):
            print()

        if open_in_browser:
            typer.launch(prediction.url)

    report_validation_errors(invalid_boards, total_boards=len(boards))
