# Defense Q&A

This file contains short, defense-ready answers for common questions about the UAV-Based Flooded Road Assessment System.

## 1. What is the code structure of the project?

The system is organized into 3 main parts:

1. **Frontend** - `uav-based-flooded-road-assessment-system/`
   - Next.js web application
   - Handles the user interface, image upload, and results display

2. **Backend** - `ml_backend/api/`
   - Python FastAPI service
   - Handles prediction requests and API processing

3. **AI Model** - `ml_backend/exports/run3_v2_best.onnx`
   - ONNX-based flood road passability model
   - Used by the backend for inference

## 2. What is the overall flow of the system?

The system flow is:

1. The user uploads an image in the frontend
2. The frontend sends the image to the backend API
3. The backend runs the ONNX model
4. The backend applies safety-classification logic
5. The system returns the road passability result and vehicle recommendations

## 3. What do you mean by validation procedure?

Our validation procedure mainly refers to **model validation**.

This includes:

- preparing and mapping the datasets into our project classes
- splitting the data into training, validation, and test sets
- training the model in phases
- checking validation metrics during training
- selecting the best model
- evaluating the final model on a separate test set

## 4. How did you validate the model?

We validated the model by:

1. Preparing the dataset from RescueNet and FloodNet
2. Mapping the original labels into 3 classes:
   - Passable
   - Limited Passability
   - Impassable
3. Splitting the dataset into:
   - Training set
   - Validation set
   - Test set
4. Training the model using transfer learning in 3 phases
5. Monitoring validation metrics such as:
   - Accuracy
   - Macro F1-score
   - Precision
   - Recall
   - Confusion Matrix
6. Testing the best model on a separate unseen test set

## 5. How was the dataset split?

For the final deployed model:

- **Total:** 4,892 images
- **Train:** 3,993 images
- **Validation:** 449 images
- **Test:** 450 images

The purpose of the split was:

- training set for learning
- validation set for monitoring performance during training
- test set for final objective evaluation

## 6. How did you train the model?

We used **EfficientNet-B0** with transfer learning.

Training was done in 3 phases:

1. **Phase 1** - train the classifier head first
2. **Phase 2** - unfreeze the last backbone blocks and fine-tune
3. **Phase 3** - unfreeze the full model for final fine-tuning

This approach helped stabilize training and improve performance.

## 7. How did you test the results like Accuracy and Macro F1?

We tested the results using a **separate test set** that was not used during training and validation.

### Accuracy

Accuracy measures the overall correctness of the model.

Formula:

```text
Accuracy = Correct Predictions / Total Predictions
```

For the final deployed model:

- **Accuracy = 78.44%**

### Macro F1-score

Macro F1-score measures how balanced the performance is across all classes.

Procedure:

1. Compute the F1-score for each class
2. Average them equally

Formula:

```text
Macro F1 = (F1_passable + F1_limited + F1_impassable) / 3
```

For the final deployed model:

- **Macro F1-score = 74.04%**

## 8. Why did you use Macro F1 and not just Accuracy?

Accuracy alone is not enough, especially when there is class imbalance.

Macro F1 is important because:

- it gives equal importance to each class
- it helps show whether one class is performing poorly
- it is more meaningful for safety-critical classes like **Impassable**

## 9. What were the final model results?

For the final deployed model:

- **Accuracy:** 78.44%
- **Macro F1-score:** 74.04%
- **Cohen’s Kappa:** 0.6134
- **Impassable Recall:** 81.29%

These values came from the final test evaluation of the selected production model.

## 10. Why is Impassable Recall important?

Impassable Recall is important because this class is safety-critical.

It tells us how many dangerous or blocked roads were correctly identified by the model.

For the final deployed model:

- **Impassable Recall = 81.29%**

That means the model was able to correctly identify most unsafe roads in the test set.

## 11. Did you add any safety layer after prediction?

Yes.

We added a **conservative safety-classification layer** in the backend.

This means:

- if the prediction is uncertain
- or if the model sees risk in a supposedly safe class

the system can downgrade the result into a safer classification such as:

- Passable -> Limited Passability
- Limited Passability -> Impassable

This was done because in disaster-response scenarios, it is safer to be conservative than to underestimate danger.

## 12. Short Ready-to-Send Answer for Validation

> Our validation procedure started with dataset preprocessing and class mapping using RescueNet and FloodNet. We split the data into training, validation, and test sets. Then we trained the model in three phases using transfer learning. During training, we monitored validation metrics such as accuracy, macro F1-score, recall, and confusion matrix. After that, we evaluated the best model on a separate test set, and we also added a conservative safety-classification layer to reduce risky predictions.

## 13. Short Ready-to-Send Answer for Accuracy and Macro F1

> We tested the results using a separate test set that was not used during training and validation. Accuracy measures the overall correctness of the model, while Macro F1 measures how balanced the model performance is across all classes. We used Macro F1 because accuracy alone is not enough, especially when the classes are imbalanced and the Impassable class is safety-critical.

## 14. Related Files

- `CODE_STRUCTURE.md`
- `CODE_STRUCTURE_SUMMARY.md`
- `VALIDATION_PROCEDURE.md`
- `METRICS_EXPLANATION.md`
- `ml_backend/README.md`
- `ml_backend/TRAINING_RUN_3_V2_RESULTS.md`
