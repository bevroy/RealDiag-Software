"""
Symptom-Based Search Service
=============================

This service provides intelligent diagnostic suggestions based on user-entered symptoms.
It searches across all disease families and ranks results by symptom match score.
"""

from fastapi import APIRouter, HTTPException, Request
from typing import List, Dict, Any, Optional
from pathlib import Path
import yaml
import re
from pydantic import BaseModel, validator, conint, conlist
import logging
from functools import lru_cache

# Import security features with fallback
try:
    from backend.services.security import limiter, InputValidator, AuditLogger
    LIMITER_AVAILABLE = True
except ImportError:
    logging.warning("Security features not available in symptom_search. Running without rate limiting.")
    LIMITER_AVAILABLE = False
    limiter = None
    
    # Provide dummy classes
    class InputValidator:
        @staticmethod
        def sanitize_string(value: str, max_length: int = 500) -> str:
            return value[:max_length].strip() if value else ""
    
    class AuditLogger:
        @staticmethod
        def log_security_event(event_type: str, details: dict, severity: str = "INFO"):
            logging.info(f"AUDIT: {event_type} - {details}")

router = APIRouter()

# Models
class SymptomSearchRequest(BaseModel):
    """Request model for symptom-based search with input validation."""
    symptoms: List[str]  # List of symptoms
    age: Optional[int] = None  # Patient age
    sex: Optional[str] = None
    family: Optional[str] = None  # Optional filter by disease family
    
    @validator('symptoms')
    def validate_symptoms(cls, v):
        """Sanitize and validate symptoms"""
        if not v:
            raise ValueError("At least one symptom is required")
        
        if len(v) > 50:
            raise ValueError("Maximum 50 symptoms allowed")
        
        # Sanitize each symptom
        sanitized = []
        for symptom in v:
            clean = InputValidator.sanitize_string(symptom, max_length=200)
            if clean:
                sanitized.append(clean)
        
        if not sanitized:
            raise ValueError("No valid symptoms provided")
        
        return sanitized
    
    @validator('age')
    def validate_age(cls, v):
        """Validate age is in reasonable range"""
        if v is not None and (v < 0 or v > 120):
            raise ValueError("Age must be between 0 and 120")
        return v
    
    @validator('sex')
    def validate_sex(cls, v):
        """Validate sex input"""
        if v and v not in ['M', 'F', 'male', 'female', '']:
            raise ValueError("Sex must be M, F, or empty")
        return v
    
    @validator('family')
    def validate_family(cls, v):
        """Sanitize family input"""
        if v:
            return InputValidator.sanitize_string(v, max_length=50)
        return v

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
    sensitivity: Optional[float] = None
    specificity: Optional[float] = None
    clinical_pearls: Optional[List[str]] = None
    management: Optional[List[str]] = None
    tests: Optional[List[str]] = None  # Diagnostic tests to order
    referrals: Optional[List[str]] = None  # Specialist referrals

class SymptomSearchResponse(BaseModel):
    """Response model for symptom search."""
    query_symptoms: List[str]
    total_results: int
    results: List[DiagnosisMatch]


# Helper functions
@lru_cache(maxsize=1)
def load_all_families() -> Dict[str, List[Dict[str, Any]]]:
    """
    Load all disease family YAML files with caching.
    Cache is automatically cleared on app reload.
    """
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
            logging.error(f"Error loading {family_name}: {e}")
            continue
    
    logging.info(f"Loaded {len(families)} disease families with {sum(len(rules) for rules in families.values())} total rules")
    return families


def normalize_text(text: str) -> str:
    """Normalize text for comparison (lowercase, remove punctuation)."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    return text.strip()


def calculate_match_score_optimized(normalized_symptoms: List[str], original_symptoms: List[str], 
                                   string_presentations: List[str], rule: Dict[str, Any] = None) -> tuple:
    """
    Optimized version - accepts pre-normalized symptoms to avoid redundant processing.
    
    Returns:
        (score, matched_presentations)
    """
    score = 0.0
    matched = []
    
    # Normalize presentations once
    normalized_presentations = [normalize_text(p) for p in string_presentations]
    
    for presentation_idx, presentation in enumerate(normalized_presentations):
        presentation_matched = False
        
        for symptom in normalized_symptoms:
            # Exact phrase match (highest weight)
            if symptom in presentation:
                score += 5.0
                presentation_matched = True
            # Word overlap - but require anatomical qualifiers to match
            else:
                symptom_words = symptom.split()
                presentation_words = presentation.split()
                
                # If symptom has multiple words (e.g., "facial pain"), require first word to match
                # This prevents "facial pain" from matching "chest pain", "back pain", etc.
                if len(symptom_words) > 1:
                    first_word = symptom_words[0]
                    # Check if the anatomical qualifier appears in the presentation
                    if first_word in presentation_words or any(first_word in pw for pw in presentation_words):
                        # First word matches, now check for other word overlap
                        symptom_word_set = set(symptom_words)
                        presentation_word_set = set(presentation_words)
                        overlap = symptom_word_set & presentation_word_set
                        if len(overlap) >= 2:  # Require at least 2 words to match
                            score += len(overlap) * 1.0
                            presentation_matched = True
                else:
                    # Single-word symptom - use original logic
                    symptom_word_set = set(symptom_words)
                    presentation_word_set = set(presentation_words)
                    overlap = symptom_word_set & presentation_word_set
                    if overlap:
                        score += len(overlap) * 1.0
                        presentation_matched = True
        
        if presentation_matched:
            matched.append(string_presentations[presentation_idx])  # Keep original case
    
    # Normalize score by number of presentations
    if string_presentations:
        score = score / len(string_presentations)
    
    # Apply clinical likelihood modifier
    if rule and 'sensitivity' in rule:
        sensitivity = float(rule['sensitivity'])
        sensitivity_modifier = 1.0 + (sensitivity - 0.5) * 0.2
        score = score * sensitivity_modifier
    
    return (score, matched)


def calculate_match_score(symptom_input: List[str], presentations: List[str], rule: Dict[str, Any] = None) -> tuple:
    """
    Calculate match score between input symptoms and rule presentations.
    Enhanced with clinical likelihood modifiers and improved matching logic.
    
    Multi-word symptoms (e.g., "facial pain") require the anatomical qualifier (first word)
    to match to prevent false positives like "facial pain" matching "chest pain".
    
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
            # Word overlap - but require anatomical qualifiers to match
            else:
                symptom_words = symptom.split()
                presentation_words = presentation.split()
                
                # If symptom has multiple words (e.g., "facial pain"), require first word to match
                # This prevents "facial pain" from matching "chest pain", "back pain", etc.
                if len(symptom_words) > 1:
                    first_word = symptom_words[0]
                    # Check if the anatomical qualifier appears in the presentation
                    if first_word in presentation_words or any(first_word in pw for pw in presentation_words):
                        # First word matches, now check for other word overlap
                        symptom_word_set = set(symptom_words)
                        presentation_word_set = set(presentation_words)
                        overlap = symptom_word_set & presentation_word_set
                        if len(overlap) >= 2:  # Require at least 2 words to match
                            score += len(overlap) * 1.0
                            presentation_matched = True
                else:
                    # Single-word symptom - use original logic
                    symptom_word_set = set(symptom_words)
                    presentation_word_set = set(presentation_words)
                    overlap = symptom_word_set & presentation_word_set
                    if overlap:
                        score += len(overlap) * 1.0
                        presentation_matched = True
        
        if presentation_matched:
            matched.append(string_presentations[presentation_idx])  # Keep original case
    
    # Normalize score by number of presentations (avoid bias toward diagnoses with many presentations)
    if string_presentations:
        score = score / len(string_presentations)
    
    # Apply clinical likelihood modifier based on sensitivity/specificity if available
    if rule and 'sensitivity' in rule:
        sensitivity = float(rule['sensitivity'])
        # Higher sensitivity = higher pre-test probability for this condition
        # Apply a small boost (max 10% increase) for high-sensitivity diagnoses
        sensitivity_modifier = 1.0 + (sensitivity - 0.5) * 0.2  # Range: 0.9 to 1.1
        score = score * sensitivity_modifier
    
    return (score, matched)


def apply_filters(rules: List[Dict], age: Optional[int], sex: Optional[str]) -> List[Dict]:
    """Apply age and sex filters to rules (placeholder for future enhancement)."""
    # For now, return all rules. In future, could filter based on:
    # - Age-specific conditions (pediatric vs geriatric)
    # - Sex-specific conditions (obstetric/gynecologic)
    return rules


@router.post("/search/by-symptoms", response_model=SymptomSearchResponse)
async def search_by_symptoms(request: SymptomSearchRequest, request_obj: Request):
    """
    Search for diagnoses based on symptom input.
    Rate limit: 60 requests per minute per IP.
    
    Returns ranked list of possible diagnoses with match scores.
    """
    # Audit log the search
    client_ip = request_obj.client.host if request_obj and request_obj.client else "unknown"
    AuditLogger.log_security_event(
        "symptom_search",
        {
            "symptom_count": len(request.symptoms),
            "age": request.age,
            "family": request.family,
            "ip": client_ip
        }
    )
    
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
    
    # Pre-normalize input symptoms once
    normalized_input = [normalize_text(s) for s in request.symptoms]
    
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
            
            # Calculate match score with clinical likelihood (pass pre-normalized input)
            score, matched_presentations = calculate_match_score_optimized(
                normalized_input, request.symptoms, string_presentations, rule
            )
            
            # Only include if there's a match
            if score > 0:
                # Prepare result with enhanced metadata
                diagnosis_match = DiagnosisMatch(
                    rule_id=rule.get('id', ''),
                    label=rule.get('label', ''),
                    family=family_name,
                    match_score=round(score, 2),
                    matched_presentations=matched_presentations,
                    all_presentations=string_presentations,  # Use filtered list
                    icd10=rule.get('icd10', []),
                    snomed=rule.get('snomed', []),
                    sensitivity=rule.get('sensitivity'),
                    specificity=rule.get('specificity'),
                    clinical_pearls=rule.get('clinical_pearls'),  # Will be None if not present, or list if present
                    management=rule.get('management'),
                    tests=rule.get('tests'),
                    referrals=rule.get('referrals')
                )
                
                results.append(diagnosis_match)
    
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
