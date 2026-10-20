"""
AI settings: one rule for every language-model feature.

Off unless the setting is exactly "true"; anything AI-generated carries
"AI-generated; not clinically validated."; ranking with allow_ai=False
never calls a language model, whatever the settings.
"""
import asyncio

import pytest

from backend.services import symptom_search
from backend.services.content_labels import (
    AI_CONTENT_LABEL,
    AI_SETTINGS,
    ai_enrichment_enabled,
    ai_generation_enabled,
    ai_setting_enabled,
)

NO_MATCH = ["zzqxv unmatched complaint", "qqxz other"]


@pytest.fixture(autouse=True)
def _clear_settings(monkeypatch):
    for name in AI_SETTINGS:
        monkeypatch.delenv(name, raising=False)


def test_label_text_is_exact():
    assert AI_CONTENT_LABEL == "AI-generated; not clinically validated."


def test_both_settings_are_off_by_default():
    assert not ai_generation_enabled()
    assert not ai_enrichment_enabled()


@pytest.mark.parametrize("value,enabled", [
    ("true", True), (" TRUE ", True), ("True", True),
    ("false", False), ("", False), ("1", False), ("yes", False), ("on", False),
])
@pytest.mark.parametrize("name", AI_SETTINGS)
def test_only_explicit_true_turns_a_setting_on(monkeypatch, name, value, enabled):
    monkeypatch.setenv(name, value)
    assert ai_setting_enabled(name) is enabled


def test_settings_are_independent(monkeypatch):
    monkeypatch.setenv("ENABLE_AI_ENRICHMENT", "true")
    assert ai_enrichment_enabled() and not ai_generation_enabled()


def test_unknown_setting_is_rejected():
    with pytest.raises(ValueError):
        ai_setting_enabled("ENABLE_AI_SOMETHING")


def _ai_returns_one(calls):
    async def fake(symptoms, age=None, sex=None):
        calls.append(symptoms)
        return [{"diagnosis": "Made-up condition", "specialty": "general", "icd10": [], "likelihood": "high",
                 "key_features": ["x"]}]
    return fake


@pytest.mark.parametrize("setting", [None, "true"])
def test_ranking_without_ai_never_calls_a_model(monkeypatch, setting):
    if setting:
        monkeypatch.setenv("ENABLE_AI_GENERATION", setting)
    calls = []
    monkeypatch.setattr(symptom_search, "AI_GENERATION_AVAILABLE", True)
    monkeypatch.setattr(symptom_search, "query_ai_for_diagnoses", _ai_returns_one(calls))
    response, tree_info = asyncio.run(symptom_search.rank_diagnoses(NO_MATCH, allow_ai=False))
    assert calls == []
    assert tree_info is None
    assert not any(r.ai_suggested for r in response.results)


def test_ranking_with_setting_off_never_calls_a_model(monkeypatch):
    calls = []
    monkeypatch.setattr(symptom_search, "AI_GENERATION_AVAILABLE", True)
    monkeypatch.setattr(symptom_search, "query_ai_for_diagnoses", _ai_returns_one(calls))
    response, tree_info = asyncio.run(symptom_search.rank_diagnoses(NO_MATCH))
    assert calls == [] and tree_info is None
    assert not any(r.ai_suggested for r in response.results)


def test_ai_suggestions_are_labelled_when_enabled(monkeypatch):
    monkeypatch.setenv("ENABLE_AI_GENERATION", "true")
    calls = []
    monkeypatch.setattr(symptom_search, "AI_GENERATION_AVAILABLE", True)
    monkeypatch.setattr(symptom_search, "query_ai_for_diagnoses", _ai_returns_one(calls))
    response, tree_info = asyncio.run(symptom_search.rank_diagnoses(NO_MATCH))
    assert calls
    ai = [r for r in response.results if r.ai_suggested]
    assert ai and all(r.ai_label == AI_CONTENT_LABEL for r in ai)
    assert tree_info is None or tree_info["ai_label"] == AI_CONTENT_LABEL


def test_tree_generation_refused_by_default(monkeypatch):
    from fastapi import HTTPException
    monkeypatch.setattr(symptom_search, "AI_GENERATION_AVAILABLE", True)
    request = symptom_search.SymptomSearchRequest(symptoms=["cough", "fever"])
    with pytest.raises(HTTPException) as err:
        asyncio.run(symptom_search.generate_ai_tree(request, background_tasks=None))
    assert err.value.status_code == 403


def test_generated_tree_response_is_labelled(monkeypatch):
    monkeypatch.setenv("ENABLE_AI_GENERATION", "true")
    monkeypatch.setattr(symptom_search, "AI_GENERATION_AVAILABLE", True)

    class FakeGenerator:
        def __init__(self, provider=None):
            pass

        async def generate_tree(self, **kwargs):
            return {"tree_id": "ai_generated_1", "name": "X", "diagnosis": {"name": "X"}}

        def save_tree(self, tree, status="pending"):
            return "/dev/null"

    monkeypatch.setattr(symptom_search, "AITreeGenerator", FakeGenerator)
    request = symptom_search.SymptomSearchRequest(symptoms=["cough", "fever"])
    body = asyncio.run(symptom_search.generate_ai_tree(request, background_tasks=None))
    assert body["ai_generated"] is True
    assert body["ai_content_label"] == AI_CONTENT_LABEL
    assert body["disclaimer"].startswith(AI_CONTENT_LABEL)


# --- EHR data is never sent to an AI provider ------------------------------------

def _forbid_ai(monkeypatch):
    """Turn every AI setting on and make any model call fail the test."""
    for name in AI_SETTINGS:
        monkeypatch.setenv(name, "true")
    monkeypatch.setattr(symptom_search, "AI_GENERATION_AVAILABLE", True)

    async def forbidden(*args, **kwargs):
        raise AssertionError("EHR-driven request reached an AI provider")
    monkeypatch.setattr(symptom_search, "query_ai_for_diagnoses", forbidden)


def test_ambulatory_differential_never_uses_ai(monkeypatch):
    from datetime import datetime, timedelta
    from types import SimpleNamespace
    from fastapi.testclient import TestClient
    from backend.main import app
    from backend.services import smart_router

    _forbid_ai(monkeypatch)
    from backend.services.patient_history_service import ComprehensivePatientHistory, HistoryAndPhysical
    history = ComprehensivePatientHistory(
        patient_id="p", patient_name="T", age=60, gender="male",
        history_and_physicals=[HistoryAndPhysical(date="2026-10-19", chief_complaint="zzqxv odd complaint")])

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
        response = TestClient(app).get("/smart/patient/p/differential")
    finally:
        app.dependency_overrides.pop(smart_router.get_active_smart_session, None)
    assert response.status_code == 200, response.text
    assert not any(r.get("ai_suggested") for r in response.json()["differential"]["results"])


def test_symptom_search_with_chart_never_uses_ai(monkeypatch):
    _forbid_ai(monkeypatch)
    calls = []

    async def fake_rank(symptoms, age=None, sex=None, family=None, allow_ai=True):
        calls.append(allow_ai)
        return symptom_search.SymptomSearchResponse(query_symptoms=symptoms, total_results=0, results=[]), None

    class FakeHistory:
        async def get_comprehensive_history(self, patient_id, lookback_days=None):
            raise RuntimeError("EHR unavailable")   # even when the chart pull fails

    async def fake_service():
        return FakeHistory()

    monkeypatch.setattr(symptom_search, "rank_diagnoses", fake_rank)
    monkeypatch.setattr(symptom_search, "get_patient_history_service", fake_service)
    provider = {"user_id": "u", "role": "provider"}
    typed = symptom_search.SymptomSearchRequest(symptoms=["cough"])
    charted = symptom_search.SymptomSearchRequest(symptoms=["cough"], emr_patient_id="p")
    asyncio.run(symptom_search.search_by_symptoms(typed, None, current_user=provider))
    asyncio.run(symptom_search.search_by_symptoms(charted, None, current_user=provider))
    assert calls == [True, False]   # typed search may use AI (if enabled); chart search never


# --- Pending AI trees require an admin login ---------------------------------------

def test_pending_ai_trees_require_login():
    from fastapi.testclient import TestClient
    from backend.main import app
    assert TestClient(app).get("/search/ai-trees/pending").status_code in (401, 403)


def test_pending_ai_trees_refuse_non_admin():
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as err:
        asyncio.run(symptom_search.get_pending_trees(current_user={"user_id": "u", "role": "provider"}))
    assert err.value.status_code == 403


def test_pending_ai_trees_listed_for_admin_with_label(monkeypatch):
    class FakeGenerator:
        def load_pending_trees(self):
            return [{"tree_id": "ai_1", "name": "X", "metadata": {}}]

    monkeypatch.setattr(symptom_search, "AI_GENERATION_AVAILABLE", True)
    monkeypatch.setattr(symptom_search, "AITreeGenerator", FakeGenerator)
    body = asyncio.run(symptom_search.get_pending_trees(current_user={"user_id": "a", "role": "admin"}))
    assert body["count"] == 1
    assert body["trees"][0]["ai_content_label"] == AI_CONTENT_LABEL
