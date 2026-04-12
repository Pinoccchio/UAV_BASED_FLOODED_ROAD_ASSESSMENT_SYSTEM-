# GPU Setup for Training

**Date:** February 20, 2026, 11:48 PM
**Status:** GPU Available but PyTorch CPU-only installed

---

## Current Situation

### ✅ GPU Hardware Detected
- **GPU:** NVIDIA GeForce RTX 3050 Laptop GPU
- **VRAM:** 4GB
- **CUDA Version:** 13.0
- **Driver:** 581.42 (latest)
- **Status:** Idle and ready (0% usage)

### ❌ Problem: CPU-only PyTorch Installed
- **Current PyTorch:** 2.0.1+cpu (CPU-only build)
- **CUDA Available in PyTorch:** False
- **GPU Count in PyTorch:** 0

---

## Impact on Training Time

| Hardware | Training Time | Status |
|----------|---------------|--------|
| **CPU only** | 24-36 hours | Current (slow) |
| **GPU (RTX 3050)** | 6-8 hours | Possible (3-4× faster!) |

**Potential Time Savings:** 16-28 hours (67-78% reduction!)

---

## Solution: Install PyTorch with CUDA Support

### Option 1: Quick Fix - Install PyTorch with CUDA (Recommended)

**IMPORTANT:** Your CUDA 13.0 is very new. PyTorch 2.0.1 officially supports up to CUDA 11.8. However, it should work with CUDA 13.0 due to backward compatibility.

#### Step 1: Uninstall CPU-only PyTorch
```bash
pip uninstall torch torchvision
```

#### Step 2: Install PyTorch with CUDA 11.8 support
```bash
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --index-url https://download.pytorch.org/whl/cu118
```

**Why CUDA 11.8?**
- PyTorch 2.0.1 officially supports CUDA 11.8
- CUDA 13.0 is backward compatible, so cu118 builds will work
- This is the recommended approach

#### Step 3: Verify GPU is detected
```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
```

**Expected output:**
```
CUDA available: True
GPU: NVIDIA GeForce RTX 3050 Laptop GPU
```

---

### Option 2: Use Latest PyTorch (Alternative)

If Option 1 doesn't work, try the latest PyTorch version:

```bash
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

This installs PyTorch with CUDA 12.1 support, which is closer to your CUDA 13.0.

---

### Option 3: Continue with CPU (No Changes)

If GPU installation fails or causes issues, you can continue with CPU:
- Training time: 24-36 hours
- Works with current setup
- No additional installation needed

---

## GPU Training Configuration

### Will It Work with 4GB VRAM?

**Yes, with adjustments!**

Your RTX 3050 has 4GB VRAM. The current config uses:
- Batch size: 32
- Image size: 448×448
- Model: EfficientNet-B0 (5.3M params)

**Estimated VRAM usage:**
- Model weights: ~500MB
- Gradients: ~500MB
- Batch size 32: ~3.5-4GB

**This is tight! You may need to reduce batch size.**

### Recommended GPU Configuration

Edit `configs/efficientnet_b0.yaml`:

```yaml
data:
  batch_size: 16  # Reduced from 32 for 4GB VRAM
  num_workers: 4
  pin_memory: true

trainer:
  accelerator: gpu  # Changed from 'auto'
  devices: 1
  precision: 16-mixed  # Enable mixed precision for faster training
```

**Benefits of mixed precision:**
- 2× faster training
- 40% less memory usage
- Perfect for 4GB VRAM GPUs

---

## Expected Performance After GPU Setup

### Training Time Comparison

| Phase | CPU Time | GPU Time (FP32) | GPU Time (FP16 Mixed) |
|-------|----------|-----------------|----------------------|
| Phase 1 (3 epochs) | 2-3 hours | 30-45 min | 15-25 min |
| Phase 2 (10 epochs) | 8-10 hours | 2-2.5 hours | 1-1.5 hours |
| Phase 3 (15 epochs) | 12-15 hours | 3-4 hours | 1.5-2 hours |
| **TOTAL** | **24-36 hours** | **6-8 hours** | **3-5 hours** |

**With GPU + Mixed Precision: 3-5 hours total!** (85% time reduction!)

---

## Step-by-Step GPU Setup Guide

### 1. Backup Current Setup
```bash
# Save current packages
pip freeze > requirements_backup.txt
```

### 2. Uninstall CPU PyTorch
```bash
pip uninstall torch torchvision
```

**When prompted, type `y` to confirm.**

### 3. Install GPU PyTorch
```bash
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --index-url https://download.pytorch.org/whl/cu118
```

**This will download ~2-3 GB.**

### 4. Verify Installation
```bash
python -c "import torch; print('CUDA Available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

**Expected:**
```
CUDA Available: True
GPU: NVIDIA GeForce RTX 3050 Laptop GPU
```

### 5. Update Training Config

Edit `ml_backend/configs/efficientnet_b0.yaml`:

```yaml
data:
  batch_size: 16  # Reduced for 4GB VRAM

trainer:
  accelerator: gpu
  devices: 1
  precision: 16-mixed  # Enable mixed precision
```

### 6. Test GPU Training (Quick Test)

Create a test script to verify GPU training works:

```python
# test_gpu.py
import torch
import torch.nn as nn

# Check GPU
print(f"CUDA Available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")

# Create simple model
model = nn.Linear(100, 10).cuda()
x = torch.randn(32, 100).cuda()

# Forward pass
y = model(x)
print(f"Output device: {y.device}")
print("✓ GPU training test successful!")
```

Run:
```bash
python test_gpu.py
```

### 7. Start Real Training

Once verified:
```bash
cd scripts
python train.py --config ../configs/efficientnet_b0.yaml
```

**Monitor GPU usage:**
```bash
# In another terminal
watch -n 1 nvidia-smi
```

You should see GPU utilization at 80-100% and memory usage ~3-4GB.

---

## Troubleshooting

### Issue: "CUDA out of memory"

**Solution 1:** Reduce batch size further
```yaml
data:
  batch_size: 8  # Even smaller
```

**Solution 2:** Reduce image size
```yaml
data:
  img_size: [224, 224]  # Half the resolution
```

**Solution 3:** Use gradient accumulation
```yaml
training:
  accumulate_grad_batches: 2  # Effective batch size = 16
data:
  batch_size: 8  # Actual batch size = 8
```

### Issue: "CUDA available: False" after installation

**Possible causes:**
1. Wrong PyTorch version installed
2. CUDA driver mismatch
3. Environment variable issues

**Solutions:**
```bash
# Check PyTorch version
python -c "import torch; print(torch.__version__)"
# Should show: 2.0.1+cu118 (NOT 2.0.1+cpu)

# If still shows +cpu, reinstall:
pip uninstall torch torchvision -y
pip cache purge
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --index-url https://download.pytorch.org/whl/cu118
```

### Issue: Training slower on GPU than expected

**Check:**
1. Mixed precision enabled?
2. Data loading bottleneck? (increase num_workers)
3. GPU actually being used? (check nvidia-smi)

---

## Decision Matrix

| Scenario | Recommendation | Training Time |
|----------|---------------|---------------|
| **GPU setup works perfectly** | Use GPU with mixed precision | 3-5 hours |
| **GPU works but VRAM limited** | Use GPU with batch_size=8 | 5-7 hours |
| **GPU installation has issues** | Continue with CPU | 24-36 hours |
| **Want to be safe** | Start with CPU, switch to GPU later | 24-36 hours |

---

## My Recommendation

**🎯 Try GPU Setup (Option 1)**

**Reasoning:**
1. ✅ You have working GPU hardware (RTX 3050)
2. ✅ CUDA 13.0 installed and working
3. ✅ 4GB VRAM is sufficient with adjustments
4. ✅ Potential 85% time reduction (36h → 5h)
5. ✅ Easy to rollback if issues occur

**Low Risk:**
- Can always revert to CPU version
- Backup created before changes
- Only affects PyTorch packages

**High Reward:**
- 3-5 hours instead of 24-36 hours
- Better for iterating and debugging
- More professional setup

---

## Quick Commands Summary

### Install GPU PyTorch (Recommended)
```bash
# 1. Uninstall CPU version
pip uninstall torch torchvision -y

# 2. Install GPU version
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --index-url https://download.pytorch.org/whl/cu118

# 3. Verify
python -c "import torch; print('CUDA:', torch.cuda.is_available())"
```

### Update Config for GPU
```yaml
# configs/efficientnet_b0.yaml
data:
  batch_size: 16

trainer:
  accelerator: gpu
  devices: 1
  precision: 16-mixed
```

### Start Training
```bash
cd scripts
python train.py --config ../configs/efficientnet_b0.yaml
```

---

**Ready to proceed with GPU setup?**
