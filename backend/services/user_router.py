"""
User Accounts & Personalization Router
=======================================

REST API endpoints for user authentication, profiles, favorites, custom lists,
search history, and analytics.
"""

from fastapi import APIRouter, HTTPException, Depends, status, Response, Request
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr
from backend.services.auth_service import (
    UserCreate, UserLogin, UserProfile, UserSettings,
    SearchHistory, FavoriteDiagnosis, CustomList,
    create_user, authenticate_user, create_access_token,
    create_mfa_pending_token,
    get_current_user, get_optional_user,
    get_user_mfa_state,
    add_search_to_history, get_user_search_history,
    add_favorite, get_user_favorites, remove_favorite,
    create_custom_list, get_user_custom_lists,
    add_diagnosis_to_list, remove_diagnosis_from_list,
    get_user_analytics,
    users_db, user_settings_db
)
from backend.services.email_service import (
    is_token_expired, send_welcome_email
)
from backend.services.subscription_router import create_subscription
from backend.services.subscription_models import PlanType, BillingInterval
from backend.services.database import DATABASE_AVAILABLE, get_db_session, User
from datetime import datetime
from backend.services.auth_cookies import (
    cookie_auth,
    create_cookie_response,
    get_token_from_cookie
)
import secrets
import logging

logger = logging.getLogger(__name__)

APPROVED_PROVIDER_DOMAINS = {"realdiag.com", "elionyxhealth.com"}


def _is_approved_provider_email(email: Optional[str]) -> bool:
    if not email:
        return False
    parts = str(email).strip().lower().rsplit("@", 1)
    return len(parts) == 2 and parts[1] in APPROVED_PROVIDER_DOMAINS


def _normalize_ui_role(email: Optional[str], role: Optional[str]) -> str:
    role_value = (role or "user").strip().lower()
    if _is_approved_provider_email(email) and role_value in {"user", "patient", ""}:
        return "provider"
    return role_value or "user"

# Import rate limiter
try:
    from backend.services.security import limiter
    LIMITER_AVAILABLE = True
except ImportError:
    LIMITER_AVAILABLE = False
    limiter = None
    
# Create a no-op limiter when security module unavailable
class NoOpLimiter:
    def limit(self, *args, **kwargs):
        def decorator(f):
            return f
        return decorator

if not LIMITER_AVAILABLE:
    limiter = NoOpLimiter()

router = APIRouter(prefix="/users", tags=["users"])


# Authentication endpoints
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/15minutes")
async def register_user(request: Request, user_data: UserCreate):
    """
    Register a new user account.
    Rate limit: 5 attempts per 15 minutes per IP.
    
    Request body:
    ```json
    {
      "email": "doctor@hospital.com",
      "password": "SecurePass123!",
      "full_name": "Dr. Jane Smith",
      "specialty": "cardiology",
      "institution": "Memorial Hospital"
    }
    ```
    
    Returns tokens in secure HttpOnly cookies instead of response body.
    """
    user = create_user(user_data)
    access_token = create_access_token(user["user_id"], user["email"])
    refresh_token = secrets.token_urlsafe(32)  # Generate refresh token
    
    # Remove sensitive data
    user_safe = {k: v for k, v in user.items() if k != "password_hash"}
    
    # Return response with tokens in HttpOnly cookies
    return create_cookie_response(
        data={
            "message": "Registration successful",
            "user": user_safe
        },
        access_token=access_token,
        refresh_token=refresh_token,
        status_code=status.HTTP_201_CREATED
    )

@router.post("/login")
@limiter.limit("5/15minutes")
async def login_user(request: Request, credentials: UserLogin):
    """
    Authenticate user and get access token.
    Rate limit: 5 attempts per 15 minutes per IP.
    
    Request body:
    ```json
    {
      "email": "doctor@hospital.com",
      "password": "SecurePass123!"
    }
    ```
    
    Returns tokens in secure HttpOnly cookies instead of response body.
    Client should check for 'csrf_token' in response to use in X-CSRF-Token header.
    """
    try:
        user = authenticate_user(credentials.email, credentials.password)
    except Exception as e:
        logger.error(f"Login error for {credentials.email}: {str(e)}")
        raise

    mfa_state = get_user_mfa_state(user["user_id"])
    if mfa_state.get("mfa_enabled"):
        mfa_token = create_mfa_pending_token(user["user_id"], user["email"])
        return {
            "mfa_required": True,
            "mfa_token": mfa_token,
            "message": "MFA verification required. Submit your code to POST /mfa/login-verify."
        }

    access_token = create_access_token(user["user_id"], user["email"])
    refresh_token = secrets.token_urlsafe(32)  # Generate refresh token
    
    # Remove sensitive data
    user_safe = {k: v for k, v in user.items() if k != "password_hash"}

    # Default role compatibility: treat generic "user" as provider-level UI role.
    user_safe["role"] = _normalize_ui_role(user_safe.get("email"), user_safe.get("role"))
    
    # Return response with tokens in HttpOnly cookies
    return create_cookie_response(
        data={
            "message": "Login successful",
            "user": user_safe
        },
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/logout")
async def logout_user(response: Response):
    """
    Logout user by clearing authentication cookies.
    """
    cookie_auth.clear_auth_cookies(response)
    return {"message": "Logout successful"}

@router.post("/verify-email")
async def verify_employee_email(token: str):
    """
    Verify employee email address using token sent via email.
    
    This endpoint verifies @realdiag.org email addresses and automatically
    creates a free employee subscription.
    """
    if not DATABASE_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    with get_db_session() as db:
        # Find user by verification token
        user = db.query(User).filter_by(email_verification_token=token).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
        
        # Check if already verified
        if user.email_verified:
            return {
                "message": "Email already verified",
                "user": user.to_dict()
            }
        
        # Check if token expired
        if is_token_expired(user.email_verification_sent_at):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token has expired. Please request a new one."
            )
        
        # Verify email
        user.email_verified = True
        user.email_verification_token = None
        user.is_verified = True
        db.flush()
        
        # Create employee subscription
        try:
            from backend.services.subscription_router import user_subscriptions
            
            subscription_id = f"sub_{secrets.token_urlsafe(16)}"
            subscription = {
                "subscription_id": subscription_id,
                "user_id": user.user_id,
                "plan_type": PlanType.EMPLOYEE,
                "status": "active",
                "billing_interval": BillingInterval.YEARLY,
                "start_date": datetime.utcnow().isoformat(),
                "current_period_start": datetime.utcnow().isoformat(),
                "current_period_end": None,  # No expiration for employees
                "trial_end": None,
                "auto_renew": True,
                "amount": 0,
                "currency": "USD",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            user_subscriptions[user.user_id] = subscription
            
        except Exception as e:
            # Don't fail verification if subscription creation fails
            pass
        
        # Send welcome email
        send_welcome_email(user.email, user.full_name)
        
        return {
            "message": "Email verified successfully! Your employee account is now active.",
            "user": user.to_dict(),
            "subscription": "employee"
        }

@router.post("/resend-verification")
async def resend_verification_email(email: EmailStr):
    """
    Resend verification email to employee.
    """
    if not DATABASE_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    with get_db_session() as db:
        user = db.query(User).filter_by(email=email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user.is_employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email verification only required for employee accounts"
            )
        
        if user.email_verified:
            return {
                "message": "Email already verified"
            }
        
        # Generate new token
        from backend.services.email_service import generate_verification_token, send_verification_email
        
        new_token = generate_verification_token()
        user.email_verification_token = new_token
        user.email_verification_sent_at = datetime.utcnow()
        
        # Send email
        send_verification_email(user.email, new_token, user.full_name)
        
        return {
            "message": "Verification email sent. Please check your inbox."
        }


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/forgot-password")
@limiter.limit("5/15minutes")
async def forgot_password(request: Request, body: ForgotPasswordRequest):
    """
    Request a password reset link by email.
    Always returns a success message regardless of whether the email exists,
    to prevent account enumeration.
    Rate limit: 5 attempts per 15 minutes per IP.
    """
    generic_response = {
        "message": "If an account exists for that email, a password reset link has been sent."
    }

    if not DATABASE_AVAILABLE:
        # Don't leak that the database is down to the caller
        logger.warning("Password reset requested but database is unavailable")
        return generic_response

    from backend.services.email_service import (
        generate_verification_token,
        send_password_reset_email,
    )

    try:
        with get_db_session() as db:
            user = db.query(User).filter_by(email=body.email).first()
            if user is None or not getattr(user, "is_active", True):
                return generic_response

            token = generate_verification_token()
            user.password_reset_token = token
            user.password_reset_sent_at = datetime.utcnow()
            db.flush()

            send_password_reset_email(user.email, token, user.full_name)
    except Exception as e:
        logger.error(f"forgot_password error for {body.email}: {e}")

    return generic_response


@router.post("/reset-password")
@limiter.limit("10/15minutes")
async def reset_password(request: Request, body: ResetPasswordRequest):
    """
    Reset password using the token sent to the user's email.
    Rate limit: 10 attempts per 15 minutes per IP.
    """
    if not DATABASE_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )

    if not body.new_password or len(body.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters."
        )

    from backend.services.auth_service import hash_password

    with get_db_session() as db:
        user = db.query(User).filter_by(password_reset_token=body.token).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token."
            )

        if is_token_expired(user.password_reset_sent_at):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset link has expired. Please request a new one."
            )

        user.hashed_password = hash_password(body.new_password)
        user.password_reset_token = None
        user.password_reset_sent_at = None
        db.flush()

        # Keep the in-memory mirror in sync so existing code paths see the new hash
        try:
            if user.user_id in users_db:
                users_db[user.user_id]["password_hash"] = user.hashed_password
        except Exception:
            pass

        return {
            "message": "Password updated successfully. You can now sign in with your new password."
        }


@router.get("/me", response_model=UserProfile)
async def get_my_profile(current_user: Dict = Depends(get_current_user)):
    """Get current user's profile."""
    profile = {k: v for k, v in current_user.items() if k != "password_hash"}
    profile["role"] = _normalize_ui_role(profile.get("email"), profile.get("role"))
    
    return profile

@router.put("/me")
async def update_my_profile(
    full_name: Optional[str] = None,
    specialty: Optional[str] = None,
    institution: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Update current user's profile."""
    user_id = current_user["user_id"]
    
    if full_name is not None:
        users_db[user_id]["full_name"] = full_name
    if specialty is not None:
        users_db[user_id]["specialty"] = specialty
    if institution is not None:
        users_db[user_id]["institution"] = institution
    
    return {k: v for k, v in users_db[user_id].items() if k != "password_hash"}


# Settings endpoints
@router.get("/me/settings")
async def get_my_settings(current_user: Dict = Depends(get_current_user)):
    """Get user settings and preferences."""
    user_id = current_user["user_id"]
    return user_settings_db.get(user_id, {})

@router.put("/me/settings")
async def update_my_settings(
    settings: UserSettings,
    current_user: Dict = Depends(get_current_user)
):
    """Update user settings and preferences."""
    user_id = current_user["user_id"]
    settings.user_id = user_id
    user_settings_db[user_id] = settings.dict()
    return user_settings_db[user_id]


# Search history endpoints
class SearchHistoryCreate(BaseModel):
    symptoms: List[str]
    age: Optional[int] = None
    sex: Optional[str] = None
    family: Optional[str] = None
    result_count: int
    top_diagnosis: Optional[str] = None

@router.post("/me/history")
async def add_to_search_history(
    search_data: SearchHistoryCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Add search to user's history."""
    return add_search_to_history(
        user_id=current_user["user_id"],
        symptoms=search_data.symptoms,
        result_count=search_data.result_count,
        age=search_data.age,
        sex=search_data.sex,
        family=search_data.family,
        top_diagnosis=search_data.top_diagnosis
    )

@router.get("/me/history")
async def get_my_search_history(
    limit: int = 50,
    current_user: Dict = Depends(get_current_user)
):
    """Get user's search history."""
    history = get_user_search_history(current_user["user_id"], limit)
    return {
        "history": history,
        "total": len(history)
    }


# Favorites endpoints
class FavoriteCreate(BaseModel):
    rule_id: str
    diagnosis_label: str
    family: str
    notes: Optional[str] = None

@router.post("/me/favorites")
async def add_to_favorites(
    favorite: FavoriteCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Add diagnosis to favorites."""
    return add_favorite(
        user_id=current_user["user_id"],
        rule_id=favorite.rule_id,
        diagnosis_label=favorite.diagnosis_label,
        family=favorite.family,
        notes=favorite.notes
    )

@router.get("/me/favorites")
async def get_my_favorites(current_user: Dict = Depends(get_current_user)):
    """Get user's favorite diagnoses."""
    favorites = get_user_favorites(current_user["user_id"])
    return {
        "favorites": favorites,
        "total": len(favorites)
    }

@router.delete("/me/favorites/{favorite_id}")
async def remove_from_favorites(
    favorite_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Remove diagnosis from favorites."""
    success = remove_favorite(current_user["user_id"], favorite_id)
    if not success:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"message": "Favorite removed successfully"}


# Custom lists endpoints
class CustomListCreate(BaseModel):
    name: str
    description: Optional[str] = None
    specialty: Optional[str] = None
    is_public: bool = False

class DiagnosisToList(BaseModel):
    rule_id: str
    label: str
    family: str
    notes: Optional[str] = None

@router.post("/me/lists")
async def create_my_custom_list(
    list_data: CustomListCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Create a custom differential diagnosis list."""
    return create_custom_list(
        user_id=current_user["user_id"],
        name=list_data.name,
        description=list_data.description,
        specialty=list_data.specialty,
        is_public=list_data.is_public
    )

@router.get("/me/lists")
async def get_my_custom_lists(current_user: Dict = Depends(get_current_user)):
    """Get user's custom differential lists."""
    lists = get_user_custom_lists(current_user["user_id"])
    return {
        "lists": lists,
        "total": len(lists)
    }

@router.post("/me/lists/{list_id}/diagnoses")
async def add_diagnosis_to_my_list(
    list_id: str,
    diagnosis: DiagnosisToList,
    current_user: Dict = Depends(get_current_user)
):
    """Add diagnosis to custom list."""
    return add_diagnosis_to_list(
        user_id=current_user["user_id"],
        list_id=list_id,
        diagnosis=diagnosis.dict()
    )

@router.delete("/me/lists/{list_id}/diagnoses/{rule_id}")
async def remove_diagnosis_from_my_list(
    list_id: str,
    rule_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Remove diagnosis from custom list."""
    return remove_diagnosis_from_list(
        user_id=current_user["user_id"],
        list_id=list_id,
        rule_id=rule_id
    )


# Analytics endpoints
@router.get("/me/analytics")
async def get_my_analytics(current_user: Dict = Depends(get_current_user)):
    """
    Get user analytics and insights.
    
    Returns:
    - Total searches and favorites
    - Most searched symptoms
    - Most viewed specialties
    - Recent activity
    - Usage trends
    """
    return get_user_analytics(current_user["user_id"])


# Public sharing endpoints
@router.get("/lists/public")
async def get_public_lists(specialty: Optional[str] = None):
    """Get publicly shared custom lists."""
    from backend.services.auth_service import custom_lists_db
    
    public_lists = []
    for user_id, lists in custom_lists_db.items():
        for custom_list in lists:
            if custom_list.get("is_public"):
                if specialty is None or custom_list.get("specialty") == specialty:
                    # Remove user_id for privacy
                    list_copy = custom_list.copy()
                    list_copy.pop("user_id", None)
                    public_lists.append(list_copy)
    
    return {
        "lists": public_lists,
        "total": len(public_lists)
    }

@router.get("/lists/public/{list_id}")
async def get_public_list_detail(list_id: str):
    """Get details of a public list."""
    from backend.services.auth_service import custom_lists_db
    
    for user_id, lists in custom_lists_db.items():
        for custom_list in lists:
            if custom_list.get("list_id") == list_id and custom_list.get("is_public"):
                list_copy = custom_list.copy()
                list_copy.pop("user_id", None)
                return list_copy
    
    raise HTTPException(status_code=404, detail="Public list not found")
