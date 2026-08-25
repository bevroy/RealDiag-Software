"""
Unit tests for the pure/stateless helper functions in smart_router.py:
issuer validation, OAuth state token signing, patient-match enforcement,
and the handoff narrative generator. None of these touch the database or
a real FHIR server, so they run fast and don't need a live sandbox.
"""
import pytest
from datetime import datetime
from types import SimpleNamespace

from fastapi import HTTPException

from backend.services.smart_router import (
    _validate_iss,
    _create_state_token,
    _verify_state_token,
    _verify_patient_match,
    _generate_handoff_narrative,
    PatientSummaryResponse,
)


# --- _validate_iss ----------------------------------------------------------

def test_validate_iss_accepts_known_epic_host():
    iss = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"
    assert _validate_iss(iss) == iss


def test_validate_iss_rejects_non_https():
    with pytest.raises(HTTPException) as exc_info:
        _validate_iss("http://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4")
    assert exc_info.value.status_code == 400


def test_validate_iss_rejects_unknown_host():
    with pytest.raises(HTTPException) as exc_info:
        _validate_iss("https://not-epic.example.com/FHIR/R4")
    assert exc_info.value.status_code == 400


# --- OAuth state token round trip -------------------------------------------

def test_state_token_round_trip():
    iss = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"
    token = _create_state_token(iss)
    payload = _verify_state_token(token)
    assert payload["iss"] == iss
    assert "nonce" in payload


def test_state_token_rejects_tampered_value():
    token = _create_state_token("https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4")
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
    with pytest.raises(HTTPException) as exc_info:
        _verify_state_token(tampered)
    assert exc_info.value.status_code == 400


def test_state_token_rejects_garbage():
    with pytest.raises(HTTPException) as exc_info:
        _verify_state_token("not-a-real-token")
    assert exc_info.value.status_code == 400


# --- _verify_patient_match ---------------------------------------------------

def test_verify_patient_match_passes_when_ids_match():
    session = SimpleNamespace(patient_id="12345")
    _verify_patient_match(session, "12345")  # should not raise


def test_verify_patient_match_rejects_mismatch():
    session = SimpleNamespace(patient_id="12345")
    with pytest.raises(HTTPException) as exc_info:
        _verify_patient_match(session, "99999")
    assert exc_info.value.status_code == 403


def test_verify_patient_match_skips_check_when_session_has_no_patient():
    # Standalone-launch sessions with no patient in the launch context
    # shouldn't be blocked - see the implementation note from the
    # security-review patch.
    session = SimpleNamespace(patient_id=None)
    _verify_patient_match(session, "anything")  # should not raise


# --- _generate_handoff_narrative ---------------------------------------------

def _summary(name="Anna Cadence", age=45, gender="female"):
    return PatientSummaryResponse(
        patient_id="12345",
        name=name,
        age=age,
        gender=gender,
        lab_count=0,
        vital_count=0,
        condition_count=0,
        medication_count=0,
        abnormal_labs=[],
        recent_vitals=[],
    )


def test_narrative_no_admission_found():
    narrative = _generate_handoff_narrative(_summary(), None, None, "none")
    assert "No active admission found for Anna Cadence" in narrative


def test_narrative_no_updates_since_admission():
    updates = {
        "new_labs": [], "new_abnormal_labs": [],
        "new_vitals": [],
        "new_conditions": [], "new_medications": [],
    }
    start = datetime(2026, 8, 20, 7, 0)
    narrative = _generate_handoff_narrative(_summary(), updates, start, "admission")
    assert "since admission" in narrative
    assert "No new labs." in narrative
    assert "No new vitals recorded." in narrative
    assert "No new conditions added." in narrative
    assert "No new medications ordered." in narrative


def test_narrative_reports_abnormal_labs_and_counts():
    lab = SimpleNamespace(display="Potassium", value=6.2, unit="mmol/L")
    updates = {
        "new_labs": [lab, lab],
        "new_abnormal_labs": [lab],
        "new_vitals": [SimpleNamespace()],
        "new_conditions": [{"code": {"text": "Acute kidney injury"}}],
        "new_medications": [{"medicationCodeableConcept": {"text": "Insulin"}}],
    }
    start = datetime(2026, 8, 20, 7, 0)
    narrative = _generate_handoff_narrative(_summary(), updates, start, "manual")
    assert "since the specified handoff time" in narrative
    assert "2 new lab result(s), including 1 abnormal: Potassium 6.2mmol/L" in narrative
    assert "1 new vital sign reading(s) recorded." in narrative
    assert "1 new condition(s) added to the problem list: Acute kidney injury." in narrative
    assert "1 new medication(s) ordered: Insulin." in narrative
