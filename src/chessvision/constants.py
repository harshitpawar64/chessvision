PIECE_CLASSES = (
    "empty",
    "wP",
    "wN",
    "wB",
    "wR",
    "wQ",
    "wK",
    "bP",
    "bN",
    "bB",
    "bR",
    "bQ",
    "bK",
)

CLASS_TO_IDX = {cls_name: idx for idx, cls_name in enumerate(PIECE_CLASSES)}
