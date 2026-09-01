import random
from collections.abc import Callable
from pathlib import Path
from typing import Any

from PIL import Image
from torch.utils.data import Dataset

from chessvision.constants import CLASS_TO_INDEX, PIECE_CLASSES

TRAIN_DIR = Path(__file__).resolve().parent
BOARD_SQUARES_DIR = TRAIN_DIR / "assets" / "board_squares"
PIECE_SETS_DIR = TRAIN_DIR / "assets" / "piece_sets"


class ChessDataset(Dataset):
    def __init__(
        self,
        epoch_size: int,
        transform: Callable[[Image.Image], Any] | None = None,
        board_squares_dir: Path = BOARD_SQUARES_DIR,
        piece_sets_dir: Path = PIECE_SETS_DIR,
    ) -> None:
        self.epoch_size = epoch_size
        self.transform = transform
        self.classes = PIECE_CLASSES

        if not board_squares_dir.exists() or not piece_sets_dir.exists():
            raise FileNotFoundError(
                f"Assets not found. Expected {board_squares_dir} and {piece_sets_dir}"
            )

        self.backgrounds = [Image.open(p) for p in board_squares_dir.glob("*.png")]
        self.pieces: dict[str, list[Image.Image]] = {
            label: [Image.open(p) for p in piece_sets_dir.glob(f"*_{label}.png")]
            for label in self.classes
            if label != "empty"
        }

    def __len__(self) -> int:
        return self.epoch_size

    def __getitem__(self, index: int) -> tuple[Any, int]:
        label = random.choice(self.classes)
        background = random.choice(self.backgrounds).copy()

        if label != "empty":
            piece = random.choice(self.pieces[label])

            # Random scale (85% - 105%)
            scale = random.uniform(0.85, 1.05)
            piece_resized = piece.resize(
                (int(piece.width * scale), int(piece.height * scale)),
                Image.Resampling.BICUBIC,
            )

            # Random jitter (±10px)
            base_x = (background.width - piece_resized.width) // 2
            base_y = (background.height - piece_resized.height) // 2

            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-10, 10)

            background.paste(
                piece_resized,
                (base_x + offset_x, base_y + offset_y),
                mask=piece_resized,
            )

        img = background.convert("RGB")

        if self.transform is not None:
            img = self.transform(img)

        return img, CLASS_TO_INDEX[label]
