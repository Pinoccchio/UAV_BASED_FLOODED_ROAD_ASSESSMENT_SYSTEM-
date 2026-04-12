"""
Dataset Splitter for UAV Flood Assessment.

Organizes processed labels into train/val/test splits with stratification.
Copies images to organized directory structure for PyTorch DataLoader.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from shutil import copy2
from tqdm import tqdm
from typing import Tuple
import json


class DatasetSplitter:
    """Splits and organizes dataset into train/val/test directories."""

    def __init__(
        self,
        labels_csv: Path,
        output_dir: Path,
        val_size: float = 0.15,
        test_size: float = 0.15,
        random_seed: int = 42
    ):
        """
        Initialize dataset splitter.

        Args:
            labels_csv: Path to processed_labels.csv
            output_dir: Output directory for organized dataset
            val_size: Validation set proportion
            test_size: Test set proportion
            random_seed: Random seed for reproducibility
        """
        self.labels_csv = Path(labels_csv)
        self.output_dir = Path(output_dir)
        self.val_size = val_size
        self.test_size = test_size
        self.random_seed = random_seed

        # Load labels
        self.df = pd.read_csv(labels_csv)
        print(f"Loaded {len(self.df)} labels from {labels_csv.name}")

        # Class names
        self.class_names = ['passable', 'limited_passability', 'heavy_vehicle_only', 'impassable']

    def create_directory_structure(self):
        """Create organized directory structure."""
        for split in ['train', 'val', 'test']:
            for class_name in self.class_names:
                split_dir = self.output_dir / split / class_name
                split_dir.mkdir(parents=True, exist_ok=True)

        print("[OK] Created directory structure")

    def stratified_split(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split dataset with stratification by class.

        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        # First split: separate test set
        train_val_df, test_df = train_test_split(
            self.df,
            test_size=self.test_size,
            stratify=self.df['class_id'],
            random_state=self.random_seed
        )

        # Second split: separate validation set from training
        # Adjust val_size to account for already removed test set
        adjusted_val_size = self.val_size / (1 - self.test_size)

        train_df, val_df = train_test_split(
            train_val_df,
            test_size=adjusted_val_size,
            stratify=train_val_df['class_id'],
            random_state=self.random_seed
        )

        print(f"\n=== Split Sizes ===")
        print(f"Train: {len(train_df)} ({len(train_df)/len(self.df)*100:.1f}%)")
        print(f"Val:   {len(val_df)} ({len(val_df)/len(self.df)*100:.1f}%)")
        print(f"Test:  {len(test_df)} ({len(test_df)/len(self.df)*100:.1f}%)")

        # Verify stratification
        print(f"\n=== Class Distribution ===")
        for split_name, split_df in [('Train', train_df), ('Val', val_df), ('Test', test_df)]:
            dist = split_df['class_name'].value_counts(normalize=True) * 100
            print(f"\n{split_name}:")
            for class_name in self.class_names:
                pct = dist.get(class_name, 0)
                count = len(split_df[split_df['class_name'] == class_name])
                print(f"  {class_name:25s}: {count:4d} ({pct:5.2f}%)")

        return train_df, val_df, test_df

    def copy_images(self, split_df: pd.DataFrame, split_name: str):
        """
        Copy images to organized directory structure.

        Args:
            split_df: DataFrame for this split
            split_name: Split name (train/val/test)
        """
        print(f"\nCopying {split_name} images...")

        for idx, row in tqdm(split_df.iterrows(), total=len(split_df)):
            src_path = Path(row['image_path'])
            class_name = row['class_name']

            if not src_path.exists():
                print(f"Warning: Image not found: {src_path}")
                continue

            # Destination path: output_dir/split/class_name/image_name
            dst_path = self.output_dir / split_name / class_name / src_path.name

            # Copy image
            copy2(src_path, dst_path)

    def save_split_metadata(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        test_df: pd.DataFrame
    ):
        """
        Save split metadata as CSV and JSON.

        Args:
            train_df, val_df, test_df: DataFrames for each split
        """
        for split_name, split_df in [('train', train_df), ('val', val_df), ('test', test_df)]:
            # Add split column
            split_df = split_df.copy()
            split_df['split'] = split_name

            # Save CSV
            csv_path = self.output_dir / f"{split_name}_labels.csv"
            split_df.to_csv(csv_path, index=False)

            # Save JSON
            json_path = self.output_dir / f"{split_name}_labels.json"
            split_df.to_json(json_path, orient='records', indent=2)

            print(f"Saved {split_name} metadata to {csv_path.name}")

        # Save combined metadata
        combined_df = pd.concat([train_df, val_df, test_df])
        combined_path = self.output_dir / "dataset_splits.csv"
        combined_df.to_csv(combined_path, index=False)
        print(f"Saved combined metadata to {combined_path.name}")

    def generate_statistics(self, train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame):
        """
        Generate dataset statistics report.

        Args:
            train_df, val_df, test_df: DataFrames for each split
        """
        stats = {
            'total_images': len(self.df),
            'num_classes': len(self.class_names),
            'class_names': self.class_names,
            'splits': {
                'train': {
                    'count': len(train_df),
                    'percentage': len(train_df) / len(self.df) * 100
                },
                'val': {
                    'count': len(val_df),
                    'percentage': len(val_df) / len(self.df) * 100
                },
                'test': {
                    'count': len(test_df),
                    'percentage': len(test_df) / len(self.df) * 100
                }
            },
            'class_distribution': {},
            'source_datasets': self.df['source_dataset'].value_counts().to_dict()
        }

        # Per-class statistics
        for class_name in self.class_names:
            class_df = self.df[self.df['class_name'] == class_name]
            stats['class_distribution'][class_name] = {
                'total': len(class_df),
                'percentage': len(class_df) / len(self.df) * 100,
                'train': len(train_df[train_df['class_name'] == class_name]),
                'val': len(val_df[val_df['class_name'] == class_name]),
                'test': len(test_df[test_df['class_name'] == class_name])
            }

        # Save statistics
        stats_path = self.output_dir / "dataset_statistics.json"
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"\n[OK] Saved statistics to {stats_path.name}")

        return stats

    def run(self):
        """Execute complete dataset splitting pipeline."""
        print("=== Dataset Splitting Pipeline ===\n")

        # Create directory structure
        self.create_directory_structure()

        # Perform stratified split
        train_df, val_df, test_df = self.stratified_split()

        # Copy images to organized directories
        self.copy_images(train_df, 'train')
        self.copy_images(val_df, 'val')
        self.copy_images(test_df, 'test')

        # Save metadata
        self.save_split_metadata(train_df, val_df, test_df)

        # Generate statistics
        stats = self.generate_statistics(train_df, val_df, test_df)

        print("\n[OK] Dataset splitting complete!")
        print(f"\nOrganized dataset location: {self.output_dir}")

        return stats


def main():
    """Main execution function."""
    # Paths
    labels_csv = Path("C:/Users/User/Documents/first_year_files/folder_for_jobs/UAV/ml_backend/data/processed_labels.csv")
    output_dir = Path("C:/Users/User/Documents/first_year_files/folder_for_jobs/UAV/ml_backend/data/processed")

    if not labels_csv.exists():
        print(f"Error: Labels file not found: {labels_csv}")
        print("Please run label_mapper.py first to generate processed_labels.csv")
        return

    # Initialize splitter
    splitter = DatasetSplitter(
        labels_csv=labels_csv,
        output_dir=output_dir,
        val_size=0.15,
        test_size=0.15,
        random_seed=42
    )

    # Run pipeline
    stats = splitter.run()


if __name__ == "__main__":
    main()
