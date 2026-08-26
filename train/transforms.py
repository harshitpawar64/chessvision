from collections.abc import Sequence

import torch
from torchvision.transforms import v2

IMAGE_SIZE = 128


def get_training_transform(
    mean: Sequence[float], std: Sequence[float], image_size: int = IMAGE_SIZE
) -> v2.Compose:
    return v2.Compose(
        [
            v2.RandomChoice(
                [
                    v2.Identity(),
                    *(
                        v2.Compose(
                            [
                                v2.Resize(
                                    (s, s), interpolation=v2.InterpolationMode.BILINEAR
                                ),
                                v2.Resize(
                                    (image_size, image_size),
                                    interpolation=v2.InterpolationMode.BICUBIC,
                                ),
                            ]
                        )
                        for s in (28, 40, 64)
                    ),
                ]
            ),
            v2.RandomApply([v2.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0))], p=0.3),
            v2.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.3, hue=0.05),
            v2.ToImage(),
            v2.ToDtype(torch.float32, scale=True),
            v2.Normalize(mean=mean, std=std),
        ]
    )


def get_validation_transform(mean: Sequence[float], std: Sequence[float]) -> v2.Compose:
    return v2.Compose(
        [
            v2.ToImage(),
            v2.ToDtype(torch.float32, scale=True),
            v2.Normalize(mean=mean, std=std),
        ]
    )
