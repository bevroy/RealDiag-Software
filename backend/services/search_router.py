"""
Diagnosis Search Router - Comprehensive clinical reference search
Provides detailed clinical information including presentations, workup, treatment, codes, and remedies
"""

from fastapi import APIRouter, Query
from typing import List, Dict, Optional
from pathlib import Path
import yaml
import sys

# Add data directory to path for ICD-10 and SNOMED databases
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "data"))
try:
    from icd10_codes import ICD10_DATABASE, get_diagnosis_from_icd10
except ImportError:
    ICD10_DATABASE = {}
    def get_diagnosis_from_icd10(code: str) -> str:
        return None

try:
    from snomed_codes import SNOMED_DATABASE, get_diagnosis_from_snomed, get_snomed_codes_for_diagnosis
except ImportError:
    SNOMED_DATABASE = {}
    def get_diagnosis_from_snomed(code: str) -> str:
        return None
    def get_snomed_codes_for_diagnosis(diagnosis_name: str) -> list:
        return []

router = APIRouter(prefix="/api", tags=["search"])

TREES_PATH = Path(__file__).resolve().parents[1] / "trees"

def _extract_clinical_info(tree_data: Dict) -> Dict:
    """Extract comprehensive clinical information from a decision tree"""
    
    # Basic metadata
    tree_id = tree_data.get('tree_id', '')
    name = tree_data.get('name', '')
    description = tree_data.get('description', '')
    icd10 = tree_data.get('icd10', '')
    family = tree_data.get('family', '')
    specialty = tree_data.get('specialty', '')
    chief_complaint = tree_data.get('chief_complaint', '')
    urgency = tree_data.get('urgency', '')
    
    # Collect clinical information from nodes
    clinical_pearls = set()
    presentations = set()
    workup_tests = set()
    treatments = set()
    referrals = set()
    snomed_codes = set()
    homeopathic_remedies = set()
    
    # Parse nodes for clinical details
    nodes = tree_data.get('nodes', [])
    if isinstance(nodes, list):
        for node in nodes:
            if not isinstance(node, dict):
                continue
                
            # Clinical pearls
            pearls = node.get('clinical_pearls', [])
            if pearls:
                for pearl in pearls:
                    clinical_pearls.add(str(pearl))
            
            # Presentations/symptoms
            when_conditions = node.get('when', {})
            if when_conditions:
                symptoms_any = when_conditions.get('symptoms_contains_any', [])
                if symptoms_any:
                    for symptom in symptoms_any:
                        presentations.add(str(symptom))
            
            # Workup/tests
            tests = node.get('tests', [])
            if tests:
                for test in tests:
                    workup_tests.add(str(test))
            
            # Treatments/management
            management = node.get('management', [])
            if management:
                for tx in management:
                    treatments.add(str(tx))
            
            treatment = node.get('treatment', [])
            if treatment:
                for tx in treatment:
                    treatments.add(str(tx))
            
            # Referrals
            refs = node.get('referrals', [])
            if refs:
                for ref in refs:
                    referrals.add(str(ref))
            
            # Homeopathic remedies
            homeopathy = node.get('homeopathy', [])
            if homeopathy:
                for remedy in homeopathy:
                    if isinstance(remedy, dict):
                        remedy_name = remedy.get('remedy', '')
                        indications = remedy.get('indications', '')
                        if remedy_name:
                            homeopathic_remedies.add(f"{remedy_name}: {indications}" if indications else remedy_name)
                    else:
                        homeopathic_remedies.add(str(remedy))
    
    # Add chief complaint to presentations
    if chief_complaint:
        for complaint in chief_complaint.split(','):
            presentations.add(complaint.strip())
    
    # Enrich with SNOMED codes if available
    if name and not snomed_codes:
        snomed_matches = get_snomed_codes_for_diagnosis(name)
        if snomed_matches:
            snomed_codes.update(snomed_matches)
    
    return {
        'tree_id': tree_id,
        'name': name,
        'description': description,
        'icd10': icd10,
        'snomed': list(snomed_codes) if snomed_codes else [],
        'family': family,
        'specialty': specialty,
        'urgency': urgency,
        'clinical_pearls': sorted(list(clinical_pearls)),
        'presentations': sorted(list(presentations)),
        'workup': sorted(list(workup_tests)),
        'treatment': sorted(list(treatments)),
        'referrals': sorted(list(referrals)),
        'homeopathic_remedies': sorted(list(homeopathic_remedies))
    }

@router.get("/search")
async def search_diagnoses(
    q: str = Query(..., min_length=1, description="Search query (diagnosis name or ICD-10 code)")
) -> Dict:
    """
    Search for diagnoses and return comprehensive clinical information.
    
    Returns: Clinical pearls, presentations, diagnostic workup, treatment recommendations,
    ICD-10/SNOMED codes, and homeopathic remedies.
    """
    query = q.strip().upper()
    results = []
    
    # Search through all tree files
    if not TREES_PATH.exists():
        return {
            'query': q,
            'count': 0,
            'results': []
        }
    
    for tree_file in TREES_PATH.glob("*.yml"):
        try:
            with tree_file.open("r", encoding="utf-8") as f:
                tree_data = yaml.safe_load(f) or {}
            
            if not tree_data:
                continue
            
            # Check if query matches
            name = tree_data.get('name', '').upper()
            description = tree_data.get('description', '').upper()
            icd10 = str(tree_data.get('icd10', '')).upper()
            tree_id = tree_data.get('tree_id', '').upper()
            chief_complaint = tree_data.get('chief_complaint', '').upper()
            
            # Check SNOMED database for match
            snomed_diagnosis = get_diagnosis_from_snomed(query)
            
            # Calculate match score for relevance ranking
            match_score = 0
            matched = False
            
            # Exact name match (highest priority)
            if query == name:
                match_score = 1000
                matched = True
            # Name starts with query
            elif name.startswith(query):
                match_score = 500
                matched = True
            # Name contains query as whole word
            elif f" {query} " in f" {name} " or f" {query}," in name:
                match_score = 300
                matched = True
            # Name contains query
            elif query in name:
                match_score = 200
                matched = True
            # Exact ICD-10 match
            elif query == icd10:
                match_score = 900
                matched = True
            # SNOMED code match
            elif snomed_diagnosis and snomed_diagnosis.upper() in name:
                match_score = 850
                matched = True
            # ICD-10 starts with query
            elif icd10.startswith(query):
                match_score = 400
                matched = True
            # Tree ID match
            elif query in tree_id:
                match_score = 250
                matched = True
            # Chief complaint contains query
            elif query in chief_complaint:
                match_score = 150
                matched = True
            # Description contains query (lowest priority)
            elif query in description:
                match_score = 50
                matched = True
            
            if matched:
                # Extract comprehensive clinical information
                clinical_info = _extract_clinical_info(tree_data)
                clinical_info['match_score'] = match_score
                results.append(clinical_info)
                
        except Exception as e:
            print(f"Error processing {tree_file}: {e}")
            continue
    
    # Deduplicate by diagnosis name - keep only highest scoring match for each unique diagnosis
    unique_results = {}
    for result in results:
        diagnosis_name = result.get('name', '').upper()
        current_score = result.get('match_score', 0)
        
        if diagnosis_name not in unique_results:
            unique_results[diagnosis_name] = result
        else:
            # Keep the one with higher score
            existing_score = unique_results[diagnosis_name].get('match_score', 0)
            if current_score > existing_score:
                unique_results[diagnosis_name] = result
    
    # Convert back to list and sort by match score (highest first), then by name
    results = list(unique_results.values())
    results.sort(key=lambda x: (-x.get('match_score', 0), x.get('name', '')))
    
    # If no results from trees, search ICD-10 database
    if len(results) == 0 and ICD10_DATABASE:
        # Check if query is an ICD-10 code
        icd10_diagnosis = get_diagnosis_from_icd10(query)
        if icd10_diagnosis:
            results.append({
                'tree_id': '',
                'name': icd10_diagnosis,
                'description': f'ICD-10: {query}',
                'icd10': query,
                'snomed': [],
                'family': 'General',
                'specialty': 'General Medicine',
                'urgency': '',
                'clinical_pearls': [],
                'presentations': [],
                'workup': [],
                'treatment': ['Consult clinical guidelines for specific treatment recommendations'],
                'referrals': [],
                'homeopathic_remedies': [],
                'match_score': 900
            })
        else:
            # Search ICD-10 database by diagnosis name
            for icd_code, diagnosis_name in ICD10_DATABASE.items():
                if query in diagnosis_name.upper():
                    # Calculate match score
                    if query == diagnosis_name.upper():
                        score = 1000
                    elif diagnosis_name.upper().startswith(query):
                        score = 500
                    elif f" {query} " in f" {diagnosis_name.upper()} ":
                        score = 300
                    else:
                        score = 200
                    
                    results.append({
                        'tree_id': '',
                        'name': diagnosis_name,
                        'description': f'ICD-10: {icd_code}',
                        'icd10': icd_code,
                        'snomed': [],
                        'family': 'General',
                        'specialty': 'General Medicine',
                        'urgency': '',
                        'clinical_pearls': [],
                        'presentations': [],
                        'workup': [],
                        'treatment': ['Consult clinical guidelines for specific treatment recommendations'],
                        'referrals': [],
                        'homeopathic_remedies': [],
                        'match_score': score
                    })
            
            # Deduplicate and sort ICD-10 results
            unique_icd = {}
            for result in results:
                diagnosis_name = result.get('name', '').upper()
                current_score = result.get('match_score', 0)
                
                if diagnosis_name not in unique_icd:
                    unique_icd[diagnosis_name] = result
                else:
                    existing_score = unique_icd[diagnosis_name].get('match_score', 0)
                    if current_score > existing_score:
                        unique_icd[diagnosis_name] = result
            
            results = list(unique_icd.values())
            results.sort(key=lambda x: (-x.get('match_score', 0), x.get('name', '')))
    
    # If still no results, search SNOMED database
    if len(results) == 0 and SNOMED_DATABASE:
        # Check if query is a SNOMED code
        snomed_diagnosis = get_diagnosis_from_snomed(query)
        if snomed_diagnosis:
            results.append({
                'tree_id': '',
                'name': snomed_diagnosis,
                'description': f'SNOMED CT: {query}',
                'icd10': '',
                'snomed': [query],
                'family': 'General',
                'specialty': 'General Medicine',
                'urgency': '',
                'clinical_pearls': [],
                'presentations': [],
                'workup': [],
                'treatment': ['Consult clinical guidelines for specific treatment recommendations'],
                'referrals': [],
                'homeopathic_remedies': [],
                'match_score': 850
            })
        else:
            # Search SNOMED database by diagnosis name
            for snomed_code, diagnosis_name in SNOMED_DATABASE.items():
                if query in diagnosis_name.upper():
                    # Calculate match score
                    if query == diagnosis_name.upper():
                        score = 1000
                    elif diagnosis_name.upper().startswith(query):
                        score = 500
                    elif f" {query} " in f" {diagnosis_name.upper()} ":
                        score = 300
                    else:
                        score = 200
                    
                    results.append({
                        'tree_id': '',
                        'name': diagnosis_name,
                        'description': f'SNOMED CT: {snomed_code}',
                        'icd10': '',
                        'snomed': [snomed_code],
                        'family': 'General',
                        'specialty': 'General Medicine',
                        'urgency': '',
                        'clinical_pearls': [],
                        'presentations': [],
                        'workup': [],
                        'treatment': ['Consult clinical guidelines for specific treatment recommendations'],
                        'referrals': [],
                        'homeopathic_remedies': [],
                        'match_score': score
                    })
            
            # Deduplicate and sort SNOMED results
            unique_snomed = {}
            for result in results:
                diagnosis_name = result.get('name', '').upper()
                current_score = result.get('match_score', 0)
                
                if diagnosis_name not in unique_snomed:
                    unique_snomed[diagnosis_name] = result
                else:
                    existing_score = unique_snomed[diagnosis_name].get('match_score', 0)
                    if current_score > existing_score:
                        unique_snomed[diagnosis_name] = result
            
            results = list(unique_snomed.values())
            results.sort(key=lambda x: (-x.get('match_score', 0), x.get('name', '')))
    
    return {
        'query': q,
        'count': len(results),
        'results': results
    }


@router.get("/search/by-family")
async def search_by_family(
    family: str = Query(..., description="Medical family/specialty")
) -> Dict:
    """
    Get all diagnoses in a specific medical family with full clinical details.
    """
    family_query = family.strip().upper()
    results = []
    
    if not TREES_PATH.exists():
        return {
            'family': family,
            'count': 0,
            'results': []
        }
    
    for tree_file in TREES_PATH.glob("*.yml"):
        try:
            with tree_file.open("r", encoding="utf-8") as f:
                tree_data = yaml.safe_load(f) or {}
            
            if not tree_data:
                continue
            
            tree_family = tree_data.get('family', '').upper()
            
            if family_query in tree_family:
                clinical_info = _extract_clinical_info(tree_data)
                results.append(clinical_info)
                
        except Exception as e:
            print(f"Error processing {tree_file}: {e}")
            continue
    
    results.sort(key=lambda x: x.get('name', ''))
    
    return {
        'family': family,
        'count': len(results),
        'results': results
    }


@router.get("/search/families")
async def get_families() -> Dict:
    """
    Get list of all medical families/specialties available.
    """
    families = set()
    
    if not TREES_PATH.exists():
        return {'families': []}
    
    for tree_file in TREES_PATH.glob("*.yml"):
        try:
            with tree_file.open("r", encoding="utf-8") as f:
                tree_data = yaml.safe_load(f) or {}
            
            family = tree_data.get('family', '')
            if family:
                families.add(family)
                
        except Exception as e:
            continue
    
    return {
        'families': sorted(list(families))
    }
