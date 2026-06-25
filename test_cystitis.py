"""
Test acute cystitis / UTI search with classic presentation
"""

import yaml

def test_cystitis_search():
    print("=" * 80)
    print("ACUTE CYSTITIS / UTI SEARCH TEST")
    print("=" * 80)
    
    with open('/workspaces/RealDiag-Software/backend/trees/URO-UTI.yml', 'r') as f:
        data = yaml.safe_load(f)
    
    # Get presentations - might be in different format
    presentations = []
    if 'presentations' in data:
        presentations = data['presentations']
    elif 'workup' in data:
        # Workup might contain clinical descriptions
        workup = data.get('workup', [])
        presentations = [str(w) for w in workup if isinstance(w, str)]
    
    presentations_lower = [str(p).lower() for p in presentations if isinstance(p, str)]
    
    print(f"\nFile name: {data.get('name', 'N/A')}")
    print(f"Chief complaint: {data.get('chief_complaint', 'N/A')}")
    print(f"\nCurrent presentations/workup ({len(presentations_lower)}):")
    for i, p in enumerate(presentations, 1):
        print(f"  {i}. {p}")
    
    # Test classic symptoms
    test_symptoms = [
        "dysuria and urgency",
        "dysuria urgency",
        "painful urination and urgency",
        "burning urination urgency",
        "acute cystitis",
        "bladder infection",
        "UTI"
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
    print("  File structure uses 'workup' field instead of 'presentations'")
    print("  Need to check if file needs 'presentations' field or")
    print("  if search algorithm looks at workup field")

if __name__ == "__main__":
    test_cystitis_search()
