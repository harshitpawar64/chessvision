from enum import StrEnum, auto

PIECES = {
    "empty": ".",
    "wP": "P",
    "wN": "N",
    "wB": "B",
    "wR": "R",
    "wQ": "Q",
    "wK": "K",
    "bP": "p",
    "bN": "n",
    "bB": "b",
    "bR": "r",
    "bQ": "q",
    "bK": "k",
}

PIECE_NAMES = {
    "empty": "Empty",
    "wP": "White Pawn",
    "wN": "White Knight",
    "wB": "White Bishop",
    "wR": "White Rook",
    "wQ": "White Queen",
    "wK": "White King",
    "bP": "Black Pawn",
    "bN": "Black Knight",
    "bB": "Black Bishop",
    "bR": "Black Rook",
    "bQ": "Black Queen",
    "bK": "Black King",
}

PIECE_CLASSES = tuple(PIECES)

CLASS_TO_INDEX = {cls_name: index for index, cls_name in enumerate(PIECES)}

_RANKS = ("1", "2", "3", "4", "5", "6", "7", "8")
_FILES = ("a", "b", "c", "d", "e", "f", "g", "h")


class Orientation(StrEnum):
    WHITE = auto()
    BLACK = auto()

    @property
    def ranks(self) -> tuple[str, ...]:
        return _RANKS[::-1] if self is Orientation.WHITE else _RANKS

    @property
    def files(self) -> tuple[str, ...]:
        return _FILES if self is Orientation.WHITE else _FILES[::-1]

    @property
    def grid_coordinates(self) -> list[str]:
        return [f"{file}{rank}" for rank in self.ranks for file in self.files]


class Turn(StrEnum):
    WHITE = auto()
    BLACK = auto()

    @property
    def symbol(self) -> str:
        return "w" if self is Turn.WHITE else "b"
