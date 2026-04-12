# Quick Start Guide

Complete setup and training in ~30 minutes (excluding training time).

## Step 1: Installation (5 minutes)

```bash
# Navigate to project directory
cd ml_backend

# Create virtual environment
python -m venv venv

# Activate environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Process Data (10-15 minutes)

### Generate 4-Class Labels

```bash
cd preprocessing
python label_mapper.py
```

**Expected output:**
```
=== Processing RescueNet train ===
Loaded 3595 labels from rescuenet-train.csv
Processed: 3595 images, Skipped: 0

=== Class Distribution ===
passable              : 1800 (50.07%)
limited_passability   :  720 (20.03%)
heavy_vehicle_only    :  540 (15.02%)
impassable            :  535 (14.88%)

Total images: 3595
✓ Label mapping complete!
```

### Split Dataset

```bash
python dataset_splitter.py
```

**Expected output:**
```
=== Split Sizes ===
Train: 4200 (70.0%)
Val:    900 (15.0%)
Test:   900 (15.0%)

✓ Dataset splitting complete!
```

**Verify structure:**
```bash
# Check that organized dataset exists
ls ../data/processed/train/
# Should show: passable  limited_passability  heavy_vehicle_only  impassable
```

## Step 3: Train Model (6-8 hours)

### Start Training

```bash
cd ../scripts
python train.py --config ../configs/efficientnet_b0.yaml
```

### Monitor Progress

**Option 1: Console Output**
```
PHASE 1: Training Classifier Head (Frozen Backbone)
Epoch 1/3: 100%|███████| 132/132 [02:15<00:00]
train/loss: 1.2345 | val/loss: 0.9876 | val/acc: 0.7234

PHASE 2: Fine-tuning Last 2 Blocks
Epoch 4/13: 100%|███████| 132/132 [03:20<00:00]
train/loss: 0.8234 | val/loss: 0.6543 | val/acc: 0.8123

PHASE 3: Full End-to-End Fine-Tuning
Epoch 14/30: 100%|███████| 132/132 [04:15<00:00]
train/loss: 0.4567 | val/loss: 0.4123 | val/acc: 0.8734
```

**Option 2: TensorBoard**
```bash
# In a new terminal
tensorboard --logdir ../logs
# Open http://localhost:6006
```

### Expected Training Time

- **GPU (NVIDIA RTX 3060):** 6-8 hours
- **GPU (NVIDIA A100):** 3-4 hours
- **CPU only:** 24-36 hours (not recommended)

### What to Expect

**Phase 1 (Epochs 1-3):**
- Target: 70-75% accuracy
- Fast training (~2-3 min/epoch)

**Phase 2 (Epochs 4-13):**
- Target: 80-85% accuracy
- Medium speed (~3-4 min/epoch)

**Phase 3 (Epochs 14-30):**
- Target: 85%+ accuracy
- Slower (~4-5 min/epoch)
- Early stopping may trigger before epoch 30

## Step 4: Export Model (2 minutes)

```bash
# Find best checkpoint
ls ../checkpoints/
# Look for: epoch29-valf10.8912.ckpt (highest F1 score)

# Export to ONNX
python export_model.py \
  --checkpoint ../checkpoints/epoch29-valf10.8912.ckpt \
  --output-dir ../exports \
  --quantize
```

**Expected output:**
```
PyTorch to ONNX Model Export
Loading checkpoint: ../checkpoints/epoch29-valf10.8912.ckpt
Model loaded successfully
Total parameters: 5,288,548

Exporting to ONNX...
✓ Exported to: ../exports/best_model.onnx
✓ ONNX model is valid
✓ ONNX Runtime inference successful

File size: 21.45 MB
EXPORT COMPLETE!
```

## Step 5: Start API Server (1 minute)

```bash
cd ../api
python main.py
```

**Expected output:**
```
UAV Flood Passability API - Starting...
✓ Model loaded: ../exports/best_model.onnx
✓ API ready!

INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Test API

**Method 1: Interactive Docs**
1. Open browser: `http://localhost:8000/docs`
2. Click on `/api/v1/predict`
3. Click "Try it out"
4. Upload a test image
5. Click "Execute"

**Method 2: cURL**
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@test_image.jpg"
```

**Method 3: Python**
```python
import requests

url = "http://localhost:8000/api/v1/predict"
files = {"image": open("test_image.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

## Step 6: Evaluate Model (5 minutes)

```bash
# Run test set evaluation
cd ../scripts
python train.py --config ../configs/efficientnet_b0.yaml --skip-phase1 --skip-phase2 --skip-phase3

# Or load checkpoint and test
python -c "
from models.efficientnet import FloodPassabilityClassifier
from data.dataset import FloodDataModule
import pytorch_lightning as pl

model = FloodPassabilityClassifier.load_from_checkpoint('../checkpoints/best_model.ckpt')
dm = FloodDataModule(data_dir='../data/processed', batch_size=32)
dm.setup('test')

trainer = pl.Trainer(accelerator='auto', devices=1)
results = trainer.test(model, dm)
print(results)
"
```

**Expected output:**
```
=== Test Results ===
test/loss                : 0.4123
test/acc                 : 0.8734
test/f1                  : 0.8456
test/kappa               : 0.8234

test/passable_precision  : 0.9012
test/limited_precision   : 0.8234
test/heavy_vehicle_precision : 0.8123
test/impassable_precision: 0.8456
```

## Troubleshooting

### Issue: "CUDA out of memory"

**Solution:** Reduce batch size
```yaml
# Edit configs/efficientnet_b0.yaml
data:
  batch_size: 16  # or 8
```

### Issue: "No module named 'pytorch_lightning'"

**Solution:** Reinstall dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

### Issue: "Model not found" in API

**Solution:** Export model first
```bash
cd scripts
python export_model.py --checkpoint ../checkpoints/best_model.ckpt
```

### Issue: Low validation accuracy (<70%)

**Possible causes:**
1. Insufficient training data
2. Class imbalance
3. Wrong learning rate

**Solutions:**
1. Check class distribution:
   ```bash
   python preprocessing/label_mapper.py
   ```
2. Enable weighted sampling in config:
   ```yaml
   data:
     use_weighted_sampling: true
   ```
3. Adjust learning rates in config

### Issue: Training too slow

**Solutions:**
1. Enable mixed precision:
   ```yaml
   trainer:
     precision: 16-mixed
   ```
2. Increase num_workers:
   ```yaml
   data:
     num_workers: 8
   ```
3. Use smaller image size:
   ```yaml
   data:
     img_size: [224, 224]  # instead of [448, 448]
   ```

## Next Steps

### Integrate with Frontend

See the main implementation plan for integrating the API with the Next.js frontend.

Key files to modify:
1. `uav-based-flooded-road-assessment-system/app/api/predict/route.ts`
2. `uav-based-flooded-road-assessment-system/components/sections/AssessmentDemo.tsx`

### Deploy to Production

For production deployment:

1. **Containerize API:**
   ```bash
   # Create Dockerfile (see DEPLOYMENT.md)
   docker build -t flood-api .
   docker run -p 8000:8000 flood-api
   ```

2. **Set up load balancing**
3. **Add authentication**
4. **Enable HTTPS**
5. **Monitor with logging service**

See `DEPLOYMENT.md` for detailed instructions.

---

**Estimated Total Time:**
- Setup: 15-20 minutes
- Training: 6-8 hours (mostly unattended)
- Testing: 10 minutes

**Need Help?**
- Check README.md for detailed documentation
- Review logs in `logs/` directory
- Check model checkpoints in `checkpoints/` directory
