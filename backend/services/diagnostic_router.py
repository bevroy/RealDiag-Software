
from fastapi import APIRouter, Body, Depends, Request, HTTPException
from typing import Any, Dict, Optional
from .decision_tree_engine import DecisionTreeEngine
from .auth_service import get_optional_user, add_search_to_history
from .search_limiter import check_search_limit, get_search_limit_info
from .subscription_gate import SubscriptionGate

router = APIRouter(prefix="/diagnostic", tags=["diagnostic"])
_trees = DecisionTreeEngine()

# Import user subscriptions from subscription_router
# In production, this would be a database connection
from .subscription_router import user_subscriptions

@router.get("/search-limit")
def get_search_limit_status(
    request: Request,
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """
    Check search limit status for the current user/IP.
    
    Returns information about remaining free searches for anonymous users,
    or unlimited status for authenticated users.
    
    Useful for displaying a banner/warning before users hit their limit.
    """
    limit_info = get_search_limit_info(request, user_authenticated=bool(current_user))
    return limit_info

@router.get("/trees")
def list_trees(
    request: Request,
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """
    List all available diagnostic trees.
    
    Public endpoint - authentication optional.
    Authenticated users get personalized recommendations.
    """
    trees = _trees.list()
    
    result = {"trees": trees}
    
    # Add personalized data for authenticated users
    if current_user:
        result["user_id"] = current_user.get("user_id")
        result["search_limit"] = "unlimited"
        # Could add: recently used trees, recommended trees based on specialty, etc.
    else:
        # Show search limit info for anonymous users
        limit_info = get_search_limit_info(request, user_authenticated=False)
        result["free_trial"] = limit_info
    
    return result

@router.post("/evaluate/{tree_id}")
async def evaluate_tree(
    tree_id: str,
    request: Request,
    patient: Dict[str, Any] = Body(...),
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """
    Evaluate a patient against a diagnostic tree.
    
    🆓 FREE TRIAL: 10 searches per week for anonymous users
    🔐 UNLIMITED: Create account for unlimited searches based on your plan
    
    Public endpoint - authentication optional but recommended.
    Authenticated users get searches based on their subscription plan.
    Anonymous users limited to 10 searches per 7 days.
    """
    # Check subscription-based limits for authenticated users
    if current_user:
        async with SubscriptionGate(current_user, user_subscriptions) as gate:
            # Check if user has module access
            tree_info = _trees.get_tree_info(tree_id)
            if tree_info and tree_info.get("module"):
                module_name = tree_info["module"]
                
                # Check module access based on subscription
                feature_key = f"modules_{module_name.lower()}"
                if not gate.has_feature(feature_key):
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "error": "Module access restricted",
                            "module": module_name,
                            "tree_id": tree_id,
                            "current_plan": gate.plan.value,
                            "upgrade_required": True,
                            "message": f"Upgrade your plan to access {module_name} module"
                        }
                    )
    
    # For anonymous users or free plan users, check free trial limits
    if not current_user or (current_user and str(user_subscriptions.get(current_user["user_id"], {}).get("plan_type", "free")) == "free"):
        # Check search limits (raises 429 if limit exceeded for anonymous users)
        limit_check = check_search_limit(
            request=request,
            tree_id=tree_id,
            user_authenticated=bool(current_user)
        )
    else:
        # Paid users have unlimited searches (handled by subscription)
        limit_check = {"searches_used": 0, "searches_remaining": float('inf')}
    
    # Perform the evaluation
    result = _trees.evaluate(tree_id, patient)
    
    # Save to search history for authenticated users
    if current_user and result:
        try:
            # Extract symptoms from patient data
            symptoms = []
            if "symptoms" in patient:
                symptoms = patient["symptoms"] if isinstance(patient["symptoms"], list) else [patient["symptoms"]]
            
            # Get top diagnosis from result
            top_diagnosis = None
            if isinstance(result, dict) and "diagnoses" in result and result["diagnoses"]:
                top_diagnosis = result["diagnoses"][0].get("label") if isinstance(result["diagnoses"][0], dict) else None
            
            # Save to history
            add_search_to_history(
                user_id=current_user["user_id"],
                symptoms=symptoms,
                result_count=len(result.get("diagnoses", [])) if isinstance(result, dict) else 0,
                age=patient.get("age"),
                sex=patient.get("sex"),
                family=patient.get("family"),
                top_diagnosis=top_diagnosis
            )
        except Exception as e:
            # Don't fail the evaluation if history saving fails
            print(f"Failed to save search history: {e}")
    
    # Return result with search limit info
    response = {"tree_result": result}
    
    # Add search limit info to response
    if not current_user:
        response["search_limit"] = {
            "searches_used": limit_check["searches_used"],
            "searches_remaining": limit_check["searches_remaining"],
            "message": limit_check.get("warning") or limit_check.get("message", "")
        }
        
        if limit_check["searches_remaining"] <= 2:
            response["search_limit"]["upgrade_message"] = "Create a free account for unlimited searches!"
            response["search_limit"]["register_url"] = "/users/register"
    
    return response
