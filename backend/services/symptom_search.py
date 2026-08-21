"""
Symptom-Based Search Service
=============================

This service provides intelligent diagnostic suggestions based on user-entered symptoms.
It searches across all disease families and ranks results by symptom match score.
Features AI tree generation for symptom combinations not in database.
"""

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, Depends
from typing import List, Dict, Any, Optional
from pathlib import Path
import yaml
import re
import time
from pydantic import BaseModel, validator, conint, conlist
import logging
from functools import lru_cache
import os
from backend.services.patient_history_service import PatientHistoryService
from backend.services.auth_service import get_current_user

# Import cache service for performance
try:
    from backend.services.cache_service import CacheService
    cache = CacheService()
    CACHE_AVAILABLE = True
    logging.info("✅ Cache service initialized")
except ImportError:
    logging.warning("Cache service not available - using simple caching")
    CACHE_AVAILABLE = False
    cache = None

# Import search index for fast lookups
try:
    from backend.services.search_index import SearchIndex
    search_index = SearchIndex()
    INDEX_AVAILABLE = True
    logging.info("✅ Search index initialized")
except ImportError:
    logging.warning("Search index not available - using standard search")
    INDEX_AVAILABLE = False
    search_index = None

# Import AI tree generator
try:
    from backend.services.ai_tree_generator import AITreeGenerator
    AI_GENERATION_AVAILABLE = True
except ImportError:
    logging.warning("AI tree generator not available")
    AI_GENERATION_AVAILABLE = False
    AITreeGenerator = None

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

# FHIR configuration for optional encounter/history enrichment
FHIR_BASE_URL = os.getenv("FHIR_BASE_URL", "http://localhost:8080/fhir")
FHIR_AUTH_TOKEN = os.getenv("FHIR_AUTH_TOKEN", None)
_patient_history = None


async def get_patient_history_service() -> PatientHistoryService:
    """Get or initialize patient history service for encounter enrichment."""
    global _patient_history
    if _patient_history is None:
        _patient_history = PatientHistoryService(
            fhir_base_url=FHIR_BASE_URL,
            auth_token=FHIR_AUTH_TOKEN
        )
    return _patient_history


class VitalSignsInput(BaseModel):
    """Optional vital signs passed from encounter context."""
    heart_rate: Optional[int] = None
    blood_pressure: Optional[Dict[str, int]] = None
    temperature: Optional[float] = None
    respiratory_rate: Optional[int] = None
    oxygen_saturation: Optional[float] = None


def _append_unique_terms(target: List[str], values: List[str]) -> List[str]:
    """Append non-empty strings to target while preserving order and uniqueness."""
    seen = {v.lower() for v in target if isinstance(v, str)}
    for value in values:
        if not isinstance(value, str):
            continue
        clean = value.strip()
        if not clean:
            continue
        key = clean.lower()
        if key not in seen:
            target.append(clean)
            seen.add(key)
    return target


def _derive_terms_from_vitals(vitals: Dict[str, Any]) -> List[str]:
    """Map raw vitals to clinically meaningful search terms."""
    if not vitals:
        return []

    terms: List[str] = []

    heart_rate = vitals.get("heart_rate")
    if isinstance(heart_rate, (int, float)):
        if heart_rate >= 100:
            terms.append("tachycardia")
        elif heart_rate <= 50:
            terms.append("bradycardia")

    bp = vitals.get("blood_pressure") or {}
    systolic = bp.get("systolic") if isinstance(bp, dict) else None
    diastolic = bp.get("diastolic") if isinstance(bp, dict) else None
    if isinstance(systolic, (int, float)):
        if systolic < 90:
            terms.append("hypotension")
        elif systolic >= 140 or (isinstance(diastolic, (int, float)) and diastolic >= 90):
            terms.append("hypertension")

    temperature = vitals.get("temperature")
    if isinstance(temperature, (int, float)):
        if temperature >= 100.4:
            terms.append("fever")
        elif temperature < 95.0:
            terms.append("hypothermia")

    respiratory_rate = vitals.get("respiratory_rate")
    if isinstance(respiratory_rate, (int, float)):
        if respiratory_rate >= 22:
            terms.append("tachypnea")
        elif respiratory_rate <= 10:
            terms.append("bradypnea")

    oxygen_saturation = vitals.get("oxygen_saturation")
    if isinstance(oxygen_saturation, (int, float)) and oxygen_saturation < 94:
        terms.append("hypoxemia")

    return terms

# Models
class SymptomSearchRequest(BaseModel):
    """Request model for symptom-based search with input validation."""
    symptoms: List[str]  # List of symptoms
    age: Optional[int] = None  # Patient age
    sex: Optional[str] = None
    family: Optional[str] = None  # Optional filter by disease family
    vital_signs: Optional[VitalSignsInput] = None
    emr_patient_id: Optional[str] = None
    lookback_days: Optional[conint(ge=1, le=1825)] = 365
    
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
    has_tree: bool = True  # Whether a decision tree exists
    ai_suggested: bool = False  # Whether suggested by AI (no tree yet)

class SymptomSearchResponse(BaseModel):
    """Response model for symptom search."""
    query_symptoms: List[str]
    total_results: int
    results: List[DiagnosisMatch]


# Helper functions
# Cache with TTL to prevent stale data but avoid reloading on every request
_families_cache = None
_cache_time = 0

def load_all_families() -> Dict[str, List[Dict[str, Any]]]:
    """
    Load all diagnostic tree YAML files with distributed caching.
    
    Supports both old format (rules: array) and new format (individual tree files).
    Uses Redis cache if available, falls back to in-memory cache.
    Cache TTL: 1 hour (3600 seconds)
    """
    global _families_cache, _cache_time
    
    import time
    current_time = time.time()
    
    # Try distributed cache first (Redis)
    if CACHE_AVAILABLE and cache:
        cached_data = cache.get("diagnostic_trees_all_families")
        if cached_data is not None:
            logging.debug(f"Using distributed cache ({len(cached_data)} families)")
            _families_cache = cached_data
            _cache_time = current_time
            return cached_data
    
    # Try in-memory cache (5 min TTL for in-memory, 1 hour for distributed)
    if _families_cache is not None and (current_time - _cache_time) < 300:
        logging.debug(f"Using in-memory cache ({len(_families_cache)} families)")
        return _families_cache
    
    logging.info("Loading diagnostic trees (cache miss or expired)")
    
    # Try trees directory first (new format)
    trees_dir = Path(__file__).parent.parent / "trees"
    rules_dir = Path(__file__).parent.parent / "rules"
    families = {}
    total_trees = 0
    
    logging.info(f"Loading diagnostic trees from: {trees_dir}")
    logging.info(f"Trees directory exists: {trees_dir.exists()}")
    
    # Load from trees directory (new format - individual tree files)
    if trees_dir.exists():
        for yaml_file in trees_dir.glob("*.yml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    tree_data = yaml.safe_load(f)
                    
                if not tree_data:
                    continue
                
                # Convert tree format to rule format for compatibility
                family = tree_data.get('family', 'general')
                
                # Extract and flatten presentations
                presentations = tree_data.get('presentations', [])
                if isinstance(presentations, dict):
                    presentations = list(presentations.values())
                elif not isinstance(presentations, list):
                    presentations = [presentations] if presentations else []
                
                # Extract and flatten workup/tests
                workup = tree_data.get('workup', [])
                tests = []
                if isinstance(workup, list):
                    for item in workup:
                        if isinstance(item, dict):
                            # Flatten nested dict structure
                            for key, value in item.items():
                                if isinstance(value, list):
                                    tests.extend([f"{key}: {v}" for v in value])
                                else:
                                    tests.append(f"{key}: {value}")
                        else:
                            tests.append(str(item))
                elif isinstance(workup, dict):
                    for key, value in workup.items():
                        if isinstance(value, list):
                            tests.extend([f"{key}: {v}" for v in value])
                        else:
                            tests.append(f"{key}: {value}")
                else:
                    tests = [str(workup)] if workup else []
                
                # Extract and flatten treatment/management
                treatment = tree_data.get('treatment', [])
                management = []
                if isinstance(treatment, list):
                    for item in treatment:
                        if isinstance(item, dict):
                            # Flatten nested dict structure
                            for key, value in item.items():
                                if isinstance(value, list):
                                    management.extend([f"{key}: {v}" for v in value])
                                elif isinstance(value, dict):
                                    for subkey, subvalue in value.items():
                                        if isinstance(subvalue, list):
                                            management.extend([f"{key} - {subkey}: {v}" for v in subvalue])
                                        else:
                                            management.append(f"{key} - {subkey}: {subvalue}")
                                else:
                                    management.append(f"{key}: {value}")
                        else:
                            management.append(str(item))
                elif isinstance(treatment, dict):
                    for key, value in treatment.items():
                        if isinstance(value, list):
                            management.extend([f"{key}: {v}" for v in value])
                        elif isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if isinstance(subvalue, list):
                                    management.extend([f"{key} - {subkey}: {v}" for v in subvalue])
                                else:
                                    management.append(f"{key} - {subkey}: {subvalue}")
                        else:
                            management.append(f"{key}: {value}")
                else:
                    management = [str(treatment)] if treatment else []
                
                # Extract referrals
                referrals = tree_data.get('referrals', [])
                referral_list = []
                if isinstance(referrals, list):
                    referral_list = [str(r) for r in referrals]
                elif isinstance(referrals, dict):
                    for key, value in referrals.items():
                        if isinstance(value, list):
                            referral_list.extend([f"{key}: {v}" for v in value])
                        else:
                            referral_list.append(f"{key}: {value}")
                else:
                    referral_list = [str(referrals)] if referrals else []
                
                # Build rule-compatible format
                # Normalize snomed to always be a list
                snomed_value = tree_data.get('snomed', [])
                if not isinstance(snomed_value, list):
                    snomed_value = [snomed_value] if snomed_value is not None else []
                
                # Normalize icd10 to always be a list of strings
                icd10_value = tree_data.get('icd10', tree_data.get('icd10_code', ''))
                if not isinstance(icd10_value, list):
                    icd10_value = [icd10_value] if icd10_value else []
                # Filter out empty strings
                icd10_value = [str(code) for code in icd10_value if code]
                
                # Normalize clinical_pearls to list of strings (convert dicts to "key: value" format)
                clinical_pearls_raw = tree_data.get('clinical_pearls', [])
                clinical_pearls = []
                if isinstance(clinical_pearls_raw, list):
                    for pearl in clinical_pearls_raw:
                        if isinstance(pearl, dict):
                            # Convert dict to "key: value" string format
                            for key, value in pearl.items():
                                clinical_pearls.append(f"{key}: {value}")
                        elif isinstance(pearl, str):
                            clinical_pearls.append(pearl)
                
                rule = {
                    'id': tree_data.get('tree_id', yaml_file.stem),
                    'label': tree_data.get('name', yaml_file.stem),
                    'family': family,
                    'applies_to': tree_data.get('applies_to'),  # Add sex-specific metadata
                    'age_min': tree_data.get('age_min'),  # Add age restrictions
                    'age_max': tree_data.get('age_max'),  # Add age restrictions
                    'presentations': presentations,
                    'icd10': icd10_value,
                    'snomed': snomed_value,
                    'sensitivity': tree_data.get('sensitivity'),
                    'specificity': tree_data.get('specificity'),
                    'clinical_pearls': clinical_pearls,
                    'management': management,
                    'tests': tests,
                    'referrals': referral_list
                }
                
                # Add to family
                if family not in families:
                    families[family] = []
                families[family].append(rule)
                total_trees += 1
                
            except Exception as e:
                logging.error(f"Error loading tree {yaml_file.name}: {e}")
                continue
    
    # Also load from rules directory (old format) if it exists
    if rules_dir.exists():
        for yaml_file in rules_dir.glob("*.yml"):
            family_name = yaml_file.stem
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and 'rules' in data:
                        if family_name not in families:
                            families[family_name] = []
                        families[family_name].extend(data['rules'])
                        total_trees += len(data['rules'])
            except Exception as e:
                logging.error(f"Error loading {family_name}: {e}")
                continue
    
    logging.info(f"Loaded {len(families)} disease families with {total_trees} total diagnostic trees")
    
    # Update in-memory cache
    _families_cache = families
    _cache_time = current_time
    
    # Update distributed cache (1 hour TTL)
    if CACHE_AVAILABLE and cache:
        cache.set("diagnostic_trees_all_families", families, ttl=3600)
        logging.info("✅ Diagnostic trees cached in Redis (1 hour TTL)")
    
    # Build search index for fast lookups
    if INDEX_AVAILABLE and search_index:
        try:
            search_index.build_index(families)
            logging.info("✅ Search index built successfully")
        except Exception as e:
            logging.warning(f"Failed to build search index: {e}")
    
    return families


# Preload families at module import time to avoid timeout on first request
# Data will be loaded and cached on first request to avoid deployment timeouts
logging.info("Symptom search module loaded - trees will be loaded on first request")


# Cache for clinical cases
_cases_cache = None
_cases_cache_time = 0

def load_clinical_cases() -> List[Dict[str, Any]]:
    """
    Load clinical cases from JSON database.
    Uses simple caching to avoid reloading on every request.
    """
    global _cases_cache, _cases_cache_time
    
    current_time = time.time()
    if _cases_cache is not None and (current_time - _cases_cache_time) < 300:
        logging.debug(f"Using cached cases data ({len(_cases_cache)} cases)")
        return _cases_cache
    
    logging.info("Loading clinical cases (cache miss or expired)")
    
    cases_file = Path(__file__).parent.parent / "data" / "clinical_cases.json"
    
    if not cases_file.exists():
        logging.warning(f"Clinical cases file not found: {cases_file}")
        return []
    
    try:
        import json
        with open(cases_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            cases = data.get('cases', [])
            logging.info(f"Loaded {len(cases)} clinical cases")
            
            # Update cache
            _cases_cache = cases
            _cases_cache_time = current_time
            
            return cases
    except Exception as e:
        logging.error(f"Error loading clinical cases: {e}")
        return []


def search_clinical_cases(normalized_symptoms: List[str], original_symptoms: List[str]) -> Dict[str, Dict]:
    """
    Search clinical cases database for diagnoses matching symptoms.
    Returns dict of {diagnosis_id: match_data} for diagnoses found in cases but not in trees.
    
    Args:
        normalized_symptoms: List of normalized symptom strings for matching
        original_symptoms: Original symptom strings for display
        
    Returns:
        Dict mapping diagnosis IDs to match information including:
        - diagnosis: str (diagnosis name)
        - specialty: str
        - score: float
        - matched_presentations: list
        - case_ids: list
        - icd10: list
    """
    cases = load_clinical_cases()
    diagnosis_matches = {}
    
    for case in cases:
        # Extract searchable text from case
        presentation = case.get('presentation', '')
        correct_diagnosis = case.get('correct_diagnosis', '')
        differential = case.get('differential', [])
        tags = case.get('tags', [])
        specialty = case.get('specialty', '')
        case_id = case.get('case_id', '')
        
        # Combine searchable text
        searchable_text = f"{presentation} {' '.join(tags)}".lower()
        
        # Calculate match score for this case
        score = 0.0
        matched = []
        
        for symptom in normalized_symptoms:
            if symptom in searchable_text:
                score += 5.0  # Exact phrase match
                matched.append(symptom)
            else:
                # Word overlap
                symptom_words = set(symptom.split())
                text_words = set(searchable_text.split())
                overlap = symptom_words & text_words
                if overlap:
                    score += len(overlap) * 1.0
                    if symptom not in matched:
                        matched.append(symptom)
        
        # Only include if there's a match
        if score > 0:
            # Add correct diagnosis
            if correct_diagnosis:
                if correct_diagnosis not in diagnosis_matches:
                    diagnosis_matches[correct_diagnosis] = {
                        'diagnosis': correct_diagnosis,
                        'specialty': specialty,
                        'score': 0.0,
                        'matched_presentations': [],
                        'case_ids': [],
                        'icd10': [],
                        'all_presentations': []
                    }
                
                # Update with best score for this diagnosis
                if score > diagnosis_matches[correct_diagnosis]['score']:
                    diagnosis_matches[correct_diagnosis]['score'] = score
                    diagnosis_matches[correct_diagnosis]['matched_presentations'] = matched
                    diagnosis_matches[correct_diagnosis]['all_presentations'].append(presentation)
                
                # Always add case ID
                if case_id not in diagnosis_matches[correct_diagnosis]['case_ids']:
                    diagnosis_matches[correct_diagnosis]['case_ids'].append(case_id)
            
            # Add differential diagnoses (with lower scores)
            for diff_dx in differential:
                if diff_dx and diff_dx != correct_diagnosis:
                    if diff_dx not in diagnosis_matches:
                        diagnosis_matches[diff_dx] = {
                            'diagnosis': diff_dx,
                            'specialty': specialty,
                            'score': 0.0,
                            'matched_presentations': [],
                            'case_ids': [],
                            'icd10': [],
                            'all_presentations': []
                        }
                    
                    # Differential diagnoses get 50% of the case's score
                    diff_score = score * 0.5
                    if diff_score > diagnosis_matches[diff_dx]['score']:
                        diagnosis_matches[diff_dx]['score'] = diff_score
                        diagnosis_matches[diff_dx]['matched_presentations'] = matched
                        diagnosis_matches[diff_dx]['all_presentations'].append(presentation)
                    
                    # Add case ID as differential example
                    if case_id not in diagnosis_matches[diff_dx]['case_ids']:
                        diagnosis_matches[diff_dx]['case_ids'].append(case_id)
    
    return diagnosis_matches


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
    
    # REMOVED: Normalization by presentation count - this penalized comprehensive diagnoses
    # OLD: score = score / len(string_presentations)
    # NEW: Keep raw score to reward actual symptom matches
    # Diagnoses with more matching presentations should rank higher
    
    # Apply clinical likelihood modifier
    if rule and 'sensitivity' in rule and rule['sensitivity'] is not None:
        try:
            sensitivity = float(rule['sensitivity'])
            sensitivity_modifier = 1.0 + (sensitivity - 0.5) * 0.2
            score = score * sensitivity_modifier
        except (ValueError, TypeError):
            pass  # Skip if sensitivity can't be converted to float
    
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
    
    # REMOVED: Normalization by presentation count - this penalized comprehensive diagnoses
    # OLD: score = score / len(string_presentations)
    # NEW: Keep raw score to reward actual symptom matches
    # A diagnosis matching 3 patient symptoms should rank higher than one matching 1 symptom
    # regardless of how many total presentations each diagnosis has in the database
    
    # Apply clinical likelihood modifier based on sensitivity/specificity if available
    if rule and 'sensitivity' in rule and rule['sensitivity'] is not None:
        try:
            sensitivity = float(rule['sensitivity'])
            # Higher sensitivity = higher pre-test probability for this condition
            # Apply a small boost (max 10% increase) for high-sensitivity diagnoses
            sensitivity_modifier = 1.0 + (sensitivity - 0.5) * 0.2  # Range: 0.9 to 1.1
            score = score * sensitivity_modifier
        except (ValueError, TypeError):
            pass  # Skip if sensitivity can't be converted to float
    
    return (score, matched)


def apply_filters(rules: List[Dict], age: Optional[int], sex: Optional[str]) -> List[Dict]:
    """Apply age and sex filters to rules."""
    filtered = []
    
    # Normalize sex input
    normalized_sex = None
    if sex:
        sex_upper = sex.upper()
        if sex_upper in ['M', 'MALE']:
            normalized_sex = 'male'
        elif sex_upper in ['F', 'FEMALE']:
            normalized_sex = 'female'
    
    for rule in rules:
        # Check age-specific applicability
        if age is not None:
            age_min = rule.get('age_min')
            age_max = rule.get('age_max')
            
            # Skip if explicit age restrictions are violated
            if age_min is not None and age < age_min:
                continue
            if age_max is not None and age > age_max:
                continue
            
            # Keyword-based age filtering as fallback
            rule_id = rule.get('id', '').upper()
            label = rule.get('label', '').upper()
            family = rule.get('family', '').upper()
            
            # Pediatric conditions (typically < 18 years)
            if age >= 18:
                pediatric_keywords = ['PEDS-', 'PEDIATRIC', 'CROUP', 'BRONCHIOLITIS', 
                                     'DEVELOPMENTAL DELAY', 'AUTISM', 'WELL-CHILD',
                                     'FEBRILE SEIZURE', 'HAND FOOT MOUTH']
                if family == 'PEDIATRICS':
                    continue
                if any(keyword in rule_id or keyword in label for keyword in pediatric_keywords):
                    continue
            
            # Geriatric conditions (typically 65+ years)
            if age < 65:
                geriatric_keywords = ['GER-', 'GERIATRIC', 'SARCOPENIA', 'FRAILTY',
                                     'DELIRIUM', 'POLYPHARMACY', 'FALLS RISK',
                                     'PRESSURE ULCER']
                if family == 'GERIATRICS':
                    continue
                if any(keyword in rule_id or keyword in label for keyword in geriatric_keywords):
                    continue
        
        # Check sex-specific applicability
        applies_to = rule.get('applies_to', None)
        
        if applies_to:
            # If rule has explicit sex restriction, filter accordingly
            if normalized_sex:
                if applies_to.lower() != normalized_sex:
                    # Skip this rule - it's for the opposite sex
                    continue
            # If no sex provided, include sex-specific conditions with warning
            # (they might be reviewing differential diagnoses)
        
        # Check if rule_id or label contains sex-specific keywords
        if normalized_sex:
            rule_id = rule.get('id', '').upper()
            label = rule.get('label', '').upper()
            family = rule.get('family', '').upper()
            
            # Male-only conditions
            if normalized_sex == 'female':
                male_keywords = [
                    'PROSTAT', 'TESTIC', 'PENILE', 'ERECTILE', 
                    'EPIDIDYM', 'ORCHITIS', 'SPERMAT'
                ]
                if any(keyword in rule_id or keyword in label for keyword in male_keywords):
                    continue
            
            # Female-only conditions
            if normalized_sex == 'male':
                female_keywords = [
                    'PREGNAN', 'OVARIAN', 'MENSTRUAL', 'CERVIC', 'UTERIN',
                    'VAGINAL', 'ENDOMETRIO', 'MENOPAUSE', 'DYSMENORRHEA',
                    'AMENORRHEA', 'MENORRHAGIA', 'ECTOPIC', 'PLACENTA',
                    'OVARY', 'VULVO', 'PCOS', 'POLYCYSTIC OVARY'
                ]
                if family == 'OBSTETRICS GYNECOLOGY' or family == 'OBGYN':
                    continue
                if any(keyword in rule_id or keyword in label for keyword in female_keywords):
                    continue
        
        filtered.append(rule)
    
    return filtered


async def query_ai_for_diagnoses(symptoms: List[str], age: Optional[int] = None, sex: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Query AI for possible diagnoses based on symptoms.
    Used when tree search returns insufficient results.
    
    Returns list of AI-suggested diagnoses with structure:
    {
        'diagnosis': str,
        'specialty': str,
        'icd10': List[str],
        'likelihood': str,
        'key_features': List[str]
    }
    """
    if not AI_GENERATION_AVAILABLE:
        logging.warning("AI not available for diagnosis suggestions")
        return []
    
    # Check if AI generation is enabled
    if not os.getenv("ENABLE_AI_GENERATION", "false").lower() == "true":
        return []
    
    try:
        # Build context
        context = f"Patient presenting with: {', '.join(symptoms)}"
        if age:
            context += f"\nAge: {age} years"
        if sex:
            context += f"\nSex: {sex}"
        
        # Create prompt for AI
        prompt = f"""Given these symptoms, list the top 10 most likely diagnoses.

{context}

For each diagnosis, provide:
1. Diagnosis name (use standard medical terminology)
2. Medical specialty
3. ICD-10 code(s)
4. Likelihood (high/moderate/low)
5. Key clinical features that match

Return ONLY a JSON array with this structure:
[
  {{
    "diagnosis": "Diagnosis Name",
    "specialty": "cardiology",
    "icd10": ["I21.9"],
    "likelihood": "high",
    "key_features": ["feature 1", "feature 2"]
  }}
]

No additional text, just the JSON array."""
        
        # Query AI
        provider = os.getenv("AI_PROVIDER", "claude")
        
        if provider == "claude":
            from anthropic import Anthropic
            client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
        else:
            # OpenAI
            import openai
            openai.api_key = os.getenv("OPENAI_API_KEY")
            
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
        
        # Parse JSON response
        import json
        # Extract JSON from response (handle potential markdown code blocks)
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        diagnoses = json.loads(content)
        logging.info(f"AI suggested {len(diagnoses)} diagnoses for symptoms: {symptoms}")
        return diagnoses
        
    except Exception as e:
        logging.error(f"Error querying AI for diagnoses: {e}", exc_info=True)
        return []


@router.post("/search/by-symptoms", response_model=SymptomSearchResponse)
async def search_by_symptoms(request: SymptomSearchRequest, request_obj: Request):
    """
    Search for diagnoses based on symptom input.
    Rate limit: 60 requests per minute per IP.
    
    Returns ranked list of possible diagnoses with match scores.
    """
    try:
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

        effective_symptoms = list(request.symptoms)

        # Add symptom terms inferred from user-entered encounter vitals.
        if request.vital_signs:
            vitals_terms = _derive_terms_from_vitals(request.vital_signs.dict(exclude_none=True))
            _append_unique_terms(effective_symptoms, vitals_terms)

        # Optionally enrich with EHR encounter/history context when available.
        if request.emr_patient_id:
            try:
                history_service = await get_patient_history_service()
                patient_history = await history_service.get_comprehensive_history(
                    patient_id=request.emr_patient_id,
                    lookback_days=request.lookback_days or 365
                )

                history_terms: List[str] = []

                for hp in patient_history.history_and_physicals[:3]:
                    if hp.chief_complaint:
                        history_terms.append(hp.chief_complaint)

                if patient_history.vital_signs:
                    latest_vitals = patient_history.vital_signs[0]
                    history_vitals = {
                        "heart_rate": latest_vitals.heart_rate,
                        "blood_pressure": {
                            "systolic": latest_vitals.blood_pressure_systolic,
                            "diastolic": latest_vitals.blood_pressure_diastolic
                        },
                        "temperature": latest_vitals.temperature,
                        "respiratory_rate": latest_vitals.respiratory_rate,
                        "oxygen_saturation": latest_vitals.oxygen_saturation,
                    }
                    history_terms.extend(_derive_terms_from_vitals(history_vitals))

                _append_unique_terms(effective_symptoms, history_terms)
            except Exception as e:
                logging.warning(f"Unable to enrich symptom search with EMR history: {e}")

        if not effective_symptoms:
            raise HTTPException(status_code=400, detail="At least one symptom is required")

        logging.info(f"Symptom search request: {effective_symptoms}")
        
        # Load all families
        all_families = load_all_families()
        logging.info(f"Loaded {len(all_families)} families")
        
        # Filter by family if specified
        if request.family:
            if request.family not in all_families:
                raise HTTPException(status_code=404, detail=f"Family not found: {request.family}")
            families_to_search = {request.family: all_families[request.family]}
        else:
            families_to_search = all_families
        
        # Pre-normalize input symptoms once
        normalized_input = [normalize_text(s) for s in effective_symptoms]
        
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
                    normalized_input, effective_symptoms, string_presentations, rule
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
        
        # Check if we should query AI for additional suggestions
        # Query AI if: <5 tree results OR best score < 3.0
        should_query_ai = len(results) < 5 or (results and results[0].match_score < 3.0)
        
        if should_query_ai and AI_GENERATION_AVAILABLE:
            logging.info(f"Insufficient tree results ({len(results)}), querying AI for additional diagnoses")
            
            try:
                ai_diagnoses = await query_ai_for_diagnoses(effective_symptoms, request.age, request.sex)
                
                # Get set of existing diagnosis IDs from tree results
                existing_ids = {r.rule_id.upper() for r in results}
                
                # Add AI suggestions that aren't already in tree results
                for ai_dx in ai_diagnoses:
                    diagnosis_name = ai_dx.get('diagnosis', '')
                    # Create simple ID from diagnosis name
                    dx_id = diagnosis_name.upper().replace(' ', '-').replace(',', '')
                    
                    # Skip if we already have this from trees
                    if dx_id in existing_ids or diagnosis_name.upper() in existing_ids:
                        continue
                    
                    # Map likelihood to score
                    likelihood = ai_dx.get('likelihood', 'moderate').lower()
                    if likelihood == 'high':
                        ai_score = 4.0
                    elif likelihood == 'moderate':
                        ai_score = 2.5
                    else:
                        ai_score = 1.5

                    display_label = f"(AI-suggested, unverified) {diagnosis_name}" if diagnosis_name else diagnosis_name
                    
                    # Create diagnosis match from AI suggestion
                    ai_match = DiagnosisMatch(
                        rule_id=dx_id,
                        label=display_label,
                        family=ai_dx.get('specialty', 'general'),
                        match_score=ai_score,
                        matched_presentations=ai_dx.get('key_features', []),
                        all_presentations=[f"AI suggestion based on: {', '.join(effective_symptoms)}"],
                        icd10=ai_dx.get('icd10', []),
                        snomed=[],
                        sensitivity=None,
                        specificity=None,
                        clinical_pearls=None,
                        management=None,
                        tests=None,
                        referrals=None,
                        has_tree=False,
                        ai_suggested=True
                    )
                    
                    results.append(ai_match)
                
                # Re-sort after adding AI suggestions
                results.sort(key=lambda x: x.match_score, reverse=True)
                
                logging.info(f"Added {len(ai_diagnoses)} AI-suggested diagnoses")
            except Exception as e:
                logging.error(f"Failed to get AI diagnosis suggestions: {e}")
        
        # Return top 20 results
        top_results = results[:20]
        
        # Check if we should trigger AI tree generation (low/no results)
        ai_tree_info = None
        if AI_GENERATION_AVAILABLE and os.getenv("ENABLE_AI_GENERATION", "false").lower() == "true":
            # Trigger AI generation if:
            # 1. No results found, OR
            # 2. Best result has low confidence (score < 2.0)
            # 3. User has 2+ symptoms (enough context for AI)
            should_generate = (
                (len(top_results) == 0 or (top_results and top_results[0].match_score < 2.0))
                and len(effective_symptoms) >= 2
            )
            
            if should_generate:
                ai_tree_info = {
                    "generation_triggered": True,
                    "reason": "No high-confidence matches found",
                    "status": "pending",
                    "message": "AI is generating a diagnostic tree for your symptoms. This may take 30-60 seconds."
                }
                
                # Note: Actual generation happens via separate endpoint to avoid blocking
        
        response_data = SymptomSearchResponse(
            query_symptoms=effective_symptoms,
            total_results=len(top_results),
            results=top_results
        )
        
        # Add AI generation info if applicable
        if ai_tree_info:
            response_dict = response_data.dict()
            response_dict["ai_generation"] = ai_tree_info
            return response_dict
        
        return response_data
        
    except Exception as e:
        logging.error(f"Error in symptom search: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Symptom search error: {str(e)}")


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
                if not isinstance(presentation, str):
                    continue
                # Extract individual symptoms (simple approach: split by comma)
                parts = [p.strip() for p in presentation.split(',')]
                symptoms.update(parts)
    
    # Return sorted list (limit to 500 most common)
    sorted_symptoms = sorted(list(symptoms))[:500]
    
    return {
        "symptoms": sorted_symptoms,
        "total": len(sorted_symptoms)
    }


@router.post("/search/generate-tree")
async def generate_ai_tree(request: SymptomSearchRequest, background_tasks: BackgroundTasks):
    """
    Generate an AI decision tree for symptoms not covered by existing trees.
    
    This endpoint is called when symptom search returns no good matches.
    Tree generation happens asynchronously and is saved to pending review.
    """
    if not AI_GENERATION_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="AI tree generation is not available. Contact administrator."
        )
    
    if not os.getenv("ENABLE_AI_GENERATION", "false").lower() == "true":
        raise HTTPException(
            status_code=403,
            detail="AI tree generation is disabled"
        )
    
    if len(request.symptoms) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 symptoms required for AI tree generation"
        )
    
    # Log the generation request
    AuditLogger.log_security_event(
        "ai_tree_generation_requested",
        {
            "symptoms": request.symptoms,
            "symptom_count": len(request.symptoms),
            "patient_age": request.age,
            "patient_sex": request.sex
        },
        severity="INFO"
    )
    
    try:
        # Choose provider (prefer Claude for medical content)
        provider = os.getenv("AI_PROVIDER", "claude")
        
        # Build context from patient info
        additional_context = ""
        if request.age:
            additional_context += f"Patient age: {request.age} years. "
        if request.sex:
            additional_context += f"Patient sex: {request.sex}. "
        
        # Generate tree
        generator = AITreeGenerator(provider=provider)
        tree_data = await generator.generate_tree(
            symptoms=request.symptoms,
            additional_context=additional_context if additional_context else None,
            temperature=0.3  # Conservative for medical content
        )
        
        # Save to pending directory
        filepath = generator.save_tree(tree_data, status="pending")
        
        # Log successful generation
        AuditLogger.log_security_event(
            "ai_tree_generated",
            {
                "tree_id": tree_data["tree_id"],
                "symptoms": request.symptoms,
                "filepath": filepath,
                "provider": provider,
                "diagnosis": tree_data.get("diagnosis", {}).get("name", "Unknown")
            },
            severity="INFO"
        )
        
        return {
            "success": True,
            "tree_id": tree_data["tree_id"],
            "tree_data": tree_data,
            "status": "pending_review",
            "message": "Decision tree generated successfully. It will be available after medical review.",
            "disclaimer": "This diagnostic tree was generated by AI and is pending review by medical professionals. Use with caution and always consult a healthcare provider."
        }
        
    except Exception as e:
        # Log error
        AuditLogger.log_security_event(
            "ai_tree_generation_failed",
            {
                "symptoms": request.symptoms,
                "error": str(e)
            },
            severity="ERROR"
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate decision tree: {str(e)}"
        )


@router.get("/search/ai-trees/pending")
async def get_pending_trees():
    """Get list of AI-generated trees pending review (admin only)"""
    if not AI_GENERATION_AVAILABLE:
        return {"trees": [], "count": 0}
    
    try:
        generator = AITreeGenerator()
        trees = generator.load_pending_trees()
        
        # Return summary (not full trees - they can be large)
        summaries = []
        for tree in trees:
            summaries.append({
                "tree_id": tree["tree_id"],
                "name": tree["name"],
                "chief_complaint": tree.get("chief_complaint", ""),
                "generated_at": tree.get("metadata", {}).get("generated_at", ""),
                "source_symptoms": tree.get("metadata", {}).get("source_symptoms", []),
                "specialty": tree.get("specialty", "")
            })
        
        return {
            "trees": summaries,
            "count": len(summaries)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load pending trees: {str(e)}"
        )


@router.get("/search/warmup")
async def warmup_cache():
    """
    Warmup endpoint to preload diagnostic trees after deployment.
    Call this after deployment to avoid timeout on first user request.
    """
    try:
        start_time = time.time()
        logging.info("Warmup: Loading diagnostic trees...")
        
        families = load_all_families()
        
        load_time = time.time() - start_time
        total_trees = sum(len(rules) for rules in families.values())
        
        return {
            "success": True,
            "families_loaded": len(families),
            "total_trees": total_trees,
            "load_time_seconds": round(load_time, 2),
            "message": f"Cache warmed up successfully in {load_time:.2f}s"
        }
    except Exception as e:
        logging.error(f"Warmup failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Warmup failed: {str(e)}"
        )
