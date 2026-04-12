"""
Test Predictions with Safety Classifier
Re-runs predictions with conservative safety measures applied
"""

import torch
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from torchvision import transforms
from tqdm import tqdm

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.models.efficientnet import FloodPassabilityClassifier
from api.services.safety_classifier import SafetyClassifier, SafetyMode

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

def predict_with_safety(model, image_path, device, safety_classifier):
    """Predict single image with safety measures"""
    img_tensor = preprocess_image(image_path).to(device)

    with torch.no_grad():
        logits = model(img_tensor)
        probs = torch.softmax(logits, dim=1)
        pred_class = torch.argmax(probs, dim=1).item()

    # Apply safety classifier
    probabilities = probs[0].cpu().numpy()
    safety_result = safety_classifier.classify(pred_class, probabilities)

    return safety_result

def scan_with_safety(model, test_dir, device, safety_classifier):
    """Scan all test images with safety measures"""
    test_dir = Path(test_dir)

    results = {
        'impassable': {'correct': [], 'wrong': [], 'safety_fixed': []},
        'limited_passability': {'correct': [], 'wrong': [], 'safety_fixed': []},
        'passable': {'correct': [], 'wrong': [], 'safety_fixed': []}
    }

    total_correct_original = 0
    total_correct_safety = 0
    total_safety_applied = 0
    total_images = 0

    print("\n" + "="*80)
    print("SCANNING TEST IMAGES WITH SAFETY CLASSIFIER")
    print("="*80 + "\n")

    # Scan each class directory
    for class_name in CLASS_NAMES.values():
        class_dir = test_dir / class_name

        if not class_dir.exists():
            continue

        images = list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.png"))

        if not images:
            continue

        print(f"\n{'='*80}")
        print(f"CLASS: {class_name.upper()} ({len(images)} images)")
        print(f"{'='*80}\n")

        correct_original = 0
        correct_safety = 0
        safety_applied = 0

        for img_path in tqdm(images, desc=f"Processing {class_name}"):
            safety_result = predict_with_safety(model, img_path, device, safety_classifier)

            # Get true class ID
            true_class_id = list(CLASS_NAMES.values()).index(class_name)
            true_class_name = class_name

            # Check if original and safety predictions are correct
            original_correct = (safety_result.original_class_id == true_class_id)
            safety_correct = (safety_result.final_class_id == true_class_id)

            result_data = {
                'image': img_path.name,
                'true_class': true_class_name,
                'original_prediction': safety_result.original_class,
                'original_confidence': safety_result.original_confidence,
                'final_prediction': safety_result.final_class,
                'final_confidence': safety_result.final_confidence,
                'probabilities': safety_result.probabilities,
                'safety_applied': safety_result.safety_applied,
                'safety_reason': safety_result.safety_reason,
                'confidence_level': safety_result.confidence_level,
                'original_correct': original_correct,
                'safety_correct': safety_correct
            }

            # Track corrections
            if original_correct:
                correct_original += 1
            if safety_correct:
                correct_safety += 1
            if safety_result.safety_applied:
                safety_applied += 1

            # Categorize results
            if safety_result.safety_applied and not original_correct and safety_correct:
                # Safety fixed a wrong prediction!
                results[class_name]['safety_fixed'].append(result_data)
            elif safety_correct:
                results[class_name]['correct'].append(result_data)
            else:
                results[class_name]['wrong'].append(result_data)

            total_images += 1

        total_correct_original += correct_original
        total_correct_safety += correct_safety
        total_safety_applied += safety_applied

        # Print class summary
        accuracy_original = (correct_original / len(images)) * 100 if images else 0
        accuracy_safety = (correct_safety / len(images)) * 100 if images else 0
        improvement = accuracy_safety - accuracy_original

        print(f"\n📊 Original Accuracy: {correct_original}/{len(images)} ({accuracy_original:.2f}%)")
        print(f"🛡️  Safety Accuracy: {correct_safety}/{len(images)} ({accuracy_safety:.2f}%)")
        print(f"{'🎯 IMPROVEMENT' if improvement > 0 else '⚠️  DEGRADATION' if improvement < 0 else '➡️  NO CHANGE'}: {improvement:+.2f}%")
        print(f"🔧 Safety Applied: {safety_applied} times")

    return results, total_correct_original, total_correct_safety, total_safety_applied, total_images

def print_safety_analysis(results, total_correct_original, total_correct_safety, total_safety_applied, total_images):
    """Print detailed safety analysis"""
    print("\n" + "="*80)
    print("SAFETY CLASSIFIER IMPACT ANALYSIS")
    print("="*80 + "\n")

    accuracy_original = (total_correct_original / total_images) * 100
    accuracy_safety = (total_correct_safety / total_images) * 100
    improvement = accuracy_safety - accuracy_original

    print(f"Total Images: {total_images}")
    print(f"\n📊 ORIGINAL MODEL:")
    print(f"   Correct: {total_correct_original}/{total_images} ({accuracy_original:.2f}%)")
    print(f"\n🛡️  WITH SAFETY MEASURES:")
    print(f"   Correct: {total_correct_safety}/{total_images} ({accuracy_safety:.2f}%)")
    print(f"   Safety Applied: {total_safety_applied} times ({total_safety_applied/total_images*100:.1f}%)")
    print(f"\n{'🎯 OVERALL IMPROVEMENT: +' if improvement > 0 else '⚠️  OVERALL DEGRADATION: ' if improvement < 0 else '➡️  NO CHANGE: '}{abs(improvement):.2f}%")

    # Safety fixes analysis
    print("\n" + "="*80)
    print("SAFETY CORRECTIONS (Fixed Wrong Predictions)")
    print("="*80 + "\n")

    total_fixes = 0
    for class_name in CLASS_NAMES.values():
        fixes = results[class_name]['safety_fixed']
        total_fixes += len(fixes)

        if fixes:
            print(f"\n{class_name.upper()} - {len(fixes)} corrections:")
            print("-" * 80)

            for fix in fixes[:5]:  # Show first 5
                print(f"\n✅ FIXED: {fix['image']}")
                print(f"   True Class: {fix['true_class']}")
                print(f"   Original: {fix['original_prediction']} ({fix['original_confidence']:.1%}) ❌")
                print(f"   Corrected: {fix['final_prediction']} ({fix['final_confidence']:.1%}) ✅")
                print(f"   Reason: {fix['safety_reason']}")

            if len(fixes) > 5:
                print(f"\n   ... and {len(fixes) - 5} more corrections")

    if total_fixes == 0:
        print("No predictions were corrected by safety measures.")

    # Remaining errors
    print("\n" + "="*80)
    print("REMAINING ERRORS (After Safety Measures)")
    print("="*80 + "\n")

    for class_name in CLASS_NAMES.values():
        errors = results[class_name]['wrong']

        if errors:
            print(f"\n{class_name.upper()} - {len(errors)} remaining errors:")
            print("-" * 80)

            # Focus on dangerous errors (impassable misclassified)
            if class_name == 'impassable':
                print("\n⚠️  CRITICAL: These dangerous roads are still misclassified:")

            for error in errors[:5]:  # Show first 5
                print(f"\n❌ ERROR: {error['image']}")
                print(f"   True Class: {error['true_class']}")
                print(f"   Predicted: {error['final_prediction']} ({error['final_confidence']:.1%})")
                print(f"   Confidence: {error['confidence_level']}")
                print(f"   Probabilities:")
                for cls, prob in error['probabilities'].items():
                    bar = '█' * int(prob * 50)
                    print(f"      {cls:20s}: {prob:.1%} {bar}")

            if len(errors) > 5:
                print(f"\n   ... and {len(errors) - 5} more errors")

def main():
    # Configuration
    checkpoint_path = "../checkpoints/epochepoch=45-valf1val/f1=0.7652.ckpt"
    test_dir = "../data/processed/test"

    print("="*80)
    print("UAV FLOOD ASSESSMENT - PREDICTIONS WITH SAFETY MEASURES")
    print("="*80)
    print(f"\nCheckpoint: {checkpoint_path}")
    print(f"Test Directory: {test_dir}")
    print(f"Safety Mode: CONSERVATIVE (production settings)")

    # Load model
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = load_model(checkpoint_path)

    # Create safety classifier
    safety_classifier = SafetyClassifier(safety_mode=SafetyMode.CONSERVATIVE)

    # Scan test images with safety
    results, total_correct_original, total_correct_safety, total_safety_applied, total_images = scan_with_safety(
        model, test_dir, device, safety_classifier
    )

    # Print analysis
    print_safety_analysis(results, total_correct_original, total_correct_safety, total_safety_applied, total_images)

    print("\n" + "="*80)
    print("SCAN COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    main()
