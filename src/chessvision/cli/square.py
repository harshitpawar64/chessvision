from pathlib import Path
from typing import Annotated

import typer

from chessvision import PieceClassifier


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
