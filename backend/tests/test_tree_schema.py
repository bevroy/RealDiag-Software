import importlib.util
from pathlib import Path

import yaml

from backend.services.decision_tree_engine import DecisionTreeEngine
from backend.services.rules_engine import RulesEngine
from backend.services.tree_schema import TEMPLATE_FIELDS, URGENCY_VALUES

TREES_DIR = Path(__file__).resolve().parents[1] / "trees"
VALIDATOR = Path(__file__).resolve().parents[1] / "scripts" / "validate_rules.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location("validate_rules", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _validate(path):
    validator = _load_validator()
    result = validator.ValidationResult()
    validator.validate_decision_tree(path, result)
    return result


def _valid_tree():
    tree = {field: [] for field in TEMPLATE_FIELDS}
    tree.update({
        "tree_id": "TEST-TREE", "name": "Test", "version": "1.0", "status": "draft",
        "family": "Test", "specialty": "Test", "urgency": "routine", "urgency_explanation": "",
        "chief_complaint": "", "description": "", "entry_point": "",
        "applies_to": {"sex": None, "age_min": None, "age_max": None},
        "codes": {"icd10": [], "snomed": [], "icpc2": []},
        "homeopathy": {"validation_statement": "This content has not been clinically validated.", "remedies": []},
        "disposition_guidance": {}, "special_populations": {},
        "change_log": [{"date": "2026-10-19", "version": "1.0", "change": "Standardized to template"}],
    })
    return tree


def test_all_trees_pass_validation():
    validator = _load_validator()
    result = validator.ValidationResult()
    files = sorted(TREES_DIR.glob("*.yml"))
    assert files
    for path in files:
        validator.validate_decision_tree(path, result)
    assert result.errors == []


def test_all_trees_load_in_engines():
    count = len(list(TREES_DIR.glob("*.yml")))
    assert len(DecisionTreeEngine().trees) == count
    rules = RulesEngine().rule_sets
    assert sum(len(f["rules"]) for f in rules.values()) == count


def test_validator_accepts_template_tree(tmp_path):
    path = tmp_path / "TEST-TREE.yml"
    path.write_text(yaml.safe_dump(_valid_tree(), sort_keys=False))
    assert _validate(path).errors == []


def test_validator_rejects_nonstandard_urgency(tmp_path):
    tree = _valid_tree()
    tree["urgency"] = "High"
    path = tmp_path / "TEST-TREE.yml"
    path.write_text(yaml.safe_dump(tree, sort_keys=False))
    errors = _validate(path).errors
    assert any("Non-standard urgency" in e for e in errors)
    assert "High" not in URGENCY_VALUES


def test_validator_rejects_empty_urgency(tmp_path):
    tree = _valid_tree()
    tree["urgency"] = ""
    path = tmp_path / "TEST-TREE.yml"
    path.write_text(yaml.safe_dump(tree, sort_keys=False))
    assert any("Urgency is empty" in e for e in _validate(path).errors)


def test_validator_rejects_missing_field(tmp_path):
    tree = _valid_tree()
    del tree["codes"]
    path = tmp_path / "TEST-TREE.yml"
    path.write_text(yaml.safe_dump(tree, sort_keys=False))
    assert any("Missing required field: codes" in e for e in _validate(path).errors)


def test_validator_rejects_duplicate_keys(tmp_path):
    path = tmp_path / "TEST-TREE.yml"
    path.write_text(yaml.safe_dump(_valid_tree(), sort_keys=False) + "treatment: []\n")
    assert any("Duplicate top-level key: treatment" in e for e in _validate(path).errors)


def test_validator_rejects_nodes_without_entry_point(tmp_path):
    tree = _valid_tree()
    tree["nodes"] = [{"id": "start", "when": {}}]
    tree["entry_point"] = ""
    path = tmp_path / "TEST-TREE.yml"
    path.write_text(yaml.safe_dump(tree, sort_keys=False))
    assert any("no entry_point" in e for e in _validate(path).errors)


def test_validator_rejects_entry_point_not_matching_node(tmp_path):
    tree = _valid_tree()
    tree["nodes"] = [{"id": "start", "when": {}}]
    tree["entry_point"] = "missing"
    path = tmp_path / "TEST-TREE.yml"
    path.write_text(yaml.safe_dump(tree, sort_keys=False))
    assert any("does not match any node id" in e for e in _validate(path).errors)


def test_validator_flags_single_node_without_branches(tmp_path):
    tree = _valid_tree()
    tree["nodes"] = [{"id": "evaluation", "type": "diagnosis", "workup": ["BMI"]}]
    tree["entry_point"] = "evaluation"
    path = tmp_path / "TEST-TREE.yml"
    path.write_text(yaml.safe_dump(tree, sort_keys=False))
    result = _validate(path)
    assert result.errors == []
    assert any("single node and no decision branches" in w for w in result.warnings)
