# RealDiag Test Environment

## 🎯 Quick Start

Set up the test environment in 3 steps:

```bash
# 1. Run setup script
./setup_test_environment.sh

# 2. Start backend (Terminal 1)
./start_backend_test.sh

# 3. Start frontend (Terminal 2)  
./start_frontend_test.sh
```

Access at: http://localhost:3000

## 📋 What You Get

In test environment, ALL users have:

- ✅ **Enterprise-level access** to all features
- ✅ **Unlimited diagnostic searches** 
- ✅ **Unlimited API calls**
- ✅ **No payment required**
- ✅ **No subscription restrictions**
- ✅ **All premium features unlocked**

## 🔧 Manual Setup

If the script doesn't work, follow these manual steps:

### 1. Environment Configuration

```bash
cp .env.test .env
```

### 2. Database (Optional)

```bash
createdb realdiag_test
```

### 3. Backend

```bash
cd backend
pip install -r requirements.txt
export ENVIRONMENT=test
uvicorn main:app --reload --port 8000
```

### 4. Frontend

```bash
cd frontend
npm install
export NEXT_PUBLIC_ENVIRONMENT=test
npm run dev
```

## ✅ Verify Test Mode

Check the health endpoint:

```bash
curl http://localhost:8000/health | jq
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "test",
  "test_mode": true,
  "test_info": {
    "subscription_checks": "bypassed",
    "user_access_level": "enterprise",
    "rate_limiting": "disabled"
  }
}
```

## 🧪 Testing Guidelines

### For Beta Testers

1. **Register a new account** - Use your real email
2. **Test all features** - Explore everything freely
3. **Report bugs** - Use GitHub issues or feedback form
4. **Document your workflow** - Help us improve UX
5. **Try edge cases** - Break things if you can!

### What to Test

- [ ] User registration and login
- [ ] Symptom search accuracy
- [ ] Diagnostic recommendations
- [ ] Health record integration
- [ ] Wearable device sync
- [ ] Report generation and export
- [ ] Mobile responsiveness
- [ ] Performance and loading times

## 🚨 Important Notes

### ⚠️ This is a TEST Environment

- Data may be reset without notice
- Not suitable for real medical decisions
- Do not enter real patient data
- Performance may vary

### 🔒 Security

- Use test credentials only
- Authentication is still required
- User data is isolated
- No real payments will be processed

## 📊 Monitoring

### Backend Logs

```bash
# Watch backend logs
tail -f backend/logs/app.log

# Check test mode status
grep "TEST MODE" backend/logs/app.log
```

### Frontend Console

Open browser DevTools → Console

Look for:
```
[TEST MODE] Environment: test
[TEST MODE] Unlimited access enabled
```

## 🐛 Troubleshooting

### Test Mode Not Active

**Problem**: Backend shows production mode

**Solution**:
```bash
# Verify .env file
cat .env | grep ENVIRONMENT
# Should show: ENVIRONMENT=test

# Restart backend
pkill -f uvicorn
./start_backend_test.sh
```

### Still Seeing Subscription Limits

**Problem**: Features are locked

**Solution**:
```bash
# Check environment variables
echo $ENVIRONMENT
echo $BYPASS_SUBSCRIPTION_CHECKS

# Verify API response
curl http://localhost:8000/health

# Clear browser cache
# Restart both frontend and backend
```

### Port Already in Use

**Problem**: `Address already in use` error

**Solution**:
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --reload --port 8001
```

### Database Connection Error

**Problem**: Can't connect to database

**Solution**:
```bash
# Check PostgreSQL is running
pg_isready

# Verify database exists
psql -l | grep realdiag_test

# Check connection string in .env
cat .env | grep DATABASE_URL
```

## 📝 Feedback

### How to Report Issues

1. **GitHub Issues**: https://github.com/bevroy/RealDiag-Software/issues
2. **Email**: testing@realdiag.com
3. **In-App**: Click feedback button (if available)

### What to Include

- Steps to reproduce
- Expected vs actual behavior
- Screenshots/videos
- Browser/device info
- Error messages from console

## 📚 Documentation

- [Full Test Environment Guide](docs/TEST_ENVIRONMENT.md)
- [API Documentation](http://localhost:8000/docs)
- [User Guide](docs/USER_GUIDE.md)
- [Developer Guide](CONTRIBUTING.md)

## 🔄 Switching Modes

### Test → Development

```bash
# Edit .env
ENVIRONMENT=development
BYPASS_SUBSCRIPTION_CHECKS=false

# Restart services
```

### Test → Production

⚠️ **NEVER deploy test mode to production!**

```bash
# Edit .env
ENVIRONMENT=production
FREE_ACCESS_TESTING=false
BYPASS_SUBSCRIPTION_CHECKS=false

# Verify
curl https://api.realdiag.com/health
# test_mode should be false
```

## 🤝 Contributing

Found a bug or have a suggestion?

1. Check existing issues
2. Create a new issue with `[TEST]` prefix
3. Include reproduction steps
4. Add `test-environment` label

## 📞 Support

- **Testing Support**: testing@realdiag.com
- **Technical Issues**: support@realdiag.com
- **Slack**: #test-environment channel

## 🎉 Thank You!

Thank you for helping us test RealDiag! Your feedback makes a huge difference in improving the platform.

---

**Last Updated**: December 10, 2025  
**Test Environment Version**: 1.0.0
