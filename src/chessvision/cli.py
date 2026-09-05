from pathlib import Path
from typing import Annotated

import typer

from chessvision import (
    BoardPredictor,
    Castling,
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

    print(f"{prediction.label} [{prediction.confidence:.2%}]")


@app.command()
def board(
    image: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to full chessboard image.",
        ),
    ],
    orientation: Annotated[
        Orientation, typer.Option("--orientation", "-o", help="Board perspective.")
    ] = Orientation.WHITE,
    turn: Annotated[
        Turn, typer.Option("--turn", "-t", help="Side to move.")
    ] = Turn.WHITE,
    castling: Annotated[
        Castling, typer.Option("--castling", "-c", help="Castling availability.")
    ] = Castling.NONE,
    open_in_browser: Annotated[
        bool, typer.Option("--open", help="Open position in Lichess editor.")
    ] = False,
) -> None:
    """Predict the chess position on a chessboard image."""
    predictor = BoardPredictor()
    prediction = predictor.predict(
        image, orientation=orientation, active_color=turn, castling=castling
    )

    print(prediction.render_board + "\n")
    print(f"FEN: {prediction.fen}")
    print(f"Confidence: {prediction.confidence:.2%}")

    if open_in_browser:
        typer.launch(prediction.url)


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
