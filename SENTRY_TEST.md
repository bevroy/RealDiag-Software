# Testing Sentry Integration

## Quick Verification

### Backend Test

```bash
# Set environment variables
export SENTRY_DSN="https://your-backend-dsn@sentry.io/project-id"
export ENVIRONMENT="development"

# Start backend
cd /workspaces/RealDiag-Software
python backend/main.py

# Expected output:
# ✅ Sentry initialized for environment: development
```

### Frontend Test

```bash
# Set environment variables
export NEXT_PUBLIC_SENTRY_DSN="https://your-frontend-dsn@sentry.io/project-id"
export NEXT_PUBLIC_SENTRY_ENVIRONMENT="development"

# Start frontend
cd /workspaces/RealDiag-Software/frontend
npm run dev

# Open browser to http://localhost:3000
# Check console for: "✅ Sentry initialized for environment: development"
```

### Manual Error Test

**Backend:**
```bash
# In Python shell
python3 << EOF
import sentry_sdk
sentry_sdk.init(dsn="https://your-backend-dsn@sentry.io/project-id")
sentry_sdk.capture_message("Test from RealDiag backend")
print("✅ Test error sent to Sentry")
EOF
```

**Frontend:**
Open browser console and run:
```javascript
throw new Error("Test error from RealDiag frontend");
```

### Check Sentry Dashboard

1. Go to [sentry.io](https://sentry.io)
2. Navigate to your project
3. Click **Issues**
4. You should see the test errors appear within ~30 seconds

## Current Status

✅ **Backend Sentry SDK**: `2.45.0` installed  
✅ **Frontend Sentry SDK**: `@sentry/nextjs@7.120.4` installed  
✅ **Backend Integration**: Added to `backend/main.py`  
✅ **Frontend Integration**: Added to `frontend/pages/_app.js` and `frontend/utils/sentry.js`

## Next Steps

1. Create Sentry projects at [sentry.io](https://sentry.io):
   - One for **backend** (Python/FastAPI)
   - One for **frontend** (JavaScript/Next.js)

2. Get DSN keys from each project

3. Set environment variables:
   ```bash
   # Backend (.env or K8s secret)
   SENTRY_DSN=https://xxx@sentry.io/backend-project-id
   ENVIRONMENT=production
   
   # Frontend (.env.production or K8s ConfigMap)
   NEXT_PUBLIC_SENTRY_DSN=https://xxx@sentry.io/frontend-project-id
   NEXT_PUBLIC_SENTRY_ENVIRONMENT=production
   ```

4. Deploy and verify error tracking works

## Reference

See full setup guide: `docs/SENTRY_SETUP.md`
