import time

import torch
from dataset import PIECE_CLASSES, TRAIN_DIR, ChessDataset
from safetensors.torch import save_file
from torch import nn
from torch.utils.data import DataLoader
from torchvision.models import MobileNet_V3_Small_Weights, mobilenet_v3_small
from transforms import IMAGE_SIZE, get_training_transform, get_validation_transform

MODELS_DIR = TRAIN_DIR / "models"

BATCH_SIZE = 128
EPOCHS = 10

TRAIN_EPOCH_SIZE = 50000
VALIDATION_EPOCH_SIZE = 5000
NUM_WORKERS = 4

if torch.cuda.is_available():
    DEVICE = "cuda"
elif torch.backends.mps.is_available():
    DEVICE = "mps"
else:
    DEVICE = "cpu"


def main() -> None:
    print(f"Using device: {DEVICE}")
    print(f"Classes ({len(PIECE_CLASSES)}): {PIECE_CLASSES}")

    weights = MobileNet_V3_Small_Weights.DEFAULT
    transforms_meta = weights.transforms()

    training_transform = get_training_transform(
        mean=transforms_meta.mean, std=transforms_meta.std
    )
    validation_transform = get_validation_transform(
        mean=transforms_meta.mean, std=transforms_meta.std
    )

    training_loader = DataLoader(
        ChessDataset(TRAIN_EPOCH_SIZE, training_transform),
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
        pin_memory=(DEVICE == "cuda"),
    )
    validation_loader = DataLoader(
        ChessDataset(VALIDATION_EPOCH_SIZE, validation_transform),
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=(DEVICE == "cuda"),
    )

    model = mobilenet_v3_small(weights=weights)
    model.classifier[3] = nn.Linear(model.classifier[3].in_features, len(PIECE_CLASSES))
    model = model.to(DEVICE)

    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)

    print("\n--- Starting Training ---")
    for epoch in range(EPOCHS):
        start_time = time.time()
        model.train()
        total_loss, correct, total = 0.0, 0, 0

        for images, labels in training_loader:
            images = images.to(DEVICE, non_blocking=True)
            labels = labels.to(DEVICE, non_blocking=True)

            optimizer.zero_grad()
            outputs = model(images)
            loss = loss_fn(outputs, labels)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            correct += (outputs.argmax(dim=1) == labels).sum().item()
            total += labels.size(0)

        scheduler.step()
        training_accuracy = correct / total
        avg_train_loss = total_loss / len(training_loader)

        model.eval()
        val_correct, val_total = 0, 0
        with torch.inference_mode():
            for images, labels in validation_loader:
                images, labels = (
                    images.to(DEVICE, non_blocking=True),
                    labels.to(DEVICE, non_blocking=True),
                )
                outputs = model(images)
                val_correct += (outputs.argmax(dim=1) == labels).sum().item()
                val_total += labels.size(0)

        validation_accuracy = val_correct / val_total
        epoch_time = time.time() - start_time

        print(
            f"Epoch {epoch + 1:02}/{EPOCHS:02} | "
            f"Training Acc: {training_accuracy:7.2%} | "
            f"Val Acc: {validation_accuracy:7.2%} | "
            f"Avg Loss: {avg_train_loss:6.4f} | "
            f"Time: {epoch_time:5.1f}s"
        )

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    safetensors_path = MODELS_DIR / "chess_piece_classifier.safetensors"
    save_file(
        model.state_dict(),
        safetensors_path,
        metadata={
            "architecture": "mobilenet_v3_small",
            "classes": ",".join(PIECE_CLASSES),
        },
    )
    print(f"Saved SafeTensors model to {safetensors_path}")

    onnx_path = MODELS_DIR / "chess_piece_classifier.onnx"
    model.eval().to("cpu")
    batch_dim = torch.export.Dim("batch_size", min=1, max=64)
    torch.onnx.export(
        model,
        (torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE),),
        onnx_path,
        input_names=["square"],
        output_names=["logits"],
        dynamic_shapes=({0: batch_dim},),
        external_data=False,
    )
    print(f"Exported ONNX model to {onnx_path}")


if __name__ == "__main__":
    main()
