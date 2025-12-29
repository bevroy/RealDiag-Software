#!/usr/bin/env python3
"""
Test script for enhanced symptom search that includes clinical cases without trees.
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from services.symptom_search import (
    load_clinical_cases,
    search_clinical_cases,
    normalize_text
)

def test_load_cases():
    """Test loading clinical cases."""
    print("=" * 60)
    print("TEST 1: Load Clinical Cases")
    print("=" * 60)
    
    cases = load_clinical_cases()
    print(f"✓ Loaded {len(cases)} clinical cases")
    
    if cases:
        # Show first case structure
        first_case = cases[0]
        print(f"\nFirst case example:")
        print(f"  Case ID: {first_case.get('case_id')}")
        print(f"  Title: {first_case.get('title')}")
        print(f"  Diagnosis: {first_case.get('correct_diagnosis')}")
        print(f"  Specialty: {first_case.get('specialty')}")
        print(f"  Presentation: {first_case.get('presentation')[:100]}...")
    
    return cases

def test_search_cases():
    """Test searching clinical cases by symptoms."""
    print("\n" + "=" * 60)
    print("TEST 2: Search Clinical Cases by Symptoms")
    print("=" * 60)
    
    # Test with symptoms that should match some cases
    test_symptoms = ["chest pain", "shortness of breath"]
    print(f"\nSearching for symptoms: {test_symptoms}")
    
    normalized = [normalize_text(s) for s in test_symptoms]
    results = search_clinical_cases(normalized, test_symptoms)
    
    print(f"\n✓ Found {len(results)} matching diagnoses")
    
    # Show top 5 results
    sorted_results = sorted(results.items(), key=lambda x: x[1]['score'], reverse=True)
    for i, (diagnosis_id, data) in enumerate(sorted_results[:5], 1):
        print(f"\n{i}. {diagnosis_id} (Score: {data['score']:.2f})")
        print(f"   Specialty: {data['specialty']}")
        print(f"   Matched symptoms: {data['matched_presentations']}")
        print(f"   Case examples: {', '.join(data['case_ids'])}")
        if data['all_presentations']:
            print(f"   Presentation: {data['all_presentations'][0][:80]}...")
    
    return results

def test_no_tree_diagnoses():
    """Test finding diagnoses that don't have decision trees."""
    print("\n" + "=" * 60)
    print("TEST 3: Find Diagnoses Without Trees")
    print("=" * 60)
    
    cases = load_clinical_cases()
    all_diagnoses = set()
    
    for case in cases:
        dx = case.get('correct_diagnosis')
        if dx:
            all_diagnoses.add(dx)
    
    print(f"\n✓ Found {len(all_diagnoses)} unique diagnoses in case database")
    print(f"\nExample diagnoses:")
    for i, dx in enumerate(list(all_diagnoses)[:10], 1):
        print(f"  {i}. {dx}")
    
    # Check if trees directory exists and count trees
    trees_dir = Path(__file__).parent / "backend" / "trees"
    if trees_dir.exists():
        tree_files = list(trees_dir.glob("*.yml"))
        print(f"\n✓ Found {len(tree_files)} decision tree files")
        
        # Load tree IDs
        import yaml
        tree_ids = set()
        for tree_file in tree_files[:20]:  # Sample first 20
            try:
                with open(tree_file) as f:
                    tree_data = yaml.safe_load(f)
                    if tree_data:
                        tree_ids.add(tree_data.get('tree_id', tree_file.stem))
            except:
                pass
        
        print(f"Sample tree IDs: {list(tree_ids)[:5]}")
        
        # Check overlap
        diagnoses_without_trees = all_diagnoses - tree_ids
        print(f"\n✓ Diagnoses in cases but potentially without trees: {len(diagnoses_without_trees)}")
        if diagnoses_without_trees:
            print(f"Examples: {list(diagnoses_without_trees)[:5]}")

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("ENHANCED SYMPTOM SEARCH TEST SUITE")
    print("=" * 60)
    
    try:
        # Test 1: Load cases
        cases = test_load_cases()
        
        if not cases:
            print("\n❌ ERROR: No cases loaded. Cannot continue tests.")
            return
        
        # Test 2: Search cases
        results = test_search_cases()
        
        # Test 3: Check for diagnoses without trees
        test_no_tree_diagnoses()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
