"""
User Accounts & Personalization Router
=======================================

REST API endpoints for user authentication, profiles, favorites, custom lists,
search history, and analytics.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr
from backend.services.auth_service import (
    UserCreate, UserLogin, UserProfile, UserSettings,
    SearchHistory, FavoriteDiagnosis, CustomList,
    create_user, authenticate_user, create_access_token,
    get_current_user, get_optional_user,
    add_search_to_history, get_user_search_history,
    add_favorite, get_user_favorites, remove_favorite,
    create_custom_list, get_user_custom_lists,
    add_diagnosis_to_list, remove_diagnosis_from_list,
    get_user_analytics,
    users_db, user_settings_db
)

router = APIRouter(prefix="/users", tags=["users"])


# Authentication endpoints
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    Register a new user account.
    
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
    """
    user = create_user(user_data)
    token = create_access_token(user["user_id"], user["email"])
    
    # Remove sensitive data
    user_safe = {k: v for k, v in user.items() if k != "password_hash"}
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_safe
    }

@router.post("/login", response_model=TokenResponse)
async def login_user(credentials: UserLogin):
    """
    Authenticate user and get access token.
    
    Request body:
    ```json
    {
      "email": "doctor@hospital.com",
      "password": "SecurePass123!"
    }
    ```
    """
    user = authenticate_user(credentials.email, credentials.password)
    token = create_access_token(user["user_id"], user["email"])
    
    # Remove sensitive data
    user_safe = {k: v for k, v in user.items() if k != "password_hash"}
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_safe
    }

@router.get("/me", response_model=UserProfile)
async def get_my_profile(current_user: Dict = Depends(get_current_user)):
    """Get current user's profile."""
    return {k: v for k, v in current_user.items() if k != "password_hash"}

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
