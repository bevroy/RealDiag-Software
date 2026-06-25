"""
Test gout search with classic presentation
"""

import yaml

def test_gout_search():
    print("=" * 80)
    print("GOUT SEARCH TEST")
    print("=" * 80)
    
    with open('/workspaces/RealDiag-Software/backend/trees/RHEUM-GOUT.yml', 'r') as f:
        data = yaml.safe_load(f)
    
    presentations = data.get('presentations', [])
    presentations_lower = [str(p).lower() for p in presentations if isinstance(p, str)]
    
    print(f"\nCurrent presentations ({len(presentations_lower)}):")
    for i, p in enumerate(presentations, 1):
        print(f"  {i}. {p}")
    
    # Test classic symptoms
    test_symptoms = [
        "sudden red swollen big toe",
        "swollen big toe",
        "red swollen toe",
        "big toe pain",
        "first toe pain",
        "podagra"
    ]
    
    print(f"\n\nTesting {len(test_symptoms)} symptom variations:")
    print("-" * 80)
    
    for symptom in test_symptoms:
        symptom_lower = symptom.lower()
        symptom_words = set(symptom_lower.split())
        
        # Find matches
        matches = []
        for p in presentations_lower:
            p_words = set(p.split())
            overlap = symptom_words & p_words
            if overlap:
                matches.append((p, len(overlap)))
        
        if matches:
            matches.sort(key=lambda x: x[1], reverse=True)
            best = matches[0]
            print(f"\n✓ '{symptom}' - {best[1]} word(s) matched")
            print(f"   Best match: '{best[0]}'")
        else:
            print(f"\n✗ '{symptom}' - NO MATCH")
    
    print("\n" + "=" * 80)
    print("ANALYSIS:")
    print("  Current presentations use medical terms:")
    print("  - 'First MTP joint (podagra)' ← medical abbreviation")
    print("  - Missing lay terms: 'big toe', 'red', 'swollen toe'")
    print("  Need to add patient-friendly descriptions!")

if __name__ == "__main__":
    test_gout_search()
