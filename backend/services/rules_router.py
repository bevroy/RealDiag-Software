
from fastapi import APIRouter, Query
from typing import Optional
from .rules_engine import RulesEngine

router = APIRouter(prefix="/rules", tags=["rules"])
_rules = RulesEngine()

@router.get("/families")
def list_families():
    """List all available clinical rule families."""
    return {"families": _rules.list_families()}

@router.get("/family/{family}")
def get_family(family: str):
    """Get all rules for a specific family."""
    return _rules.get_family(family)

@router.get("/rule/{rule_id}")
def get_rule(rule_id: str):
    """Get a specific rule by ID."""
    return _rules.get_rule(rule_id)

@router.get("/search")
def search_rules(
    q: str = Query(..., description="Search query"),
    family: Optional[str] = Query(None, description="Limit search to specific family")
):
    """Search rules by keyword in labels, presentations, or ICD-10 codes."""
    return {"results": _rules.search(q, family)}
