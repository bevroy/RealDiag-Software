"""
/diagnose walks: every conditional tree can be walked to each of its end
nodes using only the answer choices built from that tree's own branches, and
predicate keys the engine does not recognise no longer match every patient.
"""
from pathlib import Path

import pytest
import yaml

from backend.services.decision_tree_engine import DecisionTreeEngine, tree_inputs
from backend.tests.tree_walk_solver import end_nodes, missing_targets, solve

TREES_DIR = Path(__file__).resolve().parents[1] / "trees"

WALKABLE_TREES = [
    "CARD-CHEST-PAIN", "CARD-PALPITATIONS", "ENDO-DIABETES", "ENDO-THYROID", "ENT-EAR-PAIN",
    "ENT-SORE-THROAT", "ENT-VERTIGO", "GI-ABD-PAIN", "ID-FEVER", "NEU-WEAKNESS",
    "NEURO-ALTERED-MS", "ORTHO-BACK-PAIN", "PSYCH-ANXIETY", "PSYCH-PSYCHOSIS",
    "PSYCH-SUICIDAL-IDEATION", "PULM-DYSPNEA", "TRAUMA-HEAD-INJURY",
]

# Branch targets that are not nodes in the tree (tree content, reported rather
# than edited here). The walk stops with end_reason "missing_node".
KNOWN_MISSING_TARGETS = {
    "ID-FEVER": ["initial_assessment -> localized_infection"],
    "PSYCH-PSYCHOSIS": ["safety_assessment -> psychotic_disorder_assessment"],
}


@pytest.fixture(scope="module")
def engine():
    return DecisionTreeEngine()


def test_the_seventeen_walkable_trees_are_the_conditional_ones(engine):
    conditional = sorted(t["id"] for t in engine.list() if t["node_format"] == "conditional")
    assert conditional == WALKABLE_TREES


@pytest.mark.parametrize("tree_id", WALKABLE_TREES)
def test_every_end_node_is_reachable_from_the_offered_choices(engine, tree_id):
    tree = engine.trees[tree_id]
    found = solve(engine, tree_id)
    ends = end_nodes(tree)
    assert ends, tree_id
    assert [e for e in ends if e not in found] == []

    offered = tree_inputs(tree)
    for node_id, patient in found.items():
        for fact in ("symptoms", "exam", "red_flags", "patient_characteristics", "no_red_flags"):
            assert set(patient[fact]) <= set(offered[fact]), (tree_id, fact)
        for name, value in patient["findings"].items():
            assert value in offered["findings"][name], (tree_id, name)
        if "age" in patient:
            assert offered["uses_age"], tree_id
        if "onset_hours" in patient:
            assert offered["uses_onset_hours"], tree_id
        if "diagnosis" in patient:
            assert offered["uses_diagnosis"], tree_id

        result = engine.evaluate(tree_id, patient)
        assert result["evaluated"] is True
        assert result["path"][-1] == node_id
        if node_id in ends:
            assert result["end_reason"] == "end_node", (tree_id, node_id)


@pytest.mark.parametrize("tree_id", WALKABLE_TREES)
def test_missing_branch_targets_are_only_the_known_ones(engine, tree_id):
    assert missing_targets(engine.trees[tree_id]) == KNOWN_MISSING_TARGETS.get(tree_id, [])


def test_walk_into_a_missing_node_says_so(engine):
    result = engine.evaluate("ID-FEVER", {})
    assert result["path"] == ["initial_assessment"]
    assert result["end_reason"] == "missing_node"
    assert result["missing_node"] == "localized_infection"


def test_walks_that_stop_before_an_end_node_say_why(engine):
    # Some nodes branch only on findings and have no default (e.g. GI-ABD-PAIN
    # ruq_pain); answers that match none of them stop the walk there.
    stopped = 0
    for tree_id in WALKABLE_TREES:
        ends = set(end_nodes(engine.trees[tree_id]))
        for node_id, patient in solve(engine, tree_id).items():
            if node_id in ends:
                continue
            stopped += 1
            assert engine.evaluate(tree_id, patient)["end_reason"] in ("no_matching_branch", "missing_node"), (
                tree_id, node_id)
    assert stopped > 0


def test_unquoted_colon_items_are_shown_as_written(engine):
    patient = solve(engine, "CARD-CHEST-PAIN")
    texts = set()
    for p in patient.values():
        texts.update(engine.evaluate("CARD-CHEST-PAIN", p)["tests"])
    assert "HEART score (History, ECG, Age, Risk factors, Troponin): Predicts 6-week MACE" in texts


def test_sore_throat_inputs_come_from_the_tree():
    tree = yaml.safe_load((TREES_DIR / "ENT-SORE-THROAT.yml").read_text())
    tree["entry"] = tree["entry_point"]
    inputs = tree_inputs(tree)
    assert "stridor" in inputs["symptoms"]
    assert "trismus" in inputs["exam"]
    assert inputs["findings"]["rapid_strep"] == ["positive"]
    assert inputs["findings"]["centor_score"] == [">=4", "2-3"] or set(inputs["findings"]["centor_score"]) == {">=4", "2-3"}


# --- predicate semantics -------------------------------------------------

def _engine_with(tmp_path, branches):
    tree = {
        "tree_id": "TEST-PRED", "name": "Predicates", "entry_point": "start",
        "nodes": [
            {"id": "start", "when": {}, "tests": [], "suggest_dx": [], "next": branches},
            {"id": "hit", "when": {}, "tests": [], "suggest_dx": ["Hit"], "next": []},
            {"id": "miss", "when": {}, "tests": [], "suggest_dx": ["Miss"], "next": []},
        ],
    }
    (tmp_path / "TEST-PRED.yml").write_text(yaml.safe_dump(tree, sort_keys=False))
    return DecisionTreeEngine(trees_path=tmp_path)


def _end(engine, patient):
    return engine.evaluate("TEST-PRED", patient)["path"][-1]


def test_unknown_predicate_shape_fails_closed(tmp_path):
    engine = _engine_with(tmp_path, [{"when": {"mystery": {"nested": 1}}, "go": "hit"}, {"default": "miss"}])
    assert _end(engine, {}) == "miss"


def test_named_finding_matches_its_exact_value_only(tmp_path):
    engine = _engine_with(tmp_path, [{"when": {"rapid_strep": "positive"}, "go": "hit"}, {"default": "miss"}])
    assert _end(engine, {}) == "miss"
    assert _end(engine, {"findings": {"rapid_strep": "negative"}}) == "miss"
    assert _end(engine, {"findings": {"rapid_strep": "Positive"}}) == "hit"


def test_boolean_finding(tmp_path):
    engine = _engine_with(tmp_path, [{"when": {"recent_attempt": True}, "go": "hit"}, {"default": "miss"}])
    assert _end(engine, {"findings": {"recent_attempt": False}}) == "miss"
    assert _end(engine, {"findings": {"recent_attempt": True}}) == "hit"


def test_exam_findings_any_is_an_exam_list(tmp_path):
    engine = _engine_with(tmp_path, [{"when": {"exam_findings_any": ["trismus", "uvula_deviation"]}, "go": "hit"},
                                     {"default": "miss"}])
    assert _end(engine, {"exam": ["fever"]}) == "miss"
    assert _end(engine, {"exam": ["uvula_deviation"]}) == "hit"


def test_symptoms_contains_all_needs_every_token(tmp_path):
    engine = _engine_with(tmp_path, [{"when": {"symptoms_contains_all": ["hearing_loss", "tinnitus"]}, "go": "hit"},
                                     {"default": "miss"}])
    assert _end(engine, {"symptoms": ["tinnitus"]}) == "miss"
    assert _end(engine, {"symptoms": ["tinnitus", "hearing_loss"]}) == "hit"


def test_no_red_flags_needs_every_statement_confirmed(tmp_path):
    engine = _engine_with(tmp_path, [{"when": {"no_red_flags": ["no LOC", "GCS 15"]}, "go": "hit"},
                                     {"default": "miss"}])
    assert _end(engine, {"no_red_flags": ["no LOC"]}) == "miss"
    assert _end(engine, {"no_red_flags": ["no LOC", "GCS 15"]}) == "hit"


def test_age_comparator_and_string_age(tmp_path):
    engine = _engine_with(tmp_path, [{"when": {"age": "<18"}, "go": "hit"}, {"default": "miss"}])
    assert _end(engine, {}) == "miss"
    assert _end(engine, {"age": "17"}) == "hit"
    assert _end(engine, {"age": 18}) == "miss"


def test_min_age_accepts_age_sent_as_text(tmp_path):
    engine = _engine_with(tmp_path, [{"if": {"min_age": 50}, "node": "hit"}, {"default": True, "node": "miss"}])
    assert _end(engine, {"age": "65"}) == "hit"
    assert _end(engine, {"age": "30"}) == "miss"


def test_branch_decisions_appear_in_the_trace(tmp_path):
    engine = _engine_with(tmp_path, [{"when": {"rapid_strep": "positive"}, "go": "hit"}, {"default": "miss"}])
    result = engine.evaluate("TEST-PRED", {"findings": {"rapid_strep": "positive"}})
    assert "[start] -> hit: rapid_strep = positive" in result["trace"]
    result = engine.evaluate("TEST-PRED", {})
    assert "[start] -> miss (default)" in result["trace"]


# --- inputs accessor -------------------------------------------------------

def test_inputs_rejects_non_conditional_trees(engine):
    assert "not a conditional" in engine.inputs("PULM-COUGH")["error"]
    assert "not found" in engine.inputs("NOPE")["error"]


def test_inputs_carry_review_status_and_notice(engine):
    result = engine.inputs("ENT-SORE-THROAT")
    assert result["node_format"] == "conditional"
    assert "review_status" in result["tree"] and "review_status_label" in result["tree"]
    assert "clinical_review_notice" in result
