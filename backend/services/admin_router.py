"""
Admin API Router
================

Provides administrative endpoints for managing AI-generated decision trees,
user accounts, and system configuration.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, List
from pydantic import BaseModel
import json
import os
import re
import secrets
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Import AI tree generator
try:
    from backend.services.ai_tree_generator import AITreeGenerator
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    AITreeGenerator = None

router = APIRouter(prefix="/admin", tags=["admin"])

_SAFE_TREE_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def _validate_tree_id(tree_id: str) -> str:
    if not tree_id or not _SAFE_TREE_ID_RE.match(tree_id):
        raise HTTPException(status_code=400, detail="Invalid tree_id")
    return tree_id


# Models
class TreeReviewRequest(BaseModel):
    """Request to approve or reject a tree"""
    tree_id: str
    action: str  # "approve" or "reject"
    reviewer_notes: Optional[str] = None
    rejection_reason: Optional[str] = None


class AdminUser(BaseModel):
    """Admin user info"""
    username: str
    role: str
    permissions: List[str]


class RoleUpdateRequest(BaseModel):
    """Request body for role updates."""
    role: str
    reason: Optional[str] = None


class RoleUpdateByEmailRequest(BaseModel):
    """Request body for role updates using an email lookup."""
    email: str
    role: str
    reason: Optional[str] = None


ALLOWED_ACCOUNT_ROLES = {"user", "patient", "provider", "doctor", "admin"}


def _normalize_allowed_role(role: str) -> str:
    normalized = (role or "").strip().lower()
    if normalized not in ALLOWED_ACCOUNT_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{role}'. Allowed roles: {sorted(ALLOWED_ACCOUNT_ROLES)}"
        )
    return normalized


def _audit_role_change(admin: AdminUser, target_user_id: str, old_role: Optional[str], new_role: str, reason: Optional[str]):
    logger.info(
        "ROLE_CHANGE admin=%s target_user_id=%s old_role=%s new_role=%s reason=%s at=%s",
        admin.username,
        target_user_id,
        old_role,
        new_role,
        reason or "",
        datetime.utcnow().isoformat(),
    )


# Simple admin authentication (replace with proper auth in production)
def verify_admin_token(authorization: Optional[str] = Header(None)) -> AdminUser:
    """
    Verify admin authentication token.
    
    In production, replace this with proper OAuth2/JWT authentication.
    For now, checks against ADMIN_TOKEN environment variable.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Extract token (format: "Bearer <token>")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    
    # Check against admin token
    admin_token = os.getenv("ADMIN_TOKEN")
    if not admin_token:
        raise HTTPException(
            status_code=503,
            detail="Admin authentication not configured"
        )
    
    if not secrets.compare_digest(token, admin_token):
        raise HTTPException(status_code=403, detail="Invalid admin token")
    
    # Return admin user info
    return AdminUser(
        username="admin",
        role="medical_admin",
        permissions=["review_trees", "approve_trees", "manage_users"]
    )


@router.get("/trees/pending")
async def list_pending_trees(admin: AdminUser = Depends(verify_admin_token)):
    """
    List all AI-generated trees pending review.
    
    Requires admin authentication.
    Returns summary of each pending tree.
    """
    if not AI_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="AI tree management not available"
        )
    
    try:
        generator = AITreeGenerator()
        trees = generator.load_pending_trees()
        
        # Build detailed summaries
        summaries = []
        for tree in trees:
            metadata = tree.get("metadata", {})
            diagnosis = tree.get("diagnosis", {})
            
            summary = {
                "tree_id": tree["tree_id"],
                "name": tree["name"],
                "description": tree.get("description", ""),
                "chief_complaint": tree.get("chief_complaint", ""),
                "family": tree.get("family", ""),
                "specialty": tree.get("specialty", ""),
                "urgency": tree.get("urgency", ""),
                "diagnosis_name": diagnosis.get("name", ""),
                "confidence": diagnosis.get("confidence", 0),
                "icd10": tree.get("icd10", ""),
                "snomed": tree.get("snomed", []),
                "generated_at": metadata.get("generated_at", ""),
                "generated_by": metadata.get("provider", ""),
                "source_symptoms": metadata.get("source_symptoms", []),
                "question_count": len(tree.get("questions", [])),
                "differential_count": len(diagnosis.get("differential_diagnoses", []))
            }
            summaries.append(summary)
        
        # Sort by generation date (newest first)
        summaries.sort(key=lambda x: x["generated_at"], reverse=True)
        
        return {
            "trees": summaries,
            "count": len(summaries),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Failed to list pending trees: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load pending trees: {str(e)}"
        )


@router.get("/trees/pending/{tree_id}")
async def get_pending_tree_detail(
    tree_id: str,
    admin: AdminUser = Depends(verify_admin_token)
):
    """
    Get full details of a specific pending tree for review.
    
    Requires admin authentication.
    Returns complete tree structure with all questions, workup, treatment, etc.
    """
    if not AI_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="AI tree management not available"
        )
    
    tree_id = _validate_tree_id(tree_id)

    try:
        # Load tree file
        pending_dir = os.path.abspath("backend/data/generated_trees/pending")
        filepath = os.path.join(pending_dir, f"{tree_id}.json")
        if not os.path.abspath(filepath).startswith(pending_dir + os.sep):
            raise HTTPException(status_code=400, detail="Invalid tree_id")
        if not os.path.exists(filepath):
            raise HTTPException(
                status_code=404,
                detail=f"Tree {tree_id} not found in pending"
            )
        
        with open(filepath, 'r') as f:
            tree_data = json.load(f)
        
        return {
            "tree": tree_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to load tree {tree_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load tree: {str(e)}"
        )


@router.post("/trees/review")
async def review_tree(
    review: TreeReviewRequest,
    admin: AdminUser = Depends(verify_admin_token)
):
    """
    Approve or reject a pending tree.
    
    Requires admin authentication.
    
    Actions:
    - "approve": Move tree to approved directory and make it searchable
    - "reject": Move tree to rejected directory with reason
    """
    if not AI_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="AI tree management not available"
        )
    
    _validate_tree_id(review.tree_id)

    if review.action not in ["approve", "reject"]:
        raise HTTPException(
            status_code=400,
            detail="Action must be 'approve' or 'reject'"
        )
    
    try:
        generator = AITreeGenerator()
        
        if review.action == "approve":
            success = generator.approve_tree(
                tree_id=review.tree_id,
                reviewer_notes=review.reviewer_notes
            )
            
            if not success:
                raise HTTPException(
                    status_code=404,
                    detail=f"Tree {review.tree_id} not found"
                )
            
            return {
                "success": True,
                "action": "approved",
                "tree_id": review.tree_id,
                "message": "Tree approved and moved to active database",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        elif review.action == "reject":
            if not review.rejection_reason:
                raise HTTPException(
                    status_code=400,
                    detail="Rejection reason required"
                )
            
            success = generator.reject_tree(
                tree_id=review.tree_id,
                reason=review.rejection_reason
            )
            
            if not success:
                raise HTTPException(
                    status_code=404,
                    detail=f"Tree {review.tree_id} not found"
                )
            
            return {
                "success": True,
                "action": "rejected",
                "tree_id": review.tree_id,
                "reason": review.rejection_reason,
                "message": "Tree rejected and moved to rejected directory",
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to review tree {review.tree_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to review tree: {str(e)}"
        )


@router.get("/trees/approved")
async def list_approved_trees(admin: AdminUser = Depends(verify_admin_token)):
    """
    List all approved AI-generated trees.
    
    Requires admin authentication.
    """
    if not AI_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="AI tree management not available"
        )
    
    try:
        approved_dir = "backend/data/generated_trees/approved"
        if not os.path.exists(approved_dir):
            return {"trees": [], "count": 0}
        
        trees = []
        for filename in os.listdir(approved_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(approved_dir, filename)
                with open(filepath, 'r') as f:
                    tree = json.load(f)
                    
                    metadata = tree.get("metadata", {})
                    trees.append({
                        "tree_id": tree["tree_id"],
                        "name": tree["name"],
                        "specialty": tree.get("specialty", ""),
                        "approved_at": metadata.get("approved_at", ""),
                        "generated_at": metadata.get("generated_at", ""),
                        "source_symptoms": metadata.get("source_symptoms", [])
                    })
        
        # Sort by approval date (newest first)
        trees.sort(key=lambda x: x.get("approved_at", ""), reverse=True)
        
        return {
            "trees": trees,
            "count": len(trees),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Failed to list approved trees: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load approved trees: {str(e)}"
        )


@router.get("/stats")
async def get_admin_stats(admin: AdminUser = Depends(verify_admin_token)):
    """
    Get system statistics for admin dashboard.
    
    Returns counts of pending, approved, and rejected trees,
    plus other system metrics.
    """
    try:
        stats = {
            "ai_generation": {
                "available": AI_AVAILABLE,
                "enabled": os.getenv("ENABLE_AI_GENERATION", "false").lower() == "true",
                "provider": os.getenv("AI_PROVIDER", "claude")
            },
            "trees": {
                "pending": 0,
                "approved": 0,
                "rejected": 0
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Count trees in each directory
        for status in ["pending", "approved", "rejected"]:
            directory = f"backend/data/generated_trees/{status}"
            if os.path.exists(directory):
                count = len([f for f in os.listdir(directory) if f.endswith('.json')])
                stats["trees"][status] = count
        
        return stats
        
    except Exception as e:
        logging.error(f"Failed to get stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load statistics: {str(e)}"
        )


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    body: RoleUpdateRequest,
    admin: AdminUser = Depends(verify_admin_token)
):
    """
    Update a user's role by user_id.

    Admin-only endpoint. Supports both DB-backed and in-memory fallback users.
    """
    new_role = _normalize_allowed_role(body.role)

    # Prefer DB path when available.
    try:
        from backend.services.database import DATABASE_AVAILABLE, get_db_session, User
        if DATABASE_AVAILABLE:
            with get_db_session() as db:
                user = db.query(User).filter_by(user_id=user_id).first()
                if not user:
                    raise HTTPException(status_code=404, detail="User not found")
                old_role = getattr(user, "role", None)
                user.role = new_role
                _audit_role_change(admin, user_id, old_role, new_role, body.reason)
                return {
                    "success": True,
                    "user_id": user_id,
                    "email": getattr(user, "email", None),
                    "old_role": old_role,
                    "new_role": new_role,
                    "reason": body.reason,
                    "updated_at": datetime.utcnow().isoformat(),
                }
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("DB role update path unavailable for user_id=%s: %s", user_id, e)

    # Fallback to in-memory storage.
    try:
        from backend.services.auth_service import users_db
        user = users_db.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        old_role = user.get("role")
        user["role"] = new_role
        _audit_role_change(admin, user_id, old_role, new_role, body.reason)
        return {
            "success": True,
            "user_id": user_id,
            "email": user.get("email"),
            "old_role": old_role,
            "new_role": new_role,
            "reason": body.reason,
            "updated_at": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Role update failed for user_id=%s: %s", user_id, e)
        raise HTTPException(status_code=500, detail="Role update failed")


@router.put("/users/role/by-email")
async def update_user_role_by_email(
    body: RoleUpdateByEmailRequest,
    admin: AdminUser = Depends(verify_admin_token)
):
    """
    Update a user's role by email.

    This is convenient when admins don't know user_id values.
    """
    if not body.email:
        raise HTTPException(status_code=400, detail="email is required")

    email = body.email.strip().lower()
    new_role = _normalize_allowed_role(body.role)

    # Prefer DB path when available.
    try:
        from backend.services.database import DATABASE_AVAILABLE, get_db_session, User
        if DATABASE_AVAILABLE:
            with get_db_session() as db:
                user = db.query(User).filter_by(email=email).first()
                if not user:
                    raise HTTPException(status_code=404, detail="User not found")
                old_role = getattr(user, "role", None)
                user.role = new_role
                _audit_role_change(admin, user.user_id, old_role, new_role, body.reason)
                return {
                    "success": True,
                    "user_id": user.user_id,
                    "email": email,
                    "old_role": old_role,
                    "new_role": new_role,
                    "reason": body.reason,
                    "updated_at": datetime.utcnow().isoformat(),
                }
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("DB role-by-email path unavailable for email=%s: %s", email, e)

    # Fallback to in-memory storage.
    try:
        from backend.services.auth_service import users_db
        found_user_id = None
        found_user = None
        for uid, user in users_db.items():
            if str(user.get("email", "")).strip().lower() == email:
                found_user_id = uid
                found_user = user
                break

        if not found_user:
            raise HTTPException(status_code=404, detail="User not found")

        old_role = found_user.get("role")
        found_user["role"] = new_role
        _audit_role_change(admin, found_user_id, old_role, new_role, body.reason)
        return {
            "success": True,
            "user_id": found_user_id,
            "email": email,
            "old_role": old_role,
            "new_role": new_role,
            "reason": body.reason,
            "updated_at": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Role update by email failed for email=%s: %s", email, e)
        raise HTTPException(status_code=500, detail="Role update failed")
