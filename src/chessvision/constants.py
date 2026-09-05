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

PIECE_CLASSES = tuple(PIECES)

CLASS_TO_INDEX = {cls_name: idx for idx, cls_name in enumerate(PIECES)}

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


class Castling(StrEnum):
    WHITE = "KQ"
    BLACK = "kq"
    ALL = "KQkq"
    NONE = "-"

    WHITE_KINGSIDE = "K"
    WHITE_QUEENSIDE = "Q"
    BLACK_KINGSIDE = "k"
    BLACK_QUEENSIDE = "q"
