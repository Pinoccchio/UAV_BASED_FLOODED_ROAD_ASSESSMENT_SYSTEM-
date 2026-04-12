"""
EfficientNet-B0 Model for UAV Flood Passability Classification.

Implements PyTorch Lightning module with transfer learning from ImageNet.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
import pytorch_lightning as pl
from torchmetrics import Accuracy, F1Score, ConfusionMatrix, CohenKappa
from typing import Dict, Optional
import numpy as np


class FloodPassabilityClassifier(pl.LightningModule):
    """
    EfficientNet-B0 classifier for 4-class flood passability prediction.

    Classes:
        0 - Passable
        1 - Limited Passability
        2 - Heavy-Vehicle-Only
        3 - Impassable
    """

    def __init__(
        self,
        num_classes: int = 4,
        learning_rate: float = 1e-3,
        weight_decay: float = 1e-4,
        dropout: float = 0.3,
        class_weights: Optional[torch.Tensor] = None,
        freeze_backbone: bool = True,
        use_focal_loss: bool = True,
        focal_gamma: float = 2.0
    ):
        """
        Initialize model.

        Args:
            num_classes: Number of output classes
            learning_rate: Initial learning rate
            weight_decay: L2 regularization weight
            dropout: Dropout probability
            class_weights: Weights for handling class imbalance
            freeze_backbone: Whether to freeze backbone initially
            use_focal_loss: Use focal loss instead of cross-entropy
            focal_gamma: Focal loss gamma parameter
        """
        super().__init__()
        self.save_hyperparameters()

        self.num_classes = num_classes
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.use_focal_loss = use_focal_loss
        self.focal_gamma = focal_gamma

        # Load pre-trained EfficientNet-B0
        self.backbone = efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)

        # Freeze backbone if specified
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False

        # Replace classifier head
        in_features = self.backbone.classifier[1].in_features

        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=dropout, inplace=True),
            nn.Linear(in_features, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout * 0.7),  # Less dropout in second layer
            nn.Linear(512, num_classes)
        )

        # Loss function
        self.class_weights = class_weights
        if class_weights is not None:
            self.register_buffer('weights', class_weights)

        # Metrics
        self.train_acc = Accuracy(task='multiclass', num_classes=num_classes)
        self.val_acc = Accuracy(task='multiclass', num_classes=num_classes)
        self.test_acc = Accuracy(task='multiclass', num_classes=num_classes)

        self.train_f1 = F1Score(task='multiclass', num_classes=num_classes, average='macro')
        self.val_f1 = F1Score(task='multiclass', num_classes=num_classes, average='macro')
        self.test_f1 = F1Score(task='multiclass', num_classes=num_classes, average='macro')

        self.val_kappa = CohenKappa(task='multiclass', num_classes=num_classes)
        self.test_kappa = CohenKappa(task='multiclass', num_classes=num_classes)

        self.val_confusion = ConfusionMatrix(task='multiclass', num_classes=num_classes)
        self.test_confusion = ConfusionMatrix(task='multiclass', num_classes=num_classes)

        # Class names for logging (updated based on num_classes)
        if num_classes == 3:
            self.class_names = ['passable', 'limited_passability', 'impassable']
        else:  # 4 classes
            self.class_names = ['passable', 'limited', 'heavy_vehicle', 'impassable']

    def forward(self, x):
        """Forward pass."""
        return self.backbone(x)

    def focal_loss(self, logits, targets, gamma=2.0, alpha=None):
        """
        Focal loss for handling class imbalance.

        FL(p_t) = -α_t * (1 - p_t)^γ * log(p_t)

        Args:
            logits: Model predictions (B, C)
            targets: Ground truth labels (B,)
            gamma: Focusing parameter
            alpha: Class weights (C,)

        Returns:
            Scalar loss value
        """
        # Move alpha to same device as logits if provided
        if alpha is not None:
            alpha = alpha.to(logits.device)

        ce_loss = F.cross_entropy(logits, targets, reduction='none', weight=alpha)
        p_t = torch.exp(-ce_loss)
        focal_loss = ((1 - p_t) ** gamma) * ce_loss

        return focal_loss.mean()

    def compute_loss(self, logits, targets):
        """Compute loss (focal or cross-entropy)."""
        if self.use_focal_loss:
            return self.focal_loss(
                logits,
                targets,
                gamma=self.focal_gamma,
                alpha=self.class_weights
            )
        else:
            # Move class_weights to same device if provided
            weight = self.class_weights.to(logits.device) if self.class_weights is not None else None
            return F.cross_entropy(logits, targets, weight=weight)

    def training_step(self, batch, batch_idx):
        """Training step."""
        images, targets = batch
        logits = self(images)

        loss = self.compute_loss(logits, targets)
        preds = torch.argmax(logits, dim=1)

        # Update metrics
        self.train_acc(preds, targets)
        self.train_f1(preds, targets)

        # Log metrics
        self.log('train/loss', loss, on_step=True, on_epoch=True, prog_bar=True)
        self.log('train/acc', self.train_acc, on_step=False, on_epoch=True, prog_bar=True)
        self.log('train/f1', self.train_f1, on_step=False, on_epoch=True)

        return loss

    def validation_step(self, batch, batch_idx):
        """Validation step."""
        images, targets = batch
        logits = self(images)

        loss = self.compute_loss(logits, targets)
        preds = torch.argmax(logits, dim=1)

        # Update metrics
        self.val_acc(preds, targets)
        self.val_f1(preds, targets)
        self.val_kappa(preds, targets)
        self.val_confusion(preds, targets)

        # Log metrics
        self.log('val/loss', loss, on_step=False, on_epoch=True, prog_bar=True)
        self.log('val/acc', self.val_acc, on_step=False, on_epoch=True, prog_bar=True)
        self.log('val/f1', self.val_f1, on_step=False, on_epoch=True, prog_bar=True)
        self.log('val/kappa', self.val_kappa, on_step=False, on_epoch=True)

        return loss

    def test_step(self, batch, batch_idx):
        """Test step."""
        images, targets = batch
        logits = self(images)

        loss = self.compute_loss(logits, targets)
        preds = torch.argmax(logits, dim=1)

        # Update metrics
        self.test_acc(preds, targets)
        self.test_f1(preds, targets)
        self.test_kappa(preds, targets)
        self.test_confusion(preds, targets)

        # Log metrics
        self.log('test/loss', loss, on_step=False, on_epoch=True)
        self.log('test/acc', self.test_acc, on_step=False, on_epoch=True)
        self.log('test/f1', self.test_f1, on_step=False, on_epoch=True)
        self.log('test/kappa', self.test_kappa, on_step=False, on_epoch=True)

        return loss

    def predict_step(self, batch, batch_idx):
        """Prediction step for inference."""
        images, _ = batch
        logits = self(images)
        probs = F.softmax(logits, dim=1)

        return {
            'logits': logits,
            'probabilities': probs,
            'predictions': torch.argmax(logits, dim=1)
        }

    def configure_optimizers(self):
        """Configure optimizer and learning rate scheduler."""
        # AdamW optimizer
        optimizer = torch.optim.AdamW(
            self.parameters(),
            lr=self.learning_rate,
            weight_decay=self.weight_decay
        )

        # Cosine annealing scheduler
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=self.trainer.max_epochs,
            eta_min=1e-6
        )

        return {
            'optimizer': optimizer,
            'lr_scheduler': {
                'scheduler': scheduler,
                'interval': 'epoch',
                'frequency': 1
            }
        }

    def unfreeze_backbone(self):
        """Unfreeze backbone layers for fine-tuning."""
        for param in self.backbone.parameters():
            param.requires_grad = True
        print("✓ Backbone unfrozen")

    def unfreeze_last_n_blocks(self, n: int = 2):
        """
        Unfreeze last N blocks of EfficientNet for gradual fine-tuning.

        Args:
            n: Number of blocks to unfreeze (from the end)
        """
        # EfficientNet-B0 has 8 blocks (features[0] through features[7])
        total_blocks = len(self.backbone.features)

        # Freeze all first
        for param in self.backbone.parameters():
            param.requires_grad = False

        # Unfreeze last N blocks
        for i in range(total_blocks - n, total_blocks):
            for param in self.backbone.features[i].parameters():
                param.requires_grad = True

        # Always keep classifier unfrozen
        for param in self.backbone.classifier.parameters():
            param.requires_grad = True

        print(f"✓ Unfroze last {n} blocks of backbone")

    def on_validation_epoch_end(self):
        """Called at the end of validation epoch."""
        # Log confusion matrix
        confusion = self.val_confusion.compute()
        self.val_confusion.reset()

        # Log per-class metrics
        if confusion is not None:
            for i, class_name in enumerate(self.class_names):
                # Precision: TP / (TP + FP)
                tp = confusion[i, i]
                fp = confusion[:, i].sum() - tp
                precision = tp / (tp + fp + 1e-8)

                # Recall: TP / (TP + FN)
                fn = confusion[i, :].sum() - tp
                recall = tp / (tp + fn + 1e-8)

                self.log(f'val/{class_name}_precision', precision)
                self.log(f'val/{class_name}_recall', recall)

    def on_test_epoch_end(self):
        """Called at the end of test epoch."""
        # Log confusion matrix
        confusion = self.test_confusion.compute()
        self.test_confusion.reset()

        # Log per-class metrics
        if confusion is not None:
            for i, class_name in enumerate(self.class_names):
                tp = confusion[i, i]
                fp = confusion[:, i].sum() - tp
                precision = tp / (tp + fp + 1e-8)

                fn = confusion[i, :].sum() - tp
                recall = tp / (tp + fn + 1e-8)

                self.log(f'test/{class_name}_precision', precision)
                self.log(f'test/{class_name}_recall', recall)


if __name__ == "__main__":
    # Test model initialization
    model = FloodPassabilityClassifier(
        num_classes=4,
        learning_rate=1e-3,
        dropout=0.3,
        freeze_backbone=True
    )

    # Test forward pass
    dummy_input = torch.randn(2, 3, 448, 448)
    output = model(dummy_input)

    print(f"Model initialized successfully")
    print(f"Input shape: {dummy_input.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Total parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"Trainable parameters: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")
