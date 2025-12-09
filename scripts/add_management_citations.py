#!/usr/bin/env python3
"""
Add citations to each management recommendation in YAML files.
"""

import os
import yaml
from pathlib import Path
import re

def extract_citation(source_text):
    """Extract a short citation from the source text."""
    # Map common organizations to short citations
    citation_map = {
        'American Diabetes Association': 'ADA',
        'American College of Cardiology': 'ACC/AHA',
        'American Heart Association': 'ACC/AHA',
        'American Academy of Neurology': 'AAN',
        'American Stroke Association': 'ASA',
        'Endocrine Society': 'Endocrine Society',
        'European Society of Cardiology': 'ESC',
        'Infectious Diseases Society': 'IDSA',
        'American College of Gastroenterology': 'ACG',
        'American Thoracic Society': 'ATS',
        'American Academy of Pediatrics': 'AAP',
        'American College of Obstetricians': 'ACOG',
        'American Urological Association': 'AUA',
        'American Academy of Dermatology': 'AAD',
        'American Academy of Ophthalmology': 'AAO',
        'American College of Rheumatology': 'ACR',
        'American Psychiatric Association': 'APA',
        'National Kidney Foundation': 'NKF/KDIGO',
        'American Society of Hematology': 'ASH',
        'American College of Emergency': 'ACEP',
        'Orthopedic': 'AAOS',
        'Society of Thoracic Surgeons': 'STS'
    }
    
    for org, citation in citation_map.items():
        if org in source_text:
            return citation
    
    # Default fallback
    return 'Guidelines'

def add_citations_to_management(rule, citation):
    """Add citations to management items that don't already have them."""
    if 'management' not in rule or not rule['management']:
        return rule
    
    new_management = []
    for item in rule['management']:
        # Skip the intro line
        if 'Guideline-based treatment options' in item:
            new_management.append(item)
            continue
        
        # Check if item already has a citation in parentheses at the end
        if re.search(r'\([A-Z]{2,}\/?[A-Z]*\s*\d*\)$', item):
            new_management.append(item)
        else:
            # Add citation
            new_management.append(f"{item} ({citation})")
    
    rule['management'] = new_management
    return rule

def process_yaml_file(filepath):
    """Process a single YAML file."""
    print(f"Processing {filepath.name}...")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data or 'rules' not in data:
            print(f"  Skipping - no rules found")
            return
        
        # Get source citation
        source = data.get('source', '')
        citation = extract_citation(source)
        print(f"  Using citation: {citation}")
        
        # Update each rule
        updated_count = 0
        for rule in data['rules']:
            if 'management' in rule and rule['management']:
                rule = add_citations_to_management(rule, citation)
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
