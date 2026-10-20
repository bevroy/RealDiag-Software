"""
Phase 2 encounter assessment: today's complaint, the combined endpoint and
each of its sections, including partial data failures.
"""
import asyncio
import re
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from backend.services import encounter_assessment as ea
from backend.services import symptom_search
from backend.services.complaint_matching import (
    EHR_VISIT_REASON, ENTERED, NO_COMPLAINT, affirmed_phrases, encounter_reason, match_terms, resolve_complaint,
)
from backend.services.content_labels import AI_SETTINGS
from backend.services.fhir_client import LabResult, PatientData, VitalSign
from backend.services.patient_history_service import ComprehensivePatientHistory, PatientHistoryService
from backend.services.smart_diagnostic_engine import SmartDiagnosticEngine

NOW = datetime.utcnow()
ACS = "CARD-ACUTE-CORONARY-SYNDROME"
TROPONIN_I = "10839-9"
ALL_RETRIEVED = {k: "retrieved" for k in ("labs", "vitals", "conditions", "medications", "allergies")}
HISTORY_OK = {r: "retrieved" for r in ea.HISTORY_RESOURCES}


def troponin(value=0.5):
    return LabResult(code=TROPONIN_I, display="Troponin I", value=value, unit="ng/mL",
                     reference_range={"high": 0.04}, effective_date=NOW - timedelta(hours=1))


def patient(labs=(), vitals=(), conditions=(), status=None, gender="male"):
    return PatientData(patient_id="p", name="Test Patient", age=62, gender=gender, labs=list(labs),
                       vitals=list(vitals), conditions=list(conditions), medications=[], allergies=[],
                       retrieval_status=dict(status or ALL_RETRIEVED))


@pytest.fixture(scope="module")
def engine():
    return SmartDiagnosticEngine()


# --- Complaint source --------------------------------------------------------------

def test_typed_complaint_comes_first():
    c = resolve_complaint("  chest pain ", lambda: pytest.fail("EHR should not be asked"))
    assert (c.text, c.source, c.source_label) == ("chest pain", ENTERED, "Entered by clinician")


def test_ehr_visit_reason_used_when_nothing_typed():
    encounter = {"reasonCode": [{"text": "Chest pain"}, {"coding": [{"display": "Shortness of breath"}]}]}
    c = resolve_complaint("", lambda: encounter)
    assert (c.text, c.source, c.source_label) == ("Chest pain; Shortness of breath", EHR_VISIT_REASON,
                                                  "EHR visit reason")


def test_no_complaint_when_none_typed_or_found():
    c = resolve_complaint(None, lambda: {"status": "in-progress"})
    assert (c.text, c.source, c.warnings) == (None, NO_COMPLAINT, [])
    assert encounter_reason(None) is None


def test_visit_reason_lookup_failure_is_reported():
    def boom():
        raise RuntimeError("Encounter search not supported")
    c = resolve_complaint(None, boom)
    assert c.source == NO_COMPLAINT
    assert c.warnings == ["Today's visit reason could not be retrieved from the EHR."]


# --- Matching -------------------------------------------------------------------------

@pytest.mark.parametrize("complaint,terms,matched,negated", [
    ("Chest pain since this morning", ["chest pain"], ["chest pain"], []),
    ("no chest pain", ["chest pain"], [], ["chest pain"]),
    ("Denies fever, chills", ["fever", "chills"], [], ["fever", "chills"]),
    ("denies fever but new confusion", ["fever", "confusion"], ["confusion"], ["fever"]),
    ("chest pain, no fever", ["chest pain", "fever"], ["chest pain"], ["fever"]),
    ("Pain radiates to the left arm", ["pain radiating to the arm"], ["pain radiating to the arm"], []),
    ("short of breath on exertion", ["shortness of breath with exertion"], [], []),
    ("shortness of breath on exertion", ["shortness of breath with exertion"],
     ["shortness of breath with exertion"], []),
    ("feverish", ["fever"], [], []),                    # whole words only
    ("Chest-pain", ["chest pain"], ["chest pain"], []),
])
def test_match_terms(complaint, terms, matched, negated):
    assert match_terms(complaint, terms) == (matched, negated)


def test_affirmed_phrases_drop_negated_parts():
    assert affirmed_phrases("Chest pain and nausea, no fever") == ["Chest pain", "nausea"]
    assert affirmed_phrases("denies chest pain; dizziness") == ["dizziness"]
    assert affirmed_phrases(None) == []


# --- Acute cards and the complaint -----------------------------------------------------

def shown(engine, data, complaint):
    return {e.diagnosis_id: e for e in engine.evaluate_encounter(data, now=NOW, complaint=complaint).evaluations}


def test_complaint_match_shows_acute_card_without_data(engine):
    acs = shown(engine, patient(), "chest pain")[ACS]
    assert acs.complaint_matches == ["chest pain"]
    assert acs.evaluation_status == "insufficient data"
    assert acs.missing_tests
    assert acs.recommendations[0] == "Today's complaint matches (chest pain); relevant results are not available."


def test_negated_complaint_shows_no_card(engine):
    assert shown(engine, patient(), "no chest pain, no fever") == {}


def test_complaint_match_with_normal_results(engine):
    acs = shown(engine, patient(labs=[troponin(0.01)]), "chest tightness")[ACS]
    assert acs.criteria_not_met and not acs.criteria_met
    assert acs.recommendations[0].startswith(
        "Today's complaint matches (chest tightness); available results do not meet criteria for")


def test_sepsis_card_from_confusion(engine):
    assert shown(engine, patient(), "new confusion")["ID-SEPSIS"].complaint_matches == ["confusion"]


def test_unmatched_complaint_and_no_data_shows_nothing(engine):
    assert shown(engine, patient(), "ankle sprain") == {}


def test_hypotension_is_not_a_sepsis_complaint_term(engine):
    assert "ID-SEPSIS" not in shown(engine, patient(), "hypotension")


# --- History summary (template, no language model) ---------------------------------------

def _summary(status, conditions=(), meds=()):
    return PatientHistoryService._generate_summary(
        {"name": "A", "age": 50, "gender": "female"}, list(conditions), list(meds), [], [], status)


def test_summary_never_claims_no_history_when_problem_list_failed():
    text = _summary({"conditions": "failed", "medications": "retrieved"})
    assert "Problem list could not be retrieved." in text
    assert "no significant" not in text.lower()


def test_summary_states_not_available_and_none_on_file():
    text = _summary({"conditions": "not available", "medications": "retrieved"})
    assert "Problem list is not available from this EHR." in text
    assert "No active medications on file." in text
    assert "No active problems on file." in _summary({"conditions": "retrieved"})


def test_summary_medications_not_counted_when_not_retrieved():
    text = _summary({"medications": "failed"}, meds=[{"x": 1}])
    assert "Medication list could not be retrieved." in text and "active medications on file" not in text


def test_coded_condition_without_text_uses_display():
    from backend.services.patient_history_service import _concept_name
    assert _concept_name({"coding": [{"code": "E11.9", "display": "Type 2 diabetes"}]}) == "Type 2 diabetes"
    assert _concept_name({"coding": [{"code": "E11.9"}]}) == "E11.9"
    assert _concept_name(None) == "Unnamed condition"


# --- Endpoint ------------------------------------------------------------------------

class FakeFHIR:
    def __init__(self, data, encounter=None, encounter_error=False, smoking=None, smoking_error=False):
        self.data, self.encounter, self.encounter_error = data, encounter, encounter_error
        self.smoking, self.smoking_error = smoking, smoking_error
        self.requirements = None

    def get_smoking_status(self, patient_id):
        if self.smoking_error:
            raise RuntimeError("Observation query failed")
        return self.smoking

    def get_patient_data(self, patient_id, observation_requirements=None):
        self.requirements = observation_requirements
        return self.data

    def get_current_encounter(self, patient_id):
        if self.encounter_error:
            raise RuntimeError("Encounter query failed")
        return self.encounter


class FakeHistory:
    def __init__(self, status=None, error=False, procedures=(), imaging=()):
        self.status, self.error, self.skip, self.overrides = status or HISTORY_OK, error, None, None
        self.procedures, self.imaging = list(procedures), list(imaging)

    async def get_comprehensive_history(self, patient_id, lookback_days=None, skip=None, lookback_overrides=None):
        self.skip, self.overrides = skip, lookback_overrides
        if self.error:
            raise RuntimeError("DocumentReference search failed")
        return ComprehensivePatientHistory(patient_id=patient_id, patient_name="", retrieval_status=self.status,
                                           procedures=self.procedures, imaging_studies=self.imaging)


def run(engine, data, complaint=None, fhir=None, history=None):
    from backend.services.smart_router import _diagnosis_response, summary_from_patient_data
    fhir = fhir or FakeFHIR(data)
    history = history or FakeHistory()
    result = asyncio.run(ea.assess_encounter("p", complaint, fhir, history, engine,
                                             criteria_response=_diagnosis_response,
                                             summary_response=summary_from_patient_data, now=NOW))
    return result, fhir, history


@pytest.fixture
def no_ai(monkeypatch):
    """Every AI setting on, and any model call fails the test."""
    for name in AI_SETTINGS:
        monkeypatch.setenv(name, "true")
    monkeypatch.setattr(symptom_search, "AI_GENERATION_AVAILABLE", True)

    async def forbidden(*args, **kwargs):
        raise AssertionError("EHR-driven request reached an AI provider")
    monkeypatch.setattr(symptom_search, "query_ai_for_diagnoses", forbidden)


def test_all_sections_present(engine, no_ai):
    result, fhir, history = run(engine, patient(labs=[troponin()]), "chest pain")
    assert set(result) >= {"summary", "complaint", "diagnoses", "guidance", "red_flags", "not_assessed",
                           "decision_support_notice", "clinical_review_notice"}
    from backend.services.missed_items import screening_requirements
    assert fhir.requirements == {**engine.observation_requirements(), **screening_requirements()}
    assert history.overrides == {"procedures": 3650, "imaging_studies": 3650}
    assert history.skip == ea.HISTORY_SKIP                               # no overlap with the FHIR client


def test_diagnoses_merge_complaint_and_criteria_evidence(engine, no_ai):
    result, _, _ = run(engine, patient(labs=[troponin()]), "chest pain")
    items = result["diagnoses"]["items"]
    acs = next(d for d in items if d["tree_id"] == ACS)
    assert acs["evidence"] == "complaint and criteria"
    assert items[0]["tree_id"] == ACS                                    # both kinds of evidence first
    assert acs["complaint_match"]["matched_terms"] == ["chest pain"]
    met = acs["criteria"]["criteria_met"][0]
    assert met["value"] and met["source"]
    assert {d["evidence"] for d in items} >= {"complaint"}
    complaint_only = [d for d in items if d["evidence"] == "complaint"]
    assert all(d["criteria"] is None and d["review_status_label"] for d in complaint_only)


def test_criteria_only_diagnosis_without_complaint(engine, no_ai):
    result, _, _ = run(engine, patient(labs=[troponin()]), None)
    items = result["diagnoses"]["items"]
    assert [d["evidence"] for d in items] == ["criteria"] * len(items)
    assert result["complaint"]["source"] == "none"
    assert result["diagnoses"]["complaint_matches_total"] == 0
    assert {"category": "complaint", "text": "No complaint entered or found; complaint matching was skipped."} \
        in result["not_assessed"]


def test_complaint_matches_capped_at_15_with_note(engine, no_ai):
    result, _, _ = run(engine, patient(), "chest pain, shortness of breath, cough, fever, headache")
    d = result["diagnoses"]
    assert d["complaint_matches_total"] > 15
    assert d["complaint_matches_shown"] == 15
    assert d["complaint_matches_note"].startswith(f"Showing 15 of {d['complaint_matches_total']} complaint matches")
    assert len([i for i in d["items"] if i["evidence"] == "complaint"]) <= 15 + d["cant_miss_added"]
    if d["cant_miss_added"]:
        assert "can't-miss condition" in d["complaint_matches_note"]


def test_no_cap_note_when_few_matches(engine, no_ai):
    result, _, _ = run(engine, patient(), "zzqxv unmatched")
    assert result["diagnoses"]["complaint_matches_note"] is None


def test_ehr_visit_reason_used_and_shown(engine, no_ai):
    fhir = FakeFHIR(patient(), encounter={"reasonCode": [{"text": "Chest pressure"}]})
    result, _, _ = run(engine, patient(), None, fhir=fhir)
    assert result["complaint"] == {"text": "Chest pressure", "source": "ehr_visit_reason",
                                   "source_label": "EHR visit reason", "phrases_used": ["Chest pressure"],
                                   "negated_terms": []}
    assert any(d["tree_id"] == ACS for d in result["diagnoses"]["items"])


def test_guidance_has_labelled_treatment_sources_and_status(engine, no_ai):
    result, _, _ = run(engine, patient(labs=[troponin()]), "chest pain")
    g = next(g for g in result["guidance"] if g["tree_id"] == ACS)
    assert g["treatment"]["label"] == "Treatment information from the decision tree (reference, not an order)"
    assert g["treatment"]["sections"] and g["workup"] and g["referrals"]
    assert g["sources"]
    assert g["review_status_label"] == "Draft - under clinical review."
    assert [x["tree_id"] for x in result["guidance"]] == [d["tree_id"] for d in result["diagnoses"]["items"]]


def test_red_flags_listed_or_explicitly_absent(engine, no_ai):
    result, _, _ = run(engine, patient(labs=[troponin()]), "chest pain")
    acs = next(r for r in result["red_flags"] if r["tree_id"] == ACS)
    assert acs["red_flags"] == [] and acs["note"] == "No red flags listed for this condition."
    with_flags = [r for r in result["red_flags"] if r["red_flags"]]
    assert all(r["note"] is None for r in with_flags)


def test_summary_section(engine, no_ai):
    data = patient(labs=[troponin()], conditions=[{"code": {"text": "Hypertension"}}])
    data.truncation_warnings = ["Lab results cut off: the page limit was reached after 1000 results, "
                                "dated 2025-03-01 to 2026-10-18. Other results since 2024-10-19 were not "
                                "retrieved and were not assessed."]
    s = run(engine, data, "chest pain")[0]["summary"]
    assert s["summary_text"].startswith("Test Patient is a 62-year-old male. Active problems on file: Hypertension.")
    assert s["active_problems"] == ["Hypertension"]
    assert s["data_status"]["labs"] == "retrieved" and s["data_status"]["visit_notes"] == "retrieved"
    assert s["cut_off_notes"] == data.truncation_warnings
    assert s["abnormal_labs"][0]["name"] == "Troponin I"


# --- Partial failures ------------------------------------------------------------------

def test_lab_failure(engine, no_ai):
    result, _, _ = run(engine, patient(status=dict(ALL_RETRIEVED, labs="failed")), "chest pain")
    texts = [i["text"] for i in result["not_assessed"]]
    assert "Lab results could not be retrieved; do not assume none." in texts
    assert "Some conditions could not be assessed: lab results could not be retrieved." in texts
    assert "Lab results could not be retrieved; do not assume none." in result["summary"]["data_warnings"]
    acs = next(d for d in result["diagnoses"]["items"] if d["tree_id"] == ACS)
    assert acs["criteria"]["evaluation_status"] == "insufficient data"


def test_problem_list_failure(engine, no_ai):
    result, _, _ = run(engine, patient(status=dict(ALL_RETRIEVED, conditions="failed")), "chest pain")
    assert "Problem list could not be retrieved." in result["summary"]["summary_text"]
    assert "Conditions could not be retrieved; do not assume none." in [i["text"] for i in result["not_assessed"]]


def test_history_failure_still_returns_assessment(engine, no_ai):
    result, _, _ = run(engine, patient(labs=[troponin()]), "chest pain", history=FakeHistory(error=True))
    assert result["diagnoses"]["items"]
    assert result["summary"]["data_status"]["visit_notes"] == "failed"
    assert "Visit notes could not be retrieved." in result["summary"]["summary_text"]
    assert "Visit notes could not be retrieved; do not assume none." in [i["text"] for i in result["not_assessed"]]


def test_history_resource_not_available(engine, no_ai):
    history = FakeHistory(status=dict(HISTORY_OK, imaging_studies="not available"))
    result, _, _ = run(engine, patient(), "chest pain", history=history)
    assert "Imaging studies not available from this EHR; do not assume none." in \
        [i["text"] for i in result["not_assessed"]]


def test_visit_reason_failure(engine, no_ai):
    result, _, _ = run(engine, patient(), None, fhir=FakeFHIR(patient(), encounter_error=True))
    texts = [i["text"] for i in result["not_assessed"]]
    assert "Today's visit reason could not be retrieved from the EHR." in texts
    assert "No complaint entered or found; complaint matching was skipped." in texts


def test_insufficient_data_listed_with_missing_tests(engine, no_ai):
    result, _, _ = run(engine, patient(), "chest pain")
    assert any(i["text"].startswith("Acute Coronary Syndrome") and "insufficient data; missing" in i["text"]
               for i in result["not_assessed"])


# --- Wording --------------------------------------------------------------------------

ORDER_START = re.compile(r"^(administer|give|start|initiate|order|prescribe|activate|admit|transfuse|intubate)\b",
                         re.IGNORECASE)


def test_generated_text_is_decision_support(engine, no_ai):
    result, _, _ = run(engine, patient(labs=[troponin()]), "chest pain, confusion")
    generated = [result["summary"]["summary_text"], result["decision_support_notice"],
                 result["diagnoses"]["complaint_matches_note"] or ""]
    generated += [i["text"] for i in result["not_assessed"]]
    for d in result["diagnoses"]["items"]:
        generated += (d["criteria"] or {}).get("recommendations", [])
    assert generated and not [t for t in generated if ORDER_START.match(t)]
    assert "not diagnoses or orders" in result["decision_support_notice"]


# --- API ------------------------------------------------------------------------------

def test_api_endpoint(monkeypatch, no_ai):
    from fastapi.testclient import TestClient
    from backend.main import app
    from backend.services import smart_router

    data = patient(labs=[troponin()])
    monkeypatch.setattr(smart_router, "FHIRClient", lambda *a, **k: FakeFHIR(data))
    monkeypatch.setattr(smart_router, "PatientHistoryService", lambda *a, **k: FakeHistory())
    session = SimpleNamespace(patient_id="p", ehr_vendor="epic", fhir_access_token="t",
                              expires_at=datetime.utcnow() + timedelta(minutes=30))
    app.dependency_overrides[smart_router.get_active_smart_session] = lambda: session
    try:
        client = TestClient(app)
        body = client.post("/smart/encounter-assessment", json={"patient_id": "p", "chief_complaint": "chest pain"})
        other = client.post("/smart/encounter-assessment", json={"patient_id": "someone-else"})
    finally:
        app.dependency_overrides.pop(smart_router.get_active_smart_session, None)
    assert body.status_code == 200, body.text
    assert body.json()["diagnoses"]["items"][0]["tree_id"] == ACS
    assert other.status_code == 403


def test_evaluate_patient_uses_typed_complaint(monkeypatch):
    from fastapi.testclient import TestClient
    from backend.main import app
    from backend.services import smart_router

    monkeypatch.setattr(smart_router, "FHIRClient", lambda *a, **k: FakeFHIR(patient()))
    session = SimpleNamespace(patient_id="p", ehr_vendor="epic", fhir_access_token="t",
                              expires_at=datetime.utcnow() + timedelta(minutes=30))
    app.dependency_overrides[smart_router.get_active_smart_session] = lambda: session
    try:
        client = TestClient(app)
        with_complaint = client.post("/smart/evaluate-patient", json={"patient_id": "p", "chief_complaint": "chest pain"})
        without = client.post("/smart/evaluate-patient", json={"patient_id": "p"})
    finally:
        app.dependency_overrides.pop(smart_router.get_active_smart_session, None)
    acs = next(e for e in with_complaint.json()["evaluations"] if e["diagnosis_id"] == ACS)
    assert acs["complaint_matches"] == ["chest pain"]
    assert without.json()["evaluations"] == []
