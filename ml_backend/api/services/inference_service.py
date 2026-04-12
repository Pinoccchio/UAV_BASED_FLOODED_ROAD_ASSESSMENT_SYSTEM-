"""
Inference Service for ONNX Model.

Handles model loading, preprocessing, inference, and post-processing.
"""

import numpy as np
import onnxruntime as ort
from PIL import Image
import io
from pathlib import Path
from typing import Dict, List
import time
from .gps_extractor import GPSExtractor


class InferenceService:
    """ONNX model inference service."""

    # Class definitions (3 classes - alphabetical order from training)
    CLASS_NAMES = {
        0: "impassable",
        1: "limited_passability",
        2: "passable"
    }

    # Vehicle passability matrix
    VEHICLE_MATRIX = {
        0: {  # Impassable
            "civilian_sedan": False,
            "high_clearance_suv": False,
            "heavy_vehicle": False,
            "emergency_vehicle": True  # Only with special equipment
        },
        1: {  # Limited Passability
            "civilian_sedan": False,
            "high_clearance_suv": True,
            "heavy_vehicle": True,
            "emergency_vehicle": True
        },
        2: {  # Passable
            "civilian_sedan": True,
            "high_clearance_suv": True,
            "heavy_vehicle": True,
            "emergency_vehicle": True
        }
    }

    def __init__(self, model_path: Path, img_size: int = 448):
        """
        Initialize inference service.

        Args:
            model_path: Path to ONNX model
            img_size: Input image size (square)
        """
        self.model_path = Path(model_path)
        self.img_size = img_size
        self.session = None
        self.model_loaded = False

        # ImageNet normalization
        self.mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        self.std = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    def load_model(self):
        """Load ONNX model."""
        if not self.model_path.exists():
            print(f"Error: Model not found at {self.model_path}")
            print("Please run export_model.py to export the trained model to ONNX.")
            self.model_loaded = False
            return

        try:
            # Create ONNX Runtime session
            self.session = ort.InferenceSession(
                str(self.model_path),
                providers=['CPUExecutionProvider']  # Use GPU if available: ['CUDAExecutionProvider', 'CPUExecutionProvider']
            )

            self.model_loaded = True
            print(f"[OK] Model loaded from: {self.model_path}")

        except Exception as e:
            print(f"Error loading model: {str(e)}")
            self.model_loaded = False

    def preprocess(self, image_bytes: bytes) -> np.ndarray:
        """
        Preprocess image for inference.

        Args:
            image_bytes: Raw image bytes

        Returns:
            Preprocessed image array (1, 3, H, W)
        """
        # Load image
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Resize
        image = image.resize((self.img_size, self.img_size), Image.BILINEAR)

        # Convert to numpy array
        image_np = np.array(image, dtype=np.float32) / 255.0

        # Normalize
        image_np = (image_np - self.mean) / self.std

        # Transpose to (C, H, W)
        image_np = image_np.transpose(2, 0, 1)

        # Add batch dimension
        image_np = np.expand_dims(image_np, axis=0)

        return image_np

    def predict(self, image_bytes: bytes) -> Dict:
        """
        Run inference on image.

        Args:
            image_bytes: Raw image bytes

        Returns:
            Dictionary with prediction results
        """
        if not self.model_loaded:
            raise RuntimeError("Model not loaded")

        # Start timing
        start_time = time.time()

        # Extract GPS metadata from image
        gps_metadata = GPSExtractor.extract_gps_data(image_bytes)

        # Preprocess
        input_data = self.preprocess(image_bytes)

        # Run inference
        input_name = self.session.get_inputs()[0].name
        output_name = self.session.get_outputs()[0].name

        outputs = self.session.run([output_name], {input_name: input_data})
        logits = outputs[0]

        # Post-process
        result = self.postprocess(logits)

        # Add inference time
        inference_time_ms = (time.time() - start_time) * 1000
        result['metadata']['inference_time_ms'] = round(inference_time_ms, 2)

        # Add GPS metadata to result
        result['image_metadata'] = gps_metadata

        return result

    def postprocess(self, logits: np.ndarray) -> Dict:
        """
        Post-process model outputs.

        Args:
            logits: Raw model outputs (1, num_classes)

        Returns:
            Dictionary with formatted results
        """
        # Apply softmax
        exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
        probabilities = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
        probabilities = probabilities[0]  # Remove batch dimension

        # Get predicted class
        predicted_class_id = int(np.argmax(probabilities))
        predicted_class_name = self.CLASS_NAMES[predicted_class_id]
        confidence = float(probabilities[predicted_class_id])

        # Get vehicle recommendations
        vehicle_recommendations = self.VEHICLE_MATRIX[predicted_class_id]

        # Format response
        result = {
            "prediction": {
                "class": predicted_class_name,
                "class_id": predicted_class_id,
                "confidence": round(confidence, 4),
                "probabilities": {
                    self.CLASS_NAMES[i]: round(float(prob), 4)
                    for i, prob in enumerate(probabilities)
                }
            },
            "probabilities_array": probabilities,  # For safety classifier
            "vehicle_recommendations": vehicle_recommendations,
            "metadata": {
                "model_version": "v1.0.0"
            }
        }

        return result


if __name__ == "__main__":
    # Test inference service
    import sys

    model_path = Path(__file__).parent.parent.parent / "exports" / "best_model.onnx"

    if not model_path.exists():
        print(f"Model not found: {model_path}")
        print("Please export the model first using export_model.py")
        sys.exit(1)

    # Initialize service
    service = InferenceService(model_path=model_path)
    service.load_model()

    # Test with dummy image
    print("\n=== Testing Inference Service ===")

    # Create dummy image
    dummy_image = Image.new('RGB', (1000, 1000), color='blue')
    img_bytes = io.BytesIO()
    dummy_image.save(img_bytes, format='JPEG')
    img_bytes = img_bytes.getvalue()

    # Run inference
    result = service.predict(img_bytes)

    print("\n=== Prediction Result ===")
    print(f"Class: {result['prediction']['class']}")
    print(f"Confidence: {result['prediction']['confidence']:.4f}")
    print(f"\nProbabilities:")
    for class_name, prob in result['prediction']['probabilities'].items():
        print(f"  {class_name:25s}: {prob:.4f}")

    print(f"\nVehicle Recommendations:")
    for vehicle, can_pass in result['vehicle_recommendations'].items():
        status = "[OK] Can pass" if can_pass else "[X] Cannot pass"
        print(f"  {vehicle:25s}: {status}")

    print(f"\nInference time: {result['metadata']['inference_time_ms']:.2f} ms")

    print("\n[OK] Test complete!")
