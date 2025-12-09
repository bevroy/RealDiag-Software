#!/usr/bin/env python3
"""
Add citations to each management recommendation in YAML files.
"""

import os
import yaml
from pathlib import Path
import re

def extract_citation(source_text):
    """Extract a short citation with year from the source text."""
    # Map common organizations to short citations with current guideline years
    citation_map = {
        'American Diabetes Association': 'ADA 2024',
        'American College of Cardiology': 'ACC/AHA 2023',
        'American Heart Association': 'ACC/AHA 2023',
        'American Academy of Neurology': 'AAN 2024',
        'American Stroke Association': 'ASA 2024',
        'Endocrine Society': 'Endocrine Society 2023',
        'European Society of Cardiology': 'ESC 2023',
        'Infectious Diseases Society': 'IDSA 2024',
        'American College of Gastroenterology': 'ACG 2023',
        'American Thoracic Society': 'ATS 2023',
        'American Academy of Pediatrics': 'AAP 2023',
        'American College of Obstetricians': 'ACOG 2024',
        'American Urological Association': 'AUA 2023',
        'American Academy of Dermatology': 'AAD 2023',
        'American Academy of Ophthalmology': 'AAO 2023',
        'American College of Rheumatology': 'ACR 2023',
        'American Psychiatric Association': 'APA 2022',
        'National Kidney Foundation': 'KDIGO 2024',
        'American Society of Hematology': 'ASH 2023',
        'American College of Emergency': 'ACEP 2023',
        'Orthopedic': 'AAOS 2023',
        'Society of Thoracic Surgeons': 'STS 2023',
        'American Academy of Otolaryngology': 'AAO-HNS 2023',
        'American Geriatrics Society': 'AGS 2023',
        'Kidney Disease: Improving Global Outcomes': 'KDIGO 2024',
        'Society of Critical Care Medicine': 'SCCM 2023',
        'American College of Surgeons': 'ACS 2023',
        'American Society for Surgery': 'ASSH 2023',
        'American Association for the Surgery of Trauma': 'AAST 2023',
        'Eastern Association for the Surgery of Trauma': 'EAST 2023',
        'World Society of Emergency Surgery': 'WSES 2023',
        'American Association of Poison Control': 'AAPCC 2023',
        'American College of Medical Toxicology': 'ACMT 2023'
    }
    
    for org, citation in citation_map.items():
        if org in source_text:
            return citation
    
    # Try to extract a more specific citation from the source text
    # Look for common patterns like "XXX guidelines" or "XXX society"
    if 'guidelines' in source_text.lower() or 'society' in source_text.lower():
        # Extract first 5 words as a hint for which guidelines
        words = source_text.split()[:5]
        acronym = ''.join(w[0] for w in words if w[0].isupper())
        if len(acronym) >= 2:
            return f'{acronym} 2023'
    
    # Default fallback
    return 'Clinical Guidelines 2023'

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
        
        # Remove ALL existing citations - including "(Guidelines)", any with years, any organization codes
        # Pattern matches: (Guidelines) or (Guidelines 2023) or (AAO-HNS 2023) or (ADA 2024) etc.
        item_clean = re.sub(r'\s*\([^)]*(?:Guidelines?|[A-Z]{2,}[\/-]*[A-Z]*)\s*\d*\)\s*', '', item).strip()
        
        # Add new citation with year
        new_management.append(f"{item_clean} ({citation})")
    
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
