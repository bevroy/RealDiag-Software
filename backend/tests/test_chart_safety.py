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
    acs = engine._evaluate_acs(patient)
    assert acs.criteria_met == []
    assert acs.probability == 0
    assert acs.recommendations == []
    assert acs.supporting_findings[0].criterion == "Heart rate"
    assert _by_id(engine.evaluate_patient(patient), "CARD-ACS") is None


def test_elevated_troponin_gives_supportive_wording_only(engine):
    patient = _patient(labs=[_lab(CommonLOINC.TROPONIN_I, 0.5, "ng/mL", high=0.04)])
    acs = engine._evaluate_acs(patient)
    assert [c.criterion for c in acs.criteria_met] == ["Elevated troponin"]
    assert acs.recommendations[0].startswith("Findings may warrant evaluation for ACS per ACC/AHA")
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
    assert {e.diagnosis_id for e in evaluations} == {"CARD-ACS", "ID-SEPSIS", "ENDO-DKA"}
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
def test_troponin_severity_uses_units_and_reference_limit(value, unit, high, ref_unit, expected):
    lab = _lab(CommonLOINC.TROPONIN_I, value, unit, high=high, ref_unit=ref_unit)
    assert SmartDiagnosticEngine.assess_troponin(lab)["severity"] == expected


def test_ng_per_l_value_is_not_compared_with_ng_per_ml_cutoffs():
    # 50 ng/L is 0.05 ng/mL; with a 52 ng/L URL it is NOT elevated
    lab = _lab(CommonLOINC.TROPONIN_I, 50, "ng/L", high=52)
    assessment = SmartDiagnosticEngine.assess_troponin(lab)
    assert assessment["elevated"] is False


@pytest.mark.parametrize("unit,reason", [("", "no unit"), ("mmol/L", "not recognised")])
def test_missing_or_unknown_troponin_unit_gives_unknown_severity(engine, unit, reason):
    patient = _patient(labs=[_lab(CommonLOINC.TROPONIN_I, 0.5, unit, high=0.04)])
    acs = engine._evaluate_acs(patient)
    assert acs.severity == "unknown"
    assert reason in acs.severity_reason
    assert acs.criteria_unknown and not acs.criteria_met


def test_troponin_without_reference_range_is_unknown(engine):
    patient = _patient(labs=[_lab(CommonLOINC.TROPONIN_I, 0.5, "ng/mL")])
    acs = engine._evaluate_acs(patient)
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

    def get_observations(self, patient_id, category=None, code=None, date_range=None):
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
    def boom(patient_data):
        raise ValueError("bad data")
    monkeypatch.setattr(engine, "_evaluate_dka", boom)
    dka = _by_id(engine.evaluate_patient(_patient()), "ENDO-DKA")
    assert dka is not None
    assert dka.evaluation_status == "evaluation failed"
    assert "bad data" in dka.status_reason


# --- 4. Missing data ---------------------------------------------------------

def test_unknown_criteria_are_shown_as_insufficient_data(engine):
    evaluations = engine.evaluate_patient(_patient())  # no labs or vitals at all
    assert {e.diagnosis_id for e in evaluations} == {"CARD-ACS", "ID-SEPSIS", "ENDO-DKA"}
    for evaluation in evaluations:
        assert evaluation.evaluation_status == "insufficient data"
        assert evaluation.missing_tests
        assert "missing" in evaluation.status_reason


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
