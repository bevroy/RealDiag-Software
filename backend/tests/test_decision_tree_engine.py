from pathlib import Path

import yaml

from backend.services.decision_tree_engine import DecisionTreeEngine

TREES_DIR = Path(__file__).resolve().parents[1] / "trees"

QUESTIONNAIRE_WARNING = (
    "This tree is an interactive questionnaire that requires answers from the user "
    "and was not evaluated automatically."
)

QUESTIONNAIRE_TREES = [
    "ALLERGY-DRUG-ALLERGY", "DENT-DENTAL-ABSCESS", "DERM-ECZEMA-DERMATITIS",
    "EMERGENCY-ANAPHYLAXIS", "ENDO-THYROID-STORM", "ENT-HEARING-LOSS", "GENERAL-EDEMA",
    "GENERAL-FATIGUE", "GI-HEPATITIS", "HEME-ANEMIA", "NEURO-DEMENTIA",
    "ONCOLOGY-BREAST-MASS", "PSYCH-INSOMNIA", "PULM-COUGH", "SURG-ACUTE-APPENDICITIS",
    "TRAUMA-BURNS",
]


def _engine_with(tmp_path, tree):
    (tmp_path / f"{tree['tree_id']}.yml").write_text(yaml.safe_dump(tree, sort_keys=False))
    return DecisionTreeEngine(trees_path=tmp_path)


def _conditional_tree(**overrides):
    tree = {
        "tree_id": "TEST-COND",
        "name": "Test conditional tree",
        "codes": {"icd10": ["R69"], "snomed": [], "icpc2": []},
        "entry_point": "start",
        "nodes": [
            {"id": "start", "when": {}, "tests": ["CBC"], "suggest_dx": ["Dx A"],
             "referrals": ["Referral from start"], "next": [{"default": True, "node": "middle"}]},
            {"id": "middle", "when": {}, "tests": ["BMP"], "suggest_dx": ["Dx B"],
             "referrals": ["Referral from middle"], "next": [{"default": True, "node": "end"}]},
            {"id": "end", "when": {}, "tests": [], "suggest_dx": [],
             "referrals": ["Referral from end"], "next": []},
        ],
    }
    tree.update(overrides)
    return tree


def test_referrals_accumulate_across_nodes(tmp_path):
    engine = _engine_with(tmp_path, _conditional_tree())
    result = engine.evaluate("TEST-COND", {})
    assert result["path"] == ["start", "middle", "end"]
    # Path order, not alphabetical: each item appears in the order its node was reached.
    assert result["referrals"] == ["Referral from start", "Referral from middle", "Referral from end"]
    assert result["tests"] == ["CBC", "BMP"]
    assert result["evaluated"] is True


def test_items_keep_the_node_that_produced_them(tmp_path):
    tree = _conditional_tree()
    tree["nodes"][2]["tests"] = ["CBC"]  # the same test listed again at a later step
    result = _engine_with(tmp_path, tree).evaluate("TEST-COND", {})
    assert result["tests"] == ["CBC", "BMP"]
    assert result["tests_by_node"] == [{"text": "CBC", "nodes": ["start", "end"]}, {"text": "BMP", "nodes": ["middle"]}]
    assert result["provisional_dx_by_node"] == [{"text": "Dx A", "nodes": ["start"]}, {"text": "Dx B", "nodes": ["middle"]}]
    assert [i["nodes"] for i in result["referrals_by_node"]] == [["start"], ["middle"], ["end"]]


def test_tree_without_entry_point_returns_error(tmp_path):
    engine = _engine_with(tmp_path, _conditional_tree(entry_point=""))
    result = engine.evaluate("TEST-COND", {})
    assert "no entry_point" in result["error"]
    assert "path" not in result


def test_entry_point_not_matching_a_node_returns_error(tmp_path):
    engine = _engine_with(tmp_path, _conditional_tree(entry_point="does_not_exist"))
    result = engine.evaluate("TEST-COND", {})
    assert "does not match any node id" in result["error"]


def test_questionnaire_tree_is_not_evaluated(tmp_path):
    tree = {
        "tree_id": "TEST-QUESTIONS",
        "name": "Test questionnaire",
        "codes": {"icd10": [], "snomed": [], "icpc2": []},
        "entry_point": "q1",
        "nodes": [
            {"id": "q1", "type": "question", "question": "Fever?",
             "options": [{"label": "Yes", "next": "dx_a"}, {"label": "No", "next": "dx_b"}]},
            {"id": "dx_a", "type": "diagnosis", "diagnosis": "A"},
            {"id": "dx_b", "type": "diagnosis", "diagnosis": "B"},
        ],
    }
    result = _engine_with(tmp_path, tree).evaluate("TEST-QUESTIONS", {})
    assert result["evaluated"] is False
    assert result["node_format"] == "questionnaire"
    assert result["warning"] == QUESTIONNAIRE_WARNING
    assert "error" not in result


def test_real_questionnaire_trees_return_warning():
    engine = DecisionTreeEngine()
    for tree_id in QUESTIONNAIRE_TREES:
        result = engine.evaluate(tree_id, {"symptoms": ["pain"]})
        assert result.get("evaluated") is False, tree_id
        assert result["warning"] == QUESTIONNAIRE_WARNING, tree_id


def test_single_content_node_tree_is_not_evaluated(tmp_path):
    tree = {
        "tree_id": "TEST-CONTENT",
        "name": "Test content-only tree",
        "codes": {"icd10": ["E66.9"], "snomed": [], "icpc2": []},
        "entry_point": "evaluation",
        "nodes": [
            {"id": "evaluation", "type": "diagnosis", "name": "Obesity", "workup": ["BMI"]},
        ],
    }
    result = _engine_with(tmp_path, tree).evaluate("TEST-CONTENT", {"symptoms": ["weight gain"]})
    assert result["evaluated"] is False
    assert result["node_format"] == "content"
    assert "no decision branches to evaluate" in result["warning"]
    assert "error" not in result


def test_real_single_node_trees_return_warning():
    engine = DecisionTreeEngine()
    for tree_id in ("GEN-MED-OBESITY", "URO-BLADDER-CANCER"):
        result = engine.evaluate(tree_id, {"symptoms": []})
        assert result.get("evaluated") is False, tree_id
        assert "no decision branches to evaluate" in result["warning"], tree_id


def test_every_tree_evaluates_without_exception():
    engine = DecisionTreeEngine()
    for tree_id in engine.trees:
        result = engine.evaluate(tree_id, {"symptoms": []})
        assert "error" not in result, (tree_id, result.get("error"))
        assert "evaluated" in result, tree_id


def test_unmet_node_condition_is_marked_and_walk_is_unchanged(tmp_path):
    tree = _conditional_tree()
    tree["nodes"][1]["when"] = {"symptoms_contains_any": ["fever"], "min_age": 65}
    engine = _engine_with(tmp_path, tree)
    unmet = engine.evaluate("TEST-COND", {"symptoms": ["fever"], "age": 30})
    met = engine.evaluate("TEST-COND", {"symptoms": ["fever"], "age": 70})
    # The path is the same either way: node conditions do not choose the path.
    assert unmet["path"] == met["path"] == ["start", "middle", "end"]
    assert unmet["unmet_node_conditions"] == ["middle"] and met["unmet_node_conditions"] == []
    assert "[middle] (partial, condition not met) symptoms any of ['fever']" in unmet["trace"]
    assert any(line.startswith("[middle] NOT MET:") for line in unmet["trace"])
    assert "[middle] symptoms any of ['fever']" in met["trace"]
    assert not any("NOT MET" in line for line in met["trace"])
