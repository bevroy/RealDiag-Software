# 🚀 Quick Production Deployment

**Complete these 3 tasks to finish production readiness:**

---

## Task 1: Configure Sentry (Backend) ⏱️ 5 min

### Get Sentry DSN
1. Go to https://sentry.io
2. Navigate to **Settings** → **Projects** → **Client Keys (DSN)**
3. Copy DSN (format: `https://abc123@o123456.ingest.sentry.io/789012`)

### Add to Render
1. Open https://dashboard.render.com
2. Select `realdiag-software` service
3. Go to **Environment** tab
4. Click **Add Environment Variable**
5. Add these variables:

```bash
SENTRY_DSN=https://YOUR_SENTRY_DSN@sentry.io/PROJECT_ID
ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
```

6. Click **Save Changes** (auto-redeploys)

### Verify
```bash
# Wait 3-5 minutes for deployment, then:
curl https://realdiag-software.onrender.com/health
```

Check Render logs for: `✅ Sentry initialized for environment: production`

---

## Task 2: Configure Sentry (Frontend) ⏱️ 3 min

### Add to Netlify
1. Open https://app.netlify.com
2. Select your RealDiag site
3. Go to **Site settings** → **Environment variables**
4. Add these variables:

```bash
NEXT_PUBLIC_SENTRY_DSN=https://YOUR_SENTRY_DSN@sentry.io/PROJECT_ID
NEXT_PUBLIC_ENVIRONMENT=production
NEXT_PUBLIC_SENTRY_TRACES_SAMPLE_RATE=0.1
```

5. Trigger new deployment:
```bash
git commit --allow-empty -m "Configure Sentry for frontend"
git push
```

### Verify
Open https://realdiag.netlify.app in browser console, look for:
```
✅ Sentry initialized for environment: production
```

---

## Task 3: Verify Performance Improvements ⏱️ 2 min

### Run Load Test
```bash
cd /workspaces/RealDiag-Software
bash load_test.sh
```

### Expected Results
- ✅ Health endpoint: < 2s (50 concurrent)
- ✅ Education endpoints: < 1s (15 concurrent)
- ✅ Symptom search: **< 5s** (20 concurrent) ← **IMPROVED FROM 16s**

### If Performance Not Improved
1. Check Render deployment completed (shows commit `0ac42ef`)
2. Wait 24 hours for cold start caches to warm up
3. Re-run load test

---

## ✅ Success Criteria

All 3 tasks complete when you see:

1. **Sentry Dashboard** shows events from both frontend and backend
2. **Security headers** include HSTS:
   ```bash
   curl -I https://realdiag-software.onrender.com/health | grep -i strict-transport
   ```
   Output: `strict-transport-security: max-age=31536000; includeSubDomains; preload`

3. **Load test** shows symptom search < 5 seconds (improved from 16s)

---

## 🎉 Done!

**Production Readiness: 10/10** ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐

Next: Monitor Sentry dashboard for 24 hours to catch any unexpected errors.

---

## 📞 Quick Troubleshooting

**Sentry not receiving events?**
- Check DSN format is correct
- Verify environment variable saved in Render/Netlify
- Check deployment logs for Sentry initialization message

**Performance not improved?**
- Verify deployment shows commit `0ac42ef`
- Wait for cache warm-up (first request may be slow)
- Check Render logs for errors

**HSTS header missing?**
- Verify `ENVIRONMENT=production` set in Render
- Check deployment completed successfully
- Try hard refresh: `curl -I` (not browser cache)

---

**Total Time: ~10-15 minutes**  
**Risk: Low** (all code tested and deployed)  
**Impact: High** (production-ready error monitoring and performance)
