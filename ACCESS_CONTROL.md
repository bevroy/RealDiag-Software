# RealDiag Access Control Documentation

**Version:** 1.0  
**Last Updated:** November 21, 2025  
**Author:** RealDiag Development Team

---

## 📋 Overview

RealDiag implements a comprehensive access control system that balances **open access for clinical learning** with **authentication requirements for personalized features and data export**.

### Access Levels

1. **🌐 Public (View-Only)** - No authentication required
2. **🔐 Authenticated User** - Requires user login (JWT token)
3. **🔑 API Key** - For system-to-system integration
4. **👑 Admin** - Future: Administrative privileges

---

## 🔓 Public Endpoints (No Authentication Required)

These endpoints are **freely accessible** for educational and reference purposes. Users can browse diagnostic trees, search rules, view clinical cases, and access educational content without creating an account.

### Diagnostic Endpoints (`/diagnostic`)

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/diagnostic/search-limit` | GET | Check search limit status | Optional |
| `/diagnostic/trees` | GET | List all diagnostic trees | Optional* |
| `/diagnostic/evaluate/{tree_id}` | POST | Evaluate patient against tree | Optional* (⚠️ Limited) |

**🆓 FREE TRIAL for Anonymous Users:**
- **10 diagnostic searches per week** without login
- Search count tracked by IP address
- Limit resets 7 days after first search
- HTTP 429 returned when limit exceeded

**\*Optional Authentication Benefits:**
- **Unlimited searches** (no restrictions)
- Search history automatically saved
- Personalized recommendations
- Usage analytics

### Clinical Rules Endpoints (`/rules`)

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/rules/families` | GET | List all rule families | Optional* |
| `/rules/family/{family}` | GET | Get rules for specific family | Optional* |
| `/rules/rule/{rule_id}` | GET | Get specific rule by ID | Optional* |
| `/rules/search` | GET | Search rules by keyword | Optional* |

**\*Optional Authentication Benefits:**
- Favorite status shown on rules
- Personalized search ranking
- Search history tracking

### Educational Content (`/education`)

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/education/cases` | GET | List clinical cases | Optional* |
| `/education/cases/{case_id}` | GET | Get specific case | Optional* |
| `/education/cases/search/{query}` | GET | Search cases | Optional* |
| `/education/quiz/questions` | GET | Get quiz questions | Optional* |
| `/education/learning-objectives` | GET | Get learning objectives | Optional |

**\*Optional Authentication Benefits:**
- Case completion tracking
- Progress indicators
- Personalized difficulty recommendations

### Reference Endpoints (`/reference`)

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/reference/{family}` | GET | Get reference materials | Optional |

### Health & Metadata

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/` | GET | API root | None |
| `/health` | GET | Health check | None |
| `/version` | GET | API version | None |
| `/integration/health` | GET | Integration services health | None |

---

## 🔐 Authenticated Endpoints (User Login Required)

These endpoints require a **logged-in user** with a valid JWT token. Authentication can be provided via:
- **HttpOnly Cookie** (set during login, preferred for web apps)
- **Authorization Header** (`Bearer <token>`)

### User Account Management (`/users`)

| Endpoint | Method | Description | HTTP 401 if Not Authenticated |
|----------|--------|-------------|-------------------------------|
| `/users/me` | GET | Get user profile | ✅ |
| `/users/me` | PUT | Update profile | ✅ |
| `/users/me/settings` | GET | Get user settings | ✅ |
| `/users/me/settings` | PUT | Update settings | ✅ |
| `/users/me/history` | GET | Get search history | ✅ |
| `/users/me/history` | POST | Add to search history | ✅ |
| `/users/me/favorites` | GET | Get favorites | ✅ |
| `/users/me/favorites` | POST | Add favorite | ✅ |
| `/users/me/favorites/{id}` | DELETE | Remove favorite | ✅ |
| `/users/me/lists` | GET | Get custom lists | ✅ |
| `/users/me/lists` | POST | Create custom list | ✅ |
| `/users/me/lists/{id}/diagnoses` | POST | Add to list | ✅ |
| `/users/me/lists/{id}/diagnoses/{rule_id}` | DELETE | Remove from list | ✅ |
| `/users/me/analytics` | GET | Get usage analytics | ✅ |

### Educational Progress Tracking (`/education`)

| Endpoint | Method | Description | HTTP 401 if Not Authenticated |
|----------|--------|-------------|-------------------------------|
| `/education/quiz/submit` | POST | Submit quiz answer | ✅ |
| `/education/progress/{user_id}` | GET | Get progress stats | ✅ (own ID only) |
| `/education/flashcards/due` | GET | Get due flashcards | ✅ |
| `/education/flashcards/review` | POST | Review flashcard | ✅ |

**Security Note:** Users can only access their own progress data. Attempting to access another user's progress returns HTTP 403 Forbidden.

### API Key Management (`/integration`)

| Endpoint | Method | Description | HTTP 401 if Not Authenticated |
|----------|--------|-------------|-------------------------------|
| `/integration/api-keys` | POST | Create API key | ✅ |
| `/integration/api-keys` | GET | List own API keys | ✅ |

**Note:** API keys are tied to the user who created them.

---

## 🔑 Integration Endpoints (User OR API Key Required)

These endpoints support **dual authentication**: either a logged-in user OR a valid API key. This allows both:
- **Human users** to export data via the web interface
- **Systems** to integrate via API keys

### FHIR Export (`/integration`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/integration/fhir/condition` | POST | Export to FHIR Condition | User OR API Key ⚠️ |

### HL7 Export (`/integration`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/integration/hl7/message` | POST | Generate HL7 v2 message | User OR API Key ⚠️ |

### Multi-Format Export (`/integration`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/integration/export` | POST | Export (FHIR/HL7/JSON/XML/CSV) | User OR API Key ⚠️ |

### PDF Export (`/integration`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/integration/export/pdf/diagnosis` | POST | Generate diagnosis PDF | User OR API Key ⚠️ |
| `/integration/export/pdf/differential` | POST | Generate differential PDF | User OR API Key ⚠️ |

### Webhook Management (`/integration`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/integration/webhooks/register` | POST | Register webhook | User OR API Key ⚠️ |
| `/integration/webhooks` | GET | List webhooks | User OR API Key ⚠️ |
| `/integration/webhooks/{id}` | DELETE | Delete webhook | User OR API Key ⚠️ |

### EHR Integration (`/integration`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/integration/ehr/fhir/configure` | POST | Configure FHIR server | User OR API Key ⚠️ |
| `/integration/ehr/fhir/pull/patient/{id}` | GET | Pull patient data | User OR API Key ⚠️ |
| `/integration/ehr/fhir/search/patients` | GET | Search patients | User OR API Key ⚠️ |

### CPOE Integration (`/integration`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/integration/cpoe/order` | POST | Create CPOE order | User OR API Key ⚠️ |

---

## 🔒 Authentication Methods

### Method 1: User Authentication (JWT Tokens)

**For web applications and mobile apps**

1. **Register:** `POST /users/register`
   ```json
   {
     "email": "doctor@hospital.com",
     "password": "SecurePass123!",
     "full_name": "Dr. Jane Smith",
     "specialty": "cardiology",
     "institution": "Memorial Hospital"
   }
   ```

2. **Login:** `POST /users/login`
   ```json
   {
     "email": "doctor@hospital.com",
     "password": "SecurePass123!"
   }
   ```

3. **Authentication:**
   - **Web apps:** JWT token automatically stored in secure HttpOnly cookie
   - **Mobile apps:** Include token in Authorization header:
     ```
     Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
     ```

4. **Logout:** `POST /users/logout` (clears cookies)

### Method 2: API Key Authentication

**For system-to-system integration**

1. **Create API Key:** `POST /integration/api-keys` (requires user login)
   ```json
   {
     "name": "EMR Integration",
     "scopes": ["read", "write"],
     "expires_days": 365
   }
   ```

2. **Use API Key:** Include in `X-API-Key` header:
   ```bash
   curl -H "X-API-Key: rdiag_abc123..." \
        https://api.realdiag.com/integration/export
   ```

3. **Security:**
   - API keys are prefixed with `rdiag_`
   - Keys are tied to the creating user
   - Keys can expire (configurable)
   - Keys can be revoked

---

## 🛡️ Security Features

### Rate Limiting

All authenticated endpoints have rate limits to prevent abuse:

| Endpoint Type | Rate Limit |
|---------------|------------|
| User registration | 5 attempts / 15 minutes |
| User login | 5 attempts / 15 minutes |
| Quiz submissions | 30 / minute |
| Flashcard reviews | 100 / minute |
| Case browsing | 20 / minute |
| API queries | 30 / minute |

### Password Security

- Passwords hashed using SHA-256
- Minimum complexity requirements enforced
- Rate-limited login attempts

### Token Security

- JWT tokens expire after 60 minutes (configurable)
- Tokens stored in HttpOnly cookies (cannot be accessed by JavaScript)
- CSRF protection for cookie-based authentication
- Secure flag enabled in production (HTTPS only)

### Data Privacy

- Users can only access their own:
  - Search history
  - Favorites
  - Custom lists
  - Progress stats
  - API keys
- Admin role (future) for managing all data

---

## 📊 Usage Examples

### Example 1: Browse Diagnostic Trees (No Auth)

```bash
# Anyone can view diagnostic trees
curl https://api.realdiag.com/diagnostic/trees

# Response:
{
  "trees": [
    {"id": "NEU-HEADACHE", "name": "Headache Evaluation", ...},
    {"id": "CARD-CHEST-PAIN", "name": "Chest Pain", ...}
  ]
}
```

### Example 2: Save Favorite (Requires Auth)

```bash
# Must be logged in
curl -X POST https://api.realdiag.com/users/me/favorites \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "rule_id": "CARD-STEMI",
    "diagnosis_label": "STEMI",
    "family": "cardiology",
    "notes": "Review for board exam"
  }'

# Without auth: HTTP 401 Unauthorized
```

### Example 3: Export to FHIR (User OR API Key)

```bash
# Option A: With user token
curl -X POST https://api.realdiag.com/integration/fhir/condition \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"rule_id": "CARD-STEMI", "patient_id": "12345"}'

# Option B: With API key
curl -X POST https://api.realdiag.com/integration/fhir/condition \
  -H "X-API-Key: rdiag_abc123..." \
  -H "Content-Type: application/json" \
  -d '{"rule_id": "CARD-STEMI", "patient_id": "12345"}'

# Without either: HTTP 401 Unauthorized
```

### Example 4: View-Only vs Authenticated Behavior

```bash
# Unauthenticated: Basic evaluation
curl -X POST https://api.realdiag.com/diagnostic/evaluate/NEU-HEADACHE \
  -H "Content-Type: application/json" \
  -d '{"symptoms": ["headache", "photophobia"]}'

# Response: diagnosis results only
{
  "tree_result": {
    "diagnoses": [...]
  }
}

# Authenticated: Evaluation + auto-saved to history
curl -X POST https://api.realdiag.com/diagnostic/evaluate/NEU-HEADACHE \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"symptoms": ["headache", "photophobia"]}'

# Response: diagnosis results + saved to user history
{
  "tree_result": {
    "diagnoses": [...]
  }
}

# Later: View saved history
curl https://api.realdiag.com/users/me/history \
  -H "Authorization: Bearer eyJ..."

# Response:
{
  "history": [
    {
      "timestamp": "2025-11-21T10:30:00Z",
      "symptoms": ["headache", "photophobia"],
      "top_diagnosis": "NEU-MIGRAINE",
      ...
    }
  ]
}
```

---

## 🚀 Frontend Implementation Guide

### React/Next.js Example

```typescript
// lib/auth.ts
export const api = {
  // Public endpoint - no auth needed
  async getTreesList() {
    const res = await fetch('/api/diagnostic/trees');
    return res.json();
  },

  // Authenticated endpoint - requires login
  async getFavorites() {
    const res = await fetch('/api/users/me/favorites', {
      credentials: 'include' // Send HttpOnly cookies
    });
    
    if (res.status === 401) {
      // Redirect to login
      window.location.href = '/login';
      return;
    }
    
    return res.json();
  },

  // Optional auth - enhanced if logged in
  async evaluateTree(treeId: string, patient: any) {
    const res = await fetch(`/api/diagnostic/evaluate/${treeId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include', // Send auth if available
      body: JSON.stringify(patient)
    });
    
    return res.json();
  }
};
```

### Mobile App Example (React Native)

```typescript
// lib/api.ts
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE = 'https://api.realdiag.com';

export const api = {
  async login(email: string, password: string) {
    const res = await fetch(`${API_BASE}/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    const data = await res.json();
    
    if (data.access_token) {
      // Store token securely
      await AsyncStorage.setItem('jwt_token', data.access_token);
    }
    
    return data;
  },

  async getFavorites() {
    const token = await AsyncStorage.getItem('jwt_token');
    
    if (!token) {
      throw new Error('Not authenticated');
    }
    
    const res = await fetch(`${API_BASE}/users/me/favorites`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (res.status === 401) {
      // Token expired, re-login required
      await AsyncStorage.removeItem('jwt_token');
      throw new Error('Session expired');
    }
    
    return res.json();
  }
};
```

---

## 📝 Error Responses

### HTTP 401 Unauthorized

Returned when authentication is required but not provided or invalid.

```json
{
  "detail": "Authentication required: Provide either user login (JWT token) or API key (X-API-Key header)"
}
```

**Resolution:**
- Web apps: Redirect to `/login`
- Mobile apps: Show login screen
- API integrations: Check API key validity

### HTTP 403 Forbidden

Returned when authenticated but not authorized for the specific resource.

```json
{
  "detail": "Access denied: You can only view your own progress"
}
```

**Resolution:**
- Ensure user is accessing their own resources
- Check role/permissions

### HTTP 429 Too Many Requests

Returned when rate limit exceeded.

```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

**Resolution:**
- Implement exponential backoff
- Cache responses when possible
- Reduce request frequency

---

## 🔄 Migration Guide

### For Existing Integrations

If you're currently using RealDiag without authentication:

1. **No immediate action required** for read-only operations
   - Browsing trees, viewing rules, searching - still work without auth
   
2. **Create API key** for export/integration features:
   ```bash
   # Step 1: Create user account if you don't have one
   curl -X POST https://api.realdiag.com/users/register \
     -H "Content-Type: application/json" \
     -d '{...}'
   
   # Step 2: Login
   curl -X POST https://api.realdiag.com/users/login \
     -H "Content-Type: application/json" \
     -d '{"email": "...", "password": "..."}'
   
   # Step 3: Create API key (using token from login)
   curl -X POST https://api.realdiag.com/integration/api-keys \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"name": "Legacy Integration", "scopes": ["read", "write"]}'
   
   # Step 4: Update your integration to use API key
   # Add header: X-API-Key: rdiag_abc123...
   ```

3. **Update endpoints** that now require auth:
   - All `/integration/*` export endpoints
   - User-specific endpoints (`/users/me/*`)
   - Educational progress tracking

---

## 🎯 Best Practices

### For Web Applications

1. **Use HttpOnly cookies** (automatic with login)
2. **Check authentication status** on app load
3. **Handle 401 errors** with graceful login prompts
4. **Show auth-only features conditionally**:
   ```tsx
   {isAuthenticated ? (
     <Button onClick={saveFavorite}>Save to Favorites</Button>
   ) : (
     <Button onClick={showLogin}>Login to Save</Button>
   )}
   ```

### For Mobile Applications

1. **Store tokens securely** (AsyncStorage, Keychain)
2. **Implement token refresh** before expiration
3. **Cache public data** to reduce API calls
4. **Handle offline mode** for view-only features

### For System Integrations

1. **Use API keys** for automated systems
2. **Rotate keys regularly** (e.g., every 90 days)
3. **Use separate keys** for dev/staging/production
4. **Implement retry logic** with exponential backoff
5. **Monitor rate limits** and implement queuing

---

## 📞 Support

### Questions?

- **Email:** support@realdiag.com
- **Documentation:** https://docs.realdiag.com
- **GitHub Issues:** https://github.com/bevroy/RealDiag-Software/issues

### Reporting Security Issues

Please report security vulnerabilities to **security@realdiag.com** (not via GitHub issues).

---

## 📅 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-21 | Initial access control implementation |
|     |            | - Public view-only access for educational content |
|     |            | - User authentication for personalization |
|     |            | - API key support for integrations |
|     |            | - Dual auth for export endpoints |

---

**Document maintained by:** RealDiag Development Team  
**Next review:** 2026-02-21
