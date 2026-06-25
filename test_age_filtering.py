#!/usr/bin/env python3
"""
Test script to verify age-based filtering in symptom search
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.symptom_search import load_all_families, apply_filters

def test_age_filtering():
    """Test that age filtering correctly excludes age-inappropriate diagnoses"""
    
    print("=" * 80)
    print("Testing Age-Based Filtering in Symptom Search")
    print("=" * 80)
    
    # Load all diagnostic trees
    print("\n1. Loading all diagnostic trees...")
    all_families = load_all_families()
    all_rules = [rule for rules in all_families.values() for rule in rules]
    total_trees = len(all_rules)
    print(f"   ✓ Loaded {total_trees} diagnostic trees")
    
    # Find pediatric conditions
    print("\n2. Finding pediatric-specific conditions...")
    pediatric_conditions = []
    for rule in all_rules:
        rule_id = rule.get('id', '')
        label = rule.get('label', '')
        family = rule.get('family', '')
        age_max = rule.get('age_max')
        
        if 'PEDS-' in rule_id or family.upper() == 'PEDIATRICS' or age_max:
            pediatric_conditions.append({
                'id': rule_id,
                'label': label,
                'age_max': age_max,
                'family': family
            })
            if len(pediatric_conditions) >= 5:
                break
    
    print(f"   Found {len(pediatric_conditions)} sample pediatric conditions:")
    for cond in pediatric_conditions:
        age_max_str = f"age_max: {cond['age_max']}" if cond['age_max'] else "no age_max"
        print(f"   - {cond['id']}: {cond['label']} ({age_max_str})")
    
    # Find geriatric conditions
    print("\n3. Finding geriatric-specific conditions...")
    geriatric_conditions = []
    for rule in all_rules:
        rule_id = rule.get('id', '')
        label = rule.get('label', '')
        family = rule.get('family', '')
        age_min = rule.get('age_min')
        
        if 'GER-' in rule_id or family.upper() == 'GERIATRICS' or age_min:
            geriatric_conditions.append({
                'id': rule_id,
                'label': label,
                'age_min': age_min,
                'family': family
            })
            if len(geriatric_conditions) >= 5:
                break
    
    print(f"   Found {len(geriatric_conditions)} sample geriatric conditions:")
    for cond in geriatric_conditions:
        age_min_str = f"age_min: {cond['age_min']}" if cond['age_min'] else "no age_min"
        print(f"   - {cond['id']}: {cond['label']} ({age_min_str})")
    
    # Test 1: Adult patient (age 35) should NOT get pediatric conditions
    print("\n4. Testing filtering for Adult (age 35)...")
    filtered_adult = apply_filters(all_rules, age=35, sex=None)
    
    peds_in_adult = []
    for rule in filtered_adult:
        rule_id = rule.get('id', '')
        family = rule.get('family', '').upper()
        if 'PEDS-' in rule_id or family == 'PEDIATRICS':
            peds_in_adult.append(f"{rule_id} - {rule.get('label')}")
    
    print(f"   Total rules before filtering: {len(all_rules)}")
    print(f"   Total rules after filtering: {len(filtered_adult)}")
    print(f"   Pediatric conditions in results: {'❌ YES (PROBLEM!)' if peds_in_adult else '✓ NO (CORRECT!)'}")
    if peds_in_adult:
        for cond in peds_in_adult[:3]:
            print(f"      - {cond}")
    
    # Test 2: Young child (age 5) should NOT get geriatric conditions
    print("\n5. Testing filtering for Child (age 5)...")
    filtered_child = apply_filters(all_rules, age=5, sex=None)
    
    ger_in_child = []
    for rule in filtered_child:
        rule_id = rule.get('id', '')
        family = rule.get('family', '').upper()
        if 'GER-' in rule_id or family == 'GERIATRICS':
            ger_in_child.append(f"{rule_id} - {rule.get('label')}")
    
    print(f"   Total rules before filtering: {len(all_rules)}")
    print(f"   Total rules after filtering: {len(filtered_child)}")
    print(f"   Geriatric conditions in results: {'❌ YES (PROBLEM!)' if ger_in_child else '✓ NO (CORRECT!)'}")
    if ger_in_child:
        for cond in ger_in_child[:3]:
            print(f"      - {cond}")
    
    # Test 3: Elderly patient (age 75) should NOT get pediatric conditions
    print("\n6. Testing filtering for Elderly (age 75)...")
    filtered_elderly = apply_filters(all_rules, age=75, sex=None)
    
    peds_in_elderly = []
    for rule in filtered_elderly:
        rule_id = rule.get('id', '')
        family = rule.get('family', '').upper()
        if 'PEDS-' in rule_id or family == 'PEDIATRICS':
            peds_in_elderly.append(f"{rule_id} - {rule.get('label')}")
    
    print(f"   Total rules before filtering: {len(all_rules)}")
    print(f"   Total rules after filtering: {len(filtered_elderly)}")
    print(f"   Pediatric conditions in results: {'❌ YES (PROBLEM!)' if peds_in_elderly else '✓ NO (CORRECT!)'}")
    
    # Test 4: Age-specific condition filtering by metadata
    print("\n7. Testing explicit age_min/age_max filtering...")
    
    # Test bronchiolitis (age_max: 2) doesn't appear for 10-year-old
    filtered_age10 = apply_filters(all_rules, age=10, sex=None)
    bronchiolitis_found = any('BRONCHIOLITIS' in rule.get('id', '') for rule in filtered_age10)
    
    # Test sarcopenia (age_min: 65) doesn't appear for 40-year-old
    filtered_age40 = apply_filters(all_rules, age=40, sex=None)
    sarcopenia_found = any('SARCOPENIA' in rule.get('id', '') for rule in filtered_age40)
    
    print(f"   Bronchiolitis (age_max: 2) for 10-year-old: {'❌ FOUND (PROBLEM!)' if bronchiolitis_found else '✓ NOT FOUND (CORRECT!)'}")
    print(f"   Sarcopenia (age_min: 65) for 40-year-old: {'❌ FOUND (PROBLEM!)' if sarcopenia_found else '✓ NOT FOUND (CORRECT!)'}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("=" * 80)
    
    all_passed = not peds_in_adult and not ger_in_child and not peds_in_elderly and not bronchiolitis_found and not sarcopenia_found
    
    if all_passed:
        print("✅ SUCCESS: Age-based filtering is working correctly!")
        print("  - Adults (35) do NOT get pediatric diagnoses")
        print("  - Children (5) do NOT get geriatric diagnoses")
        print("  - Elderly (75) do NOT get pediatric diagnoses")
        print("  - age_min/age_max metadata respected")
        return True
    else:
        print("❌ FAILURE: Age-based filtering is NOT working correctly")
        if peds_in_adult or peds_in_elderly:
            print("  - Adults/Elderly still receiving pediatric diagnoses")
        if ger_in_child:
            print("  - Children still receiving geriatric diagnoses")
        if bronchiolitis_found or sarcopenia_found:
            print("  - age_min/age_max metadata not being respected")
        return False

if __name__ == '__main__':
    success = test_age_filtering()
    sys.exit(0 if success else 1)
