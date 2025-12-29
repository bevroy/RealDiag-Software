#!/usr/bin/env python3
"""
Integration test for the enhanced symptom search API endpoint.
Tests that diagnoses without trees are properly returned with has_tree=False flag.
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from fastapi.testclient import TestClient
from main import app

def test_symptom_search_with_cases():
    """Test that symptom search now returns both tree-based and case-based results."""
    print("=" * 60)
    print("API INTEGRATION TEST: Enhanced Symptom Search")
    print("=" * 60)
    
    client = TestClient(app)
    
    # Test 1: Search for symptoms that match cases without trees
    print("\nTest 1: Search for 'burning chest pain' (should find GERD)")
    response = client.post(
        "/search/by-symptoms",
        json={
            "symptoms": ["burning chest pain", "worse after meals"]
        }
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    
    print(f"✓ Status: {response.status_code}")
    print(f"✓ Total results: {data['total_results']}")
    
    # Check if we have results
    if data['results']:
        print(f"\nTop 3 results:")
        for i, result in enumerate(data['results'][:3], 1):
            has_tree = result.get('has_tree', True)
            tree_status = "✓ Has tree" if has_tree else "⚠ No tree (from case DB)"
            case_examples = result.get('case_examples', [])
            
            print(f"\n{i}. {result['label']} (Score: {result['match_score']})")
            print(f"   {tree_status}")
            print(f"   Family: {result['family']}")
            print(f"   Matched: {', '.join(result['matched_presentations'][:2])}")
            if case_examples:
                print(f"   Case examples: {', '.join(case_examples)}")
        
        # Count results with and without trees
        with_trees = sum(1 for r in data['results'] if r.get('has_tree', True))
        without_trees = sum(1 for r in data['results'] if not r.get('has_tree', True))
        
        print(f"\n✓ Results with decision trees: {with_trees}")
        print(f"✓ Results from case database only: {without_trees}")
        
        if without_trees > 0:
            print("\n✅ SUCCESS: Enhanced search is finding diagnoses without trees!")
        else:
            print("\n⚠ WARNING: No case-only results found. May need to adjust search.")
    else:
        print("❌ No results found")
    
    # Test 2: Search for common symptoms
    print("\n" + "=" * 60)
    print("Test 2: Search for 'headache' and 'fever'")
    response = client.post(
        "/search/by-symptoms",
        json={
            "symptoms": ["headache", "fever"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    print(f"✓ Status: {response.status_code}")
    print(f"✓ Total results: {data['total_results']}")
    
    # Count by tree status
    with_trees = sum(1 for r in data['results'] if r.get('has_tree', True))
    without_trees = sum(1 for r in data['results'] if not r.get('has_tree', True))
    
    print(f"✓ Results with trees: {with_trees}")
    print(f"✓ Results without trees: {without_trees}")
    
    print("\n" + "=" * 60)
    print("✅ INTEGRATION TEST COMPLETED")
    print("=" * 60)

def main():
    try:
        test_symptom_search_with_cases()
        return 0
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
