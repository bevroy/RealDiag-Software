"""
Search Router - Search decision trees by diagnosis name or ICD-10 code
"""

from fastapi import APIRouter, Query
from typing import List, Dict, Optional
import re
from backend.services.decision_tree_engine import DecisionTreeEngine

router = APIRouter(prefix="/api", tags=["search"])

# Initialize the decision tree engine
engine = DecisionTreeEngine()

@router.get("/search")
async def search_diagnoses(
    q: str = Query(..., min_length=1, description="Search query (diagnosis name or ICD-10 code)")
) -> Dict:
    """
    Search for diagnoses by name or ICD-10 code.
    
    Returns matching decision trees with their metadata.
    """
    query = q.strip().upper()
    results = []
    
    # Load all trees and their metadata
    for tree_path, tree_data in engine.trees.items():
        # Extract metadata
        tree_id = tree_data.get('tree_id', '')
        name = tree_data.get('name', '')
        icd10 = tree_data.get('icd10', '')
        description = tree_data.get('description', '')
        family = tree_data.get('family', '')
        specialty = tree_data.get('specialty', '')
        chief_complaint = tree_data.get('chief_complaint', '')
        
        # Check if query matches
        matches = False
        match_type = None
        
        # Check ICD-10 code (exact or partial match)
        if icd10 and query in str(icd10).upper():
            matches = True
            match_type = 'icd10'
        
        # Check diagnosis name
        elif name and query in name.upper():
            matches = True
            match_type = 'name'
        
        # Check description
        elif description and query in description.upper():
            matches = True
            match_type = 'description'
        
        # Check chief complaint
        elif chief_complaint and query in chief_complaint.upper():
            matches = True
            match_type = 'chief_complaint'
        
        # Check tree ID (for code-based searches like "CARD-" or "NEURO-")
        elif tree_id and query in tree_id.upper():
            matches = True
            match_type = 'tree_id'
        
        if matches:
            results.append({
                'tree_id': tree_id,
                'name': name,
                'icd10': icd10,
                'description': description,
                'family': family,
                'specialty': specialty,
                'chief_complaint': chief_complaint,
                'match_type': match_type
            })
    
    # Sort results: exact ICD-10 matches first, then by name
    def sort_key(item):
        if item['match_type'] == 'icd10':
            # Exact matches first
            if item['icd10'] and item['icd10'].upper() == query:
                return (0, item['name'])
            return (1, item['name'])
        elif item['match_type'] == 'name':
            return (2, item['name'])
        else:
            return (3, item['name'])
    
    results.sort(key=sort_key)
    
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
    Get all decision trees in a specific medical family.
    """
    family_query = family.strip().upper()
    results = []
    
    for tree_path, tree_data in engine.trees.items():
        tree_family = tree_data.get('family', '').upper()
        
        if family_query in tree_family:
            results.append({
                'tree_id': tree_data.get('tree_id', ''),
                'name': tree_data.get('name', ''),
                'icd10': tree_data.get('icd10', ''),
                'description': tree_data.get('description', ''),
                'family': tree_data.get('family', ''),
                'specialty': tree_data.get('specialty', ''),
                'chief_complaint': tree_data.get('chief_complaint', '')
            })
    
    results.sort(key=lambda x: x['name'])
    
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
    
    for tree_path, tree_data in engine.trees.items():
        family = tree_data.get('family', '')
        if family:
            families.add(family)
    
    return {
        'families': sorted(list(families))
    }
