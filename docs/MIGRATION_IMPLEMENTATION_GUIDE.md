# Database Migration & HttpOnly Cookie Implementation Guide

## Overview

This guide covers the implementation of two critical production security improvements:

1. **Database Migration**: Migrate from JSON file storage to PostgreSQL/MongoDB
2. **HttpOnly Cookies**: Secure JWT authentication using HttpOnly cookies instead of localStorage

---

## Part 1: Database Migration

### Why Migrate?

Current file-based JSON storage is not suitable for production:
- ❌ No concurrent access support
- ❌ No ACID transactions
- ❌ Limited scalability
- ❌ No built-in backup/replication
- ❌ Security concerns with file permissions

Production database provides:
- ✅ ACID compliance
- ✅ Concurrent access with row-level locking
- ✅ Built-in backup and replication
- ✅ Encryption at rest
- ✅ Query optimization and indexing

### Prerequisites

Install database drivers:

```bash
# For PostgreSQL
pip install psycopg2-binary

# For MongoDB
pip install pymongo

# Add to requirements.txt
echo "psycopg2-binary>=2.9.0" >> requirements.txt
echo "pymongo>=4.0.0" >> requirements.txt
```

### Step 1: Configure Environment Variables

Copy `.env.example` to `.env` and configure database credentials:

```bash
cp .env.example .env
```

For PostgreSQL, configure:
```env
# PostgreSQL Configuration
DATABASE_HOST=your-db-host.rds.amazonaws.com
DATABASE_PORT=5432
DATABASE_NAME=realdiag_prod
DATABASE_USER=realdiag_user
DATABASE_PASSWORD=CHANGE_ME_TO_STRONG_PASSWORD
DATABASE_SSL_MODE=require
DATABASE_MAX_CONNECTIONS=20
DATABASE_MIN_CONNECTIONS=5

# Database encryption
DATABASE_ENCRYPTION_ENABLED=true
DATABASE_ENCRYPTION_KEY=CHANGE_ME_TO_32_BYTE_KEY
```

For MongoDB, configure:
```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=realdiag_prod
MONGODB_MAX_POOL_SIZE=50
```

### Step 2: Backup Existing Data

**CRITICAL**: Always backup before migration!

```bash
# Backup JSON files
python -m backend.migrations.migrate_to_db --backup-only

# Verify backups created
ls -la backend/migrations/backups/
```

Expected output:
```
clinical_cases.json.20240115_143022.backup
user_progress.json.20240115_143022.backup
users.json.20240115_143022.backup
```

### Step 3: Run Database Migration

#### Option A: PostgreSQL

```bash
# Migrate to PostgreSQL
python -m backend.migrations.migrate_to_db --db-type postgresql

# Verify migration
python -m backend.migrations.migrate_to_db --verify-only
```

Expected output:
```
🐘 Starting PostgreSQL migration...
Creating PostgreSQL tables...
✅ Tables created successfully
Migrating clinical cases...
✅ Migrated 50 clinical cases
Migrating users...
✅ Migrated 10 users
Migrating user progress...
✅ Migrated progress for 10 users

🔍 Verifying migration...
✅ Verification complete:
   - Users: 10
   - Clinical cases: 50
   - User progress records: 10

✅ Migration completed successfully!
```

#### Option B: MongoDB

```bash
# Migrate to MongoDB
python -m backend.migrations.migrate_to_db --db-type mongodb

# Verify migration
python -m backend.migrations.migrate_to_db --db-type mongodb --verify-only
```

### Step 4: Update Application Code

Update database connections in your application:

**backend/database.py** (create new file):

```python
import os
from typing import Optional
import psycopg2
from psycopg2.pool import ThreadedConnectionPool

# PostgreSQL connection pool
db_pool: Optional[ThreadedConnectionPool] = None

def init_database():
    """Initialize database connection pool"""
    global db_pool
    
    db_pool = ThreadedConnectionPool(
        minconn=int(os.getenv('DATABASE_MIN_CONNECTIONS', 5)),
        maxconn=int(os.getenv('DATABASE_MAX_CONNECTIONS', 20)),
        host=os.getenv('DATABASE_HOST'),
        port=int(os.getenv('DATABASE_PORT', 5432)),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD'),
        sslmode=os.getenv('DATABASE_SSL_MODE', 'require')
    )

def get_db_connection():
    """Get connection from pool"""
    return db_pool.getconn()

def release_db_connection(conn):
    """Return connection to pool"""
    db_pool.putconn(conn)
```

**Update main.py to initialize database**:

```python
from backend.database import init_database

@app.on_event("startup")
async def startup_event():
    init_database()
    print("✅ Database connection pool initialized")
```

### Step 5: Test Migration

Run comprehensive tests:

```bash
# Test database connectivity
python -c "from backend.database import init_database, get_db_connection; init_database(); conn = get_db_connection(); print('✅ Database connected')"

# Run application tests
pytest tests/ -v

# Test API endpoints
curl http://localhost:8000/health/detailed
```

### Step 6: Rollback (if needed)

If migration fails or issues are found:

```bash
# List available backups
python -m backend.migrations.rollback_migration --list

# Rollback to latest backup
python -m backend.migrations.rollback_migration

# Rollback specific file
python -m backend.migrations.rollback_migration \
  --file clinical_cases.json \
  --timestamp 20240115_143022
```

---

## Part 2: HttpOnly Cookie Authentication

### Why HttpOnly Cookies?

Current localStorage storage is vulnerable:
- ❌ Accessible via JavaScript (XSS vulnerability)
- ❌ No built-in CSRF protection
- ❌ Exposed in browser DevTools
- ❌ Can be stolen by malicious scripts

HttpOnly cookies provide:
- ✅ Not accessible via JavaScript (XSS protection)
- ✅ Automatic CSRF protection with SameSite
- ✅ Secure transmission over HTTPS
- ✅ Browser-managed security

### Step 1: Update Backend Authentication

**Update existing user_router.py or auth endpoints**:

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from backend.services.auth_cookies import (
    create_cookie_response,
    cookie_auth,
    get_token_from_cookie,
    verify_csrf_protection
)

router = APIRouter()

# OLD LOGIN (returns token in body - INSECURE)
# @router.post("/login")
# async def login(credentials: LoginCredentials):
#     user = authenticate_user(credentials)
#     access_token = create_access_token(user.id)
#     return {"access_token": access_token}  # ❌ XSS vulnerable

# NEW LOGIN (returns token in cookie - SECURE)
@router.post("/login")
async def login(credentials: LoginCredentials):
    user = authenticate_user(credentials)
    
    # Create tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    # ✅ Tokens stored in HttpOnly cookies
    return create_cookie_response(
        data={
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        },
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/logout")
async def logout():
    response = JSONResponse({"message": "Logged out successfully"})
    cookie_auth.clear_auth_cookies(response)
    return response

@router.post("/auth/refresh")
async def refresh_token(request: Request):
    refresh_token = cookie_auth.get_refresh_token(request)
    
    if not refresh_token:
        raise HTTPException(401, "No refresh token")
    
    # Verify refresh token
    user_id = verify_refresh_token(refresh_token)
    
    # Create new tokens (token rotation)
    new_access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id)
    
    return create_cookie_response(
        data={"message": "Token refreshed"},
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )

# PROTECTED ENDPOINT
@router.get("/profile")
async def get_profile(
    token: str = Depends(get_token_from_cookie),
    csrf_verified: bool = Depends(verify_csrf_protection)
):
    # Token automatically extracted from cookie
    # CSRF automatically verified
    user = get_current_user(token)
    return {"user": user.dict()}
```

### Step 2: Update Frontend Authentication

Replace all localStorage usage with cookie-based auth:

**For React/Next.js applications**:

```jsx
// Import secure API client
import apiClient, { useAuth } from '@/lib/auth-cookies';

// In your login component
function LoginPage() {
  const { login } = useAuth();
  
  const handleLogin = async (e) => {
    e.preventDefault();
    const { success, user } = await login(username, password);
    
    if (success) {
      router.push('/dashboard');
    }
  };
  
  return <form onSubmit={handleLogin}>...</form>;
}

// Protected routes
function Dashboard() {
  const { user, logout, isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Redirect to="/login" />;
  }
  
  return (
    <div>
      <h1>Welcome {user.name}</h1>
      <button onClick={logout}>Logout</button>
    </div>
  );
}

// API calls - cookies automatically included
async function loadData() {
  const data = await apiClient.request('/api/data');
  return data;
}
```

**For vanilla JavaScript**:

```javascript
// Login
async function login(username, password) {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    credentials: 'include', // ✅ Include cookies
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  
  const data = await response.json();
  // Store CSRF token for future requests
  sessionStorage.setItem('csrf_token', data.csrf_token);
  return data;
}

// API request
async function apiRequest(endpoint, options = {}) {
  const csrfToken = sessionStorage.getItem('csrf_token');
  
  const response = await fetch(endpoint, {
    ...options,
    credentials: 'include', // ✅ Include cookies
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrfToken, // ✅ CSRF protection
      ...options.headers
    }
  });
  
  return response.json();
}
```

### Step 3: Update Environment Configuration

Add cookie settings to `.env`:

```env
# Cookie Authentication Settings
COOKIE_SECURE=true  # HTTPS only (must be true in production)
COOKIE_SAMESITE=strict  # CSRF protection
COOKIE_DOMAIN=.yourdomain.com  # Your domain
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Session Management
SESSION_MAX_AGE_SECONDS=86400
SESSION_SAME_ORIGIN_ONLY=true
```

### Step 4: Configure CORS for Cookies

Update CORS settings to allow credentials:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],
    allow_credentials=True,  # ✅ Required for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 5: Clean Up Old Authentication

Remove localStorage tokens from existing user sessions:

```javascript
// Add to application startup
function cleanupOldAuth() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  console.log('✅ Old authentication cleaned up');
}

cleanupOldAuth();
```

### Step 6: Test Cookie Authentication

```bash
# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "password"}' \
  -c cookies.txt \
  -v

# Check cookies were set
cat cookies.txt

# Test protected endpoint with cookies
curl http://localhost:8000/api/profile \
  -b cookies.txt \
  -H "X-CSRF-Token: YOUR_CSRF_TOKEN" \
  -v

# Test logout
curl -X POST http://localhost:8000/api/auth/logout \
  -b cookies.txt \
  -c cookies.txt \
  -v
```

---

## Deployment Checklist

### Database Migration Checklist

- [ ] Database credentials configured in `.env`
- [ ] Database server accessible from application
- [ ] JSON files backed up
- [ ] Migration script executed successfully
- [ ] Data verified in production database
- [ ] Application code updated to use database
- [ ] Connection pooling configured
- [ ] Database indexes created
- [ ] Backup and monitoring configured
- [ ] Old JSON files archived (not deleted yet)

### HttpOnly Cookie Checklist

- [ ] Backend updated with `auth_cookies.py`
- [ ] All login endpoints return cookies
- [ ] CSRF protection implemented
- [ ] Frontend updated to use `credentials: 'include'`
- [ ] CORS configured with `allow_credentials=True`
- [ ] Cookie settings configured (Secure, HttpOnly, SameSite)
- [ ] Token refresh endpoint working
- [ ] Logout clears cookies properly
- [ ] Old localStorage tokens cleaned up
- [ ] HTTPS enforced in production

---

## Monitoring & Validation

### Database Health Checks

```python
# Add to monitoring.py
from backend.database import get_db_connection, release_db_connection

@router.get("/health/database")
async def check_database():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        release_db_connection(conn)
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### Authentication Security Checks

```python
# Add to security tests
def test_cookies_are_httponly():
    response = client.post("/api/auth/login", json={"username": "test", "password": "test"})
    cookies = response.cookies
    
    assert "access_token" in cookies
    assert cookies["access_token"]["httponly"] == True
    assert cookies["access_token"]["secure"] == True
    assert cookies["access_token"]["samesite"] == "strict"

def test_csrf_protection():
    # Login to get cookies
    client.post("/api/auth/login", json={"username": "test", "password": "test"})
    
    # Try POST without CSRF token
    response = client.post("/api/protected", json={})
    assert response.status_code == 403
```

---

## Rollback Procedures

### Database Rollback

```bash
# Restore from backup
python -m backend.migrations.rollback_migration

# Update application to use JSON files
# Restart application
systemctl restart realdiag
```

### Authentication Rollback

```python
# Revert to localStorage (temporary, not recommended)
# 1. Comment out cookie authentication
# 2. Restore old token-in-body responses
# 3. Update frontend to use localStorage
# 4. Deploy changes
# 5. Clear user cookies
```

---

## Common Issues & Solutions

### Database Migration Issues

**Issue**: Connection refused
```
Solution: Check database host, port, and firewall rules
```

**Issue**: Authentication failed
```
Solution: Verify DATABASE_USER and DATABASE_PASSWORD in .env
```

**Issue**: SSL required
```
Solution: Set DATABASE_SSL_MODE=require and ensure SSL certificates
```

### Cookie Authentication Issues

**Issue**: Cookies not being set
```
Solution: Ensure HTTPS in production, check COOKIE_SECURE setting
```

**Issue**: Cookies not sent with requests
```
Solution: Add credentials: 'include' to fetch requests
```

**Issue**: CORS errors
```
Solution: Set allow_credentials=True in CORS config
```

**Issue**: CSRF token validation failing
```
Solution: Ensure X-CSRF-Token header matches cookie value
```

---

## Security Best Practices

### Database Security

1. ✅ Use parameterized queries (prevent SQL injection)
2. ✅ Enable encryption at rest
3. ✅ Use SSL/TLS for connections
4. ✅ Implement connection pooling with limits
5. ✅ Regular backups with encryption
6. ✅ Monitor for suspicious queries
7. ✅ Use read replicas for scaling

### Cookie Authentication Security

1. ✅ Always use HttpOnly cookies
2. ✅ Enable Secure flag (HTTPS only)
3. ✅ Set SameSite=Strict
4. ✅ Implement CSRF protection
5. ✅ Use short-lived access tokens (60 min)
6. ✅ Rotate refresh tokens on use
7. ✅ Log all authentication events
8. ✅ Implement rate limiting on auth endpoints

---

## Support & Documentation

- Database Migration Script: `backend/migrations/migrate_to_db.py`
- Rollback Script: `backend/migrations/rollback_migration.py`
- Cookie Auth Implementation: `backend/services/auth_cookies.py`
- Frontend Auth Library: `frontend/lib/auth-cookies.js`
- Production Checklist: `PRODUCTION_CHECKLIST.md`
- Environment Template: `.env.example`

For issues or questions, refer to the implementation files or create a support ticket.
