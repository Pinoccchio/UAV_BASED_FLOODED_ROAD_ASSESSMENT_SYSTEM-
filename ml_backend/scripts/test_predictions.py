"""
Test Predictions Visualizer
Runs trained model on all test images and shows predictions vs ground truth
"""

import torch
import sys
from pathlib import Path
import pandas as pd
from PIL import Image
import numpy as np
from torchvision import transforms
from tqdm import tqdm

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.models.efficientnet import FloodPassabilityClassifier

# Class names
CLASS_NAMES = {
    0: "impassable",
    1: "limited_passability",
    2: "passable"
}

def load_model(checkpoint_path):
    """Load trained model from checkpoint"""
    print(f"Loading model from {checkpoint_path}...")
    model = FloodPassabilityClassifier.load_from_checkpoint(checkpoint_path)
    model.eval()
    model.to('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"✅ Model loaded on {'GPU' if torch.cuda.is_available() else 'CPU'}")
    return model

def preprocess_image(image_path):
    """Preprocess image for model input"""
    transform = transforms.Compose([
        transforms.Resize((448, 448)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    image = Image.open(image_path).convert('RGB')
    return transform(image).unsqueeze(0)

def predict_image(model, image_path, device):
    """Predict single image"""
    img_tensor = preprocess_image(image_path).to(device)

    with torch.no_grad():
        logits = model(img_tensor)
        probs = torch.softmax(logits, dim=1)
        pred_class = torch.argmax(probs, dim=1).item()
        confidence = probs[0, pred_class].item()

    return pred_class, confidence, probs[0].cpu().numpy()

def scan_test_images(model, test_dir, device):
    """Scan all test images and predict"""
    test_dir = Path(test_dir)

    results = {
        'impassable': {'correct': [], 'wrong': []},
        'limited_passability': {'correct': [], 'wrong': []},
        'passable': {'correct': [], 'wrong': []}
    }

    total_correct = 0
    total_images = 0

    print("\n" + "="*80)
    print("SCANNING TEST IMAGES")
    print("="*80 + "\n")

    # Scan each class directory
    for class_name in CLASS_NAMES.values():
        class_dir = test_dir / class_name

        if not class_dir.exists():
            print(f"⚠️  Warning: {class_dir} not found, skipping...")
            continue

        images = list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.png"))

        if not images:
            print(f"⚠️  Warning: No images found in {class_dir}")
            continue

        print(f"\n{'='*80}")
        print(f"CLASS: {class_name.upper()} ({len(images)} images)")
        print(f"{'='*80}\n")

        correct_count = 0

        for img_path in tqdm(images, desc=f"Processing {class_name}"):
            pred_class_id, confidence, probabilities = predict_image(model, img_path, device)
            pred_class_name = CLASS_NAMES[pred_class_id]

            # Get true class ID
            true_class_id = list(CLASS_NAMES.values()).index(class_name)

            is_correct = (pred_class_id == true_class_id)

            result = {
                'image': img_path.name,
                'true_class': class_name,
                'predicted_class': pred_class_name,
                'confidence': confidence,
                'probabilities': {
                    'impassable': probabilities[0],
                    'limited_passability': probabilities[1],
                    'passable': probabilities[2]
                },
                'correct': is_correct
            }

            if is_correct:
                results[class_name]['correct'].append(result)
                correct_count += 1
                total_correct += 1
            else:
                results[class_name]['wrong'].append(result)

            total_images += 1

        # Print class summary
        accuracy = (correct_count / len(images)) * 100 if images else 0
        print(f"\n✅ Correct: {correct_count}/{len(images)} ({accuracy:.2f}%)")
        print(f"❌ Wrong: {len(images) - correct_count}/{len(images)} ({100-accuracy:.2f}%)")

    return results, total_correct, total_images

def print_detailed_results(results):
    """Print detailed results for each class"""
    print("\n" + "="*80)
    print("DETAILED RESULTS")
    print("="*80 + "\n")

    for class_name in CLASS_NAMES.values():
        print(f"\n{'='*80}")
        print(f"CLASS: {class_name.upper()}")
        print(f"{'='*80}\n")

        correct = results[class_name]['correct']
        wrong = results[class_name]['wrong']
        total = len(correct) + len(wrong)

        if total == 0:
            print("No images in this class")
            continue

        accuracy = (len(correct) / total) * 100

        print(f"📊 Total Images: {total}")
        print(f"✅ Correct Predictions: {len(correct)} ({accuracy:.2f}%)")
        print(f"❌ Wrong Predictions: {len(wrong)} ({100-accuracy:.2f}%)\n")

        # Show wrong predictions
        if wrong:
            print(f"❌ MISCLASSIFICATIONS ({len(wrong)} images):")
            print("-" * 80)

            for result in wrong[:10]:  # Show first 10
                print(f"\nImage: {result['image']}")
                print(f"  True Class: {result['true_class']}")
                print(f"  Predicted: {result['predicted_class']} (confidence: {result['confidence']:.2%})")
                print(f"  Probabilities:")
                for cls, prob in result['probabilities'].items():
                    bar = '█' * int(prob * 50)
                    print(f"    {cls:20s}: {prob:.2%} {bar}")

            if len(wrong) > 10:
                print(f"\n  ... and {len(wrong) - 10} more misclassifications")

        # Show some correct predictions
        if correct:
            print(f"\n✅ CORRECT PREDICTIONS (showing first 5):")
            print("-" * 80)

            for result in correct[:5]:
                print(f"\nImage: {result['image']}")
                print(f"  Predicted: {result['predicted_class']} (confidence: {result['confidence']:.2%})")
                print(f"  Probabilities:")
                for cls, prob in result['probabilities'].items():
                    bar = '█' * int(prob * 50)
                    print(f"    {cls:20s}: {prob:.2%} {bar}")

def create_confusion_summary(results):
    """Create confusion matrix summary"""
    print("\n" + "="*80)
    print("CONFUSION MATRIX SUMMARY")
    print("="*80 + "\n")

    confusion = {
        'impassable': {'impassable': 0, 'limited_passability': 0, 'passable': 0},
        'limited_passability': {'impassable': 0, 'limited_passability': 0, 'passable': 0},
        'passable': {'impassable': 0, 'limited_passability': 0, 'passable': 0}
    }

    for true_class in CLASS_NAMES.values():
        for result in results[true_class]['correct']:
            confusion[true_class][result['predicted_class']] += 1

        for result in results[true_class]['wrong']:
            confusion[true_class][result['predicted_class']] += 1

    # Print matrix
    print(f"{'':20s} {'Predicted →':>20s}")
    print(f"{'True ↓':20s} {'Impassable':>15s} {'Limited':>15s} {'Passable':>15s}")
    print("-" * 80)

    for true_class in CLASS_NAMES.values():
        row = confusion[true_class]
        total = sum(row.values())

        print(f"{true_class:20s}", end="")
        for pred_class in CLASS_NAMES.values():
            count = row[pred_class]
            pct = (count / total * 100) if total > 0 else 0
            if count > 0:
                print(f" {count:3d} ({pct:5.1f}%)", end="")
            else:
                print(f" {'':11s}", end="")
        print()

def main():
    # Configuration
    checkpoint_path = "../checkpoints/epochepoch=45-valf1val/f1=0.7652.ckpt"
    test_dir = "../data/processed/test"

    print("="*80)
    print("UAV FLOOD ASSESSMENT - TEST PREDICTIONS SCANNER")
    print("="*80)
    print(f"\nCheckpoint: {checkpoint_path}")
    print(f"Test Directory: {test_dir}")

    # Load model
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = load_model(checkpoint_path)

    # Scan test images
    results, total_correct, total_images = scan_test_images(model, test_dir, device)

    # Print overall accuracy
    overall_accuracy = (total_correct / total_images) * 100 if total_images > 0 else 0

    print("\n" + "="*80)
    print("OVERALL RESULTS")
    print("="*80)
    print(f"\nTotal Images: {total_images}")
    print(f"Correct Predictions: {total_correct}")
    print(f"Wrong Predictions: {total_images - total_correct}")
    print(f"\n🎯 Overall Accuracy: {overall_accuracy:.2f}%\n")

    # Print detailed results
    print_detailed_results(results)

    # Print confusion matrix
    create_confusion_summary(results)

    print("\n" + "="*80)
    print("SCAN COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    main()
