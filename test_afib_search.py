"""
Test for Atrial Fibrillation symptom search issue
"""

import sys
import json
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Import the symptom search module
from services.symptom_search import load_all_families, normalize_text, calculate_match_score

def test_afib_search():
    """Test that atrial fibrillation is found with the reported symptoms"""
    
    print("=" * 80)
    print("Testing Atrial Fibrillation Search")
    print("=" * 80)
    
    # User's reported symptoms
    test_symptoms = ["palpitations", "dizziness", "irregular pulse"]
    
    print(f"\nInput Symptoms: {test_symptoms}")
    print("-" * 80)
    
    # Load all diagnostic trees
    print("\n1. Loading diagnostic trees...")
    all_families = load_all_families()
    total_trees = sum(len(rules) for rules in all_families.values())
    print(f"   ✓ Loaded {total_trees} diagnostic trees across {len(all_families)} families")
    
    # Find atrial fibrillation specifically
    print("\n2. Looking for Atrial Fibrillation tree...")
    afib_tree = None
    
    for family_name, rules in all_families.items():
        for rule in rules:
            if 'ATRIAL-FIBRILLATION' in rule.get('id', '') or 'atrial fibrillation' in rule.get('label', '').lower():
                afib_tree = rule
                print(f"   ✓ Found: {rule.get('label')} (ID: {rule.get('id')})")
                print(f"     Family: {family_name}")
                break
        if afib_tree:
            break
    
    if not afib_tree:
        print("   ✗ ERROR: Atrial Fibrillation tree not found!")
        return
    
    # Display the presentations in the tree
    print("\n3. Atrial Fibrillation Presentations in Database:")
    print("-" * 80)
    presentations = afib_tree.get('presentations', [])
    string_presentations = [p for p in presentations if isinstance(p, str)]
    for i, p in enumerate(string_presentations, 1):
        print(f"   {i}. {p}")
    
    # Test matching
    print("\n4. Testing Symptom Matching:")
    print("-" * 80)
    
    # Normalize symptoms
    normalized_symptoms = [normalize_text(s) for s in test_symptoms]
    print(f"   Normalized input: {normalized_symptoms}")
    
    # Calculate match score
    score, matched_presentations = calculate_match_score(
        test_symptoms, string_presentations, afib_tree
    )
    
    print(f"\n   Match Score: {score:.2f}")
    print(f"   Matched Presentations: {len(matched_presentations)}")
    
    if matched_presentations:
        print("\n   Matched:")
        for mp in matched_presentations:
            print(f"     ✓ {mp}")
    else:
        print("\n   ✗ NO MATCHES FOUND!")
        print("\n   Let's check why each symptom didn't match:")
        
        for symptom in test_symptoms:
            print(f"\n   Symptom: '{symptom}'")
            normalized_symptom = normalize_text(symptom)
            print(f"   Normalized: '{normalized_symptom}'")
            
            found = False
            for pres in string_presentations:
                normalized_pres = normalize_text(pres)
                if normalized_symptom in normalized_pres:
                    print(f"     ✓ Found exact match in: {pres}")
                    found = True
                else:
                    # Check word overlap
                    symptom_words = set(normalized_symptom.split())
                    pres_words = set(normalized_pres.split())
                    overlap = symptom_words & pres_words
                    if overlap:
                        print(f"     ~ Partial match (words: {overlap}) in: {pres}")
                        found = True
            
            if not found:
                print(f"     ✗ No match found")
    
    # Now test a full search
    print("\n5. Running Full Symptom Search:")
    print("-" * 80)
    
    # Pre-normalize input
    normalized_input = [normalize_text(s) for s in test_symptoms]
    
    results = []
    for family_name, rules in all_families.items():
        for rule in rules:
            presentations = rule.get('presentations', [])
            string_presentations = [p for p in presentations if isinstance(p, str)]
            
            if not string_presentations:
                continue
            
            score, matched = calculate_match_score(test_symptoms, string_presentations, rule)
            
            if score > 0:
                results.append({
                    'label': rule.get('label', ''),
                    'id': rule.get('id', ''),
                    'family': family_name,
                    'score': score,
                    'matched': len(matched)
                })
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"   Found {len(results)} total matches")
    print("\n   Top 10 Results:")
    for i, result in enumerate(results[:10], 1):
        afib_marker = " ← ATRIAL FIBRILLATION" if 'ATRIAL-FIBRILLATION' in result['id'] else ""
        print(f"   {i}. {result['label']} (Score: {result['score']:.2f}){afib_marker}")
    
    # Check if AFib is in results
    afib_in_results = any('ATRIAL-FIBRILLATION' in r['id'] for r in results)
    
    print("\n" + "=" * 80)
    if afib_in_results:
        print("✓ SUCCESS: Atrial Fibrillation found in search results")
        afib_result = next(r for r in results if 'ATRIAL-FIBRILLATION' in r['id'])
        print(f"  Rank: {results.index(afib_result) + 1}")
        print(f"  Score: {afib_result['score']:.2f}")
    else:
        print("✗ FAILURE: Atrial Fibrillation NOT found in search results")
        print("\nRECOMMENDATION: The presentations in the AFib tree need to be updated")
        print("to include more common/vernacular symptom descriptions.")
    print("=" * 80)


if __name__ == "__main__":
    test_afib_search()
