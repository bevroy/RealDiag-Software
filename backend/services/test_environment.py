"""
Test Environment Middleware
============================

Middleware to enable free access for all users in test environment.
This allows real-world testing without subscription restrictions.

Usage:
    Set ENVIRONMENT=test in .env file to activate test mode.
"""

import os
from typing import Optional
from fastapi import Request
from backend.services.subscription_models import PlanType


# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_TEST_ENVIRONMENT = ENVIRONMENT == "test"
FREE_ACCESS_TESTING = os.getenv("FREE_ACCESS_TESTING", "false").lower() == "true"
BYPASS_SUBSCRIPTION_CHECKS = os.getenv("BYPASS_SUBSCRIPTION_CHECKS", "false").lower() == "true"


def is_test_mode() -> bool:
    """Check if application is running in test mode."""
    return IS_TEST_ENVIRONMENT or FREE_ACCESS_TESTING


def should_bypass_subscription() -> bool:
    """Check if subscription checks should be bypassed."""
    return is_test_mode() or BYPASS_SUBSCRIPTION_CHECKS


def get_test_mode_plan() -> PlanType:
    """
    Get the plan type to use for test mode users.
    In test mode, all users get enterprise-level access.
    """
    return PlanType.ENTERPRISE


class TestEnvironmentMiddleware:
    """
    Middleware to enable test mode features.
    
    In test mode:
    - All authenticated users get enterprise-level access
    - Unauthenticated users get professional-level access
    - No subscription checks are enforced
    - No payment required
    - All features unlocked
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Add test mode flag to request state
            if "state" not in scope:
                scope["state"] = {}
            scope["state"]["test_mode"] = is_test_mode()
            scope["state"]["bypass_subscription"] = should_bypass_subscription()
        
        await self.app(scope, receive, send)


def get_effective_plan(user: Optional[dict], actual_plan: PlanType) -> PlanType:
    """
    Get the effective plan for a user, considering test mode.
    
    Args:
        user: User object from authentication
        actual_plan: The user's actual subscription plan
    
    Returns:
        PlanType - In test mode, returns enterprise plan; otherwise returns actual plan
    """
    if should_bypass_subscription():
        # In test mode, everyone gets enterprise access
        return PlanType.ENTERPRISE
    
    return actual_plan


def check_feature_access_test_aware(
    plan: PlanType,
    feature_name: str,
    user: Optional[dict] = None
) -> bool:
    """
    Check feature access with test mode awareness.
    
    In test mode, always returns True for any feature.
    
    Args:
        plan: User's subscription plan
        feature_name: Feature to check access for
        user: Optional user object
    
    Returns:
        bool - True if user has access to feature
    """
    # In test mode, grant access to everything
    if should_bypass_subscription():
        return True
    
    # Import the actual check function to avoid circular imports
    from backend.services.subscription_models import check_feature_access
    return check_feature_access(plan, feature_name)


def get_usage_limit_test_aware(
    feature_name: str,
    plan: PlanType,
    user: Optional[dict] = None
) -> int:
    """
    Get usage limit for a feature with test mode awareness.
    
    In test mode, returns unlimited (999999) for all features.
    
    Args:
        feature_name: Feature to check limit for
        plan: User's subscription plan
        user: Optional user object
    
    Returns:
        int - Usage limit (999999 in test mode means unlimited)
    """
    # In test mode, grant unlimited usage
    if should_bypass_subscription():
        return 999999
    
    # Import actual function
    from backend.services.subscription_models import get_plan_features
    features = get_plan_features(plan)
    return features.get(feature_name, 0)


def inject_test_metadata(response_data: dict) -> dict:
    """
    Inject test mode metadata into API responses.
    
    Args:
        response_data: Original response data
    
    Returns:
        dict - Response data with test mode metadata
    """
    if is_test_mode():
        response_data["_test_mode"] = True
        response_data["_test_access"] = "unlimited"
        response_data["_environment"] = "test"
    
    return response_data


# Decorator for endpoints that should be test-mode aware
def test_mode_decorator(func):
    """
    Decorator to make an endpoint test-mode aware.
    Automatically grants enterprise access in test mode.
    """
    from functools import wraps
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # If in test mode, inject enterprise plan
        if "user" in kwargs and should_bypass_subscription():
            user = kwargs["user"]
            if user:
                user["_test_mode_override"] = True
                user["_effective_plan"] = PlanType.ENTERPRISE.value
        
        # Call original function
        result = await func(*args, **kwargs)
        
        # Inject test metadata if result is a dict
        if isinstance(result, dict) and is_test_mode():
            result = inject_test_metadata(result)
        
        return result
    
    return wrapper


def log_test_mode_activity(action: str, user_id: Optional[str] = None, details: Optional[dict] = None):
    """
    Log activity in test mode for analysis.
    
    Args:
        action: Action being performed
        user_id: Optional user ID
        details: Optional additional details
    """
    if is_test_mode():
        import logging
        logger = logging.getLogger("test_mode")
        log_data = {
            "action": action,
            "user_id": user_id,
            "environment": "test",
            "timestamp": None,  # Will be added by logger
        }
        if details:
            log_data["details"] = details
        
        logger.info(f"[TEST MODE] {action}", extra=log_data)


# Export test mode status for other modules
__all__ = [
    "is_test_mode",
    "should_bypass_subscription",
    "get_test_mode_plan",
    "get_effective_plan",
    "check_feature_access_test_aware",
    "get_usage_limit_test_aware",
    "inject_test_metadata",
    "test_mode_decorator",
    "log_test_mode_activity",
    "TestEnvironmentMiddleware",
    "IS_TEST_ENVIRONMENT",
    "FREE_ACCESS_TESTING",
]
