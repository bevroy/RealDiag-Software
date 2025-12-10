# RealDiag Test Environment Guide

## Overview

This guide explains how to set up and use the RealDiag test environment for real-world testing with free access to all features.

## Purpose

The test environment allows:
- ✅ Real-world testing without subscription restrictions
- ✅ Free access to all enterprise-level features
- ✅ Testing user workflows end-to-end
- ✅ Collecting feedback from beta testers
- ✅ Quality assurance before production deployment
- ✅ No payment or billing required

## Setup Instructions

### 1. Environment Configuration

Copy the test environment configuration:

```bash
cp .env.test .env
```

Or set these key variables in your `.env` file:

```bash
ENVIRONMENT=test
FREE_ACCESS_TESTING=true
BYPASS_SUBSCRIPTION_CHECKS=true
```

### 2. Database Setup (Optional)

For isolated testing, use a separate test database:

```bash
# Create test database
createdb realdiag_test

# Set in .env
DATABASE_URL=postgresql://user:password@localhost:5432/realdiag_test
```

### 3. Start Backend (Test Mode)

```bash
cd backend
uvicorn main:app --reload --port 8000
```

The backend will detect `ENVIRONMENT=test` and enable test mode automatically.

### 4. Start Frontend (Test Mode)

```bash
cd frontend
npm run dev
```

### 5. Verify Test Mode

Check the API health endpoint:

```bash
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "environment": "test",
  "test_mode": true,
  "subscription_checks": "bypassed"
}
```

## Features in Test Mode

### Unlimited Access

All users in test mode automatically receive:
- ✅ **Enterprise-level access** to all features
- ✅ **Unlimited diagnostic searches** (no rate limits)
- ✅ **Unlimited API calls** (no throttling)
- ✅ **All premium features unlocked**
- ✅ **No payment required**
- ✅ **No subscription checks**

### Test Mode Indicators

When test mode is active, API responses include:

```json
{
  "data": "...",
  "_test_mode": true,
  "_test_access": "unlimited",
  "_environment": "test"
}
```

### Disabled Features in Test Mode

For safety and simplicity:
- ❌ Payment processing (Stripe disabled)
- ❌ Production email sending (use test SMTP or mock)
- ❌ Rate limiting (unlimited requests)
- ❌ Sentry error tracking (disabled)
- ❌ Analytics tracking (disabled)

## Test User Accounts

### Creating Test Users

Test users are automatically granted enterprise access:

```bash
# Register a new test user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "tester@example.com",
    "password": "TestPassword123!",
    "name": "Test User"
  }'
```

### Pre-configured Test Accounts

The `.env.test` file includes:

```
TEST_USER_EMAIL=testuser@realdiag.com
TEST_USER_PASSWORD=TestPassword123!
TEST_ADMIN_EMAIL=admin@realdiag.com
TEST_ADMIN_PASSWORD=AdminPassword123!
```

## Testing Checklist

### Core Functionality

- [ ] User registration and login
- [ ] Diagnostic symptom search
- [ ] Decision tree evaluation
- [ ] Health record integration
- [ ] Wearable device sync
- [ ] Medical history tracking
- [ ] Report generation
- [ ] Export functionality

### Premium Features

- [ ] Bulk diagnostic exports
- [ ] API access
- [ ] Advanced analytics
- [ ] Priority support access
- [ ] Custom integrations
- [ ] Multi-user organization features

### User Experience

- [ ] Navigation and UI/UX
- [ ] Mobile responsiveness
- [ ] Loading times
- [ ] Error handling
- [ ] Help documentation
- [ ] Accessibility features

## Collecting Feedback

### Enable Test Mode Logging

Test mode automatically logs all activities:

```python
from backend.services.test_environment import log_test_mode_activity

log_test_mode_activity(
    action="diagnostic_search",
    user_id="user123",
    details={"query": "chest pain", "results": 5}
)
```

### Feedback Form Integration

Add a feedback widget to your frontend in test mode:

```javascript
if (process.env.NEXT_PUBLIC_ENVIRONMENT === 'test') {
  // Show feedback button
  <FeedbackButton />
}
```

## Switching Between Environments

### Development → Test

```bash
# In .env file
ENVIRONMENT=test
```

Restart the backend.

### Test → Production

⚠️ **IMPORTANT**: Never deploy test mode to production!

```bash
# In .env file
ENVIRONMENT=production
FREE_ACCESS_TESTING=false
BYPASS_SUBSCRIPTION_CHECKS=false
```

### Environment Detection

Backend automatically detects environment:

```python
from backend.services.test_environment import is_test_mode

if is_test_mode():
    print("Running in test environment - unlimited access enabled")
```

## Monitoring Test Environment

### Check Active Mode

```bash
# Backend logs will show
[INFO] Environment: test
[INFO] Test mode: ENABLED
[INFO] Subscription checks: BYPASSED
[INFO] All users granted: ENTERPRISE access
```

### API Health Check

```bash
curl http://localhost:8000/health | jq
```

Expected output:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "test",
  "test_mode": true,
  "features": {
    "subscription_checks": false,
    "rate_limiting": false,
    "payment_processing": false
  }
}
```

## Security Considerations

### Test Mode Safety

- ✅ Test mode is **automatically disabled** in production
- ✅ Environment variable must be explicitly set to `test`
- ✅ Cannot accidentally enable test mode via API
- ✅ Test mode status logged in all requests

### Data Isolation

- Use separate test database
- Test data should not affect production
- Clear test data regularly
- Mock external service integrations

### Access Control

While subscription checks are bypassed:
- ✅ Authentication is still required
- ✅ User isolation is maintained
- ✅ Data privacy is preserved
- ✅ API security headers still active

## Troubleshooting

### Test Mode Not Activating

1. Check `.env` file has `ENVIRONMENT=test`
2. Restart backend server
3. Clear browser cache
4. Check backend logs for environment confirmation

### Still Seeing Subscription Restrictions

1. Verify `BYPASS_SUBSCRIPTION_CHECKS=true`
2. Check API response includes `"_test_mode": true`
3. Restart the application
4. Check for import errors in test_environment.py

### Database Issues

```bash
# Reset test database
dropdb realdiag_test
createdb realdiag_test
python backend/scripts/migrate.py
```

## Best Practices

### For Testers

1. **Realistic Usage**: Test as if you were a real user
2. **Document Issues**: Report bugs with steps to reproduce
3. **Explore Features**: Try all features, even edge cases
4. **Provide Feedback**: Share both positive and negative experiences
5. **Test on Multiple Devices**: Mobile, tablet, desktop

### For Developers

1. **Regular Monitoring**: Check test environment logs daily
2. **Quick Fixes**: Address critical bugs immediately
3. **Clear Communication**: Update testers on fixes and changes
4. **Data Cleanup**: Regularly clear test data
5. **Performance Tracking**: Monitor response times and errors

## Exiting Test Mode

When testing is complete:

1. **Backup Test Data** (if needed)
   ```bash
   pg_dump realdiag_test > test_backup.sql
   ```

2. **Switch to Production Mode**
   ```bash
   ENVIRONMENT=production
   BYPASS_SUBSCRIPTION_CHECKS=false
   ```

3. **Verify Production Settings**
   ```bash
   curl https://api.realdiag.com/health
   # Should NOT show test_mode: true
   ```

4. **Monitor Production Logs**
   - Ensure no test mode indicators
   - Verify subscription checks are active
   - Confirm payment processing works

## Support

For test environment issues:

- **Email**: testing@realdiag.com
- **Slack**: #test-environment
- **GitHub**: Open issue with `test-environment` label

## Changelog

- **2025-12-10**: Initial test environment setup
- Added test mode middleware
- Implemented subscription bypass logic
- Created test environment documentation

---

**Remember**: Test mode provides free access for testing only. Production deployment requires proper subscription handling.
