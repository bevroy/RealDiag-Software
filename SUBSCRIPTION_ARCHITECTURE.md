# Subscription System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         RealDiag Frontend                            │
│                    (React/Next.js Application)                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ HTTP/HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FastAPI Backend                              │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                    API Routers                              │    │
│  │                                                             │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │    │
│  │  │ Diagnostic   │  │ Integration  │  │ Education    │   │    │
│  │  │ Router       │  │ Router       │  │ Router       │   │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │    │
│  │         │                  │                  │            │    │
│  │         └──────────────────┼──────────────────┘            │    │
│  │                            │                               │    │
│  │                            ▼                               │    │
│  │                  ┌──────────────────┐                     │    │
│  │                  │ Subscription     │                     │    │
│  │                  │ Gate             │                     │    │
│  │                  │ (Feature Check)  │                     │    │
│  │                  └────────┬─────────┘                     │    │
│  │                           │                               │    │
│  └───────────────────────────┼───────────────────────────────┘    │
│                               │                                     │
│  ┌────────────────────────────┼──────────────────────────────┐    │
│  │        Subscription System │                               │    │
│  │                            ▼                               │    │
│  │    ┌──────────────────────────────────────────┐          │    │
│  │    │     Subscription Router                  │          │    │
│  │    │  (GET/POST/PUT/DELETE endpoints)         │          │    │
│  │    └──────────┬───────────────────────────────┘          │    │
│  │               │                                           │    │
│  │               ├──────────────────┬────────────────┐      │    │
│  │               ▼                  ▼                ▼      │    │
│  │    ┌──────────────┐   ┌──────────────┐  ┌──────────┐   │    │
│  │    │ Subscription │   │ Subscription │  │  Plan    │   │    │
│  │    │ Models       │   │ Gate         │  │  Pricing │   │    │
│  │    └──────┬───────┘   └──────────────┘  └──────────┘   │    │
│  │           │                                             │    │
│  └───────────┼─────────────────────────────────────────────┘    │
│              │                                                    │
│              ▼                                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           Data Storage                                    │   │
│  │                                                            │   │
│  │  ┌──────────────────┐         ┌────────────────────┐    │   │
│  │  │  In-Memory Store │  ──►    │  PostgreSQL DB     │    │   │
│  │  │  (Current)       │         │  (Future)          │    │   │
│  │  └──────────────────┘         └────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────────────┬──────────────────────────────┘
                                     │
                                     │ Webhooks (Future)
                                     ▼
                        ┌────────────────────────┐
                        │    Stripe Payment      │
                        │    Processing          │
                        └────────────────────────┘
```

## Component Breakdown

### 1. Subscription Router (`subscription_router.py`)
**Responsibilities**:
- Handle HTTP requests for subscription management
- Create, read, update, delete subscriptions
- Calculate pricing based on plan and seats
- Manage subscription lifecycle (trial, active, canceled)

**Key Endpoints**:
```
GET    /subscriptions/plans              → List all plans
GET    /subscriptions/plans/{plan_type}  → Get plan details
GET    /subscriptions/me                 → Get user subscription
POST   /subscriptions/me                 → Create subscription
PUT    /subscriptions/me                 → Update subscription
DELETE /subscriptions/me                 → Cancel subscription
GET    /subscriptions/features/{name}    → Check feature access
GET    /subscriptions/calculate-price    → Price calculator
```

### 2. Subscription Models (`subscription_models.py`)
**Responsibilities**:
- Define subscription data structures
- Store pricing configuration
- Provide helper functions for price calculations
- Define feature matrices for each plan

**Key Components**:
```python
# Enums
PlanType            # 11 subscription tiers
BillingInterval     # Monthly, Yearly, One-time
SubscriptionStatus  # Trial, Active, Past Due, Canceled, Expired

# Configuration
PRICING = {
    PlanType.INDIVIDUAL_PROFESSIONAL: {
        "name": "Professional",
        "price_monthly": 49,
        "features": {...}
    }
}

# Database Models (SQLAlchemy)
SubscriptionPlan    # Plan definitions
UserSubscription    # User subscriptions

# Helper Functions
get_plan_price()
get_plan_features()
check_feature_access()
calculate_organization_price()
```

### 3. Subscription Gate (`subscription_gate.py`)
**Responsibilities**:
- Enforce feature access control
- Check usage limits
- Provide decorators and context managers
- Generate appropriate error responses

**Usage Patterns**:

**Decorator Pattern**:
```python
@require_feature("api_access", user_subscriptions)
async def premium_endpoint(...):
    ...
```

**Context Manager Pattern**:
```python
async with SubscriptionGate(user, subscriptions) as gate:
    gate.require_feature("fhir_export")
    gate.require_limit("exports_per_month", current_exports)
    ...
```

### 4. Data Storage

#### Current: In-Memory Dictionary
```python
user_subscriptions = {
    "user_123": {
        "subscription_id": "sub_abc",
        "plan_type": "individual_professional",
        "status": "active",
        "amount": 49.0,
        "features": {...}
    }
}
```

**Pros**: Fast, simple, no database setup
**Cons**: Lost on restart, not scalable, no persistence

#### Future: PostgreSQL Database
```sql
subscription_plans
- id, plan_type, name, description
- features (JSONB)
- price_monthly, price_yearly

user_subscriptions
- id, user_id, subscription_id
- plan_type, status, billing_interval
- stripe_customer_id, stripe_subscription_id
- current_period_start, current_period_end
- trial_end, canceled_at
```

**Pros**: Persistent, scalable, relational
**Cons**: Requires setup, migrations

## Data Flow Diagrams

### User Subscription Creation Flow

```
User                 Frontend              Backend              Stripe
 │                      │                     │                   │
 │──Select Plan────────►│                     │                   │
 │                      │                     │                   │
 │                      │──POST /subscriptions/me                 │
 │                      │     + plan_type     │                   │
 │                      │     + billing_interval                  │
 │                      │────────────────────►│                   │
 │                      │                     │                   │
 │                      │                     │──Create Customer──►│
 │                      │                     │                   │
 │                      │                     │◄──Customer ID────│
 │                      │                     │                   │
 │                      │                     │──Create Sub───────►│
 │                      │                     │                   │
 │                      │                     │◄──Sub ID──────────│
 │                      │                     │                   │
 │                      │◄─Subscription Info──│                   │
 │                      │     + trial_days    │                   │
 │                      │     + subscription  │                   │
 │                      │                     │                   │
 │◄─Show Success Msg───│                     │                   │
 │   "14-day trial"     │                     │                   │
```

### Feature Access Check Flow

```
User Request
    │
    ▼
Authentication Middleware
    │
    ├─ No Token
    │     │
    │     ├─ Public Endpoint? ──Yes──► Allow (Free Plan Features)
    │     │
    │     └─ Protected Endpoint? ──Yes──► 401 Unauthorized
    │
    └─ Valid Token
          │
          ▼
    Get User from Token
          │
          ▼
    Lookup Subscription (user_subscriptions[user_id])
          │
          ├─ No Subscription ──► Use FREE Plan Features
          │
          └─ Has Subscription ──► Load Plan Features
                │
                ▼
          Subscription Gate Check
                │
                ├─ Feature Check
                │     │
                │     ├─ Has Feature? ──Yes──► Allow
                │     │
                │     └─ No Feature? ──No──► 403 Forbidden
                │                               + Upgrade Message
                │
                └─ Limit Check
                      │
                      ├─ Within Limit? ──Yes──► Allow
                      │
                      └─ Exceeded? ──No──► 429 Too Many Requests
                                            + Current Usage
                                            + Limit Value
```

### Plan Upgrade Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                          User Action                             │
│                  "Upgrade to Professional+"                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  Validate     │
                   │  - Current plan    Current: Professional ($49/mo)
                   │  - Target plan     Target: Professional+ ($69/mo)
                   │  - User eligible   ✓ Valid
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  Calculate    │
                   │  Proration    │
                   │               │      Days Remaining: 20
                   │               │      Old Plan Credit: $32.67
                   │               │      New Plan Charge: $46
                   │               │      Amount Due: $13.33
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  Process      │
                   │  Payment      │  ──────►  Stripe: Charge $13.33
                   │               │  ◄──────  Payment Succeeded
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  Update       │
                   │  Subscription │
                   │               │      Plan: Professional+
                   │               │      Amount: $69/mo
                   │               │      Features: [API, Analytics]
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  Notify User  │
                   │               │      Email: Upgrade Confirmed
                   │               │      Access: Immediate
                   └───────────────┘
```

## Feature Gating Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                     Endpoint Request                              │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │  Authentication Layer   │
              │  - JWT Token            │
              │  - API Key              │
              │  - Optional User        │
              └────────────┬────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │  Subscription Lookup    │
              │                         │
              │  If user:               │
              │    subscription = ...   │
              │  Else:                  │
              │    plan = FREE          │
              └────────────┬────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │   Feature Gate Check    │
              │                         │
              │  Decorator Method:      │
              │  @require_feature(...)  │
              │                         │
              │  OR                     │
              │                         │
              │  Context Manager:       │
              │  async with Gate:       │
              │    gate.require_*()     │
              └────────────┬────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
       ┌────────────────┐    ┌────────────────┐
       │  Feature Check │    │  Limit Check   │
       │                │    │                │
       │  has_feature() │    │  within_limit()│
       │                │    │                │
       │  check_feature_│    │  get_remaining()
       │  access()      │    │                │
       └───────┬────────┘    └───────┬────────┘
               │                     │
        ┌──────┴──────┐       ┌──────┴──────┐
        ▼             ▼       ▼             ▼
    ✅ Allow      ❌ 403   ✅ Allow      ❌ 429
    Continue      Forbidden  Continue     Rate Limit
                  {                       {
                    error: "...",           error: "...",
                    upgrade: true           limit: 50,
                  }                         usage: 51
                                          }
```

## Integration Points

### 1. Diagnostic Router Integration
```python
# Before evaluation, check module access
async with SubscriptionGate(user, subscriptions) as gate:
    if tree_module == "neurology":
        gate.require_feature("modules_neurology")
    
    # Perform evaluation
    result = evaluate_tree(...)
```

### 2. Integration Router (Export)
```python
# Check export format permissions
async with SubscriptionGate(user, subscriptions) as gate:
    if format == "fhir":
        gate.require_feature("fhir_export")  # Professional+
    elif format == "hl7":
        gate.require_feature("ehr_integration")  # Organization+
```

### 3. Education Router (Module Access)
```python
# Check module access for educational content
async with SubscriptionGate(user, subscriptions) as gate:
    gate.require_feature(f"modules_{module_name}")
```

## Error Response Flow

```
Feature Access Denied
│
├─ 401 Unauthorized
│   └─ No valid token/authentication
│       Response: "Authentication required"
│
├─ 403 Forbidden
│   └─ Valid auth but insufficient plan
│       Response: {
│         "error": "Feature not available in your plan",
│         "feature": "api_access",
│         "current_plan": "individual_starter",
│         "upgrade_required": true,
│         "message": "Upgrade to Professional+ for API access",
│         "upgrade_url": "/subscriptions/plans/individual_professional_plus"
│       }
│
└─ 429 Too Many Requests
    └─ Valid auth but exceeded usage limit
        Response: {
          "error": "Usage limit exceeded",
          "feature": "exports_per_month",
          "limit": 50,
          "current_usage": 51,
          "reset_date": "2025-02-01",
          "upgrade_required": true,
          "message": "You've used all 50 exports this month"
        }
```

## Scalability Considerations

### Current State (MVP)
- In-memory storage
- Single server
- Manual subscription management
- ~1,000 users max

### Growth Phase (Phase 1)
- PostgreSQL database
- Connection pooling
- Read replicas
- ~10,000 users

### Scale Phase (Phase 2)
- Redis caching layer
- Load balancing
- Multi-region deployment
- ~100,000+ users

### Enterprise Scale (Phase 3)
- Microservices architecture
- Kubernetes orchestration
- Multi-tenancy
- Millions of users

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Transport Security                                      │
│     • HTTPS/TLS 1.3                                         │
│     • Certificate pinning                                   │
│                                                             │
│  2. Authentication                                          │
│     • JWT tokens (HS256)                                    │
│     • HttpOnly cookies                                      │
│     • API keys (rdiag_...)                                  │
│                                                             │
│  3. Authorization                                           │
│     • Subscription-based access control                     │
│     • Feature gating                                        │
│     • Role-based permissions                                │
│                                                             │
│  4. Rate Limiting                                           │
│     • Global: 1000 req/hour                                 │
│     • Auth endpoints: 10 req/hour                           │
│     • Search: Plan-based limits                             │
│                                                             │
│  5. Data Protection                                         │
│     • Subscription data encryption at rest                  │
│     • PCI compliance (via Stripe)                           │
│     • Audit logging                                         │
│                                                             │
│  6. Payment Security                                        │
│     • Stripe integration (PCI DSS Level 1)                  │
│     • No card data stored                                   │
│     • Webhook signature verification                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Monitoring & Observability

```
┌────────────────────────────────────────────────────────────────┐
│                     Metrics & Monitoring                        │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Application Metrics (Prometheus)                               │
│  • subscription_creations_total                                 │
│  • subscription_upgrades_total                                  │
│  • subscription_cancellations_total                             │
│  • subscription_revenue_mrr                                     │
│  • feature_access_denied_total                                  │
│  • feature_access_granted_total                                 │
│                                                                 │
│  Business Metrics                                               │
│  • MRR (Monthly Recurring Revenue)                              │
│  • ARR (Annual Recurring Revenue)                               │
│  • Churn Rate                                                   │
│  • LTV (Lifetime Value)                                         │
│  • CAC (Customer Acquisition Cost)                              │
│                                                                 │
│  Error Tracking (Sentry)                                        │
│  • Payment failures                                             │
│  • Subscription creation errors                                 │
│  • Feature gate errors                                          │
│                                                                 │
│  Logging (Structured)                                           │
│  • Subscription lifecycle events                                │
│  • Payment transactions                                         │
│  • Feature access attempts                                      │
│  • Admin actions                                                │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## Future Architecture (with Stripe)

```
┌──────────────┐
│   Frontend   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│                FastAPI Backend                   │
│                                                  │
│  ┌────────────────────────────────────────┐    │
│  │      Subscription Router               │    │
│  │                                         │    │
│  │  POST /subscriptions/me                │    │
│  │    ├─► Create Stripe Customer          │────┼──► Stripe API
│  │    ├─► Create Stripe Subscription      │    │   (Create Customer)
│  │    └─► Store subscription_id           │◄───┼─── Customer ID
│  │                                         │    │
│  └─────────────────┬───────────────────────┘    │
│                    │                             │
│  ┌─────────────────▼──────────────────────┐    │
│  │     Subscription Storage               │    │
│  │     (PostgreSQL)                       │    │
│  │                                         │    │
│  │  • user_subscriptions                  │    │
│  │    - stripe_customer_id                │    │
│  │    - stripe_subscription_id            │    │
│  │    - status, plan, features            │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
│  ┌────────────────────────────────────────┐    │
│  │     Webhook Handler                    │    │
│  │                                         │    │
│  │  POST /webhooks/stripe                 │◄───┼─── Stripe Webhook
│  │    ├─► Verify signature                │    │
│  │    ├─► Process event                   │    │
│  │    │    • invoice.paid                  │    │
│  │    │    • subscription.updated          │    │
│  │    │    • subscription.deleted          │    │
│  │    └─► Update subscription status      │    │
│  └─────────────────────────────────────────┘    │
└──────────────────────────────────────────────────┘
```

## Summary

This subscription system provides:
1. **11 flexible plan types** covering all user segments
2. **Feature-based access control** enforced at endpoint level
3. **Usage-based limits** with clear upgrade paths
4. **Scalable architecture** from MVP to enterprise
5. **Payment integration ready** (Stripe webhooks prepared)
6. **Comprehensive monitoring** for business and technical metrics
