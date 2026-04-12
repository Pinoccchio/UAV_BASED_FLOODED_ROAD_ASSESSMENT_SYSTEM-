"""
Data Augmentation Pipeline for UAV Flood Assessment.

Provides augmentation transforms for training and preprocessing transforms
for validation/test sets.
"""

import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2
import numpy as np
from PIL import Image
from typing import Dict, Tuple


class AugmentationPipeline:
    """Augmentation and preprocessing pipelines for UAV imagery."""

    def __init__(
        self,
        img_size: Tuple[int, int] = (448, 448),
        normalize: bool = True
    ):
        """
        Initialize augmentation pipeline.

        Args:
            img_size: Target image size (height, width)
            normalize: Whether to apply ImageNet normalization
        """
        self.img_size = img_size
        self.normalize = normalize

        # ImageNet statistics for normalization
        self.mean = [0.485, 0.456, 0.406]
        self.std = [0.229, 0.224, 0.225]

    def get_training_transforms(self) -> A.Compose:
        """
        Get augmentation pipeline for training.

        Augmentations:
        - Resize to target size
        - Horizontal flip
        - Rotation (±15°)
        - Brightness/contrast adjustment
        - Color jitter
        - Normalization
        - Convert to tensor

        Returns:
            Albumentations Compose object
        """
        transforms = [
            # Resize
            A.Resize(height=self.img_size[0], width=self.img_size[1], interpolation=cv2.INTER_LINEAR),

            # Geometric augmentations
            A.HorizontalFlip(p=0.5),
            A.Rotate(limit=15, p=0.3, border_mode=cv2.BORDER_CONSTANT, value=0),

            # Color augmentations
            A.OneOf([
                A.RandomBrightnessContrast(
                    brightness_limit=0.2,
                    contrast_limit=0.2,
                    p=1.0
                ),
                A.HueSaturationValue(
                    hue_shift_limit=10,
                    sat_shift_limit=20,
                    val_shift_limit=10,
                    p=1.0
                ),
            ], p=0.3),

            A.ColorJitter(
                brightness=0.2,
                contrast=0.2,
                saturation=0.2,
                hue=0.1,
                p=0.2
            ),

            # Weather-specific augmentations (useful for flood imagery)
            A.OneOf([
                A.GaussNoise(var_limit=(10.0, 50.0), p=1.0),
                A.ISONoise(color_shift=(0.01, 0.05), intensity=(0.1, 0.5), p=1.0),
            ], p=0.2),

            # Slightly blur to simulate UAV camera motion
            A.OneOf([
                A.MotionBlur(blur_limit=5, p=1.0),
                A.GaussianBlur(blur_limit=3, p=1.0),
            ], p=0.1),
        ]

        # Add normalization if enabled
        if self.normalize:
            transforms.append(
                A.Normalize(mean=self.mean, std=self.std, max_pixel_value=255.0)
            )

        # Convert to PyTorch tensor
        transforms.append(ToTensorV2())

        return A.Compose(transforms)

    def get_validation_transforms(self) -> A.Compose:
        """
        Get preprocessing pipeline for validation/test.

        No augmentation, only:
        - Resize
        - Normalization
        - Convert to tensor

        Returns:
            Albumentations Compose object
        """
        transforms = [
            A.Resize(height=self.img_size[0], width=self.img_size[1], interpolation=cv2.INTER_LINEAR),
        ]

        if self.normalize:
            transforms.append(
                A.Normalize(mean=self.mean, std=self.std, max_pixel_value=255.0)
            )

        transforms.append(ToTensorV2())

        return A.Compose(transforms)

    def get_inference_transforms(self) -> A.Compose:
        """
        Get preprocessing pipeline for inference (production).

        Same as validation transforms.

        Returns:
            Albumentations Compose object
        """
        return self.get_validation_transforms()


class MinimalAugmentationPipeline:
    """
    Lightweight augmentation pipeline with fewer transforms.

    Use this if training is too slow or if augmentation degrades performance.
    """

    def __init__(
        self,
        img_size: Tuple[int, int] = (448, 448),
        normalize: bool = True
    ):
        self.img_size = img_size
        self.normalize = normalize
        self.mean = [0.485, 0.456, 0.406]
        self.std = [0.229, 0.224, 0.225]

    def get_training_transforms(self) -> A.Compose:
        """Minimal augmentation: resize, flip, normalize."""
        transforms = [
            A.Resize(height=self.img_size[0], width=self.img_size[1]),
            A.HorizontalFlip(p=0.5),
        ]

        if self.normalize:
            transforms.append(
                A.Normalize(mean=self.mean, std=self.std, max_pixel_value=255.0)
            )

        transforms.append(ToTensorV2())

        return A.Compose(transforms)

    def get_validation_transforms(self) -> A.Compose:
        """No augmentation: resize, normalize only."""
        transforms = [
            A.Resize(height=self.img_size[0], width=self.img_size[1]),
        ]

        if self.normalize:
            transforms.append(
                A.Normalize(mean=self.mean, std=self.std, max_pixel_value=255.0)
            )

        transforms.append(ToTensorV2())

        return A.Compose(transforms)


def test_augmentation():
    """Test augmentation pipeline with a sample image."""
    import matplotlib.pyplot as plt

    # Load test image
    test_image_path = "C:/Users/User/Documents/first_year_files/folder_for_jobs/UAV/datasets/RescueNet/rescuenet-train-images/train-org-img/10778.jpg"

    try:
        image = cv2.imread(test_image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        print(f"Original image shape: {image.shape}")

        # Initialize pipeline
        pipeline = AugmentationPipeline(img_size=(448, 448))

        # Get transforms
        train_transform = pipeline.get_training_transforms()
        val_transform = pipeline.get_validation_transforms()

        # Apply transforms
        augmented = train_transform(image=image)['image']
        preprocessed = val_transform(image=image)['image']

        print(f"Augmented tensor shape: {augmented.shape}")
        print(f"Preprocessed tensor shape: {preprocessed.shape}")

        # Visualize (denormalize for display)
        def denormalize(tensor, mean, std):
            """Denormalize tensor for visualization."""
            tensor = tensor.clone()
            for t, m, s in zip(tensor, mean, std):
                t.mul_(s).add_(m)
            return tensor

        aug_img = denormalize(augmented, pipeline.mean, pipeline.std).permute(1, 2, 0).numpy()
        pre_img = denormalize(preprocessed, pipeline.mean, pipeline.std).permute(1, 2, 0).numpy()

        # Clip to [0, 1]
        aug_img = np.clip(aug_img, 0, 1)
        pre_img = np.clip(pre_img, 0, 1)

        # Plot
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        axes[0].imshow(cv2.resize(image, (448, 448)))
        axes[0].set_title("Original")
        axes[0].axis('off')

        axes[1].imshow(aug_img)
        axes[1].set_title("Augmented")
        axes[1].axis('off')

        axes[2].imshow(pre_img)
        axes[2].set_title("Preprocessed")
        axes[2].axis('off')

        plt.tight_layout()
        plt.savefig("augmentation_test.png", dpi=150, bbox_inches='tight')
        print("\n✓ Saved augmentation visualization to augmentation_test.png")

    except FileNotFoundError:
        print(f"Test image not found: {test_image_path}")
        print("Skipping visualization test.")


if __name__ == "__main__":
    test_augmentation()
