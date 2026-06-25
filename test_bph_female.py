#!/usr/bin/env python3
"""
Real-world test: Female patient with urinary symptoms should NOT get BPH
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.symptom_search import load_all_families, apply_filters, normalize_text, calculate_match_score_optimized

def test_bph_female_patient():
    """Test that BPH doesn't appear for female patient with urinary symptoms"""
    
    print("=" * 80)
    print("Simulating BPH Query for Female Patient")
    print("=" * 80)
    
    # Load all diagnostic trees
    print("\n1. Loading diagnostic trees...")
    all_families = load_all_families()
    print(f"   ✓ Loaded diagnostic trees")
    
    # Simulate female patient with urinary symptoms typical of BPH
    patient_symptoms = ["frequency", "urgency", "nocturia", "urinary hesitancy", "weak stream"]
    patient_age = 55
    patient_sex = "F"
    
    print(f"\n2. Patient Information:")
    print(f"   Age: {patient_age}")
    print(f"   Sex: {patient_sex} (Female)")
    print(f"   Symptoms: {', '.join(patient_symptoms)}")
    
    # Pre-normalize input symptoms
    normalized_input = [normalize_text(s) for s in patient_symptoms]
    
    # Search and score all rules
    print(f"\n3. Running symptom search with sex filter...")
    results = []
    
    for family_name, rules in all_families.items():
        # Apply filters (SEX FILTERING HAPPENS HERE)
        filtered_rules = apply_filters(rules, patient_age, patient_sex)
        
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
                    'applies_to': rule.get('applies_to', '')
                })
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"   Found {len(results)} matching diagnoses")
    
    # Check if BPH appears
    print(f"\n4. Checking for BPH in results...")
    bph_found = False
    bph_result = None
    
    for result in results:
        if 'BPH' in result['id'].upper() or 'PROSTATIC' in result['id'].upper() or \
           'PROSTATIC' in result['label'].upper() or 'BPH' in result['label'].upper():
            bph_found = True
            bph_result = result
            break
    
    if bph_found:
        print(f"   ❌ PROBLEM FOUND: BPH appeared in results for female patient!")
        print(f"      ID: {bph_result['id']}")
        print(f"      Label: {bph_result['label']}")
        print(f"      Score: {bph_result['score']}")
        print(f"      Applies to: {bph_result['applies_to']}")
    else:
        print(f"   ✓ CORRECT: BPH was filtered out for female patient")
    
    # Check for any male-only conditions
    print(f"\n5. Checking for other male-only conditions...")
    male_conditions = []
    for result in results[:20]:  # Check top 20
        if result['applies_to'] == 'male':
            male_conditions.append(f"{result['label']} (applies_to: male)")
        
        # Check for male-specific keywords
        rule_text = f"{result['id']} {result['label']}".upper()
        male_keywords = ['PROSTAT', 'TESTIC', 'PENILE', 'ERECTILE', 'EPIDIDYM', 'ORCHITIS']
        for keyword in male_keywords:
            if keyword in rule_text:
                male_conditions.append(f"{result['label']} (contains '{keyword}')")
                break
    
    if male_conditions:
        print(f"   ⚠️  WARNING: Found {len(male_conditions)} male-only conditions in top results:")
        for cond in male_conditions[:5]:
            print(f"      - {cond}")
    else:
        print(f"   ✓ No male-only conditions in results")
    
    # Show top 10 results
    print(f"\n6. Top 10 Matching Diagnoses for Female Patient:")
    for i, result in enumerate(results[:10], 1):
        applies_to_str = f" [applies_to: {result['applies_to']}]" if result['applies_to'] else ""
        print(f"   {i}. {result['label']}{applies_to_str}")
        print(f"      Score: {result['score']} | Family: {result['family']}")
        print(f"      Matched: {', '.join(result['matched'][:3])}...")
        print()
    
    # Summary
    print("=" * 80)
    print("RESULT:")
    print("=" * 80)
    
    if not bph_found and not male_conditions:
        print("✅ SUCCESS: Female patient does NOT get BPH or other male-only diagnoses")
        print("  The sex-based filtering is working correctly!")
        print("\n  Appropriate alternatives suggested:")
        for i, result in enumerate(results[:5], 1):
            print(f"    {i}. {result['label']} (Score: {result['score']})")
        return True
    else:
        print("❌ FAILURE: Sex-based filtering issues detected")
        if bph_found:
            print("  - BPH still appearing for female patient")
        if male_conditions:
            print("  - Other male-only conditions appearing for female patient")
        return False

if __name__ == '__main__':
    success = test_bph_female_patient()
    sys.exit(0 if success else 1)
