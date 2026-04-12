# Sample Images for Demo

This directory contains sample flood images for quick testing in the frontend demo.

## Images

1. **passable-road.jpg** (5.0 MB)
   - Source: RescueNet train set (13272.jpg)
   - Expected class: Passable (class 0)
   - Original label: Superficial Damage
   - Confidence: 0.95
   - Description: Minimal water, safe for all vehicles

2. **limited-flood.jpg** (9.1 MB)
   - Source: RescueNet test set (15180.jpg)
   - Expected class: Limited Passability (class 1)
   - Original label: Medium Damage
   - Confidence: 0.8
   - Description: Moderate flooding, high-clearance vehicles only

3. **impassable-flood.jpg** (4.6 MB)
   - Source: RescueNet test set (11401.jpg)
   - Expected class: Impassable (class 3)
   - Original label: Major Damage
   - Confidence: 0.9
   - Description: Severe flooding, road closed to all vehicles

**Note:** These images cover all 3 classification scenarios. RescueNet aerial imagery (Hurricane Michael 2018, Florida) does not contain GPS EXIF metadata - GPS functionality can be demonstrated by uploading a smartphone photo with location data enabled.

## Dataset Attribution

All sample images are from the **RescueNet** dataset:

- **Citation:** Rahnemoonfar, M., et al. (2023). "RescueNet: A High Resolution UAV Semantic Segmentation Dataset for Natural Disaster Damage Assessment"
- **Source:** RescueNet Classification Dataset (Hurricane Michael, Florida 2018)
- **License:** Creative Common License CC BY-NC-ND (Academic/Research Use)
- **Original Labels:** Superficial/Medium/Major Damage (road passability proxy)

## Usage

These images are automatically used by the frontend demo's "Quick Test: Sample Images" gallery. Users can click any sample to instantly run AI classification without uploading their own images.

## Adding/Replacing Images

To update sample images:

1. Choose images from `datasets/RescueNet/` or `datasets/FloodNet/`
2. Verify class labels in `ml_backend/data/processed/test_labels.csv`
3. Copy to this directory with descriptive filenames
4. Update `components/sections/AssessmentDemo.tsx` sampleImages array
5. Ensure images are under 10MB (resize if needed)
6. Maintain diversity: clear road, moderate flood, severe flood, GPS-tagged
