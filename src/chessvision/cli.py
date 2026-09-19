from pathlib import Path
from typing import Annotated

import typer

from chessvision import (
    BoardDetector,
    BoardPredictor,
    Orientation,
    PieceClassifier,
    Turn,
    __version__,
)

app = typer.Typer()


@app.command()
def square(
    image: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to square image.",
        ),
    ],
) -> None:
    """Predict the chess piece on a single square image."""
    classifier = PieceClassifier()
    prediction = classifier.predict_square(image)

    print(f"{prediction.name} [{prediction.confidence:.2%}]")


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


@app.command()
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
    ] = Turn.WHITE,
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
            invalid_boards[i] = prediction.validation_errors

        if len(boards) > 1 and i < len(boards):
            print()

        if open_in_browser:
            typer.launch(prediction.url)

    _report_illegal_positions(invalid_boards, total_boards=len(boards))


def version_callback(value: bool) -> None:
    if value:
        print(f"chessvision {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = False,
) -> None: ...


def _report_illegal_positions(errors: dict[int, list[str]], total_boards: int) -> None:
    if not errors:
        return

    if total_boards == 1:
        board_errors = next(iter(errors.values()))
        typer.secho(
            f"Illegal position detected: {', '.join(board_errors)}.",
            fg=typer.colors.YELLOW,
            err=True,
        )
        return

    count = len(errors)
    max_display = 10

    typer.secho(
        f"\nIllegal position{'s' if count > 1 else ''} detected:",
        fg=typer.colors.YELLOW,
        err=True,
    )
    for board_num, validation_errors in list(errors.items())[:max_display]:
        typer.secho(
            f"  - Board #{board_num}: {', '.join(validation_errors)}",
            fg=typer.colors.YELLOW,
            err=True,
        )
    if count > max_display:
        typer.secho(
            f"  ... and {count - max_display} more.", fg=typer.colors.YELLOW, err=True
        )
