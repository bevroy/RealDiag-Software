"""
Simple validation test for pyelonephritis presentations
"""

import yaml

def test_pyelonephritis_presentations():
    print("=" * 80)
    print("Pyelonephritis Presentation Analysis")
    print("=" * 80)
    
    # Load the file
    with open('/workspaces/RealDiag-Software/backend/trees/ID-PYELONEPHRITIS.yml', 'r') as f:
        data = yaml.safe_load(f)
    
    print(f"\nTree: {data['name']}")
    print(f"ID: {data['tree_id']}")
    
    presentations = data.get('presentations', [])
    print(f"\nPresentations: {len(presentations)} items")
    print("-" * 80)
    
    for i, p in enumerate(presentations, 1):
        ptype = type(p).__name__
        print(f"{i}. [{ptype}] {p}")
    
    # Test symptoms
    test_symptoms = ["flank pain", "fever", "chills"]
    
    print(f"\n\nTest Symptoms: {test_symptoms}")
    print("=" * 80)
    
    # Check matches
    presentations_lower = [str(p).lower() for p in presentations if isinstance(p, str)]
    presentations_text = " | ".join(presentations_lower)
    
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
            print(f"      This symptom won't contribute to match score!")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("CLINICAL CONTEXT:")
    print("  Flank pain + fever + chills = CLASSIC TRIAD for pyelonephritis")
    print("  This should rank in TOP 3 diagnoses")
    
    # Check current presentations
    has_flank_pain = any('flank' in p for p in presentations_lower)
    has_fever = any('fever' in p for p in presentations_lower)
    has_chills = any('chills' in p or 'chill' in p or 'rigor' in p for p in presentations_lower)
    
    print("\n" + "=" * 80)
    print("Current Coverage:")
    print(f"  {'✓' if has_flank_pain else '✗'} Flank pain")
    print(f"  {'✓' if has_fever else '✗'} Fever")
    print(f"  {'✓' if has_chills else '✗'} Chills")
    
    if not all([has_flank_pain, has_fever, has_chills]):
        print("\n❌ ISSUE IDENTIFIED:")
        print("   Missing or non-matching presentation terms for the classic triad")
        print("\nRECOMMENDATION:")
        print("   The first 3 presentations should be:")
        print('   1. "Fever and chills"')
        print('   2. "Flank pain or back pain"')  
        print('   3. "Costovertebral angle tenderness"')
    else:
        print("\n✓ All classic symptoms present in presentations")
        print("  (Ranking issue likely due to other diagnoses having better matches)")

if __name__ == "__main__":
    test_pyelonephritis_presentations()
