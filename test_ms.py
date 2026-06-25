"""
Test multiple sclerosis search with classic presentation
"""

import yaml

def test_ms_search():
    print("=" * 80)
    print("MULTIPLE SCLEROSIS SEARCH TEST")
    print("=" * 80)
    
    with open('/workspaces/RealDiag-Software/backend/trees/NEU-MS.yml', 'r') as f:
        data = yaml.safe_load(f)
    
    presentations = data.get('presentations', [])
    presentations_lower = [str(p).lower() for p in presentations if isinstance(p, str)]
    
    print(f"\nCurrent presentations ({len(presentations_lower)}):")
    for i, p in enumerate(presentations, 1):
        print(f"  {i}. {p}")
    
    # Test classic symptoms
    test_symptoms = [
        "visual loss and limb weakness",
        "vision loss and weakness",
        "visual loss and weakness",
        "vision problems and weakness",
        "optic neuritis and weakness",
        "blurred vision and limb weakness",
        "vision changes and leg weakness"
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
    print("  Current presentations use medical terms:")
    print("  - 'optic neuritis' (medical) vs 'visual loss' (patient language)")
    print("  - 'weakness' is mentioned but not combined with visual symptoms")
    print("  - Need lay language: 'visual loss', 'vision loss', 'blurred vision'")
    print("  - Need combined presentations: 'visual loss and weakness'")

if __name__ == "__main__":
    test_ms_search()
