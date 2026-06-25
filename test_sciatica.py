"""
Test lumbar disc herniation / sciatica search with classic presentation
"""

import yaml

def test_sciatica_search():
    print("=" * 80)
    print("LUMBAR DISC HERNIATION / SCIATICA SEARCH TEST")
    print("=" * 80)
    
    with open('/workspaces/RealDiag-Software/backend/trees/NEU-SCIATICA.yml', 'r') as f:
        data = yaml.safe_load(f)
    
    presentations = data.get('presentations', [])
    presentations_lower = [str(p).lower() for p in presentations if isinstance(p, str)]
    
    print(f"\nCurrent presentations ({len(presentations_lower)}):")
    for i, p in enumerate(presentations, 1):
        print(f"  {i}. {p}")
    
    # Test classic symptoms
    test_symptoms = [
        "back pain radiating down leg",
        "back pain down leg",
        "lower back pain radiating to leg",
        "radiating leg pain",
        "pain shooting down leg",
        "lumbar disc herniation",
        "sciatica"
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
    print("  Current presentation: 'radiating pain from lower back to leg'")
    print("  Issue: Multi-word matching algorithm requires first word match")
    print("  - 'back pain radiating down leg' starts with 'back'")
    print("  - 'radiating pain from lower back to leg' starts with 'radiating'")
    print("  - No first-word match = weak matching")
    print("\n  Need to add: 'back pain radiating', 'lower back pain radiating'")

if __name__ == "__main__":
    test_sciatica_search()
