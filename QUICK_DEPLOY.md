# 🚀 Quick Deploy Guide - RealDiag Test Environment

Deploy your test environment in **5 minutes** using free hosting.

---

## ✅ Prerequisites

- [ ] GitHub account
- [ ] This repository pushed to GitHub
- [ ] 5 minutes of your time

---

## 🎯 Option 1: Render.com (Recommended - Easiest)

**Why?** One-click deploy, handles backend + database + frontend.

### Steps:

1. **Go to Render**
   - Visit: https://render.com
   - Click **"Sign Up"** or **"Login with GitHub"**

2. **Create New Blueprint**
   - Click **"New +"** button (top right)
   - Select **"Blueprint"**

3. **Connect Repository**
   - Connect your GitHub account (if not already)
   - Select repository: `bevroy/RealDiag-Software`
   - Branch: `main`

4. **Select Blueprint File**
   - Render will detect `render-test.yaml`
   - If prompted, select: **`render-test.yaml`**

5. **Review & Deploy**
   - Review the services (backend, database, frontend)
   - Click **"Apply"**
   - Wait 5-10 minutes ☕

6. **Get Your URLs**
   ```
   Backend:  https://realdiag-test-backend.onrender.com
   Frontend: https://realdiag-test-frontend.onrender.com
   ```

7. **Test It!**
   ```bash
   # Check backend is in test mode
   curl https://realdiag-test-backend.onrender.com/health
   
   # Should show: "test_mode": true
   ```

8. **Visit Frontend**
   - Open: `https://realdiag-test-frontend.onrender.com`
   - You should see a **yellow banner**: "🧪 TEST ENVIRONMENT"
   - Sign up with any email
   - All features automatically unlocked! 🎉

---

## 🎯 Option 2: Netlify (Frontend) + Render (Backend)

**Why?** Best for static sites, automatic HTTPS, fast CDN.

### Backend on Render:

1. Go to https://render.com → **"New +"** → **"Web Service"**
2. Connect repo: `bevroy/RealDiag-Software`
3. Settings:
   - **Name**: `realdiag-test-api`
   - **Environment**: `Docker`
   - **Branch**: `main`
   - **Dockerfile**: `backend/Dockerfile`
   - **Plan**: Free
4. Add database:
   - Dashboard → **"New +"** → **"PostgreSQL"**
   - **Name**: `realdiag-test-db`
   - Copy connection string
5. Environment variables (in service settings):
   ```
   ENVIRONMENT=test
   FREE_ACCESS_TESTING=true
   BYPASS_SUBSCRIPTION_CHECKS=true
   RATE_LIMIT_ENABLED=false
   DATABASE_URL=<your-postgres-connection-string>
   JWT_SECRET=<generate-random-secret>
   CORS_ORIGINS=*
   ```
6. Click **"Create Web Service"**
7. Save backend URL: `https://realdiag-test-api.onrender.com`

### Frontend on Netlify:

1. Go to https://netlify.com → **"Add new site"** → **"Import an existing project"**
2. Connect GitHub → Select `bevroy/RealDiag-Software`
3. Settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `out`
4. Environment variables:
   ```
   NODE_VERSION=20
   NEXT_PUBLIC_ENVIRONMENT=test
   NEXT_PUBLIC_API_BASE=<your-render-backend-url>
   NEXT_PUBLIC_SHOW_TEST_BANNER=true
   ```
5. Click **"Deploy site"**
6. Save frontend URL: `https://your-site.netlify.app`

---

## 🎯 Option 3: Vercel (Frontend) + Railway (Backend)

**Why?** Great for Next.js, good free tier, automatic HTTPS.

### Backend on Railway:

1. Go to https://railway.app → **"New Project"**
2. **"Deploy from GitHub repo"** → Select repository
3. Settings:
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add PostgreSQL:
   - **"New"** → **"Database"** → **"PostgreSQL"**
5. Environment variables:
   ```
   ENVIRONMENT=test
   FREE_ACCESS_TESTING=true
   BYPASS_SUBSCRIPTION_CHECKS=true
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   JWT_SECRET=<random-secret>
   CORS_ORIGINS=*
   ```
6. Deploy → Save URL

### Frontend on Vercel:

1. Go to https://vercel.com → **"Add New..."** → **"Project"**
2. Import `bevroy/RealDiag-Software`
3. Settings:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
4. Environment variables:
   ```
   NEXT_PUBLIC_ENVIRONMENT=test
   NEXT_PUBLIC_API_BASE=<your-railway-backend-url>
   NEXT_PUBLIC_SHOW_TEST_BANNER=true
   ```
5. Deploy → Save URL

---

## ✅ After Deployment Checklist

- [ ] Backend health check shows `"test_mode": true`
- [ ] Frontend shows yellow test banner
- [ ] Can sign up with any email
- [ ] All features are unlocked (no payment required)
- [ ] Can create diagnoses, view reports, etc.

---

## 🧪 Testing Your Deployment

### 1. Health Check
```bash
curl https://your-backend-url/health | jq

# Expected output:
{
  "status": "healthy",
  "test_mode": true,
  "subscriptions_bypassed": true,
  "database": "connected",
  "environment": "test"
}
```

### 2. Create Test Account
- Visit frontend URL
- Click "Sign Up"
- Enter: `tester@example.com` / `TestPass123!`
- Should log in automatically (no email verification in test mode)

### 3. Verify Access
- Try symptom search (should work)
- Create a diagnosis (should work)
- View reports (should work)
- Check profile → Should show "Enterprise Plan"

---

## 📧 Invite Your Testers

Copy your URLs and send this email:

```
Subject: You're Invited to Beta Test RealDiag!

Hi [Tester Name],

You're invited to help test RealDiag's diagnostic platform!

🔗 Access Link: https://your-frontend-url.com

📝 How to Start:
1. Visit the link above
2. Click "Sign Up"
3. Use any email (no verification required)
4. Start testing!

🎁 What You Get:
✅ Full enterprise access (all features unlocked)
✅ Unlimited symptom searches
✅ Complete diagnostic tree access
✅ No payment required

📋 What to Test:
- Search symptoms and check results
- Run diagnostic assessments
- Try different medical specialties
- Test on mobile and desktop
- Report any bugs or issues

🐛 Found a Bug?
Reply to this email or file an issue at:
https://github.com/bevroy/RealDiag-Software/issues

Thank you for helping make RealDiag better!

Best regards,
[Your Name]
```

---

## 📊 Monitoring Your Test Environment

### Check Logs (Render):
```bash
# Via Render Dashboard
1. Go to service
2. Click "Logs" tab
3. Monitor real-time activity
```

### Check Logs (Netlify):
```bash
# Via Netlify Dashboard
1. Go to site
2. Click "Deploys" → "Deploy log"
3. Check for errors
```

### Check Logs (Railway):
```bash
# Via Railway Dashboard
1. Go to service
2. Click "Deployments"
3. View logs
```

---

## 🔧 Troubleshooting

### Backend not starting?
- Check environment variables are set correctly
- Verify `ENVIRONMENT=test` is set
- Check database connection string
- View logs for error messages

### Frontend not connecting to backend?
- Verify `NEXT_PUBLIC_API_BASE` matches backend URL
- Check backend health endpoint is accessible
- Look for CORS errors in browser console

### Test mode not working?
- Verify `ENVIRONMENT=test` in backend
- Check `/health` endpoint shows `"test_mode": true`
- Ensure `FREE_ACCESS_TESTING=true`

### Database errors?
- Check `DATABASE_URL` is set correctly
- Verify database service is running
- Check connection string format

---

## 💰 Cost Estimate

### Free Tier (Recommended for Testing):
- **Render**: Free (with 90-day database trial)
- **Netlify**: Free (100GB bandwidth)
- **Vercel**: Free (100GB bandwidth)
- **Railway**: Free ($5 credit/month)

**Total: $0/month** ✨

### Paid Tier (If You Need More):
- **Render Starter**: $7/month (database)
- **Netlify Pro**: $19/month (optional)
- **Vercel Pro**: $20/month (optional)

---

## 🎉 You're Done!

Your test environment is now live! Share the URL with your beta testers and start collecting feedback.

**Next Steps:**
1. ✅ Share URL with testers
2. ✅ Send them `TESTER_ACCESS_GUIDE.md`
3. ✅ Monitor logs for errors
4. ✅ Collect feedback
5. ✅ Fix bugs and redeploy

**Need Help?**
- Check: `docs/TEST_ENVIRONMENT_DEPLOYMENT.md` (detailed guide)
- Read: `TESTER_ACCESS_GUIDE.md` (for testers)
- Issues: https://github.com/bevroy/RealDiag-Software/issues

---

**Happy Testing! 🚀**
