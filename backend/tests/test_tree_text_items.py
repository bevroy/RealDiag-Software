"""
Text-list items in trees must load as text. An unquoted "- Chest pain:
substernal ..." loads as a key-value pair and was dropped by the symptom
ranking (the ACS "chest pain" miss); 3,050 such lines were quoted.
"""
import importlib.util
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def validator():
    spec = importlib.util.spec_from_file_location("validate_rules", ROOT / "scripts" / "validate_rules.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_unquoted_colon_line_is_rejected(validator):
    tree = yaml.safe_load("presentations:\n  - Chest pain: substernal, pressure-like\n")
    assert validator.list_item_problems(tree) == [
        "presentations[0] loads as a key-value pair, not text; quote it: 'Chest pain: substernal, pressure-like'"]


def test_quoted_line_loads_as_written(validator):
    tree = yaml.safe_load("presentations:\n  - 'Chest pain: substernal, pressure-like'\n")
    assert tree["presentations"] == ["Chest pain: substernal, pressure-like"]
    assert validator.list_item_problems(tree) == []


@pytest.mark.parametrize("text,problem", [
    ("treatment:\n  first_line:\n    - Labs:\n", "treatment.first_line[0] loads as a key-value pair"),
    ("workup:\n  - 2024\n", "workup[0] is int, not text"),
    ("red_flags:\n  - {a: 1, b: 2}\n", "red_flags[0] is a mapping (a, b), not text"),
])
def test_other_non_text_items_are_rejected(validator, text, problem):
    problems = validator.list_item_problems(yaml.safe_load(text))
    assert len(problems) == 1 and problems[0].startswith(problem)


def test_headings_and_structured_fields_are_allowed(validator):
    tree = yaml.safe_load(
        "treatment:\n  - Topical antifungals:\n      - Clotrimazole 1% cream\n"
        "differentials:\n  - category: medical\n    diagnoses: [CNS infection]\n"
        "sources:\n  - text: X\n    origin: citations\n"
        "metadata:\n  medications:\n    - name: Tamoxifen\n      dose: 20 mg\n")
    assert validator.list_item_problems(tree) == []


def test_nested_heading_items_are_checked(validator):
    tree = yaml.safe_load("treatment:\n  - Topical antifungals:\n      - Clotrimazole: twice daily\n")
    assert validator.list_item_problems(tree)[0].startswith("treatment[0][0] loads as a key-value pair")


def test_every_shipped_tree_has_only_text_items(validator):
    problems = {}
    for path in sorted((ROOT / "trees").glob("*.yml")):
        found = validator.list_item_problems(yaml.safe_load(path.read_text(encoding="utf-8")))
        if found:
            problems[path.name] = found
    assert problems == {}


def test_acs_presentation_loads_as_text():
    tree = yaml.safe_load((ROOT / "trees" / "CARD-ACUTE-CORONARY-SYNDROME.yml").read_text(encoding="utf-8"))
    assert tree["presentations"][0] == "Chest pain: substernal, pressure-like, radiating to left arm/jaw/back"
