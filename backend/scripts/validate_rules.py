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

import re
import yaml
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import argparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.lab_units import ANALYTES, analyte_for, canonical_unit  # noqa: E402
from services.tree_schema import (  # noqa: E402
    HOMEOPATHY_VALIDATION_STATEMENT,
    missing_branch_targets as branch_target_problems,
    node_format,
    node_list,
    REQUIRED_FIELDS as REQUIRED_TREE_FIELDS,
    REQUIRED_NON_EMPTY as REQUIRED_NON_EMPTY_TREE_FIELDS,
    STATUS_VALUES,
    URGENCY_VALUES,
)

# Trees allowed, for now, to keep a branch that points to a missing node. Their
# content is pending clinical review (docs/CLINICAL_CONTENT_REVIEW.md, section 13)
# and /diagnose does not offer them. Do not add trees here: fix the tree instead.
# backend/tests/test_branch_targets.py fails if this list grows, and the
# validator fails once a listed problem is fixed so the entry is removed.
KNOWN_MISSING_BRANCH_TARGETS = {
    "ID-FEVER": [
        "node 'initial_assessment' next.node points to 'localized_infection', which is not a node in this tree",
    ],
    "PSYCH-PSYCHOSIS": [
        "node 'safety_assessment' next.default points to 'psychotic_disorder_assessment', "
        "which is not a node in this tree",
    ],
}

# Configuration
RULES_DIR = Path(__file__).parent.parent / "rules"
TREES_DIR = Path(__file__).parent.parent / "trees"
SCREENING_RULES = Path(__file__).parent.parent / "screening" / "uspstf_rules.yml"
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
        self.node_formats = {}  # node format -> tree ids (see tree_schema.node_format)
        
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


def find_duplicate_top_level_keys(file_path: Path) -> List[str]:
    """PyYAML silently keeps the last of two identical keys; report them instead."""
    with open(file_path, 'r', encoding='utf-8') as f:
        node = yaml.compose(f)
    if not isinstance(node, yaml.MappingNode):
        return []
    keys = [k.value for k, _ in node.value]
    return sorted({k for k in keys if keys.count(k) > 1})


def validate_decision_tree(file_path: Path, result: ValidationResult):
    """Validate a decision tree against the standard template (services/tree_schema.py)."""
    data, error = load_yaml_file(file_path)
    
    if error:
        result.add_error(file_path.name, error)
        return
    if not isinstance(data, dict):
        result.add_error(file_path.name, "Tree must be a YAML mapping")
        return

    for key in find_duplicate_top_level_keys(file_path):
        result.add_error(file_path.name, f"Duplicate top-level key: {key}")
        
    # Check required fields
    for field in REQUIRED_TREE_FIELDS:
        if field not in data:
            result.add_error(file_path.name, f"Missing required field: {field}")
    for field in REQUIRED_NON_EMPTY_TREE_FIELDS:
        if field in data and not data.get(field):
            result.add_error(file_path.name, f"Required field is empty: {field}")

    # Urgency must be one of the standard values
    urgency = data.get("urgency")
    if "urgency" in data and urgency in ("", None):
        result.add_error(file_path.name, f"Urgency is empty (use one of: {', '.join(URGENCY_VALUES)})")
    elif "urgency" in data and urgency not in URGENCY_VALUES:
        result.add_error(
            file_path.name,
            f"Non-standard urgency {urgency!r} (use one of: {', '.join(URGENCY_VALUES)})"
        )

    if "status" in data and data.get("status") not in STATUS_VALUES:
        result.add_error(file_path.name, f"Invalid status {data.get('status')!r} (use one of: {', '.join(STATUS_VALUES)})")
    if "version" in data and not isinstance(data.get("version"), str):
        result.add_error(file_path.name, f"Version must be a string, got {type(data.get('version')).__name__}")
    if "secondary_specialties" in data and not isinstance(data.get("secondary_specialties"), list):
        result.add_error(file_path.name, "secondary_specialties must be a list")

    codes = data.get("codes")
    if "codes" in data:
        if not isinstance(codes, dict):
            result.add_error(file_path.name, "codes must be a mapping with icd10, snomed and icpc2 lists")
        else:
            for system in ("icd10", "snomed", "icpc2"):
                if not isinstance(codes.get(system), list):
                    result.add_error(file_path.name, f"codes.{system} must be a list")

    applies = data.get("applies_to")
    if "applies_to" in data:
        if not isinstance(applies, dict) or not {"sex", "age_min", "age_max"} <= set(applies):
            result.add_error(file_path.name, "applies_to must be a mapping with sex, age_min and age_max")
        elif applies.get("sex") not in (None, "male", "female"):
            result.add_error(file_path.name, f"applies_to.sex must be male, female or empty, got {applies.get('sex')!r}")

    homeopathy = data.get("homeopathy")
    if "homeopathy" in data:
        if not isinstance(homeopathy, dict) or not isinstance(homeopathy.get("remedies"), list):
            result.add_error(file_path.name, "homeopathy must be a mapping with validation_statement and a remedies list")
        elif homeopathy.get("validation_statement") != HOMEOPATHY_VALIDATION_STATEMENT and homeopathy.get("remedies"):
            result.add_warning(file_path.name, "homeopathy.validation_statement differs from the standard statement")

    if "sources" in data and not isinstance(data.get("sources"), list):
        result.add_error(file_path.name, "sources must be a list")
    if "change_log" in data and not (isinstance(data.get("change_log"), list) and data["change_log"]):
        result.add_error(file_path.name, "change_log must be a non-empty list")

    # Check nodes structure (list of nodes, or mapping of id -> node)
    nodes = data.get("nodes") or []
    if isinstance(nodes, list):
        for idx, node in enumerate(nodes):
            if not isinstance(node, dict) or "id" not in node:
                result.add_error(file_path.name, f"Node #{idx+1}: Missing 'id' field")
    elif not isinstance(nodes, dict):
        result.add_error(file_path.name, "nodes must be a list or mapping")
        return
    if nodes:
        node_ids = {n.get("id") for n in node_list(data)}
        entry = data.get("entry_point")
        if not entry:
            result.add_error(file_path.name, "Tree has nodes but no entry_point")
        elif entry not in node_ids:
            result.add_error(file_path.name, f"entry_point '{entry}' does not match any node id")

    known = KNOWN_MISSING_BRANCH_TARGETS.get(file_path.stem, [])
    problems = branch_target_problems(data)
    for problem in problems:
        if problem in known:
            result.add_warning(file_path.name, f"{problem} (known exception, pending clinical review)")
        else:
            result.add_error(file_path.name, problem)
    for problem in known:
        if problem not in problems:
            result.add_error(file_path.name, f"Fixed: remove this entry from KNOWN_MISSING_BRANCH_TARGETS: {problem}")

    fmt = node_format(data)
    result.node_formats[fmt] = result.node_formats.get(fmt, []) + [file_path.stem]
    if fmt == "content":
        count = len(node_list(data))
        shape = "a single node" if count == 1 else f"{count} nodes"
        result.add_warning(
            file_path.name,
            f"Tree has {shape} and no decision branches; the engine reports it as not evaluated"
        )

    for problem in criteria_problems(data.get("criteria")):
        result.add_error(file_path.name, f"criteria: {problem}")

    for problem in list_item_problems(data):
        result.add_error(file_path.name, problem)


# Fields whose entries are structured data rather than display text.
STRUCTURED_FIELDS = {"sources", "change_log", "nodes", "criteria", "codes", "applies_to", "homeopathy",
                     "entry_point", "metadata"}
# differentials may group diagnoses: {category, diagnoses[, origin]}
DIFFERENTIAL_GROUP_KEYS = {"category", "diagnoses", "origin"}


def list_item_problems(tree: Dict) -> List[str]:
    """Text-list items must be plain text (or a heading over a nested list).

    An unquoted "- Chest pain: substernal ..." loads as a key-value pair,
    not text, and is dropped or mangled by code that expects text. Quote it.
    """
    problems: List[str] = []

    def check(value, path: str, field: str):
        if isinstance(value, dict):
            for key, inner in value.items():
                check(inner, f"{path}.{key}", field)
            return
        if not isinstance(value, list):
            return
        for i, item in enumerate(value):
            where = f"{path}[{i}]"
            if isinstance(item, str) or item is None:
                continue
            if isinstance(item, dict):
                keys = set(map(str, item))
                if len(item) == 1 and isinstance(next(iter(item.values())), list):
                    check(next(iter(item.values())), where, field)      # heading over a nested list
                    continue
                if field == "differentials" and keys <= DIFFERENTIAL_GROUP_KEYS and "diagnoses" in keys:
                    check(item.get("diagnoses"), f"{where}.diagnoses", field)
                    continue
                if len(item) == 1:
                    key, inner = next(iter(item.items()))
                    text = f"{key}: {inner}" if inner is not None else f"{key}:"
                    problems.append(f"{where} loads as a key-value pair, not text; quote it: '{text[:80]}'")
                else:
                    problems.append(f"{where} is a mapping ({', '.join(sorted(keys))}), not text")
            elif isinstance(item, list):
                check(item, where, field)
            else:
                problems.append(f"{where} is {type(item).__name__}, not text; quote it: '{item}'")

    for field, value in tree.items():
        if field not in STRUCTURED_FIELDS:
            check(value, field, field)
    return problems


CRITERIA_OPERATORS = {">", ">=", "<", "<=", "between", "at_least_below", "outside", "above_ref_high", "below_ref_low"}
CRITERIA_ROLES = {"core", "supporting"}
CRITERIA_DISPLAY = {"always", "when_met", "when_found"}
CRITERIA_PROBABILITY = {"met_over_all", "met_over_known"}
SEVERITY_LEVELS = {"low", "moderate", "high", "critical", "unknown", "not rated"}
SEVERITY_RULE_TYPES = {"reference_multiple", "count_met", "unusable", "value", "any_met", "all_groups"}
LOINC_PATTERN = re.compile(r"^\d{1,7}-\d$")


def criteria_problems(criteria) -> List[str]:
    """Problems in a tree's `criteria` section (empty list = valid).

    `criteria: []` means the tree has no chart-evaluation criteria.
    """
    if criteria in (None, []):
        return []
    if not isinstance(criteria, dict):
        return ["must be a mapping with an 'items' list (or [] for none)"]
    problems = []
    for key in ("finding_label", "source"):
        if not str(criteria.get(key) or "").strip():
            problems.append(f"missing '{key}'")
    if criteria.get("display", "always") not in CRITERIA_DISPLAY:
        problems.append(f"display must be one of {sorted(CRITERIA_DISPLAY)}")
    meds = criteria.get("related_medications")
    if meds is not None and (not isinstance(meds, list) or not meds
                             or not all(isinstance(m, str) and m.strip(" *") for m in meds)):
        problems.append("related_medications must be a non-empty list of names ('*suffix' allowed)")
    terms = criteria.get("complaint_terms")
    if terms is not None and (not isinstance(terms, list) or not terms
                              or not all(isinstance(t, str) and t.strip() for t in terms)):
        problems.append("complaint_terms must be a non-empty list of non-empty strings")
    if criteria.get("probability", "met_over_known") not in CRITERIA_PROBABILITY:
        problems.append(f"probability must be one of {sorted(CRITERIA_PROBABILITY)}")
    if criteria.get("severity_default", "not rated") not in SEVERITY_LEVELS:
        problems.append(f"severity_default must be one of {sorted(SEVERITY_LEVELS)}")
    suppressed_by = criteria.get("suppressed_by")
    if suppressed_by is not None and (not isinstance(suppressed_by, list) or not suppressed_by
                                      or not all(isinstance(t, str) and t.strip() for t in suppressed_by)):
        problems.append("suppressed_by must be a non-empty list of tree ids")

    items = criteria.get("items")
    if not isinstance(items, list) or not items:
        return problems + ["'items' must be a non-empty list"]
    ids = set()
    groups = {i.get("group") for i in items if isinstance(i, dict) and i.get("group")}
    for index, item in enumerate(items):
        where = f"item {item.get('id', index + 1)}" if isinstance(item, dict) else f"item {index + 1}"
        if not isinstance(item, dict):
            problems.append(f"{where}: must be a mapping")
            continue
        if item.get("resource") == "problem_list":
            for key in ("id", "label", "source"):
                if not str(item.get(key) or "").strip():
                    problems.append(f"{where}: missing '{key}'")
            if not (item.get("icd10_prefixes") or item.get("snomed")):
                problems.append(f"{where}: problem_list items need icd10_prefixes or snomed codes")
            if item.get("id") in ids:
                problems.append(f"{where}: duplicate id")
            ids.add(item.get("id"))
            continue
        for key in ("id", "label", "loinc", "operator", "unit", "source"):
            if item.get(key) in (None, "", []):
                problems.append(f"{where}: missing '{key}'")
        if item.get("id") in ids:
            problems.append(f"{where}: duplicate id")
        ids.add(item.get("id"))
        codes = item.get("loinc") or []
        if not isinstance(codes, list) or not all(LOINC_PATTERN.match(str(c)) for c in codes):
            problems.append(f"{where}: loinc must be a list of LOINC codes like '4548-4'")
            codes = []
        if item.get("resource", "lab") not in ("lab", "vital"):
            problems.append(f"{where}: resource must be 'lab', 'vital' or 'problem_list'")
        if "aggregate" in item and item["aggregate"] != "daily_mean":
            problems.append(f"{where}: aggregate must be 'daily_mean'")
        for key in ("min_days", "max_days"):
            if key in item and not (isinstance(item[key], int) and item[key] > 0):
                problems.append(f"{where}: {key} must be a positive whole number")
        if item.get("role", "core") not in CRITERIA_ROLES:
            problems.append(f"{where}: role must be one of {sorted(CRITERIA_ROLES)}")
        op = item.get("operator")
        if op not in CRITERIA_OPERATORS:
            problems.append(f"{where}: unknown operator {op!r}")
        value = item.get("value")
        if op in (">", ">=", "<", "<=") and not isinstance(value, (int, float)):
            problems.append(f"{where}: operator {op} needs a numeric 'value'")
        if op in ("between", "at_least_below", "outside") and not (
                isinstance(value, list) and len(value) == 2 and all(isinstance(v, (int, float)) for v in value)
                and value[0] < value[1]):
            problems.append(f"{where}: operator {op} needs 'value: [low, high]' with low < high")
        if op in ("above_ref_high", "below_ref_low") and value is not None:
            problems.append(f"{where}: operator {op} compares with the lab's reference range; remove 'value'")
        for key in ("lookback_days", "min_occurrences", "min_span_days"):
            if key in item and not (isinstance(item[key], int) and item[key] > 0):
                problems.append(f"{where}: {key} must be a positive whole number")
        sex = (item.get("applies_to") or {}).get("sex")
        if sex not in (None, "male", "female"):
            problems.append(f"{where}: applies_to.sex must be male or female")
        # Unit: must be the analyte's canonical unit when units are checked
        analytes = {analyte_for(c) for c in codes}
        if item.get("unit_check", True) and codes:
            analyte = item.get("analyte") or (analytes.pop() if len(analytes) == 1 else None)
            if analyte is None or analyte not in ANALYTES:
                problems.append(f"{where}: no unit conversion is defined for LOINC {codes} "
                                "(add it to lab_units.py or set unit_check: false)")
            elif str(item.get("unit")) != canonical_unit(analyte):
                problems.append(f"{where}: unit must be {canonical_unit(analyte)!r} for {analyte} "
                                f"(results are converted to it), not {item.get('unit')!r}")

    for rule in criteria.get("severity") or []:
        kind = rule.get("type") if isinstance(rule, dict) else None
        if kind not in SEVERITY_RULE_TYPES:
            problems.append(f"severity rule {rule!r}: unknown type")
            continue
        refs = [rule["item"]] if "item" in rule else list(rule.get("items", []))
        for ref in refs:
            if ref not in ids:
                problems.append(f"severity rule {kind}: refers to unknown item {ref!r}")
        for group in rule.get("groups", []) + ([rule["group"]] if rule.get("group") else []):
            if group not in groups:
                problems.append(f"severity rule {kind}: refers to unknown group {group!r}")
        if "level" in rule and rule["level"] not in SEVERITY_LEVELS:
            problems.append(f"severity rule {kind}: unknown level {rule['level']!r}")
    for key in ("suggest_when", "confirm", "known_condition"):
        if key in criteria and not isinstance(criteria[key], dict):
            problems.append(f"'{key}' must be a mapping")

    def check_rule(rule):
        if not isinstance(rule, dict):
            problems.append("suggest_when rules must be mappings")
            return
        for sub in rule.get("any", []):
            check_rule(sub)
        for group in rule.get("all_groups", []) + ([rule["group"]] if rule.get("group") else []):
            if group not in groups:
                problems.append(f"suggest_when refers to unknown group {group!r}")
    if isinstance(criteria.get("suggest_when"), dict):
        check_rule(criteria["suggest_when"])
    return problems


def suppressed_by_problems(trees: Dict[str, Dict]) -> List[Tuple[str, str]]:
    """(tree id, problem) for `criteria.suppressed_by` entries that cannot work.

    Each entry must name another tree whose criteria declare known_condition
    codes; those codes are what suppress the finding.
    """
    problems = []
    for tree_id, tree in sorted(trees.items()):
        criteria = tree.get("criteria")
        if not isinstance(criteria, dict) or not isinstance(criteria.get("suppressed_by"), list):
            continue
        for other_id in criteria["suppressed_by"]:
            other = trees.get(other_id)
            other_criteria = (other or {}).get("criteria")
            if other_id == tree_id:
                problems.append((tree_id, "criteria.suppressed_by: a tree cannot suppress itself"))
            elif other is None:
                problems.append((tree_id, f"criteria.suppressed_by: unknown tree {other_id!r}"))
            elif not isinstance(other_criteria, dict) or not other_criteria.get("known_condition"):
                problems.append((tree_id, f"criteria.suppressed_by: {other_id} has no criteria.known_condition codes"))
    return problems


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


SCREENING_EVIDENCE_KINDS = {"lab", "vital", "procedure", "imaging"}
SCREENING_STATUSES = {"draft", "review", "approved", "retired"}


def screening_rule_problems(data: Dict) -> List[str]:
    """Each screening rule needs an id, title, status, cited source, population and evidence."""
    problems: List[str] = []
    rules = data.get("rules")
    if not isinstance(rules, list) or not rules:
        return ["rules must be a non-empty list"]
    seen = set()
    for i, rule in enumerate(rules):
        where = f"rules[{i}] ({rule.get('id', '?') if isinstance(rule, dict) else '?'})"
        if not isinstance(rule, dict):
            problems.append(f"{where}: must be a mapping")
            continue
        for key in ("id", "title", "status", "source", "population", "evidence", "grades"):
            if not rule.get(key):
                problems.append(f"{where}: missing {key}")
        if rule.get("id") in seen:
            problems.append(f"{where}: duplicate id")
        seen.add(rule.get("id"))
        if rule.get("status") and rule["status"] not in SCREENING_STATUSES:
            problems.append(f"{where}: status must be one of {sorted(SCREENING_STATUSES)}")
        source = rule.get("source") or {}
        if not (isinstance(source, dict) and source.get("citation") and str(source.get("url", "")).startswith("https://")):
            problems.append(f"{where}: source needs citation and https url")
        population = rule.get("population") or {}
        if population.get("sex") not in (None, "male", "female"):
            problems.append(f"{where}: population.sex must be male or female")
        if population.get("smoking") not in (None, "ever"):
            problems.append(f"{where}: population.smoking must be 'ever'")
        for j, ev in enumerate(rule.get("evidence") or []):
            kind = ev.get("kind")
            if kind not in SCREENING_EVIDENCE_KINDS:
                problems.append(f"{where}: evidence[{j}].kind must be one of {sorted(SCREENING_EVIDENCE_KINDS)}")
            if kind in ("lab", "vital") and not all(LOINC_PATTERN.match(str(c)) for c in ev.get("loinc") or [None]):
                problems.append(f"{where}: evidence[{j}] needs valid LOINC codes")
            if kind in ("procedure", "imaging") and not ev.get("keywords"):
                problems.append(f"{where}: evidence[{j}] needs keywords")
            years = ev.get("within_years")
            if years is not None and (not isinstance(years, (int, float)) or years <= 0):
                problems.append(f"{where}: evidence[{j}].within_years must be positive or null")
    return problems


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
    
    # criteria.suppressed_by must name trees with known_condition codes
    loaded_trees = {}
    for file_path in trees_files:
        data = yaml.safe_load(file_path.read_text(encoding="utf-8")) or {}
        if isinstance(data, dict):
            loaded_trees[str(data.get("tree_id") or file_path.stem)] = data
    for tree_id, problem in suppressed_by_problems(loaded_trees):
        result.add_error(f"{tree_id}.yml", problem)

    # Screening rules (encounter assessment: possible missed items)
    if SCREENING_RULES.exists():
        print(f"Checking {SCREENING_RULES.name}...", end=" ")
        data = yaml.safe_load(SCREENING_RULES.read_text(encoding="utf-8")) or {}
        for problem in screening_rule_problems(data):
            result.add_error(SCREENING_RULES.name, problem)
        print("✓")

    # Node formats: only "conditional" trees are evaluated automatically by the engine
    if result.node_formats:
        print("\nNode formats:")
        for fmt, ids in sorted(result.node_formats.items()):
            listed = f": {', '.join(sorted(ids))}" if fmt not in ("none", "conditional") else ""
            print(f"  • {fmt} ({len(ids)}){listed}")

    # Print results
    result.print_summary()
    
    # Optional: Generate detailed report
    if args.report:
        generate_report(result, rules_files, trees_files)
    
    # Return exit code
    return 1 if result.has_errors() else 0


if __name__ == "__main__":
    sys.exit(main())
