#!/usr/bin/env python3
"""
Update all management sections in YAML files to follow FDA-exempt safe format.

Format:
"Guideline-based treatment options for [CONDITION] include:"
[list of treatments with citations]
"""

import os
import yaml
from pathlib import Path

def update_management_section(rule):
    """Update management section to include guideline-based intro and disclaimer."""
    if 'management' not in rule or not rule['management']:
        return rule
    
    # Get condition name from label
    condition = rule.get('label', 'this condition')
    
    # Create new management list with guideline-based intro
    intro = f"Guideline-based treatment options for {condition} include:"
    
    # Keep existing management items
    new_management = [intro] + rule['management']
    
    rule['management'] = new_management
    
    return rule

def process_yaml_file(filepath):
    """Process a single YAML file."""
    print(f"Processing {filepath}...")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data or 'rules' not in data:
            print(f"  Skipping - no rules found")
            return
        
        # Update each rule
        updated_count = 0
        for rule in data['rules']:
            if 'management' in rule and rule['management']:
                rule = update_management_section(rule)
                updated_count += 1
        
        # Write back
        if updated_count > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            print(f"  Updated {updated_count} rules")
        else:
            print(f"  No management sections found")
            
    except Exception as e:
        print(f"  Error: {e}")

def main():
    """Process all YAML files in backend/rules/."""
    rules_dir = Path('/workspaces/RealDiag-Software/backend/rules')
    
    if not rules_dir.exists():
        print(f"Rules directory not found: {rules_dir}")
        return
    
    yaml_files = list(rules_dir.glob('*.yml'))
    print(f"Found {len(yaml_files)} YAML files\n")
    
    for yaml_file in yaml_files:
        process_yaml_file(yaml_file)
    
    print("\n✓ All files processed")

if __name__ == '__main__':
    main()
