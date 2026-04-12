"""
Convert existing 4-class dataset to 3-class system per contract requirements.

Contract Classes:
    0 - Passable
    1 - Limited Passability (merge limited_passability + heavy_vehicle_only)
    2 - Impassable

This script:
1. Merges limited_passability and heavy_vehicle_only into limited_passability
2. Removes empty directories
3. Creates clean 3-class structure
"""

import shutil
from pathlib import Path
from tqdm import tqdm


def convert_to_3class(data_root: Path):
    """
    Convert 4-class dataset to 3-class.

    Args:
        data_root: Path to ml_backend/data/processed
    """
    data_root = Path(data_root)

    print("=" * 60)
    print("Converting 4-Class Dataset to 3-Class (Contract Compliant)")
    print("=" * 60)

    for split in ['train', 'val', 'test']:
        split_dir = data_root / split

        if not split_dir.exists():
            print(f"WARNING: {split} directory not found, skipping...")
            continue

        print(f"\nProcessing {split} split...")

        # Paths
        limited_passability_dir = split_dir / "limited_passability"
        heavy_vehicle_only_dir = split_dir / "heavy_vehicle_only"

        # Count before merge
        limited_count = len(list(limited_passability_dir.glob("*.jpg"))) if limited_passability_dir.exists() else 0
        heavy_count = len(list(heavy_vehicle_only_dir.glob("*.jpg"))) if heavy_vehicle_only_dir.exists() else 0

        print(f"  Current state:")
        print(f"    - limited_passability: {limited_count} images")
        print(f"    - heavy_vehicle_only: {heavy_count} images")

        # Merge heavy_vehicle_only into limited_passability
        if heavy_vehicle_only_dir.exists() and heavy_count > 0:
            print(f"  Merging heavy_vehicle_only -> limited_passability...")

            # Ensure limited_passability directory exists
            limited_passability_dir.mkdir(parents=True, exist_ok=True)

            # Copy all images from heavy_vehicle_only to limited_passability
            for img_file in tqdm(list(heavy_vehicle_only_dir.glob("*.jpg")), desc="    Copying images"):
                dest = limited_passability_dir / img_file.name

                # Handle duplicate filenames (shouldn't happen, but just in case)
                if dest.exists():
                    # Add suffix to avoid overwrite
                    stem = img_file.stem
                    dest = limited_passability_dir / f"{stem}_hv.jpg"

                shutil.copy2(img_file, dest)

            merged_count = len(list(limited_passability_dir.glob("*.jpg")))
            print(f"  SUCCESS: Merged! limited_passability now has {merged_count} images")

        # Remove old 4-class directories
        print(f"  Removing old/empty directories...")

        dirs_to_remove = [
            split_dir / "heavy_vehicle_only",
            split_dir / "heavy_vehicle",
            split_dir / "limited"
        ]

        for dir_path in dirs_to_remove:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"    - Removed: {dir_path.name}")

        # Verify final structure
        passable_count = len(list((split_dir / "passable").glob("*.jpg"))) if (split_dir / "passable").exists() else 0
        limited_final = len(list((split_dir / "limited_passability").glob("*.jpg"))) if (split_dir / "limited_passability").exists() else 0
        impassable_count = len(list((split_dir / "impassable").glob("*.jpg"))) if (split_dir / "impassable").exists() else 0

        print(f"\n  SUCCESS: Final 3-class structure:")
        print(f"    - passable: {passable_count} images")
        print(f"    - limited_passability: {limited_final} images")
        print(f"    - impassable: {impassable_count} images")
        print(f"    - Total: {passable_count + limited_final + impassable_count} images")

    print("\n" + "=" * 60)
    print("SUCCESS: Conversion Complete!")
    print("=" * 60)
    print("\nNew 3-Class Structure (Contract Compliant):")
    print("  0 - passable")
    print("  1 - limited_passability")
    print("  2 - impassable")
    print("\nNext step: Update model configuration for num_classes=3")


if __name__ == "__main__":
    # Path to processed data
    data_root = Path(__file__).parent.parent / "data" / "processed"

    if not data_root.exists():
        print(f"ERROR: {data_root} not found!")
        print("Make sure you're running from ml_backend/preprocessing/")
        exit(1)

    # Confirm before proceeding
    print(f"Data directory: {data_root}")
    print("\nWARNING: This will merge limited_passability + heavy_vehicle_only")
    print("WARNING: Old directories will be removed")

    response = input("\nProceed? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        convert_to_3class(data_root)
    else:
        print("Conversion cancelled.")
