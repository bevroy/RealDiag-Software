# ✅ Deploy RealDiag Backend to Render.com

## 🚀 Quick Start (5 minutes)

Your backend is ready to deploy! Follow these steps:

---

## Step 1: Create Render.com Account

1. Go to: **https://dashboard.render.com/register**
2. Sign up with GitHub (recommended)
3. Authorize Render to access your GitHub repositories

---

## Step 2: Connect Your Repository

1. After logging in, click **"New +"** → **"Blueprint"**
2. Connect your GitHub account (if not already connected)
3. Search for: **`bevroy/RealDiag-Software`**
4. Click **"Connect"**

Render will automatically detect the `render.yaml` file! ✅

---

## Step 3: Configure Service

Render will show you the configuration from `render.yaml`:

- **Service Name**: `realdiag-backend` ✅
- **Branch**: `main` ✅
- **Environment**: Docker ✅
- **Plan**: Free ✅

Click **"Apply"** to create the service!

---

## Step 4: Set Secure Environment Variables

After the service is created:

1. Go to **Dashboard** → Your service → **"Environment"** tab
2. Add secure variables (not in render.yaml):

### **Required:**
```
FHIR_AUTH_TOKEN = <your-emr-fhir-auth-token>
```

### **Optional (update if you have EMR):**
```
FHIR_BASE_URL = https://your-emr-fhir-server.com/fhir
```

Click **"Save Changes"**

---

## Step 5: Wait for Deployment

Render will:
1. ✅ Build Docker image from `backend/Dockerfile`
2. ✅ Deploy to Render infrastructure
3. ✅ Run health checks on `/health` endpoint
4. ✅ Provide you with a URL

**Time:** 3-5 minutes

---

## Step 6: Get Your Backend URL

Once deployed, you'll get a URL like:
```
https://realdiag-backend.onrender.com
```

Or:
```
https://realdiag-backend-<random>.onrender.com
```

**Save this URL!** You'll need it for Netlify.

---

## Step 7: Test Your Backend

### Test Health Endpoint:
```bash
curl https://realdiag-backend.onrender.com/health
```

Expected response:
```json
{"ok": true}
```

### Test Diagnostic Trees:
```bash
curl https://realdiag-backend.onrender.com/diagnostic/trees
```

Expected: List of 415 diagnostic trees

### Test Medication Safety:
```bash
curl -X POST https://realdiag-backend.onrender.com/diagnostic/medication-safety-check \
  -H "Content-Type: application/json" \
  -d '{
    "current_medications": ["warfarin", "aspirin"],
    "patient_conditions": ["atrial fibrillation"],
    "age": 65
  }'
```

Expected: Medication safety alerts about warfarin + aspirin interaction

---

## Step 8: Connect Frontend to Backend

### Update Netlify Environment Variables:

1. Go to: **https://app.netlify.com**
2. Select your **RealDiag** site
3. **Site settings** → **Environment variables**
4. Add or update:

```
NEXT_PUBLIC_API_BASE = https://realdiag-backend.onrender.com
```

5. Click **"Save"**
6. **Trigger redeploy**:
   - Go to **Deploys** tab
   - Click **"Trigger deploy"** → **"Deploy site"**

---

## Step 9: Configure Custom Domain (Optional)

### Add api.realdiag.com subdomain:

**In Render Dashboard:**
1. Your service → **"Settings"** → **"Custom Domains"**
2. Click **"Add Custom Domain"**
3. Enter: `api.realdiag.com`
4. Render will show you DNS records to add

**In Your DNS Provider** (where you bought realdiag.com):
1. Add **CNAME record**:
   ```
   Type: CNAME
   Name: api
   Value: realdiag-backend.onrender.com
   TTL: Auto
   ```
2. Wait 5-30 minutes for DNS propagation

**Update Netlify env var:**
```
NEXT_PUBLIC_API_BASE = https://api.realdiag.com
```

---

## ✅ Verification Checklist

- [ ] Render.com account created
- [ ] Repository connected via Blueprint
- [ ] Service deployed successfully
- [ ] Health check passing: `curl https://<your-url>/health`
- [ ] Diagnostic trees accessible: `curl https://<your-url>/diagnostic/trees`
- [ ] Medication safety working: Test with curl command above
- [ ] Netlify env var updated with backend URL
- [ ] Netlify redeployed
- [ ] www.realdiag.com shows updated frontend
- [ ] Frontend can call backend API

---

## 🎉 Success!

Once all steps are complete:

✅ **Frontend**: www.realdiag.com (Netlify)  
✅ **Backend**: api.realdiag.com or realdiag-backend.onrender.com (Render)  
✅ **Features Live**:
- 415 diagnostic decision trees
- Medication safety checking
- EMR integration support
- Patient history management

---

## 🔄 Auto-Deployment

Now that everything is connected:

```
Git Push to main
    ↓
GitHub Actions (builds images)
    ↓
├─→ Netlify auto-deploys frontend ✅
└─→ Render auto-deploys backend ✅
```

**Future updates:** Just push to GitHub! Both will auto-deploy.

---

## 🆘 Troubleshooting

### Build Failed on Render?

**Check logs:**
1. Render Dashboard → Your service → **"Logs"** tab
2. Look for errors in build/deploy logs

**Common fixes:**
- Docker build issue → Check `backend/Dockerfile`
- Port issue → Render uses `$PORT` env var (already configured)
- Dependencies → Check `backend/requirements.txt`

### Health Check Failed?

**Fix:**
1. Check service is running: Render dashboard shows "Live"
2. Check logs for startup errors
3. Verify `/health` endpoint exists in FastAPI app
4. Try manual curl: `curl https://<your-url>/health`

### Frontend Can't Connect to Backend?

**Check:**
1. CORS settings in backend (should allow Netlify domain)
2. Netlify env var `NEXT_PUBLIC_API_BASE` is correct
3. Backend URL is accessible: `curl https://<backend-url>/health`
4. Redeploy Netlify after changing env vars

---

## 📞 Need Help?

**Render Support:**
- Dashboard → **"Help"** → Contact support
- Docs: https://render.com/docs

**RealDiag Issues:**
- GitHub: https://github.com/bevroy/RealDiag-Software/issues

---

## 🚀 Next Steps After Deployment

1. **Configure EMR Integration**:
   - Update `FHIR_BASE_URL` with your actual EMR FHIR endpoint
   - Add `FHIR_AUTH_TOKEN` securely in Render environment variables
   - Test: `GET /diagnostic/emr/patient/{id}/medications`

2. **Monitor Usage**:
   - Render Dashboard shows metrics (requests, response times, errors)
   - Free tier: 750 hours/month (enough for 24/7 uptime)

3. **Upgrade Plan** (when ready):
   - Free tier: Cold starts after 15 min inactivity
   - Starter ($7/mo): Always-on, faster response times
   - Pro ($25/mo): More resources, dedicated IP

---

**Ready?** Start with Step 1: https://dashboard.render.com/register

Your backend is configured and ready to deploy! 🎉
