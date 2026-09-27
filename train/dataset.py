import random
from pathlib import Path

from PIL import Image

from chessvision.constants import PIECE_CLASSES

TRAIN_DIR = Path(__file__).resolve().parent
BOARD_SQUARES_DIR = TRAIN_DIR / "assets" / "board_squares"
PIECE_SETS_DIR = TRAIN_DIR / "assets" / "piece_sets"
DATASET_DIR = TRAIN_DIR / "datasets" / "chess_pieces"


class ChessPieceDataset:
    def __init__(
        self,
        board_squares_dir: Path = BOARD_SQUARES_DIR,
        piece_sets_dir: Path = PIECE_SETS_DIR,
    ) -> None:
        if not board_squares_dir.exists() or not piece_sets_dir.exists():
            raise FileNotFoundError(
                f"Assets not found. Expected {board_squares_dir} and {piece_sets_dir}"
            )

        self.backgrounds = [Image.open(p) for p in board_squares_dir.glob("*.png")]
        self.pieces = {
            label: [Image.open(p) for p in piece_sets_dir.glob(f"*_{label}.png")]
            for label in PIECE_CLASSES
            if label != "empty"
        }

    def generate(
        self,
        output_dir: Path = DATASET_DIR,
        train_per_class: int = 2500,
        val_per_class: int = 300,
    ) -> Path:
        splits = [("train", train_per_class), ("val", val_per_class)]

        for split_name, count in splits:
            for label in PIECE_CLASSES:
                class_dir = output_dir / split_name / label
                class_dir.mkdir(parents=True, exist_ok=True)

                for i in range(count):
                    bg = random.choice(self.backgrounds).copy()

                    if label != "empty":
                        piece = random.choice(self.pieces[label])
                        x = (bg.width - piece.width) // 2 + random.randint(-8, 8)
                        y = (bg.height - piece.height) // 2 + random.randint(-8, 8)
                        bg.paste(piece, (x, y), mask=piece)

                    bg.save(class_dir / f"{label}_{i:05d}.png")

        return output_dir


if __name__ == "__main__":
    ChessPieceDataset().generate()
