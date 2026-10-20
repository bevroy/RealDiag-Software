"""
Can't-miss conditions: emergent trees that match a common complaint must
always be returned by symptom search, the SMART ambulatory differential and
the encounter assessment, labelled "Can't-miss condition", whatever their
score. The list below is also in docs/CLINICAL_CONTENT_REVIEW.md (section 9).
"""
import asyncio
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from backend.services import symptom_search
from backend.services.symptom_search import CANT_MISS_LABEL, rank_diagnoses
from backend.services.tree_schema import presentation_texts

# complaint -> (age, sex, emergent tree ids that must be returned)
MUST_RETURN = {
    "chest pain": (62, "male", ["CARD-ACUTE-CORONARY-SYNDROME", "CARD-PE", "PULM-PNEUMOTHORAX"]),
    "headache": (40, "male", ["NEU-SAH", "ID-BACTERIAL-MENINGITIS"]),
    "abdominal pain": (28, "female", ["SURG-ACUTE-APPENDICITIS", "OBGYN-ECTOPIC-PREGNANCY", "SURG-AAA-RUPTURED"]),
    "shortness of breath": (55, "male", ["CARD-PE", "PULM-PNEUMOTHORAX"]),
}
# Expected conditions with no tree in the library yet (content work)
MISSING_FROM_LIBRARY = {"chest pain": ["aortic dissection"]}


def ranked(complaint, age, sex, **kwargs):
    response, _ = asyncio.run(rank_diagnoses([complaint], age=age, sex=sex, allow_ai=False, **kwargs))
    return {r.rule_id: r for r in response.results}


@pytest.mark.parametrize("complaint", sorted(MUST_RETURN))
def test_emergent_conditions_returned_and_labelled(complaint):
    age, sex, expected = MUST_RETURN[complaint]
    results = ranked(complaint, age, sex)
    for tree_id in expected:
        assert tree_id in results, f"{complaint!r} did not return {tree_id}"
        assert results[tree_id].cant_miss and results[tree_id].cant_miss_label == CANT_MISS_LABEL


@pytest.mark.parametrize("complaint", sorted(MUST_RETURN))
def test_cant_miss_returned_even_below_the_cap(complaint):
    age, sex, expected = MUST_RETURN[complaint]
    results = ranked(complaint, age, sex, limit=1)
    assert set(expected) <= set(results)


def test_missing_trees_really_are_missing():
    """Fails once a tree is added, so the review doc list is updated."""
    names = {r["label"].lower() for rules in symptom_search.load_all_families().values() for r in rules}
    for conditions in MISSING_FROM_LIBRARY.values():
        for condition in conditions:
            assert not any(condition in n for n in names), f"{condition} now has a tree; update the lists"


def test_non_emergent_matches_are_not_labelled():
    results = ranked("chest pain", 62, "male")
    assert not results["ORTHO-COSTOCHONDRITIS"].cant_miss


def test_ectopic_not_returned_for_male_patient():
    assert "OBGYN-ECTOPIC-PREGNANCY" not in ranked("abdominal pain", 28, "male")


def test_negated_complaint_gives_no_cant_miss_in_encounter_assessment():
    from backend.services import encounter_assessment as ea
    from backend.services.smart_diagnostic_engine import SmartDiagnosticEngine
    from backend.services.smart_router import _diagnosis_response, summary_from_patient_data
    from backend.tests.test_encounter_page_assessment import FakeFHIR, FakeHistory, patient

    result = asyncio.run(ea.assess_encounter("p", "denies chest pain", FakeFHIR(patient()), FakeHistory(),
                                             SmartDiagnosticEngine(), criteria_response=_diagnosis_response,
                                             summary_response=summary_from_patient_data))
    assert result["diagnoses"]["items"] == []


def test_mapping_presentations_are_matched():
    """"- Chest pain: substernal ..." loads as a mapping; it used to be dropped."""
    assert presentation_texts([{"Chest pain": "substernal, pressure-like"}, "Dyspnea", None, {"Signs": ["a", "b"]}]) == [
        "Chest pain: substernal, pressure-like", "Dyspnea", "Signs: a, b"]
    acs = ranked("chest pain", 62, "male")["CARD-ACUTE-CORONARY-SYNDROME"]
    assert "Chest pain: substernal, pressure-like, radiating to left arm/jaw/back" in acs.matched_presentations


def test_synonyms_expand_lay_wording():
    assert symptom_search.expand_synonyms(["shortness of breath"]) == ["shortness of breath", "dyspnea"]
    assert symptom_search.expand_synonyms(["stomach pain"]) == ["stomach pain", "abdominal pain"]
    assert symptom_search.expand_synonyms(["sobbing"]) == ["sobbing"]   # whole phrases only


# --- The three entry points ------------------------------------------------------------

def test_symptom_search_endpoint_returns_cant_miss():
    request = symptom_search.SymptomSearchRequest(symptoms=["chest pain"], age=62, sex="male")
    response = asyncio.run(symptom_search.search_by_symptoms(request, None, current_user={"user_id": "u"}))
    results = {r.rule_id: r for r in response.results}
    assert results["CARD-PE"].cant_miss_label == CANT_MISS_LABEL


def test_ambulatory_differential_returns_cant_miss(monkeypatch):
    from fastapi.testclient import TestClient
    from backend.main import app
    from backend.services import smart_router
    from backend.services.patient_history_service import ComprehensivePatientHistory, HistoryAndPhysical

    history = ComprehensivePatientHistory(
        patient_id="p", patient_name="T", age=40, gender="male",
        history_and_physicals=[HistoryAndPhysical(date="2026-10-19", chief_complaint="headache")])

    class FakeHistoryService:
        def __init__(self, *args, **kwargs):
            pass

        async def get_comprehensive_history(self, patient_id, lookback_days=None):
            return history

    monkeypatch.setattr(smart_router, "PatientHistoryService", FakeHistoryService)
    session = SimpleNamespace(patient_id="p", ehr_vendor="epic", fhir_access_token="t",
                              expires_at=datetime.utcnow() + timedelta(minutes=30))
    app.dependency_overrides[smart_router.get_active_smart_session] = lambda: session
    try:
        body = TestClient(app).get("/smart/patient/p/differential").json()
    finally:
        app.dependency_overrides.pop(smart_router.get_active_smart_session, None)
    results = {r["rule_id"]: r for r in body["differential"]["results"]}
    for tree_id in MUST_RETURN["headache"][2]:
        assert results[tree_id]["cant_miss_label"] == CANT_MISS_LABEL


def test_encounter_assessment_returns_cant_miss_beyond_15():
    from backend.services import encounter_assessment as ea
    from backend.services.smart_diagnostic_engine import SmartDiagnosticEngine
    from backend.services.smart_router import _diagnosis_response, summary_from_patient_data
    from backend.tests.test_encounter_page_assessment import FakeFHIR, FakeHistory, patient

    complaint = "abdominal pain, headache, chest pain, shortness of breath"
    data = patient(gender="female")
    data.age = 28
    result = asyncio.run(ea.assess_encounter("p", complaint, FakeFHIR(data), FakeHistory(), SmartDiagnosticEngine(),
                                             criteria_response=_diagnosis_response,
                                             summary_response=summary_from_patient_data))
    items = {d["tree_id"]: d for d in result["diagnoses"]["items"]}
    expected = {t for _, _, ids in MUST_RETURN.values() for t in ids}
    assert result["diagnoses"]["complaint_matches_total"] > 15
    for tree_id in expected:
        assert items[tree_id]["cant_miss_label"] == CANT_MISS_LABEL, tree_id
