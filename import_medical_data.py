"""
RealDiag Medical Data Import Framework
=======================================

This script provides utilities for importing and standardizing medical diagnostic data
from various formats (CSV, JSON, YAML) into the RealDiag system.

Usage:
    python import_medical_data.py --source data.csv --format csv --family neurology
    python import_medical_data.py --update-csv  # Regenerate diagnosis_codes_all.csv
"""

import yaml
import csv
import json
from pathlib import Path
from typing import List, Dict, Any
import argparse


class MedicalDataImporter:
    """Import and standardize medical diagnostic data."""
    
    def __init__(self, rules_dir: Path = None, csv_output: Path = None):
        self.rules_dir = rules_dir or Path(__file__).parent / "backend" / "rules"
        self.csv_output = csv_output or Path(__file__).parent / "frontend" / "public" / "diagnosis_codes_all.csv"
        
    def load_yaml_family(self, family: str) -> Dict[str, Any]:
        """Load a YAML rules file for a specific family."""
        yaml_file = self.rules_dir / f"{family}.yml"
        if not yaml_file.exists():
            raise FileNotFoundError(f"Rules file not found: {yaml_file}")
            
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data
    
    def get_all_families(self) -> List[str]:
        """Get list of all available disease families."""
        families = []
        for yaml_file in self.rules_dir.glob("*.yml"):
            families.append(yaml_file.stem)
        return sorted(families)
    
    def import_from_csv(self, csv_file: Path, family: str) -> List[Dict[str, Any]]:
        """
        Import diagnoses from CSV file.
        
        Expected CSV columns:
        - rule_id: Unique identifier (e.g., NEU-STROKE)
        - label: Human-readable diagnosis name
        - presentations: Semicolon-separated list of symptoms
        - icd10: Comma-separated ICD-10 codes
        - snomed: Optional SNOMED CT codes
        """
        rules = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rule = {
                    'id': row['rule_id'],
                    'label': row['label'],
                    'presentations': [p.strip() for p in row['presentations'].split(';') if p.strip()],
                    'icd10': [c.strip() for c in row['icd10'].split(',') if c.strip()],
                }
                if 'snomed' in row and row['snomed']:
                    rule['snomed'] = [c.strip() for c in row['snomed'].split(',') if c.strip()]
                rules.append(rule)
        return rules
    
    def export_to_yaml(self, rules: List[Dict[str, Any]], family: str, output_file: Path = None):
        """Export rules to YAML format."""
        if output_file is None:
            output_file = self.rules_dir / f"{family}.yml"
        
        data = {
            'family': family,
            'version': '0.1.0',
            'source': f'RealDiag {family.title()} Core Rules',
            'rules': rules
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    def regenerate_csv_export(self):
        """Regenerate the comprehensive CSV export from all YAML files."""
        print(f"Regenerating CSV export from {self.rules_dir}...")
        
        all_rows = []
        families = self.get_all_families()
        
        for family in families:
            print(f"  Processing {family}...")
            try:
                data = self.load_yaml_family(family)
                rules = data.get('rules', [])
                
                for rule in rules:
                    row = {
                        'family': family,
                        'rule_id': rule['id'],
                        'label': rule['label'],
                        'icd10_codes': ', '.join(rule.get('icd10', []))
                    }
                    all_rows.append(row)
                    
                print(f"    Added {len(rules)} rules from {family}")
            except Exception as e:
                print(f"    Error processing {family}: {e}")
        
        # Write CSV
        self.csv_output.parent.mkdir(parents=True, exist_ok=True)
        with open(self.csv_output, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['family', 'rule_id', 'label', 'icd10_codes']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)
        
        print(f"\nSuccessfully wrote {len(all_rows)} diagnoses to {self.csv_output}")
        print(f"Families included: {', '.join(families)}")
    
    def validate_yaml_structure(self, family: str) -> List[str]:
        """Validate YAML file structure and return list of issues."""
        issues = []
        try:
            data = self.load_yaml_family(family)
            
            if 'rules' not in data:
                issues.append("Missing 'rules' key")
                return issues
            
            for idx, rule in enumerate(data['rules']):
                rule_id = rule.get('id', f'[rule {idx}]')
                
                # Check required fields
                if 'id' not in rule:
                    issues.append(f"{rule_id}: Missing 'id' field")
                if 'label' not in rule:
                    issues.append(f"{rule_id}: Missing 'label' field")
                if 'presentations' not in rule:
                    issues.append(f"{rule_id}: Missing 'presentations' field")
                if 'icd10' not in rule:
                    issues.append(f"{rule_id}: Missing 'icd10' field")
                
                # Check field types
                if 'presentations' in rule and not isinstance(rule['presentations'], list):
                    issues.append(f"{rule_id}: 'presentations' should be a list")
                if 'icd10' in rule and not isinstance(rule['icd10'], list):
                    issues.append(f"{rule_id}: 'icd10' should be a list")
                
        except Exception as e:
            issues.append(f"Error loading file: {e}")
        
        return issues
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the medical data."""
        families = self.get_all_families()
        stats = {
            'total_families': len(families),
            'families': {},
            'total_diagnoses': 0
        }
        
        for family in families:
            try:
                data = self.load_yaml_family(family)
                rule_count = len(data.get('rules', []))
                stats['families'][family] = {
                    'rule_count': rule_count,
                    'version': data.get('version', 'unknown')
                }
                stats['total_diagnoses'] += rule_count
            except Exception as e:
                stats['families'][family] = {
                    'error': str(e)
                }
        
        return stats


def main():
    parser = argparse.ArgumentParser(
        description='RealDiag Medical Data Import Framework'
    )
    parser.add_argument(
        '--update-csv',
        action='store_true',
        help='Regenerate diagnosis_codes_all.csv from YAML files'
    )
    parser.add_argument(
        '--import-csv',
        type=Path,
        help='Import diagnoses from CSV file'
    )
    parser.add_argument(
        '--family',
        type=str,
        help='Disease family name (required for CSV import)'
    )
    parser.add_argument(
        '--validate',
        type=str,
        help='Validate YAML structure for a family'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Display statistics about medical data'
    )
    
    args = parser.parse_args()
    importer = MedicalDataImporter()
    
    if args.update_csv:
        importer.regenerate_csv_export()
    
    elif args.import_csv:
        if not args.family:
            print("Error: --family is required when using --import-csv")
            return 1
        
        rules = importer.import_from_csv(args.import_csv, args.family)
        importer.export_to_yaml(rules, args.family)
        print(f"Imported {len(rules)} rules to {args.family}.yml")
    
    elif args.validate:
        issues = importer.validate_yaml_structure(args.validate)
        if issues:
            print(f"Validation issues found in {args.validate}:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"✓ {args.validate}.yml is valid")
    
    elif args.stats:
        stats = importer.get_statistics()
        print(f"\nRealDiag Medical Data Statistics")
        print(f"=" * 50)
        print(f"Total Families: {stats['total_families']}")
        print(f"Total Diagnoses: {stats['total_diagnoses']}")
        print(f"\nBy Family:")
        for family, data in stats['families'].items():
            if 'error' in data:
                print(f"  {family}: ERROR - {data['error']}")
            else:
                print(f"  {family}: {data['rule_count']} rules (v{data['version']})")
    
    else:
        parser.print_help()
    
    return 0


if __name__ == '__main__':
    exit(main())
