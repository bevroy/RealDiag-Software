"""
Test IBS presentation matching
"""

import yaml

def test_ibs():
    print("=" * 80)
    print("IBS Presentation Analysis")
    print("=" * 80)
    
    with open('/workspaces/RealDiag-Software/backend/trees/GI-IRRITABLE-BOWEL-SYNDROME.yml', 'r') as f:
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
    test_symptoms = ["crampy abdominal pain relieved by defecation"]
    
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
    print("  'Pain relieved by defecation' is one of the ROME IV CRITERIA for IBS!")
    print("  This is a CARDINAL symptom and should match strongly.")
    
    # Check coverage
    has_pain = any('pain' in p for p in presentations_lower)
    has_defecation = any('defecation' in p for p in presentations_lower)
    has_relieved = any('relieve' in p or 'improve' in p for p in presentations_lower)
    has_crampy = any('cramp' in p for p in presentations_lower)
    
    print("\n" + "=" * 80)
    print("Current Coverage:")
    print(f"  {'✓' if has_pain else '✗'} Abdominal pain")
    print(f"  {'✓' if has_defecation else '✗'} Defecation")
    print(f"  {'✓' if has_relieved else '✗'} Relief/improvement")
    print(f"  {'✓' if has_crampy else '✗'} Crampy")
    
    if has_pain and has_defecation and has_relieved:
        print("\n✓ Key concepts present but may not be matching well")
        print("  Current: 'Pain improves with defecation'")
        print("  User searched: 'Crampy abdominal pain relieved by defecation'")
        print("\n  ISSUE: Multi-word symptom matching algorithm")
        print("  - 'crampy' is the first word but doesn't match 'pain' or 'recurrent'")
        print("  - Needs explicit 'crampy' or 'cramping' in presentations")
    else:
        print("\n✗ Missing key symptom components")

if __name__ == "__main__":
    test_ibs()
