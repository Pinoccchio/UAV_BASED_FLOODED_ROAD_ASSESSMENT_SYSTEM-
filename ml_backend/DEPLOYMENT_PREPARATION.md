# Backend Deployment Preparation

## Current Production Backend

- Render URL: `https://uav-flood-api.onrender.com`
- Health: `https://uav-flood-api.onrender.com/api/v1/health`
- Docs: `https://uav-flood-api.onrender.com/docs`

## Required Backend Assets

- ONNX model committed at `ml_backend/exports/run3_v2_best.onnx`
- Docker runtime defined in [Dockerfile](C:\Users\User\Documents\first_year_files\folder_for_jobs\UAV\ml_backend\Dockerfile)
- Render config defined in [render.yaml](C:\Users\User\Documents\first_year_files\folder_for_jobs\UAV\render.yaml)

## Backend Environment Variables

```env
PORT=8000
MODEL_PATH=/app/exports/run3_v2_best.onnx
SAFETY_MODE=conservative
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,https://uav-based-flooded-road-assessment-s.vercel.app
```

## Frontend Integration

The frontend no longer proxies image uploads through a Vercel route. The browser sends images directly to:

```text
https://uav-flood-api.onrender.com/api/v1/predict
```

That requires the frontend env:

```env
NEXT_PUBLIC_API_URL=https://uav-flood-api.onrender.com
```

## Verification

1. Render logs should show successful `POST /api/v1/predict` requests.
2. `GET /api/v1/health` should return healthy with `model_loaded: true`.
3. The deployed frontend should show `Real AI prediction` after upload.
