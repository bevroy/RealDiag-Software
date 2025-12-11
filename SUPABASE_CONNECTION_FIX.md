# Supabase Connection Pooling Fix

## Problem
Backend deployment failed with error:
```
FATAL: MaxClientsInSessionMode: max clients reached - in Session mode max clients are limited to pool_size
```

## Root Cause
- **Supabase free tier** has strict connection limits in **Session mode pooler**
- Even with reduced pool settings, connection limits were exceeded
- Session mode: ~15 connection limit, one connection per client session
- Result: Connection pool exhaustion and startup failure

## Current Fix Applied ✅

### NullPool - No Connection Pooling (database.py)
```python
poolclass=NullPool,  # Creates new connection per request, closes immediately
```

**How it works:**
- No persistent connections maintained
- New connection created for each database operation
- Connection closed immediately after use
- Maximum possible connections: Number of concurrent requests (typically < 5)

**Trade-offs:**
- ✅ **Reliable:** Never exceeds connection limits
- ✅ **Simple:** No pool management complexity
- ⚠️ **Slower:** Connection overhead on each request (~50-100ms)
- ⚠️ **Less efficient:** No connection reuse

**Status:** This will allow deployment to succeed on Supabase free tier.

## RECOMMENDED: Switch to Transaction Mode Pooler 🎯

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
