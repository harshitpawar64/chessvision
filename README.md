<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/harshitpawar64/chessvision/main/assets/logo-dark.png">
    <img src="https://raw.githubusercontent.com/harshitpawar64/chessvision/main/assets/logo-light.png" width="420" alt="chessvision logo" />
  </picture>
</p>

<p align="center">
  <a href="https://github.com/harshitpawar64/chessvision/actions/workflows/ci.yml"><img src="https://github.com/harshitpawar64/chessvision/actions/workflows/ci.yml/badge.svg?event=push" alt="CI" /></a>
  <a href="https://codecov.io/github/harshitpawar64/chessvision"><img src="https://codecov.io/github/harshitpawar64/chessvision/graph/badge.svg" alt="codecov" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11+-35c555.svg?logo=python&labelColor=31373c&logoColor=skyblue" alt="python" /></a>
</p>

<p align="center">
  <a href="https://docs.astral.sh/uv/"><img src="https://img.shields.io/badge/uv-black.svg?logo=uv" alt="uv" /></a>
  <a href="https://docs.astral.sh/ruff/"><img src="https://img.shields.io/badge/ruff-black.svg?logo=ruff" alt="ruff" /></a>
  <a href="https://docs.astral.sh/ty/"><img src="https://img.shields.io/badge/ty-black.svg?logo=ty" alt="ty" /></a>
  <a href="https://docs.pytest.org/"><img src="https://img.shields.io/badge/pytest-black.svg?logo=pytest" alt="pytest" /></a>
</p>

<p align="center">
  A fast, lightweight chess board and piece recognition toolkit.
</p>

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

## Browser Extension

| Browser | Install from |
|:-------:|--------------|
| ![Firefox](https://raw.githubusercontent.com/alrra/browser-logos/refs/heads/main/src/firefox/firefox_48x48.png) | [Firefox Add-ons](https://addons.mozilla.org/firefox/addon/chessvision/) |
| ![Chrome](https://raw.githubusercontent.com/alrra/browser-logos/refs/heads/main/src/chrome/chrome_48x48.png) | [Build from source](#build-from-source) |
| ![Edge](https://raw.githubusercontent.com/alrra/browser-logos/refs/heads/main/src/edge/edge_48x48.png) | [Edge Add-ons](https://microsoftedge.microsoft.com/addons/detail/chessvision/ppkkggegonphgpmmonhhoeliokhdjbfo) |

<details id="build-from-source">
<summary><b>Build from source</b></summary>

1. Clone the repository:
   ```bash
   git clone https://github.com/harshitpawar64/chessvision.git
   cd chessvision
   ```
2. Build the browser extension bundles:
   ```bash
   uv run python extension/build.py
   ```

#### Chromium (Chrome, Edge, Brave, etc.)

1. Open your browser's extensions page (ex: `chrome://extensions`).
2. Toggle on **Developer mode** in the top-right corner.
3. Click **Load unpacked** and select the `extension/` directory.

#### Firefox

1. Open `about:debugging#/runtime/this-firefox`.
2. Click **Load Temporary Add-on...**.
3. Select the `dist/chessvision-firefox-v*.zip` file.

</details>

---

## Usage

### CLI

```bash
# Predict chess positions from a board, screenshot, or book page
chessvision board chessboard.png

# Predict directly from clipboard (screenshot or copied image)
chessvision board

# Predict chess positions from a PDF document
chessvision pdf document.pdf

# Predict a single square image
chessvision square square.png
```

### Python API

```python
from chessvision import (
    BoardDetector,
    BoardPredictor,
    Orientation,
    PDFPredictor,
    PieceClassifier,
    Turn,
)

# 1. Full Board Recognition
predictor = BoardPredictor()
prediction = predictor.predict(
    "chessboard.png", orientation=Orientation.AUTO, turn=Turn.AUTO, castling="auto"
)

print(prediction.ascii_board)
print(f"FEN: {prediction.fen}")
print(f"Confidence: {prediction.confidence:.2%}")
print(f"Valid: {prediction.is_valid}")
if not prediction.is_valid:
    print(f"Errors: {prediction.validation_errors}")
print(f"Lichess URL: {prediction.lichess_url}")
print(f"Chess.com URL: {prediction.chesscom_url}")

# Access the chess.Board object directly
board = prediction.board

# 2. Multi-Board Detection
detector = BoardDetector()
boards = detector.detect("page.png")  # Returns list of DetectedBoard objects

for board in boards:
    prediction = predictor.predict(board)
    print(f"Box: {board.box}, FEN: {prediction.fen}")

# 3. Multi-Page PDF Prediction
pdf_predictor = PDFPredictor()
for result in pdf_predictor.predict("document.pdf"):
    print(f"{result.label}: {result.prediction.fen}")

# 4. Single Square Classification
classifier = PieceClassifier()
square_prediction = classifier.predict_square("square.png")
print(f"{square_prediction.name} [{square_prediction.confidence:.2%}]")

# 5. Batch Squares Classification
batch_predictions = classifier.predict_squares(["e4.png", "e5.png"])
for prediction in batch_predictions:
    print(f"{prediction.name} [{prediction.confidence:.2%}]")
```

---

## CLI Subcommands

### `chessvision board`

| **Flag**        | **Short** | **Default** | **Description**                                  |
|-----------------|:---------:|:-----------:|--------------------------------------------------|
| `--orientation` |    `-o`   |    `auto`   | Board perspective (`auto`, `white`, or `black`). |
| `--turn`        |    `-t`   |    `auto`   | Side to move (`auto`, `white`, or `black`).      |
| `--castling`    |    `-c`   |    `auto`   | Castling availability (see options below).       |
| `--open`        |           |   `False`   | Open position directly in analysis board.        |
| `--site`        |    `-s`   |  `lichess`  | Analysis platform (`chess.com` or `lichess`).    |
| `--verbose`     |    `-v`   |   `False`   | Enable verbose logging.                          |

<details>
<summary><b>Castling Options</b></summary>

| **Value** | **Description**                              |
|:---------:|----------------------------------------------|
|   `auto`  | Automatically infer castling (default)       |
|    `-`    | No castling for both sides                   |
|  `[KQkq]` | Specific castling rights (e.g. KQkq, KQ, Qk) |

</details>

```bash
# Predict from clipboard (screenshot or copied image)
chessvision board

# Specify board perspective explicitly
chessvision board chessboard.png --orientation black
chessvision board chessboard.png -o white

# Specify castling availability explicitly
chessvision board chessboard.png --castling KQkq
chessvision board chessboard.png -c KQ

# Specify side to move explicitly
chessvision board chessboard.png --turn black
chessvision board chessboard.png -t white

# Specify analysis platform explicitly
chessvision board chessboard.png --open --site chess.com
chessvision board chessboard.png --open -s lichess
```

### `chessvision pdf`

| **Flag**    | **Short** | **Default** | **Description**          |
|-------------|:---------:|:-----------:|--------------------------|
| `--output`  |    `-o`   |    `None`   | Path to output PGN file. |
| `--verbose` |    `-v`   |   `False`   | Enable verbose logging.  |

```bash
# Predict chess positions from a PDF document
chessvision pdf document.pdf

# Export detected positions to a PGN file
chessvision pdf document.pdf --output positions.pgn
chessvision pdf document.pdf -o positions.pgn
```

### `chessvision square`

| **Flag**    | **Short** | **Default** | **Description**         |
|-------------|:---------:|:-----------:|-------------------------|
| `--verbose` |    `-v`   |   `False`   | Enable verbose logging. |

```bash
# Predict piece on a square image
chessvision square square.png
```

![square prediction demo](https://raw.githubusercontent.com/harshitpawar64/chessvision/main/assets/square_demo.png)


---

## Attributions

Training assets were extracted and preprocessed from:
- [Lichess](https://github.com/lichess-org/lila) open-source piece sets and board themes (see their [COPYING.md](https://github.com/lichess-org/lila/blob/master/COPYING.md) for individual asset licenses).
- [Chess.com](https://www.chess.com) piece sets and board themes (all rights reserved by Chess.com, LLC).

---

## License

This project is licensed under the [GNU GPL v3.0](https://github.com/harshitpawar64/chessvision/blob/main/LICENSE).
