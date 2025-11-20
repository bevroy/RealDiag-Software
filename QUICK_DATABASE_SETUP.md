# Quick Start: Database Setup

## 🚀 5-Minute Database Setup

### Step 1: Create Database (2 minutes)
1. Go to https://dashboard.render.com/
2. Click "New +" → "PostgreSQL"
3. Configure:
   - Name: `realdiag-database`
   - Database: `realdiag_prod`
   - Region: Ohio (US East)
   - Plan: Starter ($7/mo)
4. Click "Create Database"
5. Wait 2 minutes for creation

### Step 2: Get Connection String (30 seconds)
1. Click on your new database
2. Go to "Info" tab
3. Copy "Internal Database URL"
   ```
   postgres://realdiag_user:pass@dpg-xxx.ohio-postgres.render.com/realdiag_prod
   ```

### Step 3: Configure Backend (1 minute)
1. Go to https://dashboard.render.com/
2. Click on "realdiag-software" service
3. Go to "Environment" tab
4. Add environment variable:
   - **Key**: `DATABASE_URL`
   - **Value**: (paste connection string from Step 2)
5. Click "Save Changes"

### Step 4: Verify Deployment (2 minutes)
Backend will auto-redeploy. Check logs:
1. Click "Logs" tab
2. Wait for deployment to complete
3. Look for:
   ```
   ✅ Database engine created successfully
   ✅ Database connection verified
   ✅ Database initialized successfully
   ✅ Using PostgreSQL database for data persistence
   ```

### Step 5: Test (1 minute)
```bash
# Test registration
curl -X POST https://api.realdiag.com/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234!",
    "full_name": "Test User"
  }'

# Should return success with user_id
```

## ✅ Success Checklist

- [ ] PostgreSQL database created on Render
- [ ] DATABASE_URL added to backend environment
- [ ] Backend redeployed successfully
- [ ] Logs show "Database initialized successfully"
- [ ] User registration works
- [ ] User login persists after logout

## 🔥 If Something Goes Wrong

**Quick Rollback**: Remove DATABASE_URL environment variable
- Backend will fall back to in-memory storage
- No data loss (users can re-register)

## 📚 Detailed Guides

- **Complete Setup**: See `POSTGRESQL_SETUP.md`
- **Production Deployment**: See `DATABASE_DEPLOYMENT.md`
- **Implementation Details**: See `DATABASE_MIGRATION_SUMMARY.md`

## 💡 What This Gives You

### Before (In-Memory)
- Data lost on restart
- Users must re-register after deployment
- No persistence

### After (PostgreSQL)
- ✅ Data persists forever
- ✅ Users stay logged in
- ✅ Search history saved
- ✅ Favorites preserved
- ✅ Production-ready scalability

## 🎯 Next Steps

After database setup:
1. Test user registration and login
2. Verify data persists after logout
3. Move to Phase 2: EHR Integration
4. Add more medical specialties
5. Begin mobile app development

## ⏱️ Total Time: ~5-10 minutes

Most time is waiting for Render to:
- Create database (~2 minutes)
- Redeploy backend (~3 minutes)

Actual configuration: ~2 minutes
