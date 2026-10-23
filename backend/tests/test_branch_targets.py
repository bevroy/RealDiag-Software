"""
The validator rejects a tree whose branch or answer option points to a node id
the tree does not contain (the walk stops there with end_reason "missing_node").
"""
import importlib.util
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
TREES_DIR = ROOT / "trees"

# The two trees allowed, for now, to keep a missing branch target (pending
# clinical review). This must only ever shrink.
ALLOWED_EXCEPTIONS = {"ID-FEVER", "PSYCH-PSYCHOSIS"}


@pytest.fixture(scope="module")
def validator():
    spec = importlib.util.spec_from_file_location("validate_rules", ROOT / "scripts" / "validate_rules.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _tree(nodes):
    return {"tree_id": "T", "entry_point": nodes[0]["id"], "nodes": nodes}


def test_valid_targets_and_end_markers_pass(validator):
    tree = _tree([
        {"id": "a", "next": [{"if": {"symptoms_contains_any": ["x"]}, "node": "b"}, {"default": True, "node": "c"}]},
        {"id": "b", "next": [{"when": {"rapid_strep": "positive"}, "go": "c"}, {"default": "c"}]},
        {"id": "c", "next": [{"default": None}]},
    ])
    assert validator.branch_target_problems(tree) == []


@pytest.mark.parametrize("branch,where", [
    ({"if": {"symptoms_contains_any": ["x"]}, "node": "gone"}, "next.node"),
    ({"default": True, "node": "gone"}, "next.node"),
    ({"when": {"fever": ">38.5"}, "go": "gone"}, "next.go"),
    ({"default": "gone"}, "next.default"),
])
def test_missing_conditional_target_is_rejected(validator, branch, where):
    tree = _tree([{"id": "a", "next": [branch]}, {"id": "b"}])
    assert validator.branch_target_problems(tree) == [
        f"node 'a' {where} points to 'gone', which is not a node in this tree"]


def test_missing_questionnaire_option_target_is_rejected(validator):
    tree = _tree([
        {"id": "q", "type": "question", "text": "Fever?",
         "options": [{"label": "Yes", "next": "dx"}, {"label": "No", "next": "gone"}]},
        {"id": "dx", "type": "diagnosis", "diagnosis": "A"},
    ])
    assert validator.branch_target_problems(tree) == [
        "node 'q' options[1].next points to 'gone', which is not a node in this tree"]


def test_mapping_style_nodes_are_checked(validator):
    tree = {"tree_id": "T", "entry_point": "a", "nodes": {"a": {"next": [{"default": "gone"}]}}}
    assert validator.branch_target_problems(tree) == [
        "node 'a' next.default points to 'gone', which is not a node in this tree"]


def test_known_exceptions_list_does_not_grow(validator):
    added = set(validator.KNOWN_MISSING_BRANCH_TARGETS) - ALLOWED_EXCEPTIONS
    assert not added, (
        f"Trees added to KNOWN_MISSING_BRANCH_TARGETS: {sorted(added)}. "
        "Fix the tree's branch instead of adding an exception.")


def test_only_the_known_exceptions_have_missing_targets(validator):
    found = {}
    for path in sorted(TREES_DIR.glob("*.yml")):
        problems = validator.branch_target_problems(yaml.safe_load(path.read_text()) or {})
        if problems:
            found[path.stem] = problems
    assert found == validator.KNOWN_MISSING_BRANCH_TARGETS


def test_known_exception_is_a_warning_not_an_error(validator):
    result = validator.ValidationResult()
    validator.validate_decision_tree(TREES_DIR / "ID-FEVER.yml", result)
    assert not any("localized_infection" in e for e in result.errors)
    assert any("localized_infection" in w and "known exception" in w for w in result.warnings)


def test_any_other_missing_target_is_an_error(validator, tmp_path):
    tree = yaml.safe_load((TREES_DIR / "ENT-SORE-THROAT.yml").read_text())
    tree["nodes"][0]["next"].append({"default": "no_such_step"})
    path = tmp_path / "ENT-SORE-THROAT.yml"
    path.write_text(yaml.safe_dump(tree, sort_keys=False))
    result = validator.ValidationResult()
    validator.validate_decision_tree(path, result)
    assert any("no_such_step" in e for e in result.errors)


def test_fixed_exception_must_be_removed(validator, tmp_path):
    tree = yaml.safe_load((TREES_DIR / "ID-FEVER.yml").read_text())
    nodes = tree["nodes"].values() if isinstance(tree["nodes"], dict) else tree["nodes"]
    for node in nodes:
        branches = node.get("next") if isinstance(node, dict) and isinstance(node.get("next"), list) else []
        for branch in branches:
            if isinstance(branch, dict) and branch.get("node") == "localized_infection":
                branch["node"] = None
    path = tmp_path / "ID-FEVER.yml"
    path.write_text(yaml.safe_dump(tree, sort_keys=False))
    result = validator.ValidationResult()
    validator.validate_decision_tree(path, result)
    assert any("remove this entry from KNOWN_MISSING_BRANCH_TARGETS" in e for e in result.errors)
