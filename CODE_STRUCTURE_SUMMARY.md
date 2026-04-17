# UAV Code Structure Summary

This repository is organized into 3 main parts.

## 1. Frontend

**Folder:** `uav-based-flooded-road-assessment-system/`

Purpose:
- Web interface
- Image upload
- Results display
- Map visualization

Main files:
- `uav-based-flooded-road-assessment-system/app/page.tsx`
- `uav-based-flooded-road-assessment-system/components/sections/AssessmentDemo.tsx`
- `uav-based-flooded-road-assessment-system/components/map/FloodMap.tsx`

## 2. Backend

**Folder:** `ml_backend/api/`

Purpose:
- Receives prediction requests
- Validates uploaded images
- Runs backend API processing
- Returns prediction results to the frontend

Main files:
- `ml_backend/api/main.py`
- `ml_backend/api/services/inference_service.py`
- `ml_backend/api/services/safety_classifier.py`
- `ml_backend/api/services/gps_extractor.py`

Main endpoints:
- `GET /api/v1/health`
- `POST /api/v1/predict`
- `POST /api/v1/batch-predict`
- `GET /api/v1/classes`

## 3. AI Model

**Model file:** `ml_backend/exports/run3_v2_best.onnx`

Purpose:
- ONNX-based flood road passability model
- Loaded by the backend inference service for production prediction

Related development files:
- `ml_backend/src/models/efficientnet.py`
- `ml_backend/scripts/train.py`
- `ml_backend/scripts/export_model.py`
- `ml_backend/configs/`

## Main Flow

1. The user uploads an image in the frontend.
2. The frontend sends the image to the backend API using `NEXT_PUBLIC_API_URL`.
3. The backend runs the ONNX model.
4. The backend applies safety classification logic.
5. The system returns the road passability result and vehicle recommendations.

## Quick Folder Guide

- `uav-based-flooded-road-assessment-system/` = Frontend
- `ml_backend/api/` = Backend API
- `ml_backend/exports/run3_v2_best.onnx` = Deployed AI model
- `ml_backend/src/` and `ml_backend/scripts/` = Model development and training code
