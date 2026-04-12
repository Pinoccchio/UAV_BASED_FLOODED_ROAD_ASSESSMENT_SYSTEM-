# How To Run

## Local Development

This project runs as two services:

- FastAPI backend on port `8000`
- Next.js frontend on port `3000`

## Backend

```bash
cd C:\Users\User\Documents\first_year_files\folder_for_jobs\UAV\ml_backend\api
python main.py
```

Expected backend URL:

```text
http://localhost:8000
```

Health check:

```bash
curl http://localhost:8000/api/v1/health
```

## Frontend

Create or update local env in `uav-based-flooded-road-assessment-system/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Then run:

```bash
cd C:\Users\User\Documents\first_year_files\folder_for_jobs\UAV\uav-based-flooded-road-assessment-system
npm run dev
```

Expected frontend URL:

```text
http://localhost:3000
```

## Runtime Flow

- the browser loads the Next.js frontend
- uploads are sent directly to `NEXT_PUBLIC_API_URL/api/v1/predict`
- the backend returns prediction JSON
- the frontend renders class, confidence, vehicle rules, and GPS data

## Production URLs

- Frontend: `https://uav-based-flooded-road-assessment-s.vercel.app`
- Backend: `https://uav-flood-api.onrender.com`

## Common Checks

- backend running: `curl http://localhost:8000/api/v1/health`
- frontend build: `npm run build`
- deployed backend health: `https://uav-flood-api.onrender.com/api/v1/health`
