"""
Phase 2 criteria updates:
- Sepsis: qSOFA is no longer the only screen (SSC 2021); qSOFA >= 2 or SIRS >= 2.
- DKA: 2024 ADA/EASD/JBDS/AACE/DTS consensus (D + K + A).
- Hypertension: average readings per occasion (2025 AHA/ACC) instead of counting.
"""
from datetime import datetime, timedelta

import pytest

from backend.services.fhir_client import LabResult, PatientData, VitalSign
from backend.services.smart_diagnostic_engine import SmartDiagnosticEngine

NOW = datetime(2026, 10, 19, 8, 0)
ALL_RETRIEVED = {k: "retrieved" for k in ("labs", "vitals", "conditions", "medications", "allergies")}


def lab(code, value, unit, hours_ago=1):
    return LabResult(code=code, display=code, value=value, unit=unit, effective_date=NOW - timedelta(hours=hours_ago))


def vital(code, value, unit, days_ago=0, hours_ago=1):
    return VitalSign(code=code, display=code, value=value, unit=unit,
                     effective_date=NOW - timedelta(days=days_ago, hours=hours_ago))


def patient(labs=(), vitals=(), conditions=(), status=None):
    return PatientData(patient_id="p", name="T", age=50, gender="male", labs=list(labs), vitals=list(vitals),
                       conditions=list(conditions), medications=[], allergies=[],
                       retrieval_status=dict(status or ALL_RETRIEVED))


@pytest.fixture(scope="module")
def engine():
    return SmartDiagnosticEngine()


def evaluate(engine, tree_id, data):
    return engine.evaluate_tree(tree_id, data, now=NOW)


# --- Sepsis -------------------------------------------------------------------

def test_qsofa_two_still_screens_positive(engine):
    s = evaluate(engine, "ID-SEPSIS", patient(vitals=[vital("9279-1", 24, "/min"), vital("8480-6", 95, "mmHg")]))
    assert s.finding == "consistent" and s.severity == "critical"
    assert "qSOFA >= 2 or SIRS >= 2" in s.recommendations[0]


def test_sirs_screens_positive_when_qsofa_does_not(engine):
    """qSOFA alone would miss this patient (qSOFA 0) - the reason SSC 2021 advises against it."""
    s = evaluate(engine, "ID-SEPSIS", patient(vitals=[vital("8310-5", 38.6, "Cel"), vital("8867-4", 112, "/min")]))
    assert s.finding == "consistent" and s.severity == "high"
    assert {c.criterion for c in s.criteria_met} == {"Temperature > 38.0 or < 36.0 C (SIRS)", "Heart rate > 90/min (SIRS)"}


def test_one_qsofa_and_one_sirs_criterion_is_not_a_positive_screen(engine):
    s = evaluate(engine, "ID-SEPSIS", patient(vitals=[vital("8480-6", 95, "mmHg"), vital("8867-4", 110, "/min")]))
    assert s.finding is None and s.severity == "high"   # qSOFA 1


def test_temperature_in_fahrenheit_is_converted(engine):
    s = evaluate(engine, "ID-SEPSIS", patient(vitals=[vital("8310-5", 101.5, "[degF]"), vital("8867-4", 100, "/min")]))
    assert s.finding == "consistent"   # 38.6 C


def test_lactate_is_supporting_only(engine):
    s = evaluate(engine, "ID-SEPSIS", patient(labs=[lab("2524-7", 3.1, "mmol/L")]))
    assert s.finding is None
    assert s.supporting_findings[0].criterion == "Lactate > 2 mmol/L"


# --- DKA (2024 consensus) -------------------------------------------------------

DKA_FULL = [lab("2345-7", 350, "mg/dL"), lab("53060-9", 4.2, "mmol/L"), lab("2746-5", 7.21, ""), lab("2028-9", 14, "mmol/L")]


def test_dka_requires_d_k_and_a(engine):
    d = evaluate(engine, "ENDO-DKA", patient(labs=DKA_FULL))
    assert d.finding == "consistent" and d.severity == "high"
    assert d.recommendations[0].startswith("Findings consistent with diabetic ketoacidosis (2024 consensus criteria)")


def test_dka_without_ketones_is_not_suggested(engine):
    d = evaluate(engine, "ENDO-DKA", patient(labs=[l for l in DKA_FULL if l.code != "53060-9"]))
    assert d.finding is None
    assert "Serum beta-hydroxybutyrate (ketones)" in d.missing_tests


def test_dka_glucose_threshold_is_200(engine):
    labs = [lab("2345-7", 220, "mg/dL")] + DKA_FULL[1:]
    assert evaluate(engine, "ENDO-DKA", patient(labs=labs)).finding == "consistent"   # was > 250 before


def test_euglycemic_dka_with_known_diabetes(engine):
    labs = [lab("2345-7", 160, "mg/dL")] + DKA_FULL[1:]
    known = [{"code": {"text": "Type 1 diabetes", "coding": [{"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "E10.9"}]}}]
    assert evaluate(engine, "ENDO-DKA", patient(labs=labs)).finding is None
    d = evaluate(engine, "ENDO-DKA", patient(labs=labs, conditions=known))
    assert d.finding == "consistent"
    assert any(c.criterion.startswith("Known diabetes") for c in d.criteria_met)


def test_problem_list_not_retrieved_is_unknown(engine):
    d = evaluate(engine, "ENDO-DKA", patient(labs=DKA_FULL, status=dict(ALL_RETRIEVED, conditions="failed")))
    known = next(c for c in d.criteria_unknown if c.criterion.startswith("Known diabetes"))
    assert known.details == "Problem list could not be retrieved."
    assert d.finding == "consistent"   # glucose still satisfies D


@pytest.mark.parametrize("ph,bicarb,severity", [(7.21, 14, "high"), (6.95, 14, "critical"), (7.25, 8, "critical")])
def test_dka_severe_range(engine, ph, bicarb, severity):
    labs = [lab("2345-7", 400, "mg/dL"), lab("53060-9", 5.0, "mmol/L"), lab("2744-1", ph, ""), lab("2028-9", bicarb, "mEq/L")]
    assert evaluate(engine, "ENDO-DKA", patient(labs=labs)).severity == severity


# --- Hypertension (averaged readings) -------------------------------------------

def bp(systolic, diastolic, days_ago, hours_ago=1):
    return [vital("8480-6", systolic, "mm[Hg]", days_ago, hours_ago), vital("8462-4", diastolic, "mm[Hg]", days_ago, hours_ago)]


def test_average_below_threshold_is_not_hypertension(engine):
    """Counting would flag this (140 and 135 are >= 130 on two days); averaging does not."""
    readings = bp(140, 78, 20, 2) + bp(116, 70, 20, 1) + bp(135, 76, 2, 2) + bp(121, 72, 2, 1)
    h = evaluate(engine, "CARD-HYPERTENSION", patient(vitals=readings))
    assert h.finding is None
    systolic = next(c for c in h.criteria_not_met if c.criterion.startswith("Average systolic"))
    assert systolic.value == "128 mmHg (average of 4 readings on 2 days)"


def test_average_above_threshold_on_two_occasions(engine):
    readings = bp(138, 86, 30) + bp(134, 84, 3)
    h = evaluate(engine, "CARD-HYPERTENSION", patient(vitals=readings))
    assert h.finding == "consistent" and h.severity == "moderate"
    assert "Stage 1" in h.severity_reason


def test_stage_two_by_average(engine):
    h = evaluate(engine, "CARD-HYPERTENSION", patient(vitals=bp(152, 94, 30) + bp(146, 92, 3)))
    assert h.severity == "high" and "Stage 2" in h.severity_reason


def test_single_occasion_is_possible_only(engine):
    h = evaluate(engine, "CARD-HYPERTENSION", patient(vitals=bp(150, 95, 1, 2) + bp(148, 94, 1, 1)))
    assert h.finding == "possible"
    assert "1 of 2 required occasions" in h.criteria_met[0].details


def test_only_the_three_most_recent_occasions_are_averaged(engine):
    old_high = bp(170, 100, 200) + bp(168, 98, 190)
    recent_normal = bp(118, 74, 30) + bp(120, 76, 10) + bp(116, 72, 2)
    h = evaluate(engine, "CARD-HYPERTENSION", patient(vitals=old_high + recent_normal))
    assert h.finding is None


# --- Validator: new criteria shapes ----------------------------------------------

def _problems(criteria):
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        "validate_rules", Path(__file__).resolve().parents[1] / "scripts" / "validate_rules.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.criteria_problems(criteria)


def _criteria(items, **extra):
    return {"finding_label": "x", "source": "s", "items": items, **extra}


GLUCOSE = {"id": "g", "label": "G", "group": "d", "resource": "lab", "loinc": ["2345-7"], "operator": ">=",
           "value": 200, "unit": "mg/dL", "source": "s"}


def test_validator_accepts_problem_list_item_and_group_rules():
    known = {"id": "dm", "label": "Known DM", "group": "d", "resource": "problem_list", "icd10_prefixes": ["E11"], "source": "s"}
    assert _problems(_criteria([GLUCOSE, known], suggest_when={"all_groups": ["d"]})) == []


def test_validator_rejects_problem_list_item_without_codes():
    bad = {"id": "dm", "label": "Known DM", "resource": "problem_list", "source": "s"}
    assert any("icd10_prefixes or snomed" in p for p in _problems(_criteria([GLUCOSE, bad])))


def test_validator_rejects_unknown_group_in_suggest_when():
    problems = _problems(_criteria([GLUCOSE], suggest_when={"any": [{"count_met": 2, "group": "nope"}]}))
    assert any("unknown group 'nope'" in p for p in problems)


def test_validator_rejects_bad_aggregate():
    item = dict(GLUCOSE, aggregate="median", min_days=0)
    problems = _problems(_criteria([item]))
    assert any("aggregate must be 'daily_mean'" in p for p in problems)
    assert any("min_days must be a positive whole number" in p for p in problems)
