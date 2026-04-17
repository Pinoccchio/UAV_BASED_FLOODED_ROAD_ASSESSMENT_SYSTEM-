# UAV-Based Flooded Road Assessment System

This repository contains a capstone project for assessing flooded road passability from UAV imagery.

## Project Structure

- `uav-based-flooded-road-assessment-system/`
  Next.js frontend for the web interface, image upload, map view, and results display.
- `ml_backend/`
  Python FastAPI backend for inference, safety classification, GPS metadata extraction, and model-serving logic.
- `ml_backend/exports/run3_v2_best.onnx`
  Deployed ONNX model used for prediction.

## System Flow

1. A user uploads an aerial image through the frontend.
2. The frontend sends the image to the FastAPI backend.
3. The backend runs ONNX inference and applies safety rules.
4. The system returns the predicted road passability and vehicle recommendations.

## Main Technologies

- Next.js 16
- React 19
- FastAPI
- ONNX Runtime
- EfficientNet-B0

## Local Run

Backend:

```bash
cd ml_backend/api
python main.py
```

Frontend:

```bash
cd uav-based-flooded-road-assessment-system
npm install
npm run dev
```

Frontend environment variable:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Live Deployment

- Frontend: `https://uav-based-flooded-road-assessment-s.vercel.app`
- Backend: `https://uav-flood-api.onrender.com`

## Useful Documents

- `HOW_TO_RUN.md`
- `QUICK_START.md`
- `CODE_STRUCTURE.md`
- `ml_backend/README.md`

## Notes

- `.env.local`, logs, and Python cache files are intentionally ignored and should not be committed.
- Some research and implementation notes are included for documentation and defense support.
