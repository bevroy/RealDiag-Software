"""
Simple test to verify atrial fibrillation YAML fix
"""

import yaml
from pathlib import Path

def test_afib_yaml():
    """Verify that atrial fibrillation presentations are correctly formatted"""
    
    print("=" * 80)
    print("Testing Atrial Fibrillation YAML Format")
    print("=" * 80)
    
    afib_file = Path("/workspaces/RealDiag-Software/backend/trees/CARDS-ATRIAL-FIBRILLATION.yml")
    
    print(f"\nReading: {afib_file}")
    
    with open(afib_file, 'r') as f:
        data = yaml.safe_load(f)
    
    print(f"\nTree ID: {data.get('tree_id')}")
    print(f"Name: {data.get('name')}")
    
    presentations = data.get('presentations', [])
    print(f"\nPresentations ({len(presentations)} total):")
    print("-" * 80)
    
    all_strings = True
    for i, p in enumerate(presentations, 1):
        type_info = f"[{type(p).__name__}]"
        if isinstance(p, str):
            print(f"{i}. {type_info} {p}")
        else:
            print(f"{i}. {type_info} ERROR: Not a string! {p}")
            all_strings = False
    
    print("\n" + "=" * 80)
    
    # Check for key symptoms
    presentations_text = " ".join([str(p).lower() for p in presentations if isinstance(p, str)])
    
    has_palpitations = "palpitation" in presentations_text
    has_irregular = "irregular" in presentations_text
    has_dizziness = "dizziness" in presentations_text or "lightheadedness" in presentations_text
    
    print("\nKey Symptom Coverage:")
    print(f"  {'✓' if has_palpitations else '✗'} Palpitations mentioned")
    print(f"  {'✓' if has_irregular else '✗'} Irregular pulse/heartbeat mentioned")
    print(f"  {'✓' if has_dizziness else '✗'} Dizziness/lightheadedness mentioned")
    
    if all_strings and has_palpitations and has_irregular and has_dizziness:
        print("\n✓ SUCCESS: All presentations are properly formatted strings")
        print("✓ SUCCESS: Key symptoms (palpitations, irregular pulse, dizziness) are covered")
        return True
    else:
        print("\n✗ FAILURE: Issues detected")
        if not all_strings:
            print("  - Some presentations are not strings")
        if not has_palpitations:
            print("  - Missing 'palpitations'")
        if not has_irregular:
            print("  - Missing 'irregular pulse/heartbeat'")
        if not has_dizziness:
            print("  - Missing 'dizziness/lightheadedness'")
        return False


def test_atrial_flutter_yaml():
    """Verify that atrial flutter presentations are correctly formatted"""
    
    print("\n" + "=" * 80)
    print("Testing Atrial Flutter YAML Format")
    print("=" * 80)
    
    flutter_file = Path("/workspaces/RealDiag-Software/backend/trees/CARDS-ATRIAL-FLUTTER.yml")
    
    print(f"\nReading: {flutter_file}")
    
    with open(flutter_file, 'r') as f:
        data = yaml.safe_load(f)
    
    print(f"\nTree ID: {data.get('tree_id')}")
    print(f"Name: {data.get('name')}")
    
    presentations = data.get('presentations', [])
    print(f"\nPresentations ({len(presentations)} total):")
    print("-" * 80)
    
    all_strings = True
    for i, p in enumerate(presentations, 1):
        type_info = f"[{type(p).__name__}]"
        if isinstance(p, str):
            print(f"{i}. {type_info} {p}")
        else:
            print(f"{i}. {type_info} ERROR: Not a string! {p}")
            all_strings = False
    
    print("\n" + "=" * 80)
    
    if all_strings:
        print("✓ SUCCESS: All presentations are properly formatted strings")
        return True
    else:
        print("✗ FAILURE: Some presentations are not strings")
        return False


if __name__ == "__main__":
    result1 = test_afib_yaml()
    result2 = test_atrial_flutter_yaml()
    
    print("\n" + "=" * 80)
    if result1 and result2:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 80)
