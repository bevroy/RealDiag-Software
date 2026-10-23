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

# Current tree content with a missing branch target. Reported, not edited; when a
# tree is fixed, remove it here.
TREES_WITH_MISSING_TARGETS = {
    "ID-FEVER": ["node 'initial_assessment' next.node points to 'localized_infection', "
                 "which is not a node in this tree"],
    "PSYCH-PSYCHOSIS": ["node 'safety_assessment' next.default points to 'psychotic_disorder_assessment', "
                        "which is not a node in this tree"],
}


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


def test_current_trees_with_missing_targets(validator):
    found = {}
    for path in sorted(TREES_DIR.glob("*.yml")):
        problems = validator.branch_target_problems(yaml.safe_load(path.read_text()) or {})
        if problems:
            found[path.stem] = problems
    assert found == TREES_WITH_MISSING_TARGETS


def test_validate_decision_tree_reports_it_as_an_error(validator):
    result = validator.ValidationResult()
    validator.validate_decision_tree(TREES_DIR / "ID-FEVER.yml", result)
    assert any("localized_infection" in e for e in result.errors)
