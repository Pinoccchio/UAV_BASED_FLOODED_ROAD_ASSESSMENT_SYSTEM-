"""
Evaluation Metrics and Visualization for UAV Flood Assessment.

Computes comprehensive metrics and generates visualizations.
"""

import torch
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    cohen_kappa_score,
    roc_auc_score,
    roc_curve
)
from pathlib import Path
from typing import List, Dict, Tuple
import pandas as pd
import json


class MetricsComputer:
    """Compute and visualize evaluation metrics."""

    def __init__(self, num_classes: int = 4):
        """
        Initialize metrics computer.

        Args:
            num_classes: Number of classes
        """
        self.num_classes = num_classes
        self.class_names = ['Passable', 'Limited', 'Heavy-Vehicle', 'Impassable']

    def compute_all_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_probs: np.ndarray
    ) -> Dict:
        """
        Compute all evaluation metrics.

        Args:
            y_true: Ground truth labels (N,)
            y_pred: Predicted labels (N,)
            y_probs: Predicted probabilities (N, num_classes)

        Returns:
            Dictionary of metrics
        """
        metrics = {}

        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        metrics['confusion_matrix'] = cm

        # Overall accuracy
        accuracy = np.trace(cm) / np.sum(cm)
        metrics['accuracy'] = accuracy

        # Per-class metrics
        per_class = self._compute_per_class_metrics(cm)
        metrics['per_class'] = per_class

        # Macro averages
        metrics['macro_precision'] = np.mean([m['precision'] for m in per_class.values()])
        metrics['macro_recall'] = np.mean([m['recall'] for m in per_class.values()])
        metrics['macro_f1'] = np.mean([m['f1'] for m in per_class.values()])

        # Cohen's Kappa
        metrics['cohen_kappa'] = cohen_kappa_score(y_true, y_pred)

        # Classification report
        report = classification_report(
            y_true,
            y_pred,
            target_names=self.class_names,
            output_dict=True
        )
        metrics['classification_report'] = report

        return metrics

    def _compute_per_class_metrics(self, cm: np.ndarray) -> Dict:
        """
        Compute per-class precision, recall, F1.

        Args:
            cm: Confusion matrix

        Returns:
            Dictionary of per-class metrics
        """
        per_class = {}

        for i, class_name in enumerate(self.class_names):
            tp = cm[i, i]
            fp = cm[:, i].sum() - tp
            fn = cm[i, :].sum() - tp
            tn = cm.sum() - tp - fp - fn

            precision = tp / (tp + fp + 1e-8)
            recall = tp / (tp + fn + 1e-8)
            f1 = 2 * precision * recall / (precision + recall + 1e-8)

            per_class[class_name] = {
                'precision': float(precision),
                'recall': float(recall),
                'f1': float(f1),
                'support': int(cm[i, :].sum())
            }

        return per_class

    def plot_confusion_matrix(
        self,
        cm: np.ndarray,
        output_path: Path,
        normalize: bool = False
    ):
        """
        Plot confusion matrix heatmap.

        Args:
            cm: Confusion matrix
            output_path: Output file path
            normalize: Whether to normalize by row (true labels)
        """
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

        plt.figure(figsize=(10, 8))

        sns.heatmap(
            cm,
            annot=True,
            fmt='.2f' if normalize else 'd',
            cmap='Blues',
            xticklabels=self.class_names,
            yticklabels=self.class_names,
            cbar_kws={'label': 'Count'}
        )

        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.title('Confusion Matrix' + (' (Normalized)' if normalize else ''))
        plt.tight_layout()

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved confusion matrix to: {output_path}")

    def plot_per_class_metrics(
        self,
        per_class: Dict,
        output_path: Path
    ):
        """
        Plot per-class precision, recall, F1 bar chart.

        Args:
            per_class: Per-class metrics dictionary
            output_path: Output file path
        """
        classes = list(per_class.keys())
        precision = [per_class[c]['precision'] for c in classes]
        recall = [per_class[c]['recall'] for c in classes]
        f1 = [per_class[c]['f1'] for c in classes]

        x = np.arange(len(classes))
        width = 0.25

        fig, ax = plt.subplots(figsize=(12, 6))

        ax.bar(x - width, precision, width, label='Precision', alpha=0.8)
        ax.bar(x, recall, width, label='Recall', alpha=0.8)
        ax.bar(x + width, f1, width, label='F1-Score', alpha=0.8)

        ax.set_xlabel('Class')
        ax.set_ylabel('Score')
        ax.set_title('Per-Class Metrics')
        ax.set_xticks(x)
        ax.set_xticklabels(classes, rotation=15, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim([0, 1.0])

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved per-class metrics to: {output_path}")

    def plot_training_curves(
        self,
        train_metrics: Dict,
        val_metrics: Dict,
        output_path: Path
    ):
        """
        Plot training and validation curves.

        Args:
            train_metrics: Dictionary of training metrics over epochs
            val_metrics: Dictionary of validation metrics over epochs
            output_path: Output file path
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # Loss
        axes[0, 0].plot(train_metrics['loss'], label='Train Loss', alpha=0.8)
        axes[0, 0].plot(val_metrics['loss'], label='Val Loss', alpha=0.8)
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].set_title('Training and Validation Loss')
        axes[0, 0].legend()
        axes[0, 0].grid(alpha=0.3)

        # Accuracy
        axes[0, 1].plot(train_metrics['accuracy'], label='Train Acc', alpha=0.8)
        axes[0, 1].plot(val_metrics['accuracy'], label='Val Acc', alpha=0.8)
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Accuracy')
        axes[0, 1].set_title('Training and Validation Accuracy')
        axes[0, 1].legend()
        axes[0, 1].grid(alpha=0.3)

        # F1 Score
        axes[1, 0].plot(train_metrics['f1'], label='Train F1', alpha=0.8)
        axes[1, 0].plot(val_metrics['f1'], label='Val F1', alpha=0.8)
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('F1 Score (Macro)')
        axes[1, 0].set_title('Training and Validation F1 Score')
        axes[1, 0].legend()
        axes[1, 0].grid(alpha=0.3)

        # Learning Rate
        if 'lr' in train_metrics:
            axes[1, 1].plot(train_metrics['lr'], alpha=0.8, color='green')
            axes[1, 1].set_xlabel('Epoch')
            axes[1, 1].set_ylabel('Learning Rate')
            axes[1, 1].set_title('Learning Rate Schedule')
            axes[1, 1].set_yscale('log')
            axes[1, 1].grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved training curves to: {output_path}")

    def save_metrics_report(
        self,
        metrics: Dict,
        output_path: Path
    ):
        """
        Save metrics to JSON and text report.

        Args:
            metrics: Metrics dictionary
            output_path: Output file path (JSON)
        """
        # Save JSON
        # Convert numpy arrays to lists for JSON serialization
        metrics_json = {}
        for key, value in metrics.items():
            if isinstance(value, np.ndarray):
                metrics_json[key] = value.tolist()
            else:
                metrics_json[key] = value

        with open(output_path, 'w') as f:
            json.dump(metrics_json, f, indent=2)

        print(f"✓ Saved metrics JSON to: {output_path}")

        # Save text report
        txt_path = output_path.with_suffix('.txt')
        with open(txt_path, 'w') as f:
            f.write("="*60 + "\n")
            f.write("UAV Flood Assessment Model - Evaluation Report\n")
            f.write("="*60 + "\n\n")

            f.write("=== Overall Metrics ===\n")
            f.write(f"Accuracy:        {metrics['accuracy']:.4f}\n")
            f.write(f"Macro Precision: {metrics['macro_precision']:.4f}\n")
            f.write(f"Macro Recall:    {metrics['macro_recall']:.4f}\n")
            f.write(f"Macro F1:        {metrics['macro_f1']:.4f}\n")
            f.write(f"Cohen's Kappa:   {metrics['cohen_kappa']:.4f}\n\n")

            f.write("=== Per-Class Metrics ===\n")
            for class_name, class_metrics in metrics['per_class'].items():
                f.write(f"\n{class_name}:\n")
                f.write(f"  Precision: {class_metrics['precision']:.4f}\n")
                f.write(f"  Recall:    {class_metrics['recall']:.4f}\n")
                f.write(f"  F1:        {class_metrics['f1']:.4f}\n")
                f.write(f"  Support:   {class_metrics['support']}\n")

        print(f"✓ Saved metrics report to: {txt_path}")


if __name__ == "__main__":
    # Test metrics computation
    print("Testing MetricsComputer...")

    # Generate dummy predictions
    np.random.seed(42)
    n_samples = 500
    num_classes = 4

    y_true = np.random.randint(0, num_classes, n_samples)
    y_pred = np.random.randint(0, num_classes, n_samples)
    y_probs = np.random.rand(n_samples, num_classes)
    y_probs = y_probs / y_probs.sum(axis=1, keepdims=True)

    # Compute metrics
    computer = MetricsComputer(num_classes=num_classes)
    metrics = computer.compute_all_metrics(y_true, y_pred, y_probs)

    print("\n=== Test Results ===")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Macro F1: {metrics['macro_f1']:.4f}")
    print(f"Cohen's Kappa: {metrics['cohen_kappa']:.4f}")

    # Save visualizations
    output_dir = Path("test_outputs")
    output_dir.mkdir(exist_ok=True)

    computer.plot_confusion_matrix(
        metrics['confusion_matrix'],
        output_dir / "confusion_matrix.png"
    )

    computer.plot_per_class_metrics(
        metrics['per_class'],
        output_dir / "per_class_metrics.png"
    )

    computer.save_metrics_report(
        metrics,
        output_dir / "metrics_report.json"
    )

    print("\n✓ Test complete!")
