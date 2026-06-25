"""
Patient Context API Router

Provides endpoints for:
- Getting context variable definitions
- Getting context categories
- Evaluating context rules against diagnosis modules
- Generating context summaries
"""

from fastapi import APIRouter, Body
from typing import Dict, List, Any, Optional
from .context_engine import get_context_engine
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/context", tags=["context"])


@router.get("/variables")
def get_context_variables(category: Optional[str] = None):
    """
    Get available context variables, optionally filtered by category.
    
    Returns variable definitions including:
    - id, label, type, options
    - help_text and evidence level
    - references/citations
    
    Query params:
    - category: Filter by category (Diet, Supplements, Travel, etc.)
    """
    engine = get_context_engine()
    variables = engine.get_variables(category=category)
    
    return {
        "variables": variables,
        "total": len(variables),
        "categories": engine.get_categories()
    }


@router.get("/categories")
def get_context_categories():
    """
    Get list of context variable categories.
    
    Returns:
    - List of category names (Diet, Supplements, Travel, etc.)
    """
    engine = get_context_engine()
    categories = engine.get_categories()
    
    return {
        "categories": categories,
        "total": len(categories)
    }


@router.post("/evaluate/{diagnosis_module_id}")
def evaluate_context(
    diagnosis_module_id: str,
    patient_context: Dict[str, Any] = Body(...),
    base_result: Optional[Dict[str, Any]] = Body(None)
):
    """
    Evaluate patient context against a diagnosis module and return applicable modifications.
    
    This endpoint:
    1. Evaluates trigger expressions against patient context
    2. Identifies matching rules for the diagnosis module
    3. Returns context-based additions to differential, questions, workup, etc.
    4. Includes reasoning and references for transparency
    
    Request body:
    - patient_context: Dict of context variable values (e.g., {"seafood_frequency_per_week": 7})
    - base_result: Optional base diagnostic result to reference
    
    Returns:
    - has_context: Whether any rules were triggered
    - context_applied: List of rules that matched with references
    - context_differential: Additional diagnoses to consider
    - context_questions: Additional questions to ask
    - context_workup: Additional tests/workup to consider
    - context_red_flags: Additional warning signs
    - context_referral_notes: Referral guidance
    - urgency_adjustment: Any urgency level changes
    - reasoning: Detailed explanations with evidence levels and citations
    """
    engine = get_context_engine()
    
    try:
        result = engine.apply_context(
            diagnosis_module_id=diagnosis_module_id,
            patient_context=patient_context,
            base_result=base_result
        )
        
        # Add summary
        result["context_summary"] = engine.get_context_summary(patient_context)
        
        # Add disclaimer
        result["disclaimer"] = (
            "This tool provides information based on patient-reported exposures and lifestyle factors. "
            "It does not replace clinical judgment. All suggestions are guideline-based considerations, "
            "not prescriptive recommendations."
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error evaluating context for module {diagnosis_module_id}: {e}")
        return {
            "error": "Failed to evaluate context",
            "detail": str(e),
            "has_context": False
        }


@router.post("/summary")
def get_context_summary(patient_context: Dict[str, Any] = Body(...)):
    """
    Generate a human-readable summary of active context modifiers.
    
    Useful for displaying context chips/badges in the UI.
    
    Request body:
    - patient_context: Dict of context variable values
    
    Returns:
    - summary: List of human-readable summary strings
    - count: Number of active context modifiers
    """
    engine = get_context_engine()
    
    try:
        summary = engine.get_context_summary(patient_context)
        
        return {
            "summary": summary,
            "count": len(summary)
        }
    
    except Exception as e:
        logger.error(f"Error generating context summary: {e}")
        return {
            "error": "Failed to generate summary",
            "detail": str(e),
            "summary": [],
            "count": 0
        }


@router.get("/rules/{diagnosis_module_id}")
def get_rules_for_module(diagnosis_module_id: str):
    """
    Get all context rules applicable to a specific diagnosis module.
    
    Useful for understanding what context factors might affect a particular diagnosis.
    
    Path params:
    - diagnosis_module_id: ID of the diagnosis module
    
    Returns:
    - rules: List of applicable rules with triggers and effects
    - count: Number of rules for this module
    """
    engine = get_context_engine()
    
    applicable_rules = [
        {
            "id": rule.get("id"),
            "name": rule.get("name"),
            "triggers": rule.get("triggers", []),
            "trigger_logic": rule.get("trigger_logic", "any"),
            "effects_summary": {
                "adds_differential": len(rule.get("effects", {}).get("add_to_differential", [])),
                "adds_questions": len(rule.get("effects", {}).get("add_questions", [])),
                "adds_workup": len(rule.get("effects", {}).get("add_workup", [])),
                "adds_red_flags": len(rule.get("effects", {}).get("add_red_flags", [])),
                "urgency_adjustment": rule.get("effects", {}).get("adjust_urgency")
            },
            "evidence_level": rule.get("evidence_level"),
            "has_reasoning": bool(rule.get("effects", {}).get("reasoning"))
        }
        for rule in engine.rules
        if rule.get("diagnosis_module_id") == diagnosis_module_id
    ]
    
    return {
        "diagnosis_module_id": diagnosis_module_id,
        "rules": applicable_rules,
        "count": len(applicable_rules)
    }
