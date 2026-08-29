from pathlib import Path
from typing import Annotated

import typer

from chessvision import PieceClassifier, __version__

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
