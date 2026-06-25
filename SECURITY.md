# Security Policy

## 🔒 Security Overview

RealDiag-Software is a **clinical decision support tool** that handles sensitive medical information. This document outlines security considerations, data protection measures, and responsible disclosure procedures.

---

## ⚠️ CRITICAL SECURITY WARNINGS

### 1. Not FDA Approved
- **This software is NOT FDA-approved** for clinical use
- Not a substitute for professional medical judgment
- Not validated for diagnostic accuracy in clinical settings
- Should only be used as a **supplemental educational tool**

### 2. HIPAA Compliance
**CURRENT STATUS: NOT HIPAA COMPLIANT**

This software currently **does NOT meet HIPAA requirements** for protected health information (PHI). Do not use in production healthcare environments without implementing:

- ✅ Encryption at rest and in transit
- ✅ Access controls and audit logs
- ✅ Business Associate Agreements (BAAs)
- ✅ Patient consent mechanisms
- ✅ Data retention and destruction policies
- ✅ Breach notification procedures
- ✅ Security risk assessments

### 3. Patient Data Storage
**CURRENT IMPLEMENTATION:**
- Patient data stored temporarily in browser memory
- No persistent storage of PHI in current version
- Barcode scanner stores patient IDs in memory only
- Search history saved to IndexedDB without encryption

**REQUIREMENTS FOR PRODUCTION USE:**
- Implement end-to-end encryption for all PHI
- Secure database with encryption at rest
- TLS 1.2+ for all data transmission
- Regular security audits
- Penetration testing

---

## 🛡️ Current Security Measures

### 1. Authentication & Authorization
**Status: Basic Implementation**

```javascript
// Current: Simple JWT tokens (NOT production-ready)
localStorage.getItem('realdiag_token'); // ⚠️ Vulnerable to XSS

// REQUIRED FOR PRODUCTION:
// - HttpOnly cookies
// - Refresh tokens
// - Multi-factor authentication (MFA)
// - Role-based access control (RBAC)
```

**Known Issues:**
- JWT stored in localStorage (vulnerable to XSS attacks)
- No token expiration/refresh mechanism
- No MFA support
- API keys stored in-memory dictionary (not persistent)

### 2. Data Transmission
**Status: HTTPS Required**

- All API endpoints require HTTPS in production
- No plain HTTP in deployment environments
- CORS configured for specific origins only

**Known Issues:**
- Dev environment allows HTTP
- No certificate pinning
- Missing HSTS headers

### 3. Input Validation
**Status: Basic Validation**

```python
# Current validation (backend/services/diagnostic_router.py)
symptoms: List[str]  # No length/content validation
age: Optional[int]   # No range validation
```

**Vulnerabilities:**
- No input sanitization for XSS
- No SQL injection protection (using ORMs helps but not complete)
- No rate limiting on endpoints
- No request size limits

### 4. API Security
**Status: API Key Authentication**

```python
# backend/services/integration_router.py
api_keys_db = {}  # ⚠️ In-memory only, lost on restart
```

**Known Issues:**
- API keys not persisted to database
- No key rotation mechanism
- No rate limiting per key
- No IP whitelisting
- Secrets stored in plain text

### 5. Service Worker & Offline Storage
**Status: Client-Side Storage**

```javascript
// frontend/utils/offlineManager.js
// IndexedDB stores:
// - rules (diagnostic rules)
// - searches (search history)
// - favorites (user favorites)
// - syncQueue (pending requests)
// - userData (user preferences)
```

**Vulnerabilities:**
- No encryption of IndexedDB data
- Accessible via browser DevTools
- No data expiration policy
- No secure deletion

---

## 🚨 Known Vulnerabilities

### HIGH SEVERITY

1. **XSS (Cross-Site Scripting)**
   - JWT tokens in localStorage
   - No Content Security Policy (CSP)
   - User input not sanitized in voice transcripts

2. **Sensitive Data Exposure**
   - Patient IDs stored unencrypted
   - Search history contains symptoms (potential PHI)
   - API keys in plain text

3. **Insufficient Authentication**
   - No session timeout
   - No logout invalidation
   - API keys not rotated

### MEDIUM SEVERITY

1. **Missing Rate Limiting**
   - No throttling on API endpoints
   - No protection against brute force
   - No CAPTCHA on login

2. **Insufficient Logging**
   - No audit trail for PHI access
   - No security event logging
   - No breach detection

3. **Dependency Vulnerabilities**
   - Dependencies may have known CVEs
   - No automated security scanning
   - No SCA (Software Composition Analysis)

### LOW SEVERITY

1. **Information Disclosure**
   - Verbose error messages in dev mode
   - API version exposed in headers
   - Stack traces returned to client

2. **Missing Security Headers**
   - No X-Frame-Options
   - No X-Content-Type-Options
   - No Content-Security-Policy

---

## 🔐 Hardening Recommendations

### For Production Deployment

#### 1. Encryption
```bash
# Generate SSL certificates
certbot --nginx -d yourdomain.com

# Enable database encryption
# PostgreSQL: Enable SSL and column encryption
# MongoDB: Enable encryption at rest
```

#### 2. Secure Authentication
```javascript
// Use HttpOnly cookies instead of localStorage
res.cookie('token', jwtToken, {
  httpOnly: true,
  secure: true,
  sameSite: 'strict',
  maxAge: 15 * 60 * 1000 // 15 minutes
});
```

#### 3. Environment Variables
```bash
# NEVER commit these to version control
MONGODB_URI=mongodb+srv://user:SECURE_PASSWORD@cluster.mongodb.net/
JWT_SECRET=GENERATE_WITH_openssl_rand_hex_64
API_KEY_ENCRYPTION_KEY=GENERATE_STRONG_KEY
FHIR_CLIENT_SECRET=PROVIDER_SPECIFIC_SECRET
```

#### 4. Rate Limiting
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/search")
@limiter.limit("10/minute")
async def search_endpoint():
    pass
```

#### 5. Input Validation
```python
from pydantic import validator, constr, conint

class SearchRequest(BaseModel):
    symptoms: List[constr(max_length=100)] = Field(..., max_items=20)
    age: Optional[conint(ge=0, le=120)] = None
    
    @validator('symptoms')
    def sanitize_symptoms(cls, v):
        return [bleach.clean(s) for s in v]
```

#### 6. Security Headers
```python
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

---

## 📊 Security Audit Checklist

### Pre-Production Requirements

- [ ] **HIPAA Compliance Review**
  - [ ] Business Associate Agreement (BAA) with hosting provider
  - [ ] Risk assessment completed
  - [ ] Security policies documented
  - [ ] Employee training completed
  - [ ] Incident response plan

- [ ] **Data Protection**
  - [ ] Database encryption at rest
  - [ ] TLS 1.3 for all connections
  - [ ] Encrypted backups
  - [ ] Secure key management (AWS KMS, Azure Key Vault)
  - [ ] Data retention policy

- [ ] **Authentication & Authorization**
  - [ ] Multi-factor authentication (MFA)
  - [ ] Role-based access control (RBAC)
  - [ ] OAuth 2.0 / OIDC integration
  - [ ] Session management
  - [ ] Password policies

- [ ] **Monitoring & Logging**
  - [ ] Centralized logging (ELK, Splunk)
  - [ ] PHI access audit logs
  - [ ] Security event monitoring
  - [ ] Intrusion detection (IDS)
  - [ ] Breach notification procedures

- [ ] **Testing**
  - [ ] Penetration testing
  - [ ] Vulnerability scanning
  - [ ] Security code review
  - [ ] Dependency scanning (Snyk, Dependabot)
  - [ ] OWASP Top 10 compliance

- [ ] **Legal & Compliance**
  - [ ] Terms of Service
  - [ ] Privacy Policy
  - [ ] GDPR compliance (if applicable)
  - [ ] FDA guidance review
  - [ ] Medical device classification

---

## 🐛 Reporting Security Vulnerabilities

### Responsible Disclosure

**Please DO NOT:**
- Open a public GitHub issue for security vulnerabilities
- Disclose vulnerabilities publicly before patch is available

**Please DO:**
1. Email security report to: **security@realdiag.com** (if available)
2. Or create a private security advisory: GitHub → Security → Advisories
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

**Response Timeline:**
- Acknowledgment: Within 48 hours
- Initial assessment: Within 1 week
- Fix timeline: Depends on severity (Critical: 24-48h, High: 1 week, Medium: 2 weeks)

### Bug Bounty
**Status: No formal program currently**

We appreciate security researchers who help improve RealDiag security. While we don't have a formal bug bounty program, we will:
- Acknowledge your contribution
- Credit you in SECURITY.md (with permission)
- Fast-track fixes for reported issues

---

## 🔄 Security Update Policy

### Version Support

| Version | Supported          |
|---------|--------------------|
| main    | ✅ Active development |
| 1.x     | ✅ Security patches   |
| < 1.0   | ❌ Not supported      |

### Security Patches
- Critical vulnerabilities: Emergency patch within 24-48 hours
- High severity: Patch within 1 week
- Medium/Low: Included in next scheduled release

---

## 📚 Additional Resources

### Standards & Frameworks
- **HIPAA**: https://www.hhs.gov/hipaa/
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **NIST Cybersecurity Framework**: https://www.nist.gov/cyberframework
- **FDA Software Guidance**: https://www.fda.gov/medical-devices/software-medical-device-samd

### Tools
- **Security Scanning**: OWASP ZAP, Burp Suite
- **Dependency Scanning**: Snyk, npm audit, safety (Python)
- **SAST**: SonarQube, Semgrep
- **Secret Scanning**: GitGuardian, TruffleHog

---

## 🆘 Emergency Contact

**For security emergencies:**
- Email: security@realdiag.com
- GitHub Security Advisory: https://github.com/bevroy/RealDiag-Software/security/advisories

**Last Updated:** 2025-01-19  
**Next Review:** Quarterly or upon major release
