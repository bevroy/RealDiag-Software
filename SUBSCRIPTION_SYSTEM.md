# Subscription System Documentation

## Overview

The RealDiag subscription system provides tiered access to diagnostic features, modules, and integration capabilities. It includes 11 different plan types designed for individuals, organizations, academic institutions, non-profits, and enterprises.

## Plan Types

### 1. Free Plan
- **Price**: Free
- **Features**:
  - 10 diagnostic searches per week
  - Limited to 1 diagnostic module
  - Basic features only
  - Community support
- **Target**: Trial users, evaluation

### 2. Individual Plans

#### Starter ($29/month)
- **Features**:
  - Unlimited searches
  - 1 diagnostic module
  - Basic export (JSON)
  - Email support
- **Target**: Solo practitioners, students

#### Professional ($49/month)
- **Features**:
  - Unlimited searches
  - All diagnostic modules
  - FHIR export
  - Priority email support
  - Search history & favorites
- **Target**: Active clinicians

#### Professional Plus ($69/month)
- **Features**:
  - Everything in Professional
  - Advanced analytics
  - API access
  - Priority phone support
  - Custom lists & workflows
- **Target**: Power users, research

### 3. Organization Plans ($24-40/month per seat)

Volume-based pricing:
- 1-10 seats: $40/seat/month
- 11-50 seats: $32/seat/month
- 51-100 seats: $28/seat/month
- 100+ seats: $24/seat/month

**Features**:
- All Professional Plus features
- Admin dashboard
- User management
- EHR integration (HL7/FHIR)
- Bulk export
- SSO (Single Sign-On)
- Dedicated account manager
- 24/7 support

**Annual Billing**: Save 2 months (10 months price for 12 months service)

### 4. Academic Plans

#### Faculty ($25/month)
- All Professional features
- Teaching mode
- Simulated cases
- Student analytics
- Educational resources

#### Residents ($12/month)
- All Professional features
- Board prep materials
- Case reviews
- Study guides

#### Students (Free)
- Basic diagnostic access
- Educational modules
- Limited searches (50/month)
- Learning resources

### 5. Non-Profit Plans

#### Standard ($18/month)
- All Professional features
- Non-profit discount (40% off)
- Mission-focused support
- Resource optimization

#### Expanded ($10/month)
- Discounted plan for safety-net organizations
- Essential features
- Community health focus
- Grant-friendly pricing

### 6. Enterprise (Custom Pricing)

**Base Range**: $75,000 - $250,000/year

**Features**:
- Unlimited seats
- White-label solution
- Custom SLA
- On-premise deployment option
- Custom integrations
- Dedicated infrastructure
- 24/7 premium support
- Training & onboarding
- Custom analytics

## API Endpoints

### Plan Information

#### `GET /subscriptions/plans`
List all available subscription plans.

**Query Parameters**:
- `user_type` (optional): Filter by user type (individual, organization, academic, nonprofit)

**Response**:
```json
{
  "plans": [
    {
      "plan_type": "individual_professional",
      "name": "Professional",
      "description": "Full access to all diagnostic modules",
      "price_monthly": 49,
      "price_yearly": 490,
      "features": {
        "searches_per_month": "Unlimited",
        "modules_neurology": true,
        "modules_cardiology": true,
        "fhir_export": true,
        "support_level": "Priority email"
      },
      "recommended": false
    }
  ],
  "total": 11
}
```

#### `GET /subscriptions/plans/{plan_type}`
Get detailed information about a specific plan.

**Path Parameters**:
- `plan_type`: Plan identifier (e.g., `individual_professional`)

**Query Parameters**:
- `seats` (optional): Number of seats for organization plans
- `billing_interval` (optional): `monthly` or `yearly`

**Response**:
```json
{
  "plan_type": "organization",
  "name": "Organization",
  "description": "Complete solution for healthcare organizations",
  "price": 2880,
  "price_per_seat": 32,
  "billing_interval": "monthly",
  "currency": "USD",
  "features": {
    "searches_per_month": "Unlimited",
    "admin_dashboard": true,
    "ehr_integration": true,
    "sso": true
  },
  "savings_yearly": "576.00"
}
```

### User Subscriptions

#### `GET /subscriptions/me`
Get current user's subscription information.

**Authentication**: Required

**Response**:
```json
{
  "subscribed": true,
  "subscription_id": "sub_abc123",
  "user_id": "user_123",
  "plan_type": "individual_professional",
  "plan_name": "Professional",
  "status": "active",
  "billing_interval": "monthly",
  "amount": 49.0,
  "currency": "USD",
  "current_period_start": "2025-01-01T00:00:00",
  "current_period_end": "2025-02-01T00:00:00",
  "trial_end": null,
  "seats": 1,
  "features": {
    "searches_per_month": "Unlimited",
    "modules_neurology": true,
    "fhir_export": true
  },
  "auto_renew": true
}
```

#### `POST /subscriptions/me`
Create a new subscription for the current user.

**Authentication**: Required

**Request Body**:
```json
{
  "plan_type": "individual_professional",
  "billing_interval": "monthly",
  "seats": 1,
  "payment_method_id": "pm_card_visa",
  "metadata": {
    "specialty": "neurology",
    "institution": "General Hospital"
  }
}
```

**Response**:
```json
{
  "message": "Subscription created successfully",
  "subscription": {
    "subscription_id": "sub_abc123",
    "status": "trial",
    "trial_end": "2025-01-15T00:00:00"
  },
  "trial_days": 14,
  "next_steps": [
    "Complete payment setup before trial ends",
    "Explore all features during your trial",
    "Contact support if you need help"
  ]
}
```

#### `PUT /subscriptions/me`
Update current user's subscription (upgrade/downgrade, change billing).

**Authentication**: Required

**Request Body**:
```json
{
  "plan_type": "individual_professional_plus",
  "billing_interval": "yearly",
  "seats": 1,
  "auto_renew": true
}
```

#### `DELETE /subscriptions/me`
Cancel current user's subscription.

**Authentication**: Required

**Response**:
```json
{
  "message": "Subscription canceled successfully",
  "access_until": "2025-02-01T00:00:00",
  "reactivate_url": "/subscriptions/me/reactivate"
}
```

#### `POST /subscriptions/me/reactivate`
Reactivate a canceled subscription (before expiration).

**Authentication**: Required

### Feature Checking

#### `GET /subscriptions/features/{feature_name}`
Check if current user has access to a specific feature.

**Path Parameters**:
- `feature_name`: Feature identifier (e.g., `fhir_export`, `api_access`)

**Response**:
```json
{
  "feature": "fhir_export",
  "has_access": true,
  "plan": "individual_professional",
  "message": null
}
```

### Pricing Calculator

#### `GET /subscriptions/calculator`
Interactive web-based pricing calculator (HTML page).

**Type**: Public HTML Page

**Features**:
- Customer type selection (Individual, Organization, Academic, Non-Profit)
- Plan selection for individuals
- Real-time price calculations
- Volume discount visualization
- Annual savings calculator
- Feature comparison

**Access**: `http://localhost:8000/subscriptions/calculator`

#### `GET /subscriptions/calculate-price`
Calculate price for a given plan configuration (API endpoint).

**Query Parameters**:
- `plan_type`: Plan identifier
- `billing_interval`: `monthly` or `yearly`
- `seats`: Number of seats (for organization plans)

**Response**:
```json
{
  "plan_type": "organization",
  "billing_interval": "yearly",
  "seats": 25,
  "price_per_seat": 32.00,
  "total_price": 9600.00,
  "currency": "USD",
  "savings": 1920.00,
  "yearly_discount": "2 months free"
}
```

## Feature Gating

### Using Decorators

```python
from backend.services.subscription_gate import require_feature, require_plan
from backend.services.subscription_router import user_subscriptions

@router.post("/premium-endpoint")
@require_feature("api_access", user_subscriptions)
async def premium_endpoint(current_user: dict = Depends(get_current_user)):
    # Only accessible to users with API access feature
    return {"data": "premium content"}

@router.get("/professional-feature")
@require_plan(PlanType.INDIVIDUAL_PROFESSIONAL, user_subscriptions)
async def pro_feature(current_user: dict = Depends(get_current_user)):
    # Only accessible to Professional plan and above
    return {"feature": "professional"}
```

### Using Context Manager

```python
from backend.services.subscription_gate import SubscriptionGate
from backend.services.subscription_router import user_subscriptions

@router.post("/export")
async def export_data(current_user: dict = Depends(get_current_user)):
    async with SubscriptionGate(current_user, user_subscriptions) as gate:
        # Check feature access
        gate.require_feature("bulk_export")
        
        # Check usage limits
        gate.require_limit("exports_per_month", current_exports)
        
        # Get remaining quota
        remaining = gate.get_remaining("exports_per_month", current_exports)
        
        # Perform export
        return {"exported": True, "remaining": remaining}
```

## Feature Keys

Features are defined in subscription plans and can be checked programmatically:

### Search & Access
- `searches_per_month`: Number of searches allowed (or "Unlimited")
- `concurrent_sessions`: Maximum concurrent sessions

### Module Access
- `modules_neurology`: Access to neurology module
- `modules_cardiology`: Access to cardiology module
- `modules_pulmonology`: Access to pulmonology module
- `modules_gastroenterology`: Access to gastroenterology module
- `modules_all`: Access to all modules (boolean)

### Export Features
- `fhir_export`: FHIR R4 export capability
- `hl7_export`: HL7 v2 messaging
- `bulk_export`: Bulk export (CSV, XML)
- `exports_per_month`: Number of exports allowed

### Integration Features
- `api_access`: REST API access
- `webhook_support`: Webhook notifications
- `ehr_integration`: EHR system integration
- `sso`: Single Sign-On

### Advanced Features
- `admin_dashboard`: Organization admin panel
- `user_management`: Multi-user management
- `custom_workflows`: Custom diagnostic workflows
- `advanced_analytics`: Advanced usage analytics
- `white_label`: White-label customization
- `on_premise`: On-premise deployment

### Support
- `support_level`: Support tier ("Community", "Email", "Priority email", "Phone", "24/7", "Dedicated")

## Usage Limits

Different plans have different usage limits:

| Plan | Searches/Month | Modules | Exports/Month | API Calls/Day |
|------|----------------|---------|---------------|---------------|
| Free | 10/week | 1 | 0 | 0 |
| Starter | Unlimited | 1 | 10 | 0 |
| Professional | Unlimited | All | 50 | 0 |
| Professional+ | Unlimited | All | Unlimited | 1000 |
| Organization | Unlimited | All | Unlimited | 10000 |
| Enterprise | Unlimited | All | Unlimited | Unlimited |

## Payment Integration

### Stripe Integration (To Be Implemented)

The subscription system is designed to integrate with Stripe:

1. **Customer Creation**: Each user gets a Stripe customer ID
2. **Payment Methods**: Store payment methods in Stripe
3. **Subscriptions**: Create Stripe subscriptions linked to plans
4. **Webhooks**: Handle Stripe webhooks for:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

### Webhook Handler (To Be Implemented)

```python
@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    # Verify webhook signature
    # Process webhook event
    # Update subscription status
    pass
```

## Testing

### Test User Subscription Creation

```bash
curl -X POST http://localhost:8000/subscriptions/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_type": "individual_professional",
    "billing_interval": "monthly"
  }'
```

### Test Feature Access

```bash
curl http://localhost:8000/subscriptions/features/fhir_export \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Test Plan Listing

```bash
curl http://localhost:8000/subscriptions/plans
```

### Test Price Calculation

```bash
curl "http://localhost:8000/subscriptions/calculate-price?plan_type=organization&seats=25&billing_interval=yearly"
```

## Migration Path

For existing users without subscriptions:

1. **Default to Free Plan**: Users without subscriptions get free plan features
2. **Trial Period**: New paid subscriptions get 14-day trial
3. **Grace Period**: Expired subscriptions get 7-day grace period
4. **Downgrade Protection**: Features remain available until current period ends

## Admin Operations

### Manual Subscription Management

```python
# Grant subscription to user
subscription = create_subscription(user_id, SubscriptionCreate(
    plan_type=PlanType.INDIVIDUAL_PROFESSIONAL,
    billing_interval=BillingInterval.YEARLY
))

# Update subscription
user_subscriptions[user_id]["plan_type"] = "individual_professional_plus"

# Cancel subscription
user_subscriptions[user_id]["status"] = "canceled"

# Refund and cancel
del user_subscriptions[user_id]
```

## Best Practices

1. **Always check feature access** before allowing operations
2. **Use decorators** for endpoint-level protection
3. **Use context managers** for complex multi-feature checks
4. **Provide clear upgrade messages** when features are restricted
5. **Track usage** to enforce monthly limits
6. **Cache subscription data** to minimize lookups
7. **Handle edge cases** (expired, past due, trial expired)

## Future Enhancements

- [ ] Stripe payment integration
- [ ] Usage tracking and analytics
- [ ] Automated invoicing
- [ ] Subscription upgrade flow UI
- [ ] Admin dashboard for subscription management
- [ ] Referral program
- [ ] Annual plan promotions
- [ ] Custom enterprise contracts
- [ ] Usage-based pricing options
