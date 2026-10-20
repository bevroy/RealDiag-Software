import asyncio
from pathlib import Path

import pytest

from backend.services import clinical_review
from backend.services.clinical_review import (
    CLINICAL_REVIEW_NOTICE,
    review_fields,
    review_notice,
    status_label,
    tree_status_counts,
)

TREES_DIR = Path(__file__).resolve().parents[1] / "trees"

EXPECTED_NOTICE = (
    "Clinical content is under review. Urgency levels, treatment information, "
    "thresholds, and screening rules are proposed and have not completed clinical review. "
    "Verify against current guidelines before acting."
)


@pytest.fixture(autouse=True)
def _fresh_counts():
    clinical_review.reset_cache()
    yield
    clinical_review.reset_cache()


def _write_trees(tmp_path, statuses):
    for i, status in enumerate(statuses):
        (tmp_path / f"T-{i}.yml").write_text(f"tree_id: T-{i}\nname: Tree {i}\nversion: '1.0'\nstatus: {status}\n")
    return tmp_path


# --- notice text and labels --------------------------------------------------

def test_notice_text_is_exact():
    assert CLINICAL_REVIEW_NOTICE == EXPECTED_NOTICE


@pytest.mark.parametrize("status,label", [
    ("draft", "Draft - under clinical review."),
    ("review", "In clinical review - not yet approved."),
    ("approved", "Clinically reviewed."),
    ("retired", "Retired - not for clinical use."),
    ("Draft", "Draft - under clinical review."),
    (None, None),
])
def test_status_labels(status, label):
    assert status_label(status) == label
    assert review_fields(status) == {"review_status": status, "review_status_label": label}


def test_every_shipped_tree_is_draft_and_notice_is_shown():
    counts = tree_status_counts(TREES_DIR)
    assert counts == {"draft": len(list(TREES_DIR.glob("*.yml")))}
    assert review_notice() == EXPECTED_NOTICE


# --- notice disappears automatically ----------------------------------------

def test_notice_disappears_when_everything_is_reviewed(tmp_path, monkeypatch):
    trees = _write_trees(tmp_path, ["approved", "approved", "retired"])
    monkeypatch.setattr(clinical_review, "SEVERITY_THRESHOLDS_REVIEWED", True)
    assert review_notice(trees, screening_rules=tmp_path / "no-rules.yml") is None


def test_one_draft_tree_keeps_the_notice(tmp_path, monkeypatch):
    trees = _write_trees(tmp_path, ["approved", "draft"])
    monkeypatch.setattr(clinical_review, "SEVERITY_THRESHOLDS_REVIEWED", True)
    assert review_notice(trees) == EXPECTED_NOTICE


def test_tree_in_review_keeps_the_notice(tmp_path, monkeypatch):
    trees = _write_trees(tmp_path, ["approved", "review"])
    monkeypatch.setattr(clinical_review, "SEVERITY_THRESHOLDS_REVIEWED", True)
    assert review_notice(trees) == EXPECTED_NOTICE


def test_unreviewed_thresholds_keep_the_notice(tmp_path, monkeypatch):
    trees = _write_trees(tmp_path, ["approved"])
    monkeypatch.setattr(clinical_review, "SEVERITY_THRESHOLDS_REVIEWED", False)
    assert review_notice(trees) == EXPECTED_NOTICE


def test_tree_without_status_counts_as_unreviewed(tmp_path, monkeypatch):
    (tmp_path / "X.yml").write_text("tree_id: X\nname: X\n")
    monkeypatch.setattr(clinical_review, "SEVERITY_THRESHOLDS_REVIEWED", True)
    assert review_notice(tmp_path) == EXPECTED_NOTICE


def test_label_follows_the_tree_status(tmp_path):
    from backend.services.decision_tree_engine import DecisionTreeEngine
    (tmp_path / "T.yml").write_text("tree_id: T\nname: T\nstatus: approved\nnodes: []\n")
    tree = DecisionTreeEngine(trees_path=tmp_path).list()[0]
    assert tree["review_status_label"] == "Clinically reviewed."


# --- API responses carry the fields -----------------------------------------

def test_tree_engine_list_and_evaluation_carry_fields():
    from backend.services.decision_tree_engine import DecisionTreeEngine
    engine = DecisionTreeEngine()
    listed = engine.list()[0]
    assert listed["review_status"] == "draft"
    assert listed["review_status_label"] == "Draft - under clinical review."

    result = engine.evaluate("CARD-CHEST-PAIN", {"symptoms": ["chest pain"]})
    assert result["clinical_review_notice"] == EXPECTED_NOTICE
    assert result["tree"]["review_status_label"] == "Draft - under clinical review."

    not_evaluated = engine.evaluate("GEN-MED-OBESITY", {})
    assert not_evaluated["clinical_review_notice"] == EXPECTED_NOTICE


def test_rules_engine_carries_fields():
    from backend.services.rules_engine import RulesEngine
    engine = RulesEngine()
    rule = engine.get_rule("CARD-CHEST-PAIN")
    assert rule["review_status_label"] == "Draft - under clinical review."
    hit = engine.search("chest pain")[0]
    assert hit["review_status"] == "draft"


def test_rules_router_responses_carry_notice():
    from backend.services import rules_router
    assert rules_router.search_rules(q="chest", family=None, current_user=None)["clinical_review_notice"] == EXPECTED_NOTICE
    assert rules_router.list_families(current_user=None)["clinical_review_notice"] == EXPECTED_NOTICE
    assert rules_router.get_rule("CARD-CHEST-PAIN", current_user=None)["clinical_review_notice"] == EXPECTED_NOTICE


def test_search_router_results_carry_fields():
    from backend.services import search_router
    search_router.ai_enricher = None
    response = asyncio.run(search_router.search_diagnoses(q="Pulmonary embolism"))
    assert response["clinical_review_notice"] == EXPECTED_NOTICE
    top = response["results"][0]
    assert top["review_status"] == "draft"
    assert top["review_status_label"] == "Draft - under clinical review."


def test_symptom_search_results_carry_fields():
    from backend.services.symptom_search import rank_diagnoses
    response, _ = asyncio.run(rank_diagnoses(["chest pain", "shortness of breath"]))
    assert response.clinical_review_notice == EXPECTED_NOTICE
    tree_results = [r for r in response.results if not r.ai_suggested]
    assert tree_results and all(r.review_status_label == "Draft - under clinical review." for r in tree_results)


def test_patient_facing_search_carries_fields(monkeypatch):
    from backend.services import symptom_search
    from backend.services.symptom_search import (
        DiagnosisMatch, SymptomSearchRequest, SymptomSearchResponse, build_patient_symptom_search_response,
    )
    match = DiagnosisMatch(rule_id="X", label="X", family="f", match_score=5.0, matched_presentations=["cough"],
                           all_presentations=["cough"], icd10=[], snomed=[], **review_fields("draft"))

    async def fake_search(request, request_obj):
        return SymptomSearchResponse(query_symptoms=["cough"], total_results=1, results=[match])
    monkeypatch.setattr(symptom_search, "search_by_symptoms", fake_search)

    result = asyncio.run(build_patient_symptom_search_response(SymptomSearchRequest(symptoms=["cough"]), request_obj=None))
    assert result.clinical_review_notice == EXPECTED_NOTICE
    assert result.topics[0].review_status_label == "Draft - under clinical review."


def test_reference_trees_carry_fields():
    from backend.services.reference_router import _load_trees_by_family
    tree = _load_trees_by_family("cardiology")[0]
    assert tree["review_status_label"] == "Draft - under clinical review."


def test_smart_evaluation_response_carries_notice(monkeypatch):
    from datetime import datetime, timedelta
    from types import SimpleNamespace
    from fastapi.testclient import TestClient
    from backend.main import app
    from backend.services import smart_router

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def get_patient_data(self, patient_id, observation_requirements=None):
            return SimpleNamespace(patient_id="p1", name="A", age=50, gender="female", labs=[], vitals=[],
                                   conditions=[], medications=[], allergies=[],
                                   retrieval_status={"labs": "retrieved"}, data_notes=[])

    monkeypatch.setattr(smart_router, "FHIRClient", FakeClient)
    session = SimpleNamespace(patient_id="p1", ehr_vendor="epic", fhir_access_token="t",
                              expires_at=datetime.utcnow() + timedelta(minutes=30))
    app.dependency_overrides[smart_router.get_active_smart_session] = lambda: session
    try:
        body = TestClient(app).post("/smart/evaluate-patient", json={"patient_id": "p1"}).json()
    finally:
        app.dependency_overrides.pop(smart_router.get_active_smart_session, None)
    assert body["clinical_review_notice"] == EXPECTED_NOTICE


# --- screening rules count toward the notice ---------------------------------

def _write_rules(tmp_path, statuses):
    path = tmp_path / "rules.yml"
    path.write_text("rules:\n" + "".join(f"  - id: R{i}\n    status: {s}\n" for i, s in enumerate(statuses)))
    return path


def test_draft_screening_rule_keeps_the_notice(tmp_path, monkeypatch):
    (tmp_path / "t").mkdir()
    trees = _write_trees(tmp_path / "t", ["approved"])
    monkeypatch.setattr(clinical_review, "SEVERITY_THRESHOLDS_REVIEWED", True)
    assert review_notice(trees, screening_rules=_write_rules(tmp_path, ["approved", "draft"])) == EXPECTED_NOTICE


def test_notice_disappears_when_trees_rules_and_thresholds_are_reviewed(tmp_path, monkeypatch):
    (tmp_path / "t").mkdir()
    trees = _write_trees(tmp_path / "t", ["approved", "retired"])
    monkeypatch.setattr(clinical_review, "SEVERITY_THRESHOLDS_REVIEWED", True)
    assert review_notice(trees, screening_rules=_write_rules(tmp_path, ["approved", "approved"])) is None


def test_tree_review_fields_by_id():
    assert clinical_review.tree_review_fields("CARD-AORTIC-DISSECTION") == {
        "review_status": "draft", "review_status_label": "Draft - under clinical review."}
    assert clinical_review.tree_review_fields("NO-SUCH-TREE") == {"review_status": None, "review_status_label": None}


# --- exports, PDFs and AI review endpoints carry the notice -------------------

AUTH = {"auth_type": "api_key"}


@pytest.mark.parametrize("fmt", ["json", "xml", "csv"])
def test_export_formats_carry_notice_and_status(fmt):
    from backend.services import integration_router as router
    body = asyncio.run(router.export_diagnosis(router.DiagnosisExportRequest(rule_id="CARD-PE", format=fmt), auth=AUTH))
    assert body["clinical_review_notice"] == EXPECTED_NOTICE
    assert body["review_status_label"] == "Draft - under clinical review."
    if fmt == "xml":
        assert f"<clinical_review_notice>{EXPECTED_NOTICE}</clinical_review_notice>" in body["data"]
    if fmt == "csv":
        assert body["data"]["review_status"] == "draft"


def test_fhir_condition_and_hl7_carry_notice():
    from backend.services import integration_router as router
    fhir = asyncio.run(router.export_to_fhir_condition(
        router.FHIRConditionRequest(rule_id="CARD-PE", patient_id="p"), auth=AUTH))
    hl7 = asyncio.run(router.generate_hl7_message(router.HL7MessageRequest(
        rule_id="CARD-PE", patient_id="p", patient_name="A B", message_type="ORU"), auth=AUTH))
    notes = [n["text"] for n in fhir["fhir_resource"]["note"]]
    assert EXPECTED_NOTICE in notes and "Draft - under clinical review." in notes
    assert f"NTE|2|L|{EXPECTED_NOTICE}" in hl7["hl7_message"]
    assert hl7["clinical_review_notice"] == EXPECTED_NOTICE


def test_pdf_reports_include_notice_and_status(monkeypatch):
    pytest.importorskip("reportlab")
    from backend.services import pdf_export
    seen = []
    real = pdf_export.Paragraph

    def capture(text, *args, **kwargs):
        seen.append(text)
        return real(text, *args, **kwargs)
    monkeypatch.setattr(pdf_export, "Paragraph", capture)
    generator = pdf_export.PDFReportGenerator()
    generator.generate_diagnosis_report({"rule_id": "CARD-PE", "label": "Pulmonary embolism", "family": "cardiology"})
    generator.generate_multi_diagnosis_report([{"rule_id": "CARD-AORTIC-DISSECTION", "label": "Aortic dissection",
                                                "match_score": 5, "cant_miss": True}])
    assert sum(EXPECTED_NOTICE in t for t in seen) == 2
    assert sum("Draft - under clinical review." in t for t in seen) == 2
    assert any("Can't-miss condition" in t for t in seen)


def test_ai_pending_trees_carry_notice(monkeypatch):
    from backend.services import symptom_search

    class FakeGenerator:
        def load_pending_trees(self):
            return [{"tree_id": "ai_1", "name": "X", "metadata": {}}]
    monkeypatch.setattr(symptom_search, "AI_GENERATION_AVAILABLE", True)
    monkeypatch.setattr(symptom_search, "AITreeGenerator", FakeGenerator)
    body = asyncio.run(symptom_search.get_pending_trees(current_user={"user_id": "a", "role": "admin"}))
    assert body["clinical_review_notice"] == EXPECTED_NOTICE
