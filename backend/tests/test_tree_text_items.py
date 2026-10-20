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


ORDER_VERB = __import__("re").compile(
    r"(?:^|:\s+|\s[-–]\s|;\s+|\.\s+|,\s+then\s+|\bthen\s+)(activate|administer|admit|transfuse|intubate|give|start|initiate)\b",
    __import__("re").IGNORECASE)


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)


def test_treatment_has_no_clinician_orders():
    """Clinician-directed actions are worded as decision support (review doc section 10)."""
    orders = []
    for path in sorted((ROOT / "trees").glob("*.yml")):
        tree = yaml.safe_load(path.read_text(encoding="utf-8"))
        for line in _strings(tree.get("treatment")):
            if not line.startswith("Patient advice:") and ORDER_VERB.search(line):
                orders.append(f"{path.stem}: {line}")
    assert orders == []


def test_examples_of_reworded_and_labelled_lines():
    acs = yaml.safe_load((ROOT / "trees" / "CARD-ACUTE-CORONARY-SYNDROME.yml").read_text(encoding="utf-8"))
    lines = list(_strings(acs["treatment"]))
    assert "Consider immediate cardiac catheterization lab activation per institutional STEMI protocol" in lines
    heat = yaml.safe_load((ROOT / "trees" / "EMERGENCY-HEAT-STROKE.yml").read_text(encoding="utf-8"))
    assert "Patient advice: Wear light, loose clothing" in list(_strings(heat["treatment"]))
