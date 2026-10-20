"""
Negation in the shared ranking (typed symptom search, SMART ambulatory
differential, encounter assessment): negated parts of the input are not
searched and cannot trigger a can't-miss label.
"""
import asyncio
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from backend.services import symptom_search
from backend.services.complaint_matching import split_negated
from backend.services.symptom_search import rank_diagnoses

ACS = "CARD-ACUTE-CORONARY-SYNDROME"


def ranked(symptoms, **kwargs):
    response, _ = asyncio.run(rank_diagnoses(symptoms, age=60, sex="male", allow_ai=False, **kwargs))
    return response


@pytest.mark.parametrize("text,kept,dropped", [
    ("no chest pain", "", ["chest pain"]),
    ("denies chest pain", "", ["chest pain"]),
    ("chest pain, no fever", "chest pain", ["fever"]),
    ("denies fever but new confusion", "new confusion", ["fever"]),
    ("chest pain without radiation", "chest pain", ["radiation"]),
    ("no appetite", "no appetite", []),            # a symptom, not a negation
    ("not eating, no fever", "not eating", ["fever"]),
])
def test_split_negated(text, kept, dropped):
    assert split_negated(text) == (kept, dropped)


@pytest.mark.parametrize("complaint", ["no chest pain", "denies chest pain", "Negative for chest pain"])
def test_negated_chest_pain_gives_no_cant_miss_acs(complaint):
    response = ranked([complaint])
    assert ACS not in {r.rule_id for r in response.results}
    assert not any(r.cant_miss for r in response.results)
    assert response.negated_terms


def test_affirmed_part_still_searched():
    response = ranked(["chest pain, no fever"])
    results = {r.rule_id: r for r in response.results}
    assert results[ACS].cant_miss
    assert "ID-SEPSIS" not in results
    assert response.negated_terms == ["fever"]
    assert response.query_symptoms == ["chest pain, no fever"]


def test_typed_symptom_search_endpoint(monkeypatch):
    for name in ("ENABLE_AI_GENERATION",):
        monkeypatch.setenv(name, "true")
    monkeypatch.setattr(symptom_search, "AI_GENERATION_AVAILABLE", True)

    async def forbidden(*args, **kwargs):
        raise AssertionError("nothing affirmed to search; AI must not be asked")
    monkeypatch.setattr(symptom_search, "query_ai_for_diagnoses", forbidden)
    request = symptom_search.SymptomSearchRequest(symptoms=["no chest pain"], age=60, sex="male")
    response = asyncio.run(symptom_search.search_by_symptoms(request, None, current_user={"user_id": "u"}))
    assert response.results == [] and response.negated_terms == ["chest pain"]


def test_ambulatory_differential_negated_chief_complaint(monkeypatch):
    from fastapi.testclient import TestClient
    from backend.main import app
    from backend.services import smart_router
    from backend.services.patient_history_service import ComprehensivePatientHistory, HistoryAndPhysical

    history = ComprehensivePatientHistory(
        patient_id="p", patient_name="T", age=60, gender="male",
        history_and_physicals=[HistoryAndPhysical(date="2026-10-19", chief_complaint="Cough. No chest pain.")])

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
    assert ACS not in results
    assert "chest pain" in body["differential"]["negated_terms"]


def test_encounter_assessment_negated_complaint():
    from backend.services import encounter_assessment as ea
    from backend.services.smart_diagnostic_engine import SmartDiagnosticEngine
    from backend.services.smart_router import _diagnosis_response, summary_from_patient_data
    from backend.tests.test_encounter_page_assessment import FakeFHIR, FakeHistory, patient

    result = asyncio.run(ea.assess_encounter("p", "cough, no chest pain", FakeFHIR(patient()), FakeHistory(),
                                             SmartDiagnosticEngine(), criteria_response=_diagnosis_response,
                                             summary_response=summary_from_patient_data))
    items = {d["tree_id"]: d for d in result["diagnoses"]["items"]}
    assert ACS not in items
    assert result["complaint"]["negated_terms"] == ["chest pain"]
