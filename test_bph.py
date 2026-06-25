"""
Test BPH search with classic presentation
"""

import yaml

def test_bph_search():
    print("=" * 80)
    print("BENIGN PROSTATIC HYPERPLASIA (BPH) SEARCH TEST")
    print("=" * 80)
    
    with open('/workspaces/RealDiag-Software/backend/trees/UROLOGY-BENIGN-PROSTATIC-HYPERPLASIA.yml', 'r') as f:
        data = yaml.safe_load(f)
    
    presentations = data.get('presentations', [])
    presentations_lower = [str(p).lower() for p in presentations if isinstance(p, str)]
    
    print(f"\nCurrent presentations ({len(presentations_lower)}):")
    for i, p in enumerate(presentations, 1):
        print(f"  {i}. {p}")
    
    # Test classic symptoms
    test_symptoms = [
        "weak urinary stream and nocturia",
        "weak stream and nocturia",
        "weak urinary stream nocturia",
        "weak stream nocturia",
        "urinary frequency nocturia",
        "hesitancy weak stream",
        "BPH symptoms"
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
            print(f"\n{'✓' if best[1] >= 2 else '~'} '{symptom}' - {best[1]} word(s) matched")
            print(f"   Best match: '{best[0]}'")
        else:
            print(f"\n✗ '{symptom}' - NO MATCH")
    
    print("\n" + "=" * 80)
    print("ANALYSIS:")
    print("  Current presentations:")
    print("  - 'weak stream' is in obstructive symptoms list")
    print("  - 'nocturia' is in irritative symptoms list")
    print("  - They're separated in different presentations")
    print("  Need combined: 'weak urinary stream and nocturia'")

if __name__ == "__main__":
    test_bph_search()
