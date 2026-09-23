import importlib
from typing import TYPE_CHECKING

__version__ = "0.9.0"  # x-release-please-version

__all__ = [
    "BoardDetector",
    "BoardPrediction",
    "BoardPredictor",
    "Orientation",
    "PDFBoardPrediction",
    "PDFPredictor",
    "PieceClassifier",
    "SquarePrediction",
    "Turn",
    "__version__",
]

if TYPE_CHECKING:
    from chessvision.board import BoardPrediction, BoardPredictor
    from chessvision.classifier import PieceClassifier, SquarePrediction
    from chessvision.constants import Orientation, Turn
    from chessvision.detector import BoardDetector
    from chessvision.pdf import PDFBoardPrediction, PDFPredictor


_LAZY_IMPORTS = {
    "BoardDetector": "chessvision.detector",
    "BoardPrediction": "chessvision.board",
    "BoardPredictor": "chessvision.board",
    "Orientation": "chessvision.constants",
    "PDFBoardPrediction": "chessvision.pdf",
    "PDFPredictor": "chessvision.pdf",
    "PieceClassifier": "chessvision.classifier",
    "SquarePrediction": "chessvision.classifier",
    "Turn": "chessvision.constants",
}


def __getattr__(name: str):
    if name in _LAZY_IMPORTS:
        module = importlib.import_module(_LAZY_IMPORTS[name])
        attr = getattr(module, name)

        globals()[name] = attr
        return attr
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
