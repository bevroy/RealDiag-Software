"""
Subscription Feature Gating
============================

Decorators and utilities for enforcing subscription-based feature access.
"""

from functools import wraps
from fastapi import HTTPException, Request, Depends
from typing import Optional, Callable, Any
from backend.services.subscription_models import PlanType, check_feature_access, get_plan_features


def get_user_plan(user: Optional[dict], subscriptions_store: dict) -> PlanType:
    """
    Get the plan type for a user.
    
    Args:
        user: User object from authentication
        subscriptions_store: Dictionary of user subscriptions
    
    Returns:
        PlanType enum value
    """
    if not user:
        return PlanType.FREE
    
    subscription = subscriptions_store.get(user["user_id"])
    if not subscription:
        return PlanType.FREE
    
    return PlanType(subscription["plan_type"])


def require_feature(feature_name: str, user_subscriptions: dict):
    """
    Decorator to require a specific feature access.
    
    Usage:
        @router.get("/premium-endpoint")
        @require_feature("api_access", user_subscriptions)
        async def premium_endpoint(user: dict = Depends(get_current_user)):
            ...
    
    Args:
        feature_name: Name of the feature to check (e.g., "api_access", "bulk_export")
        user_subscriptions: Dictionary storing user subscriptions
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from kwargs
            user = kwargs.get("current_user") or kwargs.get("user")
            
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required to access this feature"
                )
            
            # Get user's plan
            plan = get_user_plan(user, user_subscriptions)
            
            # Check feature access
            has_access = check_feature_access(plan, feature_name)
            
            if not has_access:
                features = get_plan_features(plan)
                current_limit = features.get(feature_name, "Not available")
                
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "Feature not available in your plan",
                        "feature": feature_name,
                        "current_plan": plan.value,
                        "current_limit": current_limit,
                        "upgrade_required": True,
                        "message": f"Upgrade your subscription to access {feature_name}"
                    }
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_plan(minimum_plan: PlanType, user_subscriptions: dict):
    """
    Decorator to require a minimum subscription plan level.
    
    Usage:
        @router.get("/professional-feature")
        @require_plan(PlanType.INDIVIDUAL_PROFESSIONAL, user_subscriptions)
        async def pro_feature(user: dict = Depends(get_current_user)):
            ...
    
    Args:
        minimum_plan: Minimum plan required
        user_subscriptions: Dictionary storing user subscriptions
    
    Returns:
        Decorator function
    """
    # Define plan hierarchy (higher number = more features)
    plan_hierarchy = {
        PlanType.FREE: 0,
        PlanType.ACADEMIC_STUDENT: 1,
        PlanType.INDIVIDUAL_STARTER: 2,
        PlanType.NONPROFIT_EXPANDED: 3,
        PlanType.ACADEMIC_RESIDENT: 4,
        PlanType.NONPROFIT_STANDARD: 5,
        PlanType.ACADEMIC_FACULTY: 6,
        PlanType.INDIVIDUAL_PROFESSIONAL: 7,
        PlanType.INDIVIDUAL_PROFESSIONAL_PLUS: 8,
        PlanType.ORGANIZATION: 9,
        PlanType.ENTERPRISE: 10
    }
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from kwargs
            user = kwargs.get("current_user") or kwargs.get("user")
            
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required to access this feature"
                )
            
            # Get user's plan
            user_plan = get_user_plan(user, user_subscriptions)
            
            # Compare plan levels
            user_level = plan_hierarchy.get(user_plan, 0)
            required_level = plan_hierarchy.get(minimum_plan, 0)
            
            if user_level < required_level:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "Insufficient subscription level",
                        "current_plan": user_plan.value,
                        "required_plan": minimum_plan.value,
                        "upgrade_required": True,
                        "message": f"This feature requires {minimum_plan.value} or higher"
                    }
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def check_usage_limit(feature_name: str, current_usage: int, user_subscriptions: dict):
    """
    Check if user has exceeded their plan's usage limit for a feature.
    
    Args:
        feature_name: Name of the feature (e.g., "searches_per_month", "exports_per_month")
        current_usage: Current usage count
        user_subscriptions: Dictionary storing user subscriptions
    
    Returns:
        Tuple of (allowed: bool, limit: int, remaining: int)
    
    Usage:
        allowed, limit, remaining = check_usage_limit("searches_per_month", user_searches, user_subscriptions)
        if not allowed:
            raise HTTPException(status_code=429, detail=f"Monthly limit exceeded ({limit} searches)")
    """
    def get_limit(user: Optional[dict]) -> int:
        """Extract limit value from user's plan."""
        plan = get_user_plan(user, user_subscriptions)
        features = get_plan_features(plan)
        
        limit_value = features.get(feature_name, 0)
        
        # Handle "Unlimited" or boolean values
        if isinstance(limit_value, str):
            if limit_value.lower() == "unlimited":
                return float('inf')
            # Try to extract number from string like "10 per month"
            try:
                return int(''.join(filter(str.isdigit, limit_value)))
            except ValueError:
                return 0
        elif isinstance(limit_value, bool):
            return float('inf') if limit_value else 0
        elif isinstance(limit_value, int):
            return limit_value
        else:
            return 0
    
    return get_limit, lambda user: current_usage


class SubscriptionGate:
    """
    Context manager for subscription-based feature gating.
    
    Usage:
        async with SubscriptionGate(user, user_subscriptions) as gate:
            if not gate.has_feature("api_access"):
                raise HTTPException(403, "API access not available")
            
            if not gate.within_limit("searches_per_month", current_searches):
                raise HTTPException(429, "Search limit exceeded")
    """
    
    def __init__(self, user: Optional[dict], user_subscriptions: dict):
        self.user = user
        self.user_subscriptions = user_subscriptions
        self.plan = get_user_plan(user, user_subscriptions)
        self.features = get_plan_features(self.plan)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def has_feature(self, feature_name: str) -> bool:
        """Check if user has access to a feature."""
        return check_feature_access(self.plan, feature_name)
    
    def get_feature_value(self, feature_name: str) -> Any:
        """Get the value of a feature for user's plan."""
        return self.features.get(feature_name)
    
    def within_limit(self, feature_name: str, current_usage: int) -> bool:
        """Check if usage is within plan limits."""
        limit_value = self.features.get(feature_name, 0)
        
        # Handle "Unlimited"
        if isinstance(limit_value, str) and limit_value.lower() == "unlimited":
            return True
        
        # Handle boolean
        if isinstance(limit_value, bool):
            return limit_value
        
        # Handle numeric limits
        try:
            if isinstance(limit_value, str):
                limit = int(''.join(filter(str.isdigit, limit_value)))
            else:
                limit = int(limit_value)
            
            return current_usage < limit
        except (ValueError, TypeError):
            return False
    
    def get_remaining(self, feature_name: str, current_usage: int) -> Optional[int]:
        """Get remaining usage for a feature."""
        limit_value = self.features.get(feature_name, 0)
        
        # Handle "Unlimited"
        if isinstance(limit_value, str) and limit_value.lower() == "unlimited":
            return None
        
        # Handle numeric limits
        try:
            if isinstance(limit_value, str):
                limit = int(''.join(filter(str.isdigit, limit_value)))
            else:
                limit = int(limit_value)
            
            remaining = limit - current_usage
            return max(0, remaining)
        except (ValueError, TypeError):
            return 0
    
    def require_feature(self, feature_name: str):
        """
        Raise exception if feature not available.
        
        Usage:
            gate.require_feature("api_access")
        """
        if not self.has_feature(feature_name):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Feature not available in your plan",
                    "feature": feature_name,
                    "current_plan": self.plan.value,
                    "upgrade_required": True
                }
            )
    
    def require_limit(self, feature_name: str, current_usage: int):
        """
        Raise exception if usage limit exceeded.
        
        Usage:
            gate.require_limit("searches_per_month", user_searches)
        """
        if not self.within_limit(feature_name, current_usage):
            limit_value = self.features.get(feature_name, 0)
            
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Usage limit exceeded",
                    "feature": feature_name,
                    "limit": str(limit_value),
                    "current_usage": current_usage,
                    "upgrade_required": True,
                    "message": f"You've reached your plan's limit for {feature_name}"
                }
            )


# ========== MIDDLEWARE HELPERS ==========

async def add_subscription_context(request: Request, user: Optional[dict], user_subscriptions: dict):
    """
    Add subscription context to request state.
    
    Usage in middleware:
        @app.middleware("http")
        async def subscription_middleware(request: Request, call_next):
            user = await get_optional_user_from_request(request)
            await add_subscription_context(request, user, user_subscriptions)
            response = await call_next(request)
            return response
    """
    request.state.subscription_plan = get_user_plan(user, user_subscriptions)
    request.state.subscription_features = get_plan_features(request.state.subscription_plan)


def get_plan_from_request(request: Request) -> PlanType:
    """Get subscription plan from request state."""
    return getattr(request.state, "subscription_plan", PlanType.FREE)


def get_features_from_request(request: Request) -> dict:
    """Get subscription features from request state."""
    return getattr(request.state, "subscription_features", get_plan_features(PlanType.FREE))
