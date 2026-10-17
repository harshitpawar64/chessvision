import numpy as np
from PIL import Image

from chessvision.classifier import PieceClassifier

classifier = PieceClassifier()


def test_predict_square() -> None:
    prediction = classifier.predict_square("assets/square.png")
    assert prediction.label == "bN"
    assert prediction.name == "Black Knight"


def test_predict_square_pil() -> None:
    img = Image.open("assets/square.png")
    prediction = classifier.predict_square(img)
    assert prediction.label == "bN"
    assert prediction.name == "Black Knight"


def test_predict_square_arr() -> None:
    img = Image.open("assets/square.png")
    arr = np.array(img)
    prediction_arr = classifier.predict_square(arr)
    assert prediction_arr.label == "bN"
    assert prediction_arr.name == "Black Knight"


def test_predict_squares_batch() -> None:
    predictions = classifier.predict_squares(["assets/square.png", "assets/square.png"])
    assert len(predictions) == 2
    assert all(prediction.label == "bN" for prediction in predictions)


def test_predict_squares_empty() -> None:
    assert classifier.predict_squares([]) == []
