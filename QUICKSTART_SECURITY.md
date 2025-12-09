# Security Features - Quick Start Guide

## ⚡ Quick Setup (5 minutes)

### 1. Generate Encryption Key
```bash
python -m backend.services.encryption
# Copy the output: DATABASE_ENCRYPTION_KEY=xxxxx
```

### 2. Add to Environment
```bash
# Add to .env file
echo "DATABASE_ENCRYPTION_KEY=<your-key-here>" >> .env
```

### 3. Run Database Migration
```bash
python -m backend.migrations.add_mfa_rbac_columns
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Test Services
```bash
# Test encryption
python -c "from backend.services.encryption import encrypt_phi; print('✓ Encryption OK')"

# Test MFA
python -c "from backend.services.mfa_service import MFAService; print('✓ MFA OK')"

# Test RBAC
python -c "from backend.services.rbac_service import RBACService; print('✓ RBAC OK')"
```

---

## 🎯 What's Implemented

✅ **Client-Side Encryption** - IndexedDB data encrypted with Web Crypto API  
✅ **Database Encryption** - PHI fields encrypted with Fernet  
✅ **MFA/2FA** - TOTP with Google Authenticator compatibility  
✅ **RBAC** - 4 roles, 17+ permissions  
✅ **MFA API Endpoints** - Complete enrollment/verification flow  
✅ **Frontend Components** - MFASetup.jsx and MFALogin.jsx ready  

---

## 📋 What's Left (6 hours work)

### HIGH Priority (2 hours)

1. **Initialize Encryption on Login** (5 min)
   ```javascript
   // In login success handler
   import { generateSessionKey, storeEncryptionKey } from '../utils/crypto';
   const key = generateSessionKey();
   storeEncryptionKey(key);
   ```

2. **Apply RBAC to Endpoints** (30 min)
   ```python
   # Add to sensitive endpoints
   from backend.services.rbac_service import require_permission, Permission
   
   @router.get("/patients")
   @require_permission(Permission.PATIENT_READ)
   async def get_patients(...):
       ...
   ```

3. **Update Auth for MFA** (1 hour)
   - Modify login to check `user.mfa_enabled`
   - Return `mfa_required: true` flag
   - Create `/auth/verify-mfa` endpoint

### MEDIUM Priority (3 hours)

4. **MFA Account Settings Page** (1 hour)
   ```jsx
   import MFASetup from '../components/MFASetup';
   // Display MFASetup component in account settings
   ```

5. **MFA Login Flow** (1 hour)
   ```jsx
   import MFALogin from '../components/MFALogin';
   // Show MFALogin after password auth if MFA enabled
   ```

6. **Testing** (1 hour)
   - Create `backend/tests/test_security.py`
   - Test encryption, MFA, RBAC
   - Run integration tests

### LOW Priority (1 hour)

7. **Documentation** (1 hour)
   - Update API docs with MFA endpoints
   - Create user guide for MFA enrollment
   - Document RBAC roles

---

## 🔒 Security Features Summary

### IndexedDB Encryption
- **Algorithm**: AES-GCM 256-bit
- **Key Derivation**: PBKDF2 (100k iterations)
- **Encrypted**: Searches, Favorites, User Data
- **File**: `frontend/utils/crypto.js`

### Database Encryption
- **Algorithm**: Fernet (AES-128 + HMAC)
- **Encrypted**: 16 PHI fields (mrn, name, dob, ssn, etc.)
- **File**: `backend/services/encryption.py`
- **Env Var**: `DATABASE_ENCRYPTION_KEY`

### MFA/2FA
- **Algorithm**: TOTP (6-digit codes)
- **Compatible**: Google Authenticator, Authy, Microsoft Authenticator
- **Backup**: 10 recovery codes (hashed)
- **Files**: `backend/services/mfa_service.py`, `mfa_router.py`

### RBAC
- **Roles**: ADMIN (17 perms), PROVIDER (9), USER (3), GUEST (1)
- **Categories**: User, Patient, Diagnosis, EHR, System, API, Rules
- **File**: `backend/services/rbac_service.py`

---

## 🧪 Testing Commands

```bash
# Test encryption
python -m backend.services.encryption

# Test MFA token generation
python -c "
from backend.services.mfa_service import MFAService
s = MFAService()
secret = s.generate_secret()
token = s.get_current_token(secret)
print(f'Secret: {secret}')
print(f'Token: {token}')
print(f'Valid: {s.verify_token(secret, token)}')
"

# Test RBAC permissions
python -c "
from backend.services.rbac_service import RBACService, Role, Permission
rbac = RBACService()
print('ADMIN can read patients:', rbac.has_permission(Role.ADMIN, Permission.PATIENT_READ))
print('USER can write patients:', rbac.has_permission(Role.USER, Permission.PATIENT_WRITE))
"

# Start backend with new features
cd backend && uvicorn main:app --reload

# Test MFA API
curl -X POST http://localhost:8000/mfa/enroll \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📚 Documentation Files

- `SECURITY_SETUP.md` - Complete setup guide with architecture details
- `SECURITY_IMPLEMENTATION_STATUS.md` - Current status and remaining tasks
- `README.md` - Update with security features section

---

## 🚨 Important Notes

1. **DATABASE_ENCRYPTION_KEY**: Keep this secure! Lost key = lost data
2. **Backup Codes**: Users must download and save backup codes
3. **MFA Enrollment**: Optional but recommended for admin/provider roles
4. **RBAC**: Apply to all sensitive endpoints before production
5. **Testing**: Run full security test suite before deployment

---

## 🎉 Quick Win Checklist

- [ ] Generate `DATABASE_ENCRYPTION_KEY`
- [ ] Run database migration
- [ ] Test all three services (encryption, MFA, RBAC)
- [ ] Apply RBAC to 5 most sensitive endpoints
- [ ] Initialize encryption key on login
- [ ] Deploy and test MFA enrollment flow

**Time to Production-Ready**: ~6 hours remaining work

---

## 🆘 Troubleshooting

**"No module named 'pyotp'"**
```bash
pip install pyotp>=2.9.0 qrcode[pil]>=7.4.2
```

**"DATABASE_ENCRYPTION_KEY not found"**
```bash
python -m backend.services.encryption
# Copy output to .env file
```

**"Encryption key not available"**
```javascript
// Initialize on login
import { generateSessionKey, storeEncryptionKey } from './utils/crypto';
storeEncryptionKey(generateSessionKey());
```

---

For detailed information, see `SECURITY_SETUP.md`
