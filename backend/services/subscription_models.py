"""
Subscription & Pricing Models
==============================

Database models for subscription plans, user subscriptions, and billing.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum

try:
    from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import relationship
    SQLALCHEMY_AVAILABLE = True
    Base = declarative_base()
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    Base = None


class PlanType(str, Enum):
    """Subscription plan types."""
    FREE = "free"
    INDIVIDUAL_STARTER = "individual_starter"
    INDIVIDUAL_PROFESSIONAL = "individual_professional"
    INDIVIDUAL_PROFESSIONAL_PLUS = "individual_professional_plus"
    ORGANIZATION = "organization"
    ACADEMIC_FACULTY = "academic_faculty"
    ACADEMIC_RESIDENT = "academic_resident"
    ACADEMIC_STUDENT = "academic_student"
    NONPROFIT_STANDARD = "nonprofit_standard"
    NONPROFIT_EXPANDED = "nonprofit_expanded"
    ENTERPRISE = "enterprise"


class BillingInterval(str, Enum):
    """Billing cycle intervals."""
    MONTHLY = "monthly"
    YEARLY = "yearly"
    ONE_TIME = "one_time"


class SubscriptionStatus(str, Enum):
    """Subscription status."""
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    EXPIRED = "expired"


# Pricing configuration
PRICING = {
    PlanType.FREE: {
        "name": "Free Trial",
        "description": "10 diagnostic searches per week",
        "price_monthly": 0,
        "price_yearly": 0,
        "features": {
            "diagnostic_searches": 10,  # per week
            "diagnostic_searches_unlimited": False,
            "save_favorites": False,
            "search_history": False,
            "custom_lists": False,
            "export_pdf": False,
            "export_fhir": False,
            "api_access": False,
            "priority_support": False,
            "modules": [],
        }
    },
    PlanType.INDIVIDUAL_STARTER: {
        "name": "Individual Starter",
        "description": "Perfect for solo clinicians getting started",
        "price_monthly": 29,
        "price_yearly": 290,  # 2 months free
        "features": {
            "diagnostic_searches": "unlimited",
            "diagnostic_searches_unlimited": True,
            "save_favorites": True,
            "search_history": True,
            "custom_lists": True,
            "export_pdf": True,
            "export_fhir": False,
            "api_access": False,
            "priority_support": False,
            "modules": ["cardiology"],  # 1 module
            "max_modules": 1,
        }
    },
    PlanType.INDIVIDUAL_PROFESSIONAL: {
        "name": "Individual Professional",
        "description": "All clinical modules included",
        "price_monthly": 49,
        "price_yearly": 490,  # 2 months free
        "features": {
            "diagnostic_searches": "unlimited",
            "diagnostic_searches_unlimited": True,
            "save_favorites": True,
            "search_history": True,
            "custom_lists": True,
            "export_pdf": True,
            "export_fhir": True,
            "api_access": False,
            "priority_support": False,
            "modules": "all",
            "max_modules": "unlimited",
        }
    },
    PlanType.INDIVIDUAL_PROFESSIONAL_PLUS: {
        "name": "Individual Professional+",
        "description": "Everything + priority support",
        "price_monthly": 69,
        "price_yearly": 690,  # 2 months free
        "features": {
            "diagnostic_searches": "unlimited",
            "diagnostic_searches_unlimited": True,
            "save_favorites": True,
            "search_history": True,
            "custom_lists": True,
            "export_pdf": True,
            "export_fhir": True,
            "api_access": True,
            "priority_support": True,
            "modules": "all",
            "max_modules": "unlimited",
        }
    },
    PlanType.ORGANIZATION: {
        "name": "Organization",
        "description": "For clinics and health systems",
        "price_monthly": 40,  # per clinician, reduces with volume
        "price_yearly": 400,  # per clinician
        "features": {
            "diagnostic_searches": "unlimited",
            "diagnostic_searches_unlimited": True,
            "save_favorites": True,
            "search_history": True,
            "custom_lists": True,
            "export_pdf": True,
            "export_fhir": True,
            "api_access": True,
            "priority_support": True,
            "modules": "all",
            "max_modules": "unlimited",
            "admin_dashboard": True,
            "ehr_integration": True,
            "onboarding": True,
            "training": True,
            "volume_pricing": True,  # $24-$40 based on seats
        }
    },
    PlanType.ACADEMIC_FACULTY: {
        "name": "Academic Faculty",
        "description": "For university faculty and teaching physicians",
        "price_monthly": 25,
        "price_yearly": 250,
        "features": {
            "diagnostic_searches": "unlimited",
            "diagnostic_searches_unlimited": True,
            "save_favorites": True,
            "search_history": True,
            "custom_lists": True,
            "export_pdf": True,
            "export_fhir": True,
            "api_access": False,
            "priority_support": True,
            "modules": "all",
            "max_modules": "unlimited",
            "teaching_mode": True,
            "simulated_cases": True,
            "research_license": True,
        }
    },
    PlanType.ACADEMIC_RESIDENT: {
        "name": "Academic Resident",
        "description": "Discounted rate for medical residents",
        "price_monthly": 12,
        "price_yearly": 120,
        "features": {
            "diagnostic_searches": "unlimited",
            "diagnostic_searches_unlimited": True,
            "save_favorites": True,
            "search_history": True,
            "custom_lists": True,
            "export_pdf": True,
            "export_fhir": False,
            "api_access": False,
            "priority_support": False,
            "modules": "all",
            "max_modules": "unlimited",
            "teaching_mode": True,
            "simulated_cases": True,
        }
    },
    PlanType.ACADEMIC_STUDENT: {
        "name": "Academic Student",
        "description": "Free for up to 500 medical students",
        "price_monthly": 0,
        "price_yearly": 0,
        "features": {
            "diagnostic_searches": "unlimited",
            "diagnostic_searches_unlimited": True,
            "save_favorites": True,
            "search_history": True,
            "custom_lists": True,
            "export_pdf": False,
            "export_fhir": False,
            "api_access": False,
            "priority_support": False,
            "modules": "all",
            "max_modules": "unlimited",
            "teaching_mode": True,
            "simulated_cases": True,
            "requires_verification": True,  # Must verify student status
        }
    },
    PlanType.NONPROFIT_STANDARD: {
        "name": "Non-Profit Standard",
        "description": "For FQHCs and community health centers",
        "price_monthly": 18,
        "price_yearly": 180,
        "features": {
            "diagnostic_searches": "unlimited",
            "diagnostic_searches_unlimited": True,
            "save_favorites": True,
            "search_history": True,
            "custom_lists": True,
            "export_pdf": True,
            "export_fhir": True,
            "api_access": False,
            "priority_support": True,
            "modules": "all",
            "max_modules": "unlimited",
            "requires_verification": True,  # Must verify 501(c)(3) status
        }
    },
    PlanType.NONPROFIT_EXPANDED: {
        "name": "Non-Profit Expanded",
        "description": "Expanded access for safety-net organizations",
        "price_monthly": 10,
        "price_yearly": 100,
        "features": {
            "diagnostic_searches": "unlimited",
            "diagnostic_searches_unlimited": True,
            "save_favorites": True,
            "search_history": True,
            "custom_lists": True,
            "export_pdf": True,
            "export_fhir": True,
            "api_access": False,
            "priority_support": False,
            "modules": "all",
            "max_modules": "unlimited",
            "requires_verification": True,  # Must verify eligibility
        }
    },
    PlanType.ENTERPRISE: {
        "name": "Enterprise",
        "description": "Custom solutions for large health systems",
        "price_monthly": None,  # Custom pricing
        "price_yearly": None,   # $75k-$250k range
        "features": {
            "diagnostic_searches": "unlimited",
            "diagnostic_searches_unlimited": True,
            "save_favorites": True,
            "search_history": True,
            "custom_lists": True,
            "export_pdf": True,
            "export_fhir": True,
            "api_access": True,
            "priority_support": True,
            "modules": "all",
            "max_modules": "unlimited",
            "admin_dashboard": True,
            "ehr_integration": True,
            "custom_sla": True,
            "white_label": True,
            "dedicated_support": True,
            "custom_training": True,
            "unlimited_seats": True,
        }
    },
}


if SQLALCHEMY_AVAILABLE:
    class SubscriptionPlan(Base):
        """Subscription plan configuration (stored in database)."""
        __tablename__ = "subscription_plans"
        
        id = Column(Integer, primary_key=True)
        plan_type = Column(SQLEnum(PlanType), unique=True, nullable=False)
        name = Column(String(100), nullable=False)
        description = Column(String(500))
        price_monthly = Column(Float)
        price_yearly = Column(Float)
        features = Column(JSON)
        active = Column(Boolean, default=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Relationships
        subscriptions = relationship("UserSubscription", back_populates="plan")
    
    
    class UserSubscription(Base):
        """User subscription instance."""
        __tablename__ = "user_subscriptions"
        
        id = Column(Integer, primary_key=True)
        user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False)
        plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
        
        status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.TRIAL)
        billing_interval = Column(SQLEnum(BillingInterval), default=BillingInterval.MONTHLY)
        
        # Dates
        start_date = Column(DateTime, default=datetime.utcnow)
        current_period_start = Column(DateTime)
        current_period_end = Column(DateTime)
        trial_end = Column(DateTime)
        canceled_at = Column(DateTime)
        ended_at = Column(DateTime)
        
        # Pricing
        amount = Column(Float)  # Actual amount charged (may differ due to discounts)
        currency = Column(String(3), default="USD")
        
        # Payment
        stripe_subscription_id = Column(String(100))
        stripe_customer_id = Column(String(100))
        payment_method = Column(String(50))
        
        # Organization details (for org/enterprise plans)
        organization_name = Column(String(200))
        seats = Column(Integer, default=1)  # Number of users/clinicians
        
        # Metadata
        plan_metadata = Column(JSON)  # Additional plan-specific data
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Relationships
        plan = relationship("SubscriptionPlan", back_populates="subscriptions")


def get_plan_price(plan_type: PlanType, billing_interval: BillingInterval = BillingInterval.MONTHLY) -> Optional[float]:
    """Get the price for a specific plan and billing interval."""
    plan = PRICING.get(plan_type)
    if not plan:
        return None
    
    if billing_interval == BillingInterval.MONTHLY:
        return plan.get("price_monthly")
    elif billing_interval == BillingInterval.YEARLY:
        return plan.get("price_yearly")
    
    return None


def get_plan_features(plan_type: PlanType) -> Dict[str, Any]:
    """Get features for a specific plan."""
    plan = PRICING.get(plan_type)
    if not plan:
        return {}
    
    return plan.get("features", {})


def check_feature_access(plan_type: PlanType, feature_name: str) -> bool:
    """Check if a plan has access to a specific feature."""
    features = get_plan_features(plan_type)
    return features.get(feature_name, False)


def get_all_plans() -> Dict[str, Dict[str, Any]]:
    """Get all available subscription plans."""
    return PRICING


def calculate_organization_price(seats: int, billing_interval: BillingInterval = BillingInterval.MONTHLY) -> float:
    """
    Calculate organization pricing with volume discounts.
    
    Pricing tiers:
    - 1-10 users: $40/user/month
    - 11-50 users: $32/user/month
    - 51-100 users: $28/user/month
    - 100+ users: $24/user/month
    """
    if seats <= 10:
        price_per_seat = 40
    elif seats <= 50:
        price_per_seat = 32
    elif seats <= 100:
        price_per_seat = 28
    else:
        price_per_seat = 24
    
    monthly_total = seats * price_per_seat
    
    if billing_interval == BillingInterval.YEARLY:
        # 2 months free on yearly billing
        return monthly_total * 10
    
    return monthly_total


def get_recommended_plan(user_type: str, organization_size: Optional[int] = None) -> PlanType:
    """
    Recommend a plan based on user type and organization size.
    
    Args:
        user_type: "individual", "organization", "academic", "nonprofit"
        organization_size: Number of users (for organization plans)
    
    Returns:
        Recommended PlanType
    """
    if user_type == "individual":
        return PlanType.INDIVIDUAL_PROFESSIONAL
    elif user_type == "organization":
        return PlanType.ORGANIZATION
    elif user_type == "academic":
        return PlanType.ACADEMIC_FACULTY
    elif user_type == "nonprofit":
        return PlanType.NONPROFIT_STANDARD
    else:
        return PlanType.FREE
