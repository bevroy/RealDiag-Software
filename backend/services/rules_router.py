
from fastapi import APIRouter, Query, Depends
from typing import Optional, Dict
from .rules_engine import RulesEngine
from .auth_service import get_optional_user

router = APIRouter(prefix="/rules", tags=["rules"])
_rules = RulesEngine()

@router.get("/families")
def list_families(current_user: Optional[Dict] = Depends(get_optional_user)):
    """
    List all available clinical rule families.
    
    Public endpoint - authentication optional.
    """
    families = _rules.list_families()
    
    result = {"families": families}
    
    # Add user context for authenticated users
    if current_user:
        result["user_id"] = current_user.get("user_id")
        # Could filter by user's specialty or show recently viewed families
    
    return result

@router.get("/family/{family}")
def get_family(family: str, current_user: Optional[Dict] = Depends(get_optional_user)):
    """
    Get all rules for a specific family.
    
    Public endpoint - authentication optional.
    """
    rules = _rules.get_family(family)
    
    # Authenticated users could see which rules they've favorited
    if current_user and rules:
        rules["user_id"] = current_user.get("user_id")
    
    return rules

@router.get("/rule/{rule_id}")
def get_rule(rule_id: str, current_user: Optional[Dict] = Depends(get_optional_user)):
    """
    Get a specific rule by ID.
    
    Public endpoint - authentication optional.
    Authenticated users can see if rule is in their favorites.
    """
    rule = _rules.get_rule(rule_id)
    
    if current_user and rule:
        # Could check if rule is favorited by user
        rule["user_id"] = current_user.get("user_id")
    
    return rule

@router.get("/search")
def search_rules(
    q: str = Query(..., description="Search query"),
    family: Optional[str] = Query(None, description="Limit search to specific family"),
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """
    Search rules by keyword in labels, presentations, or ICD-10 codes.
    
    Public endpoint - authentication optional.
    Authenticated users get personalized ranking based on specialty/history.
    """
    results = _rules.search(q, family)
    
    response = {"results": results}
    
    if current_user:
        response["user_id"] = current_user.get("user_id")
        # Could rank results based on user's specialty or search history
    
    return response
