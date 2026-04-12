# Quick Deployment Guide (Step-by-Step)

## 🚀 Deploy in 1 Hour

### Prerequisites
- [ ] GitHub account
- [ ] Vercel account (sign up with GitHub)
- [ ] Render account (sign up with GitHub)

---

## Step 1: Prepare Backend (10 minutes)

### 1.1 Update CORS

Edit `ml_backend/app/main.py`:

```python
# Find this section (around line 20):
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",  # ← Add this line!
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 1.2 Create requirements.txt

```bash
cd ml_backend
pip freeze > requirements.txt
```

Or create manually with:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pillow==10.1.0
numpy==1.24.3
onnxruntime==1.16.3
python-dotenv==1.0.0
```

### 1.3 Test locally one more time

```bash
cd ml_backend
uvicorn app.main:app --reload

# In browser: http://localhost:8000/docs
# Test /health endpoint
```

---

## Step 2: Deploy Backend to Render (15 minutes)

### 2.1 Create GitHub Repository (Backend)

```bash
cd /c/Users/User/Documents/first_year_files/folder_for_jobs/UAV

# Option A: Create single repo for whole project
git init
git add .
git commit -m "Initial commit: UAV Flood Assessment System"

# Create new repo on GitHub: https://github.com/new
# Name: uav-flood-assessment

git remote add origin https://github.com/YOUR_USERNAME/uav-flood-assessment.git
git branch -M main
git push -u origin main
```

### 2.2 Deploy on Render

1. **Go to:** https://render.com
2. **Sign up** with GitHub
3. Click **"New +"** → **"Web Service"**
4. **Connect repository:** `uav-flood-assessment`
5. **Configure:**

```
Name:            uav-flood-api
Region:          Oregon (or Singapore if available)
Branch:          main
Root Directory:  ml_backend              ← Important!
Environment:     Python 3
Build Command:   pip install -r requirements.txt
Start Command:   uvicorn app.main:app --host 0.0.0.0 --port $PORT
Instance Type:   Free
```

6. **Click "Create Web Service"**
7. **Wait 5-10 minutes** (watch build logs)
8. **Copy URL:** `https://uav-flood-api.onrender.com`

### 2.3 Test Backend

Open in browser:
```
https://uav-flood-api.onrender.com/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

✅ **Backend deployed!**

---

## Step 3: Prepare Frontend (10 minutes)

### 3.1 Update API endpoint

Edit `uav-based-flooded-road-assessment-system/app/api/predict/route.ts`:

```typescript
// Around line 10-15, find:
const response = await fetch('http://localhost:8000/api/v1/predict', {

// Replace with:
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const response = await fetch(`${API_URL}/api/v1/predict`, {
```

### 3.2 Test locally with deployed backend

Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=https://uav-flood-api.onrender.com
```

Test:
```bash
cd uav-based-flooded-road-assessment-system
npm run dev
# Open http://localhost:3000
# Click sample image → Should work with deployed backend!
```

### 3.3 Commit changes

```bash
cd /c/Users/User/Documents/first_year_files/folder_for_jobs/UAV
git add .
git commit -m "Frontend: Update API to use environment variable"
git push
```

---

## Step 4: Deploy Frontend to Vercel (15 minutes)

### 4.1 Deploy on Vercel

1. **Go to:** https://vercel.com
2. **Sign up** with GitHub
3. Click **"Add New Project"**
4. **Import:** `uav-flood-assessment` repository
5. **Configure:**

```
Framework Preset:  Next.js (auto-detected)
Root Directory:    uav-based-flooded-road-assessment-system  ← Important!
Build Command:     npm run build
Output Directory:  .next
Install Command:   npm install
```

6. **Add Environment Variable:**

Click "Environment Variables" → Add:
```
Key:   NEXT_PUBLIC_API_URL
Value: https://uav-flood-api.onrender.com
```
(Use YOUR actual Render URL!)

7. **Click "Deploy"**
8. **Wait 3-5 minutes**
9. **Copy URL:** `https://uav-flood-assessment.vercel.app`

### 4.2 Test Frontend

1. Open: `https://uav-flood-assessment.vercel.app`
2. Click a sample image
3. Wait ~30s (first request wakes backend)
4. Verify prediction works!

✅ **Frontend deployed!**

---

## Step 5: Final Configuration (10 minutes)

### 5.1 Update Backend CORS (Important!)

Now that you have the Vercel URL, update CORS:

Edit `ml_backend/app/main.py`:
```python
allow_origins=[
    "http://localhost:3000",
    "https://uav-flood-assessment.vercel.app",  # ← Your actual URL
    "https://*.vercel.app",
]
```

Commit and push:
```bash
git add ml_backend/app/main.py
git commit -m "Update CORS for production Vercel URL"
git push
```

Render will auto-redeploy (~3 minutes).

### 5.2 Set Up Keep-Alive (Optional but Recommended)

**Option A: UptimeRobot (Free, Recommended)**

1. Go to https://uptimerobot.com
2. Sign up (free)
3. Add New Monitor:
   - Type: HTTP(s)
   - URL: `https://uav-flood-api.onrender.com/api/v1/health`
   - Interval: 5 minutes
4. Save

Now backend stays warm 24/7!

**Option B: Frontend Keep-Alive**

Add to `uav-based-flooded-road-assessment-system/app/layout.tsx`:

```typescript
'use client';

import { useEffect } from 'react';

export default function RootLayout({ children }) {
  useEffect(() => {
    // Ping backend every 10 minutes to keep warm
    const interval = setInterval(async () => {
      try {
        await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/health`);
      } catch (err) {
        console.log('Keep-alive ping failed');
      }
    }, 10 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <html>
      <body>{children}</body>
    </html>
  );
}
```

---

## Step 6: Test Full System (5 minutes)

### 6.1 Test Checklist

Visit: `https://uav-flood-assessment.vercel.app`

- [ ] Page loads correctly
- [ ] Sample images visible (3 samples)
- [ ] Click "Clear Road" → Prediction works
- [ ] Click "Moderate Flood" → Different prediction
- [ ] Click "Severe Flood" → Impassable result
- [ ] Upload custom image → Works
- [ ] Download JSON → File downloads
- [ ] Map loads correctly
- [ ] Mobile responsive (test on phone)
- [ ] No console errors (F12 → Console)

### 6.2 Test Backend Directly

API Docs: `https://uav-flood-api.onrender.com/docs`

- [ ] Health endpoint: `/api/v1/health` → Returns healthy
- [ ] Try upload in docs UI → Works
- [ ] Classes endpoint: `/api/v1/classes` → Returns 3 classes

---

## Troubleshooting Common Issues

### Issue: CORS Error

**Symptom:** Console shows "blocked by CORS policy"

**Fix:**
1. Check `ml_backend/app/main.py` has correct Vercel URL
2. Push changes to GitHub
3. Wait for Render to redeploy (~3 min)
4. Hard refresh frontend (Ctrl+Shift+R)

---

### Issue: "Model not found" on Render

**Symptom:** Backend logs show `FileNotFoundError: models/...`

**Fix:**
```bash
# Ensure model is committed to git
cd ml_backend
git lfs install  # If model >100MB
git add models/efficientnet_b0_flood_classifier.onnx
git commit -m "Add ONNX model"
git push
```

---

### Issue: Backend takes 30+ seconds

**Symptom:** First request after inactivity is slow

**This is normal!** Free tier sleeps after 15 min.

**Solutions:**
1. Set up UptimeRobot (keeps it warm)
2. Add loading message: "Waking backend... (30s)"
3. Upgrade to Render paid ($7/mo, instant wake)

---

### Issue: Environment variable not working

**Symptom:** Frontend still uses localhost:8000

**Fix:**
1. Vercel Dashboard → Settings → Environment Variables
2. Verify: `NEXT_PUBLIC_API_URL` (must have `NEXT_PUBLIC_` prefix!)
3. Redeploy: Deployments → ⋯ → Redeploy

---

## Final URLs

### Share These with Your Thesis Committee

```
📱 Live Demo:
https://uav-flood-assessment.vercel.app

🔧 API Documentation:
https://uav-flood-api.onrender.com/docs

📦 GitHub Repository:
https://github.com/YOUR_USERNAME/uav-flood-assessment

📊 System Status:
https://uav-flood-api.onrender.com/api/v1/health
```

---

## Deployment Complete! ✅

**What You've Deployed:**

✅ **Frontend (Vercel):**
- Next.js app with interactive demo
- Sample images gallery
- Real-time AI predictions
- Interactive map visualization
- Results export (JSON)
- Mobile responsive

✅ **Backend (Render):**
- FastAPI REST API
- ONNX model inference
- Image processing
- CORS configured
- Auto-scaling

✅ **Total Cost:** $0/month (free tier)

✅ **Performance:**
- Frontend: Instant (global CDN)
- Backend: ~2-3s (warm), ~30s (cold start)

---

## Next Steps

### For Thesis Defense

1. **Test thoroughly** (all features work?)
2. **Prepare backup** (video recording if live demo fails)
3. **Document URLs** (add to thesis document)
4. **Practice demo flow** (sample image → prediction → download)

### Optional Improvements

1. **Custom Domain:**
   - Vercel: `floodassessment.plm.edu.ph`
   - Render: `api.floodassessment.plm.edu.ph`

2. **Analytics:**
   - Vercel Analytics (free)
   - Google Analytics

3. **Error Tracking:**
   - Sentry.io (free tier)

4. **Performance:**
   - Optimize images (WebP format)
   - Enable caching

---

## Deployment Timeline

| Step | Duration | Status |
|------|----------|--------|
| Prepare Backend | 10 min | ✅ |
| Deploy Backend (Render) | 15 min | ✅ |
| Prepare Frontend | 10 min | ✅ |
| Deploy Frontend (Vercel) | 15 min | ✅ |
| Final Configuration | 10 min | ✅ |
| **TOTAL** | **60 min** | **✅ DONE** |

---

**Congratulations! Your system is now live! 🎉**

Share the URLs with your thesis committee and prepare for your defense! 🎓

---

**Quick Start Guide Version:** 1.0
**Last Updated:** February 22, 2026
**Estimated Time:** 1 hour
**Cost:** $0 (free tier)
