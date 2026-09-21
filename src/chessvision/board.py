import re
from dataclasses import dataclass
from pathlib import Path

import chess
import chess.pgn
import numpy as np
from chess import Status
from PIL import Image

from chessvision.classifier import PieceClassifier, SquarePrediction
from chessvision.constants import PIECES, Orientation, Turn

STATUS_ERROR_MESSAGES = {
    Status.EMPTY: "Board is empty",
    Status.NO_WHITE_KING: "Missing white king",
    Status.NO_BLACK_KING: "Missing black king",
    Status.TOO_MANY_KINGS: "Too many kings",
    Status.TOO_MANY_WHITE_PAWNS: "Too many white pawns",
    Status.TOO_MANY_BLACK_PAWNS: "Too many black pawns",
    Status.PAWNS_ON_BACKRANK: "Pawns on back rank",
    Status.TOO_MANY_WHITE_PIECES: "Too many white pieces",
    Status.TOO_MANY_BLACK_PIECES: "Too many black pieces",
    Status.BAD_CASTLING_RIGHTS: "Bad castling rights",
    Status.INVALID_EP_SQUARE: "Invalid en passant square",
    Status.OPPOSITE_CHECK: "Side not to move is in check",
    Status.RACE_CHECK: "Race check",
    Status.RACE_OVER: "Race over",
    Status.RACE_MATERIAL: "Race material",
    Status.TOO_MANY_CHECKERS: "Too many checkers",
    Status.IMPOSSIBLE_CHECK: "Impossible check",
}


@dataclass(frozen=True, slots=True)
class BoardPrediction:
    fen: str
    squares: dict[str, SquarePrediction]
    confidence: float
    orientation: Orientation

    @property
    def board(self) -> chess.Board:
        return chess.Board(self.fen)

    @property
    def is_valid(self) -> bool:
        return not self.validation_errors

    @property
    def validation_errors(self) -> list[str]:
        try:
            status = self.board.status()
        except ValueError:
            return ["Invalid FEN syntax"]

        if status is Status.VALID:
            return []

        return [msg for flag, msg in STATUS_ERROR_MESSAGES.items() if status & flag]

    @property
    def render_board(self) -> str:
        border = f"  +{'-' * 17}+"
        lines = [border]

        for rank in self.orientation.ranks:
            row_symbols = [
                PIECES.get(self.squares[f"{file}{rank}"].label, ".")
                for file in self.orientation.files
            ]

            lines.append(f"{rank} | " + " ".join(row_symbols) + " |")

        lines.append(border)
        lines.append("    " + " ".join(self.orientation.files))
        return "\n".join(lines)

    @property
    def url(self) -> str:
        fen_slug = self.fen.replace(" ", "_")
        return f"https://lichess.org/editor/{fen_slug}?color={self.orientation}"

    @property
    def pgn(self) -> str:
        game = chess.pgn.Game()
        game.setup(self.fen)

        game.headers["FEN"] = self.fen
        game.headers["SetUp"] = "1"

        return str(game)


class BoardPredictor:
    def __init__(self, classifier: PieceClassifier | None = None) -> None:
        self.classifier = classifier or PieceClassifier()

    def predict(
        self,
        image: Image.Image | Path | str | np.ndarray,
        orientation: Orientation = Orientation.AUTO,
        turn: Turn = Turn.AUTO,
        castling: str = "auto",
    ) -> BoardPrediction:
        square_images = slice_board(image)
        predictions = self.classifier.predict_squares(square_images)

        avg_confidence = np.mean([prediction.confidence for prediction in predictions])

        if orientation is Orientation.AUTO:
            orientation = self._infer_orientation(predictions)

        square_map = dict(zip(orientation.grid_coordinates, predictions))

        fen = self.fen(square_map=square_map, active_color=turn, castling=castling)

        return BoardPrediction(
            fen=fen,
            squares=square_map,
            confidence=avg_confidence,
            orientation=orientation,
        )

    @staticmethod
    def fen(
        square_map: dict[str, SquarePrediction],
        active_color: Turn = Turn.AUTO,
        castling: str = "auto",
        en_passant: str = "-",
        halfmove: int = 0,
        fullmove: int = 1,
    ) -> str:
        if castling == "auto":
            castling = BoardPredictor._infer_castling(square_map)

        if active_color is Turn.AUTO:
            active_color = BoardPredictor._infer_turn(square_map)

        raw = "/".join(
            "".join(
                PIECES[square_map[f"{file}{rank}"].label]
                for file in Orientation.WHITE.files
            )
            for rank in Orientation.WHITE.ranks
        )
        placement = re.sub(r"\.+", lambda m: str(len(m.group())), raw)

        return f"{placement} {active_color.symbol} {castling} {en_passant} {halfmove} {fullmove}"

    @staticmethod
    def _infer_orientation(predictions: list[SquarePrediction]) -> Orientation:
        white_rows = [
            i // 8
            for i, prediction in enumerate(predictions)
            if prediction.label.startswith("w")
        ]
        black_rows = [
            i // 8
            for i, prediction in enumerate(predictions)
            if prediction.label.startswith("b")
        ]

        if not white_rows or not black_rows:
            return Orientation.WHITE

        return (
            Orientation.WHITE
            if np.mean(white_rows) > np.mean(black_rows)
            else Orientation.BLACK
        )

    @staticmethod
    def _infer_castling(square_map: dict[str, SquarePrediction]) -> str:
        castling_rights = ""

        if square_map["e1"].label == "wK":
            if square_map["h1"].label == "wR":
                castling_rights += "K"
            if square_map["a1"].label == "wR":
                castling_rights += "Q"

        if square_map["e8"].label == "bK":
            if square_map["h8"].label == "bR":
                castling_rights += "k"
            if square_map["a8"].label == "bR":
                castling_rights += "q"

        return castling_rights if castling_rights else "-"

    @staticmethod
    def _infer_turn(square_map: dict[str, SquarePrediction]) -> Turn:
        board = chess.Board(None)
        for square, prediction in square_map.items():
            if prediction.label != "empty":
                board.set_piece_at(
                    chess.parse_square(square),
                    chess.Piece.from_symbol(PIECES[prediction.label]),
                )

        white_king = board.king(chess.WHITE)
        black_king = board.king(chess.BLACK)

        white_in_check = white_king is not None and board.is_attacked_by(
            chess.BLACK, white_king
        )
        black_in_check = black_king is not None and board.is_attacked_by(
            chess.WHITE, black_king
        )

        if white_in_check and not black_in_check:
            return Turn.WHITE

        if black_in_check and not white_in_check:
            return Turn.BLACK

        top_left_square = next(iter(square_map), None)

        return Turn.BLACK if top_left_square == "h1" else Turn.WHITE


def slice_board(image: Image.Image | Path | str | np.ndarray) -> list[Image.Image]:
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

    return square_images
