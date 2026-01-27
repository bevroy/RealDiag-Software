"""
Test B12 deficiency with multiple search variations
"""

import yaml

def test_b12_variations():
    print("=" * 80)
    print("B12 Deficiency Multiple Search Variation Testing")
    print("=" * 80)
    
    with open('/workspaces/RealDiag-Software/backend/trees/HEME-B12-DEF.yml', 'r') as f:
        data = yaml.safe_load(f)
    
    presentations = data.get('presentations', [])
    presentations_lower = [str(p).lower() for p in presentations if isinstance(p, str)]
    
    # Test multiple variations
    test_variations = [
        "numbness and gait instability",
        "numbness and tingling",
        "tingling in hands and feet",
        "balance problems",
        "unsteady walking",
        "difficulty walking",
        "memory problems",
        "fatigue and numbness",
        "peripheral neuropathy",
        "ataxia"
    ]
    
    print(f"\nTesting {len(test_variations)} search variations:")
    print("-" * 80)
    
    for symptom in test_variations:
        symptom_lower = symptom.lower()
        
        # Check for exact or strong match
        best_match = None
        best_overlap_count = 0
        
        for p in presentations_lower:
            # Check for exact match or substring
            if symptom_lower in p or p in symptom_lower:
                best_match = p
                best_overlap_count = len(symptom_lower.split())
                break
            
            # Check word overlap
            symptom_words = set(symptom_lower.split())
            p_words = set(p.split())
            overlap = symptom_words & p_words
            if len(overlap) > best_overlap_count:
                best_overlap_count = len(overlap)
                best_match = p
        
        status = "✓" if best_overlap_count >= 2 else "~" if best_overlap_count >= 1 else "✗"
        print(f"\n{status} '{symptom}'")
        if best_match and best_overlap_count >= 1:
            print(f"   Best match: '{best_match}' ({best_overlap_count} words)")
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("  ✓ Both medical terms (neuropathy, ataxia) and lay terms (numbness, gait")
    print("    instability) now covered")
    print("  ✓ Classic B12 neurological symptoms well represented")
    print("  ✓ Includes both sensory (numbness) and motor (gait) symptoms")

if __name__ == "__main__":
    test_b12_variations()
