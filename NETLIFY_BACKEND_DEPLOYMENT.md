# Netlify + Backend API Deployment Guide

## 🌐 Current Setup

**Frontend (www.realdiag.com):**
- ✅ Deployed on Netlify
- ✅ Auto-deploys from GitHub main branch
- ✅ DNS configured: www.realdiag.com → Netlify

**Backend API (NEW - needs deployment):**
- ⏳ Contains medication safety features
- ⏳ EMR integration endpoints
- ⏳ Needs separate hosting (Netlify doesn't support FastAPI)

---

## 🚀 Deploy Backend API

### **Option 1: Render.com** (Recommended - Free tier available)

1. **Sign up**: https://render.com
2. **New Web Service** → Connect GitHub repo
3. **Configure**:
   ```
   Name: realdiag-api
   Region: US East (or closest to users)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
4. **Environment Variables**:
   ```
   FHIR_BASE_URL=<your-emr-fhir-url>
   FHIR_AUTH_TOKEN=<your-token>
   ```
5. **Deploy** → Get URL: `https://realdiag-api.onrender.com`

### **Option 2: Railway.app** (Also Free tier)

1. **Sign up**: https://railway.app
2. **New Project** → Deploy from GitHub
3. **Select** `RealDiag-Software` repo
4. **Configure**:
   ```
   Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
5. **Add Domain**: `api.realdiag.com` (configure DNS)

### **Option 3: Fly.io** (Docker-based)

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy
cd /workspaces/RealDiag-Software/backend
fly launch --name realdiag-api
fly deploy

# Get URL
fly apps open realdiag-api
```

---

## 🔗 Connect Frontend to Backend

### **Update Netlify Environment Variables**

1. Go to Netlify Dashboard → Your Site → **Site settings**
2. **Environment variables** → Add:
   ```
   NEXT_PUBLIC_API_BASE=https://realdiag-api.onrender.com
   ```
3. **Trigger redeploy** (builds will use new API URL)

### **Or Update in Code** (netlify.toml)

Add to `netlify.toml`:
```toml
[build.environment]
  NEXT_PUBLIC_API_BASE = "https://realdiag-api.onrender.com"
```

---

## 🌍 Configure Custom Domain for API

### **Option A: Use Subdomain** (api.realdiag.com)

**In your DNS provider (where you bought realdiag.com):**

1. Add **CNAME record**:
   ```
   Type: CNAME
   Name: api
   Value: realdiag-api.onrender.com (or your provider)
   TTL: Auto
   ```

2. **Render/Railway**: Add custom domain
   - Go to Settings → Custom Domains
   - Add: `api.realdiag.com`
   - Wait for DNS propagation (5-30 minutes)

### **Option B: Use Provider's URL**

Just use the provided URL:
- Render: `https://realdiag-api.onrender.com`
- Railway: `https://realdiag-api.up.railway.app`
- Fly.io: `https://realdiag-api.fly.dev`

---

## ✅ Verify Deployment

### **1. Check Frontend**
```bash
# Visit www.realdiag.com in browser
# Should show latest UI changes
```

### **2. Check Backend API**
```bash
curl https://api.realdiag.com/health
# Expected: {"ok": true}

curl https://api.realdiag.com/diagnostic/trees
# Expected: List of diagnostic trees (415 trees)
```

### **3. Test Medication Safety**
```bash
curl -X POST https://api.realdiag.com/diagnostic/medication-safety-check \
  -H "Content-Type: application/json" \
  -d '{
    "current_medications": ["warfarin", "aspirin"],
    "patient_conditions": ["atrial fibrillation"],
    "age": 65
  }'
```

Expected response with drug interaction alerts!

---

## 🔄 Auto-Deployment Flow

```
GitHub Push
    ↓
GitHub Actions (builds Docker images)
    ↓
├─→ Netlify (auto-deploys frontend from main branch)
│   └─→ www.realdiag.com updated ✅
│
└─→ Render/Railway (auto-deploys from main branch)
    └─→ api.realdiag.com updated ✅
```

---

## 📊 Current Status

- ✅ Code pushed to GitHub
- ✅ Netlify build triggered (empty commit)
- ✅ Frontend will update in 2-5 minutes
- ⏳ **Backend needs deployment** (choose Option 1, 2, or 3 above)

---

## 🆘 Quick Deploy Backend Now

**Fastest way (Railway.app - 2 minutes):**

1. Visit: https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Select `bevroy/RealDiag-Software`
4. Click **"Add variables"**:
   - `PORT`: 8000
   - `FHIR_BASE_URL`: (your EMR URL)
5. Click **"Deploy"**
6. Copy the URL provided
7. Update Netlify env var `NEXT_PUBLIC_API_BASE` with Railway URL
8. Redeploy Netlify

**Done!** Your medication safety features will be live! 🚀

---

## 📝 Notes

- **Netlify** = Frontend only (static Next.js export)
- **Render/Railway/Fly** = Backend API (FastAPI with Python)
- **Kubernetes cluster** = Development/staging environment (not production)
- **www.realdiag.com** = Production site on Netlify
- **api.realdiag.com** = Should point to backend (needs deployment)

---

**Next Step:** Choose a backend hosting provider and deploy! I recommend **Render.com** for simplicity.
