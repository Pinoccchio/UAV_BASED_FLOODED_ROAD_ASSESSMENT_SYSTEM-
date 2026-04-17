# Metrics Explanation

This document explains how the project tested and interpreted the main evaluation metrics used for the model results.

## Overview

The two main metrics asked about in defense are:

- **Accuracy**
- **Macro F1-score**

These were measured using a **separate test set** that was not used for training and validation.

That is important because it makes the evaluation more objective and shows how the model performs on unseen images.

## 1. How the Results Were Tested

After training, the best model was evaluated using the **held-out test set**.

For the final deployed model:

- **Total dataset:** 4,892 images
- **Train:** 3,993 images
- **Validation:** 449 images
- **Test:** 450 images

The testing step was done only after model training and validation were already finished.

## 2. Accuracy

### Meaning

Accuracy shows the **overall percentage of correct predictions** made by the model.

### Formula

```text
Accuracy = Number of Correct Predictions / Total Number of Predictions
```

### Interpretation

If the model predicts the correct class for most test images, the accuracy becomes higher.

For example:

- if 100 images are tested
- and 78 are predicted correctly

then:

```text
Accuracy = 78 / 100 = 78%
```

### Our Result

For the final deployed model:

- **Accuracy = 78.44%**

This means the model correctly classified about 78 out of every 100 test images overall.

## 3. Macro F1-score

### Meaning

Macro F1-score measures how balanced the model performance is across all classes.

This is important because our classes are not perfectly balanced:

1. Passable
2. Limited Passability
3. Impassable

### Why Not Accuracy Alone

Accuracy alone can sometimes look acceptable even if one class performs poorly.

That is risky in this project because **Impassable** is safety-critical.

So aside from overall correctness, we also need to know whether the model performs fairly across all classes.

### Procedure

First, an **F1-score** is computed for each class separately.

Then the three class F1-scores are averaged equally:

```text
Macro F1 = (F1_passable + F1_limited + F1_impassable) / 3
```

Because it is **Macro** F1, each class gets equal importance even if one class has fewer samples than the others.

### Interpretation

- A higher Macro F1 means the model performs more consistently across all classes.
- A lower Macro F1 may mean the model performs well on some classes but poorly on others.

### Our Result

For the final deployed model:

- **Macro F1-score = 74.04%**

This means the model’s performance across Passable, Limited Passability, and Impassable is reasonably balanced.

## 4. Why Macro F1 Matters in This Project

Macro F1 is important for this system because:

- the dataset is class-imbalanced
- road safety is involved
- the **Impassable** class must not be ignored

Even if overall accuracy is acceptable, we still need to check whether dangerous-road predictions are being handled properly.

That is why the project monitored not only accuracy, but also:

- Macro F1-score
- Per-class precision
- Per-class recall
- Cohen’s Kappa
- Confusion Matrix

## 5. Final Reported Results

For the final deployed model:

- **Accuracy:** 78.44%
- **Macro F1-score:** 74.04%
- **Cohen’s Kappa:** 0.6134
- **Impassable Recall:** 81.29%

These were taken from the final test evaluation of the selected production model.

## 6. Short Defense Answer

If asked briefly during defense, this can be answered as:

> Sir, tinest po namin yung results gamit ang separate test set na hindi na kasama sa training at validation para objective yung evaluation. Yung Accuracy po measures overall correctness, or ilan ang tamang predictions out of all test images. Yung Macro F1 naman po kino-compute by getting the F1-score of each class first, then averaging them equally. Ginamit po namin yung Macro F1 kasi hindi enough ang accuracy lang, especially since safety-critical yung Impassable class and may class imbalance sa dataset.

## 7. Related Files in the Repository

- `METRICS_EXPLANATION.md`
- `VALIDATION_PROCEDURE.md`
- `ml_backend/README.md`
- `ml_backend/src/evaluation/metrics.py`
- `ml_backend/TRAINING_RUN_3_V2_RESULTS.md`
