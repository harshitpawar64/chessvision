from pathlib import Path
from typing import Annotated

import typer

from chessvision import PieceClassifier
from chessvision.cli.utils import setup_logging


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
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Enable verbose logging.")
    ] = False,
) -> None:
    """Predict the chess piece on a single square image."""
    setup_logging(verbose)

    classifier = PieceClassifier()
    prediction = classifier.predict_square(image)

    print(f"{prediction.name} [{prediction.confidence:.2%}]")
