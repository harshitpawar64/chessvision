from chessvision.board import BoardPrediction, BoardPredictor
from chessvision.classifier import PieceClassifier, SquarePrediction
from chessvision.constants import Orientation, Turn
from chessvision.detector import BoardDetector
from chessvision.pdf import PDFBoardPrediction, PDFPredictor

__version__ = "0.8.0"  # x-release-please-version

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
