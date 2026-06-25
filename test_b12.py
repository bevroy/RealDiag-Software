"""
Test Vitamin B12 deficiency presentation matching
"""

import yaml

def test_b12():
    print("=" * 80)
    print("Vitamin B12 Deficiency Presentation Analysis")
    print("=" * 80)
    
    with open('/workspaces/RealDiag-Software/backend/trees/HEME-B12-DEF.yml', 'r') as f:
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
    test_symptoms = ["numbness", "gait instability"]
    
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
            for p, words in word_matches[:3]:
                print(f"      - '{p}' (words: {words})")
        else:
            print(f"    ✗ NO MATCH")
    
    print("\n" + "=" * 80)
    print("CLINICAL CONTEXT:")
    print("  Numbness + gait instability = Classic for B12 deficiency neuropathy!")
    print("  'Subacute combined degeneration' is the medical term")
    print("  Causes: peripheral neuropathy (numbness) + posterior column dysfunction (ataxia)")
    
    # Check coverage
    has_numbness = any('numbness' in p or 'numb' in p for p in presentations_lower)
    has_gait = any('gait' in p or 'ataxia' in p or 'walking' in p for p in presentations_lower)
    has_neuropathy = any('neuropathy' in p for p in presentations_lower)
    has_ataxia = any('ataxia' in p for p in presentations_lower)
    
    print("\n" + "=" * 80)
    print("Current Coverage:")
    print(f"  {'✓' if has_numbness else '✗'} Numbness")
    print(f"  {'✓' if has_gait else '✗'} Gait instability")
    print(f"  {'✓' if has_neuropathy else '✗'} Neuropathy (medical term)")
    print(f"  {'✓' if has_ataxia else '✗'} Ataxia (medical term)")
    
    if not has_numbness:
        print("\n✗ MISSING: 'numbness' or 'paresthesias'")
        print("  Peripheral neuropathy CAUSES numbness but term not explicit")
    
    if not has_gait:
        print("\n✗ MISSING: 'gait instability' or 'balance problems'")
        print("  Ataxia IS gait instability but term not explicit")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATION:")
    print("  Add lay terms alongside medical terms:")
    print('  - "Peripheral neuropathy, numbness, tingling, paresthesias"')
    print('  - "Ataxia, gait instability, balance problems, unsteady walking"')

if __name__ == "__main__":
    test_b12()
