#!/usr/bin/env python3
"""
Real-world test: Young adult with respiratory symptoms should not get pediatric croup
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.symptom_search import load_all_families, apply_filters, normalize_text, calculate_match_score_optimized

def test_croup_adult_patient():
    """Test that croup doesn't appear for adult patient with cough"""
    
    print("=" * 80)
    print("Simulating Croup Query for Adult Patient")
    print("=" * 80)
    
    # Load all diagnostic trees
    print("\n1. Loading diagnostic trees...")
    all_families = load_all_families()
    print(f"   ✓ Loaded diagnostic trees")
    
    # Simulate adult patient with upper respiratory symptoms
    patient_symptoms = ["cough", "difficulty breathing", "stridor"]
    patient_age = 28  # Adult
    
    print(f"\n2. Patient Information:")
    print(f"   Age: {patient_age} (Adult)")
    print(f"   Symptoms: {', '.join(patient_symptoms)}")
    
    # Pre-normalize input symptoms
    normalized_input = [normalize_text(s) for s in patient_symptoms]
    
    # Search and score all rules
    print(f"\n3. Running symptom search...")
    results = []
    
    for family_name, rules in all_families.items():
        # Apply filters (AGE FILTERING HAPPENS HERE)
        filtered_rules = apply_filters(rules, patient_age, None)
        
        for rule in filtered_rules:
            presentations = rule.get('presentations', [])
            string_presentations = [p for p in presentations if isinstance(p, str)]
            
            if not string_presentations:
                continue
            
            score, matched_presentations = calculate_match_score_optimized(
                normalized_input, patient_symptoms, string_presentations, rule
            )
            
            if score > 0:
                results.append({
                    'id': rule.get('id', ''),
                    'label': rule.get('label', ''),
                    'family': family_name,
                    'score': round(score, 2),
                    'matched': matched_presentations,
                    'age_max': rule.get('age_max', '')
                })
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"   Found {len(results)} matching diagnoses")
    
    # Check if croup appears
    print(f"\n4. Checking for Croup in results...")
    croup_found = False
    croup_result = None
    
    for result in results:
        if 'CROUP' in result['id'].upper() or 'CROUP' in result['label'].upper():
            croup_found = True
            croup_result = result
            break
    
    if croup_found:
        print(f"   ❌ PROBLEM FOUND: Croup appeared in results for adult patient!")
        print(f"      ID: {croup_result['id']}")
        print(f"      Label: {croup_result['label']}")
        print(f"      Score: {croup_result['score']}")
        print(f"      Age Max: {croup_result['age_max']}")
    else:
        print(f"   ✓ CORRECT: Croup was filtered out for adult patient")
    
    # Show top 10 results
    print(f"\n5. Top 10 Matching Diagnoses:")
    for i, result in enumerate(results[:10], 1):
        age_indicator = ""
        if result['age_max']:
            age_indicator = f" [age_max: {result['age_max']}]"
        print(f"   {i}. {result['label']}{age_indicator}")
        print(f"      Score: {result['score']} | Family: {result['family']}")
        print(f"      Matched: {', '.join(result['matched'][:3])}...")
        print()
    
    # Summary
    print("=" * 80)
    print("RESULT:")
    print("=" * 80)
    
    if not croup_found:
        print("✅ SUCCESS: Adult patient with respiratory symptoms does NOT get Croup")
        print("  The age-based filtering is working correctly!")
        return True
    else:
        print("❌ FAILURE: Adult patient STILL getting pediatric Croup diagnosis")
        return False

def test_sarcopenia_young_patient():
    """Test that sarcopenia doesn't appear for young patient"""
    
    print("\n\n" + "=" * 80)
    print("Simulating Sarcopenia Query for Young Patient")
    print("=" * 80)
    
    # Load all diagnostic trees
    print("\n1. Loading diagnostic trees...")
    all_families = load_all_families()
    
    # Simulate young patient with muscle weakness
    patient_symptoms = ["muscle weakness", "fatigue", "weight loss"]
    patient_age = 30  # Young adult
    
    print(f"\n2. Patient Information:")
    print(f"   Age: {patient_age} (Young Adult)")
    print(f"   Symptoms: {', '.join(patient_symptoms)}")
    
    # Pre-normalize input symptoms
    normalized_input = [normalize_text(s) for s in patient_symptoms]
    
    # Search and score all rules
    print(f"\n3. Running symptom search...")
    results = []
    
    for family_name, rules in all_families.items():
        filtered_rules = apply_filters(rules, patient_age, None)
        
        for rule in filtered_rules:
            presentations = rule.get('presentations', [])
            string_presentations = [p for p in presentations if isinstance(p, str)]
            
            if not string_presentations:
                continue
            
            score, matched_presentations = calculate_match_score_optimized(
                normalized_input, patient_symptoms, string_presentations, rule
            )
            
            if score > 0:
                results.append({
                    'id': rule.get('id', ''),
                    'label': rule.get('label', ''),
                    'family': family_name,
                    'score': round(score, 2),
                    'age_min': rule.get('age_min', '')
                })
    
    results.sort(key=lambda x: x['score'], reverse=True)
    print(f"   Found {len(results)} matching diagnoses")
    
    # Check if sarcopenia appears
    print(f"\n4. Checking for Sarcopenia in results...")
    sarcopenia_found = any('SARCOPENIA' in r['id'].upper() for r in results)
    
    if sarcopenia_found:
        print(f"   ❌ PROBLEM: Sarcopenia appeared for young patient!")
    else:
        print(f"   ✓ CORRECT: Sarcopenia filtered out for young patient")
    
    print("\n" + "=" * 80)
    print("RESULT:")
    print("=" * 80)
    
    if not sarcopenia_found:
        print("✅ SUCCESS: Young patient does NOT get geriatric Sarcopenia")
        return True
    else:
        print("❌ FAILURE: Young patient getting geriatric diagnosis")
        return False

if __name__ == '__main__':
    test1 = test_croup_adult_patient()
    test2 = test_sarcopenia_young_patient()
    
    print("\n\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    if test1 and test2:
        print("✅ ALL TESTS PASSED")
        print("\nAge-based filtering prevents:")
        print("  - Adults from getting pediatric diagnoses (croup, etc.)")
        print("  - Young patients from getting geriatric diagnoses (sarcopenia, etc.)")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)
