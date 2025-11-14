"""
Symptom-Based Search Service
=============================

This service provides intelligent diagnostic suggestions based on user-entered symptoms.
It searches across all disease families and ranks results by symptom match score.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pathlib import Path
import yaml
import re
from pydantic import BaseModel

router = APIRouter()

# Models
class SymptomSearchRequest(BaseModel):
    """Request model for symptom-based search."""
    symptoms: List[str]
    age: Optional[int] = None
    sex: Optional[str] = None
    family: Optional[str] = None  # Optional filter by disease family

class DiagnosisMatch(BaseModel):
    """Model for a matched diagnosis."""
    rule_id: str
    label: str
    family: str
    match_score: float
    matched_presentations: List[str]
    all_presentations: List[str]
    icd10: List[str]
    snomed: List[Any]  # Can be int or str in YAML

class SymptomSearchResponse(BaseModel):
    """Response model for symptom search."""
    query_symptoms: List[str]
    total_results: int
    results: List[DiagnosisMatch]


# Helper functions
def load_all_families() -> Dict[str, List[Dict[str, Any]]]:
    """Load all disease family YAML files."""
    rules_dir = Path(__file__).parent.parent / "rules"
    families = {}
    
    for yaml_file in rules_dir.glob("*.yml"):
        family_name = yaml_file.stem
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data and 'rules' in data:
                    families[family_name] = data['rules']
        except Exception as e:
            print(f"Error loading {family_name}: {e}")
            continue
    
    return families


def normalize_text(text: str) -> str:
    """Normalize text for comparison (lowercase, remove punctuation)."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    return text.strip()


def calculate_match_score(symptom_input: List[str], presentations: List[str]) -> tuple:
    """
    Calculate match score between input symptoms and rule presentations.
    
    Returns:
        (score, matched_presentations)
    """
    score = 0.0
    matched = []
    
    # Filter out non-string presentations (sometimes YAML has dicts)
    string_presentations = [p for p in presentations if isinstance(p, str)]
    
    # Normalize all inputs
    normalized_symptoms = [normalize_text(s) for s in symptom_input]
    normalized_presentations = [normalize_text(p) for p in string_presentations]
    
    for presentation_idx, presentation in enumerate(normalized_presentations):
        presentation_matched = False
        
        for symptom in normalized_symptoms:
            # Exact phrase match (highest weight)
            if symptom in presentation:
                score += 5.0
                presentation_matched = True
            # Word overlap (lower weight)
            else:
                symptom_words = set(symptom.split())
                presentation_words = set(presentation.split())
                overlap = symptom_words & presentation_words
                if overlap:
                    score += len(overlap) * 1.0
                    presentation_matched = True
        
        if presentation_matched:
            matched.append(string_presentations[presentation_idx])  # Keep original case
    
    # Normalize score by number of presentations (avoid bias toward diagnoses with many presentations)
    if string_presentations:
        score = score / len(string_presentations)
    
    return (score, matched)


def apply_filters(rules: List[Dict], age: Optional[int], sex: Optional[str]) -> List[Dict]:
    """Apply age and sex filters to rules (placeholder for future enhancement)."""
    # For now, return all rules. In future, could filter based on:
    # - Age-specific conditions (pediatric vs geriatric)
    # - Sex-specific conditions (obstetric/gynecologic)
    return rules


@router.post("/search/by-symptoms", response_model=SymptomSearchResponse)
async def search_by_symptoms(request: SymptomSearchRequest):
    """
    Search for diagnoses based on symptom input.
    
    Returns ranked list of possible diagnoses with match scores.
    """
    if not request.symptoms:
        raise HTTPException(status_code=400, detail="At least one symptom is required")
    
    # Load all families
    all_families = load_all_families()
    
    # Filter by family if specified
    if request.family:
        if request.family not in all_families:
            raise HTTPException(status_code=404, detail=f"Family not found: {request.family}")
        families_to_search = {request.family: all_families[request.family]}
    else:
        families_to_search = all_families
    
    # Search and score all rules
    results = []
    
    for family_name, rules in families_to_search.items():
        # Apply filters
        filtered_rules = apply_filters(rules, request.age, request.sex)
        
        for rule in filtered_rules:
            # Get presentations - filter to only strings
            presentations = rule.get('presentations', [])
            # Filter out non-string presentations (sometimes YAML has dicts or other types)
            string_presentations = [p for p in presentations if isinstance(p, str)]
            
            if not string_presentations:
                continue
            
            # Calculate match score
            score, matched_presentations = calculate_match_score(request.symptoms, string_presentations)
            
            # Only include if there's a match
            if score > 0:
                results.append(DiagnosisMatch(
                    rule_id=rule.get('id', ''),
                    label=rule.get('label', ''),
                    family=family_name,
                    match_score=round(score, 2),
                    matched_presentations=matched_presentations,
                    all_presentations=string_presentations,  # Use filtered list
                    icd10=rule.get('icd10', []),
                    snomed=rule.get('snomed', [])
                ))
    
    # Sort by score (descending)
    results.sort(key=lambda x: x.match_score, reverse=True)
    
    # Return top 20 results
    top_results = results[:20]
    
    return SymptomSearchResponse(
        query_symptoms=request.symptoms,
        total_results=len(top_results),
        results=top_results
    )


@router.get("/search/suggestions")
async def get_search_suggestions():
    """
    Get common symptoms for autocomplete suggestions.
    
    Returns a list of unique symptoms extracted from all presentations.
    """
    all_families = load_all_families()
    symptoms = set()
    
    for family_name, rules in all_families.items():
        for rule in rules:
            presentations = rule.get('presentations', [])
            for presentation in presentations:
                # Extract individual symptoms (simple approach: split by comma)
                parts = [p.strip() for p in presentation.split(',')]
                symptoms.update(parts)
    
    # Return sorted list (limit to 500 most common)
    sorted_symptoms = sorted(list(symptoms))[:500]
    
    return {
        "symptoms": sorted_symptoms,
        "total": len(sorted_symptoms)
    }
