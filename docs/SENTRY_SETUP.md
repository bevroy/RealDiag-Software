# Sentry Error Tracking Setup Guide

## Overview

RealDiag uses Sentry for comprehensive error tracking, performance monitoring, and session replay across both backend (FastAPI) and frontend (Next.js) applications.

## Features

### Backend Monitoring
- **Error Tracking**: Automatic capture of Python exceptions
- **Performance Monitoring**: Request tracing and profiling (10% sample rate)
- **Logging Integration**: Automatic error log capture (breadcrumbs + errors)
- **FastAPI Integration**: Automatic route instrumentation
- **Environment Filtering**: Production/staging error filtering

### Frontend Monitoring
- **Browser Error Tracking**: JavaScript exceptions and unhandled rejections
- **Session Replay**: User session recordings with privacy masking
- **Performance Tracing**: Page load and navigation tracking
- **User Context**: Automatic user identification
- **Sensitive Data Filtering**: Automatic removal of auth tokens/cookies

## Setup Instructions

### 1. Create Sentry Account and Project

1. Sign up at [sentry.io](https://sentry.io)
2. Create a new organization (or use existing)
3. Create two projects:
   - **Backend**: Platform = Python
   - **Frontend**: Platform = Next.js

### 2. Get Your DSN Keys

Each project has a unique DSN (Data Source Name):

```bash
# Backend DSN format
https://[key]@o[orgid].ingest.sentry.io/[projectid]

# Frontend DSN format  
https://[key]@o[orgid].ingest.sentry.io/[projectid]
```

Find your DSN at:
- **Settings** → **Projects** → [Your Project] → **Client Keys (DSN)**

### 3. Configure Backend

#### Development Environment

Add to your `.env` file:

```bash
# Sentry Configuration
SENTRY_DSN=https://your-backend-dsn@sentry.io/project-id
ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% of requests (optional, default)
SENTRY_PROFILES_SAMPLE_RATE=0.1  # 10% of traces (optional, default)
```

#### Production Environment

Add to Kubernetes secrets:

```bash
kubectl create secret generic realdiag-secrets \
  --from-literal=SENTRY_DSN=https://your-backend-dsn@sentry.io/project-id \
  -n production
```

Or add to your `.env.production` file:

```bash
SENTRY_DSN=https://your-backend-dsn@sentry.io/project-id
ENVIRONMENT=production
```

#### Test Backend Setup

```python
# Test error capture
import sentry_sdk

# This will send a test error to Sentry
def test_sentry():
    try:
        1 / 0
    except Exception as e:
        sentry_sdk.capture_exception(e)
        
# Or trigger directly
sentry_sdk.capture_message("Test message from RealDiag backend")
```

Run:
```bash
curl -X POST http://localhost:8000/test-error  # If you add test endpoint
```

### 4. Configure Frontend

#### Development Environment

Add to `.env.local`:

```bash
NEXT_PUBLIC_SENTRY_DSN=https://your-frontend-dsn@sentry.io/project-id
NEXT_PUBLIC_SENTRY_ENVIRONMENT=development
```

#### Production Environment

Add to `.env.production`:

```bash
NEXT_PUBLIC_SENTRY_DSN=https://your-frontend-dsn@sentry.io/project-id
NEXT_PUBLIC_SENTRY_ENVIRONMENT=production
```

Or set in Kubernetes ConfigMap:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: realdiag-web-config
  namespace: production
data:
  NEXT_PUBLIC_SENTRY_DSN: "https://your-frontend-dsn@sentry.io/project-id"
  NEXT_PUBLIC_SENTRY_ENVIRONMENT: "production"
```

#### Install Frontend Dependencies

```bash
cd frontend
npm install @sentry/nextjs
```

#### Test Frontend Setup

Open browser console and run:

```javascript
// Test error capture
throw new Error("Test error from RealDiag frontend");

// Or use the utility function
import { captureError } from '../utils/sentry';
captureError(new Error("Test error"));
```

### 5. User Context Tracking

The application automatically captures user context when users log in. You can also manually set user info:

```javascript
// In frontend after authentication
import { setUserContext } from '../utils/sentry';

setUserContext({
  id: user.id,
  email: user.email,
  role: user.role
});
```

```python
# In backend after authentication
import sentry_sdk

sentry_sdk.set_user({
    "id": user.id,
    "email": user.email,
    "role": user.role
})
```

### 6. Verify Installation

#### Backend Verification

1. Start the backend: `python main.py`
2. Check logs for: `"Sentry initialized for environment: [env]"`
3. Trigger a test error
4. Check Sentry dashboard: **Issues** → Should see new error

#### Frontend Verification

1. Start frontend: `npm run dev`
2. Open browser DevTools → Console
3. Trigger a test error (throw Error)
4. Check Sentry dashboard: **Issues** → Should see new error
5. Check **Session Replay** → Should see recorded session

### 7. Production Deployment

#### Update Kubernetes Secrets

```bash
# Create production secrets file
cat > .env.production.secrets <<EOF
JWT_SECRET_KEY=$(openssl rand -base64 32)
DATABASE_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
SENTRY_DSN=https://your-backend-dsn@sentry.io/project-id
EOF

# Create Kubernetes secret
kubectl create secret generic realdiag-secrets \
  --from-env-file=.env.production.secrets \
  -n production

# Clean up secrets file
shred -u .env.production.secrets
```

#### Deploy Application

```bash
kubectl apply -f k8s/production-realdiag.yaml
```

#### Verify Deployment

```bash
# Check pods are running
kubectl get pods -n production

# Check Sentry initialization in logs
kubectl logs -n production deployment/realdiag-api | grep -i sentry
kubectl logs -n production deployment/realdiag-web | grep -i sentry

# Check for errors in Sentry dashboard
# Should see deployment marker and any startup errors
```

## Configuration Options

### Backend Sampling Rates

Control how much data is sent to Sentry:

```bash
# Default: 10% of requests traced
SENTRY_TRACES_SAMPLE_RATE=0.1

# Default: 10% of traces profiled
SENTRY_PROFILES_SAMPLE_RATE=0.1

# Set to 1.0 for 100% (not recommended for production)
# Set to 0.0 to disable
```

### Frontend Session Replay

Session replay captures user interactions. Privacy settings:

```javascript
// In frontend/utils/sentry.js
replaysSessionSampleRate: 0.1,  // 10% of sessions
replaysOnErrorSampleRate: 1.0,  // 100% of sessions with errors
```

Adjust these rates based on your traffic and Sentry plan limits.

### Sensitive Data Filtering

The application automatically filters:
- Authentication tokens
- Cookie values
- Authorization headers
- Password fields
- Credit card numbers (if applicable)

See `frontend/utils/sentry.js` for full configuration.

## Monitoring and Alerts

### Set Up Alerts

1. Go to **Alerts** → **Create Alert**
2. Recommended alerts:
   - **High Error Rate**: > 10 errors in 1 minute
   - **Critical Errors**: Any error with level=fatal
   - **Performance Degradation**: API response time > 2s
   - **User Impact**: Affected users > 100

### Dashboard Widgets

Create custom dashboards with:
- Error rate over time
- Most common errors
- Slowest endpoints
- Browser/OS distribution
- User impact metrics

### Release Tracking

Sentry automatically tracks releases using the `APP_VERSION` from your environment:

```bash
# Set in backend/main.py
release=f"realdiag@{os.getenv('APP_VERSION', '1.4.0')}"
```

View releases in Sentry: **Releases** → See deployments and error rates per version

## Troubleshooting

### Backend: No errors appearing

1. Check `SENTRY_DSN` is set: `echo $SENTRY_DSN`
2. Check logs for initialization: `grep -i sentry logs/app.log`
3. Verify DSN is correct: Should start with `https://`
4. Test with: `sentry_sdk.capture_message("Test")`

### Frontend: No errors appearing

1. Check browser console for Sentry errors
2. Verify `NEXT_PUBLIC_SENTRY_DSN` in build: `console.log(process.env.NEXT_PUBLIC_SENTRY_DSN)`
3. Check Network tab for requests to `sentry.io`
4. Rebuild app: `npm run build && npm start`

### Session Replay not working

1. Check you're on a Sentry plan that includes Session Replay
2. Verify sampling rates > 0
3. Check browser console for replay errors
4. Ensure you're not blocking third-party scripts

### Too many events (quota exceeded)

1. Reduce sampling rates:
   ```bash
   SENTRY_TRACES_SAMPLE_RATE=0.05  # 5%
   ```
2. Add error filtering (see `backend/main.py`)
3. Upgrade Sentry plan or request quota increase

## Cost Optimization

### Recommended Settings for Production

```bash
# Backend
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% tracing
SENTRY_PROFILES_SAMPLE_RATE=0.1  # 10% profiling

# Frontend
replaysSessionSampleRate: 0.1  # 10% of sessions
replaysOnErrorSampleRate: 1.0  # All error sessions
```

### Estimate Your Usage

- **Errors**: ~1,000-5,000/month for typical app
- **Transactions**: Depends on traffic (sample at 10%)
- **Session Replays**: Depends on traffic and sample rate

Check Sentry dashboard: **Settings** → **Usage & Billing**

## HIPAA Compliance

When handling medical data:

1. **Sign Sentry BAA**: Contact Sentry sales for Business Associate Agreement
2. **Enable Data Scrubbing**: Already configured in `utils/sentry.js`
3. **Limit PII**: Never log patient names, MRNs, or PHI
4. **Use Session Replay carefully**: Consider disabling or aggressive masking
5. **Audit Logs**: Enable Sentry audit logs for compliance

## Best Practices

1. **Add Context**: Use breadcrumbs for debugging
   ```python
   sentry_sdk.add_breadcrumb(
       category='user_action',
       message='User searched for symptom',
       level='info'
   )
   ```

2. **Tag Errors**: Add custom tags
   ```python
   sentry_sdk.set_tag("diagnostic_tree", "NEU-HEADACHE")
   ```

3. **Custom Fingerprints**: Group similar errors
   ```python
   sentry_sdk.set_tag("fingerprint", ["database-timeout"])
   ```

4. **Error Levels**: Use appropriate severity
   - `fatal`: Critical system failure
   - `error`: Expected errors (404, validation)
   - `warning`: Potential issues
   - `info`: Informational breadcrumbs

5. **Performance Monitoring**: Add custom transactions
   ```python
   with sentry_sdk.start_transaction(op="task", name="diagnostic_evaluation"):
       # Your code here
       pass
   ```

## Support

- **Sentry Documentation**: https://docs.sentry.io
- **Python SDK**: https://docs.sentry.io/platforms/python/
- **Next.js SDK**: https://docs.sentry.io/platforms/javascript/guides/nextjs/
- **RealDiag Issues**: https://github.com/bevroy/RealDiag-Software/issues

## Next Steps

After Sentry setup:
1. ✅ Sentry configured and tested
2. ⬜ Set up Sentry alerts
3. ⬜ Configure release tracking
4. ⬜ Review and adjust sampling rates based on usage
5. ⬜ Create custom Sentry dashboard
6. ⬜ Sign BAA if handling PHI (HIPAA)
