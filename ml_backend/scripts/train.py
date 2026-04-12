"""
Main Training Script for UAV Flood Passability Classifier.

Implements 3-phase transfer learning:
    Phase 1: Train classifier head only (frozen backbone)
    Phase 2: Fine-tune last 2 blocks
    Phase 3: Full end-to-end fine-tuning
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent / "preprocessing"))

import torch
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping, LearningRateMonitor
from pytorch_lightning.loggers import TensorBoardLogger, WandbLogger
import yaml
from argparse import ArgumentParser
import warnings
warnings.filterwarnings('ignore')

from models.efficientnet import FloodPassabilityClassifier
from data.dataset import FloodDataModule


def load_config(config_path: Path) -> dict:
    """Load YAML configuration file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def create_callbacks(config: dict, checkpoint_dir: Path) -> list:
    """Create PyTorch Lightning callbacks."""
    callbacks = []

    # Model checkpoint
    checkpoint_config = config['callbacks']['checkpoint']
    checkpoint_callback = ModelCheckpoint(
        dirpath=checkpoint_dir,
        monitor=checkpoint_config['monitor'],
        mode=checkpoint_config['mode'],
        save_top_k=checkpoint_config['save_top_k'],
        save_last=checkpoint_config['save_last'],
        filename=checkpoint_config['filename'],
        verbose=True
    )
    callbacks.append(checkpoint_callback)

    # Early stopping
    early_stop_config = config['callbacks']['early_stopping']
    early_stop_callback = EarlyStopping(
        monitor=early_stop_config['monitor'],
        patience=early_stop_config['patience'],
        mode=early_stop_config['mode'],
        min_delta=early_stop_config['min_delta'],
        verbose=True
    )
    callbacks.append(early_stop_callback)

    # Learning rate monitor
    lr_monitor = LearningRateMonitor(
        logging_interval=config['callbacks']['lr_monitor']['logging_interval']
    )
    callbacks.append(lr_monitor)

    return callbacks


def create_logger(config: dict, log_dir: Path):
    """Create PyTorch Lightning logger."""
    logger_type = config['logging']['logger']

    if logger_type == 'wandb':
        logger = WandbLogger(
            project=config['logging']['project_name'],
            name=config['logging']['experiment_name'],
            save_dir=log_dir
        )
    else:  # tensorboard
        logger = TensorBoardLogger(
            save_dir=log_dir,
            name=config['logging']['experiment_name']
        )

    return logger


def train_phase_1(
    model: FloodPassabilityClassifier,
    datamodule: FloodDataModule,
    config: dict,
    callbacks: list,
    logger,
    checkpoint_dir: Path
):
    """
    Phase 1: Train classifier head only with frozen backbone.

    Target: 70-75% accuracy
    """
    print("\n" + "="*60)
    print("PHASE 1: Training Classifier Head (Frozen Backbone)")
    print("="*60)

    # Ensure backbone is frozen
    model.freeze_backbone = True
    for param in model.backbone.features.parameters():
        param.requires_grad = False

    # Update learning rate for Phase 1
    model.learning_rate = config['training']['phase1_lr']

    # Create trainer
    trainer = pl.Trainer(
        max_epochs=config['training']['phase1_epochs'],
        callbacks=callbacks,
        logger=logger,
        accelerator=config['trainer']['accelerator'],
        devices=config['trainer']['devices'],
        precision=config['trainer']['precision'],
        gradient_clip_val=config['training']['gradient_clip_val'],
        log_every_n_steps=config['logging']['log_every_n_steps'],
        deterministic=config['trainer']['deterministic']
    )

    # Train
    trainer.fit(model, datamodule)

    print(f"\n✓ Phase 1 complete!")
    print(f"Best val/f1: {trainer.callback_metrics.get('val/f1', 0.0):.4f}")

    return model


def train_phase_2(
    model: FloodPassabilityClassifier,
    datamodule: FloodDataModule,
    config: dict,
    callbacks: list,
    logger,
    checkpoint_dir: Path
):
    """
    Phase 2: Fine-tune last N blocks of backbone.

    Target: 80-85% accuracy
    """
    print("\n" + "="*60)
    print(f"PHASE 2: Fine-tuning Last {config['training']['phase2_unfreeze_blocks']} Blocks")
    print("="*60)

    # Unfreeze last N blocks
    model.unfreeze_last_n_blocks(config['training']['phase2_unfreeze_blocks'])

    # Update learning rate for Phase 2
    model.learning_rate = config['training']['phase2_lr']

    # Create trainer
    trainer = pl.Trainer(
        max_epochs=config['training']['phase1_epochs'] + config['training']['phase2_epochs'],
        callbacks=callbacks,
        logger=logger,
        accelerator=config['trainer']['accelerator'],
        devices=config['trainer']['devices'],
        precision=config['trainer']['precision'],
        gradient_clip_val=config['training']['gradient_clip_val'],
        log_every_n_steps=config['logging']['log_every_n_steps'],
        deterministic=config['trainer']['deterministic']
    )

    # Continue training
    trainer.fit(model, datamodule, ckpt_path='last')

    print(f"\n✓ Phase 2 complete!")
    print(f"Best val/f1: {trainer.callback_metrics.get('val/f1', 0.0):.4f}")

    return model


def train_phase_3(
    model: FloodPassabilityClassifier,
    datamodule: FloodDataModule,
    config: dict,
    callbacks: list,
    logger,
    checkpoint_dir: Path
):
    """
    Phase 3: Full end-to-end fine-tuning.

    Target: 85%+ accuracy
    """
    print("\n" + "="*60)
    print("PHASE 3: Full End-to-End Fine-Tuning")
    print("="*60)

    # Unfreeze entire backbone
    model.unfreeze_backbone()

    # Update learning rate for Phase 3
    model.learning_rate = config['training']['phase3_lr']

    # Create trainer
    trainer = pl.Trainer(
        max_epochs=config['training']['max_epochs'],
        callbacks=callbacks,
        logger=logger,
        accelerator=config['trainer']['accelerator'],
        devices=config['trainer']['devices'],
        precision=config['trainer']['precision'],
        gradient_clip_val=config['training']['gradient_clip_val'],
        log_every_n_steps=config['logging']['log_every_n_steps'],
        deterministic=config['trainer']['deterministic']
    )

    # Continue training
    trainer.fit(model, datamodule, ckpt_path='last')

    print(f"\n✓ Phase 3 complete!")
    print(f"Best val/f1: {trainer.callback_metrics.get('val/f1', 0.0):.4f}")

    return model, trainer


def main(args):
    """Main training function."""
    # Load configuration
    config_path = Path(args.config)
    config = load_config(config_path)

    print("="*60)
    print("UAV Flood Passability Classifier - Training Pipeline")
    print("="*60)
    print(f"Config: {config_path.name}")
    print(f"Model: {config['model']['name']}")
    print(f"Batch size: {config['data']['batch_size']}")
    print(f"Image size: {config['data']['img_size']}")

    # Set random seed
    pl.seed_everything(config['seed'], workers=True)

    # Create directories
    checkpoint_dir = Path(config['paths']['checkpoint_dir'])
    log_dir = Path(config['paths']['log_dir'])
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Initialize DataModule
    data_dir = Path(config['data']['data_dir'])
    if not data_dir.is_absolute():
        # Make relative to config file location
        data_dir = config_path.parent / data_dir

    datamodule = FloodDataModule(
        data_dir=data_dir,
        batch_size=config['data']['batch_size'],
        num_workers=config['data']['num_workers'],
        img_size=tuple(config['data']['img_size']),
        use_weighted_sampling=config['data']['use_weighted_sampling'],
        pin_memory=config['data']['pin_memory']
    )

    # Setup datasets
    datamodule.setup('fit')

    # Compute class weights
    class_weights = None
    if config['loss']['use_class_weights']:
        # Check if manual class weights are provided in config
        if 'class_weights' in config['loss'] and config['loss']['class_weights'] is not None:
            class_weights = torch.tensor(config['loss']['class_weights'], dtype=torch.float32)
            print(f"\nUsing manual class weights from config: {class_weights}")
        else:
            class_weights = datamodule.get_class_weights()
            print(f"\nUsing computed class weights: {class_weights}")

    # Initialize model
    model = FloodPassabilityClassifier(
        num_classes=config['model']['num_classes'],
        learning_rate=config['training']['phase1_lr'],
        weight_decay=config['training']['weight_decay'],
        dropout=config['model']['dropout'],
        class_weights=class_weights,
        freeze_backbone=config['model']['freeze_backbone'],
        use_focal_loss=(config['loss']['type'] == 'focal_loss'),
        focal_gamma=config['loss']['focal_gamma']
    )

    # Create callbacks
    callbacks = create_callbacks(config, checkpoint_dir)

    # Create logger
    logger = create_logger(config, log_dir)

    # Execute 3-phase training
    if not args.skip_phase1:
        model = train_phase_1(model, datamodule, config, callbacks, logger, checkpoint_dir)

    if not args.skip_phase2:
        model = train_phase_2(model, datamodule, config, callbacks, logger, checkpoint_dir)

    if not args.skip_phase3:
        model, trainer = train_phase_3(model, datamodule, config, callbacks, logger, checkpoint_dir)

        # Evaluate on test set
        print("\n" + "="*60)
        print("FINAL EVALUATION ON TEST SET")
        print("="*60)

        datamodule.setup('test')
        test_results = trainer.test(model, datamodule)

        print("\n=== Test Results ===")
        for key, value in test_results[0].items():
            print(f"{key:30s}: {value:.4f}")

    print("\n" + "="*60)
    print("TRAINING COMPLETE!")
    print("="*60)
    print(f"Checkpoints saved to: {checkpoint_dir}")
    print(f"Logs saved to: {log_dir}")


if __name__ == "__main__":
    parser = ArgumentParser(description="Train UAV Flood Passability Classifier")

    parser.add_argument(
        '--config',
        type=str,
        default='../configs/efficientnet_b0.yaml',
        help='Path to configuration file'
    )

    parser.add_argument(
        '--skip-phase1',
        action='store_true',
        help='Skip Phase 1 (classifier head training)'
    )

    parser.add_argument(
        '--skip-phase2',
        action='store_true',
        help='Skip Phase 2 (partial fine-tuning)'
    )

    parser.add_argument(
        '--skip-phase3',
        action='store_true',
        help='Skip Phase 3 (full fine-tuning)'
    )

    args = parser.parse_args()
    main(args)
