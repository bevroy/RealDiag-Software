"""
Prediabetes criteria ranges end exactly where the diabetes thresholds start:
HbA1c [5.7, 6.5) % and fasting plasma glucose [100, 126) mg/dL
(operator at_least_below: low <= value < high). Before, the inclusive
5.7-6.4% and 100-125 mg/dL left 6.4-6.5% and 125-126 mg/dL in neither tree.
"""
import importlib.util
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from backend.services.fhir_client import LabResult, PatientData
from backend.services.smart_diagnostic_engine import SmartDiagnosticEngine

NOW = datetime(2026, 10, 30, 8, 0)
ALL_RETRIEVED = {k: "retrieved" for k in ("labs", "vitals", "conditions", "medications", "allergies")}
HBA1C, FPG = "4548-4", "1558-6"


def patient(code, value, unit):
    lab = LabResult(code=code, display=code, value=value, unit=unit, effective_date=NOW - timedelta(days=10))
    return PatientData(patient_id="p", name="T", age=50, gender="male", labs=[lab], vitals=[], conditions=[],
                       medications=[], allergies=[], retrieval_status=dict(ALL_RETRIEVED))


@pytest.fixture(scope="module")
def engine():
    return SmartDiagnosticEngine()


def prediabetes_met(engine, code, value, unit):
    evaluation = engine.evaluate_tree("ENDO-PREDIABETES", patient(code, value, unit), now=NOW)
    return bool(evaluation.criteria_met)


def diabetes_met(engine, code, value, unit):
    evaluation = engine.evaluate_tree("ENDO-DIABETES", patient(code, value, unit), now=NOW)
    return bool(evaluation.criteria_met)


@pytest.mark.parametrize("value, prediabetes, diabetes", [
    (5.6, False, False),
    (5.7, True, False),
    (6.4, True, False),
    (6.45, True, False),   # was in neither tree
    (6.49, True, False),   # was in neither tree
    (6.5, False, True),
    (7.0, False, True),
])
def test_hba1c_ranges_meet_without_gap_or_overlap(engine, value, prediabetes, diabetes):
    assert prediabetes_met(engine, HBA1C, value, "%") is prediabetes
    assert diabetes_met(engine, HBA1C, value, "%") is diabetes


@pytest.mark.parametrize("value, prediabetes, diabetes", [
    (99, False, False),
    (100, True, False),
    (125, True, False),
    (125.5, True, False),  # was in neither tree
    (126, False, True),
])
def test_fasting_glucose_ranges_meet_without_gap_or_overlap(engine, value, prediabetes, diabetes):
    assert prediabetes_met(engine, FPG, value, "mg/dL") is prediabetes
    assert diabetes_met(engine, FPG, value, "mg/dL") is diabetes


def test_upper_bounds_equal_the_diabetes_thresholds(engine):
    pre = {i["id"]: i for i in engine.trees["ENDO-PREDIABETES"]["criteria"]["items"]}
    dm = engine.trees["ENDO-DIABETES"]["criteria"]["items"]
    dm_threshold = {tuple(i["loinc"]): i["value"] for i in dm if i["operator"] == ">="}
    assert pre["hba1c"]["operator"] == pre["fasting_glucose"]["operator"] == "at_least_below"
    assert pre["hba1c"]["value"][1] == dm_threshold[tuple(pre["hba1c"]["loinc"])]
    assert pre["fasting_glucose"]["value"][1] == dm_threshold[tuple(pre["fasting_glucose"]["loinc"])]


def _validator():
    path = Path(__file__).resolve().parents[1] / "scripts" / "validate_rules.py"
    spec = importlib.util.spec_from_file_location("validate_rules", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_validator_accepts_at_least_below_and_checks_its_value():
    module = _validator()
    base = {"finding_label": "x", "source": "y"}
    item = {"id": "a", "label": "A", "resource": "lab", "loinc": ["4548-4"], "unit": "%",
            "expected": "e", "missing_test": "m", "source": "s"}
    ok = module.criteria_problems({**base, "items": [{**item, "operator": "at_least_below", "value": [5.7, 6.5]}]})
    assert not [p for p in ok if "operator" in p]
    bad = module.criteria_problems({**base, "items": [{**item, "operator": "at_least_below", "value": [6.5, 5.7]}]})
    assert any("operator at_least_below needs 'value: [low, high]'" in p for p in bad)
