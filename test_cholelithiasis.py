"""
Test cholelithiasis presentation matching
"""

import yaml

def test_cholelithiasis():
    print("=" * 80)
    print("Cholelithiasis Presentation Analysis")
    print("=" * 80)
    
    with open('/workspaces/RealDiag-Software/backend/trees/GI-CHOLELITHIASIS.yml', 'r') as f:
        data = yaml.safe_load(f)
    
    print(f"\nTree: {data['name']}")
    print(f"ID: {data['tree_id']}")
    
    presentations = data.get('presentations', [])
    print(f"\nPresentations: {len(presentations)} items")
    print("-" * 80)
    
    for i, p in enumerate(presentations, 1):
        ptype = type(p).__name__
        print(f"{i}. [{ptype}] {p}")
    
    # Test symptoms from user
    test_symptoms = ["RUQ pain after fatty meals", "nausea"]
    
    print(f"\n\nTest Symptoms: {test_symptoms}")
    print("=" * 80)
    
    # Check matches
    presentations_lower = [str(p).lower() for p in presentations if isinstance(p, str)]
    
    print("\nMatching Analysis:")
    for symptom in test_symptoms:
        symptom_lower = symptom.lower()
        
        # Check for exact phrase
        exact_match = any(symptom_lower in p for p in presentations_lower)
        
        # Check for word matches
        symptom_words = set(symptom_lower.split())
        word_matches = []
        for p in presentations_lower:
            p_words = set(p.split())
            overlap = symptom_words & p_words
            if overlap:
                word_matches.append((p, overlap))
        
        print(f"\n  '{symptom}':")
        if exact_match:
            matching_pres = [p for p in presentations_lower if symptom_lower in p]
            print(f"    ✓ EXACT MATCH found in: {matching_pres}")
        elif word_matches:
            print(f"    ~ PARTIAL matches ({len(word_matches)} presentations):")
            for p, words in word_matches[:5]:
                print(f"      - '{p}' (words: {words})")
        else:
            print(f"    ✗ NO MATCH")
    
    print("\n" + "=" * 80)
    print("CLINICAL CONTEXT:")
    print("  RUQ pain after fatty meals + nausea = CLASSIC for cholelithiasis/biliary colic")
    print("  This should rank in TOP 3 diagnoses")
    
    # Check coverage
    has_ruq_fatty = any('ruq' in p and 'fatty' in p for p in presentations_lower)
    has_ruq_pain = any('ruq' in p and 'pain' in p for p in presentations_lower)
    has_nausea = any('nausea' in p for p in presentations_lower)
    
    print("\n" + "=" * 80)
    print("Current Coverage:")
    print(f"  {'✓' if has_ruq_fatty else '✗'} RUQ + fatty meals together")
    print(f"  {'✓' if has_ruq_pain else '✗'} RUQ + pain")
    print(f"  {'✓' if has_nausea else '✗'} Nausea")
    
    if all([has_ruq_fatty, has_ruq_pain, has_nausea]):
        print("\n✓ All key symptoms covered!")
    else:
        print("\n✗ Missing key symptom combinations")

if __name__ == "__main__":
    test_cholelithiasis()
