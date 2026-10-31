"""Questionnaire trees (16) are offered on /diagnose and returned for walking one question
at a time: questions with options, outcome steps with their content as written."""
import pytest

from backend.services.decision_tree_engine import STEP_VALUES_NOTE, DecisionTreeEngine


@pytest.fixture(scope="module")
def engine():
    return DecisionTreeEngine()


def questionnaire_ids(engine):
    return sorted(t["id"] for t in engine.list() if t["node_format"] == "questionnaire")


def test_all_questionnaire_trees_are_walkable(engine):
    listed = {t["id"]: t for t in engine.list() if t["node_format"] == "questionnaire"}
    assert len(listed) == 16
    assert all(t["walk_available"] for t in listed.values())


def test_every_answer_leads_to_a_question_or_outcome_and_every_outcome_is_reachable(engine):
    for tree_id in questionnaire_ids(engine):
        q = engine.questionnaire(tree_id)
        nodes = q["nodes"]
        assert q["entry"] in nodes and nodes[q["entry"]]["kind"] == "question", tree_id
        reached, stack = set(), [q["entry"]]
        while stack:
            node_id = stack.pop()
            if node_id in reached:
                continue
            reached.add(node_id)
            node = nodes[node_id]
            if node["kind"] == "question":
                assert node["text"] and node["options"], (tree_id, node_id)
                stack.extend(o["next"] for o in node["options"])
            else:
                assert node["title"], (tree_id, node_id)
        outcomes = {i for i, n in nodes.items() if n["kind"] == "outcome"}
        assert outcomes and outcomes <= reached, tree_id


def test_outcome_content_is_as_written(engine):
    q = engine.questionnaire("PULM-COUGH")
    cap = q["nodes"]["pneumonia_diagnosis"]
    assert cap["title"] == "Community-Acquired Pneumonia (CAP)"
    assert cap["icd10"] == ["J18.9"] and cap["urgency"] == "high"
    assert "Chest X-ray" in cap["workup"]
    assert q["step_values_note"] == STEP_VALUES_NOTE and q["clinical_review_notice"]
    assert q["tree"]["review_status"] == "draft"


def test_not_a_questionnaire_is_an_error(engine):
    assert "not a questionnaire" in engine.questionnaire("CARD-CHEST-PAIN")["error"]
    assert "not found" in engine.questionnaire("NOPE")["error"]
