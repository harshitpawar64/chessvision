from dataset import DATASET_DIR, TRAIN_DIR
from ultralytics import YOLO

from chessvision.constants import SQUARE_SIZE

MODELS_DIR = TRAIN_DIR / "models"


def main() -> None:
    model = YOLO(MODELS_DIR / "yolo26n-cls.pt")
    model.train(
        data=DATASET_DIR,
        epochs=50,
        patience=10,
        batch=256,
        imgsz=SQUARE_SIZE,
        project=MODELS_DIR,
        name="chess_piece_classifier",
        exist_ok=True,
    )

    model.export(format="onnx", dynamic=True, device="cpu")


if __name__ == "__main__":
    main()
