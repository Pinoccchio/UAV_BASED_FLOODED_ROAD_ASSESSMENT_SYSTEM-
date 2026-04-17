# UAV Flood Assessment System - Code Structure Guide

## Overview

This repository is split into a frontend application, a Python backend API, and the deployed ONNX model used for prediction.

## Top-Level Structure

```text
UAV/
|-- uav-based-flooded-road-assessment-system/   Frontend (Next.js)
|-- ml_backend/                                 Backend, model-serving, training code
|-- CODE_STRUCTURE_SUMMARY.md                   Quick structure overview
|-- HOW_TO_RUN.md                               Local run guide
|-- QUICK_START.md                              Short startup and deployment notes
|-- DEPLOYMENT_GUIDE.md                         Deployment details
```

## Frontend Structure

**Base folder:** `uav-based-flooded-road-assessment-system/`

```text
uav-based-flooded-road-assessment-system/
|-- app/
|   |-- layout.tsx                  Root layout
|   |-- page.tsx                    Main landing page
|   `-- globals.css                 Global styles
|-- components/
|   |-- layout/
|   |   |-- Header.tsx              Top navigation
|   |   `-- Footer.tsx              Footer
|   |-- sections/
|   |   |-- Hero.tsx                Hero section
|   |   |-- Features.tsx            Feature overview
|   |   |-- HowItWorks.tsx          System explanation
|   |   |-- AssessmentDemo.tsx      Upload and prediction UI
|   |   |-- Technology.tsx          Tech stack section
|   |   `-- About.tsx               Project background
|   |-- map/
|   |   |-- FloodMap.tsx            Leaflet map component
|   |   `-- floodMapData.ts         Static map segment data
|   `-- ui/
|       |-- badge.tsx               Reusable badge
|       |-- button.tsx              Reusable button
|       `-- card.tsx                Reusable card
|-- lib/
|   |-- constants.ts                Shared frontend classification constants
|   `-- utils.ts                    Utility helpers
|-- public/
|   `-- sample-images/              Demo images for prediction testing
|-- package.json
|-- next.config.ts
`-- README.md
```

### Key frontend files

- `app/page.tsx`
  Composes the landing page by rendering `Header`, the main content sections, and `Footer`.
- `components/sections/AssessmentDemo.tsx`
  Handles file upload, calls the backend prediction endpoint, and renders the returned result.
- `components/map/FloodMap.tsx`
  Displays the map view used in the UI.
- `lib/constants.ts`
  Keeps frontend classification labels aligned with backend classes.

### Frontend request behavior

The frontend does **not** use a local Next.js API proxy route in the current codebase.

Instead, `AssessmentDemo.tsx` reads `NEXT_PUBLIC_API_URL` and sends uploads directly to:

```text
${NEXT_PUBLIC_API_URL}/api/v1/predict
```

## Backend Structure

**Base folder:** `ml_backend/`

```text
ml_backend/
|-- api/
|   |-- main.py                     FastAPI entry point
|   |-- routes/
|   |   `-- __init__.py
|   `-- services/
|       |-- inference_service.py    ONNX inference logic
|       |-- safety_classifier.py    Safety classification rules
|       |-- gps_extractor.py        EXIF GPS extraction
|       `-- __init__.py
|-- exports/
|   `-- run3_v2_best.onnx           Deployed ONNX model
|-- scripts/
|   |-- train.py                    Training script
|   |-- export_model.py             Export PyTorch checkpoint to ONNX
|   |-- test_predictions.py         Prediction tests
|   |-- test_predictions_with_safety.py
|   |-- test_gpu_training.py
|   |-- verify_gps_all_datasets.py
|   `-- verify_setup.py
|-- preprocessing/
|   |-- label_mapper.py             Dataset label mapping
|   |-- dataset_splitter.py         Train/val/test splitting
|   |-- augmentation.py             Data augmentation utilities
|   |-- organize_dataset.py
|   `-- segmentation_analyzer.py
|-- src/
|   |-- data/
|   |   `-- dataset.py              Dataset loader
|   |-- evaluation/
|   |   `-- metrics.py              Evaluation metrics
|   |-- models/
|   |   `-- efficientnet.py         EfficientNet-B0 model definition
|   `-- training/
|-- configs/
|   |-- efficientnet_b0.yaml
|   |-- efficientnet_b0_3class.yaml
|   |-- efficientnet_b0_3class_fixed.yaml
|   |-- efficientnet_b0_3class_floodnet.yaml
|   `-- efficientnet_b0_improved.yaml
|-- requirements.txt
|-- requirements.render.txt
`-- README.md
```

### Key backend files

- `api/main.py`
  Defines the FastAPI app and exposes the main endpoints.
- `api/services/inference_service.py`
  Loads the ONNX model, preprocesses images, runs inference, and formats prediction output.
- `api/services/safety_classifier.py`
  Applies conservative safety rules to raw model predictions.
- `api/services/gps_extractor.py`
  Extracts GPS metadata from uploaded images when available.

## AI Model

**Deployed model file:** `ml_backend/exports/run3_v2_best.onnx`

This is the ONNX model used in production inference.

Related development files:

- `ml_backend/src/models/efficientnet.py`
- `ml_backend/scripts/train.py`
- `ml_backend/scripts/export_model.py`
- `ml_backend/configs/`

## Main API Endpoints

Defined in `ml_backend/api/main.py`:

- `GET /api/v1/health`
  Backend health and model status
- `POST /api/v1/predict`
  Single-image prediction
- `POST /api/v1/batch-predict`
  Batch prediction for up to 10 images
- `GET /api/v1/classes`
  Returns class metadata used by the frontend

## End-to-End Request Flow

1. The user uploads an image through the frontend.
2. `AssessmentDemo.tsx` sends the file to `${NEXT_PUBLIC_API_URL}/api/v1/predict`.
3. `ml_backend/api/main.py` receives the upload.
4. `inference_service.py` preprocesses the image and runs ONNX inference.
5. `safety_classifier.py` adjusts the result using conservative safety logic.
6. The backend returns prediction data, safety information, vehicle recommendations, and image metadata.
7. The frontend renders the result in the assessment demo.

## Configuration Files

- `uav-based-flooded-road-assessment-system/.env.example`
  Frontend environment example
- `ml_backend/.env.example`
  Backend environment example
- `render.yaml`
  Render deployment configuration
- `next.config.ts`
  Next.js configuration

## Quick Reference

- Frontend folder: `uav-based-flooded-road-assessment-system/`
- Backend folder: `ml_backend/`
- Backend entry point: `ml_backend/api/main.py`
- Main frontend upload UI: `uav-based-flooded-road-assessment-system/components/sections/AssessmentDemo.tsx`
- Deployed AI model: `ml_backend/exports/run3_v2_best.onnx`
