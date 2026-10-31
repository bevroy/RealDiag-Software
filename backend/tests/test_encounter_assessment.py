"""
Criteria-driven chart evaluation: chronic-condition display rules, known
conditions on the problem list, each new condition's criteria, unit handling,
the longer-lookback FHIR fetch, and the validator's criteria checks.
"""
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
import requests

from backend.services.fhir_client import FHIRClient, LabResult, PatientData, VitalSign
from backend.services.smart_diagnostic_engine import SmartDiagnosticEngine

NOW = datetime(2026, 10, 19, 8, 0)
ALL_RETRIEVED = {k: "retrieved" for k in ("labs", "vitals", "conditions", "medications", "allergies")}
CHRONIC = {"ENDO-DIABETES", "ENDO-PREDIABETES", "CARD-HYPERTENSION", "NEPHRO-CHRONIC-KIDNEY-DISEASE",
           "HEME-ANEMIA", "ENDO-HYPOTHYROIDISM", "NEPHRO-HYPERKALEMIA", "ENDO-DYSLIPIDEMIA"}
ACUTE = {"CARD-ACUTE-CORONARY-SYNDROME", "ID-SEPSIS", "ENDO-DKA"}


def lab(code, value, unit, days_ago=1, high=None, low=None):
    ref = {}
    if high is not None:
        ref["high"] = high
    if low is not None:
        ref["low"] = low
    return LabResult(code=code, display=code, value=value, unit=unit, reference_range=ref or None,
                     effective_date=NOW - timedelta(days=days_ago))


def bp(systolic, diastolic, days_ago):
    when = NOW - timedelta(days=days_ago)
    return [VitalSign(code="8480-6", display="SBP", value=systolic, unit="mm[Hg]", effective_date=when),
            VitalSign(code="8462-4", display="DBP", value=diastolic, unit="mm[Hg]", effective_date=when)]


def patient(labs=(), vitals=(), gender="female", conditions=(), status=None):
    return PatientData(patient_id="p", name="Test", age=55, gender=gender, labs=list(labs), vitals=list(vitals),
                       conditions=list(conditions), medications=[], allergies=[],
                       retrieval_status=dict(status or ALL_RETRIEVED))


def problem(code, system="http://hl7.org/fhir/sid/icd-10-cm", text=None):
    return {"code": {"text": text, "coding": [{"system": system, "code": code}]}}


@pytest.fixture(scope="module")
def engine():
    return SmartDiagnosticEngine()


def shown(engine, data):
    assessment = engine.evaluate_encounter(data, now=NOW)
    return {e.diagnosis_id: e for e in assessment.evaluations}, assessment.warnings


# --- Condition 1: chronic cards hidden only when retrieved and not done -------

def test_no_cards_when_nothing_relevant_was_measured(engine):
    results, warnings = shown(engine, patient())
    assert results == {}                  # neither chronic nor acute cards
    assert warnings == []


def test_failed_lab_query_gives_global_warning_not_silence(engine):
    status = dict(ALL_RETRIEVED, labs="failed")
    results, warnings = shown(engine, patient(status=status))
    assert not CHRONIC & set(results)
    assert "Some conditions could not be assessed: lab results could not be retrieved." in warnings


def test_failed_vitals_query_gives_global_warning(engine):
    status = dict(ALL_RETRIEVED, vitals="not available")
    _, warnings = shown(engine, patient(status=status))
    assert "Some conditions could not be assessed: vital signs could not be retrieved." in warnings


def test_chronic_condition_with_unreadable_result_is_shown_as_insufficient_data(engine):
    results, _ = shown(engine, patient(labs=[lab("2823-3", 6.8, "")]))
    k = results["NEPHRO-HYPERKALEMIA"]
    assert k.evaluation_status == "insufficient data"
    assert "potassium result has no unit" in k.criteria_unknown[0].details


def test_anemia_with_unknown_sex_is_reported(engine):
    _, warnings = shown(engine, patient(labs=[lab("718-7", 9.0, "g/dL")], gender="unknown"))
    assert any(w.endswith("could not be assessed: patient sex is not recorded.") for w in warnings)


# --- Condition 2: known condition on the problem list --------------------------

def test_known_condition_labelled_not_presented_as_new(engine):
    data = patient(labs=[lab("4548-4", 7.2, "%", 100), lab("4548-4", 7.5, "%", 5)],
                   conditions=[problem("E11.9", text="Type 2 diabetes mellitus")])
    dm = shown(engine, data)[0]["ENDO-DIABETES"]
    assert dm.known_condition is True
    assert dm.known_condition_text == "Type 2 diabetes mellitus"
    assert dm.recommendations[0] == "Known condition on the problem list (Type 2 diabetes mellitus)."
    assert dm.recommendations[1].startswith("Current findings consistent with diabetes mellitus")
    assert not any(r.startswith("Findings consistent with") for r in dm.recommendations)


def test_known_condition_matched_by_snomed(engine):
    data = patient(vitals=bp(150, 95, 30) + bp(148, 92, 2),
                   conditions=[problem("38341003", system="http://snomed.info/sct", text="Hypertension")])
    assert shown(engine, data)[0]["CARD-HYPERTENSION"].known_condition is True


def test_unrelated_problem_is_not_a_known_condition(engine):
    data = patient(vitals=bp(150, 95, 30) + bp(148, 92, 2), conditions=[problem("J45.909", text="Asthma")])
    htn = shown(engine, data)[0]["CARD-HYPERTENSION"]
    assert htn.known_condition is False
    assert htn.recommendations[0].startswith("Findings consistent with hypertension")


# --- Each new condition -------------------------------------------------------

def test_diabetes_needs_two_abnormal_results(engine):
    one = shown(engine, patient(labs=[lab("4548-4", 7.0, "%")]))[0]["ENDO-DIABETES"]
    assert one.finding == "possible"
    assert "1 of 2 required abnormal results" in one.recommendations[0]
    two = shown(engine, patient(labs=[lab("4548-4", 7.0, "%"), lab("1558-6", 140, "mg/dL")]))[0]["ENDO-DIABETES"]
    assert two.finding == "consistent"
    normal = shown(engine, patient(labs=[lab("4548-4", 5.2, "%")]))[0]
    assert "ENDO-DIABETES" not in normal


def test_hba1c_in_mmol_per_mol_is_converted(engine):
    data = patient(labs=[lab("59261-8", 53, "mmol/mol", 40), lab("59261-8", 58, "mmol/mol", 2)])
    assert shown(engine, data)[0]["ENDO-DIABETES"].finding == "consistent"   # 53 mmol/mol = 7.0%


def test_prediabetes_range(engine):
    results = shown(engine, patient(labs=[lab("4548-4", 6.0, "%")]))[0]
    assert results["ENDO-PREDIABETES"].finding == "consistent"
    assert "ENDO-DIABETES" not in results


def test_hypertension_needs_two_days(engine):
    one_day = shown(engine, patient(vitals=bp(150, 95, 1) + bp(152, 96, 1)))[0]["CARD-HYPERTENSION"]
    assert one_day.finding == "possible"
    two_days = shown(engine, patient(vitals=bp(135, 85, 20) + bp(134, 84, 2)))[0]["CARD-HYPERTENSION"]
    assert two_days.finding == "consistent" and two_days.severity == "moderate"
    stage2 = shown(engine, patient(vitals=bp(150, 95, 20) + bp(148, 92, 2)))[0]["CARD-HYPERTENSION"]
    assert stage2.severity == "high" and "Stage 2" in stage2.severity_reason


def test_ckd_needs_three_months(engine):
    short = shown(engine, patient(labs=[lab("33914-3", 50, "mL/min/1.73m2", 30), lab("33914-3", 48, "mL/min/1.73m2", 2)]))[0]
    assert short["NEPHRO-CHRONIC-KIDNEY-DISEASE"].finding == "possible"
    persistent = shown(engine, patient(labs=[lab("62238-1", 50, "mL/min/{1.73_m2}", 120), lab("62238-1", 48, "mL/min/{1.73_m2}", 2)]))[0]
    assert persistent["NEPHRO-CHRONIC-KIDNEY-DISEASE"].finding == "consistent"
    acr = shown(engine, patient(labs=[lab("9318-7", 45, "mg/g", 200), lab("9318-7", 5.0, "mg/mmol", 10)]))[0]
    assert acr["NEPHRO-CHRONIC-KIDNEY-DISEASE"].finding == "consistent"   # 5.0 mg/mmol = 44 mg/g


def test_anemia_uses_sex_specific_cutoffs_and_units(engine):
    female = shown(engine, patient(labs=[lab("718-7", 125, "g/L")], gender="female"))[0]
    assert "HEME-ANEMIA" not in female                                    # 12.5 g/dL
    male = shown(engine, patient(labs=[lab("718-7", 125, "g/L")], gender="male"))[0]
    assert male["HEME-ANEMIA"].finding == "consistent"                    # < 13.0 g/dL


def test_hypothyroidism_uses_lab_reference_range(engine):
    overt = shown(engine, patient(labs=[lab("3016-3", 9.0, "mIU/L", high=4.5), lab("3024-7", 0.5, "ng/dL", low=0.8)]))[0]
    hypo = overt["ENDO-HYPOTHYROIDISM"]
    assert hypo.finding == "consistent" and "overt" in hypo.severity_reason
    subclinical = shown(engine, patient(labs=[lab("3016-3", 6.0, "uIU/mL", high=4.5)]))[0]["ENDO-HYPOTHYROIDISM"]
    assert "subclinical" in subclinical.severity_reason
    no_range = shown(engine, patient(labs=[lab("3016-3", 9.0, "mIU/L")]))[0]["ENDO-HYPOTHYROIDISM"]
    assert no_range.evaluation_status == "insufficient data"


@pytest.mark.parametrize("value,unit,severity", [(5.6, "mmol/L", "moderate"), (6.2, "mEq/L", "high"), (6.8, "mmol/L", "critical")])
def test_hyperkalemia_bands(engine, value, unit, severity):
    k = shown(engine, patient(labs=[lab("2823-3", value, unit)]))[0]["NEPHRO-HYPERKALEMIA"]
    assert k.finding == "consistent" and k.severity == severity


def test_dyslipidemia_ldl_in_mmol(engine):
    results = shown(engine, patient(labs=[lab("18262-6", 5.0, "mmol/L", 100)]))[0]   # 193 mg/dL
    assert results["ENDO-DYSLIPIDEMIA"].criteria_met[0].value == "5.0 mmol/L (= 193 mg/dL)"
    assert "ENDO-DYSLIPIDEMIA" not in shown(engine, patient(labs=[lab("18262-6", 160, "mg/dL")]))[0]


def test_lookback_excludes_old_results(engine):
    old = shown(engine, patient(labs=[lab("2823-3", 6.8, "mmol/L", days_ago=45)]))[0]
    assert "NEPHRO-HYPERKALEMIA" not in old   # potassium lookback is 30 days


def test_every_finding_cites_sources_and_is_draft(engine):
    data = patient(labs=[lab("2823-3", 6.2, "mmol/L"), lab("18262-6", 200, "mg/dL")])
    for e in shown(engine, data)[0].values():
        if e.finding:
            assert e.sources and all(c.source for c in e.criteria_met)
            assert e.review_status_label == "Draft - under clinical review."
            assert not any(word in " ".join(e.recommendations).lower() for word in (" stat", " mg ", "administer"))


# --- FHIR fetch ----------------------------------------------------------------

def test_observation_requirements_use_longest_lookback(engine):
    needs = engine.observation_requirements()
    assert needs["labs"]["lookback_days"] == 730
    assert {"4548-4", "33914-3", "2823-3", "18262-6"} <= set(needs["labs"]["codes"])
    assert needs["vitals"] == {"codes": ["8462-4", "8480-6"], "lookback_days": 365}


class _Client(FHIRClient):
    def __init__(self, fail_criteria=False):
        super().__init__("https://fhir.example.test/R4", "c", access_token="t")
        self.fail_criteria = fail_criteria
        self.calls = []

    def get_patient(self, patient_id):
        return {"name": [{"family": "X"}], "birthDate": "1970-01-01", "gender": "female"}

    def get_observations(self, patient_id, category=None, code=None, date_range=None, max_pages=1):
        self.calls.append({"category": category, "code": code, "date": date_range, "max_pages": max_pages})
        if code and self.fail_criteria:
            raise requests.HTTPError("500", response=SimpleNamespace(status_code=500))
        if code and "4548-4" in code:
            return [{"status": "final", "code": {"coding": [{"system": "http://loinc.org", "code": "4548-4"}]},
                     "valueQuantity": {"value": 7.1, "unit": "%"}, "effectiveDateTime": "2026-02-01T08:00:00Z"}]
        if code and "8480-6" in code:
            return [{"status": "final", "code": {"coding": [{"system": "http://loinc.org", "code": "85354-9"}]},
                     "effectiveDateTime": "2026-05-01T08:00:00Z",
                     "component": [
                         {"code": {"coding": [{"system": "http://loinc.org", "code": "8480-6"}]},
                          "valueQuantity": {"value": 150, "unit": "mm[Hg]"}},
                         {"code": {"coding": [{"system": "http://loinc.org", "code": "8462-4"}]},
                          "valueQuantity": {"value": 95, "unit": "mm[Hg]"}}]}]
        return []

    def get_conditions(self, patient_id):
        return []

    def get_medications(self, patient_id):
        return []

    def get_allergies(self, patient_id):
        return []


def test_criteria_fetch_uses_codes_lookback_and_paging(engine):
    client = _Client()
    data = client.get_patient_data("p", observation_requirements=engine.observation_requirements())
    criteria_calls = [c for c in client.calls if c["code"]]
    lab_call = next(c for c in criteria_calls if "4548-4" in c["code"])
    assert "http://loinc.org|4548-4" in lab_call["code"]
    since = datetime.strptime(lab_call["date"][2:], "%Y-%m-%d")
    assert lab_call["date"].startswith("ge") and 725 <= (datetime.now() - since).days <= 731
    assert lab_call["max_pages"] > 1
    assert any(l.code == "4548-4" and l.value == 7.1 for l in data.labs)
    # Blood pressure panel components became separate readings
    assert {(v.code, v.value) for v in data.vitals} == {("8480-6", 150.0), ("8462-4", 95.0)}


def test_failed_criteria_fetch_marks_labs_failed(engine):
    data = _Client(fail_criteria=True).get_patient_data("p", observation_requirements=engine.observation_requirements())
    assert data.retrieval_status["labs"] == "failed"     # worst outcome wins over the summary fetch


def test_get_observations_follows_next_links(monkeypatch):
    client = FHIRClient("https://fhir.example.test/R4", "c", access_token="t")
    first = {"entry": [{"resource": {"id": "1"}}], "link": [{"relation": "next", "url": "https://fhir.example.test/R4/p2"}]}
    second = {"entry": [{"resource": {"id": "2"}}], "link": []}
    monkeypatch.setattr(client, "_query_resource", lambda resource, params: first)

    class Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return second
    monkeypatch.setattr(requests, "get", lambda url, headers=None, timeout=None: Resp())
    assert [o["id"] for o in client.get_observations("p", code="x", max_pages=5)] == ["1", "2"]
    assert [o["id"] for o in client.get_observations("p", code="x")] == ["1"]


# --- Validator -----------------------------------------------------------------

def _problems(criteria):
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        "validate_rules", Path(__file__).resolve().parents[1] / "scripts" / "validate_rules.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.criteria_problems(criteria)


def _valid_criteria(**item_overrides):
    item = {"id": "k", "label": "K", "resource": "lab", "loinc": ["2823-3"], "operator": ">=", "value": 5.5,
            "unit": "mmol/L", "source": "UKKA 2023"}
    item.update(item_overrides)
    return {"finding_label": "x", "source": "UKKA 2023", "items": [item]}


def test_validator_accepts_valid_and_empty_criteria():
    assert _problems(_valid_criteria()) == []
    assert _problems([]) == []


@pytest.mark.parametrize("override,message", [
    ({"operator": "=="}, "unknown operator"),
    ({"source": ""}, "missing 'source'"),
    ({"unit": "mg/dL"}, "unit must be 'mmol/L'"),
    ({"loinc": ["abc"]}, "loinc must be a list"),
    ({"operator": "between", "value": 5}, "needs 'value: [low, high]'"),
    ({"lookback_days": -3}, "lookback_days must be a positive whole number"),
    ({"loinc": ["99999-9"]}, "no unit conversion is defined"),
    ({"applies_to": {"sex": "other"}}, "applies_to.sex"),
])
def test_validator_rejects_bad_criteria(override, message):
    assert any(message in p for p in _problems(_valid_criteria(**override)))


def test_validator_rejects_severity_rule_for_unknown_item():
    criteria = _valid_criteria()
    criteria["severity"] = [{"type": "value", "item": "nope", "op": ">", "value": 6, "level": "high"}]
    assert any("unknown item 'nope'" in p for p in _problems(criteria))


# --- API ------------------------------------------------------------------------

def test_evaluate_patient_api_returns_assessment_fields(monkeypatch):
    from fastapi.testclient import TestClient
    from backend.main import app
    from backend.services import smart_router

    data = patient(labs=[lab("2823-3", 6.2, "mmol/L", days_ago=0)], conditions=[problem("E87.5", text="Hyperkalemia")],
                   status=dict(ALL_RETRIEVED, vitals="failed"))

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def get_patient_data(self, patient_id, observation_requirements=None):
            assert observation_requirements and observation_requirements["labs"]["lookback_days"] == 730
            return data

    monkeypatch.setattr(smart_router, "FHIRClient", FakeClient)
    session = SimpleNamespace(patient_id="p", ehr_vendor="epic", fhir_access_token="t",
                              expires_at=datetime.utcnow() + timedelta(minutes=30))
    app.dependency_overrides[smart_router.get_active_smart_session] = lambda: session
    try:
        body = TestClient(app).post("/smart/evaluate-patient", json={"patient_id": "p"}).json()
    finally:
        app.dependency_overrides.pop(smart_router.get_active_smart_session, None)

    assert "Some conditions could not be assessed: vital signs could not be retrieved." in body["assessment_warnings"]
    k = next(e for e in body["evaluations"] if e["diagnosis_id"] == "NEPHRO-HYPERKALEMIA")
    assert k["known_condition"] is True and k["known_condition_text"] == "Hyperkalemia"
    assert k["finding"] == "consistent" and k["display"] == "when_found"
    assert k["criteria_met"][0]["source"].startswith("UK Kidney Association")
    assert k["review_status_label"] == "Draft - under clinical review."


# --- Acute cards: shown only when a criterion is met ----------------------------

def test_acute_card_shown_when_a_criterion_is_met(engine):
    results, _ = shown(engine, patient(labs=[lab("2345-7", 320, "mg/dL")]))
    assert "ENDO-DKA" in results and results["ENDO-DKA"].finding is None   # D met, K/A not measured
    assert "CARD-ACUTE-CORONARY-SYNDROME" not in results and "ID-SEPSIS" not in results


def test_acute_supporting_finding_alone_does_not_show_a_card(engine):
    tachy = [VitalSign(code="8867-4", display="HR", value=130, unit="/min", effective_date=NOW)]
    assert "CARD-ACUTE-CORONARY-SYNDROME" not in shown(engine, patient(vitals=tachy))[0]


def test_failed_retrieval_warns_for_acute_conditions_too(engine):
    _, warnings = shown(engine, patient(status=dict(ALL_RETRIEVED, labs="failed", vitals="failed")))
    assert "Some conditions could not be assessed: lab results could not be retrieved." in warnings
    assert "Some conditions could not be assessed: vital signs could not be retrieved." in warnings


# --- Sepsis wording ------------------------------------------------------------

def test_sepsis_screen_wording_names_the_positive_screen(engine):
    sirs = [VitalSign(code="8310-5", display="T", value=38.7, unit="Cel", effective_date=NOW),
            VitalSign(code="8867-4", display="HR", value=112, unit="/min", effective_date=NOW)]
    s = shown(engine, patient(vitals=sirs))[0]["ID-SEPSIS"]
    assert s.recommendations[0].startswith(
        "Screen positive (SIRS >= 2); consider sepsis evaluation if infection is suspected, per")
    both = sirs + [VitalSign(code="9279-1", display="RR", value=26, unit="/min", effective_date=NOW),
                   VitalSign(code="8480-6", display="SBP", value=92, unit="mmHg", effective_date=NOW)]
    s = shown(engine, patient(vitals=both))[0]["ID-SEPSIS"]
    assert s.recommendations[0].startswith("Screen positive (qSOFA >= 2 and SIRS >= 2); consider sepsis evaluation")


# --- Results cut off at the page cap ----------------------------------------------

def _paged_client(monkeypatch, total, page=100):
    """FHIRClient whose Observation queries return `total` results, `page` per page."""
    from backend.services import fhir_client as fhir
    client = FHIRClient("https://fhir.example.test/R4", "c", access_token="t")

    def obs(i):
        day = (NOW - timedelta(days=i)).strftime("%Y-%m-%d")
        return {"status": "final", "code": {"coding": [{"system": "http://loinc.org", "code": "2823-3"}]},
                "valueQuantity": {"value": 4.2, "unit": "mmol/L"}, "effectiveDateTime": f"{day}T08:00:00Z"}

    def bundle(offset):
        entries = [{"resource": obs(i)} for i in range(offset, min(offset + page, total))]
        links = [{"relation": "next", "url": f"https://fhir.example.test/R4/next?o={offset + page}"}] \
            if offset + page < total else []
        return {"entry": entries, "link": links}

    class Resp:
        def __init__(self, body):
            self.body = body

        def raise_for_status(self):
            pass

        def json(self):
            return self.body

    monkeypatch.setattr(client, "_query_resource", lambda resource, params: bundle(0))
    monkeypatch.setattr(fhir.requests, "get", lambda url, headers=None, timeout=None: Resp(bundle(int(url.split("o=")[1]))))
    monkeypatch.setattr(client, "get_patient", lambda pid: {"name": [{"family": "X"}], "birthDate": "1970-01-01"})
    for name in ("get_conditions", "get_medications", "get_allergies"):
        monkeypatch.setattr(client, name, lambda pid: [])
    return client


def test_page_cap_adds_visible_cut_off_warning(monkeypatch):
    from backend.services import fhir_client as fhir
    monkeypatch.setattr(fhir, "CRITERIA_MAX_PAGES", 3)
    client = _paged_client(monkeypatch, total=450)
    data = client.get_patient_data("p", observation_requirements={"labs": {"codes": ["2823-3"], "lookback_days": 730}})
    cut = [w for w in data.data_warnings if w.startswith("Lab results cut off")]
    assert len(cut) >= 1
    newest = NOW.strftime("%Y-%m-%d")
    oldest = (NOW - timedelta(days=299)).strftime("%Y-%m-%d")
    criteria_note = next(w for w in cut if "300 results" in w)
    assert f"dated {oldest} to {newest}" in criteria_note
    assert "were not retrieved and were not assessed" in criteria_note
    assert "since" in criteria_note


def test_no_cut_off_warning_when_everything_fits(monkeypatch):
    client = _paged_client(monkeypatch, total=80)
    data = client.get_patient_data("p", observation_requirements={"labs": {"codes": ["2823-3"], "lookback_days": 730}})
    assert not any("cut off" in w for w in data.data_warnings)


def test_cut_off_warning_reaches_the_api(monkeypatch):
    from fastapi.testclient import TestClient
    from backend.main import app
    from backend.services import smart_router

    data = patient(labs=[lab("2823-3", 6.2, "mmol/L")])
    data.truncation_warnings = ["Lab results cut off: the page limit was reached after 1000 results, dated 2025-03-01 to 2026-10-18. Other results since 2024-10-19 were not retrieved and were not assessed."]

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def get_patient_data(self, patient_id, observation_requirements=None):
            return data

    monkeypatch.setattr(smart_router, "FHIRClient", FakeClient)
    session = SimpleNamespace(patient_id="p", ehr_vendor="epic", fhir_access_token="t",
                              expires_at=datetime.utcnow() + timedelta(minutes=30))
    app.dependency_overrides[smart_router.get_active_smart_session] = lambda: session
    try:
        body = TestClient(app).post("/smart/evaluate-patient", json={"patient_id": "p"}).json()
    finally:
        app.dependency_overrides.pop(smart_router.get_active_smart_session, None)
    assert any(w.startswith("Lab results cut off") for w in body["data_warnings"])
