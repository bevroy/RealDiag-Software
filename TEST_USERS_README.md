# Test User Accounts - Quick Reference

## Created Test Accounts

Four test accounts have been created for testing different user roles and features:

### 1. Administrator Account
- **Email:** `admin@realdiag.org`
- **Password:** `Admin123!Test`
- **Name:** Admin User
- **Role:** Administrator
- **Permissions:** Full system access
- **Use for:** System configuration, user management, all features

### 2. Healthcare Provider Account
- **Email:** `provider@realdiag.org`
- **Password:** `Provider123!Test`
- **Name:** Dr. Sarah Provider
- **Specialty:** Internal Medicine
- **Institution:** Memorial Hospital
- **Role:** Provider
- **Permissions:** Patient data access, diagnostic tools, EHR integration
- **Use for:** Clinical workflow testing, patient management

### 3. Regular User (Doctor) Account
- **Email:** `doctor@example.com`
- **Password:** `Doctor123!Test`
- **Name:** Dr. John Smith
- **Specialty:** Cardiology
- **Institution:** City Medical Center
- **Role:** User
- **Permissions:** Personal data, diagnostic searches, favorites
- **Use for:** Standard doctor/clinician features

### 4. Patient Account
- **Email:** `patient@example.com`
- **Password:** `Patient123!Test`
- **Name:** Jane Patient
- **Role:** User
- **Permissions:** Personal health data access (read-only for most features)
- **Use for:** Patient portal testing, personal health records

## How to Use These Accounts

### Login via Web UI
1. Go to https://realdiag.netlify.app/account
2. Enter email and password from above
3. Click "Sign In"

### Login via API (for developers)
```bash
curl -X POST https://realdiag-software.onrender.com/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@example.com",
    "password": "Doctor123!Test"
  }'
```

## Features to Test

### For All Users
- ✅ Login/Logout
- ✅ Profile management
- ✅ Symptom search
- ✅ Diagnostic tree browsing
- ✅ Favorites
- ✅ Search history

### For Healthcare Providers
- ✅ Patient data access
- ✅ EHR integration features
- ✅ Advanced diagnostic tools
- ✅ Export functionality

### For Admin Users
- ✅ User management
- ✅ System configuration
- ✅ API key management
- ✅ Analytics dashboard

### Patient-Specific Features
- ✅ Personal health record access
- ✅ Symptom checker (patient-friendly)
- ✅ Educational content
- ✅ Appointment requests (if implemented)

## Testing Patient Features

To test patient-specific functionality:

1. **Login as patient:**
   - Email: `patient@example.com`
   - Password: `Patient123!Test`

2. **Test these pages:**
   - `/account` - Personal account dashboard
   - `/symptom-search` - Symptom search (patient view)
   - `/education` - Educational resources
   - `/diagnose` - Interactive diagnostic tools

3. **Verify patient permissions:**
   - Cannot access provider-only features
   - Cannot modify clinical data
   - Has read-only access to personal health information

## Security Notes

⚠️ **Important:**
- These are TEST accounts only
- Do not use these credentials in production
- Change passwords before deploying to production
- Employee emails (@realdiag.org) may require email verification

## Re-running the Script

To recreate or add more test users:

```bash
# Production backend
python3 scripts/create_test_users.py

# Local development
python3 scripts/create_test_users.py --local

# Custom backend URL
python3 scripts/create_test_users.py --url http://your-backend-url.com
```

## Stored Credentials

All credentials are saved in `test_users_credentials.json` for easy reference:

```json
{
  "backend_url": "https://realdiag-software.onrender.com",
  "users": [
    {
      "email": "admin@realdiag.org",
      "password": "Admin123!Test",
      "full_name": "Admin User",
      "role": "Administrator"
    },
    ...
  ]
}
```

## Support

If you encounter issues:
1. Check that the backend is running
2. Verify the email hasn't been used before
3. Check browser console for error messages
4. Review backend logs for authentication errors

---

*Last Updated: January 5, 2026*
