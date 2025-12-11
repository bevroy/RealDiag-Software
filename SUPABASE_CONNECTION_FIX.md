# Supabase Connection Pooling Fix

## Problem
Backend deployment failed with error:
```
FATAL: MaxClientsInSessionMode: max clients reached - in Session mode max clients are limited to pool_size
```

## Root Cause
- **Supabase free tier** has strict connection limits in **Session mode pooler**
- **2 gunicorn workers** × **5 pool_size** × **10 max_overflow** = up to **30 connections**
- Supabase Session mode limit: typically **15 connections** on free tier
- Result: Connection pool exhaustion and startup failure

## Immediate Fix Applied ✅

### 1. Reduced Connection Pool (database.py)
```python
pool_size=2,          # Reduced from 5 to 2 per worker
max_overflow=3,       # Reduced from 10 to 3
pool_recycle=300,     # Recycle connections every 5 min
pool_timeout=30,      # Add connection timeout
```

### 2. Reduced Workers (Dockerfile)
```
-w 1  # Reduced from 2 to 1 worker
```

**New max connections:** 1 worker × (2 pool + 3 overflow) = **5 connections max**

## Better Long-Term Solution: Transaction Mode Pooler

Supabase offers two pooler modes:
- **Session mode** (current): Low connection limit, one connection per client session
- **Transaction mode**: Higher connection limit (6000+), connections released after each transaction

### How to Switch to Transaction Mode

1. **Get your Supabase connection string:**
   - Go to: Supabase Dashboard → Project Settings → Database
   - Look for **"Connection string"** section
   - You'll see two URLs:
     - **Session mode:** `*.pooler.supabase.com:5432` (current)
     - **Transaction mode:** `*.pooler.supabase.com:6543` (port 6543)

2. **Update connection string:**
   - Change port from `5432` to `6543` in your DATABASE_URL
   - Example:
     ```
     OLD: postgresql://user:pass@aws-1-us-east-1.pooler.supabase.com:5432/postgres
     NEW: postgresql://user:pass@aws-1-us-east-1.pooler.supabase.com:6543/postgres
     ```

3. **Update in Render:**
   - Render Dashboard → `realdiag-backend` service
   - Environment Variables → Edit `DATABASE_URL`
   - Change port `5432` → `6543`
   - Save and redeploy

4. **After switching to Transaction mode, you can increase workers:**
   ```dockerfile
   # backend/Dockerfile
   CMD [...] -w 2 [...]  # Can use 2 workers again
   ```
   
   ```python
   # backend/services/database.py
   pool_size=5,        # Can increase back to 5
   max_overflow=10,    # Can increase back to 10
   ```

## Alternative: Use Render's PostgreSQL Database

Instead of Supabase, use Render's managed database (already configured in render.yaml):

### Advantages of Render PostgreSQL
- ✅ No connection pooling issues
- ✅ Direct connection (no pooler mode confusion)
- ✅ Integrated with Render services
- ✅ Free tier: 90 days free, then $7/month
- ✅ Simpler setup (already in render.yaml)

### How to Switch to Render Database

1. **Deploy the database** (if not already created):
   - Render will auto-create `realdiag-database` from render.yaml
   - Or manually: Render Dashboard → New → PostgreSQL
   - Name: `realdiag-database`
   - Plan: Free

2. **Update backend service:**
   - The `DATABASE_URL` in render.yaml already references the Render database
   - Just ensure the envVar points to the right database:
     ```yaml
     - key: DATABASE_URL
       fromDatabase:
         name: realdiag-database
         property: connectionString
     ```

3. **Migrate data from Supabase to Render** (if needed):
   ```bash
   # Dump from Supabase
   pg_dump "postgresql://user:pass@supabase-host:5432/db" > backup.sql
   
   # Restore to Render
   psql "postgresql://render-connection-string" < backup.sql
   ```

4. **Redeploy backend:**
   - Will now use Render database instead of Supabase
   - Can use higher pool_size and more workers

## Current Configuration (After Fix)

With the immediate fix applied:
- **Workers:** 1
- **Pool size:** 2 per worker
- **Max overflow:** 3
- **Max connections:** ~5 concurrent
- **Status:** Should deploy successfully ✅

## Next Steps

**Option A: Keep Supabase + Transaction Mode**
1. Change DATABASE_URL port from 5432 → 6543
2. Increase workers back to 2
3. Increase pool_size back to 5

**Option B: Switch to Render Database**
1. Create Render PostgreSQL database
2. Migrate data (if any)
3. Update DATABASE_URL to point to Render
4. Increase workers back to 2
5. Increase pool_size back to 5

**For now:** The current fix should allow deployment to succeed. You can optimize later based on your preference.

## Testing After Deployment

Verify the fix worked:
```bash
# 1. Check health endpoint
curl https://realdiag-backend.onrender.com/health

# 2. Check if rules load
curl https://realdiag-backend.onrender.com/reference/endocrinology | \
  python -c "import sys, json; d=json.load(sys.stdin); \
  print(f'Conditions: {len(d[\"rules\"])}')"

# 3. Monitor logs for database errors
# Render Dashboard → realdiag-backend → Logs
# Should NOT see MaxClientsInSessionMode errors
```

## Summary

✅ **Immediate fix applied:** Reduced pool size and workers  
⚠️ **Performance trade-off:** Lower concurrency (acceptable for free tier)  
🔄 **Long-term options:** Transaction mode pooler OR Render database  
📈 **To scale:** Increase workers + pool_size after fixing pooler mode
