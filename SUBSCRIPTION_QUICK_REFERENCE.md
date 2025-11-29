# Subscription System Quick Reference

## 🚀 Quick Start

### Import Required Modules
```python
from backend.services.subscription_gate import SubscriptionGate, require_feature, require_plan
from backend.services.subscription_router import user_subscriptions
from backend.services.subscription_models import PlanType
```

## 🎯 Common Use Cases

### 1. Protect Endpoint with Feature Check
```python
@router.post("/premium-feature")
@require_feature("api_access", user_subscriptions)
async def premium_feature(current_user: dict = Depends(get_current_user)):
    return {"data": "premium content"}
```

### 2. Require Minimum Plan Level
```python
@router.get("/professional-only")
@require_plan(PlanType.INDIVIDUAL_PROFESSIONAL, user_subscriptions)
async def pro_feature(current_user: dict = Depends(get_current_user)):
    return {"feature": "professional"}
```

### 3. Check Multiple Features
```python
@router.post("/export")
async def export_data(current_user: dict = Depends(get_current_user)):
    async with SubscriptionGate(current_user, user_subscriptions) as gate:
        # Check feature access
        gate.require_feature("fhir_export")
        
        # Check usage limits
        gate.require_limit("exports_per_month", current_exports)
        
        # Perform export
        remaining = gate.get_remaining("exports_per_month", current_exports)
        return {"exported": True, "remaining": remaining}
```

### 4. Conditional Feature Access
```python
async with SubscriptionGate(current_user, user_subscriptions) as gate:
    if gate.has_feature("advanced_analytics"):
        # Show advanced analytics
        return generate_advanced_report()
    else:
        # Show basic analytics
        return generate_basic_report()
```

## 📋 Plan Types

```python
PlanType.FREE                           # Free trial (10 searches/week)
PlanType.INDIVIDUAL_STARTER             # $29/mo (1 module)
PlanType.INDIVIDUAL_PROFESSIONAL        # $49/mo (all modules)
PlanType.INDIVIDUAL_PROFESSIONAL_PLUS   # $69/mo (+ API, analytics)
PlanType.ORGANIZATION                   # $24-40/seat/mo (volume-based)
PlanType.ACADEMIC_FACULTY               # $25/mo
PlanType.ACADEMIC_RESIDENT              # $12/mo
PlanType.ACADEMIC_STUDENT               # Free
PlanType.NONPROFIT_STANDARD             # $18/mo
PlanType.NONPROFIT_EXPANDED             # $10/mo
PlanType.ENTERPRISE                     # Custom pricing
```

## 🔑 Feature Keys

### Module Access
- `modules_neurology`, `modules_cardiology`, `modules_pulmonology`, etc.
- `modules_all` (boolean)

### Export & Integration
- `fhir_export` (Professional+)
- `hl7_export` (Organization+)
- `bulk_export` (Enterprise)
- `api_access` (Professional+)
- `webhook_support` (Organization+)
- `ehr_integration` (Organization+)

### Advanced Features
- `admin_dashboard` (Organization+)
- `user_management` (Organization+)
- `advanced_analytics` (Professional+)
- `white_label` (Enterprise)
- `sso` (Organization+)

### Usage Limits
- `searches_per_month` ("Unlimited" or number)
- `exports_per_month` (number)
- `api_calls_per_day` (number)

## 🛠️ API Endpoints

### Public (No Auth)
```bash
GET  /subscriptions/plans                    # List all plans
GET  /subscriptions/plans/{plan_type}        # Plan details
GET  /subscriptions/calculate-price          # Price calculator
GET  /subscriptions/features/{feature_name}  # Feature check
```

### Authenticated (Requires Login)
```bash
GET    /subscriptions/me              # Current subscription
POST   /subscriptions/me              # Create subscription
PUT    /subscriptions/me              # Update/upgrade
DELETE /subscriptions/me              # Cancel subscription
POST   /subscriptions/me/reactivate   # Reactivate
```

## 💡 Examples

### Example 1: Check if User Can Export
```python
from backend.services.subscription_gate import SubscriptionGate

async def can_export(user: dict) -> bool:
    async with SubscriptionGate(user, user_subscriptions) as gate:
        return gate.has_feature("fhir_export")
```

### Example 2: Get User's Plan Info
```python
from backend.services.subscription_models import get_plan_features, PlanType

def get_user_plan_info(user_id: str) -> dict:
    subscription = user_subscriptions.get(user_id)
    if not subscription:
        return get_plan_features(PlanType.FREE)
    
    plan_type = PlanType(subscription["plan_type"])
    return get_plan_features(plan_type)
```

### Example 3: Calculate Price with Volume Discount
```python
from backend.services.subscription_models import calculate_organization_price, BillingInterval

# 25 seats, yearly billing
price = calculate_organization_price(25, BillingInterval.YEARLY)
# Returns: $9,600 ($32/seat/mo * 25 seats * 10 months + 2 free months)
```

### Example 4: Recommend Plan
```python
from backend.services.subscription_models import get_recommended_plan

recommended = get_recommended_plan("individual")  # Returns: INDIVIDUAL_PROFESSIONAL
```

## ⚠️ Error Handling

### Feature Access Denied (403)
```json
{
  "error": "Feature not available in your plan",
  "feature": "api_access",
  "current_plan": "individual_starter",
  "upgrade_required": true,
  "message": "Upgrade your subscription to access api_access"
}
```

### Usage Limit Exceeded (429)
```json
{
  "error": "Usage limit exceeded",
  "feature": "exports_per_month",
  "limit": "50",
  "current_usage": 51,
  "upgrade_required": true,
  "message": "You've reached your plan's limit for exports_per_month"
}
```

## 🧪 Testing

### Run Test Suite
```bash
# Start backend
cd /workspaces/RealDiag-Software
python backend/main.py &

# Run tests
python test_subscriptions.py
```

### Manual Testing
```bash
# List plans
curl http://localhost:8000/subscriptions/plans

# Register user
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User"}'

# Create subscription
curl -X POST http://localhost:8000/subscriptions/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan_type":"individual_professional","billing_interval":"monthly"}'

# Check subscription
curl http://localhost:8000/subscriptions/me \
  -H "Authorization: Bearer $TOKEN"
```

## 📊 Pricing Quick Reference

| Plan | Price/Month | Searches | Modules | FHIR | API | Support |
|------|-------------|----------|---------|------|-----|---------|
| Free | $0 | 10/week | 1 | ❌ | ❌ | Community |
| Starter | $29 | Unlimited | 1 | ❌ | ❌ | Email |
| Professional | $49 | Unlimited | All | ✅ | ❌ | Priority |
| Professional+ | $69 | Unlimited | All | ✅ | ✅ | Phone |
| Organization | $24-40 | Unlimited | All | ✅ | ✅ | 24/7 |
| Enterprise | Custom | Unlimited | All | ✅ | ✅ | Dedicated |

## 🔗 Related Documentation

- **Full Documentation**: `SUBSCRIPTION_SYSTEM.md`
- **Implementation Summary**: `PRICING_IMPLEMENTATION_SUMMARY.md`
- **Access Control**: `ACCESS_CONTROL.md`
- **Free Trial**: `FREE_TRIAL_IMPLEMENTATION.md`

## 🎓 Best Practices

1. **Always check subscription** before performing premium operations
2. **Use decorators** for simple feature gates
3. **Use context managers** for complex multi-feature checks
4. **Provide upgrade paths** in error messages
5. **Cache subscription data** when making multiple checks
6. **Handle edge cases** (expired, trial, past due)
7. **Log access attempts** for audit and analytics

## 🚨 Common Gotchas

1. **Anonymous Users**: Always return FREE plan for non-authenticated users
2. **API Keys**: System API keys might bypass subscription checks - be careful!
3. **Unlimited Features**: Check for "Unlimited" strings, not just numbers
4. **Volume Pricing**: Organization pricing depends on seat count
5. **Yearly vs Monthly**: Remember to check billing interval for correct pricing
6. **Trial Period**: New subscriptions default to 14-day trial
7. **Grace Period**: Expired subscriptions should get grace period before lockout

## 💰 Revenue Calculations

```python
# Calculate MRR (Monthly Recurring Revenue)
def calculate_mrr(subscriptions: dict) -> float:
    mrr = 0
    for sub in subscriptions.values():
        if sub["status"] == "active":
            amount = sub["amount"]
            if sub["billing_interval"] == "yearly":
                amount = amount / 12  # Convert yearly to monthly
            mrr += amount
    return mrr

# Calculate ARR (Annual Recurring Revenue)
def calculate_arr(subscriptions: dict) -> float:
    return calculate_mrr(subscriptions) * 12
```
