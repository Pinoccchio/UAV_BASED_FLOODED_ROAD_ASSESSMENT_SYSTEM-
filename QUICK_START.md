# Quick Start

## Live System

- Frontend: `https://uav-based-flooded-road-assessment-s.vercel.app`
- Backend: `https://uav-flood-api.onrender.com`

## Local Startup

1. Start the backend:

```bash
cd ml_backend/api
python main.py
```

2. Set frontend local env:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Start the frontend:

```bash
cd uav-based-flooded-road-assessment-system
npm run dev
```

4. Open:

```text
http://localhost:3000
```

## Production Env Summary

### Vercel

```env
NEXT_PUBLIC_API_URL=https://uav-flood-api.onrender.com
```

### Render

```env
PORT=8000
SAFETY_MODE=conservative
MODEL_PATH=/app/exports/run3_v2_best.onnx
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,https://uav-based-flooded-road-assessment-s.vercel.app
```

## Test

- Upload a JPEG/PNG image under 10 MB
- Confirm the UI shows `Real AI prediction`
- Confirm Render logs show `POST /api/v1/predict` with `200 OK`
