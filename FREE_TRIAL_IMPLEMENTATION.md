# Free Trial Search Limiting - Implementation

## 🎯 Feature: Limited Diagnostic Searches for Anonymous Users

**Implemented:** November 21, 2025

### Summary

Anonymous users now have a **free trial with 10 diagnostic searches per week**. After exhausting their free searches, users must create a free account to continue with unlimited searches.

---

## 📊 Configuration

### Default Settings
- **Free Search Limit:** 10 searches
- **Time Window:** 7 days (rolling window)
- **Tracking Method:** IP address
- **Authenticated Users:** Unlimited searches

### Adjustable Parameters
Located in `/backend/services/search_limiter.py`:

```python
FREE_SEARCH_LIMIT = 10  # Number of free searches
FREE_SEARCH_WINDOW_DAYS = 7  # Time window in days
STORAGE_CLEANUP_HOURS = 24  # Clean old entries every 24 hours
```

---

## 🔧 Implementation Details

### New File Created

**`backend/services/search_limiter.py`**
- Tracks anonymous searches by IP address
- Implements rolling 7-day window
- Periodic cleanup of old entries
- Handles proxies and load balancers correctly
- In-memory storage (can be upgraded to Redis/database)

### Key Functions

1. **`check_search_limit(request, tree_id, user_authenticated)`**
   - Enforces search limits
   - Raises HTTP 429 when limit exceeded
   - Returns limit status information

2. **`get_search_limit_info(request, user_authenticated)`**
   - Query limit status without recording search
   - Useful for displaying status to users

3. **`get_client_ip(request)`**
   - Extracts real IP from proxies/load balancers
   - Handles X-Forwarded-For and X-Real-IP headers

4. **`cleanup_old_entries()`**
   - Removes expired search records
   - Runs automatically every 24 hours
   - Prevents memory bloat

### Modified Files

**`backend/services/diagnostic_router.py`**
- Added `GET /diagnostic/search-limit` endpoint
- Updated `POST /diagnostic/evaluate/{tree_id}` to check limits
- Updated `GET /diagnostic/trees` to show limit info
- Returns search status in responses

---

## 🌐 API Changes

### New Endpoint

#### `GET /diagnostic/search-limit`

Check search limit status without performing a search.

**Response (Anonymous User):**
```json
{
  "authenticated": false,
  "searches_used": 3,
  "searches_remaining": 7,
  "limit": 10,
  "window_days": 7,
  "reset_date": "2025-11-28T10:30:00Z",
  "message": "Free trial: 7 of 10 searches remaining (resets 2025-11-28)"
}
```

**Response (Authenticated User):**
```json
{
  "authenticated": true,
  "searches_remaining": "unlimited",
  "message": "You have unlimited diagnostic searches"
}
```

### Modified Endpoints

#### `POST /diagnostic/evaluate/{tree_id}`

Now enforces search limits for anonymous users.

**New Behavior:**
- Checks search limit before evaluation
- Returns HTTP 429 if limit exceeded
- Includes limit status in response

**Response (Success with Limit Info):**
```json
{
  "tree_result": {
    "diagnoses": [...]
  },
  "search_limit": {
    "searches_used": 5,
    "searches_remaining": 5,
    "message": ""
  }
}
```

**Response (Limit Exceeded - HTTP 429):**
```json
{
  "detail": {
    "error": "Free search limit exceeded",
    "message": "You've used all 10 free diagnostic searches. Create a free account to continue with unlimited searches.",
    "searches_used": 10,
    "searches_remaining": 0,
    "limit": 10,
    "window_days": 7,
    "reset_date": "2025-11-28T10:30:00Z",
    "action_required": "login",
    "login_url": "/users/login",
    "register_url": "/users/register"
  }
}
```

**Response (Warning - Near Limit):**
```json
{
  "tree_result": {
    "diagnoses": [...]
  },
  "search_limit": {
    "searches_used": 9,
    "searches_remaining": 1,
    "message": "You have 1 free searches remaining. Create an account for unlimited searches.",
    "upgrade_message": "Create a free account for unlimited searches!",
    "register_url": "/users/register"
  }
}
```

#### `GET /diagnostic/trees`

Now includes free trial status for anonymous users.

**Response (Anonymous):**
```json
{
  "trees": [...],
  "free_trial": {
    "authenticated": false,
    "searches_used": 2,
    "searches_remaining": 8,
    "limit": 10,
    "window_days": 7,
    "message": "Free trial: 8 of 10 searches remaining"
  }
}
```

**Response (Authenticated):**
```json
{
  "trees": [...],
  "user_id": "user_123",
  "search_limit": "unlimited"
}
```

---

## 💻 Frontend Integration

### Display Search Limit Banner

```typescript
// Check limit status on page load
async function checkSearchLimit() {
  const response = await fetch('/api/diagnostic/search-limit');
  const data = await response.json();
  
  if (!data.authenticated && data.searches_remaining <= 2) {
    // Show warning banner
    showBanner({
      type: 'warning',
      message: `${data.searches_remaining} free searches remaining. Sign up for unlimited access!`,
      action: {
        text: 'Create Free Account',
        url: '/register'
      }
    });
  }
}
```

### Handle Limit Exceeded Error

```typescript
// Handle 429 response
async function evaluateDiagnosis(treeId: string, patient: any) {
  try {
    const response = await fetch(`/api/diagnostic/evaluate/${treeId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patient)
    });
    
    if (response.status === 429) {
      const error = await response.json();
      
      // Show modal to encourage signup
      showModal({
        title: 'Free Trial Limit Reached',
        message: error.detail.message,
        primaryAction: {
          text: 'Create Free Account',
          url: '/register'
        },
        secondaryAction: {
          text: 'Login',
          url: '/login'
        },
        details: `Limit resets on ${new Date(error.detail.reset_date).toLocaleDateString()}`
      });
      
      return null;
    }
    
    const data = await response.json();
    
    // Show remaining searches if near limit
    if (data.search_limit && data.search_limit.searches_remaining <= 2) {
      showToast({
        type: 'info',
        message: data.search_limit.message
      });
    }
    
    return data.tree_result;
    
  } catch (error) {
    console.error('Evaluation failed:', error);
    throw error;
  }
}
```

### Show Limit in UI

```tsx
// React component example
function SearchLimitIndicator() {
  const { data: limitInfo } = useQuery('/api/diagnostic/search-limit');
  
  if (!limitInfo || limitInfo.authenticated) {
    return null; // No limit for authenticated users
  }
  
  const { searches_used, searches_remaining, limit } = limitInfo;
  const percentage = (searches_used / limit) * 100;
  
  return (
    <div className="search-limit-indicator">
      <div className="progress-bar">
        <div 
          className="progress" 
          style={{ width: `${percentage}%` }}
        />
      </div>
      <p className="limit-text">
        {searches_remaining} of {limit} free searches remaining
      </p>
      {searches_remaining <= 2 && (
        <button onClick={() => navigate('/register')}>
          Sign Up for Unlimited Access
        </button>
      )}
    </div>
  );
}
```

---

## 🧪 Testing

### Test Cases

1. **Anonymous User - Within Limit**
   ```bash
   # Should succeed
   curl -X POST http://localhost:8000/diagnostic/evaluate/test-tree \
     -H "Content-Type: application/json" \
     -d '{"symptoms": ["fever"]}'
   ```

2. **Anonymous User - At Limit**
   ```bash
   # After 10 searches, should return HTTP 429
   for i in {1..11}; do
     curl -X POST http://localhost:8000/diagnostic/evaluate/test-tree \
       -H "Content-Type: application/json" \
       -d '{"symptoms": ["fever"]}'
     echo "Search $i completed"
   done
   ```

3. **Authenticated User - Unlimited**
   ```bash
   # Should always succeed
   curl -X POST http://localhost:8000/diagnostic/evaluate/test-tree \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"symptoms": ["fever"]}'
   ```

4. **Check Limit Status**
   ```bash
   # Check status without using a search
   curl http://localhost:8000/diagnostic/search-limit
   ```

### Manual Testing Steps

1. Start server: `uvicorn backend.main:app --reload`
2. Open browser to `http://localhost:8000/docs`
3. Try `/diagnostic/evaluate/{tree_id}` 10 times
4. Verify 11th attempt returns 429
5. Login via `/users/login`
6. Verify unlimited searches work
7. Check `/diagnostic/search-limit` shows correct status

---

## 📊 Monitoring & Analytics

### Track Anonymous Usage

```python
from backend.services.search_limiter import get_all_stats

# Get overall statistics
stats = get_all_stats()
print(f"Total IPs tracked: {stats['total_tracked_ips']}")
print(f"IPs at limit: {stats['ips_at_limit']}")
print(f"IPs near limit: {stats['ips_near_limit']}")
```

### Example Output:
```json
{
  "total_tracked_ips": 150,
  "total_recent_searches": 487,
  "ips_at_limit": 23,
  "ips_near_limit": 45,
  "free_search_limit": 10,
  "window_days": 7,
  "last_cleanup": "2025-11-21T10:30:00Z"
}
```

### Metrics to Track

1. **Conversion Rate:** % of users who hit limit and create account
2. **Search Distribution:** How many searches before conversion
3. **Peak Usage Times:** When are free searches used most
4. **Abandoned Sessions:** Users who hit limit but don't convert

---

## 🔧 Configuration Options

### Increase Free Limit

```python
# backend/services/search_limiter.py
FREE_SEARCH_LIMIT = 20  # Increase to 20 searches
```

### Change Time Window

```python
# backend/services/search_limiter.py
FREE_SEARCH_WINDOW_DAYS = 14  # 2-week rolling window
```

### Disable Limits (Testing)

```python
# Temporarily bypass limits in development
# backend/services/diagnostic_router.py

# Comment out the check_search_limit call:
# limit_check = check_search_limit(...)
```

### Reset Specific IP

```python
from backend.services.search_limiter import reset_ip_searches

# Reset search count for testing
reset_ip_searches("192.168.1.100")
```

---

## 🚀 Future Enhancements

### Short-term
1. **Persist to database** - Move from in-memory to Redis/PostgreSQL
2. **User fingerprinting** - Track by browser fingerprint + IP
3. **Admin dashboard** - View and manage search limits
4. **A/B testing** - Test different limit thresholds

### Medium-term
1. **Graduated limits** - More searches for registered but unverified users
2. **Referral bonuses** - Extra searches for referrals
3. **Educational exceptions** - Higher limits for .edu domains
4. **Rate limit bypass** - Special codes for demos/conferences

### Long-term
1. **Smart throttling** - ML-based fraud detection
2. **Geo-based limits** - Different limits by region
3. **Usage analytics** - Track conversion funnels
4. **Premium tiers** - Paid plans with higher limits

---

## 🛡️ Security Considerations

### IP Spoofing Protection
- Uses X-Forwarded-For correctly
- Validates proxy headers
- Logs suspicious patterns

### Privacy
- No PII stored with IP addresses
- Automatic cleanup after 7 days
- Search content not stored

### Abuse Prevention
- Rate limiting still applies
- HTTP 429 with retry-after
- Can be upgraded to Redis for distributed systems

### GDPR Compliance
- IP addresses auto-deleted after window
- No tracking cookies used
- Clear opt-out via account creation

---

## 📞 Support

### Common Issues

**Q: Why am I blocked even though I haven't used 10 searches?**
A: Check if you're behind a shared IP (VPN, corporate network). All users on that IP share the limit.

**Q: When does my limit reset?**
A: 7 days after your first search in the window. Check the `reset_date` in the error response.

**Q: Can I get more free searches?**
A: Create a free account for unlimited searches! No payment required.

**Q: I'm a developer testing. How do I bypass limits?**
A: Use `reset_ip_searches("your.ip.address")` or authenticate with a test account.

---

## 📝 Changelog

### Version 1.0 - November 21, 2025
- Initial implementation
- 10 searches per 7 days for anonymous users
- IP-based tracking with rolling window
- HTTP 429 error when limit exceeded
- Integration with authentication system
- Frontend-friendly error responses

---

**Implementation Status:** ✅ Complete  
**Testing Status:** ⏳ Pending  
**Production Ready:** After testing
