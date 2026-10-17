import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image

from chessvision.constants import PIECE_CLASSES

TRAIN_DIR = Path(__file__).resolve().parent
ASSETS_DIR = TRAIN_DIR / "assets"
DATASET_DIR = TRAIN_DIR / "datasets" / "chess_pieces"


class ChessPieceDataset:
    def __init__(self, assets_dir: Path = ASSETS_DIR) -> None:
        if not assets_dir.exists():
            raise FileNotFoundError(f"Assets directory not found: {assets_dir}")

        self.backgrounds = [
            Image.open(p).convert("RGBA")
            for p in sorted(assets_dir.rglob("board_squares/*.png"))
        ]
        self.pieces = {
            label: [
                Image.open(p).convert("RGBA")
                for p in sorted(assets_dir.rglob(f"piece_sets/*_{label}.png"))
            ]
            for label in PIECE_CLASSES
            if label != "empty"
        }

    def _generate_chunk(
        self, class_dir: Path, label: str, start_index: int, count: int, seed: int
    ) -> int:
        rng = random.Random(seed)

        if label == "empty":
            for i in range(start_index, start_index + count):
                bg = rng.choice(self.backgrounds)
                bg.save(f"{class_dir}/{label}_{i:05d}.png", compress_level=1)
        else:
            pieces = self.pieces[label]
            for i in range(start_index, start_index + count):
                bg = rng.choice(self.backgrounds).copy()
                piece = rng.choice(pieces)
                x = (bg.width - piece.width) // 2 + rng.randint(-8, 8)
                y = (bg.height - piece.height) // 2 + rng.randint(-8, 8)
                bg.paste(piece, (x, y), mask=piece)
                bg.save(f"{class_dir}/{label}_{i:05d}.png", compress_level=1)

        return count

    def generate(
        self,
        output_dir: Path = DATASET_DIR,
        train_per_class: int = 10000,
        val_per_class: int = 1000,
        chunk_size: int = 250,
        seed: int = 42,
        max_workers: int | None = None,
    ) -> Path:
        splits = {"train": train_per_class, "val": val_per_class}
        chunks = []

        for split_name, count in splits.items():
            for label in PIECE_CLASSES:
                class_dir = output_dir / split_name / label
                class_dir.mkdir(parents=True, exist_ok=True)
                for start_index in range(0, count, chunk_size):
                    chunks.append(
                        (
                            class_dir,
                            label,
                            start_index,
                            min(chunk_size, count - start_index),
                        )
                    )

        total_images = (train_per_class + val_per_class) * len(PIECE_CLASSES)
        completed_images = 0
        start_time = time.perf_counter()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self._generate_chunk, *chunk, seed + chunk_index)
                for chunk_index, chunk in enumerate(chunks)
            ]
            for future in as_completed(futures):
                completed_images += future.result()
                elapsed = time.perf_counter() - start_time
                rate = completed_images / elapsed if elapsed > 0 else 0
                eta = (total_images - completed_images) / rate if rate > 0 else 0
                msg = (
                    f"Generated {completed_images:,}/{total_images:,} images "
                    f"({completed_images / total_images:.1%}) | "
                    f"{rate:.0f} img/s | ETA: {eta:.0f}s"
                )
                sys.stdout.write(f"\r{msg:<80}")
                sys.stdout.flush()

        total_time = time.perf_counter() - start_time
        rate = total_images / total_time if total_time > 0 else 0
        final_msg = (
            f"Generated {total_images:,}/{total_images:,} images (100.0%) | "
            f"{rate:.0f} img/s | Total time: {total_time:.1f}s"
        )
        sys.stdout.write(f"\r{final_msg:<80}\n")
        sys.stdout.flush()
        return output_dir


if __name__ == "__main__":
    ChessPieceDataset().generate()
