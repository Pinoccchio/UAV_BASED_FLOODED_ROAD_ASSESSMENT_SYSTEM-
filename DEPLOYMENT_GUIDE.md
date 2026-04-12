# Complete Deployment Guide: Frontend (Vercel) + Backend

## Overview

**Frontend:** Next.js app → Deploy to **Vercel** (free tier)
**Backend:** Python FastAPI → Deploy to **Render / Railway / Fly.io** (free tier options)

---

## Architecture After Deployment

```
┌─────────────────────────────────────────────────────┐
│                    USERS                            │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  FRONTEND (Vercel)                                  │
│  https://uav-flood-assessment.vercel.app            │
│  • Next.js static/SSR pages                         │
│  • Sample images (served from /public)              │
│  • Interactive map (Leaflet)                        │
└─────────────────────────────────────────────────────┘
                        ↓ API calls
┌─────────────────────────────────────────────────────┐
│  BACKEND (Render/Railway/Fly.io)                    │
│  https://uav-flood-api.onrender.com                 │
│  • FastAPI REST API                                 │
│  • ONNX model inference                             │
│  • Image processing                                 │
└─────────────────────────────────────────────────────┘
```

---

## Part 1: Backend Deployment

### Option A: Render.com (RECOMMENDED - Easiest)

#### Why Render?
- ✅ **Free tier:** 750 hours/month (enough for demo)
- ✅ **Easy setup:** Auto-deploy from GitHub
- ✅ **Persistent storage:** For model files
- ✅ **Logs:** Good debugging tools
- ⚠️ **Cold starts:** ~30s if inactive for 15 min (acceptable for demo)

#### Step 1: Prepare Backend for Deployment

**1.1 Create `requirements.txt`** (if not exists)

```bash
cd ml_backend
pip freeze > requirements.txt
```

Or create manually:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pillow==10.1.0
numpy==1.24.3
onnxruntime==1.16.3
python-dotenv==1.0.0
```

**1.2 Create `render.yaml`** (optional, for easier config)

```yaml
services:
  - type: web
    name: uav-flood-api
    env: python
    region: oregon
    plan: free
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: ENVIRONMENT
        value: production
```

**1.3 Update `app/main.py` - Fix CORS for production**

```python
from fastapi.middleware.cors import CORSMiddleware

# BEFORE (local only):
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    ...
)

# AFTER (production):
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local dev
        "https://uav-flood-assessment.vercel.app",  # Production frontend
        "https://*.vercel.app",  # All Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**1.4 Check model file path**

Ensure `app/main.py` uses relative path:

```python
# GOOD (works in production):
MODEL_PATH = Path(__file__).parent.parent / "models" / "efficientnet_b0_flood_classifier.onnx"

# BAD (absolute path won't work):
MODEL_PATH = "C:/Users/User/Documents/.../model.onnx"
```

**1.5 Create `.env.example`** (document env vars)

```env
ENVIRONMENT=production
PORT=8000
```

#### Step 2: Deploy to Render

**2.1 Push to GitHub**

```bash
cd /c/Users/User/Documents/first_year_files/folder_for_jobs/UAV
git init
git add .
git commit -m "Initial commit: UAV Flood Assessment System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/uav-flood-assessment.git
git push -u origin main
```

**2.2 Create Render Account**

1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"

**2.3 Configure Service**

```
Name:            uav-flood-api
Region:          Oregon (or closest to Philippines: Singapore if available)
Branch:          main
Root Directory:  ml_backend
Environment:     Python 3
Build Command:   pip install -r requirements.txt
Start Command:   uvicorn app.main:app --host 0.0.0.0 --port $PORT
Instance Type:   Free
```

**2.4 Add Environment Variables**

In Render dashboard → Environment:
```
PYTHON_VERSION=3.11.0
ENVIRONMENT=production
```

**2.5 Deploy**

- Click "Create Web Service"
- Wait 5-10 minutes for build
- Check logs for errors

**2.6 Test Backend**

```bash
# Check health endpoint
curl https://uav-flood-api.onrender.com/api/v1/health

# Expected response:
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

---

### Option B: Railway.app (Alternative)

#### Why Railway?
- ✅ **Free tier:** $5/month credit (500 hours)
- ✅ **Faster cold starts:** ~10s
- ✅ **Better performance:** More resources on free tier
- ⚠️ **Requires credit card:** For verification

#### Quick Setup

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
cd ml_backend
railway init

# Deploy
railway up
```

---

### Option C: Fly.io (Advanced)

#### Why Fly.io?
- ✅ **Global deployment:** Edge locations worldwide
- ✅ **Fast cold starts:** Instant wake
- ⚠️ **More complex:** Requires Dockerfile

#### Dockerfile for FastAPI

Create `ml_backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Expose port
EXPOSE 8080

# Run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Deploy:
```bash
fly launch
fly deploy
```

---

## Part 2: Frontend Deployment (Vercel)

### Step 1: Prepare Frontend

**1.1 Update API endpoint for production**

Edit `uav-based-flooded-road-assessment-system/.env.local`:

```env
# For local development
NEXT_PUBLIC_API_URL=http://localhost:8000

# For production (will override via Vercel env vars)
```

**1.2 Update `app/api/predict/route.ts`**

```typescript
// BEFORE (hardcoded):
const response = await fetch('http://localhost:8000/api/v1/predict', {
  method: 'POST',
  body: formData,
});

// AFTER (use environment variable):
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const response = await fetch(`${API_URL}/api/v1/predict`, {
  method: 'POST',
  body: formData,
});
```

**1.3 Optimize sample images** (optional but recommended)

Sample images are ~19MB total. Optimize to reduce bandwidth:

```bash
cd uav-based-flooded-road-assessment-system/public/sample-images

# Install ImageMagick or use online tools
# Compress to ~70% quality
mogrify -quality 70 -strip *.jpg

# Or convert to WebP (smaller)
for img in *.jpg; do
  cwebp -q 70 "$img" -o "${img%.jpg}.webp"
done
```

**1.4 Create `vercel.json`** (optional config)

```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["sin1"],
  "env": {
    "NEXT_PUBLIC_API_URL": "@api-url"
  }
}
```

### Step 2: Deploy to Vercel

**2.1 Push frontend to GitHub**

```bash
cd uav-based-flooded-road-assessment-system
git init
git add .
git commit -m "Frontend: UAV Flood Assessment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/uav-flood-frontend.git
git push -u origin main
```

**2.2 Connect to Vercel**

1. Go to https://vercel.com
2. Sign up with GitHub
3. Click "Add New Project"
4. Import your frontend repository
5. Configure:

```
Framework Preset: Next.js
Root Directory: ./
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

**2.3 Add Environment Variables**

In Vercel dashboard → Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=https://uav-flood-api.onrender.com
```

(Use your actual backend URL from Render/Railway/Fly.io)

**2.4 Deploy**

- Click "Deploy"
- Wait 2-5 minutes
- Vercel will give you a URL: `https://uav-flood-assessment.vercel.app`

**2.5 Test Deployment**

1. Visit your Vercel URL
2. Click a sample image
3. Check browser console for API errors
4. Verify prediction works

---

## Part 3: Post-Deployment Configuration

### 3.1 Update Backend CORS

Now that you have the Vercel URL, update backend CORS:

**In `ml_backend/app/main.py`:**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://uav-flood-assessment.vercel.app",  # Your actual Vercel URL
        "https://*.vercel.app",  # All Vercel preview URLs
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Push to GitHub → Render auto-redeploys.

### 3.2 Custom Domain (Optional)

**For Frontend (Vercel):**
1. Vercel Dashboard → Domains
2. Add custom domain (e.g., `floodassessment.com`)
3. Update DNS records as instructed

**For Backend (Render):**
1. Render Dashboard → Settings → Custom Domain
2. Add domain (e.g., `api.floodassessment.com`)
3. Update DNS records

### 3.3 SSL/HTTPS

- ✅ Both Vercel and Render provide **automatic HTTPS**
- ✅ No configuration needed
- ✅ Certificates auto-renewed

---

## Part 4: Performance Optimization

### 4.1 Frontend Optimizations

**Optimize Images:**
```bash
# Already in public/sample-images/
# Compress to WebP format (50-70% smaller)
npm install sharp
node scripts/optimize-images.js
```

**Enable Caching:**
```typescript
// In next.config.js
module.exports = {
  images: {
    formats: ['image/webp'],
  },
  async headers() {
    return [
      {
        source: '/sample-images/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
};
```

### 4.2 Backend Optimizations

**Enable Response Compression:**
```python
# In app/main.py
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

**Add Caching for Model:**
```python
# Model is already loaded once on startup
# Ensure it's not reloaded per request (already implemented)
```

### 4.3 Handle Cold Starts

**For Render (30s cold start):**

Add a "keep-alive" ping from frontend:

```typescript
// In app/layout.tsx or a component
useEffect(() => {
  // Ping backend every 10 minutes to keep it warm
  const interval = setInterval(async () => {
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/health`);
    } catch (err) {
      console.log('Keep-alive ping failed');
    }
  }, 10 * 60 * 1000); // 10 minutes

  return () => clearInterval(interval);
}, []);
```

**Better: Use UptimeRobot (Free)**
1. Sign up at https://uptimerobot.com
2. Add monitor: `https://uav-flood-api.onrender.com/api/v1/health`
3. Check interval: 5 minutes
4. Keeps backend warm automatically

---

## Part 5: Monitoring & Debugging

### 5.1 Vercel Logs

```bash
# Install Vercel CLI
npm install -g vercel

# View logs
vercel logs uav-flood-assessment
```

Or in dashboard: Deployments → View Logs

### 5.2 Render Logs

In Render dashboard:
- Logs tab (real-time)
- Metrics tab (CPU, memory)

### 5.3 Error Tracking (Optional)

**Add Sentry for error monitoring:**

```bash
npm install @sentry/nextjs
npx @sentry/wizard@latest -i nextjs
```

---

## Part 6: Cost Breakdown

### Free Tier Limits

**Vercel (Frontend):**
- ✅ Unlimited bandwidth
- ✅ 100 GB-hours compute/month
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Preview deployments
- **Cost:** FREE ✅

**Render (Backend):**
- ✅ 750 hours/month (enough for 24/7)
- ✅ 512 MB RAM
- ✅ 0.1 CPU
- ⚠️ Sleeps after 15 min inactivity
- **Cost:** FREE ✅

**Total Monthly Cost: $0** 🎉

---

## Part 7: Deployment Checklist

### Pre-Deployment

#### Backend:
- [ ] `requirements.txt` created
- [ ] CORS origins updated with Vercel URL
- [ ] Model file path is relative (not absolute)
- [ ] Environment variables documented
- [ ] Health endpoint works: `/api/v1/health`
- [ ] Test predict endpoint locally

#### Frontend:
- [ ] API URL uses environment variable
- [ ] Sample images optimized (<5MB each)
- [ ] All disclaimers in place
- [ ] Mobile responsive tested
- [ ] No console errors

### Deployment

#### Backend:
- [ ] Pushed to GitHub
- [ ] Render/Railway account created
- [ ] Service configured and deployed
- [ ] Health endpoint accessible
- [ ] Test prediction from Postman/curl

#### Frontend:
- [ ] Pushed to GitHub
- [ ] Vercel account created
- [ ] Environment variable set (NEXT_PUBLIC_API_URL)
- [ ] Deployed successfully
- [ ] Test sample images work
- [ ] Map loads correctly

### Post-Deployment

- [ ] Update backend CORS with actual Vercel URL
- [ ] Test full flow (sample image → prediction → map)
- [ ] Check mobile responsiveness
- [ ] Set up UptimeRobot (keep backend warm)
- [ ] Share URLs with thesis committee
- [ ] Add custom domain (optional)

---

## Part 8: Troubleshooting

### Issue 1: CORS Error

**Symptom:**
```
Access to fetch at 'https://api.example.com' from origin 'https://frontend.vercel.app'
has been blocked by CORS policy
```

**Solution:**
Update `ml_backend/app/main.py`:
```python
allow_origins=["https://your-actual-vercel-url.vercel.app"]
```

### Issue 2: Cold Start Timeout

**Symptom:**
First prediction after 15 min takes 30-60 seconds

**Solutions:**
1. Add loading message: "Waking up backend (30s)..."
2. Use UptimeRobot to keep warm
3. Upgrade to Render paid plan ($7/mo, no sleep)

### Issue 3: Model File Not Found

**Symptom:**
```
FileNotFoundError: models/efficientnet_b0_flood_classifier.onnx
```

**Solution:**
Ensure model file is committed to GitHub:
```bash
cd ml_backend
git add models/efficientnet_b0_flood_classifier.onnx
git commit -m "Add ONNX model file"
git push
```

### Issue 4: Large Deployment Size

**Symptom:**
Deployment fails due to size limit

**Solutions:**
1. Add `.gitignore` to exclude unnecessary files:
```
ml_backend/venv/
ml_backend/__pycache__/
ml_backend/.pytest_cache/
*.pyc
.env
```

2. Optimize model file (if >100MB):
```python
# Quantize ONNX model to reduce size
# (Advanced - may reduce accuracy slightly)
```

### Issue 5: Environment Variable Not Working

**Symptom:**
Frontend still uses localhost:8000

**Solution:**
1. Check Vercel env var name: Must be `NEXT_PUBLIC_API_URL`
2. Redeploy after adding env var (not automatic)
3. Check in browser console: `console.log(process.env.NEXT_PUBLIC_API_URL)`

---

## Part 9: Production URLs

### Example Final URLs

**Frontend (Vercel):**
```
Production:  https://uav-flood-assessment.vercel.app
Preview:     https://uav-flood-assessment-git-main-username.vercel.app
Custom:      https://floodassessment.plm.edu.ph (if configured)
```

**Backend (Render):**
```
Production:  https://uav-flood-api.onrender.com
Health:      https://uav-flood-api.onrender.com/api/v1/health
Docs:        https://uav-flood-api.onrender.com/docs
Custom:      https://api.floodassessment.plm.edu.ph (if configured)
```

---

## Part 10: Thesis Defense Preparation

### What to Show During Defense

**1. Live Demo:**
- Open production URL: `https://uav-flood-assessment.vercel.app`
- Click sample image → Show real-time AI prediction
- Upload custom image (have test images ready)
- Show GPS features (upload phone photo with location)
- Download results JSON

**2. Technical Architecture:**
- Show deployment diagram (frontend on Vercel, backend on Render)
- Explain CORS, API communication
- Discuss free tier limitations (cold starts)

**3. Monitoring:**
- Show Render logs (prove it's working)
- Show Vercel analytics (if traffic)
- Demonstrate error handling

### Backup Plan

**If live demo fails:**
- Have **video recording** of working demo
- Have **screenshots** of successful predictions
- Have **exported JSON files** ready to show
- Explain: "Due to free tier cold start (30s), I have a backup recording"

---

## Part 11: Future Scaling (Post-Thesis)

### When Traffic Increases

**Frontend (Vercel):**
- ✅ Auto-scales infinitely
- ✅ No action needed

**Backend (Render/Railway):**
- Upgrade to paid plan: $7-25/month
- Or migrate to AWS/GCP with autoscaling

### For Production Use

**Recommended Stack:**
```
Frontend:  Vercel (remains same)
Backend:   AWS Lambda + API Gateway (serverless)
Model:     AWS SageMaker or Azure ML
Database:  PostgreSQL (for prediction history)
Storage:   S3 (for uploaded images)
CDN:       CloudFront (for sample images)
```

**Estimated Cost:** $50-100/month for 10,000 predictions

---

## Summary: Deployment Steps (TL;DR)

### Backend (30 minutes)
```bash
1. Update CORS in app/main.py
2. Create requirements.txt
3. Push to GitHub
4. Sign up for Render.com
5. Create Web Service → Connect GitHub repo
6. Wait for deploy → Test health endpoint
```

### Frontend (20 minutes)
```bash
1. Update API URL to use env var
2. Push to GitHub
3. Sign up for Vercel.com
4. Import repository
5. Add env var: NEXT_PUBLIC_API_URL
6. Deploy → Test sample images
```

### Post-Deployment (10 minutes)
```bash
1. Update backend CORS with Vercel URL
2. Test full flow
3. Set up UptimeRobot (optional)
4. Share URLs with thesis committee
```

**Total Time:** ~1 hour
**Total Cost:** $0 ✅

---

## Final URLs to Share

**For Thesis Committee:**

```
System Name: UAV-Based Flood Road Assessment System
Frontend:    https://uav-flood-assessment.vercel.app
API Docs:    https://uav-flood-api.onrender.com/docs
GitHub:      https://github.com/YOUR_USERNAME/uav-flood-assessment
```

---

**Deployment Guide Version:** 1.0
**Last Updated:** February 22, 2026
**Status:** ✅ Ready for deployment
