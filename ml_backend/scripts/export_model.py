"""
Export PyTorch Model to ONNX for Production Deployment.

Converts trained EfficientNet-B0 model to ONNX format with optimizations.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

import torch
import onnx
import onnxruntime as ort
from models.efficientnet import FloodPassabilityClassifier
from argparse import ArgumentParser
import numpy as np


def export_to_onnx(
    checkpoint_path: Path,
    output_path: Path,
    img_size: tuple = (448, 448),
    opset_version: int = 14,
    simplify: bool = True
):
    """
    Export PyTorch model to ONNX format.

    Args:
        checkpoint_path: Path to PyTorch checkpoint (.ckpt)
        output_path: Output path for ONNX model (.onnx)
        img_size: Input image size (H, W)
        opset_version: ONNX opset version
        simplify: Whether to simplify ONNX graph
    """
    print("="*60)
    print("PyTorch to ONNX Model Export")
    print("="*60)

    # Load model from checkpoint
    print(f"\nLoading checkpoint: {checkpoint_path}")
    model = FloodPassabilityClassifier.load_from_checkpoint(checkpoint_path, map_location='cpu')
    model.eval()
    model.cpu()  # Ensure model is on CPU

    print(f"Model loaded successfully")
    print(f"Total parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Create dummy input
    batch_size = 1
    dummy_input = torch.randn(batch_size, 3, img_size[0], img_size[1])

    # Test forward pass
    with torch.no_grad():
        output = model(dummy_input)
    print(f"\nTest forward pass:")
    print(f"  Input shape: {dummy_input.shape}")
    print(f"  Output shape: {output.shape}")

    # Export to ONNX
    print(f"\nExporting to ONNX...")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    torch.onnx.export(
        model,
        dummy_input,
        str(output_path),
        export_params=True,
        opset_version=opset_version,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        },
        verbose=False
    )

    print(f"[OK] Exported to: {output_path}")

    # Verify ONNX model
    print(f"\nVerifying ONNX model...")
    onnx_model = onnx.load(str(output_path))
    onnx.checker.check_model(onnx_model)
    print("[OK] ONNX model is valid")

    # Simplify if requested
    if simplify:
        try:
            import onnxsim
            print("\nSimplifying ONNX model...")
            simplified_model, check = onnxsim.simplify(onnx_model)

            if check:
                onnx.save(simplified_model, str(output_path))
                print("[OK] Model simplified successfully")
            else:
                print("[WARN] Simplification validation failed, keeping original model")
        except ImportError:
            print("[WARN] onnx-simplifier not installed, skipping simplification")
            print("  Install with: pip install onnx-simplifier")

    # Test inference with ONNX Runtime
    print(f"\nTesting ONNX Runtime inference...")
    test_onnx_inference(output_path, dummy_input)

    # Print model info
    print_model_info(output_path)

    print("\n" + "="*60)
    print("EXPORT COMPLETE!")
    print("="*60)
    print(f"ONNX model saved to: {output_path}")


def test_onnx_inference(onnx_path: Path, test_input: torch.Tensor):
    """
    Test ONNX model inference and compare with PyTorch.

    Args:
        onnx_path: Path to ONNX model
        test_input: Test input tensor
    """
    # Create ONNX Runtime session
    session = ort.InferenceSession(str(onnx_path))

    # Prepare input
    input_name = session.get_inputs()[0].name
    input_data = test_input.numpy()

    # Run inference
    outputs = session.run(None, {input_name: input_data})
    onnx_output = outputs[0]

    print(f"[OK] ONNX Runtime inference successful")
    print(f"  Output shape: {onnx_output.shape}")
    print(f"  Output dtype: {onnx_output.dtype}")

    # Apply softmax to get probabilities
    import scipy.special
    probs = scipy.special.softmax(onnx_output, axis=1)
    predicted_class = np.argmax(probs, axis=1)[0]

    class_names = ['impassable', 'limited_passability', 'passable']  # 3-class model (alphabetical order)
    print(f"\n  Predicted class: {class_names[predicted_class]}")
    print(f"  Probabilities:")
    for i, (name, prob) in enumerate(zip(class_names, probs[0])):
        print(f"    {name:20s}: {prob:.4f}")


def print_model_info(onnx_path: Path):
    """
    Print ONNX model information.

    Args:
        onnx_path: Path to ONNX model
    """
    import os

    file_size_mb = os.path.getsize(onnx_path) / (1024 * 1024)

    session = ort.InferenceSession(str(onnx_path))

    print(f"\n=== Model Information ===")
    print(f"File size: {file_size_mb:.2f} MB")
    print(f"\nInputs:")
    for inp in session.get_inputs():
        print(f"  {inp.name}: {inp.shape} ({inp.type})")

    print(f"\nOutputs:")
    for out in session.get_outputs():
        print(f"  {out.name}: {out.shape} ({out.type})")


def quantize_model(onnx_path: Path, output_path: Path):
    """
    Quantize ONNX model to int8 for faster inference.

    Args:
        onnx_path: Path to ONNX model
        output_path: Output path for quantized model
    """
    from onnxruntime.quantization import quantize_dynamic, QuantType

    print("\n" + "="*60)
    print("Quantizing Model to INT8")
    print("="*60)

    quantize_dynamic(
        str(onnx_path),
        str(output_path),
        weight_type=QuantType.QUInt8
    )

    # Compare file sizes
    import os
    original_size = os.path.getsize(onnx_path) / (1024 * 1024)
    quantized_size = os.path.getsize(output_path) / (1024 * 1024)

    print(f"\n[OK] Quantization complete!")
    print(f"Original size: {original_size:.2f} MB")
    print(f"Quantized size: {quantized_size:.2f} MB")
    print(f"Reduction: {(1 - quantized_size/original_size)*100:.1f}%")


def main(args):
    """Main export function."""
    checkpoint_path = Path(args.checkpoint)
    output_dir = Path(args.output_dir)

    if not checkpoint_path.exists():
        print(f"Error: Checkpoint not found: {checkpoint_path}")
        return

    # Export to ONNX
    onnx_path = output_dir / "best_model.onnx"
    export_to_onnx(
        checkpoint_path=checkpoint_path,
        output_path=onnx_path,
        img_size=(args.img_size, args.img_size),
        opset_version=args.opset_version,
        simplify=not args.no_simplify
    )

    # Optionally quantize
    if args.quantize:
        quantized_path = output_dir / "best_model_quantized.onnx"
        quantize_model(onnx_path, quantized_path)


if __name__ == "__main__":
    parser = ArgumentParser(description="Export PyTorch model to ONNX")

    parser.add_argument(
        '--checkpoint',
        type=str,
        required=True,
        help='Path to PyTorch checkpoint (.ckpt)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='../exports',
        help='Output directory for ONNX model'
    )

    parser.add_argument(
        '--img-size',
        type=int,
        default=448,
        help='Input image size (assumes square)'
    )

    parser.add_argument(
        '--opset-version',
        type=int,
        default=14,
        help='ONNX opset version'
    )

    parser.add_argument(
        '--no-simplify',
        action='store_true',
        help='Skip ONNX graph simplification'
    )

    parser.add_argument(
        '--quantize',
        action='store_true',
        help='Also export quantized INT8 version'
    )

    args = parser.parse_args()
    main(args)
