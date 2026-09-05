# chessvision ♟️

[![CI](https://github.com/harshitpawar64/chessvision/actions/workflows/ci.yml/badge.svg?event=push)](https://github.com/harshitpawar64/chessvision/actions/workflows/ci.yml)
[![python](https://img.shields.io/badge/Python-3.12_|_3.13_|_3.14-35c555.svg?logo=python&labelColor=31373c&logoColor=skyblue)](https://www.python.org/)

[![uv](https://img.shields.io/badge/uv-black.svg?logo=uv)](https://docs.astral.sh/uv/)
[![ruff](https://img.shields.io/badge/ruff-black.svg?logo=ruff)](https://docs.astral.sh/ruff/)
[![ty](https://img.shields.io/badge/ty-black.svg?logo=ty)](https://docs.astral.sh/ty/)

A fast, lightweight chess board and piece recognition toolkit.

![chessvision demo](https://raw.githubusercontent.com/harshitpawar64/chessvision/main/assets/demo.png)

---

## Install

```bash
# With uv (recommended)
uv tool install chessvision

# With pipx
pipx install chessvision
```

```bash
# As a library
uv add chessvision

# or
pip install chessvision
```

---

## Usage

### CLI

```bash
# Predict chess position on a full board image
chessvision board chessboard.png

# Predict a single square image
chessvision square square.png
```

### Python API

```python
from chessvision import BoardPredictor, Castling, Orientation, PieceClassifier, Turn

# 1. Full Board Recognition
predictor = BoardPredictor()
prediction = predictor.predict(
    "chessboard.png",
    orientation=Orientation.WHITE,
    active_color=Turn.WHITE,
    castling=Castling.ALL,
)

print(prediction.render_board)
print(f"FEN: {prediction.fen}")
print(f"Confidence: {prediction.confidence:.2%}")
print(f"URL: {prediction.url}")

# 2. Single Square Classification
classifier = PieceClassifier()
square_prediction = classifier.predict_square("square.png")
print(f"{square_prediction.label} [{square_prediction.confidence:.2%}]")

# 3. Batch Squares Classification
batch_predictions = classifier.predict_squares(["e4.png", "e5.png"])
for prediction in batch_predictions:
    print(f"{prediction.label} [{prediction.confidence:.2%}]")
```

---

## CLI Subcommands

### `chessvision board`

| **Flag**        | **Short** | **Default** | **Description**                                                       |
|-----------------|:---------:|:-----------:|-----------------------------------------------------------------------|
| `--orientation` |    `-o`   |   `white`   | Board perspective (`white` or `black`).                               |
| `--turn`        |    `-t`   |   `white`   | Side to move (`white` or `black`).                                    |
| `--castling`    |    `-c`   |     `-`     | Castling availability (see [castling options](#castling-options)).    |
| `--open`        |           |   `False`   | Open position directly in Lichess editor.                             |

#### Castling Options

| **Value** | **Description**                      |
|:---------:|--------------------------------------|
|    `-`    | No castling for both sides (default) |
|   `KQkq`  | Both sides can castle both sides     |
|    `KQ`   | White can castle both sides          |
|    `kq`   | Black can castle both sides          |
|    `K`    | White can castle kingside only       |
|    `Q`    | White can castle queenside only      |
|    `k`    | Black can castle kingside only       |
|    `q`    | Black can castle queenside only      |

```bash
# Specify board perspective (white or black orientation)
chessvision board chessboard.png --orientation black
chessvision board chessboard.png -o black

# Specify castling availability
chessvision board chessboard.png --castling KQkq
chessvision board chessboard.png -c KQ

# Specify side to move (white or black)
chessvision board chessboard.png --turn black
chessvision board chessboard.png -t black

# Open position directly in Lichess editor
chessvision board chessboard.png --open
```

### `chessvision square`

```bash
# Predict piece on a square image
chessvision square square.png
```

![square prediction demo](https://raw.githubusercontent.com/harshitpawar64/chessvision/main/assets/square_demo.png)

---

## Model & Cache Management

`chessvision` automatically downloads the pre-trained ONNX piece classifier (`chess_piece_classifier.onnx`) from [Hugging Face](https://huggingface.co/harshitpawar64/chessvision) on its first run and caches it locally:

### Default File Paths

| **OS**  | **Cache Path**                                                 |
|---------|----------------------------------------------------------------|
| Linux   | `~/.cache/chessvision/chess_piece_classifier.onnx`             |
| macOS   | `~/Library/Caches/chessvision/chess_piece_classifier.onnx`     |
| Windows | `%LOCALAPPDATA%\chessvision\Cache\chess_piece_classifier.onnx` |

---

## Attributions

Training assets were extracted, and preprocessed from [Lichess](https://github.com/lichess-org/lila) open-source piece sets and board themes (see their [COPYING.md](https://github.com/lichess-org/lila/blob/master/COPYING.md) for individual asset licenses).

---

## License

This project is licensed under the [MIT License](https://github.com/harshitpawar64/chessvision/blob/main/LICENSE).
