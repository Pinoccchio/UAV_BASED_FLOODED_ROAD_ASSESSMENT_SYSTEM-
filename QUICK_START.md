# Quick Start Guide - UAV Flood Assessment System

## Current Status ✅

Both services are **RUNNING** and ready to use:

- **Backend**: http://localhost:8000 (Healthy, model loaded)
- **Frontend**: http://localhost:3000 (Ready)

## Access the Application

1. Open your browser
2. Go to: **http://localhost:3000**
3. Scroll down to the **"Assessment Demo"** section
4. Upload a flood image or use the sample scenarios

## Test the System

### Option 1: Upload Your Own Image
1. Click the upload area in the demo section
2. Select a JPEG or PNG flood image (max 10MB)
3. Wait 1-2 seconds for analysis
4. View results:
   - Classification (Passable/Limited/Impassable)
   - Confidence level (High/Medium/Low)
   - Vehicle recommendations
   - Safety warnings (if applicable)

### Option 2: Use Sample Images
Use the provided test images in `ml_backend/data/processed/test/`:
- `impassable/` - Dangerous flooded roads
- `limited_passability/` - Moderate flooding
- `passable/` - Low-level flooding

### Option 3: Test via API Directly

**Backend Health Check:**
```bash
curl http://localhost:8000/api/v1/health
```

**Upload Image for Prediction:**
```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -F "image=@path/to/your/flood/image.jpg"
```

**Frontend API Route:**
```bash
curl -X POST http://localhost:3000/api/predict \
  -F "image=@path/to/your/flood/image.jpg"
```

## Understanding the Results

### Classification Classes:
1. **Passable** (Green) - Road is clear, all vehicles can pass
2. **Limited Passability** (Yellow) - Only high-clearance vehicles
3. **Impassable** (Red) - Road is dangerous, do not attempt

### Safety Features:
- **Conservative Mode**: Downgrades uncertain predictions for safety
- **Warning Messages**: Shows when safety measures are applied
- **Original Prediction**: Displays if classification was adjusted

### Example Output:
```json
{
  "prediction": {
    "class": "impassable",
    "confidence": 0.8302,
    "confidence_level": "high"
  },
  "safety_info": {
    "safety_applied": false,
    "warning_message": "⚠️ MODEL TRAINED ON US DATA - Validate with local ground knowledge..."
  },
  "vehicle_recommendations": {
    "civilian_sedan": false,
    "high_clearance_suv": false,
    "heavy_vehicle": false,
    "emergency_vehicle": true
  }
}
```

## If Services Are Not Running

### Start Backend:
```bash
cd ml_backend/api
source ../venv/Scripts/activate  # On Windows: ../venv/Scripts/activate
python main.py
```

Expected output:
```
============================================================
UAV Flood Passability API - Loading Model...
============================================================
[OK] Model loaded from: ../exports/run3_v2_best.onnx
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Start Frontend:
```bash
cd uav-based-flooded-road-assessment-system
npm run dev
```

Expected output:
```
▲ Next.js 16.1.6
- Local:   http://localhost:3000
✓ Ready in 2.1s
```

## Troubleshooting

### Backend Issues:

**Model not loading:**
- Check that `ml_backend/exports/run3_v2_best.onnx` exists (18 MB)
- Verify virtual environment is activated

**Port 8000 already in use:**
```bash
# Windows
taskkill /F /IM python.exe
# Then restart
```

### Frontend Issues:

**Port 3000 already in use:**
```bash
# Kill the process or use different port
npm run dev -- -p 3001
```

**API connection failed:**
- Verify backend is running on port 8000
- Check `.env.local` has `PYTHON_API_URL=http://localhost:8000`

## API Endpoints

### Backend (FastAPI)
- `GET  /` - Root endpoint
- `GET  /api/v1/health` - Health check
- `POST /api/v1/predict` - Single image prediction
- `POST /api/v1/batch-predict` - Batch predictions (max 10)
- `GET  /api/v1/classes` - Available classes info
- `GET  /docs` - Interactive API documentation (Swagger UI)

### Frontend (Next.js)
- `POST /api/predict` - Proxy to Python backend

## Performance Expectations

- **Inference Time**: <500ms per image (CPU)
- **Total Latency**: <2 seconds (including network)
- **Max File Size**: 10 MB
- **Supported Formats**: JPEG, PNG

## Model Information

- **Architecture**: EfficientNet-B0
- **Classes**: 3 (Impassable, Limited Passability, Passable)
- **Training Data**: RescueNet + FloodNet (US-based)
- **Test Accuracy**: 79.56% (with safety measures)
- **Impassable Recall**: 83.02%
- **Safety Improvement**: 22.64% better dangerous road detection

## Important Notes

⚠️ **Model Limitations:**
- Trained on US flood imagery
- Expected 10-15% accuracy drop in other regions
- Always validate with local ground knowledge
- Conservative safety measures may over-predict danger

🛡️ **Safety Features:**
- Automatic downgrading of uncertain predictions
- Warning messages for low-confidence results
- Shows original prediction when adjusted

## Need Help?

- **Full Documentation**: See `INTEGRATION_COMPLETE.md`
- **Backend Code**: `ml_backend/api/`
- **Frontend Code**: `uav-based-flooded-road-assessment-system/`
- **Model Export**: `ml_backend/scripts/export_model.py`

## What's Next?

Once you've tested the system:

1. **Collect Philippine Data**: Improve accuracy for local use
2. **Production Deployment**: Docker, HTTPS, monitoring
3. **Mobile App**: React Native or Flutter integration
4. **Real-time Processing**: WebSocket for live UAV feeds
5. **Geographic Expansion**: Train on diverse flood datasets

---

**System is READY! Start testing at http://localhost:3000** 🚀
