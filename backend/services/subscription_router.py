"""
Subscription Management Router
===============================

API endpoints for subscription management, plan selection, and billing.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
from backend.services.auth_service import get_current_user, get_optional_user
from backend.services.subscription_models import (
    PlanType, BillingInterval, SubscriptionStatus,
    PRICING, get_plan_price, get_plan_features, check_feature_access,
    get_all_plans, calculate_organization_price, get_recommended_plan
)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])
templates = Jinja2Templates(directory="backend/templates")

# In-memory subscription storage (replace with database in production)
user_subscriptions: Dict[str, Dict[str, Any]] = {}


# ========== REQUEST/RESPONSE MODELS ==========

class SubscriptionCreate(BaseModel):
    """Request to create a new subscription."""
    plan_type: PlanType
    billing_interval: BillingInterval = BillingInterval.MONTHLY
    organization_name: Optional[str] = None
    seats: int = Field(default=1, ge=1)
    payment_method_id: Optional[str] = None
    metadata: Dict[str, Any] = {}


class SubscriptionUpdate(BaseModel):
    """Request to update an existing subscription."""
    plan_type: Optional[PlanType] = None
    billing_interval: Optional[BillingInterval] = None
    seats: Optional[int] = Field(default=None, ge=1)
    auto_renew: Optional[bool] = None


class SubscriptionResponse(BaseModel):
    """Subscription information response."""
    subscription_id: str
    user_id: str
    plan_type: PlanType
    plan_name: str
    status: SubscriptionStatus
    billing_interval: BillingInterval
    amount: float
    currency: str = "USD"
    current_period_start: str
    current_period_end: str
    trial_end: Optional[str] = None
    seats: int
    organization_name: Optional[str] = None
    features: Dict[str, Any]
    auto_renew: bool


class PlanInfo(BaseModel):
    """Information about a subscription plan."""
    plan_type: PlanType
    name: str
    description: str
    price_monthly: Optional[float]
    price_yearly: Optional[float]
    features: Dict[str, Any]
    recommended: bool = False


# ========== HELPER FUNCTIONS ==========

def get_user_subscription(user_id: str) -> Optional[Dict[str, Any]]:
    """Get active subscription for a user."""
    return user_subscriptions.get(user_id)


def create_subscription(user_id: str, subscription_data: SubscriptionCreate) -> Dict[str, Any]:
    """Create a new subscription for a user."""
    import secrets
    
    subscription_id = f"sub_{secrets.token_hex(16)}"
    now = datetime.utcnow()
    
    # Calculate period dates
    trial_end = now + timedelta(days=14)  # 14-day trial
    
    if subscription_data.billing_interval == BillingInterval.MONTHLY:
        period_end = now + timedelta(days=30)
    else:  # YEARLY
        period_end = now + timedelta(days=365)
    
    # Calculate amount
    if subscription_data.plan_type == PlanType.ORGANIZATION:
        amount = calculate_organization_price(subscription_data.seats, subscription_data.billing_interval)
    else:
        amount = get_plan_price(subscription_data.plan_type, subscription_data.billing_interval) or 0
    
    # Get features
    features = get_plan_features(subscription_data.plan_type)
    
    subscription = {
        "subscription_id": subscription_id,
        "user_id": user_id,
        "plan_type": subscription_data.plan_type.value,
        "plan_name": PRICING[subscription_data.plan_type]["name"],
        "status": SubscriptionStatus.TRIAL.value if amount > 0 else SubscriptionStatus.ACTIVE.value,
        "billing_interval": subscription_data.billing_interval.value,
        "amount": amount,
        "currency": "USD",
        "current_period_start": now.isoformat(),
        "current_period_end": period_end.isoformat(),
        "trial_end": trial_end.isoformat() if amount > 0 else None,
        "seats": subscription_data.seats,
        "organization_name": subscription_data.organization_name,
        "features": features,
        "auto_renew": True,
        "payment_method_id": subscription_data.payment_method_id,
        "metadata": subscription_data.metadata,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }
    
    user_subscriptions[user_id] = subscription
    return subscription


# ========== API ENDPOINTS ==========

@router.get("/plans")
async def list_plans(
    request: Request,
    user_type: Optional[str] = None,
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """
    List all available subscription plans.
    
    Query parameters:
    - user_type: Filter by user type (individual, organization, academic, nonprofit)
    
    Public endpoint - shows all available plans.
    """
    all_plans = get_all_plans()
    
    # Convert to list format
    plans_list = []
    for plan_type, plan_data in all_plans.items():
        plan_info = {
            "plan_type": plan_type.value,
            "name": plan_data["name"],
            "description": plan_data["description"],
            "price_monthly": plan_data["price_monthly"],
            "price_yearly": plan_data["price_yearly"],
            "features": plan_data["features"]
        }
        
        # Mark recommended plan
        if user_type:
            recommended_plan = get_recommended_plan(user_type)
            plan_info["recommended"] = (plan_type == recommended_plan)
        
        plans_list.append(plan_info)
    
    return {
        "plans": plans_list,
        "total": len(plans_list)
    }


@router.get("/plans/{plan_type}")
async def get_plan_details(
    plan_type: PlanType,
    seats: Optional[int] = 1,
    billing_interval: BillingInterval = BillingInterval.MONTHLY
):
    """
    Get detailed information about a specific plan.
    
    For organization plans, provide seats parameter to calculate pricing.
    """
    if plan_type not in PRICING:
        raise HTTPException(status_code=404, detail=f"Plan {plan_type} not found")
    
    plan_data = PRICING[plan_type]
    
    # Calculate price
    if plan_type == PlanType.ORGANIZATION:
        price = calculate_organization_price(seats, billing_interval)
        price_per_seat = price / seats
    else:
        price = get_plan_price(plan_type, billing_interval)
        price_per_seat = None
    
    return {
        "plan_type": plan_type.value,
        "name": plan_data["name"],
        "description": plan_data["description"],
        "price": price,
        "price_per_seat": price_per_seat,
        "billing_interval": billing_interval.value,
        "currency": "USD",
        "features": plan_data["features"],
        "savings_yearly": None if billing_interval == BillingInterval.MONTHLY else f"{(price / 10 * 2):.2f}"  # 2 months free
    }


@router.get("/me")
async def get_my_subscription(current_user: Dict = Depends(get_current_user)):
    """
    Get current user's subscription information.
    
    ⚠️ REQUIRES AUTHENTICATION
    """
    user_id = current_user["user_id"]
    subscription = get_user_subscription(user_id)
    
    if not subscription:
        # User has no subscription, return free plan info
        return {
            "subscribed": False,
            "plan_type": PlanType.FREE.value,
            "plan_name": "Free Trial",
            "status": "active",
            "features": get_plan_features(PlanType.FREE),
            "message": "You're on the free trial. Upgrade for unlimited access!"
        }
    
    return {
        "subscribed": True,
        **subscription
    }


@router.post("/me")
async def create_my_subscription(
    subscription_data: SubscriptionCreate,
    current_user: Dict = Depends(get_current_user)
):
    """
    Create or upgrade subscription for current user.
    
    ⚠️ REQUIRES AUTHENTICATION
    
    Note: In production, this would integrate with Stripe/payment processor.
    """
    user_id = current_user["user_id"]
    
    # Check if user already has a subscription
    existing_subscription = get_user_subscription(user_id)
    if existing_subscription:
        raise HTTPException(
            status_code=400,
            detail="You already have an active subscription. Use PUT /subscriptions/me to update it."
        )
    
    # Validate plan
    if subscription_data.plan_type not in PRICING:
        raise HTTPException(status_code=400, detail=f"Invalid plan type: {subscription_data.plan_type}")
    
    # Create subscription
    subscription = create_subscription(user_id, subscription_data)
    
    return {
        "message": "Subscription created successfully",
        "subscription": subscription,
        "trial_days": 14,
        "next_steps": [
            "Complete payment setup before trial ends",
            "Explore all features during your trial",
            "Contact support if you need help"
        ]
    }


@router.put("/me")
async def update_my_subscription(
    subscription_data: SubscriptionUpdate,
    current_user: Dict = Depends(get_current_user)
):
    """
    Update current user's subscription.
    
    ⚠️ REQUIRES AUTHENTICATION
    
    Allows changing plan, billing interval, or seats.
    """
    user_id = current_user["user_id"]
    subscription = get_user_subscription(user_id)
    
    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="No active subscription found. Use POST /subscriptions/me to create one."
        )
    
    # Update fields
    if subscription_data.plan_type:
        old_plan = subscription["plan_type"]
        subscription["plan_type"] = subscription_data.plan_type.value
        subscription["plan_name"] = PRICING[subscription_data.plan_type]["name"]
        subscription["features"] = get_plan_features(subscription_data.plan_type)
        
        # Recalculate amount
        if subscription_data.plan_type == PlanType.ORGANIZATION:
            subscription["amount"] = calculate_organization_price(
                subscription.get("seats", 1),
                BillingInterval(subscription["billing_interval"])
            )
        else:
            subscription["amount"] = get_plan_price(
                subscription_data.plan_type,
                BillingInterval(subscription["billing_interval"])
            ) or 0
    
    if subscription_data.billing_interval:
        subscription["billing_interval"] = subscription_data.billing_interval.value
        
        # Recalculate amount based on new interval
        plan_type = PlanType(subscription["plan_type"])
        if plan_type == PlanType.ORGANIZATION:
            subscription["amount"] = calculate_organization_price(
                subscription.get("seats", 1),
                subscription_data.billing_interval
            )
        else:
            subscription["amount"] = get_plan_price(plan_type, subscription_data.billing_interval) or 0
    
    if subscription_data.seats:
        subscription["seats"] = subscription_data.seats
        
        # Recalculate amount for organization plans
        plan_type = PlanType(subscription["plan_type"])
        if plan_type == PlanType.ORGANIZATION:
            subscription["amount"] = calculate_organization_price(
                subscription_data.seats,
                BillingInterval(subscription["billing_interval"])
            )
    
    if subscription_data.auto_renew is not None:
        subscription["auto_renew"] = subscription_data.auto_renew
    
    subscription["updated_at"] = datetime.utcnow().isoformat()
    user_subscriptions[user_id] = subscription
    
    return {
        "message": "Subscription updated successfully",
        "subscription": subscription
    }


@router.delete("/me")
async def cancel_my_subscription(current_user: Dict = Depends(get_current_user)):
    """
    Cancel current user's subscription.
    
    ⚠️ REQUIRES AUTHENTICATION
    
    Subscription remains active until end of current period.
    """
    user_id = current_user["user_id"]
    subscription = get_user_subscription(user_id)
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    # Mark as canceled
    subscription["status"] = SubscriptionStatus.CANCELED.value
    subscription["auto_renew"] = False
    subscription["canceled_at"] = datetime.utcnow().isoformat()
    subscription["updated_at"] = datetime.utcnow().isoformat()
    
    user_subscriptions[user_id] = subscription
    
    return {
        "message": "Subscription canceled successfully",
        "access_until": subscription["current_period_end"],
        "reactivate_url": "/subscriptions/me/reactivate"
    }


@router.post("/me/reactivate")
async def reactivate_my_subscription(current_user: Dict = Depends(get_current_user)):
    """
    Reactivate a canceled subscription.
    
    ⚠️ REQUIRES AUTHENTICATION
    
    Only works if subscription hasn't expired yet.
    """
    user_id = current_user["user_id"]
    subscription = get_user_subscription(user_id)
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")
    
    if subscription["status"] != SubscriptionStatus.CANCELED.value:
        raise HTTPException(status_code=400, detail="Subscription is not canceled")
    
    # Check if expired
    period_end = datetime.fromisoformat(subscription["current_period_end"])
    if datetime.utcnow() > period_end:
        raise HTTPException(
            status_code=400,
            detail="Subscription has expired. Please create a new subscription."
        )
    
    # Reactivate
    subscription["status"] = SubscriptionStatus.ACTIVE.value
    subscription["auto_renew"] = True
    subscription["canceled_at"] = None
    subscription["updated_at"] = datetime.utcnow().isoformat()
    
    user_subscriptions[user_id] = subscription
    
    return {
        "message": "Subscription reactivated successfully",
        "subscription": subscription
    }


@router.get("/features/{feature_name}")
async def check_feature(
    feature_name: str,
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """
    Check if current user has access to a specific feature.
    
    Public endpoint - returns feature access based on subscription.
    """
    if not current_user:
        # Anonymous user - free plan
        has_access = check_feature_access(PlanType.FREE, feature_name)
        return {
            "feature": feature_name,
            "has_access": has_access,
            "plan": PlanType.FREE.value,
            "message": "Login to access premium features" if not has_access else None
        }
    
    user_id = current_user["user_id"]
    subscription = get_user_subscription(user_id)
    
    if not subscription:
        # User logged in but no subscription - free plan
        has_access = check_feature_access(PlanType.FREE, feature_name)
        plan = PlanType.FREE
    else:
        plan = PlanType(subscription["plan_type"])
        has_access = check_feature_access(plan, feature_name)
    
    return {
        "feature": feature_name,
        "has_access": has_access,
        "plan": plan.value,
        "message": "Upgrade your plan to access this feature" if not has_access else None
    }


@router.get("/calculator", response_class=HTMLResponse)
async def pricing_calculator(request: Request):
    """
    Interactive pricing calculator page.
    
    Public endpoint - displays HTML calculator for estimating costs.
    """
    return templates.TemplateResponse("pricing_calculator.html", {"request": request})


@router.get("/calculate-price")
async def calculate_price(
    plan_type: PlanType,
    billing_interval: BillingInterval = BillingInterval.MONTHLY,
    seats: int = 1
):
    """
    Calculate price for a given plan configuration.
    
    Public endpoint - useful for pricing calculators.
    """
    if plan_type not in PRICING:
        raise HTTPException(status_code=404, detail=f"Plan {plan_type} not found")
    
    # Calculate price
    if plan_type == PlanType.ORGANIZATION:
        total_price = calculate_organization_price(seats, billing_interval)
        price_per_seat = total_price / seats
        
        # Calculate savings
        monthly_price_per_seat = 40 if seats <= 10 else 32 if seats <= 50 else 28 if seats <= 100 else 24
        monthly_total = seats * monthly_price_per_seat
        
        if billing_interval == BillingInterval.YEARLY:
            savings = monthly_total * 2  # 2 months free
        else:
            savings = 0
    else:
        price = get_plan_price(plan_type, billing_interval)
        if price is None:
            return {
                "plan_type": plan_type.value,
                "billing_interval": billing_interval.value,
                "message": "Custom pricing - contact sales",
                "contact_url": "/contact/sales"
            }
        
        total_price = price
        price_per_seat = price
        
        # Calculate savings for yearly
        if billing_interval == BillingInterval.YEARLY:
            monthly_price = get_plan_price(plan_type, BillingInterval.MONTHLY) or 0
            savings = monthly_price * 2  # 2 months free
        else:
            savings = 0
    
    return {
        "plan_type": plan_type.value,
        "billing_interval": billing_interval.value,
        "seats": seats,
        "price_per_seat": round(price_per_seat, 2),
        "total_price": round(total_price, 2),
        "currency": "USD",
        "savings": round(savings, 2) if savings > 0 else None,
        "yearly_discount": "2 months free" if billing_interval == BillingInterval.YEARLY and savings > 0 else None
    }
