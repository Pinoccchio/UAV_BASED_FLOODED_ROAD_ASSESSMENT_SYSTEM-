"""
Segmentation Mask Analyzer for RescueNet and FloodNet datasets.

This module parses PNG segmentation masks where pixel values encode class information.
It computes flood severity metrics and road condition statistics.

RescueNet Mask Encoding:
    0  → Background
    1  → Water
    2  → Building_No_Damage
    3  → Building_Minor_Damage
    4  → Building_Major_Damage
    5  → Building_Total_Destruction
    6  → Vehicle
    7  → Road-Clear
    8  → Road-Blocked
    9  → Tree
    10 → Pool
"""

import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, Tuple, Optional
import cv2


class SegmentationAnalyzer:
    """Analyzes segmentation masks to compute flood severity metrics."""

    # RescueNet class definitions
    CLASS_NAMES = {
        0: "Background",
        1: "Water",
        2: "Building_No_Damage",
        3: "Building_Minor_Damage",
        4: "Building_Major_Damage",
        5: "Building_Total_Destruction",
        6: "Vehicle",
        7: "Road-Clear",
        8: "Road-Blocked",
        9: "Tree",
        10: "Pool"
    }

    def __init__(self):
        self.valid_classes = set(self.CLASS_NAMES.keys())

    def load_mask(self, mask_path: Path) -> np.ndarray:
        """
        Load segmentation mask as numpy array.

        Args:
            mask_path: Path to PNG mask file

        Returns:
            numpy array with shape (H, W) containing class indices
        """
        mask = np.array(Image.open(mask_path))

        # Handle RGB masks (some datasets save masks as RGB)
        if len(mask.shape) == 3:
            mask = mask[:, :, 0]  # Take first channel

        return mask

    def compute_class_distribution(self, mask: np.ndarray) -> Dict[int, float]:
        """
        Compute percentage of each class in the mask.

        Args:
            mask: Segmentation mask array

        Returns:
            Dictionary mapping class_id -> percentage (0-100)
        """
        total_pixels = mask.size
        distribution = {}

        unique_classes, counts = np.unique(mask, return_counts=True)

        for class_id, count in zip(unique_classes, counts):
            if class_id in self.valid_classes:
                distribution[class_id] = (count / total_pixels) * 100

        return distribution

    def compute_flood_metrics(self, mask: np.ndarray) -> Dict[str, float]:
        """
        Compute flood severity metrics from segmentation mask.

        Key metrics:
        - water_ratio: Percentage of water pixels
        - road_blocked_ratio: Blocked road / total road pixels
        - road_clear_ratio: Clear road / total road pixels
        - flood_severity: Combined score (0-1) indicating severity

        Args:
            mask: Segmentation mask array

        Returns:
            Dictionary of flood metrics
        """
        total_pixels = mask.size

        # Count pixels for each class
        water_pixels = np.sum(mask == 1)
        road_clear_pixels = np.sum(mask == 7)
        road_blocked_pixels = np.sum(mask == 8)
        total_road_pixels = road_clear_pixels + road_blocked_pixels

        # Compute ratios
        water_ratio = water_pixels / total_pixels

        if total_road_pixels > 0:
            road_blocked_ratio = road_blocked_pixels / total_road_pixels
            road_clear_ratio = road_clear_pixels / total_road_pixels
        else:
            road_blocked_ratio = 0.0
            road_clear_ratio = 0.0

        # Compute composite flood severity score (0-1)
        # Weighted combination: 60% water coverage + 40% road blockage
        flood_severity = (0.6 * water_ratio) + (0.4 * road_blocked_ratio)

        return {
            'water_ratio': float(water_ratio),
            'road_blocked_ratio': float(road_blocked_ratio),
            'road_clear_ratio': float(road_clear_ratio),
            'total_road_pixels': int(total_road_pixels),
            'flood_severity': float(flood_severity)
        }

    def compute_damage_metrics(self, mask: np.ndarray) -> Dict[str, float]:
        """
        Compute building damage metrics.

        Args:
            mask: Segmentation mask array

        Returns:
            Dictionary of damage metrics
        """
        total_pixels = mask.size

        # Building damage classes
        no_damage = np.sum(mask == 2)
        minor_damage = np.sum(mask == 3)
        major_damage = np.sum(mask == 4)
        total_destruction = np.sum(mask == 5)

        total_buildings = no_damage + minor_damage + major_damage + total_destruction

        if total_buildings > 0:
            severe_damage_ratio = (major_damage + total_destruction) / total_buildings
        else:
            severe_damage_ratio = 0.0

        return {
            'building_coverage': float(total_buildings / total_pixels),
            'severe_damage_ratio': float(severe_damage_ratio),
            'no_damage_pct': float(no_damage / total_pixels * 100),
            'minor_damage_pct': float(minor_damage / total_pixels * 100),
            'major_damage_pct': float(major_damage / total_pixels * 100),
            'total_destruction_pct': float(total_destruction / total_pixels * 100)
        }

    def analyze_floodnet_mask(self, mask_path: Path) -> Dict[str, float]:
        """
        Analyze FloodNet Track 2 segmentation mask for flood severity.

        FloodNet Track 2 Mask Encoding:
            0  - Background
            1  - Building-flooded
            2  - Building-non-flooded
            3  - Road-flooded
            4  - Road-non-flooded
            5  - Water
            6  - Tree
            7  - Vehicle
            8  - Pool
            9  - Grass

        Args:
            mask_path: Path to FloodNet mask PNG file

        Returns:
            Dictionary containing flood severity metrics
        """
        mask = self.load_mask(mask_path)
        total_pixels = mask.size

        # Count pixels for FloodNet classes
        road_flooded = np.sum(mask == 3)
        road_non_flooded = np.sum(mask == 4)
        water = np.sum(mask == 5)
        building_flooded = np.sum(mask == 1)
        building_non_flooded = np.sum(mask == 2)

        total_road = road_flooded + road_non_flooded
        total_building = building_flooded + building_non_flooded

        # Compute ratios
        if total_road > 0:
            road_flooded_ratio = road_flooded / total_road
        else:
            road_flooded_ratio = 0.0

        water_ratio = water / total_pixels

        if total_building > 0:
            building_flooded_ratio = building_flooded / total_building
        else:
            building_flooded_ratio = 0.0

        # Flood severity score (weighted combination)
        # 70% weight on road flooding, 30% on water presence
        flood_severity = (0.7 * road_flooded_ratio) + (0.3 * water_ratio)

        return {
            'road_flooded_pixels': int(road_flooded),
            'road_non_flooded_pixels': int(road_non_flooded),
            'water_pixels': int(water),
            'building_flooded_pixels': int(building_flooded),
            'building_non_flooded_pixels': int(building_non_flooded),
            'road_flooded_ratio': float(road_flooded_ratio),
            'water_ratio': float(water_ratio),
            'building_flooded_ratio': float(building_flooded_ratio),
            'flood_severity': float(flood_severity),
            'total_road_pixels': int(total_road),
            'total_building_pixels': int(total_building)
        }

    def analyze_mask(self, mask_path: Path) -> Dict:
        """
        Complete analysis of a segmentation mask.

        Args:
            mask_path: Path to mask file

        Returns:
            Dictionary containing all metrics
        """
        mask = self.load_mask(mask_path)

        return {
            'mask_shape': mask.shape,
            'class_distribution': self.compute_class_distribution(mask),
            'flood_metrics': self.compute_flood_metrics(mask),
            'damage_metrics': self.compute_damage_metrics(mask)
        }

    def visualize_mask(self, mask: np.ndarray, output_path: Optional[Path] = None) -> np.ndarray:
        """
        Create color-coded visualization of segmentation mask.

        Args:
            mask: Segmentation mask array
            output_path: Optional path to save visualization

        Returns:
            RGB visualization array
        """
        # Color map for each class (BGR format for OpenCV)
        color_map = {
            0: [0, 0, 0],         # Background - Black
            1: [255, 0, 0],       # Water - Blue
            2: [0, 255, 0],       # Building_No_Damage - Green
            3: [0, 255, 255],     # Building_Minor_Damage - Yellow
            4: [0, 165, 255],     # Building_Major_Damage - Orange
            5: [0, 0, 255],       # Building_Total_Destruction - Red
            6: [255, 255, 255],   # Vehicle - White
            7: [147, 20, 255],    # Road-Clear - Pink
            8: [128, 0, 128],     # Road-Blocked - Purple
            9: [0, 128, 0],       # Tree - Dark Green
            10: [255, 255, 0]     # Pool - Cyan
        }

        # Create RGB image
        h, w = mask.shape
        vis = np.zeros((h, w, 3), dtype=np.uint8)

        for class_id, color in color_map.items():
            vis[mask == class_id] = color

        if output_path:
            cv2.imwrite(str(output_path), vis)

        return vis


def test_analyzer():
    """Test the analyzer on a sample mask."""
    analyzer = SegmentationAnalyzer()

    # Test with RescueNet image 10778_lab.png (from plan notes)
    test_mask_path = Path("C:/Users/User/Documents/first_year_files/folder_for_jobs/UAV/datasets/RescueNet/rescuenet-train-labels-vis/train-label-vis/10778_lab.png")

    if test_mask_path.exists():
        print(f"Analyzing: {test_mask_path.name}")
        results = analyzer.analyze_mask(test_mask_path)

        print("\n=== Mask Shape ===")
        print(f"{results['mask_shape']}")

        print("\n=== Class Distribution ===")
        for class_id, percentage in sorted(results['class_distribution'].items()):
            class_name = SegmentationAnalyzer.CLASS_NAMES[class_id]
            print(f"{class_name:30s}: {percentage:6.2f}%")

        print("\n=== Flood Metrics ===")
        for key, value in results['flood_metrics'].items():
            print(f"{key:25s}: {value:.4f}")

        print("\n=== Damage Metrics ===")
        for key, value in results['damage_metrics'].items():
            print(f"{key:25s}: {value:.4f}")
    else:
        print(f"Test file not found: {test_mask_path}")


if __name__ == "__main__":
    test_analyzer()
