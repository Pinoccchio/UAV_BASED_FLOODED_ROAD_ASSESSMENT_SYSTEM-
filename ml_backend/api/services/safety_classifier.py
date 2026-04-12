"""
Safety-Enhanced Flood Passability Classifier
Implements conservative classification strategies for disaster response
"""

from typing import Dict, Tuple, Any
import numpy as np
from dataclasses import dataclass
from enum import Enum


class SafetyMode(Enum):
    """Safety classification modes"""
    STANDARD = "standard"  # Normal classification
    CONSERVATIVE = "conservative"  # Err on side of caution
    AGGRESSIVE = "aggressive"  # Trust model more (not recommended for production)


@dataclass
class PredictionResult:
    """Enhanced prediction result with safety features"""
    original_class: str
    original_class_id: int
    original_confidence: float

    final_class: str
    final_class_id: int
    final_confidence: float

    probabilities: Dict[str, float]

    safety_applied: bool
    safety_reason: str
    confidence_level: str  # "high", "medium", "low"

    warning_message: str
    vehicle_recommendations: Dict[str, bool]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API response format"""
        return {
            "prediction": {
                "class": self.final_class,
                "class_id": self.final_class_id,
                "confidence": self.final_confidence,
                "probabilities": self.probabilities,
                "confidence_level": self.confidence_level
            },
            "safety_info": {
                "safety_applied": self.safety_applied,
                "safety_reason": self.safety_reason,
                "warning_message": self.warning_message,
                "original_prediction": {
                    "class": self.original_class,
                    "confidence": self.original_confidence
                } if self.safety_applied else None
            },
            "vehicle_recommendations": self.vehicle_recommendations
        }


class SafetyClassifier:
    """
    Applies safety measures to model predictions for disaster response.

    Philosophy: In disaster scenarios, it's better to be overly cautious than
    to underestimate danger. False alarms are acceptable; missed dangers are not.
    """

    # Class IDs (alphabetical order from model training)
    IMPASSABLE = 0
    LIMITED = 1
    PASSABLE = 2

    CLASS_NAMES = {
        0: "impassable",
        1: "limited_passability",
        2: "passable"
    }

    # Vehicle capability matrix
    VEHICLE_MATRIX = {
        "impassable": {
            "civilian_sedan": False,
            "high_clearance_suv": False,
            "heavy_vehicle": False,
            "emergency_vehicle": True  # Only with special equipment
        },
        "limited_passability": {
            "civilian_sedan": False,
            "high_clearance_suv": True,
            "heavy_vehicle": True,
            "emergency_vehicle": True
        },
        "passable": {
            "civilian_sedan": True,
            "high_clearance_suv": True,
            "heavy_vehicle": True,
            "emergency_vehicle": True
        }
    }

    def __init__(self, safety_mode: SafetyMode = SafetyMode.CONSERVATIVE):
        """
        Initialize safety classifier.

        Args:
            safety_mode: Classification safety mode
        """
        self.safety_mode = safety_mode

        # Confidence thresholds
        self.HIGH_CONFIDENCE = 0.80
        self.MEDIUM_CONFIDENCE = 0.70
        self.LOW_CONFIDENCE = 0.50

        # Safety thresholds (for conservative mode)
        self.IMPASSABLE_CONCERN_THRESHOLD = 0.35  # If impassable prob > 35%, consider it risky
        self.LIMITED_CONCERN_THRESHOLD = 0.40     # If limited prob > 40%, don't call it passable

    def classify(
        self,
        class_id: int,
        probabilities: np.ndarray,
        safety_mode: SafetyMode = None
    ) -> PredictionResult:
        """
        Apply safety-enhanced classification.

        Args:
            class_id: Predicted class ID from model
            probabilities: Class probabilities [impassable, limited, passable]
            safety_mode: Override default safety mode

        Returns:
            PredictionResult with safety measures applied
        """
        mode = safety_mode or self.safety_mode

        # Original prediction
        original_class = self.CLASS_NAMES[class_id]
        original_confidence = float(probabilities[class_id])

        # Convert probabilities to dict
        prob_dict = {
            "impassable": float(probabilities[self.IMPASSABLE]),
            "limited_passability": float(probabilities[self.LIMITED]),
            "passable": float(probabilities[self.PASSABLE])
        }

        # Determine confidence level
        confidence_level = self._get_confidence_level(original_confidence)

        # Apply safety logic based on mode
        if mode == SafetyMode.CONSERVATIVE:
            final_class_id, safety_applied, safety_reason = self._apply_conservative_safety(
                class_id, probabilities, original_confidence
            )
        elif mode == SafetyMode.AGGRESSIVE:
            # Trust the model completely
            final_class_id = class_id
            safety_applied = False
            safety_reason = "Aggressive mode: using model prediction as-is"
        else:  # STANDARD
            final_class_id, safety_applied, safety_reason = self._apply_standard_safety(
                class_id, probabilities, original_confidence
            )

        final_class = self.CLASS_NAMES[final_class_id]
        final_confidence = float(probabilities[final_class_id])

        # Generate warning message
        warning_message = self._generate_warning(
            final_class_id,
            confidence_level,
            safety_applied,
            probabilities
        )

        # Get vehicle recommendations
        vehicle_recommendations = self.VEHICLE_MATRIX[final_class].copy()

        return PredictionResult(
            original_class=original_class,
            original_class_id=class_id,
            original_confidence=original_confidence,
            final_class=final_class,
            final_class_id=final_class_id,
            final_confidence=final_confidence,
            probabilities=prob_dict,
            safety_applied=safety_applied,
            safety_reason=safety_reason,
            confidence_level=confidence_level,
            warning_message=warning_message,
            vehicle_recommendations=vehicle_recommendations
        )

    def _apply_conservative_safety(
        self,
        class_id: int,
        probabilities: np.ndarray,
        confidence: float
    ) -> Tuple[int, bool, str]:
        """
        Conservative safety logic: Downgrade to safer class when uncertain.

        Strategy:
        1. If predicting LIMITED/PASSABLE with low confidence AND impassable prob > 35%
           → Downgrade to IMPASSABLE
        2. If predicting PASSABLE with medium confidence AND limited prob > 40%
           → Downgrade to LIMITED
        3. Never upgrade (IMPASSABLE stays IMPASSABLE)
        """
        impassable_prob = probabilities[self.IMPASSABLE]
        limited_prob = probabilities[self.LIMITED]

        # Rule 1: Low confidence prediction with high impassable risk
        if class_id in [self.LIMITED, self.PASSABLE]:
            if confidence < self.MEDIUM_CONFIDENCE and impassable_prob > self.IMPASSABLE_CONCERN_THRESHOLD:
                return (
                    self.IMPASSABLE,
                    True,
                    f"Low confidence ({confidence:.1%}) with significant impassable risk ({impassable_prob:.1%}). Downgraded to impassable for safety."
                )

        # Rule 2: Predicting PASSABLE but LIMITED probability is concerning
        if class_id == self.PASSABLE:
            if confidence < self.HIGH_CONFIDENCE and limited_prob > self.LIMITED_CONCERN_THRESHOLD:
                return (
                    self.LIMITED,
                    True,
                    f"Moderate confidence ({confidence:.1%}) with significant limited risk ({limited_prob:.1%}). Downgraded to limited passability for safety."
                )

        # Rule 3: Very low confidence on any prediction
        if confidence < self.LOW_CONFIDENCE:
            # Find the most dangerous class with reasonable probability
            if impassable_prob > 0.25:
                return (
                    self.IMPASSABLE,
                    True,
                    f"Very low confidence ({confidence:.1%}). Defaulting to most conservative classification."
                )
            elif limited_prob > 0.30 and class_id == self.PASSABLE:
                return (
                    self.LIMITED,
                    True,
                    f"Very low confidence ({confidence:.1%}). Defaulting to conservative classification."
                )

        # No safety adjustment needed
        return class_id, False, "Standard prediction (conservative mode, no adjustment needed)"

    def _apply_standard_safety(
        self,
        class_id: int,
        probabilities: np.ndarray,
        confidence: float
    ) -> Tuple[int, bool, str]:
        """
        Standard safety logic: Only adjust in very uncertain cases.
        """
        impassable_prob = probabilities[self.IMPASSABLE]

        # Only downgrade if confidence is very low AND impassable risk is high
        if class_id in [self.LIMITED, self.PASSABLE]:
            if confidence < 0.60 and impassable_prob > 0.45:
                return (
                    self.IMPASSABLE,
                    True,
                    f"Very uncertain prediction ({confidence:.1%}) with high impassable risk ({impassable_prob:.1%})."
                )

        return class_id, False, "Standard prediction (no adjustment needed)"

    def _get_confidence_level(self, confidence: float) -> str:
        """Categorize confidence level"""
        if confidence >= self.HIGH_CONFIDENCE:
            return "high"
        elif confidence >= self.MEDIUM_CONFIDENCE:
            return "medium"
        else:
            return "low"

    def _generate_warning(
        self,
        class_id: int,
        confidence_level: str,
        safety_applied: bool,
        probabilities: np.ndarray
    ) -> str:
        """Generate user-facing warning message"""

        class_name = self.CLASS_NAMES[class_id]
        impassable_prob = probabilities[self.IMPASSABLE]
        limited_prob = probabilities[self.LIMITED]

        warnings = []

        # Base warning for all predictions
        warnings.append("⚠️ MODEL TRAINED ON US DATA - Validate with local ground knowledge")

        # Safety adjustment warning
        if safety_applied:
            warnings.append("🛡️ SAFETY MEASURE APPLIED - Prediction adjusted to safer classification")

        # Confidence-based warnings
        if confidence_level == "low":
            warnings.append("⚠️ LOW CONFIDENCE - Model is uncertain. Exercise extreme caution.")
        elif confidence_level == "medium":
            warnings.append("⚠️ MODERATE CONFIDENCE - Verify with additional information if possible.")

        # Class-specific warnings
        if class_id == self.IMPASSABLE:
            warnings.append("🚫 IMPASSABLE - Do not attempt passage. Road is dangerous.")

        elif class_id == self.LIMITED:
            if impassable_prob > 0.25:
                warnings.append(f"⚠️ CAUTION - {impassable_prob:.0%} chance road is actually impassable")
            warnings.append("⚠️ LIMITED PASSABILITY - Only high-clearance vehicles. Proceed with extreme caution.")

        elif class_id == self.PASSABLE:
            if impassable_prob > 0.15:
                warnings.append(f"⚠️ CAUTION - {impassable_prob:.0%} chance road may have damage")
            if limited_prob > 0.25:
                warnings.append(f"ℹ️ NOTE - {limited_prob:.0%} chance limited passability")
            warnings.append("✓ PASSABLE - Road appears clear, but remain vigilant")

        return " | ".join(warnings)


class SafetyClassifierFactory:
    """Factory for creating safety classifiers"""

    @staticmethod
    def create_for_deployment() -> SafetyClassifier:
        """Create classifier for production deployment (conservative)"""
        return SafetyClassifier(safety_mode=SafetyMode.CONSERVATIVE)

    @staticmethod
    def create_for_testing() -> SafetyClassifier:
        """Create classifier for testing (standard)"""
        return SafetyClassifier(safety_mode=SafetyMode.STANDARD)

    @staticmethod
    def create_for_research() -> SafetyClassifier:
        """Create classifier for research (aggressive)"""
        return SafetyClassifier(safety_mode=SafetyMode.AGGRESSIVE)


# Example usage
if __name__ == "__main__":
    # Example: Model predicts LIMITED with 54% confidence
    # but IMPASSABLE probability is 46% (very close!)

    classifier = SafetyClassifier(safety_mode=SafetyMode.CONSERVATIVE)

    # Case 1: Uncertain prediction between impassable and limited
    print("="*80)
    print("CASE 1: Uncertain prediction (54% limited, 46% impassable)")
    print("="*80)

    probabilities = np.array([0.46, 0.54, 0.00])  # [impassable, limited, passable]
    predicted_class = 1  # LIMITED

    result = classifier.classify(predicted_class, probabilities)

    print(f"\nOriginal Prediction: {result.original_class} ({result.original_confidence:.1%})")
    print(f"Final Prediction: {result.final_class} ({result.final_confidence:.1%})")
    print(f"Safety Applied: {result.safety_applied}")
    print(f"Reason: {result.safety_reason}")
    print(f"Confidence Level: {result.confidence_level}")
    print(f"\nWarning: {result.warning_message}")

    # Case 2: High confidence passable
    print("\n" + "="*80)
    print("CASE 2: High confidence passable (97% passable)")
    print("="*80)

    probabilities = np.array([0.00, 0.03, 0.97])  # [impassable, limited, passable]
    predicted_class = 2  # PASSABLE

    result = classifier.classify(predicted_class, probabilities)

    print(f"\nOriginal Prediction: {result.original_class} ({result.original_confidence:.1%})")
    print(f"Final Prediction: {result.final_class} ({result.final_confidence:.1%})")
    print(f"Safety Applied: {result.safety_applied}")
    print(f"Reason: {result.safety_reason}")
    print(f"Confidence Level: {result.confidence_level}")
    print(f"\nWarning: {result.warning_message}")

    # Case 3: Borderline passable with limited risk
    print("\n" + "="*80)
    print("CASE 3: Borderline passable (64% passable, 36% limited)")
    print("="*80)

    probabilities = np.array([0.00, 0.36, 0.64])  # [impassable, limited, passable]
    predicted_class = 2  # PASSABLE

    result = classifier.classify(predicted_class, probabilities)

    print(f"\nOriginal Prediction: {result.original_class} ({result.original_confidence:.1%})")
    print(f"Final Prediction: {result.final_class} ({result.final_confidence:.1%})")
    print(f"Safety Applied: {result.safety_applied}")
    print(f"Reason: {result.safety_reason}")
    print(f"Confidence Level: {result.confidence_level}")
    print(f"\nWarning: {result.warning_message}")

    print("\n" + "="*80)
    print("API Response Format:")
    print("="*80)
    print("\nimport json")
    print("print(json.dumps(result.to_dict(), indent=2))")
