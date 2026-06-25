"""
Homeopathy Router
=================

API endpoints for complementary homeopathic remedy suggestions.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from backend.services.homeopathy_service import get_homeopathy_service, HomeopathicRemedy

router = APIRouter(prefix="/homeopathy", tags=["homeopathy"])


class HomeopathyRequest(BaseModel):
    """Request for homeopathic remedy suggestions."""
    condition: Optional[str] = None
    symptoms: Optional[List[str]] = None


class HomeopathyResponse(BaseModel):
    """Response with homeopathic remedy suggestions."""
    remedies: List[HomeopathicRemedy]
    disclaimer: str = (
        "DISCLAIMER: Homeopathic remedies are complementary suggestions based on classical "
        "homeopathic materia medica. These suggestions are for informational purposes only "
        "and should NOT replace conventional medical diagnosis, treatment, or medications. "
        "Always consult with a licensed healthcare provider for medical conditions. "
        "Homeopathy should be used as a complementary approach under professional guidance."
    )
    sources: List[str] = [
        "Boericke's Materia Medica",
        "Kent's Repertory",
        "Clarke's Dictionary of Practical Materia Medica",
        "Classical Homeopathic Literature"
    ]


@router.post("/suggest", response_model=HomeopathyResponse)
async def get_homeopathy_suggestions(request: HomeopathyRequest):
    """
    Get homeopathic remedy suggestions for a condition or symptoms.
    
    This endpoint provides complementary homeopathic remedy suggestions based on
    classical homeopathic materia medica and repertory references.
    
    **IMPORTANT:** These are complementary suggestions only and should not replace
    conventional medical care.
    """
    service = get_homeopathy_service()
    remedies = []
    
    if request.condition:
        remedies = service.get_remedies_for_condition(request.condition)
    elif request.symptoms:
        remedies = service.get_remedies_for_symptoms(request.symptoms)
    else:
        raise HTTPException(
            status_code=400,
            detail="Either 'condition' or 'symptoms' must be provided"
        )
    
    return HomeopathyResponse(remedies=remedies)


@router.get("/conditions")
async def list_available_conditions():
    """
    List all conditions for which homeopathic suggestions are available.
    
    Returns a list of condition names that can be used with the /suggest endpoint.
    """
    service = get_homeopathy_service()
    conditions = list(service.remedy_database.keys())
    
    return {
        "conditions": [c.replace("_", " ").title() for c in conditions],
        "count": len(conditions),
        "disclaimer": (
            "Homeopathic suggestions are complementary and should not replace "
            "conventional medical diagnosis and treatment."
        )
    }
