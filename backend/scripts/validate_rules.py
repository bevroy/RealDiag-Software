"""
Validate medical rules for completeness, consistency, and currency.

This script checks all rule YAML files for:
- Required metadata fields
- Outdated rules (not reviewed within specified time period)
- Missing citations
- Version consistency
- YAML syntax errors

Usage:
    python validate_rules.py                  # Basic validation
    python validate_rules.py --check-dates    # Check for outdated rules
    python validate_rules.py --check-citations # Check for missing citations
    python validate_rules.py --report         # Generate detailed report
    python validate_rules.py --all            # All checks + report
"""

import yaml
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import argparse

# Configuration
RULES_DIR = Path(__file__).parent.parent / "rules"
TREES_DIR = Path(__file__).parent.parent / "trees"
MAX_AGE_DAYS = 365  # Flag rules older than 1 year
REQUIRED_RULE_FIELDS = [
    "family",
    "version",
    "source",
    "rules"
]

REQUIRED_INDIVIDUAL_RULE_FIELDS = [
    "id",
    "label",
    "icd10",
    "snomed",
    "presentations"
]

RECOMMENDED_FIELDS = [
    "last_updated",
    "citations",
    "evidence_level",
    "guideline_version"
]


class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        
    def add_error(self, file_path, message):
        self.errors.append(f"❌ {file_path}: {message}")
        
    def add_warning(self, file_path, message):
        self.warnings.append(f"⚠️  {file_path}: {message}")
        
    def add_info(self, file_path, message):
        self.info.append(f"ℹ️  {file_path}: {message}")
        
    def has_errors(self):
        return len(self.errors) > 0
        
    def print_summary(self):
        print("\n" + "="*70)
        print("VALIDATION SUMMARY")
        print("="*70)
        
        if self.errors:
            print(f"\n🔴 ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
                
        if self.warnings:
            print(f"\n🟡 WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
                
        if self.info:
            print(f"\n🔵 INFO ({len(self.info)}):")
            for info in self.info:
                print(f"  {info}")
                
        print("\n" + "="*70)
        if not self.errors and not self.warnings:
            print("✅ ALL CHECKS PASSED!")
        elif not self.errors:
            print("✅ VALIDATION PASSED (with warnings)")
        else:
            print("❌ VALIDATION FAILED")
        print("="*70 + "\n")


def load_yaml_file(file_path: Path) -> Tuple[Dict, str]:
    """Load YAML file and return data or error message."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data, None
    except yaml.YAMLError as e:
        return None, f"YAML syntax error: {e}"
    except Exception as e:
        return None, f"Error reading file: {e}"


def validate_rule_file_structure(file_path: Path, result: ValidationResult):
    """Validate basic structure of a rule file."""
    data, error = load_yaml_file(file_path)
    
    if error:
        result.add_error(file_path.name, error)
        return None
        
    # Check required top-level fields
    for field in REQUIRED_RULE_FIELDS:
        if field not in data:
            result.add_error(file_path.name, f"Missing required field: {field}")
            
    # Check recommended fields
    for field in RECOMMENDED_FIELDS:
        if field == "last_updated" and field not in data:
            result.add_warning(file_path.name, f"Missing recommended field: {field}")
            
    # Validate version format (semantic versioning)
    if "version" in data:
        version = data.get("version")
        if not isinstance(version, str):
            result.add_error(file_path.name, f"Version must be a string, got {type(version)}")
        elif not all(part.isdigit() for part in str(version).split(".")):
            result.add_warning(file_path.name, f"Version '{version}' doesn't follow semantic versioning (e.g., 1.0.0)")
            
    return data


def validate_individual_rules(file_path: Path, data: Dict, result: ValidationResult):
    """Validate individual rules within a file."""
    if not data or "rules" not in data:
        return
        
    rules = data.get("rules", [])
    
    for idx, rule in enumerate(rules):
        rule_id = rule.get("id", f"Rule #{idx+1}")
        
        # Check required fields
        for field in REQUIRED_INDIVIDUAL_RULE_FIELDS:
            if field not in rule:
                result.add_error(file_path.name, f"Rule {rule_id}: Missing required field '{field}'")
                
        # Check for empty arrays
        for field in ["icd10", "snomed", "presentations"]:
            if field in rule and not rule[field]:
                result.add_warning(file_path.name, f"Rule {rule_id}: Field '{field}' is empty")
                
        # Check for citations
        if "citations" not in rule or not rule["citations"]:
            result.add_info(file_path.name, f"Rule {rule_id}: No citations provided")


def check_rule_dates(file_path: Path, data: Dict, result: ValidationResult, max_age_days: int):
    """Check if rules are outdated based on last_updated date."""
    if not data:
        return
        
    last_updated = data.get("last_updated")
    
    if not last_updated:
        result.add_warning(file_path.name, "No 'last_updated' date found - unable to verify currency")
        return
        
    try:
        # Try parsing date (supports YYYY-MM-DD format)
        update_date = datetime.strptime(str(last_updated), "%Y-%m-%d")
        age_days = (datetime.now() - update_date).days
        
        if age_days > max_age_days:
            result.add_warning(
                file_path.name, 
                f"Rules are {age_days} days old (last updated: {last_updated}). Consider reviewing."
            )
        elif age_days > max_age_days * 2:
            result.add_error(
                file_path.name,
                f"Rules are VERY outdated ({age_days} days old). Immediate review needed!"
            )
            
    except ValueError:
        result.add_error(file_path.name, f"Invalid date format for 'last_updated': {last_updated} (use YYYY-MM-DD)")


def check_citations(file_path: Path, data: Dict, result: ValidationResult):
    """Check if rules have proper citations."""
    if not data or "rules" not in data:
        return
        
    rules = data.get("rules", [])
    rules_without_citations = []
    
    for rule in rules:
        rule_id = rule.get("id", "Unknown")
        if "citations" not in rule or not rule["citations"]:
            rules_without_citations.append(rule_id)
            
    if rules_without_citations:
        result.add_warning(
            file_path.name,
            f"{len(rules_without_citations)} rules missing citations: {', '.join(rules_without_citations[:5])}"
            + ("..." if len(rules_without_citations) > 5 else "")
        )


def validate_decision_tree(file_path: Path, result: ValidationResult):
    """Validate decision tree YAML files."""
    data, error = load_yaml_file(file_path)
    
    if error:
        result.add_error(file_path.name, error)
        return
        
    # Check required fields
    required_tree_fields = ["id", "title", "entry", "nodes"]
    for field in required_tree_fields:
        if field not in data:
            result.add_error(file_path.name, f"Missing required field: {field}")
            
    # Check for version and last_updated
    if "version" not in data:
        result.add_warning(file_path.name, "No version specified")
    if "last_updated" not in data:
        result.add_warning(file_path.name, "No last_updated date specified")
        
    # Check nodes structure
    if "nodes" in data:
        nodes = data.get("nodes", [])
        for idx, node in enumerate(nodes):
            if "id" not in node:
                result.add_error(file_path.name, f"Node #{idx+1}: Missing 'id' field")


def generate_report(result: ValidationResult, rules_files: List[Path], trees_files: List[Path]):
    """Generate detailed validation report."""
    print("\n" + "="*70)
    print("DETAILED VALIDATION REPORT")
    print("="*70)
    
    print(f"\n📁 Files Checked:")
    print(f"  • Rule files: {len(rules_files)}")
    print(f"  • Decision tree files: {len(trees_files)}")
    print(f"  • Total: {len(rules_files) + len(trees_files)}")
    
    print(f"\n📊 Results:")
    print(f"  • Errors: {len(result.errors)}")
    print(f"  • Warnings: {len(result.warnings)}")
    print(f"  • Info: {len(result.info)}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if result.warnings:
        print("  1. Review and address warnings to improve data quality")
    if any("citations" in w for w in result.warnings):
        print("  2. Add citations to rules for better source attribution")
    if any("last_updated" in w for w in result.warnings):
        print("  3. Add 'last_updated' dates to track rule currency")
    if any("outdated" in w.lower() or "old" in w.lower() for w in result.warnings):
        print("  4. Review and update outdated rules per current guidelines")
        
    print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser(
        description="Validate RealDiag medical rules for completeness and consistency"
    )
    parser.add_argument(
        "--check-dates",
        action="store_true",
        help=f"Check for rules older than {MAX_AGE_DAYS} days"
    )
    parser.add_argument(
        "--check-citations",
        action="store_true",
        help="Check for missing citations"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed validation report"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all checks and generate report"
    )
    parser.add_argument(
        "--max-age",
        type=int,
        default=MAX_AGE_DAYS,
        help=f"Maximum age in days before flagging rules (default: {MAX_AGE_DAYS})"
    )
    
    args = parser.parse_args()
    
    # If --all is specified, enable all checks
    if args.all:
        args.check_dates = True
        args.check_citations = True
        args.report = True
    
    result = ValidationResult()
    
    print("🔍 RealDiag Medical Rules Validator")
    print("="*70)
    
    # Find all rule files
    rules_files = list(RULES_DIR.glob("*.yml")) if RULES_DIR.exists() else []
    trees_files = list(TREES_DIR.glob("*.yml")) if TREES_DIR.exists() else []
    
    if not rules_files and not trees_files:
        print(f"❌ No YAML files found in {RULES_DIR} or {TREES_DIR}")
        return 1
        
    print(f"Found {len(rules_files)} rule files and {len(trees_files)} decision tree files")
    print()
    
    # Validate rule files
    for file_path in rules_files:
        print(f"Checking {file_path.name}...", end=" ")
        
        # Basic structure validation
        data = validate_rule_file_structure(file_path, result)
        
        # Validate individual rules
        if data:
            validate_individual_rules(file_path, data, result)
            
            # Optional: Check dates
            if args.check_dates:
                check_rule_dates(file_path, data, result, args.max_age)
                
            # Optional: Check citations
            if args.check_citations:
                check_citations(file_path, data, result)
                
        print("✓")
    
    # Validate decision tree files
    for file_path in trees_files:
        print(f"Checking {file_path.name}...", end=" ")
        validate_decision_tree(file_path, result)
        print("✓")
    
    # Print results
    result.print_summary()
    
    # Optional: Generate detailed report
    if args.report:
        generate_report(result, rules_files, trees_files)
    
    # Return exit code
    return 1 if result.has_errors() else 0


if __name__ == "__main__":
    sys.exit(main())
