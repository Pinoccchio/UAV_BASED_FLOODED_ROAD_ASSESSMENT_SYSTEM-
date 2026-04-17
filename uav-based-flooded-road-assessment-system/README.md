# Frontend

This is the Next.js frontend for the UAV-Based Flooded Road Assessment System.

## Responsibilities

- Render the landing page and project sections
- Accept image uploads for flood-road assessment
- Display AI prediction results and vehicle recommendations
- Show map-based visualization for sample and GPS-tagged imagery

## Stack

- Next.js 16
- React 19
- Tailwind CSS 4
- Framer Motion
- Leaflet / React Leaflet

## Local Development

Set the backend URL in `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run the development server:

```bash
npm install
npm run dev
```

Open `http://localhost:3000` in the browser.

## Runtime Behavior

The frontend sends uploaded images directly to:

```text
${NEXT_PUBLIC_API_URL}/api/v1/predict
```

The backend response is then rendered in the assessment demo UI.

## Key Files

- `app/page.tsx` - page composition
- `components/sections/AssessmentDemo.tsx` - upload and prediction flow
- `components/map/FloodMap.tsx` - map rendering
- `lib/constants.ts` - shared frontend classification constants

## Deployment

- Frontend: Vercel
- Backend target: Render-hosted FastAPI API
