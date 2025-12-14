"""
Authentication & User Management Service
=========================================

Provides user authentication, session management, and profile handling.
Supports multiple auth providers: JWT, OAuth2, API keys.
"""

from fastapi import HTTPException, Depends, Header, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
import secrets
import hashlib
import jwt
from pathlib import Path
import json
import os
import logging

# Import database module
try:
    from .database import (
        DATABASE_AVAILABLE,
        get_db_session,
        User,
        Session as DBSession,
        SearchHistory,
        Favorite,
        CustomList,
        UserSettings,
        get_user_by_email,
        get_user_by_id,
        get_user_search_history as db_get_user_search_history,
        get_user_favorites as db_get_user_favorites,
        get_user_custom_lists as db_get_user_custom_lists,
        get_user_settings as db_get_user_settings
    )
except (ImportError, Exception) as e:
    DATABASE_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️  Database module not available - using in-memory storage: {e}")

# Import email service for verification
try:
    from .email_service import (
        is_employee_email,
        generate_verification_token,
        send_verification_email
    )
except ImportError:
    # Fallback if email service not available
    def is_employee_email(email: str) -> bool:
        return email.lower().endswith("@realdiag.org")
    def generate_verification_token() -> str:
        return secrets.token_urlsafe(32)
    def send_verification_email(email: str, token: str, full_name: str = None) -> bool:
        return False

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))  # Load from env in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))  # 1 hour default

security = HTTPBearer(auto_error=False)  # Don't auto-error, we'll check cookies too

# Models
class UserCreate(BaseModel):
    """User registration model."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    specialty: Optional[str] = None
    institution: Optional[str] = None

class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    """User profile model."""
    user_id: str
    email: str
    full_name: str
    specialty: Optional[str] = None
    institution: Optional[str] = None
    created_at: str
    last_login: Optional[str] = None
    search_count: int = 0
    favorite_count: int = 0

class UserSettings(BaseModel):
    """User settings and preferences."""
    user_id: str
    default_specialty: Optional[str] = None
    notification_preferences: Dict[str, bool] = {
        "email_updates": True,
        "new_features": True,
        "weekly_digest": False
    }
    display_preferences: Dict[str, Any] = {
        "theme": "light",
        "results_per_page": 10,
        "show_icd_codes": True,
        "show_snomed_codes": False
    }

class SearchHistory(BaseModel):
    """Search history entry."""
    search_id: str
    user_id: str
    symptoms: List[str]
    age: Optional[int] = None
    sex: Optional[str] = None
    family: Optional[str] = None
    timestamp: str
    result_count: int
    top_diagnosis: Optional[str] = None

class FavoriteDiagnosis(BaseModel):
    """Favorite diagnosis entry."""
    favorite_id: str
    user_id: str
    rule_id: str
    diagnosis_label: str
    family: str
    notes: Optional[str] = None
    added_at: str

class CustomList(BaseModel):
    """Custom differential diagnosis list."""
    list_id: str
    user_id: str
    name: str
    description: Optional[str] = None
    specialty: Optional[str] = None
    diagnoses: List[Dict[str, Any]] = []
    created_at: str
    updated_at: str
    is_public: bool = False


# In-memory storage (fallback when database not available)
users_db: Dict[str, Dict] = {}
sessions_db: Dict[str, Dict] = {}
search_history_db: Dict[str, List[Dict]] = {}
favorites_db: Dict[str, List[Dict]] = {}
custom_lists_db: Dict[str, List[Dict]] = {}
user_settings_db: Dict[str, Dict] = {}

logger = logging.getLogger(__name__)
if DATABASE_AVAILABLE:
    logger.info("✅ Using PostgreSQL database for data persistence")
else:
    logger.warning("⚠️  Using in-memory storage - data will be lost on restart")


# Helper functions
def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return hash_password(plain_password) == hashed_password

def create_access_token(user_id: str, email: str) -> str:
    """Create JWT access token."""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": user_id,
        "email": email,
        "exp": expire
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user.
    Checks HttpOnly cookie first, then Authorization header (for backwards compatibility).
    """
    token = None
    
    # First, try to get token from HttpOnly cookie (preferred method)
    token = request.cookies.get("access_token")
    
    # Fall back to Authorization header if cookie not present (backwards compatibility)
    if not token and credentials:
        token = credentials.credentials
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - no access token found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    # Try database first, fall back to in-memory
    if DATABASE_AVAILABLE:
        user = get_user_by_id(user_id)
        if user:
            return user.to_dict()
    
    # Fallback to in-memory storage
    if user_id in users_db:
        return users_db[user_id]
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )

async def get_optional_user(
    request: Request,
    authorization: Optional[str] = Header(None)
) -> Optional[Dict[str, Any]]:
    """
    Dependency to get user if authenticated, None otherwise.
    Checks HttpOnly cookie first, then Authorization header.
    """
    token = None
    
    # Try cookie first
    token = request.cookies.get("access_token")
    
    # Fall back to Authorization header
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
    
    if not token:
        return None
    
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        # Try database first
        if DATABASE_AVAILABLE:
            user = get_user_by_id(user_id)
            if user:
                return user.to_dict()
        
        # Fallback to in-memory
        return users_db.get(user_id)
    except:
        return None


# User management functions
def create_user(user_data: UserCreate) -> Dict[str, Any]:
    """Create new user account."""
    if DATABASE_AVAILABLE:
        # Database version
        with get_db_session() as db:
            # Check if email already exists
            existing = db.query(User).filter_by(email=user_data.email).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Create user
            user_id = f"user_{secrets.token_urlsafe(16)}"
            hashed_pwd = hash_password(user_data.password)
            
            # Check if this is an employee email
            is_employee_flag = is_employee_email(user_data.email)
            verification_token = None
            
            if is_employee_flag:
                # Generate verification token for employee
                verification_token = generate_verification_token()
            
            # Create user with backward compatibility for old database schema
            user_kwargs = {
                "user_id": user_id,
                "email": user_data.email,
                "username": user_data.email.split('@')[0],  # Default username from email
                "hashed_password": hashed_pwd,
                "full_name": user_data.full_name,
                "specialty": user_data.specialty,
                "institution": user_data.institution,
                "created_at": datetime.utcnow(),
                "is_active": True,
                "search_count": 0,
                "favorite_count": 0
            }
            
            # Add employee fields only if they exist in the schema
            try:
                # Test if these columns exist
                if hasattr(User, 'is_employee'):
                    user_kwargs["is_employee"] = is_employee_flag
                    user_kwargs["email_verified"] = False
                    user_kwargs["email_verification_token"] = verification_token
                    user_kwargs["email_verification_sent_at"] = datetime.utcnow() if is_employee_flag else None
            except:
                pass  # Old schema without employee fields
            
            user = User(**user_kwargs)
            
            db.add(user)
            db.flush()  # Get user.id without committing
            
            # Send verification email for employees
            if is_employee_flag and verification_token:
                send_verification_email(user_data.email, verification_token, user_data.full_name)
            
            # Commit the transaction to persist the user
            db.commit()
            db.refresh(user)
            
            # Note: User settings will be stored as part of the User model
            # No separate settings table needed for now
            
            return user.to_dict()
    
    else:
        # In-memory version (fallback)
        # Check if email already exists
        for user in users_db.values():
            if user["email"] == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Create user
        user_id = f"user_{secrets.token_urlsafe(16)}"
        hashed_pwd = hash_password(user_data.password)
        
        user = {
            "user_id": user_id,
            "email": user_data.email,
            "password_hash": hashed_pwd,
            "full_name": user_data.full_name,
            "specialty": user_data.specialty,
            "institution": user_data.institution,
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None,
            "search_count": 0,
            "favorite_count": 0,
            "is_active": True
        }
        
        users_db[user_id] = user
        
        # Initialize user data structures
        search_history_db[user_id] = []
        favorites_db[user_id] = []
        custom_lists_db[user_id] = []
        user_settings_db[user_id] = {
            "user_id": user_id,
            "default_specialty": user_data.specialty,
            "notification_preferences": {
                "email_updates": True,
                "new_features": True,
                "weekly_digest": False
            },
            "display_preferences": {
                "theme": "light",
                "results_per_page": 10,
                "show_icd_codes": True,
                "show_snomed_codes": False
            }
        }
        
        return user

def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    """Authenticate user and return user data."""
    if DATABASE_AVAILABLE:
        # Database version
        try:
            with get_db_session() as db:
                user = db.query(User).filter_by(email=email).first()
                
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found"
                    )
                
                if not verify_password(password, user.hashed_password):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Incorrect password"
                    )
                
                # Update last login
                try:
                    user.last_login = datetime.utcnow()
                    db.commit()
                except:
                    # Don't fail login if we can't update last_login
                    pass
                
                return user.to_dict()
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"Database error during authentication: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Authentication error: {str(e)}"
            )
    
    else:
        # In-memory version (fallback)
        for user in users_db.values():
            if user["email"] == email:
                if verify_password(password, user["password_hash"]):
                    # Update last login
                    user["last_login"] = datetime.utcnow().isoformat()
                    return user
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Incorrect password"
                    )
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


# Search history functions
def add_search_to_history(
    user_id: str,
    symptoms: List[str],
    result_count: int,
    age: Optional[int] = None,
    sex: Optional[str] = None,
    family: Optional[str] = None,
    top_diagnosis: Optional[str] = None
) -> Dict[str, Any]:
    """Add search to user's history."""
    search_id = f"search_{secrets.token_urlsafe(12)}"
    
    if DATABASE_AVAILABLE:
        # Database version
        with get_db_session() as db:
            search = SearchHistory(
                search_id=search_id,
                user_id=user_id,
                symptoms=symptoms,
                age=age,
                sex=sex,
                family=family,
                timestamp=datetime.utcnow(),
                result_count=result_count,
                top_diagnosis=top_diagnosis
            )
            db.add(search)
            
            # Update user's search count
            user = db.query(User).filter_by(user_id=user_id).first()
            if user:
                user.search_count += 1
            
            return search.to_dict()
    
    else:
        # In-memory version (fallback)
        if user_id not in search_history_db:
            search_history_db[user_id] = []
        
        search_entry = {
            "search_id": search_id,
            "user_id": user_id,
            "symptoms": symptoms,
            "age": age,
            "sex": sex,
            "family": family,
            "timestamp": datetime.utcnow().isoformat(),
            "result_count": result_count,
            "top_diagnosis": top_diagnosis
        }
        
        search_history_db[user_id].insert(0, search_entry)  # Most recent first
        
        # Update user's search count
        if user_id in users_db:
            users_db[user_id]["search_count"] += 1
        
        # Keep only last 100 searches
        search_history_db[user_id] = search_history_db[user_id][:100]
        
        return search_entry

def get_user_search_history(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get user's search history."""
    if DATABASE_AVAILABLE:
        # Database version
        searches = db_get_user_search_history(user_id, limit)
        return [s.to_dict() for s in searches]
    else:
        # In-memory version (fallback)
        return search_history_db.get(user_id, [])[:limit]


# Favorites functions
def add_favorite(
    user_id: str,
    rule_id: str,
    diagnosis_label: str,
    family: str,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """Add diagnosis to user's favorites."""
    favorite_id = f"fav_{secrets.token_urlsafe(12)}"
    
    if DATABASE_AVAILABLE:
        # Database version
        with get_db_session() as db:
            # Check if already favorited
            existing = db.query(Favorite).filter_by(user_id=user_id, rule_id=rule_id).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Diagnosis already in favorites"
                )
            
            favorite = Favorite(
                favorite_id=favorite_id,
                user_id=user_id,
                rule_id=rule_id,
                diagnosis_label=diagnosis_label,
                family=family,
                notes=notes,
                added_at=datetime.utcnow()
            )
            db.add(favorite)
            
            # Update user's favorite count
            user = db.query(User).filter_by(user_id=user_id).first()
            if user:
                user.favorite_count += 1
            
            return favorite.to_dict()
    
    else:
        # In-memory version (fallback)
        if user_id not in favorites_db:
            favorites_db[user_id] = []
        
        # Check if already favorited
        for fav in favorites_db[user_id]:
            if fav["rule_id"] == rule_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Diagnosis already in favorites"
                )
        
        favorite = {
            "favorite_id": favorite_id,
            "user_id": user_id,
            "rule_id": rule_id,
            "diagnosis_label": diagnosis_label,
            "family": family,
            "notes": notes,
            "added_at": datetime.utcnow().isoformat()
        }
        
        favorites_db[user_id].append(favorite)
        
        # Update user's favorite count
        if user_id in users_db:
            users_db[user_id]["favorite_count"] += 1
        
        return favorite

def get_user_favorites(user_id: str) -> List[Dict[str, Any]]:
    """Get user's favorite diagnoses."""
    if DATABASE_AVAILABLE:
        # Database version
        favorites = db_get_user_favorites(user_id)
        return [f.to_dict() for f in favorites]
    else:
        # In-memory version (fallback)
        return favorites_db.get(user_id, [])

def remove_favorite(user_id: str, favorite_id: str) -> bool:
    """Remove diagnosis from favorites."""
    if DATABASE_AVAILABLE:
        # Database version
        with get_db_session() as db:
            favorite = db.query(Favorite).filter_by(user_id=user_id, favorite_id=favorite_id).first()
            if favorite:
                db.delete(favorite)
                
                # Update user's favorite count
                user = db.query(User).filter_by(user_id=user_id).first()
                if user:
                    user.favorite_count -= 1
                
                return True
            return False
    
    else:
        # In-memory version (fallback)
        if user_id not in favorites_db:
            return False
        
        favorites = favorites_db[user_id]
        for i, fav in enumerate(favorites):
            if fav["favorite_id"] == favorite_id:
                favorites.pop(i)
                if user_id in users_db:
                    users_db[user_id]["favorite_count"] -= 1
                return True
        
        return False


# Custom lists functions
def create_custom_list(
    user_id: str,
    name: str,
    description: Optional[str] = None,
    specialty: Optional[str] = None,
    is_public: bool = False
) -> Dict[str, Any]:
    """Create custom differential diagnosis list."""
    list_id = f"list_{secrets.token_urlsafe(12)}"
    
    if DATABASE_AVAILABLE:
        # Database version
        with get_db_session() as db:
            custom_list = CustomList(
                list_id=list_id,
                user_id=user_id,
                name=name,
                description=description,
                specialty=specialty,
                diagnoses=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_public=is_public
            )
            db.add(custom_list)
            return custom_list.to_dict()
    
    else:
        # In-memory version (fallback)
        if user_id not in custom_lists_db:
            custom_lists_db[user_id] = []
        
        custom_list = {
            "list_id": list_id,
            "user_id": user_id,
            "name": name,
            "description": description,
            "specialty": specialty,
            "diagnoses": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "is_public": is_public
        }
        
        custom_lists_db[user_id].append(custom_list)
        return custom_list

def get_user_custom_lists(user_id: str) -> List[Dict[str, Any]]:
    """Get user's custom lists."""
    if DATABASE_AVAILABLE:
        # Database version
        lists = db_get_user_custom_lists(user_id)
        return [l.to_dict() for l in lists]
    else:
        # In-memory version (fallback)
        return custom_lists_db.get(user_id, [])

def add_diagnosis_to_list(user_id: str, list_id: str, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
    """Add diagnosis to custom list."""
    if DATABASE_AVAILABLE:
        # Database version
        with get_db_session() as db:
            custom_list = db.query(CustomList).filter_by(user_id=user_id, list_id=list_id).first()
            if not custom_list:
                raise HTTPException(status_code=404, detail="List not found")
            
            custom_list.diagnoses.append(diagnosis)
            custom_list.updated_at = datetime.utcnow()
            
            # SQLAlchemy requires flag_modified for JSON columns
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(custom_list, "diagnoses")
            
            return custom_list.to_dict()
    
    else:
        # In-memory version (fallback)
        if user_id not in custom_lists_db:
            raise HTTPException(status_code=404, detail="User has no lists")
        
        for custom_list in custom_lists_db[user_id]:
            if custom_list["list_id"] == list_id:
                custom_list["diagnoses"].append(diagnosis)
                custom_list["updated_at"] = datetime.utcnow().isoformat()
                return custom_list
        
        raise HTTPException(status_code=404, detail="List not found")

def remove_diagnosis_from_list(user_id: str, list_id: str, rule_id: str) -> Dict[str, Any]:
    """Remove diagnosis from custom list."""
    if DATABASE_AVAILABLE:
        # Database version
        with get_db_session() as db:
            custom_list = db.query(CustomList).filter_by(user_id=user_id, list_id=list_id).first()
            if not custom_list:
                raise HTTPException(status_code=404, detail="List not found")
            
            custom_list.diagnoses = [
                d for d in custom_list.diagnoses if d.get("rule_id") != rule_id
            ]
            custom_list.updated_at = datetime.utcnow()
            
            # SQLAlchemy requires flag_modified for JSON columns
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(custom_list, "diagnoses")
            
            return custom_list.to_dict()
    
    else:
        # In-memory version (fallback)
        if user_id not in custom_lists_db:
            raise HTTPException(status_code=404, detail="User has no lists")
        
        for custom_list in custom_lists_db[user_id]:
            if custom_list["list_id"] == list_id:
                custom_list["diagnoses"] = [
                    d for d in custom_list["diagnoses"] if d.get("rule_id") != rule_id
                ]
                custom_list["updated_at"] = datetime.utcnow().isoformat()
                return custom_list
        
        raise HTTPException(status_code=404, detail="List not found")


# Analytics functions
def get_user_analytics(user_id: str) -> Dict[str, Any]:
    """Get user analytics and insights."""
    if DATABASE_AVAILABLE:
        # Database version
        with get_db_session() as db:
            user = db.query(User).filter_by(user_id=user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            searches = db.query(SearchHistory)\
                .filter_by(user_id=user_id)\
                .order_by(SearchHistory.timestamp.desc())\
                .all()
            
            # Calculate statistics
            total_searches = len(searches)
            
            # Most searched symptoms
            symptom_counts = {}
            for search in searches:
                for symptom in search.symptoms or []:
                    symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1
            
            top_symptoms = sorted(symptom_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Most viewed specialties
            family_counts = {}
            for search in searches:
                if search.family:
                    family_counts[search.family] = family_counts.get(search.family, 0) + 1
            
            top_specialties = sorted(family_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Recent activity
            recent_activity = [s.to_dict() for s in searches[:10]]
            
            # Get custom lists count
            total_custom_lists = db.query(CustomList).filter_by(user_id=user_id).count()
            
            return {
                "user_id": user_id,
                "total_searches": total_searches,
                "total_favorites": user.favorite_count,
                "total_custom_lists": total_custom_lists,
                "member_since": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "top_symptoms": [{"symptom": s, "count": c} for s, c in top_symptoms],
                "top_specialties": [{"specialty": s, "count": c} for s, c in top_specialties],
                "recent_activity": recent_activity
            }
    
    else:
        # In-memory version (fallback)
        if user_id not in users_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = users_db[user_id]
        searches = search_history_db.get(user_id, [])
        
        # Calculate statistics
        total_searches = len(searches)
        
        # Most searched symptoms
        symptom_counts = {}
        for search in searches:
            for symptom in search.get("symptoms", []):
                symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1
        
        top_symptoms = sorted(symptom_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Most viewed specialties
        family_counts = {}
        for search in searches:
            family = search.get("family")
            if family:
                family_counts[family] = family_counts.get(family, 0) + 1
        
        top_specialties = sorted(family_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Recent activity
        recent_activity = searches[:10]
        
        return {
            "user_id": user_id,
            "total_searches": total_searches,
            "total_favorites": user.get("favorite_count", 0),
            "total_custom_lists": len(custom_lists_db.get(user_id, [])),
            "member_since": user.get("created_at"),
            "last_login": user.get("last_login"),
            "top_symptoms": [{"symptom": s, "count": c} for s, c in top_symptoms],
            "top_specialties": [{"specialty": s, "count": c} for s, c in top_specialties],
            "recent_activity": recent_activity
        }
