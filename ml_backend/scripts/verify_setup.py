"""
Verification Script for ML Backend Setup.

Checks that all components are properly installed and configured.
"""

import sys
import os
from pathlib import Path
import importlib.util

# Fix encoding for Windows console
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent / "preprocessing"))


def check_python_version():
    """Check Python version."""
    print("Checking Python version...")
    version = sys.version_info

    if version.major == 3 and version.minor >= 8:
        print(f"  [OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  [FAIL] Python {version.major}.{version.minor} (requires 3.8+)")
        return False


def check_dependencies():
    """Check if required packages are installed."""
    print("\nChecking dependencies...")

    required_packages = [
        ('torch', 'PyTorch'),
        ('torchvision', 'TorchVision'),
        ('pytorch_lightning', 'PyTorch Lightning'),
        ('albumentations', 'Albumentations'),
        ('onnx', 'ONNX'),
        ('onnxruntime', 'ONNX Runtime'),
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('PIL', 'Pillow'),
        ('cv2', 'OpenCV'),
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
        ('sklearn', 'scikit-learn'),
        ('matplotlib', 'Matplotlib'),
        ('seaborn', 'Seaborn'),
        ('yaml', 'PyYAML'),
    ]

    all_installed = True

    for module_name, display_name in required_packages:
        try:
            __import__(module_name)
            print(f"  [OK] {display_name}")
        except ImportError:
            print(f"  [FAIL] {display_name} (not installed)")
            all_installed = False

    return all_installed


def check_gpu():
    """Check if GPU is available."""
    print("\nChecking GPU availability...")

    try:
        import torch

        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            print(f"  [OK] GPU available: {gpu_name}")
            print(f"  [OK] GPU count: {gpu_count}")
            print(f"  [OK] CUDA version: {torch.version.cuda}")
            return True
        else:
            print("  [WARN] No GPU detected (training will use CPU - much slower)")
            return False
    except Exception as e:
        print(f"  [FAIL] Error checking GPU: {str(e)}")
        return False


def check_datasets():
    """Check if datasets exist."""
    print("\nChecking datasets...")

    dataset_root = Path(__file__).parent.parent.parent / "datasets"

    datasets = {
        'RescueNet': dataset_root / "RescueNet",
        'FloodNet': dataset_root / "FloodNet"
    }

    all_exist = True

    for name, path in datasets.items():
        if path.exists():
            print(f"  [OK] {name} found at: {path}")

            # Check for key files
            if name == 'RescueNet':
                # Check new path
                csv_file = path / "classification" / "RescueNet-classification-train.csv"
                if not csv_file.exists():
                    # Fallback to old path
                    csv_file = path / "rescuenet-train.csv"

                if csv_file.exists():
                    print(f"    [OK] Training CSV found: {csv_file.name}")
                else:
                    print(f"    [FAIL] Training CSV not found")
                    all_exist = False

            elif name == 'FloodNet':
                csv_file = path / "train-label-img" / "FloodNet_Binary_Classification_Labels.csv"
                if csv_file.exists():
                    print(f"    [OK] Labels CSV found")
                else:
                    print(f"    [FAIL] Labels CSV not found")
                    all_exist = False
        else:
            print(f"  [FAIL] {name} not found (expected at: {path})")
            all_exist = False

    return all_exist


def check_project_structure():
    """Check if all required files exist."""
    print("\nChecking project structure...")

    project_root = Path(__file__).parent.parent

    required_files = [
        'preprocessing/label_mapper.py',
        'preprocessing/segmentation_analyzer.py',
        'preprocessing/augmentation.py',
        'preprocessing/dataset_splitter.py',
        'src/models/efficientnet.py',
        'src/data/dataset.py',
        'src/evaluation/metrics.py',
        'scripts/train.py',
        'scripts/export_model.py',
        'api/main.py',
        'api/services/inference_service.py',
        'configs/efficientnet_b0.yaml',
        'requirements.txt',
        'README.md',
    ]

    all_exist = True

    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  [OK] {file_path}")
        else:
            print(f"  [FAIL] {file_path} (missing)")
            all_exist = False

    return all_exist


def check_imports():
    """Test importing key modules."""
    print("\nTesting module imports...")

    modules_to_test = [
        ('models.efficientnet', 'FloodPassabilityClassifier'),
        ('data.dataset', 'FloodDataModule'),
        ('preprocessing.segmentation_analyzer', 'SegmentationAnalyzer'),
        ('preprocessing.label_mapper', 'LabelMapper'),
        ('preprocessing.augmentation', 'AugmentationPipeline'),
        ('api.services.inference_service', 'InferenceService'),
    ]

    all_imported = True

    for module_path, class_name in modules_to_test:
        try:
            # Import module
            if '.' in module_path:
                parts = module_path.split('.')
                module = __import__(module_path, fromlist=[parts[-1]])
            else:
                module = __import__(module_path)

            # Check if class exists
            if hasattr(module, class_name):
                print(f"  [OK] {module_path}.{class_name}")
            else:
                print(f"  [FAIL] {module_path}.{class_name} (class not found)")
                all_imported = False

        except ImportError as e:
            print(f"  [FAIL] {module_path} (import error: {str(e)})")
            all_imported = False
        except Exception as e:
            print(f"  [FAIL] {module_path} (error: {str(e)})")
            all_imported = False

    return all_imported


def check_disk_space():
    """Check available disk space."""
    print("\nChecking disk space...")

    import shutil

    project_root = Path(__file__).parent.parent
    total, used, free = shutil.disk_usage(project_root)

    free_gb = free / (1024**3)

    print(f"  Free space: {free_gb:.2f} GB")

    if free_gb >= 50:
        print(f"  [OK] Sufficient disk space (50+ GB recommended)")
        return True
    else:
        print(f"  [WARN] Low disk space (50+ GB recommended for training)")
        return False


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)

    print("\n1. Process Datasets (10-15 minutes):")
    print("   cd preprocessing")
    print("   python label_mapper.py")
    print("   python dataset_splitter.py")

    print("\n2. Train Model (6-8 hours):")
    print("   cd scripts")
    print("   python train.py --config ../configs/efficientnet_b0.yaml")

    print("\n3. Export Model (2 minutes):")
    print("   python export_model.py --checkpoint ../checkpoints/best_model.ckpt")

    print("\n4. Start API Server:")
    print("   cd api")
    print("   python main.py")

    print("\nFor detailed instructions, see:")
    print("  - README.md (complete documentation)")
    print("  - QUICKSTART.md (step-by-step guide)")


def main():
    """Run all verification checks."""
    print("="*60)
    print("ML Backend Setup Verification")
    print("="*60)

    results = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'GPU': check_gpu(),
        'Datasets': check_datasets(),
        'Project Structure': check_project_structure(),
        'Module Imports': check_imports(),
        'Disk Space': check_disk_space(),
    }

    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)

    for check, passed in results.items():
        status = "[OK] PASS" if passed else "[FAIL] FAIL"
        print(f"{check:20s}: {status}")

    # Overall status
    all_passed = all(results.values())
    critical_passed = results['Python Version'] and results['Dependencies'] and results['Project Structure']

    print("\n" + "="*60)

    if all_passed:
        print("[OK] ALL CHECKS PASSED!")
        print("Your setup is complete and ready for training.")
        print_next_steps()
    elif critical_passed:
        print("[WARN] SETUP READY (with warnings)")
        print("\nCritical components are installed, but some checks failed.")
        print("You can proceed with training, but review the warnings above.")
        print_next_steps()
    else:
        print("[FAIL] SETUP INCOMPLETE")
        print("\nSome critical components are missing.")
        print("Please install missing dependencies:")
        print("  pip install -r requirements.txt")

    print("="*60)


if __name__ == "__main__":
    main()
