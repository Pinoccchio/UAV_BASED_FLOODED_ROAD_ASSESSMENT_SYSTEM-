# Deployment Quickstart

## Live URLs

- Frontend: `https://uav-based-flooded-road-assessment-s.vercel.app`
- Backend: `https://uav-flood-api.onrender.com`
- Health: `https://uav-flood-api.onrender.com/api/v1/health`
- Docs: `https://uav-flood-api.onrender.com/docs`

## Production Architecture

- Vercel hosts the Next.js frontend from `uav-based-flooded-road-assessment-system/`
- Render hosts the FastAPI backend from `ml_backend/`
- The browser sends image uploads directly to Render using `NEXT_PUBLIC_API_URL`
- The ONNX model is bundled with the backend at `ml_backend/exports/run3_v2_best.onnx`

## Required Environment Variables

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

## Redeploy Checklist

1. Push changes to GitHub.
2. Vercel redeploys the frontend from `uav-based-flooded-road-assessment-system`.
3. Render redeploys the backend from `ml_backend`.
4. Test the frontend upload flow.
5. Confirm Render logs show `POST /api/v1/predict HTTP/1.1 200 OK`.

## Verification

1. Open the frontend URL.
2. Upload a JPEG or PNG image smaller than 10 MB.
3. Confirm the UI shows `Real AI prediction`.
4. Confirm GPS metadata appears when the image contains EXIF coordinates.
5. Confirm the export button downloads the JSON result.

## Notes

- Render free instances sleep after inactivity, so the first request may take up to ~50 seconds.
- The frontend no longer depends on a Vercel `/api/predict` proxy for production uploads.
