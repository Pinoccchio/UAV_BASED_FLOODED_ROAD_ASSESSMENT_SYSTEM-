"""
PyTorch Dataset for UAV Flood Assessment.

Loads images from organized directory structure and applies augmentation.
"""

import torch
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from pathlib import Path
from PIL import Image
import numpy as np
import pandas as pd
from typing import Optional, Callable, Tuple, Dict
import cv2
import pytorch_lightning as pl

import sys
sys.path.append(str(Path(__file__).parent.parent.parent / "preprocessing"))
from augmentation import AugmentationPipeline


class FloodDataset(Dataset):
    """Dataset for flood passability classification."""

    # Auto-detected class mapping (will be updated in __init__)
    CLASS_TO_IDX = {}
    IDX_TO_CLASS = {}

    def __init__(
        self,
        data_dir: Path,
        split: str = 'train',
        transform: Optional[Callable] = None,
        use_csv: bool = False,
        csv_path: Optional[Path] = None
    ):
        """
        Initialize dataset.

        Args:
            data_dir: Root directory containing train/val/test splits
            split: Dataset split ('train', 'val', or 'test')
            transform: Albumentations transform pipeline
            use_csv: Load from CSV instead of directory structure
            csv_path: Path to CSV file (if use_csv=True)
        """
        self.data_dir = Path(data_dir)
        self.split = split
        self.transform = transform

        # Auto-detect classes from directory structure
        self._detect_classes()

        # Load data
        if use_csv and csv_path:
            self.samples = self._load_from_csv(csv_path)
        else:
            self.samples = self._load_from_directory()

        print(f"Loaded {len(self.samples)} images for {split} split")

    def _detect_classes(self):
        """Auto-detect classes from directory structure."""
        split_dir = self.data_dir / self.split

        if not split_dir.exists():
            # Fallback to default 3-class mapping
            FloodDataset.CLASS_TO_IDX = {
                'passable': 0,
                'limited_passability': 1,
                'impassable': 2
            }
            FloodDataset.IDX_TO_CLASS = {v: k for k, v in FloodDataset.CLASS_TO_IDX.items()}
            return

        # Get all class directories
        class_dirs = sorted([d.name for d in split_dir.iterdir() if d.is_dir()])

        # Create mapping
        FloodDataset.CLASS_TO_IDX = {class_name: idx for idx, class_name in enumerate(class_dirs)}
        FloodDataset.IDX_TO_CLASS = {idx: class_name for class_name, idx in FloodDataset.CLASS_TO_IDX.items()}

        print(f"Detected {len(class_dirs)} classes: {class_dirs}")

    def _load_from_directory(self) -> list:
        """
        Load images from organized directory structure.

        Expected structure:
            data_dir/split/class_name/*.jpg

        Returns:
            List of (image_path, class_id) tuples
        """
        samples = []
        split_dir = self.data_dir / self.split

        if not split_dir.exists():
            raise FileNotFoundError(f"Split directory not found: {split_dir}")

        for class_name, class_id in self.CLASS_TO_IDX.items():
            class_dir = split_dir / class_name

            if not class_dir.exists():
                print(f"Warning: Class directory not found: {class_dir}")
                continue

            # Find all images
            image_paths = list(class_dir.glob('*.jpg')) + list(class_dir.glob('*.png'))

            for image_path in image_paths:
                samples.append((image_path, class_id))

        return samples

    def _load_from_csv(self, csv_path: Path) -> list:
        """
        Load images from CSV file.

        CSV format: image_path, class_id, class_name, ...

        Args:
            csv_path: Path to CSV file

        Returns:
            List of (image_path, class_id) tuples
        """
        df = pd.read_csv(csv_path)

        samples = []
        for _, row in df.iterrows():
            image_path = Path(row['image_path'])
            class_id = int(row['class_id'])

            if image_path.exists():
                samples.append((image_path, class_id))

        return samples

    def __len__(self) -> int:
        """Return dataset size."""
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        """
        Get item by index.

        Args:
            idx: Sample index

        Returns:
            Tuple of (image_tensor, class_id)
        """
        image_path, class_id = self.samples[idx]

        # Load image
        image = cv2.imread(str(image_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Apply transform
        if self.transform:
            transformed = self.transform(image=image)
            image = transformed['image']

        return image, class_id

    def get_class_distribution(self) -> Dict[int, int]:
        """
        Get class distribution.

        Returns:
            Dictionary mapping class_id -> count
        """
        distribution = {i: 0 for i in range(len(self.CLASS_TO_IDX))}

        for _, class_id in self.samples:
            distribution[class_id] += 1

        return distribution

    def compute_class_weights(self) -> torch.Tensor:
        """
        Compute class weights for handling imbalance.

        Uses inverse frequency: weight = 1 / frequency

        Returns:
            Tensor of class weights
        """
        distribution = self.get_class_distribution()
        total = sum(distribution.values())

        weights = []
        for i in range(len(self.CLASS_TO_IDX)):
            count = distribution[i]
            if count > 0:
                weight = total / (len(self.CLASS_TO_IDX) * count)
            else:
                weight = 0.0
            weights.append(weight)

        return torch.tensor(weights, dtype=torch.float32)


class FloodDataModule(pl.LightningDataModule):
    """PyTorch Lightning DataModule for flood assessment."""

    def __init__(
        self,
        data_dir: Path,
        batch_size: int = 32,
        num_workers: int = 4,
        img_size: Tuple[int, int] = (448, 448),
        use_weighted_sampling: bool = True,
        pin_memory: bool = True
    ):
        """
        Initialize DataModule.

        Args:
            data_dir: Root directory containing processed dataset
            batch_size: Batch size for training
            num_workers: Number of data loading workers
            img_size: Target image size
            use_weighted_sampling: Use weighted sampling for class balance
            pin_memory: Pin memory for faster GPU transfer
        """
        super().__init__()
        self.data_dir = Path(data_dir)
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.img_size = img_size
        self.use_weighted_sampling = use_weighted_sampling
        self.pin_memory = pin_memory

        # Initialize augmentation pipeline
        self.aug_pipeline = AugmentationPipeline(img_size=img_size)

        # Datasets
        self.train_dataset = None
        self.val_dataset = None
        self.test_dataset = None

    def setup(self, stage: Optional[str] = None):
        """Setup datasets for each stage."""
        if stage == 'fit' or stage is None:
            # Training dataset
            self.train_dataset = FloodDataset(
                data_dir=self.data_dir,
                split='train',
                transform=self.aug_pipeline.get_training_transforms()
            )

            # Validation dataset
            self.val_dataset = FloodDataset(
                data_dir=self.data_dir,
                split='val',
                transform=self.aug_pipeline.get_validation_transforms()
            )

        if stage == 'test' or stage is None:
            # Test dataset
            self.test_dataset = FloodDataset(
                data_dir=self.data_dir,
                split='test',
                transform=self.aug_pipeline.get_validation_transforms()
            )

    def train_dataloader(self) -> DataLoader:
        """Create training dataloader."""
        if self.use_weighted_sampling:
            # Compute sample weights for balanced sampling
            class_counts = self.train_dataset.get_class_distribution()
            sample_weights = []

            for _, class_id in self.train_dataset.samples:
                weight = 1.0 / class_counts[class_id]
                sample_weights.append(weight)

            sampler = WeightedRandomSampler(
                weights=sample_weights,
                num_samples=len(sample_weights),
                replacement=True
            )

            return DataLoader(
                self.train_dataset,
                batch_size=self.batch_size,
                sampler=sampler,
                num_workers=self.num_workers,
                pin_memory=self.pin_memory,
                persistent_workers=True if self.num_workers > 0 else False
            )
        else:
            return DataLoader(
                self.train_dataset,
                batch_size=self.batch_size,
                shuffle=True,
                num_workers=self.num_workers,
                pin_memory=self.pin_memory,
                persistent_workers=True if self.num_workers > 0 else False
            )

    def val_dataloader(self) -> DataLoader:
        """Create validation dataloader."""
        return DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
            persistent_workers=True if self.num_workers > 0 else False
        )

    def test_dataloader(self) -> DataLoader:
        """Create test dataloader."""
        return DataLoader(
            self.test_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
            persistent_workers=True if self.num_workers > 0 else False
        )

    def get_class_weights(self) -> torch.Tensor:
        """Get class weights from training dataset."""
        if self.train_dataset is None:
            self.setup('fit')
        return self.train_dataset.compute_class_weights()


if __name__ == "__main__":
    # Test dataset loading
    data_dir = Path("C:/Users/User/Documents/first_year_files/folder_for_jobs/UAV/ml_backend/data/processed")

    if data_dir.exists():
        # Initialize DataModule
        dm = FloodDataModule(
            data_dir=data_dir,
            batch_size=4,
            num_workers=0,
            img_size=(448, 448)
        )

        # Setup
        dm.setup('fit')

        # Get class distribution
        print("\n=== Class Distribution ===")
        train_dist = dm.train_dataset.get_class_distribution()
        for class_id, count in train_dist.items():
            class_name = FloodDataset.IDX_TO_CLASS[class_id]
            print(f"{class_name:25s}: {count:4d}")

        # Get class weights
        weights = dm.get_class_weights()
        print("\n=== Class Weights ===")
        for class_id, weight in enumerate(weights):
            class_name = FloodDataset.IDX_TO_CLASS[class_id]
            print(f"{class_name:25s}: {weight:.4f}")

        # Test data loading
        train_loader = dm.train_dataloader()
        batch = next(iter(train_loader))
        images, labels = batch

        print(f"\n=== Test Batch ===")
        print(f"Images shape: {images.shape}")
        print(f"Labels shape: {labels.shape}")
        print(f"Labels: {labels}")
        print(f"Image min/max: {images.min():.3f} / {images.max():.3f}")

        print("\n✓ Dataset loading test passed!")
    else:
        print(f"Data directory not found: {data_dir}")
        print("Please run preprocessing scripts first.")
