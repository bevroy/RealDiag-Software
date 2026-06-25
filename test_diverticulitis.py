"""
Test diverticulitis presentation matching
"""

import yaml

def test_diverticulitis():
    print("=" * 80)
    print("Diverticulitis Presentation Analysis")
    print("=" * 80)
    
    with open('/workspaces/RealDiag-Software/backend/trees/GI-DIVERTICULITIS.yml', 'r') as f:
        data = yaml.safe_load(f)
    
    print(f"\nTree: {data['name']}")
    print(f"ID: {data['tree_id']}")
    
    presentations = data.get('presentations', [])
    print(f"\nPresentations: {len(presentations)} items")
    print("-" * 80)
    
    for i, p in enumerate(presentations, 1):
        ptype = type(p).__name__
        print(f"{i}. [{ptype}] {p}")
    
    # Test symptoms - note user said "LLQ abdominal pain"
    test_symptoms = ["LLQ abdominal pain", "fever"]
    
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
    print("ISSUE IDENTIFIED:")
    
    # Check for LLQ specifically
    has_llq = any('llq' in p for p in presentations_lower)
    has_left_lower = any('left lower' in p for p in presentations_lower)
    has_fever = any('fever' in p for p in presentations_lower)
    
    print(f"  {'✓' if has_llq else '✗'} Contains 'LLQ'")
    print(f"  {'✓' if has_left_lower else '✗'} Contains 'left lower'")
    print(f"  {'✓' if has_fever else '✗'} Contains 'fever'")
    
    if has_left_lower and not has_llq:
        print("\n❌ PROBLEM: Presentation uses 'Left lower quadrant' but user searched 'LLQ'")
        print("   These are medical abbreviations that need to be matched!")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATION:")
    print("  Update first presentation to include the abbreviation:")
    print('  "Left lower quadrant (LLQ) abdominal pain"')
    print("  OR add a separate entry:")
    print('  "LLQ abdominal pain"')

if __name__ == "__main__":
    test_diverticulitis()
