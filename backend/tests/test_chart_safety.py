"""
Chart-safety tests for the SMART on FHIR decision-support path:
no treatment orders, troponin unit handling, visible data-retrieval
failures, missing-data handling, input quality, and AI/homeopathy labels.
"""
import re
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest
import requests
import yaml

from backend.services.fhir_client import (
    CommonLOINC, FHIRClient, LabResult, PatientData, VitalSign,
)
from backend.services.smart_diagnostic_engine import SmartDiagnosticEngine

ACS = "CARD-ACUTE-CORONARY-SYNDROME"
from backend.services.smart_router import _build_patient_summary, _generate_handoff_narrative
from backend.services.content_labels import AI_CONTENT_LABEL, HOMEOPATHY_VALIDATION_STATEMENT

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 10, 19, 8, 0)

# Drug + dose, STAT orders, or procedure activation - none may appear in output
TREATMENT_ORDER = re.compile(
    r"\d\s*(mg|mcg|g|units?|mL)(/kg|/hr)?\b|\bSTAT\b|cath lab|\badminister\b|insulin drip|start IV",
    re.IGNORECASE,
)


def _lab(code, value, unit, high=None, ref_unit=None, status="final", display="Lab"):
    ref = {"high": high} if high is not None else None
    return LabResult(code=code, display=display, value=value, unit=unit, reference_range=ref,
                     status=status, effective_date=NOW, reference_unit=ref_unit)


def _vital(code, value, unit="/min"):
    return VitalSign(code=code, display="Vital", value=value, unit=unit, effective_date=NOW)


def _patient(labs=(), vitals=(), status=None, age=60):
    return PatientData(
        patient_id="p1", name="Test Patient", age=age, gender="female",
        labs=list(labs), vitals=list(vitals), conditions=[], medications=[], allergies=[],
        retrieval_status=status or {k: "retrieved" for k in ("labs", "vitals", "conditions", "medications", "allergies")},
    )


@pytest.fixture
def engine():
    return SmartDiagnosticEngine()


def _by_id(evaluations, diagnosis_id):
    return next((e for e in evaluations if e.diagnosis_id == diagnosis_id), None)


# --- 1. ACS logic ------------------------------------------------------------

def test_tachycardia_alone_does_not_suggest_acs(engine):
    patient = _patient(
        labs=[_lab(CommonLOINC.TROPONIN_I, 0.01, "ng/mL", high=0.04)],
        vitals=[_vital(CommonLOINC.HEART_RATE, 130, "beats/min")],
    )
    acs = engine.evaluate_tree(ACS, patient)
    assert acs.criteria_met == []
    assert acs.probability == 0
    assert acs.recommendations == []
    assert acs.supporting_findings[0].criterion == "Heart rate"
    assert _by_id(engine.evaluate_patient(patient), ACS) is None


def test_elevated_troponin_gives_supportive_wording_only(engine):
    patient = _patient(labs=[_lab(CommonLOINC.TROPONIN_I, 0.5, "ng/mL", high=0.04)])
    acs = engine.evaluate_tree(ACS, patient)
    assert [c.criterion for c in acs.criteria_met] == ["Elevated troponin"]
    assert acs.recommendations[0].startswith(
        "Findings consistent with acute coronary syndrome; consider evaluation per 2025 ACC/AHA")
    assert acs.criteria_met[0].source.startswith("Fourth Universal Definition of Myocardial Infarction")
    for rec in acs.recommendations:
        assert not TREATMENT_ORDER.search(rec), rec


def test_no_evaluator_issues_treatment_orders(engine):
    patient = _patient(
        labs=[
            _lab(CommonLOINC.TROPONIN_I, 5, "ng/mL", high=0.04),
            _lab(CommonLOINC.WBC, 20, "K/uL"),
            _lab(CommonLOINC.GLUCOSE, 600, "mg/dL"),
            _lab(CommonLOINC.CO2, 10, "mEq/L"),
        ],
        vitals=[
            _vital(CommonLOINC.RESPIRATORY_RATE, 30),
            _vital(CommonLOINC.SYSTOLIC_BP, 80, "mmHg"),
            _vital(CommonLOINC.GCS_SCORE, 12, "{score}"),
        ],
    )
    evaluations = engine.evaluate_patient(patient)
    assert {e.diagnosis_id for e in evaluations} == {ACS, "ID-SEPSIS", "ENDO-DKA"}
    for evaluation in evaluations:
        for rec in evaluation.recommendations:
            assert not TREATMENT_ORDER.search(rec), (evaluation.diagnosis_id, rec)


def test_frontend_alert_lists_have_no_drug_doses():
    for name in ("redFlagAlerts.js", "timeSensitiveAlerts.js"):
        text = (ROOT / "frontend" / "utils" / name).read_text()
        assert not re.search(r"\d\s*(mg|mcg|PE/kg|mL/kg)\b", text), name
        assert "ACTIVATE CATH LAB" not in text and "'Activate cath lab'" not in text


# --- 2. Troponin units -------------------------------------------------------

@pytest.mark.parametrize("value,unit,high,ref_unit,expected", [
    (0.05, "ng/mL", 0.04, None, "moderate"),      # 1.25x URL
    (0.2, "ng/mL", 0.04, None, "high"),           # 5x
    (0.5, "ng/mL", 0.04, None, "critical"),       # 12.5x
    (150, "ng/L", 14, None, "critical"),          # hs-troponin in ng/L, 10.7x
    (40, "ng/L", 14, None, "high"),               # 2.9x
    (0.05, "ng/mL", 26, "ng/L", "moderate"),      # value ng/mL, range ng/L: 50/26 = 1.9x
    (10, "ng/L", 14, None, "low"),                # below URL
])
def test_troponin_severity_uses_units_and_reference_limit(engine, value, unit, high, ref_unit, expected):
    lab = _lab(CommonLOINC.TROPONIN_I, value, unit, high=high, ref_unit=ref_unit)
    assert engine.evaluate_tree(ACS, _patient(labs=[lab])).severity == expected


def test_ng_per_l_value_is_not_compared_with_ng_per_ml_cutoffs(engine):
    # 50 ng/L is 0.05 ng/mL; with a 52 ng/L URL it is NOT elevated
    lab = _lab(CommonLOINC.TROPONIN_I, 50, "ng/L", high=52)
    acs = engine.evaluate_tree(ACS, _patient(labs=[lab]))
    assert acs.criteria_met == [] and acs.criteria_not_met[0].criterion == "Elevated troponin"


@pytest.mark.parametrize("unit,reason", [("", "no unit"), ("mmol/L", "not recognised")])
def test_missing_or_unknown_troponin_unit_gives_unknown_severity(engine, unit, reason):
    patient = _patient(labs=[_lab(CommonLOINC.TROPONIN_I, 0.5, unit, high=0.04)])
    acs = engine.evaluate_tree(ACS, patient)
    assert acs.severity == "unknown"
    assert reason in acs.severity_reason
    assert acs.criteria_unknown and not acs.criteria_met


def test_troponin_without_reference_range_is_unknown(engine):
    patient = _patient(labs=[_lab(CommonLOINC.TROPONIN_I, 0.5, "ng/mL")])
    acs = engine.evaluate_tree(ACS, patient)
    assert acs.severity == "unknown"
    assert "no upper reference limit" in acs.severity_reason
    assert not acs.recommendations or "ACS" not in acs.recommendations[0]


# --- 3. Silent data failures -------------------------------------------------

def _http_error(status_code):
    return requests.HTTPError(f"{status_code} error", response=SimpleNamespace(status_code=status_code))


class _StubClient(FHIRClient):
    """FHIRClient with canned FHIR responses; individual fetches can fail."""

    def __init__(self, fail=None, patient=None, observations=None, conditions=None):
        super().__init__("https://fhir.example.test/R4", "client", access_token="token")
        self.fail = fail or {}
        self.patient = patient if patient is not None else {
            "name": [{"given": ["Test"], "family": "Patient"}], "birthDate": "1960-05-01", "gender": "female",
        }
        self.observations = observations or {"laboratory": [], "vital-signs": []}
        self.conditions = conditions or []

    def _maybe_fail(self, resource):
        if resource in self.fail:
            raise _http_error(self.fail[resource])

    def get_patient(self, patient_id):
        return self.patient

    def get_observations(self, patient_id, category=None, code=None, date_range=None, max_pages=1):
        self._maybe_fail("labs" if category == "laboratory" else "vitals")
        return self.observations.get(category, [])

    def get_conditions(self, patient_id):
        self._maybe_fail("conditions")
        return self.conditions

    def get_medications(self, patient_id):
        self._maybe_fail("medications")
        return []

    def get_allergies(self, patient_id):
        self._maybe_fail("allergies")
        return []


def test_failed_allergy_query_is_reported_not_empty():
    data = _StubClient(fail={"allergies": 500}).get_patient_data("p1")
    assert data.retrieval_status["allergies"] == "failed"
    assert data.retrieval_status["labs"] == "retrieved"
    assert "Allergies could not be retrieved; do not assume none." in data.data_warnings


def test_forbidden_resource_is_not_available():
    data = _StubClient(fail={"medications": 403}).get_patient_data("p1")
    assert data.retrieval_status["medications"] == "not available"
    assert "Medications could not be retrieved; do not assume none." in data.data_warnings


def test_failed_lab_query_no_longer_aborts_the_summary():
    data = _StubClient(fail={"labs": 500}).get_patient_data("p1")
    assert data.retrieval_status["labs"] == "failed"
    assert data.labs == []


def test_summary_counts_are_none_when_not_retrieved():
    summary = _build_patient_summary(_StubClient(fail={"allergies": 500, "conditions": 503}), "p1")
    assert summary.allergy_count is None
    assert summary.condition_count is None
    assert summary.medication_count == 0  # retrieved, none found
    assert summary.data_status["allergies"] == "failed"
    assert "Allergies could not be retrieved; do not assume none." in summary.data_warnings
    assert "Conditions could not be retrieved; do not assume none." in summary.data_warnings


def test_handoff_narrative_says_when_labs_could_not_be_retrieved():
    summary = _build_patient_summary(_StubClient(), "p1")
    updates = {
        "new_labs": [], "new_abnormal_labs": [], "new_vitals": [], "new_conditions": [], "new_medications": [],
        "retrieval_status": {"labs": "failed", "vitals": "retrieved", "conditions": "retrieved", "medications": "retrieved"},
    }
    narrative = _generate_handoff_narrative(summary, updates, NOW - timedelta(days=1), "admission")
    assert "Lab results could not be retrieved; do not assume none." in narrative
    assert "No new labs." not in narrative
    assert "No new vitals recorded." in narrative


def test_updates_since_tracks_status():
    updates = _StubClient(fail={"medications": 500}).get_patient_updates_since("p1", NOW - timedelta(days=2))
    assert updates["retrieval_status"]["medications"] == "failed"
    assert "Medications could not be retrieved; do not assume none." in updates["data_warnings"]


def test_evaluator_exception_is_reported_as_failed(engine, monkeypatch):
    real = engine._evaluate_tree

    def boom(tree_id, patient_data, now=None):
        if tree_id == "ENDO-DKA":
            raise ValueError("bad data")
        return real(tree_id, patient_data, now)
    monkeypatch.setattr(engine, "_evaluate_tree", boom)
    dka = _by_id(engine.evaluate_patient(_patient()), "ENDO-DKA")
    assert dka is not None
    assert dka.evaluation_status == "evaluation failed"
    assert "bad data" in dka.status_reason


# --- 4. Missing data ---------------------------------------------------------

def test_nothing_measured_shows_no_cards(engine):
    assert engine.evaluate_patient(_patient()) == []   # no labs or vitals at all


def test_unreadable_result_is_shown_as_insufficient_data(engine):
    evaluations = engine.evaluate_patient(_patient(labs=[_lab(CommonLOINC.TROPONIN_I, 0.5, "", high=0.04)]))
    acs = _by_id(evaluations, ACS)
    assert acs.evaluation_status == "insufficient data"
    assert "missing" in acs.status_reason


def test_missing_birth_date_gives_unknown_age():
    data = _StubClient(patient={"name": [{"family": "Doe"}], "gender": "male"}).get_patient_data("p1")
    assert data.age is None
    assert any("age is unknown" in note for note in data.data_notes)


def _observation(value=None, status="final", codings=None, unit="mmol/L", ref_high=None):
    obs = {
        "status": status,
        "code": {"coding": codings or [{"system": "http://loinc.org", "code": CommonLOINC.POTASSIUM, "display": "Potassium"}]},
        "valueQuantity": {"value": value, "unit": unit},
        "effectiveDateTime": "2026-10-18T08:00:00Z",
    }
    if ref_high is not None:
        obs["referenceRange"] = [{"high": {"value": ref_high, "unit": unit}}]
    return obs


def test_blank_lab_value_is_skipped_not_zero():
    notes = []
    assert FHIRClient("https://x.test", "c", access_token="t").parse_observation(_observation(value=None), notes) is None
    assert notes and "no value" in notes[0]


def test_zero_reference_low_is_respected():
    lab = _lab("x", -1, "u")
    lab.reference_range = {"low": 0.0}
    lab.__post_init__()
    assert lab.is_abnormal


# --- 5. Input quality --------------------------------------------------------

@pytest.mark.parametrize("status", ["entered-in-error", "cancelled"])
def test_excluded_observations_are_dropped(status):
    notes = []
    client = FHIRClient("https://x.test", "c", access_token="t")
    assert client.parse_observation(_observation(value=4.0, status=status), notes) is None
    assert "excluded" in notes[0]


def test_entered_in_error_condition_is_excluded():
    conditions = [
        {"code": {"text": "Hypertension"}, "verificationStatus": {"coding": [{"code": "confirmed"}]}},
        {"code": {"text": "Diabetes"}, "verificationStatus": {"coding": [{"code": "entered-in-error"}]}},
    ]
    data = _StubClient(conditions=conditions).get_patient_data("p1")
    assert [c["code"]["text"] for c in data.conditions] == ["Hypertension"]
    assert any("Diabetes" in note for note in data.data_notes)


def test_preliminary_result_is_labelled():
    obs = _observation(value=6.5, status="preliminary", ref_high=5.0)
    summary = _build_patient_summary(_StubClient(observations={"laboratory": [obs], "vital-signs": []}), "p1")
    assert summary.abnormal_labs[0]["preliminary"] is True


def test_loinc_code_found_in_any_coding():
    codings = [
        {"system": "urn:oid:1.2.840.114350", "code": "12345", "display": "Troponin (local)"},
        {"system": "http://loinc.org", "code": CommonLOINC.TROPONIN_I, "display": "Troponin I"},
    ]
    lab = FHIRClient("https://x.test", "c", access_token="t").parse_observation(
        _observation(value=0.5, codings=codings, unit="ng/mL"))
    assert lab.code == CommonLOINC.TROPONIN_I


def test_non_loinc_first_coding_is_not_treated_as_loinc():
    codings = [{"system": "urn:oid:local", "code": CommonLOINC.TROPONIN_I}]
    lab = FHIRClient("https://x.test", "c", access_token="t").parse_observation(
        _observation(value=0.5, codings=codings, unit="ng/mL"))
    assert lab.code is None


# --- 6. AI content and homeopathy labels -------------------------------------

def test_ai_enrichment_off_by_default(monkeypatch):
    from backend.services import content_labels
    monkeypatch.delenv("ENABLE_AI_ENRICHMENT", raising=False)
    assert content_labels.ai_enrichment_enabled() is False
    monkeypatch.setenv("ENABLE_AI_ENRICHMENT", "true")
    assert content_labels.ai_enrichment_enabled() is True


def test_ai_enrichment_labels_every_filled_section():
    from backend.services.search_router import _apply_ai_enrichment
    result = {"name": "X", "presentations": ["cough"], "workup": [], "treatment": [],
              "clinical_pearls": [], "referrals": [], "homeopathic_remedies": []}
    enriched = {"workup": ["CBC"], "treatment": ["Supportive care"],
                "homeopathy": [{"remedy": "Arnica 30C", "indications": "bruising"}]}
    _apply_ai_enrichment(result, enriched)
    assert result["ai_generated_sections"] == {
        "workup": AI_CONTENT_LABEL, "treatment": AI_CONTENT_LABEL, "homeopathic_remedies": AI_CONTENT_LABEL,
    }
    assert "presentations" not in result["ai_generated_sections"]  # existing content untouched
    assert result["homeopathic_remedies"] == ["Arnica 30C: bruising"]
    assert result["homeopathy_validation_statement"] == HOMEOPATHY_VALIDATION_STATEMENT
    assert AI_CONTENT_LABEL == "AI-generated; not clinically validated."


def test_tree_homeopathy_in_search_results_carries_statement():
    from backend.services.search_router import _extract_clinical_info
    tree = {"name": "Test", "nodes": [{"id": "n", "homeopathy": [{"remedy": "Arnica 30C", "indications": "x"}]}]}
    info = _extract_clinical_info(tree)
    assert info["homeopathy_validation_statement"] == HOMEOPATHY_VALIDATION_STATEMENT


def test_ai_suggested_symptom_match_carries_label():
    from backend.services.symptom_search import DiagnosisMatch
    match = DiagnosisMatch(rule_id="X", label="X", family="f", match_score=1.0, matched_presentations=[],
                           all_presentations=[], icd10=[], snomed=[], ai_suggested=True, ai_label=AI_CONTENT_LABEL)
    assert match.ai_label == AI_CONTENT_LABEL


def test_homeopathy_api_includes_validation_statement():
    from backend.services.homeopathy_router import HomeopathyResponse
    assert HomeopathyResponse(remedies=[]).validation_statement == HOMEOPATHY_VALIDATION_STATEMENT


# --- 8. Test environment config ----------------------------------------------

def test_test_backend_uses_test_database():
    config = yaml.safe_load((ROOT / "render-test-final.yaml").read_text())
    backend = next(s for s in config["services"] if s["name"] == "realdiag-test-backend")
    db_var = next(v for v in backend["envVars"] if v["key"] == "DATABASE_URL")
    assert db_var["fromDatabase"]["name"] == "realdiag-test-database"


# --- DKA glucose units -------------------------------------------------------

def _dka(engine, glucose_value, glucose_unit, co2=None):
    labs = [_lab(CommonLOINC.GLUCOSE, glucose_value, glucose_unit)]
    if co2 is not None:
        labs.append(_lab(CommonLOINC.CO2, co2, "mmol/L"))
    return engine.evaluate_tree("ENDO-DKA", _patient(labs=labs))


def _glucose(dka):
    return next(c for c in dka.criteria_met + dka.criteria_not_met + dka.criteria_unknown
                if c.criterion.startswith("Glucose"))


@pytest.mark.parametrize("value,unit,met", [
    (600, "mg/dL", True),
    (30, "mmol/L", True),     # 540 mg/dL
    (12, "mmol/L", True),     # 216 mg/dL
    (10, "mmol/L", False),    # 180 mg/dL
    (200, "mg/dL", True),     # 2024 consensus: >= 200 mg/dL
    (199, "mg/dL", False),
])
def test_dka_glucose_converted_before_comparison(engine, value, unit, met):
    assert (_glucose(_dka(engine, value, unit)).status.value == "present") is met


def test_mmol_glucose_is_not_read_as_mg_dl(engine):
    assert _glucose(_dka(engine, 30, "mmol/L", co2=12)).value == "30 mmol/L (= 540 mg/dL)"


@pytest.mark.parametrize("unit,reason", [("", "no unit"), ("g/L", "not recognised")])
def test_dka_glucose_unit_missing_or_unknown(engine, unit, reason):
    dka = _dka(engine, 600, unit, co2=12)
    glucose = _glucose(dka)
    assert glucose.status.value == "unknown" and reason in glucose.details
    assert "Blood glucose with units (mg/dL or mmol/L)" in dka.missing_tests


# --- Patient history service retrieval status --------------------------------

import asyncio  # noqa: E402

import httpx  # noqa: E402

from backend.services.patient_history_service import PatientHistoryService  # noqa: E402

_EMPTY_BUNDLE = {"resourceType": "Bundle", "entry": []}


def _history_service(failures):
    """PatientHistoryService whose FHIR server fails the given resource paths."""
    def handler(request):
        path = request.url.path.rsplit("/", 2)
        resource = path[-1] if path[-1] != "p1" else path[-2]
        if resource in failures:
            return httpx.Response(failures[resource], json={})
        if resource == "Patient":
            return httpx.Response(200, json={"name": [{"given": ["Ann"], "family": "Lee"}],
                                             "birthDate": "1970-01-01", "gender": "female"})
        return httpx.Response(200, json=_EMPTY_BUNDLE)

    service = PatientHistoryService("https://fhir.example.test/R4", auth_token="t")
    service.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return service


def test_history_service_reports_status_per_data_type():
    history = asyncio.run(_history_service({"AllergyIntolerance": 500, "MedicationRequest": 403})
                          .get_comprehensive_history("p1"))
    assert history.retrieval_status["allergies"] == "failed"
    assert history.retrieval_status["medications"] == "not available"
    assert history.retrieval_status["conditions"] == "retrieved"
    assert history.retrieval_status["visit_notes"] == "retrieved"
    assert "Allergies could not be retrieved; do not assume none." in history.data_warnings
    assert "Medications could not be retrieved; do not assume none." in history.data_warnings
    assert len(history.data_warnings) == 2


def test_history_service_transport_error_is_failed():
    def handler(request):
        if "Condition" in request.url.path:
            raise httpx.ConnectError("connection reset")
        return httpx.Response(200, json=_EMPTY_BUNDLE if "Patient" not in request.url.path else {})

    service = PatientHistoryService("https://fhir.example.test/R4", auth_token="t")
    service.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    history = asyncio.run(service.get_comprehensive_history("p1"))
    assert history.retrieval_status["conditions"] == "failed"


def test_history_status_is_not_shared_between_concurrent_requests():
    # One shared service instance (as symptom_search uses); allergies fail
    # only for patient "bad". Requests interleave at every await.
    async def handler(request):
        await asyncio.sleep(0)
        if "AllergyIntolerance" in request.url.path and request.url.params.get("patient") == "bad":
            return httpx.Response(500, json={})
        if "/Patient/" in request.url.path:
            return httpx.Response(200, json={"name": [{"family": "X"}], "birthDate": "1970-01-01"})
        return httpx.Response(200, json=_EMPTY_BUNDLE)

    service = PatientHistoryService("https://fhir.example.test/R4", auth_token="t")
    service.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    async def both():
        return await asyncio.gather(
            service.get_comprehensive_history("bad"), service.get_comprehensive_history("good"))

    bad_history, good_history = asyncio.run(both())
    assert bad_history.retrieval_status["allergies"] == "failed"
    assert good_history.retrieval_status["allergies"] == "retrieved"
    assert good_history.data_warnings == []


def test_ambulatory_differential_shows_retrieval_warnings(monkeypatch):
    from fastapi.testclient import TestClient
    from backend.main import app
    from backend.services import smart_router
    from backend.services.symptom_search import SymptomSearchResponse

    service = _history_service({"AllergyIntolerance": 500})
    monkeypatch.setattr(smart_router, "PatientHistoryService", lambda **kwargs: service)

    async def fake_rank(terms, age=None, sex=None, allow_ai=True):
        assert allow_ai is False   # chart-driven: never AI
        return SymptomSearchResponse(query_symptoms=terms, total_results=0, results=[]), None
    monkeypatch.setattr(smart_router, "rank_diagnoses", fake_rank)

    session = SimpleNamespace(patient_id="p1", ehr_vendor="epic", fhir_access_token="t",
                              expires_at=datetime.utcnow() + timedelta(minutes=30))
    app.dependency_overrides[smart_router.get_active_smart_session] = lambda: session
    try:
        response = TestClient(app).get("/smart/patient/p1/differential", params={"symptoms": "cough"})
    finally:
        app.dependency_overrides.pop(smart_router.get_active_smart_session, None)

    assert response.status_code == 200
    body = response.json()
    assert body["data_status"]["allergies"] == "failed"
    assert body["data_pulled"]["allergies"] is None
    assert body["data_pulled"]["current_medications"] == 0
    assert "Allergies could not be retrieved; do not assume none." in body["data_warnings"]
    assert "Allergies could not be retrieved" in body["chart_summary"]
