"""
Test for Pyelonephritis symptom search ranking
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from services.symptom_search import load_all_families, normalize_text, calculate_match_score

def test_pyelonephritis_search():
    """Test that pyelonephritis ranking for classic symptoms"""
    
    print("=" * 80)
    print("Testing Pyelonephritis Search")
    print("=" * 80)
    
    # User's reported symptoms - CLASSIC pyelonephritis triad
    test_symptoms = ["flank pain", "fever", "chills"]
    
    print(f"\nInput Symptoms: {test_symptoms}")
    print("NOTE: These are the CLASSIC TRIAD for pyelonephritis!")
    print("-" * 80)
    
    # Load all diagnostic trees
    print("\n1. Loading diagnostic trees...")
    all_families = load_all_families()
    total_trees = sum(len(rules) for rules in all_families.values())
    print(f"   ✓ Loaded {total_trees} diagnostic trees across {len(all_families)} families")
    
    # Find pyelonephritis specifically
    print("\n2. Looking for Pyelonephritis tree...")
    pyelo_tree = None
    
    for family_name, rules in all_families.items():
        for rule in rules:
            if 'pyelonephritis' in rule.get('label', '').lower() or 'PYELONEPHRITIS' in rule.get('id', ''):
                pyelo_tree = rule
                print(f"   ✓ Found: {rule.get('label')} (ID: {rule.get('id')})")
                print(f"     Family: {family_name}")
                break
        if pyelo_tree:
            break
    
    if not pyelo_tree:
        print("   ✗ ERROR: Pyelonephritis tree not found!")
        return
    
    # Display the presentations in the tree
    print("\n3. Pyelonephritis Presentations in Database:")
    print("-" * 80)
    presentations = pyelo_tree.get('presentations', [])
    string_presentations = [p for p in presentations if isinstance(p, str)]
    
    if not string_presentations:
        print("   ✗ ERROR: No valid string presentations found!")
        print(f"   Raw presentations: {presentations}")
        return
    
    for i, p in enumerate(string_presentations, 1):
        print(f"   {i}. {p}")
    
    # Test matching
    print("\n4. Testing Symptom Matching:")
    print("-" * 80)
    
    # Normalize symptoms
    normalized_symptoms = [normalize_text(s) for s in test_symptoms]
    print(f"   Normalized input: {normalized_symptoms}")
    
    # Calculate match score
    score, matched_presentations = calculate_match_score(
        test_symptoms, string_presentations, pyelo_tree
    )
    
    print(f"\n   Match Score: {score:.2f}")
    print(f"   Matched Presentations: {len(matched_presentations)}")
    
    if matched_presentations:
        print("\n   Matched:")
        for mp in matched_presentations:
            print(f"     ✓ {mp}")
    else:
        print("\n   ✗ NO MATCHES FOUND!")
        print("\n   Detailed analysis:")
        
        for symptom in test_symptoms:
            print(f"\n   Symptom: '{symptom}'")
            normalized_symptom = normalize_text(symptom)
            print(f"   Normalized: '{normalized_symptom}'")
            
            found = False
            for pres in string_presentations:
                normalized_pres = normalize_text(pres)
                if normalized_symptom in normalized_pres:
                    print(f"     ✓ Found exact match in: {pres}")
                    found = True
                else:
                    # Check word overlap
                    symptom_words = set(normalized_symptom.split())
                    pres_words = set(normalized_pres.split())
                    overlap = symptom_words & pres_words
                    if overlap:
                        print(f"     ~ Partial match (words: {overlap}) in: {pres}")
            
            if not found:
                print(f"     ✗ No match found for '{symptom}'")
    
    # Now test a full search
    print("\n5. Running Full Symptom Search:")
    print("-" * 80)
    
    results = []
    for family_name, rules in all_families.items():
        for rule in rules:
            presentations = rule.get('presentations', [])
            string_presentations = [p for p in presentations if isinstance(p, str)]
            
            if not string_presentations:
                continue
            
            score, matched = calculate_match_score(test_symptoms, string_presentations, rule)
            
            if score > 0:
                results.append({
                    'label': rule.get('label', ''),
                    'id': rule.get('id', ''),
                    'family': family_name,
                    'score': score,
                    'matched': len(matched),
                    'matched_presentations': matched
                })
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"   Found {len(results)} total matches")
    print("\n   Top 15 Results:")
    for i, result in enumerate(results[:15], 1):
        pyelo_marker = " ← PYELONEPHRITIS" if 'pyelonephritis' in result['label'].lower() else ""
        print(f"   {i}. {result['label']} (Score: {result['score']:.2f}, Matched: {result['matched']}){pyelo_marker}")
    
    # Check ranking of Pyelonephritis
    pyelo_results = [r for r in results if 'pyelonephritis' in r['label'].lower()]
    
    print("\n" + "=" * 80)
    if pyelo_results:
        pyelo = pyelo_results[0]
        rank = results.index(pyelo) + 1
        print(f"Pyelonephritis Ranking: #{rank}")
        print(f"Match Score: {pyelo['score']:.2f}")
        print(f"Matched Presentations: {pyelo['matched']}")
        
        if rank <= 3:
            print("\n✓ GOOD: Pyelonephritis in top 3 (clinically appropriate)")
        elif rank <= 5:
            print("\n⚠ ACCEPTABLE: Pyelonephritis in top 5 but could be higher")
        else:
            print(f"\n✗ ISSUE: Pyelonephritis at rank #{rank} is too low!")
            print("\nFor classic symptoms (flank pain + fever + chills),")
            print("pyelonephritis should typically rank in the TOP 3.")
            
            print("\n📊 Diagnoses ranking HIGHER than Pyelonephritis:")
            for i, r in enumerate(results[:rank-1], 1):
                print(f"   {i}. {r['label']} (Score: {r['score']:.2f})")
                print(f"      Matched: {r['matched_presentations'][:2]}")  # Show first 2 matches
    else:
        print("✗ FAILURE: Pyelonephritis NOT found in search results!")
    
    print("=" * 80)


if __name__ == "__main__":
    test_pyelonephritis_search()
