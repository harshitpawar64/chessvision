import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from chessvision.classifier import PieceClassifier, SquarePrediction
from chessvision.constants import PIECES, Castling, Orientation


@dataclass(frozen=True, slots=True)
class BoardPrediction:
    fen: str
    squares: dict[str, SquarePrediction]
    confidence: float
    orientation: Orientation

    @property
    def render_board(self) -> str:
        lines = []

        header = "  " + " ".join(self.orientation.files)

        for rank in self.orientation.ranks:
            row_symbols = [
                PIECES.get(self.squares[f"{file}{rank}"].label, ".")
                for file in self.orientation.files
            ]

            lines.append(f"{rank} " + " ".join(row_symbols))

        lines.append(header)
        return "\n".join(lines)


class BoardPredictor:
    def __init__(self, classifier: PieceClassifier | None = None) -> None:
        self.classifier = classifier or PieceClassifier()

    def predict(
        self,
        image: Image.Image | Path | str | np.ndarray,
        orientation: Orientation = Orientation.WHITE,
        active_color: str = "w",
        castling: Castling = Castling.NONE,
    ) -> BoardPrediction:
        square_images, coordinates = slice_board(image, orientation=orientation)
        predictions = self.classifier.predict_squares(square_images)

        avg_confidence = np.mean([prediction.confidence for prediction in predictions])

        square_map = {
            coordinate: prediction
            for coordinate, prediction in zip(coordinates, predictions)
        }

        fen = self.fen(
            square_map=square_map, active_color=active_color, castling=castling
        )

        return BoardPrediction(
            fen=fen,
            squares=square_map,
            confidence=avg_confidence,
            orientation=orientation,
        )

    @staticmethod
    def fen(
        square_map: dict[str, SquarePrediction],
        active_color: str = "w",
        castling: Castling = Castling.NONE,
        en_passant: str = "-",
        halfmove: int = 0,
        fullmove: int = 1,
    ) -> str:

        raw = "/".join(
            "".join(
                PIECES[square_map[f"{file}{rank}"].label]
                for file in Orientation.WHITE.files
            )
            for rank in Orientation.WHITE.ranks
        )
        placement = re.sub(r"\.+", lambda m: str(len(m.group())), raw)

        return (
            f"{placement} {active_color} {castling} {en_passant} {halfmove} {fullmove}"
        )


def slice_board(
    image: Image.Image | Path | str | np.ndarray,
    orientation: Orientation = Orientation.WHITE,
) -> tuple[list[Image.Image], list[str]]:
    if isinstance(image, (Path, str)):
        img = Image.open(image).convert("RGB")
    elif isinstance(image, np.ndarray):
        img = Image.fromarray(image).convert("RGB")
    else:
        img = image.convert("RGB")

    width, height = img.size

    square_w = width / 8
    square_h = height / 8

    square_images = [
        img.crop(
            (col * square_w, row * square_h, (col + 1) * square_w, (row + 1) * square_h)
        )
        for row in range(8)
        for col in range(8)
    ]

    return square_images, orientation.grid_coordinates
