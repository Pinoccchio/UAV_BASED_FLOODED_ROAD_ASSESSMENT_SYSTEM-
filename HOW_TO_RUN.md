# How to Run the UAV Flood Assessment System

## Overview

This system consists of **two separate services** that must both be running:

1. **Python Backend (FastAPI)** - Port 8000 - AI model inference
2. **Next.js Frontend (React)** - Port 3000 - User interface

Both services communicate with each other to provide the complete functionality.

---

## Prerequisites

Before running, ensure you have:

- ✅ Python 3.10+ installed
- ✅ Node.js 18+ installed
- ✅ All dependencies installed:
  - Backend: `pip install -r ml_backend/requirements.txt`
  - Frontend: `npm install` (in the frontend directory)
- ✅ ONNX model exported at: `ml_backend/exports/run3_v2_best.onnx`

---

## Starting the System

### Step 1: Start the Backend (Terminal 1)

Open a terminal/PowerShell window:

```bash
cd C:\Users\User\Documents\first_year_files\folder_for_jobs\UAV\ml_backend\api
python main.py
```

**Expected Output:**
```
============================================================
UAV Flood Passability API - Loading Model...
============================================================
[OK] Model loaded from: C:\Users\User\Documents\first_year_files\folder_for_jobs\UAV\ml_backend\exports\run3_v2_best.onnx
============================================================
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
============================================================
UAV Flood Passability API - Starting...
============================================================
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

✅ **Backend is now running on http://localhost:8000**

**Test it:** Open browser to `http://localhost:8000` - you should see:
```json
{"message":"UAV Flood Passability API","version":"1.0.0","docs":"/docs","health":"/api/v1/health"}
```

**⚠️ IMPORTANT:** Keep this terminal window open! Don't close it or press Ctrl+C.

---

### Step 2: Start the Frontend (Terminal 2)

Open a **NEW** terminal/PowerShell window (keep the first one running):

```bash
cd C:\Users\User\Documents\first_year_files\folder_for_jobs\UAV\uav-based-flooded-road-assessment-system
npm run dev
```

**Expected Output:**
```
  ▲ Next.js 16.1.6
  - Local:        http://localhost:3000
  - Network:      http://192.168.x.x:3000

 ✓ Starting...
 ✓ Ready in 2.3s
```

✅ **Frontend is now running on http://localhost:3000**

**⚠️ IMPORTANT:** Keep this terminal window open too!

---

### Step 3: Use the System

1. **Open your browser:** `http://localhost:3000`
2. **Navigate to:** "Assessment Demo" section (scroll down or use navigation)
3. **Upload an image:** Click the upload area, select a flood image (JPEG/PNG)
4. **View results:** The AI will analyze the image and show:
   - Passability classification (Passable, Limited, Impassable)
   - Confidence score
   - Vehicle recommendations
   - Safety warnings (if applicable)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Browser                         │
│                 http://localhost:3000                   │
└────────────────────┬────────────────────────────────────┘
                     │ Uploads flood image
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Next.js Frontend (Port 3000)               │
│  - User interface                                       │
│  - File upload handling                                 │
│  - Results display                                      │
└────────────────────┬────────────────────────────────────┘
                     │ POST /api/predict
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Python Backend API (Port 8000)                  │
│  - FastAPI server                                       │
│  - ONNX model inference                                 │
│  - Safety classifier                                    │
│  - Image preprocessing                                  │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
              Returns prediction JSON
```

---

## Troubleshooting

### Port Already in Use Error

**Error:**
```
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)
```

**Solution:** Kill the process using port 8000:

1. Find the process:
   ```bash
   netstat -ano | findstr :8000
   ```

2. Check what it is:
   ```bash
   tasklist | findstr <PID_NUMBER>
   ```

3. Kill it (if it's python.exe):
   ```bash
   taskkill /PID <PID_NUMBER> /F
   ```

4. Restart the backend:
   ```bash
   python main.py
   ```

---

### Backend Not Loading Model

**Error:** Model file not found

**Solution:** Export the model first:
```bash
cd C:\Users\User\Documents\first_year_files\folder_for_jobs\UAV\ml_backend\scripts
python export_model.py
```

This will create: `ml_backend/exports/run3_v2_best.onnx`

---

### Frontend Can't Connect to Backend

**Error:** "Failed to process image" or network errors

**Checklist:**
1. ✅ Backend is running (check Terminal 1)
2. ✅ Backend responds at `http://localhost:8000/api/v1/health`
3. ✅ `.env.local` file exists with:
   ```
   PYTHON_API_URL=http://localhost:8000
   ```
4. ✅ Restart the frontend after creating `.env.local`

---

### CORS Errors

**Error:** CORS policy blocking requests

**Solution:** The backend is already configured to allow `localhost:3000`. If you change the frontend port, update `api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your port here
    ...
)
```

---

## Quick Reference Commands

### Start Backend
```bash
cd C:\Users\User\Documents\first_year_files\folder_for_jobs\UAV\ml_backend\api
python main.py
```

### Start Frontend
```bash
cd C:\Users\User\Documents\first_year_files\folder_for_jobs\UAV\uav-based-flooded-road-assessment-system
npm run dev
```

### Stop Services
- Press `Ctrl+C` in each terminal window

### Check if Backend is Running
```bash
curl http://localhost:8000/api/v1/health
```

Or open in browser: `http://localhost:8000/api/v1/health`

### Check if Frontend is Running
Open browser: `http://localhost:3000`

---

## API Endpoints Reference

### Backend API (Port 8000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/docs` | GET | Interactive API documentation (Swagger) |
| `/api/v1/health` | GET | Health check |
| `/api/v1/predict` | POST | Image classification endpoint |

### Frontend (Port 3000)

| Endpoint | Description |
|----------|-------------|
| `/` | Home page |
| `/api/predict` | Proxy to backend (used internally) |

---

## Testing the Backend Directly

You can test the backend API without the frontend using `curl` or Postman:

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Predict (with image file)
curl -X POST http://localhost:8000/api/v1/predict \
  -F "image=@path/to/your/image.jpg"
```

Or visit the interactive docs: `http://localhost:8000/docs`

---

## Development Workflow

### Typical Development Session

1. **Morning:**
   - Start backend (Terminal 1)
   - Start frontend (Terminal 2)
   - Open `http://localhost:3000` in browser

2. **During Development:**
   - Backend: Restart manually after code changes
   - Frontend: Auto-reloads on file changes (hot reload)

3. **End of Day:**
   - Press `Ctrl+C` in both terminals to stop services

---

## Performance Notes

- **Backend startup:** ~2-5 seconds (loads ONNX model)
- **Frontend startup:** ~2-3 seconds
- **Inference time:** ~200-500ms per image (depends on CPU/GPU)
- **Total response time:** <2 seconds from upload to result

---

## Production Deployment (Future)

For production deployment:

1. Use environment variables for configuration
2. Enable HTTPS
3. Set up reverse proxy (nginx)
4. Use Docker containers
5. Configure proper CORS origins
6. Add rate limiting
7. Set up monitoring and logging

See `DEPLOYMENT.md` for detailed production setup.

---

## Support

**Issues?**
- Check the troubleshooting section above
- Review backend logs in Terminal 1
- Review frontend logs in Terminal 2
- Check browser console for errors (F12)

**Model Info:**
- **Architecture:** EfficientNet-B0
- **Classes:** 3 (Impassable, Limited Passability, Passable)
- **Test Accuracy:** 79.56%
- **Model Version:** Run #3 v2

---

## Summary Checklist

Before using the system, verify:

- [ ] Backend terminal is running and shows "Uvicorn running on http://0.0.0.0:8000"
- [ ] Frontend terminal is running and shows "Ready in X.Xs"
- [ ] Browser opens `http://localhost:3000` successfully
- [ ] Can see the UAV Flood Assessment website
- [ ] Can navigate to "Assessment Demo" section
- [ ] Upload button is visible and clickable
- [ ] Test image upload works and returns prediction

**Both terminals must stay open while using the system!**

---

*Last updated: February 21, 2026*
