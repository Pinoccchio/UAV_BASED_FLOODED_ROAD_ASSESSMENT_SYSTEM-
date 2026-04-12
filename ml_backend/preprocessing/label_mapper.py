"""
Label Mapper for UAV Flood Assessment Dataset.

Converts RescueNet (3-class damage) and FloodNet (binary flood) labels
into a unified 4-class vehicle passability system:
    0 - Passable
    1 - Limited Passability
    2 - Heavy-Vehicle-Only
    3 - Impassable

Strategy:
- RescueNet: Combines CSV classification labels + segmentation mask analysis
- FloodNet: Uses binary labels + mask-based flood severity estimation
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from tqdm import tqdm
import json

from segmentation_analyzer import SegmentationAnalyzer


@dataclass
class ImageLabel:
    """Container for processed image label."""
    image_path: Path
    class_id: int
    class_name: str
    confidence: float
    source_dataset: str
    metadata: Dict


class LabelMapper:
    """Maps multi-source labels to 4-class passability system."""

    # Class definitions (3-class system)
    CLASS_NAMES = {
        0: "passable",
        1: "limited_passability",
        2: "impassable"
    }

    # RescueNet CSV damage levels
    RESCUENET_DAMAGE_LEVELS = {
        0: "Superficial Damage",
        1: "Medium Damage",
        2: "Major Damage"
    }

    def __init__(self, dataset_root: Path, output_dir: Path):
        """
        Initialize label mapper.

        Args:
            dataset_root: Root directory containing RescueNet and FloodNet
            output_dir: Output directory for processed labels
        """
        self.dataset_root = Path(dataset_root)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.analyzer = SegmentationAnalyzer()
        self.processed_labels: List[ImageLabel] = []

        # Paths to dataset components
        self.rescuenet_root = self.dataset_root / "RescueNet"
        self.floodnet_root = self.dataset_root / "FloodNet"

    def load_rescuenet_csv(self, split: str = "train") -> pd.DataFrame:
        """
        Load RescueNet classification labels from CSV.

        Args:
            split: Dataset split (train/val/test)

        Returns:
            DataFrame with columns: [Image_ID, Neighborhood_ID]
        """
        # Try new path first (classification subdirectory)
        csv_path = self.rescuenet_root / "classification" / f"RescueNet-classification-{split}.csv"

        # Fallback to old path
        if not csv_path.exists():
            csv_path = self.rescuenet_root / f"rescuenet-{split}.csv"

        if not csv_path.exists():
            raise FileNotFoundError(f"CSV not found: {csv_path}")

        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} labels from {csv_path.name}")

        return df

    def map_rescuenet_to_passability(
        self,
        classification_label: int,
        flood_metrics: Dict,
        damage_metrics: Dict
    ) -> Tuple[int, float]:
        """
        Map RescueNet labels to 3-class passability.

        Decision tree combining classification + segmentation analysis:

        Superficial Damage (0):
            → Passable

        Medium Damage (1):
            IF road_blocked > 0.50 OR water > 0.50
                → Impassable
            ELSE
                → Limited Passability

        Major Damage (2):
            IF road_blocked > 0.40 OR water > 0.40
                → Impassable
            ELSE
                → Limited Passability

        Args:
            classification_label: RescueNet damage level (0, 1, 2)
            flood_metrics: Output from SegmentationAnalyzer
            damage_metrics: Building damage metrics

        Returns:
            Tuple of (class_id, confidence)
        """
        road_blocked_ratio = flood_metrics['road_blocked_ratio']
        water_ratio = flood_metrics['water_ratio']
        flood_severity = flood_metrics['flood_severity']

        # Superficial Damage → Passable
        if classification_label == 0:
            confidence = 0.95 if water_ratio < 0.10 else 0.85
            return 0, confidence

        # Medium Damage
        elif classification_label == 1:
            if road_blocked_ratio > 0.50 or water_ratio > 0.50:
                # Impassable (severe flooding)
                confidence = 0.85
                return 2, confidence
            else:
                # Limited Passability
                confidence = 0.80
                return 1, confidence

        # Major Damage
        elif classification_label == 2:
            if road_blocked_ratio > 0.40 or water_ratio > 0.40:
                # Impassable
                confidence = 0.90
                return 2, confidence
            else:
                # Limited Passability
                confidence = 0.75
                return 1, confidence

        else:
            # Fallback to Limited Passability with low confidence
            return 1, 0.50

    def map_floodnet_to_passability(
        self,
        binary_label: int,
        flood_metrics: Dict
    ) -> Tuple[int, float]:
        """
        Map FloodNet binary labels to 3-class passability.

        Non-flooded (1):
            → Passable

        Flooded (0):
            Use flood_severity score from FloodNet masks:
            road_flooded_ratio > 0.60 OR water_ratio > 0.50 → Impassable
            road_flooded_ratio > 0.30 OR water_ratio > 0.30 → Limited Passability
            else → Limited Passability (conservative)

        Args:
            binary_label: FloodNet label (0=flooded, 1=non-flooded)
            flood_metrics: Output from SegmentationAnalyzer.analyze_floodnet_mask()

        Returns:
            Tuple of (class_id, confidence)
        """
        if binary_label == 1:  # Non-flooded
            return 0, 0.90

        # Flooded - use FloodNet-specific metrics
        road_flooded_ratio = flood_metrics.get('road_flooded_ratio', 0.0)
        water_ratio = flood_metrics.get('water_ratio', 0.0)
        flood_severity = flood_metrics.get('flood_severity', 0.0)

        # High severity → Impassable
        if road_flooded_ratio > 0.60 or water_ratio > 0.50:
            return 2, 0.85  # Impassable

        # Medium/Low severity → Limited Passability
        elif road_flooded_ratio > 0.30 or water_ratio > 0.30:
            return 1, 0.75  # Limited

        # Very low severity but still marked flooded → Limited (conservative)
        else:
            return 1, 0.70  # Limited

    def process_rescuenet(self, split: str = "train") -> List[ImageLabel]:
        """
        Process RescueNet dataset split.

        Args:
            split: Dataset split (train/val/test)

        Returns:
            List of ImageLabel objects
        """
        print(f"\n=== Processing RescueNet {split} ===")

        # Load CSV labels
        df = self.load_rescuenet_csv(split)

        # Paths - try new structure first
        images_dir = self.rescuenet_root / split / f"{split}-org-img"
        masks_dir = self.rescuenet_root / split / f"{split}-label-img"

        # Fallback to old structure
        if not images_dir.exists():
            images_dir = self.rescuenet_root / f"rescuenet-{split}-images" / f"{split}-org-img"
            masks_dir = self.rescuenet_root / f"rescuenet-{split}-labels" / f"{split}-label-img"

        if not images_dir.exists():
            print(f"Warning: Images directory not found: {images_dir}")
            return []

        labels = []
        skipped = 0

        for idx, row in tqdm(df.iterrows(), total=len(df), desc=f"Processing {split}"):
            image_name = row['Image_ID']
            classification_label = row['Neighborhood_ID']

            # Construct paths
            # Image filename - check if extension already included
            if image_name.endswith(('.jpg', '.png')):
                image_path = images_dir / image_name
                base_name = image_name.rsplit('.', 1)[0]
            else:
                image_path = images_dir / f"{image_name}.jpg"
                base_name = image_name

            # Mask filename format: XXXXX_lab.png
            mask_path = masks_dir / f"{base_name}_lab.png"

            # Verify files exist
            if not image_path.exists():
                skipped += 1
                continue

            # If mask doesn't exist, use classification label only
            if not mask_path.exists():
                # Simple mapping without segmentation (3-class)
                if classification_label == 0:
                    class_id, confidence = 0, 0.80  # Passable
                elif classification_label == 1:
                    class_id, confidence = 1, 0.70  # Limited Passability
                else:
                    class_id, confidence = 2, 0.70  # Impassable
            else:
                # Full analysis with segmentation
                results = self.analyzer.analyze_mask(mask_path)
                flood_metrics = results['flood_metrics']
                damage_metrics = results['damage_metrics']

                class_id, confidence = self.map_rescuenet_to_passability(
                    classification_label,
                    flood_metrics,
                    damage_metrics
                )

            # Create label object
            label = ImageLabel(
                image_path=image_path,
                class_id=class_id,
                class_name=self.CLASS_NAMES[class_id],
                confidence=confidence,
                source_dataset=f"RescueNet-{split}",
                metadata={
                    'original_label': int(classification_label),
                    'original_label_name': self.RESCUENET_DAMAGE_LEVELS[classification_label],
                    'has_segmentation': mask_path.exists()
                }
            )

            labels.append(label)

        print(f"Processed: {len(labels)} images, Skipped: {skipped}")

        return labels

    def process_floodnet(self) -> List[ImageLabel]:
        """
        Process FloodNet Track-1 labeled dataset.

        FloodNet structure:
        FloodNet/FloodNet Challenge - Track 1/Train/Labeled/
            Flooded/
                image/  (51 JPG files)
                mask/   (51 PNG files with Track 2 segmentation)
            Non-Flooded/
                image/  (347 JPG files)
                mask/   (347 PNG files with Track 2 segmentation)

        Returns:
            List of ImageLabel objects
        """
        print(f"\n=== Processing FloodNet ===")

        # FloodNet labeled data path
        floodnet_train = (self.floodnet_root /
                         "FloodNet Challenge - Track 1" /
                         "Train" /
                         "Labeled")

        if not floodnet_train.exists():
            print(f"FloodNet labeled directory not found: {floodnet_train}")
            return []

        labels = []
        skipped = 0

        # Process Non-Flooded images (binary_label = 1)
        non_flooded_dir = floodnet_train / "Non-Flooded"
        if non_flooded_dir.exists():
            image_dir = non_flooded_dir / "image"
            mask_dir = non_flooded_dir / "mask"

            if image_dir.exists():
                for img_path in tqdm(list(image_dir.glob("*.jpg")),
                                    desc="Processing Non-Flooded"):
                    # Non-flooded → Passable (no need for mask analysis)
                    label = ImageLabel(
                        image_path=img_path,
                        class_id=0,  # Passable
                        class_name=self.CLASS_NAMES[0],
                        confidence=0.90,
                        source_dataset="FloodNet",
                        metadata={
                            'original_label': 1,
                            'original_label_name': 'Non-flooded',
                            'has_segmentation': False
                        }
                    )
                    labels.append(label)

        # Process Flooded images (binary_label = 0)
        # These require mask analysis to determine severity
        flooded_dir = floodnet_train / "Flooded"
        if flooded_dir.exists():
            image_dir = flooded_dir / "image"
            mask_dir = flooded_dir / "mask"

            if image_dir.exists() and mask_dir.exists():
                for img_path in tqdm(list(image_dir.glob("*.jpg")),
                                    desc="Processing Flooded"):
                    # Find corresponding mask
                    mask_path = mask_dir / f"{img_path.stem}_lab.png"

                    if not mask_path.exists():
                        skipped += 1
                        continue

                    # Analyze FloodNet Track 2 mask
                    flood_metrics = self.analyzer.analyze_floodnet_mask(mask_path)

                    # Map to 3-class based on flood severity
                    class_id, confidence = self.map_floodnet_to_passability(
                        binary_label=0,  # Flooded
                        flood_metrics=flood_metrics
                    )

                    label = ImageLabel(
                        image_path=img_path,
                        class_id=class_id,
                        class_name=self.CLASS_NAMES[class_id],
                        confidence=confidence,
                        source_dataset="FloodNet",
                        metadata={
                            'original_label': 0,
                            'original_label_name': 'Flooded',
                            'has_segmentation': True,
                            'flood_severity': flood_metrics['flood_severity'],
                            'road_flooded_ratio': flood_metrics['road_flooded_ratio'],
                            'water_ratio': flood_metrics['water_ratio']
                        }
                    )
                    labels.append(label)

        print(f"Processed: {len(labels)} images, Skipped: {skipped}")

        return labels

    def process_all_datasets(self) -> pd.DataFrame:
        """
        Process all datasets and combine into single DataFrame.

        Returns:
            DataFrame with all processed labels
        """
        all_labels = []

        # Process RescueNet splits
        for split in ['train', 'val', 'test']:
            try:
                labels = self.process_rescuenet(split)
                all_labels.extend(labels)
            except FileNotFoundError as e:
                print(f"Warning: {e}")

        # Process FloodNet
        try:
            labels = self.process_floodnet()
            all_labels.extend(labels)
        except Exception as e:
            print(f"Warning: Error processing FloodNet: {e}")

        self.processed_labels = all_labels

        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'image_path': str(label.image_path),
                'class_id': label.class_id,
                'class_name': label.class_name,
                'confidence': label.confidence,
                'source_dataset': label.source_dataset,
                'original_label': label.metadata.get('original_label'),
                'original_label_name': label.metadata.get('original_label_name'),
                'has_segmentation': label.metadata.get('has_segmentation')
            }
            for label in all_labels
        ])

        return df

    def analyze_class_distribution(self, df: pd.DataFrame):
        """
        Print class distribution statistics.

        Args:
            df: DataFrame with processed labels
        """
        if len(df) == 0:
            print("\n=== Class Distribution ===")
            print("No images processed!")
            return

        print("\n=== Class Distribution ===")
        class_counts = df['class_name'].value_counts()

        total = len(df)
        for class_name, count in class_counts.items():
            percentage = (count / total) * 100
            print(f"{class_name:25s}: {count:5d} ({percentage:5.2f}%)")

        print(f"\nTotal images: {total}")

        # By source dataset
        print("\n=== Distribution by Source ===")
        source_dist = df.groupby(['source_dataset', 'class_name']).size().unstack(fill_value=0)
        print(source_dist)

    def save_labels(self, df: pd.DataFrame, filename: str = "processed_labels.csv"):
        """
        Save processed labels to CSV.

        Args:
            df: DataFrame with labels
            filename: Output filename
        """
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False)
        print(f"\nSaved labels to: {output_path}")

        # Also save as JSON for metadata preservation
        json_path = self.output_dir / filename.replace('.csv', '.json')
        df.to_json(json_path, orient='records', indent=2)
        print(f"Saved JSON to: {json_path}")


def main():
    """Main execution function."""
    # Paths
    dataset_root = Path("C:/Users/User/Documents/first_year_files/folder_for_jobs/UAV/datasets")
    output_dir = Path("C:/Users/User/Documents/first_year_files/folder_for_jobs/UAV/ml_backend/data")

    # Initialize mapper
    mapper = LabelMapper(dataset_root, output_dir)

    # Process all datasets
    df = mapper.process_all_datasets()

    # Analyze distribution
    mapper.analyze_class_distribution(df)

    # Save results
    mapper.save_labels(df)

    print("\n[OK] Label mapping complete!")


if __name__ == "__main__":
    main()
