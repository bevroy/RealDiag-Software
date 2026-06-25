# Render PostgreSQL Database Setup Guide

## Quick Setup (5 minutes)

Your `render.yaml` is already configured! Follow these steps to activate the database:

### Step 1: Push the Updated Configuration

```bash
git add render.yaml
git commit -m "Configure PostgreSQL database with free plan"
git push origin main
```

### Step 2: Access Render Dashboard

1. Go to: **https://dashboard.render.com/**
2. Log in with your GitHub account (or existing Render account)

### Step 3: Create Database from Blueprint

**Option A: Using Blueprint (Recommended - Automated)**

1. In Render Dashboard, click **"Blueprints"** in the left sidebar
2. Find your **RealDiag-Software** repository
3. Click **"Sync Blueprint"** or **"New Blueprint Instance"**
4. Render will automatically:
   - Create `realdiag-database` PostgreSQL instance
   - Create/update `realdiag-backend` web service
   - Connect `DATABASE_URL` environment variable automatically

**Option B: Manual Database Creation**

1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `realdiag-database`
   - **Database**: `realdiag_prod`
   - **User**: `realdiag_user`
   - **Region**: `Ohio (US East)`
   - **Plan**: `Free` (90-day trial) or `Starter` ($7/month)
3. Click **"Create Database"**
4. Wait 2-3 minutes for provisioning

### Step 4: Connect Database to Backend

**If using Blueprint (Option A)**: Skip this step - already connected!

**If using Manual Creation (Option B)**:

1. Go to your **realdiag-backend** service
2. Click **"Environment"** tab
3. Find or add `DATABASE_URL` variable:
   - Click **"Add Environment Variable"**
   - **Key**: `DATABASE_URL`
   - **Value**: Click **"Select Database"** → Choose `realdiag-database`
   - This automatically uses the internal connection string
4. Click **"Save Changes"**
5. Backend will automatically redeploy (takes 2-3 minutes)

### Step 5: Verify Database Connection

After deployment completes (watch the "Logs" tab):

```bash
# Test health endpoint
curl https://realdiag-software.onrender.com/health

# Check if database is connected (should show database info, not "in-memory")
curl https://realdiag-software.onrender.com/docs
```

You can also check the logs in Render dashboard for:
```
✅ Database engine created successfully
```

### Step 6: Initialize Database Tables

The database tables will be created automatically on first startup. Check logs for:
```
✅ Database tables created successfully
```

## Database Plans Comparison

### Free Plan (90 days)
- ✅ **Cost**: Free for 90 days, then expires
- ✅ **Storage**: 1 GB
- ✅ **RAM**: 256 MB
- ✅ **Connections**: 97
- ❌ Expires after 90 days (need to upgrade)
- ❌ No backups

### Starter Plan ($7/month)
- ✅ **Cost**: $7/month (billed monthly)
- ✅ **Storage**: 10 GB
- ✅ **RAM**: 1 GB
- ✅ **Connections**: 97
- ✅ Permanent (no expiration)
- ✅ Daily automated backups
- ✅ Point-in-time recovery (7 days)

**Recommendation**: Start with **Free** for testing, upgrade to **Starter** for production.

## Troubleshooting

### Database Not Connecting

1. **Check Environment Variable**:
   - Go to backend service → Environment tab
   - Verify `DATABASE_URL` exists and points to `realdiag-database`

2. **Check Database Status**:
   - Go to `realdiag-database` in dashboard
   - Status should be "Available" (green)
   - If "Suspended", click "Resume"

3. **Check Backend Logs**:
   ```
   # Look for these messages:
   ✅ Database engine created successfully
   OR
   ⚠️  DATABASE_URL not set - using in-memory storage
   ```

4. **Restart Backend**:
   - Go to backend service
   - Click "Manual Deploy" → "Clear build cache & deploy"

### Connection String Format

Internal connection string (automatically provided):
```
postgresql://realdiag_user:PASSWORD@dpg-xxxxx/realdiag_prod
```

External connection string (for local development):
```
postgresql://realdiag_user:PASSWORD@dpg-xxxxx-a.ohio-postgres.render.com/realdiag_prod
```

## Verification Checklist

- [ ] Database created in Render dashboard
- [ ] Database status shows "Available"
- [ ] DATABASE_URL connected to backend service
- [ ] Backend redeployed successfully
- [ ] Backend logs show "Database engine created successfully"
- [ ] Health endpoint returns 200 OK
- [ ] Can register a new user account
- [ ] User data persists after backend restart

## Quick Commands

```bash
# Push configuration
git add render.yaml
git commit -m "Configure PostgreSQL database"
git push origin main

# Verify deployment
curl https://realdiag-software.onrender.com/health

# Test user registration
curl -X POST https://realdiag-software.onrender.com/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "full_name": "Test User"
  }'
```

## Security Notes

- ✅ Database only accessible from Render services (ipAllowList: [])
- ✅ Connection uses TLS encryption
- ✅ Password automatically generated and rotated
- ✅ Internal connection string (not exposed externally)

## Cost Estimate

**Free Plan**: $0 for 90 days
**After 90 days**: Upgrade to Starter ($7/month) or database will be suspended

**Total Monthly Cost (Production)**:
- Backend: Free (with limitations) or $7/month for Starter
- Database: $7/month (Starter plan)
- **Total**: $7-14/month

## Next Steps

1. ✅ Push the updated `render.yaml`
2. ✅ Create database in Render dashboard
3. ✅ Verify connection in backend logs
4. ✅ Test user registration and login
5. ✅ Celebrate! 🎉

## Support

- **Render Docs**: https://render.com/docs/databases
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Project Issues**: https://github.com/bevroy/RealDiag-Software/issues

---

**Last Updated**: December 6, 2025
