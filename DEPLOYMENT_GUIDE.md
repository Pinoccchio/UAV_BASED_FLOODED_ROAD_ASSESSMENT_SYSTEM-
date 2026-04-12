# Deployment Guide

## Overview

This project deploys as a monorepo with two services:

- Frontend on Vercel from `uav-based-flooded-road-assessment-system/`
- Backend on Render from `ml_backend/`

The production system is live at:

- Frontend: `https://uav-based-flooded-road-assessment-s.vercel.app`
- Backend: `https://uav-flood-api.onrender.com`

## Final Architecture

```text
Browser
  -> Vercel frontend
  -> direct POST to Render /api/v1/predict
  -> JSON response rendered in the UI
```

This direct browser-to-Render path is intentional. It avoids Vercel function payload limits on image uploads.

## Render Configuration

Render service settings:

- Name: `uav-flood-api`
- Runtime: `Docker`
- Branch: `main`
- Root Directory: `ml_backend`
- Dockerfile Path: `./Dockerfile`
- Region: `Singapore`
- Instance Type: `Free`

Tracked backend deployment files:

- [render.yaml](C:\Users\User\Documents\first_year_files\folder_for_jobs\UAV\render.yaml)
- [ml_backend/Dockerfile](C:\Users\User\Documents\first_year_files\folder_for_jobs\UAV\ml_backend\Dockerfile)
- [ml_backend/.env.example](C:\Users\User\Documents\first_year_files\folder_for_jobs\UAV\ml_backend\.env.example)

Required Render env vars:

```env
PORT=8000
SAFETY_MODE=conservative
MODEL_PATH=/app/exports/run3_v2_best.onnx
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,https://uav-based-flooded-road-assessment-s.vercel.app
```

## Vercel Configuration

Vercel project settings:

- Framework: `Next.js`
- Root Directory: `uav-based-flooded-road-assessment-system`

Tracked frontend env example:

- [uav-based-flooded-road-assessment-system/.env.example](C:\Users\User\Documents\first_year_files\folder_for_jobs\UAV\uav-based-flooded-road-assessment-system\.env.example)

Required Vercel env vars:

```env
NEXT_PUBLIC_API_URL=https://uav-flood-api.onrender.com
```

## Local Development

Backend:

```bash
cd ml_backend/api
python main.py
```

Frontend:

```bash
cd uav-based-flooded-road-assessment-system
npm run dev
```

Local frontend env:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testing

Backend health check:

```bash
curl https://uav-flood-api.onrender.com/api/v1/health
```

Local health check:

```bash
curl http://localhost:8000/api/v1/health
```

Expected live behavior:

- image uploads succeed from the deployed frontend
- sample images return predictions
- Render logs show `POST /api/v1/predict` with `200 OK`
- the map updates when GPS metadata is present

## Troubleshooting

### Upload returns `Failed to fetch`

Check:

- `NEXT_PUBLIC_API_URL` is set correctly in Vercel
- `CORS_ORIGINS` includes the exact Vercel production URL
- Render has redeployed after the env change

### Backend is slow on first request

Render free instances sleep when idle. The first request can take tens of seconds.

### Model not found

The backend expects:

```text
/app/exports/run3_v2_best.onnx
```

If this fails, confirm `ml_backend/exports/run3_v2_best.onnx` is committed to Git.
