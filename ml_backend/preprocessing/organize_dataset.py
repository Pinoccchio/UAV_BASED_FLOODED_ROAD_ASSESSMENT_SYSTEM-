"""
Organize Dataset - Copy images into class-based directory structure.

Reads processed_labels.csv and organizes images into:
    data/processed/
        train/
            passable/
            limited_passability/
            impassable/
        val/
            passable/
            limited_passability/
            impassable/
        test/
            passable/
            limited_passability/
            impassable/
"""

import pandas as pd
import shutil
from pathlib import Path
from tqdm import tqdm
import argparse


def organize_dataset(labels_csv: Path, output_dir: Path):
    """
    Organize images into class-based directory structure.

    Args:
        labels_csv: Path to processed_labels.csv
        output_dir: Output directory (e.g., data/processed)
    """
    print(f"\n=== Organizing Dataset ===")
    print(f"Labels: {labels_csv}")
    print(f"Output: {output_dir}")

    # Load labels
    df = pd.read_csv(labels_csv)
    print(f"\nLoaded {len(df)} labels")

    # Create output directory structure
    output_dir = Path(output_dir)
    splits = ['train', 'val', 'test']
    classes = ['passable', 'limited_passability', 'impassable']

    for split in splits:
        for class_name in classes:
            class_dir = output_dir / split / class_name
            class_dir.mkdir(parents=True, exist_ok=True)

    print("\nCreated directory structure")

    # Organize images by split
    stats = {split: {class_name: 0 for class_name in classes} for split in splits}
    skipped = 0

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Organizing images"):
        image_path = Path(row['image_path'])
        class_name = row['class_name']
        source = row['source_dataset']

        # Determine split from source
        if 'train' in source.lower():
            split = 'train'
        elif 'val' in source.lower():
            split = 'val'
        elif 'test' in source.lower():
            split = 'test'
        elif 'FloodNet' in source:
            # FloodNet goes to train
            split = 'train'
        else:
            print(f"Warning: Unknown source {source}, skipping")
            skipped += 1
            continue

        # Check if source image exists
        if not image_path.exists():
            skipped += 1
            continue

        # Copy to destination
        dest_dir = output_dir / split / class_name
        dest_path = dest_dir / image_path.name

        # Copy file
        shutil.copy2(image_path, dest_path)
        stats[split][class_name] += 1

    # Print statistics
    print("\n=== Organization Complete ===\n")

    for split in splits:
        print(f"{split.upper()}:")
        for class_name in classes:
            count = stats[split][class_name]
            print(f"  {class_name:25s}: {count:5d} images")
        total = sum(stats[split].values())
        print(f"  {'TOTAL':25s}: {total:5d} images")
        print()

    overall_total = sum(sum(stats[split].values()) for split in splits)
    print(f"Overall Total: {overall_total} images")
    print(f"Skipped: {skipped} images")

    print(f"\n[OK] Dataset organized at: {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organize dataset into class directories")
    parser.add_argument(
        '--input',
        type=str,
        default='../data/processed_labels.csv',
        help='Path to processed_labels.csv'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='../data/processed',
        help='Output directory for organized dataset'
    )

    args = parser.parse_args()

    labels_csv = Path(args.input)
    output_dir = Path(args.output)

    if not labels_csv.exists():
        print(f"Error: Labels file not found: {labels_csv}")
        exit(1)

    organize_dataset(labels_csv, output_dir)
