from pathlib import Path

import yaml

from backend.services.decision_tree_engine import DecisionTreeEngine

TREES_DIR = Path(__file__).resolve().parents[1] / "trees"

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
    assert result["referrals"] == ["Referral from end", "Referral from middle", "Referral from start"]
    assert result["tests"] == ["BMP", "CBC"]
    assert result["evaluated"] is True


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
    assert "NOT evaluated automatically" in result["warning"]
    assert "error" not in result


def test_real_questionnaire_trees_return_warning():
    engine = DecisionTreeEngine()
    for tree_id in QUESTIONNAIRE_TREES:
        result = engine.evaluate(tree_id, {"symptoms": ["pain"]})
        assert result.get("evaluated") is False, tree_id
        assert "interactive questionnaire" in result["warning"], tree_id


def test_every_tree_evaluates_without_exception():
    engine = DecisionTreeEngine()
    for tree_id in engine.trees:
        result = engine.evaluate(tree_id, {"symptoms": []})
        assert "error" not in result, (tree_id, result.get("error"))
        assert "evaluated" in result, tree_id
