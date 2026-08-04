
from fastapi import APIRouter, Query, Depends
from typing import Optional, Dict
from .rules_engine import RulesEngine
from .auth_service import get_current_user, get_optional_user
from .cache_service import cache
from functools import lru_cache

router = APIRouter(prefix="/rules", tags=["rules"], dependencies=[Depends(get_current_user)])

# Lazy initialization - only create engine when first accessed
_rules_engine: Optional[RulesEngine] = None

def get_rules_engine() -> RulesEngine:
    """Get or create the rules engine singleton with caching."""
    global _rules_engine
    
    # Try to load from cache first
    cached_engine = cache.get("rules_engine_data")
    if cached_engine:
        if _rules_engine is None:
            _rules_engine = RulesEngine()
            _rules_engine.rule_sets = cached_engine
        return _rules_engine
    
    # Create new engine and cache it
    if _rules_engine is None:
        _rules_engine = RulesEngine()
        # Cache the loaded rule sets for 1 hour
        cache.set("rules_engine_data", _rules_engine.rule_sets, ttl=3600)
    
    return _rules_engine

@router.get("/families")
def list_families(current_user: Optional[Dict] = Depends(get_optional_user)):
    """
    List all available clinical rule families.
    
    Public endpoint - authentication optional.
    Cached for performance.
    """
    # Check cache first
    cached_families = cache.get("rules_families_list")
    if cached_families:
        result = {"families": cached_families}
        if current_user:
            result["user_id"] = current_user.get("user_id")
        return result
    
    # Load from engine
    rules = get_rules_engine()
    families = rules.list_families()
    
    # Cache for 1 hour
    cache.set("rules_families_list", families, ttl=3600)
    
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
    Cached for performance.
    """
    # Check cache first
    cache_key = f"rules_family_{family}"
    cached_rules = cache.get(cache_key)
    if cached_rules:
        if current_user:
            cached_rules["user_id"] = current_user.get("user_id")
        return cached_rules
    
    # Load from engine
    rules_engine = get_rules_engine()
    rules = rules_engine.get_family(family)
    
    # Cache for 1 hour
    if rules and "error" not in rules:
        cache.set(cache_key, rules, ttl=3600)
    
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
    Cached for performance.
    """
    # Check cache first
    cache_key = f"rules_rule_{rule_id}"
    cached_rule = cache.get(cache_key)
    if cached_rule:
        if current_user:
            cached_rule["user_id"] = current_user.get("user_id")
        return cached_rule
    
    # Load from engine
    rules_engine = get_rules_engine()
    rule = rules_engine.get_rule(rule_id)
    
    # Cache for 1 hour
    if rule and "error" not in rule:
        cache.set(cache_key, rule, ttl=3600)
    
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
    Cached for performance.
    """
    # Check cache for this search query
    cache_key = f"rules_search_{q}_{family or 'all'}"
    cached_results = cache.get(cache_key)
    if cached_results:
        response = {"results": cached_results}
        if current_user:
            response["user_id"] = current_user.get("user_id")
        return response
    
    # Perform search
    rules_engine = get_rules_engine()
    results = rules_engine.search(q, family)
    
    # Cache for 30 minutes (shorter than other endpoints since searches vary more)
    cache.set(cache_key, results, ttl=1800)
    
    response = {"results": results}
    
    if current_user:
        response["user_id"] = current_user.get("user_id")
        # Could rank results based on user's specialty or search history
    
    return response
