#!/usr/bin/env python3
"""Test script to verify homeopathy disease aliases work correctly."""

import sys
sys.path.insert(0, '/workspaces/RealDiag-Software/backend')

from services.homeopathy_service import HomeopathyService

def test_aliases():
    """Test that disease names return appropriate remedies."""
    service = HomeopathyService()
    
    test_cases = [
        # Cardiac conditions
        ("Myocardial Infarction", "cardiac"),
        ("Acute coronary syndrome", "cardiac"),
        ("Angina", "cardiac"),
        ("Heart attack", "cardiac"),
        
        # Neurological
        ("Migraine", "neurological"),
        ("Tension headache", "neurological"),
        
        # Respiratory
        ("Bronchitis", "respiratory"),
        ("Pneumonia", "respiratory"),
        ("Influenza", "respiratory"),
        ("Asthma", "respiratory"),
        
        # GI
        ("Gastritis", "GI"),
        ("IBS", "GI"),
        ("GERD", "GI"),
        
        # Musculoskeletal
        ("Arthritis", "musculoskeletal"),
        ("Sciatica", "musculoskeletal"),
        
        # Mental health
        ("Panic disorder", "mental health"),
        ("Anxiety disorder", "mental health"),
    ]
    
    print("Testing Homeopathy Disease Aliases\n" + "="*50)
    passed = 0
    failed = 0
    
    for condition, category in test_cases:
        remedies = service.get_remedies_for_condition(condition)
        if remedies:
            print(f"✓ {condition:30s} → {len(remedies)} remedies ({category})")
            passed += 1
        else:
            print(f"✗ {condition:30s} → NO REMEDIES ({category})")
            failed += 1
    
    print("\n" + "="*50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n✓ All tests passed! Disease aliases are working correctly.")
        return 0
    else:
        print(f"\n✗ {failed} tests failed. Some aliases may need attention.")
        return 1

if __name__ == "__main__":
    sys.exit(test_aliases())
