"""
Endpoint-level tests for the SMART on FHIR router. These use the real
FastAPI app (routing, the /smart/ PUBLIC_PREFIXES exemption, etc.) but
replace two things so no database or real FHIR server is needed:

  1. get_active_smart_session is overridden per-test via
     app.dependency_overrides, standing in for a real DB-backed session.
  2. FHIRClient (as imported into smart_router.py) is monkeypatched with a
     fake that returns canned data, standing in for a real Epic sandbox
     call.

GET /smart/session/status doesn't use get_active_smart_session (it's
designed to never throw, even with no session), so its tests
monkeypatch get_smart_session directly instead.
"""
import pytest
from datetime import datetime, timedelta
from types import SimpleNamespace

from backend.services import smart_router as smart_router_module
from backend.services.smart_router import get_active_smart_session
from backend.main import app


# --- fakes -------------------------------------------------------------

def _fake_session(patient_id="12345", ehr_vendor="epic", expires_in_minutes=30):
    return SimpleNamespace(
        patient_id=patient_id,
        ehr_vendor=ehr_vendor,
        fhir_access_token="fake-access-token",
        expires_at=datetime.utcnow() + timedelta(minutes=expires_in_minutes),
    )


def _fake_lab(display, value, unit, abnormal=False, ref_range="3.5-5.0"):
    return SimpleNamespace(
        display=display, value=value, unit=unit, is_abnormal=abnormal,
        reference_range=ref_range, effective_date=datetime(2026, 8, 24, 9, 0),
        code="LAB1",
    )


def _fake_vital(code, display, value, unit):
    return SimpleNamespace(
        code=code, display=display, value=value, unit=unit,
        effective_date=datetime(2026, 8, 24, 9, 0),
    )


def _fake_patient_data():
    return SimpleNamespace(
        patient_id="12345",
        name="Anna Cadence",
        age=45,
        gender="female",
        labs=[_fake_lab("Potassium", 6.2, "mmol/L", abnormal=True)],
        vitals=[_fake_vital("8867-4", "Heart Rate", 88, "bpm")],
        conditions=[], medications=[],
    )


class _FakeFHIRClient:
    """Stands in for the real FHIRClient - no network calls."""
    def __init__(self, *args, **kwargs):
        pass

    def get_patient_data(self, patient_id):
        return _fake_patient_data()

    def get_current_encounter(self, patient_id):
        return None

    def get_patient_updates_since(self, patient_id, since):
        return {
            "new_labs": [], "new_abnormal_labs": [],
            "new_vitals": [], "new_conditions": [], "new_medications": [],
        }


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.pop(get_active_smart_session, None)


@pytest.fixture
def fake_fhir_client(monkeypatch):
    monkeypatch.setattr(smart_router_module, "FHIRClient", _FakeFHIRClient)
    monkeypatch.setattr(
        smart_router_module.diagnostic_engine, "evaluate_patient", lambda **kwargs: []
    )


# --- GET /smart/session/status ----------------------------------------------

def test_session_status_no_cookie_returns_inactive(test_client):
    response = test_client.get("/smart/session/status")
    assert response.status_code == 200
    assert response.json()["active"] is False


def test_session_status_unknown_cookie_returns_inactive(test_client, monkeypatch):
    monkeypatch.setattr(smart_router_module, "get_smart_session", lambda sid: None)
    response = test_client.get(
        "/smart/session/status", cookies={"realdiag_smart_session": "does-not-exist"}
    )
    assert response.status_code == 200
    assert response.json()["active"] is False


def test_session_status_active_session_reports_patient(test_client, monkeypatch):
    monkeypatch.setattr(
        smart_router_module, "get_smart_session", lambda sid: _fake_session()
    )
    response = test_client.get(
        "/smart/session/status", cookies={"realdiag_smart_session": "abc123"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["active"] is True
    assert body["patient_id"] == "12345"
    assert body["ehr_vendor"] == "epic"


# --- Auth requirement: every patient-scoped endpoint needs a session --------

def test_patient_summary_requires_session(test_client):
    response = test_client.get("/smart/patient/12345")
    assert response.status_code == 401


def test_evaluate_patient_requires_session(test_client):
    response = test_client.post("/smart/evaluate-patient", json={"patient_id": "12345"})
    assert response.status_code == 401


def test_handoff_requires_session(test_client):
    response = test_client.get("/smart/patient/12345/handoff")
    assert response.status_code == 401


# --- Patient-match enforcement (the security-review follow-up fix) ---------

def test_patient_summary_rejects_mismatched_patient(test_client):
    app.dependency_overrides[get_active_smart_session] = lambda: _fake_session(patient_id="12345")
    response = test_client.get("/smart/patient/99999")
    assert response.status_code == 403


def test_evaluate_patient_rejects_mismatched_patient(test_client):
    app.dependency_overrides[get_active_smart_session] = lambda: _fake_session(patient_id="12345")
    response = test_client.post("/smart/evaluate-patient", json={"patient_id": "99999"})
    assert response.status_code == 403


def test_handoff_rejects_mismatched_patient(test_client):
    app.dependency_overrides[get_active_smart_session] = lambda: _fake_session(patient_id="12345")
    response = test_client.get("/smart/patient/99999/handoff")
    assert response.status_code == 403


# --- Happy paths (with FHIRClient faked out) --------------------------------

def test_patient_summary_happy_path(test_client, fake_fhir_client):
    app.dependency_overrides[get_active_smart_session] = lambda: _fake_session(patient_id="12345")
    response = test_client.get("/smart/patient/12345")
    assert response.status_code == 200
    body = response.json()
    assert body["patient_id"] == "12345"
    assert body["name"] == "Anna Cadence"
    assert len(body["abnormal_labs"]) == 1
    assert body["abnormal_labs"][0]["name"] == "Potassium"


def test_evaluate_patient_happy_path(test_client, fake_fhir_client):
    app.dependency_overrides[get_active_smart_session] = lambda: _fake_session(patient_id="12345")
    response = test_client.post("/smart/evaluate-patient", json={"patient_id": "12345"})
    assert response.status_code == 200
    assert response.json() == []


def test_handoff_falls_back_when_no_active_admission(test_client, fake_fhir_client):
    app.dependency_overrides[get_active_smart_session] = lambda: _fake_session(patient_id="12345")
    response = test_client.get("/smart/patient/12345/handoff")
    assert response.status_code == 200
    body = response.json()
    assert body["timeframe_source"] == "none"
    assert body["admission_start"] is None
    assert "No active admission found" in body["narrative"]


def test_handoff_accepts_manual_since_override(test_client, fake_fhir_client):
    app.dependency_overrides[get_active_smart_session] = lambda: _fake_session(patient_id="12345")
    response = test_client.get(
        "/smart/patient/12345/handoff", params={"since": "2026-08-24T07:00:00"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["timeframe_source"] == "manual"
    assert "since the specified handoff time" in body["narrative"]


# --- /smart/launch: issuer allowlist is checked before anything else -------

def test_launch_rejects_unknown_iss(test_client):
    response = test_client.get(
        "/smart/launch", params={"iss": "https://not-epic.example.com/FHIR/R4", "launch": "abc"}
    )
    assert response.status_code == 400
