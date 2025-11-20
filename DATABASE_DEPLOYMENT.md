# Database Migration Deployment Guide

## Overview
This guide walks you through deploying the PostgreSQL database migration to production.

## Pre-Deployment Checklist

- [ ] PostgreSQL database created on Render
- [ ] DATABASE_URL environment variable configured
- [ ] SQLAlchemy and psycopg2-binary added to requirements.txt
- [ ] All code changes committed to git
- [ ] Tested locally (if possible)

## Step 1: Create PostgreSQL Database on Render

1. **Go to Render Dashboard**: https://dashboard.render.com/
2. **Create New PostgreSQL Instance**:
   - Click "New +" → "PostgreSQL"
   - **Name**: `realdiag-database`
   - **Database**: `realdiag_prod`
   - **Region**: Ohio (US East) - same as backend
   - **PostgreSQL Version**: 16
   - **Plan**: Starter ($7/month) or Free (90 days)
3. **Wait for Creation**: Takes ~2 minutes
4. **Copy Internal Database URL**: 
   - Click on database → "Info" tab
   - Copy the "Internal Database URL"
   - Format: `postgres://realdiag_user:password@dpg-xxxxx.ohio-postgres.render.com/realdiag_prod`

## Step 2: Configure Environment Variables

1. **Go to Backend Service**: https://dashboard.render.com/
2. **Click on `realdiag-software` service**
3. **Go to "Environment" tab**
4. **Add DATABASE_URL**:
   ```
   Key: DATABASE_URL
   Value: <paste Internal Database URL from Step 1>
   ```
5. **Click "Save Changes"**
6. Backend will automatically redeploy with new environment variable

## Step 3: Deploy Code Changes

### Option A: Push to GitHub (Recommended)

```bash
# Commit changes
git add .
git commit -m "feat: Add PostgreSQL database integration

- Created database.py module with SQLAlchemy ORM
- Updated auth_service.py to use PostgreSQL with fallback to in-memory
- Added database initialization on startup
- Added sqlalchemy and psycopg2-binary to requirements.txt

Closes #database-migration"

# Push to main branch
git push origin main
```

Render will automatically detect the commit and redeploy.

### Option B: Manual Deploy

1. Go to Render Dashboard → realdiag-software service
2. Click "Manual Deploy" → "Deploy latest commit"
3. Wait for build to complete (~3-5 minutes)

## Step 4: Verify Deployment

### Check Build Logs

1. Go to Render Dashboard → realdiag-software service
2. Click "Logs" tab
3. Look for these messages:
   ```
   ✅ Database engine created successfully
   ✅ Database connection verified
   ✅ Database tables created successfully
   ✅ Using PostgreSQL database for data persistence
   ```

### Test API Endpoints

```bash
# Health check
curl https://api.realdiag.com/health
# Expected: {"ok":true}

# Check database status (if monitoring endpoint exists)
curl https://api.realdiag.com/monitoring/database
```

### Test User Registration

```bash
# Register new user
curl -X POST https://api.realdiag.com/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234!",
    "full_name": "Test User",
    "specialty": "Internal Medicine"
  }'
```

Expected response:
```json
{
  "message": "User registered successfully",
  "user": {
    "user_id": "user_xxx",
    "email": "test@example.com",
    "full_name": "Test User"
  },
  "access_token": "eyJ..."
}
```

### Test User Login

```bash
# Login
curl -X POST https://api.realdiag.com/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234!"
  }'
```

### Test Data Persistence

1. Register a user
2. Log out (clear browser cookies)
3. Log in again
4. Verify user data persists (not "User not found" error)

## Step 5: Monitor for Errors

### Check Sentry

1. Go to: https://sentry.io/organizations/your-org/projects/
2. Look for errors related to database connections
3. Common issues:
   - "could not connect to server" - DATABASE_URL incorrect
   - "password authentication failed" - Wrong credentials
   - "relation does not exist" - Tables not created

### Check Render Logs

Watch logs for 5-10 minutes after deployment:
```bash
# Real-time logs
render logs -f realdiag-software
```

Look for:
- Database connection errors
- User registration/login failures
- SQLAlchemy warnings

## Step 6: Test User Flows

### Test Registration Flow
1. Go to: https://www.realdiag.com/account
2. Click "Sign Up"
3. Fill in form and submit
4. Verify successful registration

### Test Login Flow
1. Log out
2. Click "Sign In"
3. Enter credentials
4. Verify successful login

### Test Search History
1. Log in
2. Perform symptom search
3. Go to account page
4. Verify search appears in history

### Test Favorites
1. Search for symptoms
2. Click "Add to Favorites" on a diagnosis
3. Go to account page
4. Verify favorite appears in list

## Rollback Plan (If Issues Occur)

### Option 1: Disable Database (Quick)

Remove DATABASE_URL environment variable:
1. Render Dashboard → realdiag-software → Environment
2. Delete DATABASE_URL variable
3. Click "Save Changes"
4. Backend will redeploy without database (fall back to in-memory)

### Option 2: Revert Code

```bash
# Find previous working commit
git log --oneline

# Revert to previous commit
git revert HEAD

# Push revert
git push origin main
```

### Option 3: Emergency Rollback

1. Render Dashboard → realdiag-software → "Rollbacks" tab
2. Click "Rollback" on previous working deployment
3. System will instantly restore previous version

## Common Issues and Solutions

### Issue: "Database connection failed"

**Cause**: Wrong DATABASE_URL or database not running

**Solution**:
1. Verify DATABASE_URL is correct (copy from Render database dashboard)
2. Check database status on Render (should be "Available")
3. Ensure using Internal Database URL (not External)

### Issue: "relation 'users' does not exist"

**Cause**: Tables not created

**Solution**:
1. Check startup logs for "Database initialized successfully"
2. Manually run migration (see below)
3. Verify init_database() is being called on startup

### Issue: "No module named 'sqlalchemy'"

**Cause**: SQLAlchemy not installed

**Solution**:
1. Verify sqlalchemy is in requirements.txt
2. Force rebuild: Render Dashboard → Settings → Clear build cache
3. Redeploy

### Issue: "Users can't log in after migration"

**Cause**: No users in database (in-memory data lost)

**Solution**:
1. Users need to re-register
2. Or run migration script to import old data (if any)

## Manual Database Operations

### Connect to Database

```bash
# Get connection string from Render
psql "$DATABASE_URL"
```

### View Tables

```sql
\dt
-- Lists all tables
```

### Check User Count

```sql
SELECT COUNT(*) FROM users;
```

### View Recent Users

```sql
SELECT user_id, email, full_name, created_at 
FROM users 
ORDER BY created_at DESC 
LIMIT 10;
```

### Clear All Data (DANGEROUS)

```sql
TRUNCATE TABLE search_history CASCADE;
TRUNCATE TABLE favorites CASCADE;
TRUNCATE TABLE custom_lists CASCADE;
TRUNCATE TABLE user_settings CASCADE;
TRUNCATE TABLE sessions CASCADE;
TRUNCATE TABLE users CASCADE;
```

## Performance Optimization (Post-Deployment)

### Add Indexes (if needed)

```sql
-- Index on email for faster login
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Index on timestamps for faster history queries
CREATE INDEX IF NOT EXISTS idx_search_history_timestamp 
ON search_history(timestamp DESC);

-- Index on user_id foreign keys
CREATE INDEX IF NOT EXISTS idx_search_history_user_id 
ON search_history(user_id);

CREATE INDEX IF NOT EXISTS idx_favorites_user_id 
ON favorites(user_id);
```

### Monitor Query Performance

```sql
-- Show slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
WHERE mean_time > 100  -- queries taking > 100ms
ORDER BY mean_time DESC
LIMIT 20;
```

## Success Criteria

Deployment is successful when:

- ✅ Build completes without errors
- ✅ Startup logs show "Database initialized successfully"
- ✅ Health endpoint returns 200 OK
- ✅ New users can register
- ✅ Users can log in
- ✅ User data persists after logout/login
- ✅ Search history is saved
- ✅ Favorites work correctly
- ✅ No database errors in Sentry
- ✅ No "User not found" errors after login

## Post-Deployment Tasks

1. **Monitor Sentry** for 24 hours for any database errors
2. **Check Render logs** for database connection issues
3. **Test all user features** (registration, login, search, favorites, lists)
4. **Backup database** (Render does automatic backups on paid plans)
5. **Document database schema** for future reference
6. **Update README** with database setup instructions

## Next Steps

After successful deployment:

1. ✅ Database migration complete
2. 🔄 Begin EHR integration (Phase 2)
3. 🔄 Add more medical specialties (Phase 3)
4. 🔄 Start mobile app development (Phase 4)

## Support

If you encounter issues:
1. Check Render logs first
2. Check Sentry for error details
3. Review this guide's "Common Issues" section
4. Test locally if possible (with local PostgreSQL)
5. Rollback if critical issues persist
