# UAV Flood Assessment System - Code Structure Guide

## Overview

This document explains where to find key code files in both the **Python Backend** and **Next.js Frontend**.

---

## Table of Contents

1. [Python Backend Structure](#python-backend-structure)
2. [Next.js Frontend Structure](#next-js-frontend-structure)
3. [Request Flow Diagram](#request-flow-diagram)
4. [Key API Endpoints](#key-api-endpoints)
5. [Configuration Files](#configuration-files)
6. [Quick Reference](#quick-reference)

---

## Python Backend Structure

**Base Directory:** `ml_backend/`

```
ml_backend/
├── api/                          # FastAPI application
│   ├── main.py                   # ⭐ MAIN API SERVER - Entry point, endpoints
│   ├── services/                 # Business logic services
│   │   ├── inference_service.py  # ⭐ AI MODEL INFERENCE - ONNX prediction
│   │   └── safety_classifier.py  # ⭐ SAFETY CHECKS - Conservative classification
│   └── routes/                   # Additional API routes (future)
│
├── exports/                      # Exported models
│   └── run3_v2_best.onnx        # ⭐ TRAINED AI MODEL (54 MB)
│
├── scripts/                      # Utility scripts
│   ├── export_model.py          # PyTorch → ONNX conversion
│   ├── train.py                 # Model training script
│   └── evaluate.py              # Model evaluation
│
├── checkpoints/                  # Training checkpoints
│   └── epochepoch=45-valf1val/f1=0.7652.ckpt  # Best model checkpoint
│
├── src/                          # Training code
│   ├── models/                  # Model architectures
│   ├── data/                    # Data loaders
│   └── training/                # Training loops
│
├── preprocessing/                # Data preprocessing
│   ├── label_mapper.py          # Dataset label mapping
│   └── augmentation.py          # Data augmentation
│
├── requirements.txt              # Python dependencies
└── README.md                     # Backend documentation
```

### Key Python Files Explained

#### 1. **`api/main.py`** - FastAPI Application
**Location:** `ml_backend/api/main.py`

**What it does:**
- Initializes FastAPI application
- Defines API endpoints (`/predict`, `/health`)
- Loads the ONNX model on startup
- Integrates safety classifier
- Handles CORS (allows frontend to connect)

**Key code:**
```python
@app.post("/api/v1/predict")
async def predict(image: UploadFile = File(...)):
    # Receives image from Next.js
    # Calls inference service
    # Returns prediction JSON
```

**When to edit:**
- Adding new API endpoints
- Changing CORS settings
- Modifying response format
- Adding authentication

---

#### 2. **`api/services/inference_service.py`** - AI Inference
**Location:** `ml_backend/api/services/inference_service.py`

**What it does:**
- Loads ONNX model into memory
- Preprocesses uploaded images (resize, normalize)
- Runs model inference
- Returns prediction probabilities

**Key code:**
```python
class InferenceService:
    def __init__(self, model_path):
        self.session = ort.InferenceSession(model_path)

    def predict(self, image_bytes):
        # Preprocess image
        # Run ONNX inference
        # Return class + probabilities
```

**When to edit:**
- Changing image preprocessing (resize, normalization)
- Updating class names/labels
- Modifying prediction logic
- Optimizing inference speed

---

#### 3. **`api/services/safety_classifier.py`** - Safety Logic
**Location:** `ml_backend/api/services/safety_classifier.py`

**What it does:**
- Applies conservative safety measures
- Downgrades uncertain predictions
- Adds warning messages
- Prevents dangerous misclassifications

**Key code:**
```python
class SafetyClassifier:
    def classify(self, class_id, probabilities):
        # Check confidence threshold
        # Apply conservative rules
        # Return safe classification
```

**When to edit:**
- Adjusting safety thresholds
- Changing conservative rules
- Modifying warning messages
- Fine-tuning safety vs accuracy tradeoff

---

#### 4. **`exports/run3_v2_best.onnx`** - AI Model
**Location:** `ml_backend/exports/run3_v2_best.onnx`

**What it is:**
- Trained EfficientNet-B0 model (3-class classifier)
- ONNX format (optimized for production inference)
- 54 MB file size
- Test accuracy: 79.56%

**Classes:**
- 0: Impassable
- 1: Limited Passability
- 2: Passable

**When to replace:**
- After training a new model
- When improving model accuracy
- After adding more training data

---

## Next.js Frontend Structure

**Base Directory:** `uav-based-flooded-road-assessment-system/`

```
uav-based-flooded-road-assessment-system/
├── app/                          # Next.js 16 App Router
│   ├── page.tsx                 # ⭐ HOME PAGE - Landing page
│   ├── layout.tsx               # Root layout with navigation
│   ├── api/                     # API routes (server-side)
│   │   └── predict/
│   │       └── route.ts         # ⭐ API PROXY - Forwards to Python backend
│   └── globals.css              # Global styles
│
├── components/                   # React components
│   ├── sections/                # Page sections
│   │   ├── AssessmentDemo.tsx   # ⭐ IMAGE UPLOAD & PREDICTION UI
│   │   ├── Hero.tsx             # Hero section
│   │   ├── Features.tsx         # Features section
│   │   ├── FloodMap.tsx         # Interactive Leaflet map
│   │   ├── HowItWorks.tsx       # Process explanation
│   │   └── ImpactMetrics.tsx    # Statistics display
│   │
│   ├── ui/                      # Reusable UI components
│   │   ├── badge.tsx            # ⭐ CLASSIFICATION BADGES
│   │   ├── button.tsx           # Button component
│   │   ├── card.tsx             # Card component
│   │   └── tabs.tsx             # Tabs component
│   │
│   └── layout/                  # Layout components
│       ├── Header.tsx           # Navigation header
│       └── Footer.tsx           # Footer
│
├── lib/                         # Utilities
│   └── utils.ts                 # Helper functions
│
├── public/                      # Static assets
│   └── images/                  # Images, icons
│
├── .env.local                   # ⭐ ENVIRONMENT VARIABLES
├── package.json                 # Node.js dependencies
├── next.config.ts               # Next.js configuration
└── tailwind.config.ts           # Tailwind CSS configuration
```

### Key Frontend Files Explained

#### 1. **`app/page.tsx`** - Home Page
**Location:** `uav-based-flooded-road-assessment-system/app/page.tsx`

**What it does:**
- Main landing page
- Imports and renders all sections (Hero, Features, AssessmentDemo, etc.)
- Defines page layout

**Key code:**
```tsx
export default function Home() {
  return (
    <>
      <Hero />
      <Features />
      <AssessmentDemo />
      <FloodMap />
      {/* ... */}
    </>
  )
}
```

**When to edit:**
- Adding/removing page sections
- Changing page layout
- Modifying section order

---

#### 2. **`app/api/predict/route.ts`** - API Proxy Route
**Location:** `uav-based-flooded-road-assessment-system/app/api/predict/route.ts`

**What it does:**
- Next.js API route (runs on server-side)
- Receives image uploads from frontend
- Validates file type and size
- Forwards requests to Python backend (localhost:8000)
- Returns prediction to frontend

**Key code:**
```typescript
export async function POST(request: NextRequest) {
  const formData = await request.formData();
  const image = formData.get('image');

  // Validate and forward to Python backend
  const response = await fetch(`${PYTHON_API_URL}/api/v1/predict`, {
    method: 'POST',
    body: pythonFormData,
  });

  return NextResponse.json(result);
}
```

**When to edit:**
- Changing backend URL
- Adding request validation
- Modifying error handling
- Adding request logging

---

#### 3. **`components/sections/AssessmentDemo.tsx`** - Main UI Component
**Location:** `uav-based-flooded-road-assessment-system/components/sections/AssessmentDemo.tsx`

**What it does:**
- Interactive demo section on homepage
- File upload UI (drag & drop + button)
- Sends images to `/api/predict`
- Displays AI predictions
- Shows confidence scores, vehicle recommendations, safety warnings
- Animated transitions

**Key code:**
```tsx
const handleImageUpload = async (file: File) => {
  const formData = new FormData();
  formData.append('image', file);

  const response = await fetch('/api/predict', {
    method: 'POST',
    body: formData,
  });

  const result = await response.json();
  // Update UI with prediction
}
```

**When to edit:**
- Changing upload UI design
- Modifying prediction display
- Adding new features (map integration, history)
- Customizing animations

---

#### 4. **`components/ui/badge.tsx`** - Classification Badges
**Location:** `uav-based-flooded-road-assessment-system/components/ui/badge.tsx`

**What it does:**
- Renders color-coded classification badges
- Shows passability levels (Passable, Limited, Impassable)
- Different colors for each severity level

**Classes:**
- `passable`: Green badge
- `limited`: Yellow/orange badge
- `impassable`: Red badge

**When to edit:**
- Changing badge colors
- Adding new classification levels
- Modifying badge styles

---

#### 5. **`.env.local`** - Environment Variables
**Location:** `uav-based-flooded-road-assessment-system/.env.local`

**What it contains:**
```
PYTHON_API_URL=http://localhost:8000
NEXT_PUBLIC_MODEL_VERSION=v1.0.0-run3-v2
```

**When to edit:**
- Changing backend URL (production deployment)
- Adding new environment variables
- Configuring API keys (future)

**⚠️ Important:** Restart Next.js dev server after editing this file!

---

## Request Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                            │
│                    http://localhost:3000                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ 1. User uploads flood image
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              NEXT.JS FRONTEND (Port 3000)                       │
│                                                                 │
│  File: app/page.tsx                                            │
│    └─> components/sections/AssessmentDemo.tsx                 │
│         ├─> User clicks upload button                         │
│         ├─> handleImageUpload(file)                          │
│         └─> fetch('/api/predict', {image})                   │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             │ 2. POST /api/predict
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│         NEXT.JS API ROUTE (Server-side)                        │
│                                                                 │
│  File: app/api/predict/route.ts                               │
│    ├─> Validates file type (JPEG/PNG)                        │
│    ├─> Validates file size (<10MB)                           │
│    └─> Forwards to Python backend                            │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             │ 3. POST http://localhost:8000/api/v1/predict
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              PYTHON BACKEND (Port 8000)                        │
│                                                                 │
│  File: api/main.py                                            │
│    └─> @app.post("/api/v1/predict")                          │
│         └─> async def predict(image)                          │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             │ 4. Call inference service
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              INFERENCE SERVICE                                  │
│                                                                 │
│  File: api/services/inference_service.py                      │
│    ├─> Load image bytes                                       │
│    ├─> Preprocess (resize to 448x448, normalize)             │
│    ├─> Run ONNX model inference                              │
│    └─> Get class probabilities                               │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             │ 5. Load ONNX model
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ONNX MODEL                                   │
│                                                                 │
│  File: exports/run3_v2_best.onnx                              │
│    ├─> EfficientNet-B0 architecture                          │
│    ├─> Input: [1, 3, 448, 448] tensor                        │
│    ├─> Output: [1, 3] logits                                 │
│    └─> Classes: [Impassable, Limited, Passable]              │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             │ 6. Return probabilities
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              SAFETY CLASSIFIER                                  │
│                                                                 │
│  File: api/services/safety_classifier.py                      │
│    ├─> Check confidence threshold (>0.60)                    │
│    ├─> Apply conservative safety rules                       │
│    ├─> Downgrade if uncertain                                │
│    └─> Add warning messages                                  │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             │ 7. Return final classification JSON
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              RESPONSE JSON                                      │
│                                                                 │
│  {                                                             │
│    "prediction": {                                            │
│      "class": "limited_passability",                         │
│      "class_id": 1,                                          │
│      "confidence": 0.89,                                     │
│      "probabilities": {...}                                  │
│    },                                                         │
│    "vehicle_recommendations": {...},                         │
│    "safety_info": {...}                                      │
│  }                                                            │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             │ 8. Return to Next.js API route
                             ▼
                      (Back to Next.js)
                             │
                             │ 9. Return to frontend component
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              FRONTEND UI UPDATE                                 │
│                                                                 │
│  File: components/sections/AssessmentDemo.tsx                 │
│    ├─> Update active segment (passable/limited/impassable)   │
│    ├─> Animate confidence score                              │
│    ├─> Show vehicle recommendations                          │
│    ├─> Display safety warnings                               │
│    └─> Update map (if integrated)                            │
└─────────────────────────────────────────────────────────────────┘
                             │
                             │ 10. User sees result
                             ▼
                    ┌─────────────────┐
                    │  PREDICTION UI  │
                    │  ✅ Displayed   │
                    └─────────────────┘
```

---

## Key API Endpoints

### Backend API (Python - Port 8000)

| Endpoint | Method | File | Description |
|----------|--------|------|-------------|
| `/` | GET | `api/main.py` | API info and welcome message |
| `/docs` | GET | Auto-generated | Interactive Swagger documentation |
| `/api/v1/health` | GET | `api/main.py` | Health check, model status |
| `/api/v1/predict` | POST | `api/main.py` | Image classification endpoint |

### Frontend API (Next.js - Port 3000)

| Endpoint | Method | File | Description |
|----------|--------|------|-------------|
| `/` | GET | `app/page.tsx` | Home page |
| `/api/predict` | POST | `app/api/predict/route.ts` | Proxy to Python backend |

---

## Configuration Files

### Python Backend Configuration

**`ml_backend/requirements.txt`**
- Python package dependencies
- Install: `pip install -r requirements.txt`

**`ml_backend/api/main.py`** (Configuration section)
```python
# Model path
MODEL_PATH = "../exports/run3_v2_best.onnx"

# CORS settings
allow_origins=["http://localhost:3000"]

# Server settings
uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Frontend Configuration

**`.env.local`**
```
PYTHON_API_URL=http://localhost:8000
NEXT_PUBLIC_MODEL_VERSION=v1.0.0-run3-v2
```

**`next.config.ts`**
- Next.js configuration
- Image optimization settings
- Build settings

**`tailwind.config.ts`**
- Tailwind CSS theme
- Custom colors, fonts
- Component styling

---

## Quick Reference

### Where to Find Things

**Want to change...**

| What | File to Edit |
|------|--------------|
| **API endpoint logic** | `ml_backend/api/main.py` |
| **Prediction algorithm** | `ml_backend/api/services/inference_service.py` |
| **Safety rules** | `ml_backend/api/services/safety_classifier.py` |
| **Upload UI design** | `components/sections/AssessmentDemo.tsx` |
| **Classification badges** | `components/ui/badge.tsx` |
| **Backend URL** | `.env.local` |
| **Page layout** | `app/page.tsx` |
| **API proxy logic** | `app/api/predict/route.ts` |
| **Styling/colors** | `tailwind.config.ts` or component files |
| **Model** | Replace `exports/run3_v2_best.onnx` |

### Common Tasks

**Add a new API endpoint (Python):**
1. Edit `ml_backend/api/main.py`
2. Add `@app.get("/api/v1/your-endpoint")`

**Change frontend text:**
1. Edit component in `components/sections/`
2. Save (auto-reloads in dev mode)

**Update the AI model:**
1. Train new model → checkpoint
2. Run `scripts/export_model.py`
3. Replace `exports/run3_v2_best.onnx`
4. Restart backend

**Change upload validation:**
1. Edit `app/api/predict/route.ts`
2. Modify file type/size checks

**Customize safety rules:**
1. Edit `api/services/safety_classifier.py`
2. Adjust confidence thresholds
3. Restart backend

---

## File Naming Conventions

### Python Backend
- **Files:** `snake_case.py` (e.g., `inference_service.py`)
- **Classes:** `PascalCase` (e.g., `InferenceService`)
- **Functions:** `snake_case()` (e.g., `load_model()`)

### Next.js Frontend
- **Components:** `PascalCase.tsx` (e.g., `AssessmentDemo.tsx`)
- **Routes:** `kebab-case/route.ts` (e.g., `predict/route.ts`)
- **Utilities:** `camelCase.ts` (e.g., `utils.ts`)
- **CSS:** `kebab-case.css` (e.g., `globals.css`)

---

## Development Workflow

### Making Changes to Backend

1. Edit Python files in `ml_backend/`
2. Stop backend (`Ctrl+C`)
3. Restart: `python api/main.py`
4. Test: `http://localhost:8000/docs`

### Making Changes to Frontend

1. Edit TypeScript/TSX files
2. Save file (Next.js auto-reloads)
3. Check browser (hot reload)
4. No restart needed!

### Testing End-to-End

1. Both services running
2. Upload test image at `localhost:3000`
3. Check browser console (F12) for errors
4. Check backend terminal for logs
5. Verify prediction appears

---

## Troubleshooting Guide

**Backend won't start:**
- Check `exports/run3_v2_best.onnx` exists
- Verify Python dependencies installed
- Check port 8000 not in use

**Frontend can't connect to backend:**
- Verify backend running (check Terminal 1)
- Check `.env.local` has correct URL
- Restart Next.js after editing `.env.local`

**Predictions not showing:**
- Open browser console (F12) for errors
- Check network tab for failed requests
- Verify image is JPEG/PNG <10MB
- Check backend logs for errors

**Need to debug:**
- **Backend:** Add `print()` statements in Python
- **Frontend:** Add `console.log()` in TypeScript
- **API calls:** Check Network tab in browser DevTools

---

## Additional Resources

**Documentation:**
- FastAPI: https://fastapi.tiangolo.com
- Next.js: https://nextjs.org/docs
- ONNX Runtime: https://onnxruntime.ai
- Tailwind CSS: https://tailwindcss.com

**Project Files:**
- `HOW_TO_RUN.md` - Startup instructions
- `README.md` (backend) - Backend documentation
- `README.md` (frontend) - Frontend documentation

---

*Last updated: February 21, 2026*
