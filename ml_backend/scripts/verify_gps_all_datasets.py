"""
Verify GPS EXIF data across all dataset images.

This script checks every image in RescueNet and FloodNet datasets
to confirm GPS metadata presence and extract coordinate ranges.
"""

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from pathlib import Path
from collections import defaultdict
import sys

def extract_gps_coordinates(image_path):
    """
    Extract GPS coordinates from image EXIF.

    Returns:
        tuple: (latitude, longitude, altitude) or None if no GPS data
    """
    try:
        image = Image.open(image_path)
        exif = image.getexif()

        if not exif:
            return None

        # Find GPS info
        gps_info = {}
        for tag_id in exif:
            tag = TAGS.get(tag_id, tag_id)
            if tag == 'GPSInfo':
                gps_data = exif.get_ifd(tag_id)
                for gps_tag_id in gps_data:
                    gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_info[gps_tag] = gps_data.get(gps_tag_id)

        if not gps_info or 'GPSLatitude' not in gps_info:
            return None

        # Parse latitude
        lat_dms = gps_info['GPSLatitude']
        lat_ref = gps_info.get('GPSLatitudeRef', 'N')
        lat_deg = float(lat_dms[0]) if hasattr(lat_dms[0], 'numerator') else lat_dms[0]
        lat_min = float(lat_dms[1]) if hasattr(lat_dms[1], 'numerator') else lat_dms[1]
        lat_sec = float(lat_dms[2]) if hasattr(lat_dms[2], 'numerator') else lat_dms[2]
        lat = lat_deg + lat_min / 60 + lat_sec / 3600
        if lat_ref == 'S':
            lat = -lat

        # Parse longitude
        lon_dms = gps_info['GPSLongitude']
        lon_ref = gps_info.get('GPSLongitudeRef', 'E')
        lon_deg = float(lon_dms[0]) if hasattr(lon_dms[0], 'numerator') else lon_dms[0]
        lon_min = float(lon_dms[1]) if hasattr(lon_dms[1], 'numerator') else lon_dms[1]
        lon_sec = float(lon_dms[2]) if hasattr(lon_dms[2], 'numerator') else lon_dms[2]
        lon = lon_deg + lon_min / 60 + lon_sec / 3600
        if lon_ref == 'W':
            lon = -lon

        # Parse altitude if available
        alt = None
        if 'GPSAltitude' in gps_info:
            alt_val = gps_info['GPSAltitude']
            alt = float(alt_val) if hasattr(alt_val, 'numerator') else alt_val

        return (lat, lon, alt)

    except Exception as e:
        print(f"Error processing {image_path.name}: {e}")
        return None


def scan_directory(directory, dataset_name):
    """
    Scan directory for images and check GPS data.

    Returns:
        dict: Statistics about GPS coverage
    """
    stats = {
        'total': 0,
        'with_gps': 0,
        'without_gps': 0,
        'coordinates': [],
        'missing_files': []
    }

    # Find all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    image_files = [f for f in directory.rglob('*') if f.suffix in image_extensions]

    print(f"\n{'='*60}")
    print(f"Scanning: {dataset_name}")
    print(f"Directory: {directory}")
    print(f"Found {len(image_files)} images")
    print(f"{'='*60}")

    for img_path in image_files:
        stats['total'] += 1
        coords = extract_gps_coordinates(img_path)

        if coords:
            stats['with_gps'] += 1
            stats['coordinates'].append(coords)

            # Print first few examples
            if stats['with_gps'] <= 3:
                lat, lon, alt = coords
                print(f"[+] {img_path.name}: ({lat:.6f}, {lon:.6f}, {alt:.1f}m)")
        else:
            stats['without_gps'] += 1
            stats['missing_files'].append(img_path.name)

            # Print first few missing
            if stats['without_gps'] <= 5:
                print(f"[-] {img_path.name}: NO GPS DATA")

    return stats


def print_summary(stats, dataset_name):
    """Print summary statistics."""
    print(f"\n{'='*60}")
    print(f"SUMMARY: {dataset_name}")
    print(f"{'='*60}")
    print(f"Total images:       {stats['total']:,}")
    print(f"With GPS:           {stats['with_gps']:,} ({stats['with_gps']/stats['total']*100:.1f}%)")
    print(f"Without GPS:        {stats['without_gps']:,} ({stats['without_gps']/stats['total']*100:.1f}%)")

    if stats['coordinates']:
        lats = [c[0] for c in stats['coordinates']]
        lons = [c[1] for c in stats['coordinates']]
        alts = [c[2] for c in stats['coordinates'] if c[2] is not None]

        print(f"\nCoordinate Ranges:")
        print(f"  Latitude:  {min(lats):.6f}° to {max(lats):.6f}°")
        print(f"  Longitude: {min(lons):.6f}° to {max(lons):.6f}°")
        if alts:
            print(f"  Altitude:  {min(alts):.1f}m to {max(alts):.1f}m")

        # Determine location
        avg_lat = sum(lats) / len(lats)
        avg_lon = sum(lons) / len(lons)

        print(f"\nAverage Center: ({avg_lat:.6f}, {avg_lon:.6f})")

        if 29.5 <= avg_lat <= 30.5 and -86 <= avg_lon <= -85:
            print("  -> Location: Florida (Hurricane Michael)")
        elif 29.0 <= avg_lat <= 30.0 and -96 <= avg_lon <= -95:
            print("  -> Location: Texas (Hurricane Harvey)")
        elif 14.0 <= avg_lat <= 15.0 and 120.0 <= avg_lon <= 121.5:
            print("  -> Location: Philippines")
        else:
            print(f"  -> Location: Other")

    if stats['without_gps'] > 0:
        print(f"\nFirst 10 files without GPS:")
        for fname in stats['missing_files'][:10]:
            print(f"  - {fname}")


def main():
    """Main function to verify GPS data across all datasets."""
    print("="*60)
    print("GPS VERIFICATION ACROSS ALL DATASETS")
    print("="*60)

    base_path = Path(__file__).parent.parent.parent / "datasets"

    all_stats = {}

    # Check RescueNet
    rescuenet_path = base_path / "RescueNet"
    if rescuenet_path.exists():
        for split in ['train', 'val', 'test']:
            split_path = rescuenet_path / split / f"{split}-org-img"
            if split_path.exists():
                stats = scan_directory(split_path, f"RescueNet - {split}")
                all_stats[f"RescueNet_{split}"] = stats
                print_summary(stats, f"RescueNet - {split}")
    else:
        print(f"\n[!] RescueNet not found at {rescuenet_path}")

    # Check FloodNet Track 1
    floodnet_track1_path = base_path / "FloodNet" / "FloodNet Challenge - Track 1"
    if floodnet_track1_path.exists():
        # Test split
        test_path = floodnet_track1_path / "Test" / "image"
        if test_path.exists():
            stats = scan_directory(test_path, "FloodNet Track 1 - Test")
            all_stats["FloodNet_Track1_test"] = stats
            print_summary(stats, "FloodNet Track 1 - Test")

        # Validation split
        val_path = floodnet_track1_path / "Validation" / "image"
        if val_path.exists():
            stats = scan_directory(val_path, "FloodNet Track 1 - Validation")
            all_stats["FloodNet_Track1_val"] = stats
            print_summary(stats, "FloodNet Track 1 - Validation")

        # Train split - check both Flooded and Non-Flooded subdirectories
        train_flooded_path = floodnet_track1_path / "Train" / "Labeled" / "Flooded"
        train_nonflooded_path = floodnet_track1_path / "Train" / "Labeled" / "Non-Flooded"

        # Scan both and combine stats
        train_stats = {
            'total': 0,
            'with_gps': 0,
            'without_gps': 0,
            'coordinates': [],
            'missing_files': []
        }

        if train_flooded_path.exists():
            flooded_stats = scan_directory(train_flooded_path, "FloodNet Track 1 - Train (Flooded)")
            # Merge into train_stats
            train_stats['total'] += flooded_stats['total']
            train_stats['with_gps'] += flooded_stats['with_gps']
            train_stats['without_gps'] += flooded_stats['without_gps']
            train_stats['coordinates'].extend(flooded_stats['coordinates'])
            train_stats['missing_files'].extend(flooded_stats['missing_files'])

        if train_nonflooded_path.exists():
            nonflooded_stats = scan_directory(train_nonflooded_path, "FloodNet Track 1 - Train (Non-Flooded)")
            # Merge into train_stats
            train_stats['total'] += nonflooded_stats['total']
            train_stats['with_gps'] += nonflooded_stats['with_gps']
            train_stats['without_gps'] += nonflooded_stats['without_gps']
            train_stats['coordinates'].extend(nonflooded_stats['coordinates'])
            train_stats['missing_files'].extend(nonflooded_stats['missing_files'])

        if train_stats['total'] > 0:
            all_stats["FloodNet_Track1_train"] = train_stats
            print_summary(train_stats, "FloodNet Track 1 - Train (Combined)")
    else:
        print(f"\n[!] FloodNet Track 1 not found at {floodnet_track1_path}")

    # Overall summary
    print(f"\n{'='*60}")
    print("OVERALL SUMMARY - ALL DATASETS")
    print(f"{'='*60}")

    total_images = sum(s['total'] for s in all_stats.values())
    total_with_gps = sum(s['with_gps'] for s in all_stats.values())
    total_without_gps = sum(s['without_gps'] for s in all_stats.values())

    print(f"Total images across all datasets:  {total_images:,}")
    print(f"Images with GPS:                   {total_with_gps:,} ({total_with_gps/total_images*100:.1f}%)")
    print(f"Images without GPS:                {total_without_gps:,} ({total_without_gps/total_images*100:.1f}%)")

    print(f"\nBreakdown by dataset:")
    for name, stats in all_stats.items():
        pct = stats['with_gps'] / stats['total'] * 100 if stats['total'] > 0 else 0
        print(f"  {name:30s}: {stats['with_gps']:4d}/{stats['total']:4d} ({pct:5.1f}%)")

    print(f"\n{'='*60}")
    print("Verification complete!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
