# UAV Flood Assessment Model Training

Deep learning pipeline for training a 3-class vehicle passability classifier using RescueNet and FloodNet datasets.

## Project Overview

This system trains an EfficientNet-B0 CNN to classify flooded road imagery into 3 vehicle passability levels:

1. **Passable** - Road is clear and safe for all vehicle types
2. **Limited Passability** - Road passable with caution for high-clearance vehicles only
3. **Impassable** - Road is completely blocked, no vehicles can pass (emergency vehicles only)

**Actual Performance (on US hurricane test data):**
- Overall Accuracy: 78.44%
- Macro F1-Score: 74.04%
- Cohen's Kappa: 0.6134
- Impassable Recall: 81.29% (with safety classifier: 83.02%)

## Quick Start

### 1. Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Data Preparation

```bash
# Run label mapping (converts datasets to 3-class system)
cd preprocessing
python label_mapper.py

# Split dataset into train/val/test
python dataset_splitter.py
```

Expected output structure:
```
ml_backend/data/processed/
├── train/
│   ├── passable/
│   ├── limited_passability/
│   └── impassable/
├── val/
└── test/
```

### 3. Training

```bash
# Train model with 3-phase transfer learning
cd scripts
python train.py --config ../configs/efficientnet_b0.yaml
```

Training phases:
- **Phase 1** (2-3 epochs): Train classifier head only
- **Phase 2** (5-10 epochs): Fine-tune last 2 blocks
- **Phase 3** (10-15 epochs): Full end-to-end fine-tuning

### 4. Model Export

```bash
# Export trained model to ONNX
python export_model.py \
  --checkpoint ../checkpoints/best_model.ckpt \
  --output-dir ../exports \
  --quantize
```

### 5. API Server

```bash
# Start FastAPI server
cd api
python main.py
```

API will be available at: `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs`

## Project Structure

```
ml_backend/
├── preprocessing/           # Data pipeline
│   ├── label_mapper.py      # Convert datasets to 3-class labels
│   ├── segmentation_analyzer.py  # Analyze segmentation masks
│   ├── augmentation.py      # Data augmentation
│   └── dataset_splitter.py  # Split into train/val/test
├── src/
│   ├── models/
│   │   └── efficientnet.py  # EfficientNet-B0 model
│   ├── data/
│   │   └── dataset.py       # PyTorch Dataset and DataModule
│   ├── training/
│   └── evaluation/
│       └── metrics.py       # Evaluation metrics and visualization
├── scripts/
│   ├── train.py             # Main training script
│   └── export_model.py      # PyTorch → ONNX export
├── api/
│   ├── main.py              # FastAPI application
│   └── services/
│       └── inference_service.py  # ONNX inference
├── configs/
│   └── efficientnet_b0.yaml # Training configuration
├── data/                    # Processed datasets
├── checkpoints/             # Model checkpoints
├── logs/                    # Training logs
└── exports/                 # ONNX models
```

## Dataset Processing

### RescueNet Label Mapping

RescueNet provides:
- **Classification labels**: 3 damage levels (Superficial, Medium, Major)
- **Segmentation masks**: 11 classes including Water, Road-Clear, Road-Blocked

**Mapping rules:**
```python
Superficial Damage (0) → Passable

Medium Damage (1):
  IF road_blocked < 30% AND water < 40%
    → Limited Passability
  ELSE
    → Impassable

Major Damage (2) → Impassable
```

### FloodNet Label Mapping

FloodNet provides:
- **Binary labels**: 0=Flooded, 1=Non-flooded

**Mapping rules:**
```python
Non-flooded (1) → Passable

Flooded (0):
  IF flood_severity < 0.35 → Limited Passability
  ELSE → Impassable
```

## Model Architecture

**Base Model:** EfficientNet-B0 (pretrained on ImageNet)

**Modifications:**
- Custom classifier head: 512 hidden units + dropout
- Focal loss for class imbalance
- Weighted random sampling

**Input:** 448x448 RGB images
**Output:** 3-class probabilities

**Parameters:** ~5.3M
**Inference time:** ~287ms on CPU (ONNX Runtime)

## Training Configuration

Key hyperparameters (see `configs/efficientnet_b0.yaml`):

```yaml
data:
  img_size: [448, 448]
  batch_size: 32
  use_weighted_sampling: true

training:
  phase1_lr: 0.001    # Classifier head only
  phase2_lr: 0.0001   # Last 2 blocks
  phase3_lr: 0.00005  # Full fine-tuning
  optimizer: adamw
  weight_decay: 0.0001

loss:
  type: focal_loss
  focal_gamma: 2.0
  use_class_weights: true
```

## API Usage

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "v1.0.0"
}
```

### Single Prediction

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@flooded_road.jpg"
```

Response:
```json
{
  "prediction": {
    "class": "limited_passability",
    "class_id": 1,
    "confidence": 0.8942,
    "probabilities": {
      "passable": 0.0512,
      "limited_passability": 0.8942,
      "impassable": 0.0546
    }
  },
  "vehicle_recommendations": {
    "civilian_sedan": false,
    "high_clearance_suv": true,
    "heavy_vehicle": true,
    "emergency_vehicle": true
  },
  "metadata": {
    "model_version": "v1.0.0",
    "inference_time_ms": 287
  }
}
```

### Batch Prediction

```bash
curl -X POST "http://localhost:8000/api/v1/batch-predict" \
  -F "images=@image1.jpg" \
  -F "images=@image2.jpg"
```

## Evaluation

### Generate Evaluation Report

```bash
cd src/evaluation
python metrics.py
```

Outputs:
- Confusion matrix (normalized and raw)
- Per-class precision/recall/F1
- Training curves (loss, accuracy, F1)
- Metrics JSON and text report

### Metrics Computed

- **Overall:** Accuracy, Macro F1, Cohen's Kappa
- **Per-class:** Precision, Recall, F1, Support
- **Confusion Matrix:** Both raw counts and normalized

## Troubleshooting

### Model not loading in API

```bash
# Check if ONNX model exists
ls exports/best_model.onnx

# If not, export from checkpoint
python scripts/export_model.py --checkpoint checkpoints/best_model.ckpt
```

### Out of memory during training

Reduce batch size in config:
```yaml
data:
  batch_size: 16  # or 8
```

### Low validation accuracy

Check class distribution:
```bash
python preprocessing/label_mapper.py
```

Ensure all classes have sufficient samples (>500 recommended).

### Slow training

Enable mixed precision:
```yaml
trainer:
  precision: 16-mixed
```

Use GPU if available:
```yaml
trainer:
  accelerator: gpu
```

## Dataset Requirements

**Location:** `../datasets/`

Expected structure:
```
datasets/
├── RescueNet/
│   ├── rescuenet-train-images/
│   ├── rescuenet-train-labels/
│   ├── rescuenet-train-labels-vis/
│   ├── rescuenet-train.csv
│   ├── rescuenet-val.csv
│   └── rescuenet-test.csv
└── FloodNet-Supervised_v1.0/
    ├── train-org-img/
    ├── train-label-img/
    └── train-label-img/FloodNet_Binary_Classification_Labels.csv
```

## Development

### Run Tests

```bash
# Test label mapper
python preprocessing/label_mapper.py

# Test dataset loading
python src/data/dataset.py

# Test model
python src/models/efficientnet.py

# Test inference service
python api/services/inference_service.py
```

### Add Custom Augmentations

Edit `preprocessing/augmentation.py`:

```python
# Add to training transforms
A.RandomRain(p=0.2),  # Simulate rain
A.RandomFog(p=0.1),   # Simulate fog
```

### Monitor Training

TensorBoard:
```bash
tensorboard --logdir logs/
```

Weights & Biases (if using):
```bash
wandb login
# Set logger in config to 'wandb'
```

## Citation

If you use this codebase, please cite:

```
UAV-Based Flooded Road Assessment System for Vehicle Passability Classification
Uses RescueNet and FloodNet datasets for training
```

**Datasets:**
- RescueNet: https://github.com/BinaLab/RescueNet-A-High-Resolution-UAV-Semantic-Segmentation-Dataset
- FloodNet: http://www.classic.grss-ieee.org/earthvision2021/challenge.html

## License

This project is for research and educational purposes.

## Contact

For issues or questions, please open an issue on the project repository.

---

**Last Updated:** February 2026
**Version:** 1.0.0
