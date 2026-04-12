"""
FastAPI backend for UAV flood passability prediction.

Designed to run both locally and in containerized production environments.
"""

from contextlib import asynccontextmanager
import os
from pathlib import Path
from typing import Dict, List

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from .services.inference_service import InferenceService
    from .services.safety_classifier import SafetyClassifier, SafetyMode
except ImportError:
    from services.inference_service import InferenceService
    from services.safety_classifier import SafetyClassifier, SafetyMode


def parse_cors_origins() -> list[str]:
    """Parse comma-separated CORS origins from the environment."""
    configured = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000",
    )
    return [origin.strip() for origin in configured.split(",") if origin.strip()]


MODEL_PATH = Path(
    os.getenv(
        "MODEL_PATH",
        str(Path(__file__).resolve().parent.parent / "exports" / "run3_v2_best.onnx"),
    )
)
SAFETY_MODE = SafetyMode(os.getenv("SAFETY_MODE", "conservative"))

inference_service = InferenceService(model_path=MODEL_PATH)
safety_classifier = SafetyClassifier(safety_mode=SAFETY_MODE)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Load the ONNX model once when the app starts."""
    print("=" * 60)
    print("UAV Flood Passability API - Starting...")
    print("=" * 60)
    inference_service.load_model()
    print(f"[OK] Model path: {MODEL_PATH}")
    print(f"[OK] Model loaded: {inference_service.model_loaded}")
    print("=" * 60)
    yield


app = FastAPI(
    title="UAV Flood Passability API",
    description="AI-powered flood assessment for vehicle passability classification",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=parse_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictionResponse(BaseModel):
    """Prediction API response."""

    prediction: Dict
    safety_info: Dict
    vehicle_recommendations: Dict
    image_metadata: Dict


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    model_loaded: bool
    model_version: str


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "UAV Flood Passability API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Return backend health and model status."""
    return HealthResponse(
        status="healthy" if inference_service.model_loaded else "unhealthy",
        model_loaded=inference_service.model_loaded,
        model_version="v1.0.0",
    )


@app.post("/api/v1/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict(image: UploadFile = File(...)):
    """Predict vehicle passability from a single uploaded image."""
    allowed_types = ["image/jpeg", "image/jpg", "image/png"]
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}",
        )

    max_size = 10 * 1024 * 1024
    contents = await image.read()

    if len(contents) > max_size:
        raise HTTPException(status_code=400, detail="File too large. Maximum size: 10MB")

    if not inference_service.model_loaded:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please check server logs.",
        )

    try:
        result = inference_service.predict(contents)
        safety_result = safety_classifier.classify(
            result["prediction"]["class_id"],
            result["probabilities_array"],
        )

        response_dict = safety_result.to_dict()
        response_dict["image_metadata"] = result.get(
            "image_metadata",
            {
                "has_gps": False,
                "location_note": "No GPS data found in image EXIF.",
            },
        )

        return PredictionResponse(**response_dict)
    except Exception as exc:
        print(f"Prediction error: {exc}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc


@app.post("/api/v1/batch-predict", tags=["Prediction"])
async def batch_predict(images: List[UploadFile] = File(...)):
    """Predict vehicle passability for up to 10 uploaded images."""
    if len(images) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 images per batch")

    results = []
    allowed_types = ["image/jpeg", "image/jpg", "image/png"]

    for image in images:
        if image.content_type not in allowed_types:
            results.append({"filename": image.filename, "error": "Invalid file type"})
            continue

        contents = await image.read()

        try:
            result = inference_service.predict(contents)
            safety_result = safety_classifier.classify(
                result["prediction"]["class_id"],
                result["probabilities_array"],
            )

            final_result = safety_result.to_dict()
            final_result["filename"] = image.filename
            results.append(final_result)
        except Exception as exc:
            results.append({"filename": image.filename, "error": str(exc)})

    return {"predictions": results}


@app.get("/api/v1/classes", tags=["Info"])
async def get_classes():
    """Return class metadata used by the frontend."""
    return {
        "classes": [
            {
                "id": 0,
                "name": "impassable",
                "label": "Impassable",
                "description": "Road is completely blocked, no vehicles can pass",
                "color": "#ef4444",
            },
            {
                "id": 1,
                "name": "limited_passability",
                "label": "Limited Passability",
                "description": "Road passable with caution for high-clearance vehicles only",
                "color": "#eab308",
            },
            {
                "id": 2,
                "name": "passable",
                "label": "Passable",
                "description": "Road is clear and safe for all vehicle types",
                "color": "#22c55e",
            },
        ]
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=False,
        log_level="info",
    )
