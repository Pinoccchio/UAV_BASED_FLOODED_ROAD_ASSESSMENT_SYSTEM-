# Validation Procedure

This document explains the validation procedure used for the UAV-Based Flooded Road Assessment System.

## Overview

When we say "validation," we refer mainly to **model validation**:

- how the dataset was prepared
- how the model was trained
- how performance was measured
- how the final deployed model was selected

For this project, the deployed model is a **3-class flood road passability classifier**:

1. Passable
2. Limited Passability
3. Impassable

## 1. Dataset Preparation

The model was developed using combined flood-disaster image datasets:

- **RescueNet**
- **FloodNet**

These datasets were first processed and mapped into the project’s 3 road-passability classes.

### Class Mapping

The original dataset labels were converted into:

- **Passable** - road is safe for normal vehicle passage
- **Limited Passability** - road is passable only with caution or for higher-clearance vehicles
- **Impassable** - road is unsafe or blocked for normal vehicle passage

This step ensured that the training data matched the actual decision classes used in the deployed system.

## 2. Data Splitting Procedure

After preprocessing, the dataset was divided into three parts:

- **Training set** - used to train the model
- **Validation set** - used to monitor learning and tune the model during training
- **Test set** - used only for final evaluation

For the final production run:

- **Total dataset:** 4,892 images
- **Train:** 3,993 images
- **Validation:** 449 images
- **Test:** 450 images

The split was done so the model could be trained, checked during training, and then evaluated on unseen data.

## 3. Training Procedure

The model used was **EfficientNet-B0** with transfer learning.

Training was done in **3 phases**:

### Phase 1: Classifier Head Training

- Only the classifier head was trained first
- The backbone stayed frozen
- Goal: let the model adapt to the new flood-road classification task

### Phase 2: Partial Fine-Tuning

- The last backbone blocks were unfrozen
- The model learned more task-specific visual features

### Phase 3: Full Fine-Tuning

- The full backbone was unfrozen
- Final optimization was performed across the entire model

This phased approach helped improve stability and performance during training.

## 4. Validation During Training

During training, performance was checked regularly using the **validation set**.

The main metrics monitored were:

- **Accuracy**
- **Macro F1-score**
- **Per-class precision**
- **Per-class recall**
- **Cohen’s Kappa**
- **Confusion Matrix**

The main model-selection metric was **validation F1-score** (`val/f1`).

This is important because the task is class-imbalanced, and F1-score gives a more balanced view of performance than accuracy alone.

## 5. Final Test Evaluation

After training, the best-performing model was evaluated on the **held-out test set**.

### Final Deployed Model Results

- **Model:** EfficientNet-B0
- **Classes:** 3
- **Test Accuracy:** **78.44%**
- **Macro F1-score:** **74.04%**
- **Cohen’s Kappa:** **0.6134**
- **Impassable Recall:** **81.29%**

These results were used as the basis for selecting the final deployed model.

## 6. Safety Validation

Aside from raw model prediction, the system also applies a **conservative safety classification layer**.

This was added because in disaster-response scenarios, it is better to be cautious than to underestimate danger.

### Safety Logic

If the model is uncertain:

- a risky prediction can be downgraded to a safer class
- uncertain "passable" results may be treated as "limited" or "impassable"

This reduces the chance of recommending a dangerous road as safe.

## 7. Why This Validation Procedure Was Used

This validation procedure was chosen to make the system more reliable:

- the dataset was aligned to the actual deployment classes
- training used a separate validation set to avoid blindly selecting a model
- final testing used unseen data
- safety rules were added after prediction for disaster-response use

## 8. Short Defense Answer

If asked briefly during defense, this can be summarized as:

> Our validation procedure started with dataset preprocessing and class mapping using RescueNet and FloodNet. We split the data into training, validation, and test sets. Then we trained the model in three phases using transfer learning. During training, we monitored validation metrics such as accuracy, macro F1-score, recall, and confusion matrix. After that, we evaluated the best model on a separate test set, and we also added a conservative safety-classification layer to reduce risky predictions.

## 9. Related Files in the Repository

- `VALIDATION_PROCEDURE.md`
- `CODE_STRUCTURE.md`
- `CODE_STRUCTURE_SUMMARY.md`
- `ml_backend/README.md`
- `ml_backend/TRAINING_RUN_3_V2_RESULTS.md`
- `ml_backend/api/services/safety_classifier.py`
