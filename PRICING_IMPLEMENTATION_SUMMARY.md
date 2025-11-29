# Pricing System Implementation Summary

## Overview

A comprehensive subscription and pricing system has been implemented for RealDiag, featuring 11 different plan types across 5 main tiers: Individual, Organization, Academic, Non-Profit, and Enterprise.

## Files Created

### 1. **backend/services/subscription_models.py** (~450 lines)
**Purpose**: Core data models and pricing configuration

**Key Components**:
- `PlanType` enum: 11 subscription plan types
- `BillingInterval` enum: Monthly, Yearly, One-time
- `SubscriptionStatus` enum: Trial, Active, Past Due, Canceled, Expired
- `PRICING` dict: Complete feature matrix for all plans
- SQLAlchemy models: `SubscriptionPlan`, `UserSubscription`
- Helper functions:
  - `get_plan_price()`: Get price for any plan/interval
  - `get_plan_features()`: Get feature list for a plan
  - `check_feature_access()`: Check if plan has feature access
  - `calculate_organization_price()`: Volume-based pricing calculator
  - `get_recommended_plan()`: Plan recommendations by user type

**Features**:
- Volume-based organization pricing (1-10: $40, 11-50: $32, 51-100: $28, 100+: $24 per seat)
- Yearly billing discount (2 months free)
- Comprehensive feature definitions per plan
- Prepared for Stripe integration

### 2. **backend/services/subscription_router.py** (~650 lines)
**Purpose**: API endpoints for subscription management

**Endpoints**:
- `GET /subscriptions/plans` - List all plans
- `GET /subscriptions/plans/{plan_type}` - Plan details
- `GET /subscriptions/me` - Current user's subscription
- `POST /subscriptions/me` - Create subscription
- `PUT /subscriptions/me` - Update/upgrade subscription
- `DELETE /subscriptions/me` - Cancel subscription
- `POST /subscriptions/me/reactivate` - Reactivate canceled subscription
- `GET /subscriptions/features/{feature_name}` - Check feature access
- `GET /subscriptions/calculate-price` - Price calculator

**Features**:
- In-memory subscription storage (upgradeable to database)
- 14-day trial period for paid plans
- Automatic price calculation based on seats and billing interval
- Feature access verification
- Upgrade/downgrade support
- Cancellation with access-until-end-of-period

### 3. **backend/services/subscription_gate.py** (~400 lines)
**Purpose**: Feature gating and access control utilities

**Components**:

**Decorators**:
- `@require_feature(feature_name)`: Require specific feature access
- `@require_plan(minimum_plan)`: Require minimum plan level

**Context Manager**:
- `SubscriptionGate`: Async context manager for complex checks
  - `has_feature(feature_name)`: Check feature availability
  - `within_limit(feature_name, usage)`: Check usage limits
  - `get_remaining(feature_name, usage)`: Get remaining quota
  - `require_feature(feature_name)`: Enforce feature access (raises 403)
  - `require_limit(feature_name, usage)`: Enforce usage limits (raises 429)

**Middleware Helpers**:
- `add_subscription_context()`: Add subscription to request state
- `get_plan_from_request()`: Extract plan from request
- `get_features_from_request()`: Extract features from request

### 4. **SUBSCRIPTION_SYSTEM.md** (~500 lines)
**Purpose**: Complete documentation for the subscription system

**Contents**:
- Plan type descriptions with pricing
- API endpoint documentation
- Feature gating examples
- Usage limits table
- Payment integration guide (Stripe)
- Testing instructions
- Best practices
- Future enhancements

### 5. **test_subscriptions.py** (~300 lines)
**Purpose**: Automated test suite for subscription API

**Test Coverage**:
- ✅ List all plans
- ✅ Get plan details
- ✅ Calculate organization pricing
- ✅ Register test user
- ✅ Check subscription status
- ✅ Create subscription
- ✅ Check feature access
- ✅ Upgrade subscription
- ✅ Anonymous feature checks
- ✅ Cancel subscription

## Files Modified

### 1. **backend/services/diagnostic_router.py**
**Changes**:
- Added subscription gate import
- Added module access checks based on subscription
- Integrated with free trial system
- Enforces subscription limits for authenticated users
- Shows appropriate upgrade messages

**Before**: Free trial limits for anonymous only
**After**: Subscription-based access for all users

### 2. **backend/services/integration_router.py**
**Changes**:
- Added subscription gate import
- Added feature checks for export formats:
  - JSON: All plans
  - FHIR: Professional+ and above
  - HL7: Organization and above
  - Bulk Export: Enterprise only
- Enforces subscription requirements on export endpoints

**Before**: Authentication only
**After**: Authentication + subscription-based feature access

### 3. **backend/main.py**
**Changes**:
- Added subscription router import
- Registered subscription router with FastAPI app

**Before**: 8 routers
**After**: 9 routers (added subscription_router)

## Pricing Structure

### Individual Plans
| Plan | Monthly | Yearly | Features |
|------|---------|--------|----------|
| **Free** | $0 | - | 10 searches/week, 1 module |
| **Starter** | $29 | $290 | Unlimited searches, 1 module, JSON export |
| **Professional** | $49 | $490 | All modules, FHIR export, priority support |
| **Professional Plus** | $69 | $690 | API access, analytics, phone support |

### Organization Plans
**Volume-Based Pricing** (per seat/month):
- 1-10 seats: $40
- 11-50 seats: $32
- 51-100 seats: $28
- 100+ seats: $24

**Features**: Admin dashboard, EHR integration, SSO, 24/7 support

### Academic Plans
| Role | Monthly | Features |
|------|---------|----------|
| **Faculty** | $25 | Teaching mode, simulated cases |
| **Residents** | $12 | Board prep, case reviews |
| **Students** | Free | Educational access, 50 searches/month |

### Non-Profit Plans
| Tier | Monthly | Discount |
|------|---------|----------|
| **Standard** | $18 | 40% off Professional |
| **Expanded** | $10 | Safety-net organizations |

### Enterprise
**Custom Pricing**: $75,000 - $250,000/year
- White-label solution
- Custom SLA
- On-premise deployment
- Unlimited seats
- Dedicated infrastructure

## Feature Matrix

### Search & Access
- `searches_per_month`: Unlimited (except Free: 10/week)
- `concurrent_sessions`: 1-10 depending on plan

### Module Access
- `modules_neurology`, `modules_cardiology`, etc.
- `modules_all`: Boolean for all-module access

### Export Features
- `fhir_export`: Professional+ and above
- `hl7_export`: Organization and above
- `bulk_export`: Enterprise only
- `exports_per_month`: 10-Unlimited

### Integration Features
- `api_access`: Professional+ and above
- `webhook_support`: Organization and above
- `ehr_integration`: Organization and above
- `sso`: Organization and above

### Advanced Features
- `admin_dashboard`: Organization and above
- `user_management`: Organization and above
- `white_label`: Enterprise only
- `on_premise`: Enterprise only
- `advanced_analytics`: Professional+ and above

### Support Levels
- Free: Community
- Starter/Academic Student: Email
- Professional/Academic: Priority email
- Professional+: Phone support
- Organization: 24/7 support
- Enterprise: Dedicated support

## Integration Points

### 1. Diagnostic Router
```python
# Check module access based on subscription
async with SubscriptionGate(current_user, user_subscriptions) as gate:
    if not gate.has_feature(f"modules_{module_name}"):
        raise HTTPException(403, "Upgrade to access this module")
```

### 2. Integration Router
```python
# Check export format access
if export_format == "fhir":
    gate.require_feature("fhir_export")
elif export_format == "hl7":
    gate.require_feature("ehr_integration")
```

### 3. Usage Tracking (Future)
```python
# Check monthly limits
async with SubscriptionGate(user, subscriptions) as gate:
    gate.require_limit("searches_per_month", user_searches)
```

## API Usage Examples

### Check Available Plans
```bash
curl http://localhost:8000/subscriptions/plans
```

### Get Plan Details
```bash
curl http://localhost:8000/subscriptions/plans/individual_professional
```

### Calculate Organization Price
```bash
curl "http://localhost:8000/subscriptions/calculate-price?plan_type=organization&seats=25&billing_interval=yearly"
```

### Create Subscription (Authenticated)
```bash
curl -X POST http://localhost:8000/subscriptions/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_type": "individual_professional",
    "billing_interval": "monthly"
  }'
```

### Check Subscription Status
```bash
curl http://localhost:8000/subscriptions/me \
  -H "Authorization: Bearer $TOKEN"
```

### Check Feature Access
```bash
curl http://localhost:8000/subscriptions/features/fhir_export \
  -H "Authorization: Bearer $TOKEN"
```

### Upgrade Subscription
```bash
curl -X PUT http://localhost:8000/subscriptions/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_type": "individual_professional_plus",
    "billing_interval": "yearly"
  }'
```

## Testing

### Run Test Suite
```bash
# Make sure backend is running
python backend/main.py &

# Run tests
python test_subscriptions.py
```

**Test Coverage**:
- ✅ Public plan listing
- ✅ Plan detail retrieval
- ✅ Price calculations
- ✅ User registration
- ✅ Subscription creation
- ✅ Feature access checks
- ✅ Subscription upgrades
- ✅ Subscription cancellation

## Next Steps

### Phase 1: Core Enhancements
1. **Database Migration**
   - Replace in-memory storage with PostgreSQL
   - Create migration scripts
   - Populate subscription_plans table

2. **Usage Tracking**
   - Implement monthly usage counters
   - Add usage analytics per user
   - Enforce monthly limits

3. **Admin Dashboard**
   - Subscription management UI
   - Revenue reporting
   - User analytics
   - Manual adjustments

### Phase 2: Payment Integration
1. **Stripe Setup**
   - Configure Stripe account
   - Add Stripe SDK
   - Create customer records
   - Link payment methods

2. **Webhook Handlers**
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `customer.subscription.deleted`

3. **Payment UI**
   - Checkout flow
   - Payment method management
   - Billing history
   - Invoice downloads

### Phase 3: Advanced Features
1. **Feature Gating**
   - Complete middleware implementation
   - Add to all protected endpoints
   - Grace period handling
   - Trial expiration workflows

2. **Subscription Management**
   - Upgrade flow with prorating
   - Downgrade protection
   - Cancellation surveys
   - Win-back campaigns

3. **Analytics & Reporting**
   - MRR (Monthly Recurring Revenue)
   - Churn rate
   - LTV (Lifetime Value)
   - Plan conversion rates

### Phase 4: Enterprise Features
1. **Organization Management**
   - Seat allocation
   - User invitation
   - Role-based access
   - Department organization

2. **Custom Contracts**
   - Enterprise pricing calculator
   - Quote generation
   - Contract management
   - Custom SLA tracking

3. **Integrations**
   - SSO (SAML, OAuth)
   - SCIM user provisioning
   - Audit logging
   - Compliance reports

## Technical Architecture

### Data Flow
```
User Request
    ↓
Authentication (JWT/API Key)
    ↓
Subscription Lookup (user_subscriptions)
    ↓
Feature Gate Check (SubscriptionGate)
    ↓
Usage Limit Verification
    ↓
Endpoint Handler
    ↓
Response
```

### Storage Structure (Current: In-Memory)
```python
user_subscriptions = {
    "user_123": {
        "subscription_id": "sub_abc",
        "plan_type": "individual_professional",
        "status": "active",
        "billing_interval": "monthly",
        "amount": 49.0,
        "features": {...},
        "current_period_end": "2025-02-01T00:00:00"
    }
}
```

### Storage Structure (Future: Database)
```sql
-- subscription_plans table
CREATE TABLE subscription_plans (
    id SERIAL PRIMARY KEY,
    plan_type VARCHAR(50) UNIQUE,
    name VARCHAR(100),
    description TEXT,
    features JSONB,
    price_monthly DECIMAL,
    price_yearly DECIMAL
);

-- user_subscriptions table
CREATE TABLE user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    subscription_id VARCHAR(100) UNIQUE,
    plan_type VARCHAR(50),
    status VARCHAR(20),
    stripe_customer_id VARCHAR(100),
    stripe_subscription_id VARCHAR(100),
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    trial_end TIMESTAMP,
    canceled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Configuration

### Environment Variables (Future)
```bash
# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Subscription Settings
TRIAL_DAYS=14
GRACE_PERIOD_DAYS=7
ENABLE_FREE_TIER=true

# Feature Flags
ENABLE_ORGANIZATION_PLANS=true
ENABLE_ACADEMIC_PRICING=true
ENABLE_ENTERPRISE_PRICING=true
```

## Security Considerations

1. **Subscription Verification**
   - Always verify subscription status before granting access
   - Check expiration dates
   - Handle past-due accounts gracefully

2. **Feature Access**
   - Use decorators for endpoint protection
   - Double-check in business logic
   - Log access attempts for audit

3. **Payment Security**
   - Never store credit card data
   - Use Stripe for PCI compliance
   - Verify webhook signatures

4. **Fraud Prevention**
   - Rate limit subscription changes
   - Monitor unusual patterns
   - Verify email addresses
   - Implement grace periods

## Monitoring & Alerts

### Key Metrics to Track
- New subscriptions per day
- Churn rate (cancellations)
- MRR growth
- Plan distribution
- Failed payments
- Feature usage by plan
- Support tickets by plan

### Alerts to Configure
- Payment failures
- Subscription cancellations
- Trial expirations approaching
- High-value customer changes
- System errors in billing

## Conclusion

The subscription system is now fully implemented and ready for testing. The architecture is designed to scale from in-memory storage to a full database-backed solution with Stripe integration.

**Status**: ✅ Core implementation complete
**Next Priority**: Database migration and Stripe integration
**Documentation**: Complete in SUBSCRIPTION_SYSTEM.md
**Testing**: Automated test suite available (test_subscriptions.py)
