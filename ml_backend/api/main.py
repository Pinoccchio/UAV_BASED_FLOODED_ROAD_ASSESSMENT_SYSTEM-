"""
FastAPI Backend for UAV Flood Passability Prediction.

Production-ready API serving ONNX model for real-time inference.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List
import uvicorn
from pathlib import Path

from services.inference_service import InferenceService
from services.safety_classifier import SafetyClassifier, SafetyMode
import os

# Initialize FastAPI app
app = FastAPI(
    title="UAV Flood Passability API",
    description="AI-powered flood assessment for vehicle passability classification",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize inference service
MODEL_PATH = Path(os.getenv("MODEL_PATH", str(Path(__file__).parent.parent / "exports" / "run3_v2_best.onnx")))
SAFETY_MODE = SafetyMode(os.getenv("SAFETY_MODE", "conservative"))

inference_service = InferenceService(model_path=MODEL_PATH)
safety_classifier = SafetyClassifier(safety_mode=SAFETY_MODE)

# Load model immediately
print("="*60)
print("UAV Flood Passability API - Loading Model...")
print("="*60)
inference_service.load_model()
print("="*60)


# Response models
class PredictionResponse(BaseModel):
    """Prediction API response."""
    prediction: Dict
    safety_info: Dict
    vehicle_recommendations: Dict
    image_metadata: Dict  # GPS and camera metadata


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
    model_version: str


@app.on_event("startup")
async def startup_event():
    """Load model on startup."""
    print("="*60)
    print("UAV Flood Passability API - Starting...")
    print("="*60)

    # Load model
    inference_service.load_model()

    print(f"[OK] Model loaded: {MODEL_PATH}")
    print(f"[OK] API ready!")
    print("="*60)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "UAV Flood Passability API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status and model information
    """
    return HealthResponse(
        status="healthy" if inference_service.model_loaded else "unhealthy",
        model_loaded=inference_service.model_loaded,
        model_version="v1.0.0"
    )


@app.post("/api/v1/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict(image: UploadFile = File(...)):
    """
    Predict vehicle passability from UAV flood imagery.

    Args:
        image: Uploaded image file (JPEG/PNG, max 10MB)

    Returns:
        Prediction with class, confidence, and vehicle recommendations
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png"]
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )

    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    contents = await image.read()

    if len(contents) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: 10MB"
        )

    # Check if model is loaded
    if not inference_service.model_loaded:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please check server logs."
        )

    try:
        # Run inference
        result = inference_service.predict(contents)

        # Apply safety classifier
        safety_result = safety_classifier.classify(
            result['prediction']['class_id'],
            result['probabilities_array']
        )

        # Combine safety result with image metadata
        response_dict = safety_result.to_dict()
        response_dict['image_metadata'] = result.get('image_metadata', {
            "has_gps": False,
            "location_note": "No GPS data found in image EXIF."
        })

        # Return safety-enhanced result with GPS metadata
        return PredictionResponse(**response_dict)

    except Exception as e:
        print(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post("/api/v1/batch-predict", tags=["Prediction"])
async def batch_predict(images: List[UploadFile] = File(...)):
    """
    Batch prediction for multiple images.

    Args:
        images: List of uploaded image files

    Returns:
        List of predictions
    """
    if len(images) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 images per batch"
        )

    results = []

    for image in images:
        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png"]
        if image.content_type not in allowed_types:
            results.append({
                "filename": image.filename,
                "error": "Invalid file type"
            })
            continue

        # Read file
        contents = await image.read()

        try:
            # Run inference
            result = inference_service.predict(contents)

            # Apply safety classifier
            safety_result = safety_classifier.classify(
                result['prediction']['class_id'],
                result['probabilities_array']
            )

            final_result = safety_result.to_dict()
            final_result["filename"] = image.filename
            results.append(final_result)

        except Exception as e:
            results.append({
                "filename": image.filename,
                "error": str(e)
            })

    return {"predictions": results}


@app.get("/api/v1/classes", tags=["Info"])
async def get_classes():
    """
    Get available classification classes.

    Returns:
        List of class definitions
    """
    return {
        "classes": [
            {
                "id": 0,
                "name": "impassable",
                "label": "Impassable",
                "description": "Road is completely blocked, no vehicles can pass",
                "color": "#ef4444"
            },
            {
                "id": 1,
                "name": "limited_passability",
                "label": "Limited Passability",
                "description": "Road passable with caution for high-clearance vehicles only",
                "color": "#eab308"
            },
            {
                "id": 2,
                "name": "passable",
                "label": "Passable",
                "description": "Road is clear and safe for all vehicle types",
                "color": "#22c55e"
            }
        ]
    }


if __name__ == "__main__":
    # Run server
    uvicorn.run(
        app,  # Pass app directly instead of string
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload so model loads in main process
        log_level="info"
    )
