# Security Features Setup Guide

This document describes the comprehensive security features implemented in RealDiag and how to set them up.

## Table of Contents

1. [Overview](#overview)
2. [Client-Side Encryption (IndexedDB)](#client-side-encryption-indexeddb)
3. [Database Field Encryption](#database-field-encryption)
4. [Multi-Factor Authentication (MFA)](#multi-factor-authentication-mfa)
5. [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
6. [Setup Instructions](#setup-instructions)
7. [Testing](#testing)

---

## Overview

RealDiag implements multiple layers of security:

- **Client-Side Encryption**: IndexedDB data encrypted with Web Crypto API (AES-GCM 256-bit)
- **Database Encryption**: PHI/PII encrypted at rest using Fernet (AES-128)
- **Multi-Factor Authentication**: TOTP-based 2FA compatible with Google Authenticator
- **Role-Based Access Control**: 4 roles (ADMIN, PROVIDER, USER, GUEST) with 17+ permissions

These features address OWASP Top 10 vulnerabilities:
- **A01 Broken Access Control**: RBAC with granular permissions
- **A02 Cryptographic Failures**: Encryption at rest and in transit
- **A04 Insecure Design**: Defense in depth with multiple security layers
- **A07 Identification/Authentication Failures**: MFA strengthens authentication

---

## Client-Side Encryption (IndexedDB)

### Architecture

**Technology**: Web Crypto API  
**Algorithm**: AES-GCM 256-bit  
**Key Derivation**: PBKDF2 with SHA-256 (100,000 iterations)

### What Gets Encrypted

- **Searches**: May contain patient symptom information (PHI)
- **Favorites**: May contain patient context
- **User Data**: May contain sensitive settings/preferences
- **Rules**: Not encrypted (public medical knowledge)

### How It Works

```javascript
// Encryption flow
1. User logs in → Generate session encryption key
2. Key stored in sessionStorage (cleared on logout)
3. Data encrypted before IndexedDB storage
4. Data decrypted on retrieval
5. Key destroyed on logout
```

### Implementation

**Files**:
- `frontend/utils/crypto.js` - Encryption utilities
- `frontend/utils/offlineManager.js` - IndexedDB manager with encryption

**Example Usage**:

```javascript
import { generateSessionKey, storeEncryptionKey } from './utils/crypto';
import { saveSearch } from './utils/offlineManager';

// On login
const encryptionKey = generateSessionKey();
storeEncryptionKey(encryptionKey);

// Automatically encrypts if key available
await saveSearch({
  symptoms: ['headache', 'fever'],
  diagnosis: 'Migraine',
  timestamp: Date.now()
});
```

### Security Properties

✓ **Forward Secrecy**: Each session uses a unique key  
✓ **At-Rest Protection**: Data unreadable without session key  
✓ **Salt + IV**: Unique per record (prevents rainbow tables)  
✓ **Graceful Degradation**: Falls back to unencrypted if key unavailable

---

## Database Field Encryption

### Architecture

**Technology**: Python `cryptography` library  
**Algorithm**: Fernet (AES-128 CBC + HMAC-SHA256)  
**Key Management**: Environment variable (`DATABASE_ENCRYPTION_KEY`)

### What Gets Encrypted

**PHI_FIELDS** (16 sensitive fields):
- Patient identifiers: `mrn`, `name`, `date_of_birth`, `ssn`
- Contact info: `address`, `phone`, `email`, `emergency_contact`
- Medical data: `medications`, `allergies`, `medical_history`, `diagnosis_notes`
- Insurance: `insurance_id`, `insurance_provider`
- Other: `notes`, `comments`

### How It Works

```python
# Encryption flow
1. Application reads DATABASE_ENCRYPTION_KEY from .env
2. Data encrypted before INSERT/UPDATE
3. Data decrypted after SELECT
4. Key never logged or exposed
```

### Implementation

**Files**:
- `backend/services/encryption.py` - Encryption service

**Example Usage**:

```python
from backend.services.encryption import encrypt_phi, decrypt_phi

# Encrypt patient data before saving
patient_data = {
    'mrn': '12345',
    'name': 'John Doe',
    'dob': '1980-01-01',
    'diagnosis': 'Hypertension'
}

encrypted_data = encrypt_phi(patient_data)
# {'mrn': 'gAAAAB...', 'name': 'gAAAAB...', ...}

# Decrypt when retrieving
decrypted_data = decrypt_phi(encrypted_data)
# {'mrn': '12345', 'name': 'John Doe', ...}
```

### Key Generation

```bash
# Generate new encryption key
python -m backend.services.encryption

# Output: DATABASE_ENCRYPTION_KEY=<base64-encoded-key>
```

### Security Properties

✓ **HIPAA Compliant**: PHI encrypted at rest  
✓ **Authenticated Encryption**: HMAC prevents tampering  
✓ **Key Rotation**: Supports gradual key migration  
✓ **Selective Encryption**: Only sensitive fields encrypted

---

## Multi-Factor Authentication (MFA)

### Architecture

**Technology**: pyotp (Python OTP library)  
**Algorithm**: TOTP (Time-based One-Time Password)  
**Compatibility**: Google Authenticator, Authy, Microsoft Authenticator, 1Password

### How It Works

```
1. User enrolls in MFA → Server generates TOTP secret
2. QR code displayed → User scans with authenticator app
3. User enters 6-digit code → Server verifies
4. MFA enabled → Subsequent logins require code
5. Backup codes provided → Emergency access if device lost
```

### API Endpoints

```
POST   /mfa/enroll                    - Enroll in MFA
POST   /mfa/verify                    - Verify TOTP token
POST   /mfa/verify-backup             - Verify backup code
DELETE /mfa/disable                   - Disable MFA
GET    /mfa/status                    - Get MFA status
POST   /mfa/regenerate-backup-codes   - Generate new backup codes
```

### Implementation

**Backend Files**:
- `backend/services/mfa_service.py` - MFA service
- `backend/services/mfa_router.py` - API endpoints

**Frontend Files**:
- `frontend/components/MFASetup.jsx` - Enrollment UI
- `frontend/components/MFALogin.jsx` - Login verification

### User Flow

**Enrollment**:
1. Navigate to account settings
2. Click "Enable Two-Factor Authentication"
3. Scan QR code with authenticator app
4. Download backup codes
5. Enter 6-digit code to verify setup

**Login**:
1. Enter username/password (normal login)
2. If MFA enabled → Prompt for 6-digit code
3. Enter code from authenticator app
4. Access granted

### Security Properties

✓ **NIST Compliant**: Follows SP 800-63B guidelines  
✓ **Time-Based**: Codes expire every 30 seconds  
✓ **Backup Codes**: 10 single-use recovery codes  
✓ **Hashed Storage**: Backup codes stored as SHA-256 hashes

---

## Role-Based Access Control (RBAC)

### Architecture

**Roles**: ADMIN, PROVIDER, USER, GUEST  
**Permissions**: 17+ granular permissions across 7 categories

### Role Permissions Matrix

| Permission | ADMIN | PROVIDER | USER | GUEST |
|------------|-------|----------|------|-------|
| USER_READ | ✓ | ✓ | ✓ | - |
| USER_WRITE | ✓ | - | - | - |
| USER_DELETE | ✓ | - | - | - |
| PATIENT_READ | ✓ | ✓ | - | - |
| PATIENT_WRITE | ✓ | ✓ | - | - |
| PATIENT_DELETE | ✓ | - | - | - |
| DIAGNOSIS_READ | ✓ | ✓ | ✓ | - |
| DIAGNOSIS_WRITE | ✓ | ✓ | - | - |
| DIAGNOSIS_EXPORT | ✓ | ✓ | ✓ | - |
| EHR_READ | ✓ | ✓ | - | - |
| EHR_WRITE | ✓ | ✓ | - | - |
| SYSTEM_CONFIG | ✓ | - | - | - |
| SYSTEM_LOGS | ✓ | - | - | - |
| SYSTEM_BACKUP | ✓ | - | - | - |
| API_KEY_CREATE | ✓ | - | - | - |
| API_KEY_DELETE | ✓ | - | - | - |
| RULES_READ_PUBLIC | ✓ | ✓ | ✓ | ✓ |

### Implementation

**Files**:
- `backend/services/rbac_service.py` - RBAC service with decorators

### Protecting Endpoints

```python
from backend.services.rbac_service import require_permission, require_role, Permission, Role

# Protect by permission
@app.get("/patients")
@require_permission(Permission.PATIENT_READ)
async def get_patients(current_user = Depends(get_current_user)):
    return patients

# Protect by role
@app.post("/admin/config")
@require_role(Role.ADMIN)
async def update_config(current_user = Depends(get_current_user)):
    return config
```

### Security Properties

✓ **Principle of Least Privilege**: Minimal permissions by default  
✓ **Separation of Duties**: Admins ≠ Providers ≠ Users  
✓ **Audit Ready**: All permission checks logged  
✓ **Extensible**: Easy to add new roles/permissions

---

## Setup Instructions

### 1. Database Migration

Add MFA and RBAC columns to users table:

```bash
# Run migration
python -m backend.migrations.add_mfa_rbac_columns

# Or use Supabase SQL editor
python -m backend.migrations.add_mfa_rbac_columns --sql-only
```

### 2. Generate Encryption Key

```bash
# Generate DATABASE_ENCRYPTION_KEY
python -m backend.services.encryption

# Add to .env
echo "DATABASE_ENCRYPTION_KEY=<generated-key>" >> .env
```

### 3. Install Dependencies

```bash
# Install new packages
pip install -r requirements.txt

# Verify installation
python -c "import pyotp, qrcode; print('MFA dependencies OK')"
```

### 4. Update Frontend

No build required if using JSX/React components:

```javascript
// Import in account settings page
import MFASetup from '../components/MFASetup';

// Import in login page
import MFALogin from '../components/MFALogin';
```

### 5. Apply RBAC to Endpoints

```python
# Add decorators to sensitive endpoints
from backend.services.rbac_service import require_permission, Permission

@app.get("/api/patients")
@require_permission(Permission.PATIENT_READ)
async def get_patients(...):
    ...
```

### 6. Initialize Encryption on Login

```javascript
// In login success handler
import { generateSessionKey, storeEncryptionKey } from './utils/crypto';

async function onLoginSuccess() {
  const encryptionKey = generateSessionKey();
  storeEncryptionKey(encryptionKey);
  // Continue with normal login flow
}
```

---

## Testing

### Test Encryption

```bash
# Test database encryption
python -m backend.services.encryption

# Test MFA service
python -m backend.services.mfa_service

# Test RBAC service
python -m backend.services.rbac_service
```

### Test MFA Flow

```bash
# Start backend
cd backend && uvicorn main:app --reload

# Enroll in MFA
curl -X POST http://localhost:8000/mfa/enroll \
  -H "Authorization: Bearer <token>"

# Verify token
curl -X POST http://localhost:8000/mfa/verify \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"token": "123456"}'
```

### Test RBAC

```python
# In Python shell
from backend.services.rbac_service import RBACService, Role, Permission

rbac = RBACService()

# Check permissions
rbac.has_permission(Role.ADMIN, Permission.PATIENT_READ)  # True
rbac.has_permission(Role.USER, Permission.PATIENT_WRITE)  # False
```

### Integration Tests

```bash
# Run full security test suite
pytest backend/tests/test_security.py -v

# Test coverage
pytest --cov=backend/services backend/tests/test_security.py
```

---

## Compliance Checklist

- [ ] **HIPAA**: PHI encrypted at rest ✓
- [ ] **SOC 2**: RBAC implemented ✓
- [ ] **SOC 2**: MFA available ✓
- [ ] **OWASP A01**: Access control enforced ✓
- [ ] **OWASP A02**: Cryptographic failures mitigated ✓
- [ ] **OWASP A07**: Strong authentication (MFA) ✓
- [ ] **NIST SP 800-63B**: TOTP implementation compliant ✓

---

## Key Rotation

### Database Encryption Key

```bash
# Generate new key
python -m backend.services.encryption

# Gradual migration
1. Add NEW_DATABASE_ENCRYPTION_KEY to .env
2. Decrypt with old key, re-encrypt with new key
3. Update DATABASE_ENCRYPTION_KEY to new value
4. Remove old key
```

### MFA Secret Reset

Users can disable and re-enable MFA to get a new secret:

```
1. User: Account Settings → Disable MFA
2. User: Enable MFA → New secret generated
3. User: Scan new QR code
4. Old secret invalidated
```

---

## Troubleshooting

### "Encryption key not found"

**Cause**: Session encryption key not initialized  
**Solution**: Generate and store key on login

```javascript
import { generateSessionKey, storeEncryptionKey } from './utils/crypto';
const key = generateSessionKey();
storeEncryptionKey(key);
```

### "Invalid MFA token"

**Cause**: Clock skew between server and authenticator  
**Solution**: Verify system time is synchronized (NTP)

```bash
# Check system time
timedatectl

# Sync time (Ubuntu)
sudo timedatectl set-ntp true
```

### "Permission denied"

**Cause**: User role lacks required permission  
**Solution**: Update user role in database

```sql
UPDATE users SET role = 'provider' WHERE email = 'user@example.com';
```

---

## Support

For security issues, contact: security@realdiag.com

**DO NOT** share encryption keys or MFA secrets in public channels.
