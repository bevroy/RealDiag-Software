"""
Phase 3: possible missed items (abnormal results without a diagnosis,
diagnoses without support, overdue USPSTF screenings), including partial
data failures and wording.
"""
import asyncio
import re
from datetime import datetime, timedelta

import pytest

from backend.services import missed_items as mi
from backend.services.fhir_client import LabResult, PatientData, VitalSign
from backend.services.patient_history_service import ComprehensivePatientHistory, ImagingStudy, Procedure
from backend.services.smart_diagnostic_engine import SmartDiagnosticEngine

NOW = datetime(2026, 10, 19, 8, 0)
FHIR_RESOURCES = ("labs", "vitals", "conditions", "medications", "allergies")
OK = {**{k: "retrieved" for k in FHIR_RESOURCES}, "procedures": "retrieved", "imaging_studies": "retrieved",
      "smoking_status": "retrieved"}
ICD = "http://hl7.org/fhir/sid/icd-10-cm"


def lab(code, value, unit, days_ago=10, display=None):
    return LabResult(code=code, display=display or code, value=value, unit=unit,
                     effective_date=NOW - timedelta(days=days_ago))


def vital(code, value, unit, days_ago=10):
    return VitalSign(code=code, display=code, value=value, unit=unit, effective_date=NOW - timedelta(days=days_ago))


def condition(text, code):
    return {"code": {"text": text, "coding": [{"system": ICD, "code": code}]}}


def med(name):
    return {"medicationCodeableConcept": {"text": name}}


def patient(age=50, sex="male", labs=(), vitals=(), conditions=(), meds=()):
    return PatientData(patient_id="p", name="T", age=age, gender=sex, labs=list(labs), vitals=list(vitals),
                       conditions=list(conditions), medications=list(meds), allergies=[],
                       retrieval_status={k: "retrieved" for k in FHIR_RESOURCES})


def history(procedures=(), imaging=()):
    return ComprehensivePatientHistory(patient_id="p", patient_name="T", procedures=list(procedures),
                                       imaging_studies=list(imaging))


@pytest.fixture(scope="module")
def engine():
    return SmartDiagnosticEngine()


def run(engine, data, hist=None, smoking=None, status=None):
    return mi.possible_missed_items(engine, data, hist or history(), smoking, dict(OK, **(status or {})), now=NOW)


def check(result, kind):
    return next(c for c in result["checks"] if c["type"] == kind)


A1C_HIGH = [lab("4548-4", 7.2, "%", 30), lab("4548-4", 7.0, "%", 200)]


# --- Check 1: abnormal results without a diagnosis -----------------------------------

def test_abnormal_results_not_on_problem_list(engine):
    c = check(run(engine, patient(labs=A1C_HIGH)), "abnormal_without_diagnosis")
    item = next(i for i in c["items"] if i["tree_id"] == "ENDO-DIABETES")
    assert item["summary"].startswith("Results may be consistent with diabetes")
    assert "not on the problem list. Consider evaluation per ADA" in item["summary"]
    assert any("7.2" in e for e in item["details"]["evidence"])
    assert item["review_status_label"] == "Draft - under clinical review."


def test_condition_on_problem_list_is_not_listed(engine):
    data = patient(labs=A1C_HIGH, conditions=[condition("Type 2 diabetes", "E11.9")], meds=[med("metformin 500 mg")])
    c = check(run(engine, data), "abnormal_without_diagnosis")
    assert not [i for i in c["items"] if i["tree_id"] == "ENDO-DIABETES"]


def test_diabetes_on_problem_list_suppresses_prediabetes(engine):
    # HbA1c 6.0% is in the prediabetes range; with type 2 diabetes on the problem list,
    # prediabetes is not "missing" from it (ENDO-PREDIABETES criteria.suppressed_by).
    data = patient(labs=[lab("4548-4", 6.0, "%", 30)], conditions=[condition("Type 2 diabetes", "E11.9")],
                   meds=[med("metformin 500 mg")])
    c = check(run(engine, data), "abnormal_without_diagnosis")
    assert not [i for i in c["items"] + c["single_results"]["items"] if i["tree_id"] == "ENDO-PREDIABETES"]


def test_prediabetes_still_flagged_without_diabetes(engine):
    c = check(run(engine, patient(labs=[lab("4548-4", 6.0, "%", 30)])), "abnormal_without_diagnosis")
    assert [i for i in c["items"] if i["tree_id"] == "ENDO-PREDIABETES"]


def test_suppressing_condition_uses_the_other_trees_codes(engine):
    from backend.services.smart_diagnostic_engine import suppressing_condition
    criteria = engine.trees["ENDO-PREDIABETES"]["criteria"]
    assert criteria["suppressed_by"] == ["ENDO-DIABETES"]
    assert suppressing_condition(engine.trees, criteria, [condition("Type 1 diabetes", "E10.9")]) == "Type 1 diabetes"
    assert suppressing_condition(engine.trees, criteria, [condition("Hypertension", "I10")]) is None
    assert suppressing_condition(engine.trees, {}, [condition("Type 1 diabetes", "E10.9")]) is None


def test_validator_checks_suppressed_by():
    import importlib.util
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / "scripts" / "validate_rules.py"
    spec = importlib.util.spec_from_file_location("validate_rules", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    known = {"known_condition": {"icd10_prefixes": ["E11"]}}
    trees = {"A": {"criteria": {"suppressed_by": ["B", "C", "D", "A"]}},
             "B": {"criteria": known}, "C": {"criteria": []}}
    assert module.suppressed_by_problems(trees) == [
        ("A", "criteria.suppressed_by: C has no criteria.known_condition codes"),
        ("A", "criteria.suppressed_by: unknown tree 'D'"),
        ("A", "criteria.suppressed_by: a tree cannot suppress itself")]
    assert "suppressed_by must be a non-empty list of tree ids" in module.criteria_problems(
        {"finding_label": "x", "source": "y", "suppressed_by": "B", "items": []})


def test_single_result_goes_to_the_collapsed_line(engine):
    c = check(run(engine, patient(labs=[lab("4548-4", 7.0, "%", 30)])), "abnormal_without_diagnosis")
    assert not [i for i in c["items"] if i["tree_id"] == "ENDO-DIABETES"]
    single = c["single_results"]
    assert single["title"] == "Single results that may need repeating"
    item = next(i for i in single["items"] if i["tree_id"] == "ENDO-DIABETES")
    assert item["summary"].startswith("HbA1c >= 6.5%: 7.0 % on 2026-09-19: a single result above the diabetes")
    assert "consider repeating per ADA Standards of Care" in item["summary"]
    assert item["source"].startswith("ADA") and item["review_status_label"] == "Draft - under clinical review."


def test_single_bp_reading_is_not_in_the_main_list(engine):
    data = patient(vitals=[vital("8480-6", 132, "mmHg"), vital("8462-4", 78, "mmHg")])
    c = check(run(engine, data), "abnormal_without_diagnosis")
    assert not [i for i in c["items"] if i["tree_id"] == "CARD-HYPERTENSION"]
    assert [i for i in c["single_results"]["items"] if i["tree_id"] == "CARD-HYPERTENSION"]


def test_acute_criteria_are_not_missed_items(engine):
    data = patient(labs=[LabResult(code="10839-9", display="Troponin I", value=0.5, unit="ng/mL",
                                   reference_range={"high": 0.04}, effective_date=NOW - timedelta(hours=1))])
    c = check(run(engine, data), "abnormal_without_diagnosis")
    assert not [i for i in c["items"] if i["tree_id"] == "CARD-ACUTE-CORONARY-SYNDROME"]


def test_problem_list_failure_skips_check_1(engine):
    c = check(run(engine, patient(labs=A1C_HIGH), status={"conditions": "failed"}), "abnormal_without_diagnosis")
    assert c["items"] == []
    assert c["not_checked"] == ["Conditions could not be retrieved; abnormal results could not be compared with it."]


# --- Check 2: diagnoses without support -----------------------------------------------

HYPOTHYROID = condition("Hypothyroidism", "E03.9")


def test_problem_list_condition_without_results_or_medication(engine):
    c = check(run(engine, patient(conditions=[HYPOTHYROID], meds=[med("atorvastatin 20 mg")])),
              "diagnosis_without_support")
    item = next(i for i in c["items"] if i["tree_id"] == "ENDO-HYPOTHYROIDISM")
    assert item["summary"].startswith("Hypothyroidism is on the problem list, with no supporting result")
    assert item["summary"].endswith("Consider reviewing.")
    evidence = item["details"]["evidence"]
    assert evidence[0] == "Problem list: Hypothyroidism"
    assert evidence[1].startswith("No relevant results in the")
    assert evidence[2] == "Medication list: atorvastatin 20 mg"
    assert "levothyroxine" in evidence[3]


def test_normal_results_are_shown_not_resolved(engine):
    tsh = LabResult(code="3016-3", display="TSH", value=2.1, unit="mIU/L", reference_range={"low": 0.4, "high": 4.5},
                    effective_date=NOW - timedelta(days=40))
    item = next(i for i in check(run(engine, patient(conditions=[HYPOTHYROID], labs=[tsh])),
                                 "diagnosis_without_support")["items"] if i["tree_id"] == "ENDO-HYPOTHYROIDISM")
    assert item["details"]["evidence"][1].startswith("Results found, not meeting criteria:")
    assert "2.1" in item["details"]["evidence"][1]


def test_unreadable_results_are_shown_too(engine):
    data = patient(conditions=[HYPOTHYROID], labs=[lab("3016-3", 2.1, "mIU/L", 40)])   # no reference range
    item = next(i for i in check(run(engine, data), "diagnosis_without_support")["items"]
                if i["tree_id"] == "ENDO-HYPOTHYROIDISM")
    assert item["details"]["evidence"][1].startswith("Results found that could not be compared:")


@pytest.mark.parametrize("meds,conditions,tree", [
    ([med("Levothyroxine 75 mcg tablet")], [HYPOTHYROID], "ENDO-HYPOTHYROIDISM"),
    ([med("lisinopril 10 mg")], [condition("Essential hypertension", "I10")], "CARD-HYPERTENSION"),
    ([med("Rosuvastatin 10 mg")], [condition("Hyperlipidemia", "E78.5")], "ENDO-DYSLIPIDEMIA"),
])
def test_related_medication_counts_as_support(engine, meds, conditions, tree):
    items = check(run(engine, patient(conditions=conditions, meds=meds)), "diagnosis_without_support")["items"]
    assert not [i for i in items if i["tree_id"] == tree]


def test_supporting_result_counts_as_support(engine):
    data = patient(conditions=[condition("Type 2 diabetes", "E11.9")], labs=A1C_HIGH)
    items = check(run(engine, data), "diagnosis_without_support")["items"]
    assert not [i for i in items if i["tree_id"] == "ENDO-DIABETES"]


def test_medication_failure_skips_check_2(engine):
    c = check(run(engine, patient(conditions=[HYPOTHYROID]), status={"medications": "failed"}),
              "diagnosis_without_support")
    assert c["items"] == [] and "Medications could not be retrieved" in c["not_checked"][0]


def test_lab_failure_lists_condition_as_not_checked(engine):
    c = check(run(engine, patient(conditions=[HYPOTHYROID]), status={"labs": "failed"}), "diagnosis_without_support")
    assert c["items"] == []
    assert c["not_checked"] == ["Hypothyroidism: Lab results could not be retrieved; supporting results could not be checked."]


def test_medication_patterns():
    meds = [med("Lisinopril 10 mg"), med("Metoprolol tartrate"), med("Aspirin")]
    assert mi.matching_medications(meds, ["*pril", "*olol"]) == ["Lisinopril 10 mg", "Metoprolol tartrate"]
    assert mi.matching_medications([med("Prilosec")], ["*pril"]) == []
    assert mi.medication_names([med("A"), {"medicationReference": {"display": "B"}},
                                {"medicationCodeableConcept": {"coding": [{"display": "C"}]}}]) == ["A", "B", "C"]


# --- Check 4: medications without a matching diagnosis -----------------------------------

RXNORM = "http://www.nlm.nih.gov/research/umls/rxnorm"


def meds_check(engine, data, status=None):
    return check(run(engine, data, status=status), "medication_without_diagnosis")


def test_statin_without_a_lipid_diagnosis_is_listed(engine):
    c = meds_check(engine, patient(meds=[med("Atorvastatin 40 mg")]))
    item = next(i for i in c["items"] if i["name"] == "Atorvastatin 40 mg")
    assert item["summary"].startswith("Atorvastatin 40 mg is on the medication list, but no condition RealDiag links")
    assert "It may be prescribed for another condition" in item["summary"]
    assert item["tree_ids"] == ["ENDO-DYSLIPIDEMIA"]
    assert "Matched as: atorvastatin (name)" in item["details"]["evidence"]
    assert item["review_status_label"] == "Draft - under clinical review."


def test_medication_with_a_linked_diagnosis_is_not_listed(engine):
    data = patient(meds=[med("Carvedilol 12.5 mg"), med("Lisinopril 10 mg"), med("Metformin 500 mg")],
                   conditions=[condition("Hypertension", "I10"), condition("Prediabetes", "R73.03")])
    assert meds_check(engine, data)["items"] == []


def test_carvedilol_without_hypertension_is_listed(engine):
    # carvedilol was missed by the old "*olol" name pattern
    c = meds_check(engine, patient(meds=[med("Carvedilol 12.5 mg")]))
    assert [i["tree_ids"] for i in c["items"]] == [["CARD-HYPERTENSION"]]


def test_one_linked_condition_is_enough(engine):
    # lisinopril is linked to hypertension and chronic kidney disease
    data = patient(meds=[med("Lisinopril 10 mg")], conditions=[condition("CKD stage 3", "N18.30")])
    assert meds_check(engine, data)["items"] == []


def test_medication_matched_by_rxnorm_code_only(engine):
    rx = {"medicationCodeableConcept": {"coding": [{"system": RXNORM, "code": "860975", "display": None}]}}
    c = meds_check(engine, patient(meds=[rx]))
    assert [i["tree_ids"] for i in c["items"]] == [["ENDO-DIABETES", "ENDO-PREDIABETES"]]


def test_unlinked_medications_are_not_checked_not_flagged(engine):
    c = meds_check(engine, patient(meds=[med("Aspirin 81 mg"), med("Nystatin suspension")]))
    assert c["items"] == []
    assert c["not_checked"] == ["2 medication(s) RealDiag does not link to any condition: Aspirin 81 mg, Nystatin suspension."]


def test_unretrieved_medications_or_conditions_skip_the_check(engine):
    c = meds_check(engine, patient(meds=[med("Atorvastatin 40 mg")]), status={"conditions": "failed"})
    assert c["items"] == [] and "could not be retrieved" in c["not_checked"][0]


# --- Check 3: screenings that may be due -----------------------------------------------

def screenings(engine, data, hist=None, smoking=None, status=None):
    return {i["rule_id"]: i for i in check(run(engine, data, hist, smoking, status), "overdue_screening")["items"]}


@pytest.mark.parametrize("age,expected_grade", [(44, None), (45, "B"), (49, "B"), (50, "A"), (75, "A"), (76, None)])
def test_colorectal_age_bands(engine, age, expected_grade):
    items = screenings(engine, patient(age=age))
    if expected_grade is None:
        assert "colorectal-cancer" not in items
    else:
        assert f"(Grade {expected_grade})" in items["colorectal-cancer"]["summary"]


@pytest.mark.parametrize("evidence", [
    {"procedures": [Procedure(date=(NOW - timedelta(days=9 * 365)).strftime("%Y-%m-%d"), procedure_name="Colonoscopy")]},
    {"labs": [lab("29771-3", 0, "", 200)]},
    {"imaging": [ImagingStudy(date=(NOW - timedelta(days=3 * 365)).strftime("%Y-%m-%d"), modality="CT",
                              body_site="Colon", impression="CT colonography: no polyps")]},
])
def test_colorectal_evidence_within_window(engine, evidence):
    data = patient(age=60, labs=evidence.get("labs", []))
    hist = history(procedures=evidence.get("procedures", []), imaging=evidence.get("imaging", []))
    assert "colorectal-cancer" not in screenings(engine, data, hist)


def test_colonoscopy_outside_window_is_not_evidence(engine):
    old = Procedure(date=(NOW - timedelta(days=11 * 365)).strftime("%Y-%m-%d"), procedure_name="Colonoscopy")
    assert "colorectal-cancer" in screenings(engine, patient(age=60), history(procedures=[old]))


def test_breast_screening(engine):
    recent = ImagingStudy(date=(NOW - timedelta(days=400)).strftime("%Y-%m-%d"), modality="MG", body_site="Breast",
                          impression="Screening mammogram")
    old = ImagingStudy(date=(NOW - timedelta(days=3 * 365)).strftime("%Y-%m-%d"), modality="MG", body_site="Breast",
                       impression="Screening mammogram")
    assert "breast-cancer" not in screenings(engine, patient(age=55, sex="female"), history(imaging=[recent]))
    assert "breast-cancer" in screenings(engine, patient(age=55, sex="female"), history(imaging=[old]))
    assert "breast-cancer" not in screenings(engine, patient(age=55, sex="male"))


def test_cervical_screening_hysterectomy_and_hpv_age(engine):
    hyst = Procedure(date="2015-03-01", procedure_name="Total abdominal hysterectomy")
    assert "cervical-cancer" not in screenings(engine, patient(age=40, sex="female"), history(procedures=[hyst]))
    hpv = [lab("21440-3", 0, "", 4 * 365)]
    assert "cervical-cancer" not in screenings(engine, patient(age=40, sex="female", labs=hpv))
    assert "cervical-cancer" in screenings(engine, patient(age=25, sex="female", labs=hpv))   # HPV option is 30+


def test_cervical_procedures_failure_adds_caveat(engine):
    item = screenings(engine, patient(age=40, sex="female"), status={"procedures": "failed"})["cervical-cancer"]
    assert "Procedures not retrieved; hysterectomy was not checked." in item["details"]["caveats"]


def test_hypertension_screening(engine):
    assert "hypertension" in screenings(engine, patient(age=45))
    assert "hypertension" not in screenings(engine, patient(age=45, vitals=[vital("8480-6", 128, "mmHg", 100)]))
    assert "hypertension" not in screenings(engine, patient(age=45, conditions=[condition("HTN", "I10")]))
    young = screenings(engine, patient(age=30))["hypertension"]
    assert "Only the last 1 year of vital signs were retrieved." in young["details"]["caveats"]


def test_diabetes_screening_needs_bmi(engine):
    no_bmi = screenings(engine, patient(age=50))["prediabetes-diabetes"]
    assert no_bmi["summary"].startswith("Prediabetes and type 2 diabetes screening may apply")
    assert no_bmi["missing_data"] == ["BMI"]
    assert "prediabetes-diabetes" not in screenings(engine, patient(age=50, vitals=[vital("39156-5", 22, "kg/m2")]))
    due = screenings(engine, patient(age=50, vitals=[vital("39156-5", 29, "kg/m2")]))
    assert due["prediabetes-diabetes"]["summary"].startswith("Prediabetes and type 2 diabetes screening may be due")
    done = patient(age=50, vitals=[vital("39156-5", 29, "kg/m2")], labs=[lab("4548-4", 5.4, "%", 2 * 365)])
    assert "prediabetes-diabetes" not in screenings(engine, done)


def test_once_only_screenings_note_the_retrieved_window(engine):
    item = screenings(engine, patient(age=40))["hepatitis-c"]
    assert "(ever)" in item["summary"]
    assert "Only the last 10 years of lab results were retrieved." in item["details"]["caveats"]
    assert "hiv" not in screenings(engine, patient(age=40, labs=[lab("75622-1", 0, "", 9 * 365)]))


def test_aaa_uses_smoking_status(engine):
    man = patient(age=70)
    assert "abdominal-aortic-aneurysm" not in screenings(engine, man, smoking={"status": "never"})
    due = screenings(engine, man, smoking={"status": "former", "text": "Former smoker", "date": "2020-01-01"})
    assert due["abdominal-aortic-aneurysm"]["summary"].startswith("Abdominal aortic aneurysm screening may be due")
    assert due["abdominal-aortic-aneurysm"]["details"]["caveats"][0] == "Smoking status: Former smoker (2020-01-01)."
    missing = screenings(engine, man, smoking=None)["abdominal-aortic-aneurysm"]
    assert "no smoking status is recorded" in missing["summary"]
    assert missing["summary"].endswith("Consider whether it applies, per USPSTF. Abdominal Aortic Aneurysm: "
                                       "Screening. Final Recommendation Statement, December 2019 (Grade B).")
    failed = screenings(engine, man, smoking=None, status={"smoking_status": "failed"})["abdominal-aortic-aneurysm"]
    assert "smoking status could not be retrieved" in failed["summary"]
    assert "abdominal-aortic-aneurysm" not in screenings(engine, patient(age=70, sex="female"), smoking={"status": "former"})


def test_lung_screening_states_unavailable_pack_years(engine):
    item = screenings(engine, patient(age=60), smoking={"status": "current"})["lung-cancer"]
    assert item["summary"].startswith("Lung cancer screening may be due if eligible")
    assert "Eligibility also depends on pack-years and quit date, which RealDiag cannot see." in item["summary"]
    assert "pack-years (20 pack-year history required)" in item["missing_data"]
    assert "lung-cancer" not in screenings(engine, patient(age=60), smoking={"status": "never"})


def test_osteoporosis_screening(engine):
    dxa = ImagingStudy(date="2020-05-01", modality="DX", body_site="Hip", impression="DXA bone density")
    assert "osteoporosis" in screenings(engine, patient(age=66, sex="female"))
    assert "osteoporosis" not in screenings(engine, patient(age=66, sex="female"), history(imaging=[dxa]))


def test_partial_failures_in_screening(engine):
    # Labs failed, procedures retrieved: still checked, with a caveat
    item = screenings(engine, patient(age=60), status={"labs": "failed"})["colorectal-cancer"]
    assert "Lab results could not be retrieved; it was not checked." in item["details"]["caveats"]
    # Every evidence source failed: not checked rather than "may be due"
    result = run(engine, patient(age=60), status={"labs": "failed", "procedures": "failed", "imaging_studies": "failed"})
    c = check(result, "overdue_screening")
    assert "colorectal-cancer" not in {i["rule_id"] for i in c["items"]}
    assert any(t.startswith("Colorectal cancer screening:") for t in c["not_checked"])


def test_unknown_age_or_sex(engine):
    c = check(run(engine, patient(age=None)), "overdue_screening")
    assert c["items"] == [] and c["not_checked"] == ["Age is unknown; screenings were not checked."]
    c = check(run(engine, patient(age=55, sex="unknown")), "overdue_screening")
    assert "Breast cancer screening: sex is not recorded." in c["not_checked"]


# --- Wording, sources, review status -----------------------------------------------------

def test_wording_never_states_a_miss(engine):
    data = patient(age=67, labs=A1C_HIGH, conditions=[HYPOTHYROID])
    result = run(engine, data, smoking={"status": "current"})
    items = [i for c in result["checks"] for i in c["items"]]
    assert len(items) >= 5
    for item in items:
        assert not re.search(r"\bmissed\b|\bwas missed\b|\boverdue\b", item["summary"], re.IGNORECASE)
        assert re.search(r"\bmay\b|Consider", item["summary"])
        assert "Consider" in item["summary"]
        assert item["source"] and item["review_status_label"] == "Draft - under clinical review."
        assert item["details"]["window"] and item["details"]["caveats"]
    assert "none is a finding that something was missed" in result["notice"]


def test_no_ai_in_missed_items(monkeypatch, engine):
    from backend.services import symptom_search
    for name in ("ENABLE_AI_GENERATION", "ENABLE_AI_ENRICHMENT"):
        monkeypatch.setenv(name, "true")

    async def forbidden(*args, **kwargs):
        raise AssertionError("AI called")
    monkeypatch.setattr(symptom_search, "query_ai_for_diagnoses", forbidden)
    assert run(engine, patient(age=67, labs=A1C_HIGH))["item_count"] > 0
    source = open(mi.__file__, encoding="utf-8").read()
    assert "anthropic" not in source.lower() and "openai" not in source.lower()


# --- Screening rules file ----------------------------------------------------------------

def test_rules_file_is_valid_and_all_draft():
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        "validate_rules", Path(__file__).resolve().parents[1] / "scripts" / "validate_rules.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    import yaml
    data = yaml.safe_load(mi.SCREENING_RULES_PATH.read_text())
    assert module.screening_rule_problems(data) == []
    assert {r["status"] for r in data["rules"]} == {"draft"}
    assert len(data["rules"]) == 10


def test_screening_requirements_fetch_long_lookback():
    req = mi.screening_requirements()
    assert req["labs:screening"]["lookback_days"] == 3650 and "29771-3" in req["labs:screening"]["codes"]
    assert req["vitals:screening"] == {"codes": ["39156-5"], "lookback_days": 365}


# --- In the encounter assessment ------------------------------------------------------------

def test_encounter_assessment_includes_missed_items_and_smoking_status(engine):
    from backend.services import encounter_assessment as ea
    from backend.services.smart_router import _diagnosis_response, summary_from_patient_data
    from backend.tests.test_encounter_page_assessment import FakeFHIR, FakeHistory

    data = patient(age=70, labs=A1C_HIGH)
    result = asyncio.run(ea.assess_encounter("p", None, FakeFHIR(data, smoking_error=True), FakeHistory(), engine,
                                             criteria_response=_diagnosis_response,
                                             summary_response=summary_from_patient_data, now=NOW))
    missed = result["missed_items"]
    assert [c["type"] for c in missed["checks"]] == ["abnormal_without_diagnosis", "diagnosis_without_support",
                                                     "overdue_screening", "medication_without_diagnosis"]
    assert result["summary"]["data_status"]["smoking_status"] == "failed"
    assert "Smoking status could not be retrieved; do not assume none." in [i["text"] for i in result["not_assessed"]]
    aaa = next(i for i in check(missed, "overdue_screening")["items"] if i["rule_id"] == "abdominal-aortic-aneurysm")
    assert "smoking status could not be retrieved" in aaa["summary"]
