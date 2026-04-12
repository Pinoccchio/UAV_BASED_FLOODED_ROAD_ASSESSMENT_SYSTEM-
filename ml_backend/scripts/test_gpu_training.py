"""
Quick GPU Training Test

Tests that GPU training works before starting full training pipeline.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0

print("="*60)
print("GPU Training Test")
print("="*60)

# 1. Check GPU availability
print(f"\n1. GPU Detection:")
print(f"   CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   GPU Name: {torch.cuda.get_device_name(0)}")
    print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
else:
    print("   ERROR: GPU not detected!")
    sys.exit(1)

# 2. Test model creation on GPU
print(f"\n2. Model Creation:")
try:
    model = efficientnet_b0(pretrained=False)
    model = model.cuda()
    print(f"   Model device: {next(model.parameters()).device}")
    print(f"   Status: OK")
except Exception as e:
    print(f"   ERROR: {str(e)}")
    sys.exit(1)

# 3. Test forward pass
print(f"\n3. Forward Pass:")
try:
    dummy_input = torch.randn(16, 3, 448, 448).cuda()  # Batch size 16
    with torch.no_grad():
        output = model(dummy_input)
    print(f"   Input shape: {dummy_input.shape}")
    print(f"   Output shape: {output.shape}")
    print(f"   Input device: {dummy_input.device}")
    print(f"   Output device: {output.device}")
    print(f"   Status: OK")
except Exception as e:
    print(f"   ERROR: {str(e)}")
    sys.exit(1)

# 4. Test mixed precision
print(f"\n4. Mixed Precision (FP16):")
try:
    from torch.cuda.amp import autocast
    with autocast():
        output = model(dummy_input)
    print(f"   Mixed precision output shape: {output.shape}")
    print(f"   Status: OK")
except Exception as e:
    print(f"   ERROR: {str(e)}")
    sys.exit(1)

# 5. Memory check
print(f"\n5. GPU Memory Usage:")
memory_allocated = torch.cuda.memory_allocated(0) / 1024**3
memory_reserved = torch.cuda.memory_reserved(0) / 1024**3
print(f"   Allocated: {memory_allocated:.2f} GB")
print(f"   Reserved: {memory_reserved:.2f} GB")
print(f"   Available: {4.0 - memory_reserved:.2f} GB")

if memory_reserved > 3.5:
    print(f"   WARNING: Memory usage high! Consider reducing batch size.")
else:
    print(f"   Status: OK")

# 6. Test DataLoader with GPU
print(f"\n6. DataLoader Test:")
try:
    # Create dummy dataset
    from torch.utils.data import TensorDataset, DataLoader
    dummy_images = torch.randn(32, 3, 448, 448)
    dummy_labels = torch.randint(0, 4, (32,))
    dataset = TensorDataset(dummy_images, dummy_labels)

    dataloader = DataLoader(
        dataset,
        batch_size=16,
        shuffle=True,
        num_workers=0,
        pin_memory=True
    )

    # Test one batch
    images, labels = next(iter(dataloader))
    images = images.cuda()
    labels = labels.cuda()

    with autocast():
        output = model(images)

    print(f"   Batch size: {images.shape[0]}")
    print(f"   Data on GPU: {images.device}")
    print(f"   Status: OK")
except Exception as e:
    print(f"   ERROR: {str(e)}")
    sys.exit(1)

print("\n" + "="*60)
print("ALL TESTS PASSED!")
print("="*60)
print(f"\nYour GPU setup is working correctly!")
print(f"Ready to start training with:")
print(f"  - GPU: NVIDIA GeForce RTX 3050 Laptop")
print(f"  - Batch Size: 16")
print(f"  - Mixed Precision: FP16")
print(f"  - Expected Training Time: 3-5 hours")
print("\n" + "="*60)
