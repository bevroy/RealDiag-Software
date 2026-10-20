"""
Synthetic patients for the SMART chart-evaluation equivalence tests.

`python -m backend.tests.smart_engine_cases` regenerates
backend/tests/fixtures/smart_engine_golden.json. The golden file was produced
by the hand-written ACS / sepsis / DKA evaluators *before* they were replaced
by tree criteria; test_criteria_equivalence.py checks the criteria engine
still produces the same results.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from backend.services.fhir_client import CommonLOINC, LabResult, PatientData, VitalSign

GOLDEN_PATH = Path(__file__).resolve().parent / "fixtures" / "smart_engine_golden.json"
BASE = datetime(2026, 10, 18, 8, 0)

TNI, TNT = CommonLOINC.TROPONIN_I, CommonLOINC.TROPONIN_T
HR, RR, SBP, GCS = CommonLOINC.HEART_RATE, CommonLOINC.RESPIRATORY_RATE, CommonLOINC.SYSTOLIC_BP, CommonLOINC.GCS_SCORE
WBC, GLU, CO2 = CommonLOINC.WBC, CommonLOINC.GLUCOSE, CommonLOINC.CO2


def lab(code, value, unit, high=None, ref_unit=None, status="final", hours_ago=0):
    ref = {"high": high} if high is not None else None
    return LabResult(code=code, display=code, value=value, unit=unit, reference_range=ref, status=status,
                     effective_date=BASE - timedelta(hours=hours_ago), reference_unit=ref_unit)


def vital(code, value, unit, hours_ago=0):
    return VitalSign(code=code, display=code, value=value, unit=unit, effective_date=BASE - timedelta(hours=hours_ago))


# name -> (labs, vitals)
CASES = {
    "no_data": ([], []),
    # --- ACS
    "acs_tni_normal_hr_normal": ([lab(TNI, 0.01, "ng/mL", 0.04)], [vital(HR, 88, "beats/min")]),
    "acs_tni_moderate": ([lab(TNI, 0.05, "ng/mL", 0.04)], []),
    "acs_tni_high": ([lab(TNI, 0.2, "ng/mL", 0.04)], []),
    "acs_tni_critical": ([lab(TNI, 0.5, "ng/mL", 0.04)], []),
    "acs_tnt_hs_ng_l": ([lab(TNT, 40, "ng/L", 14)], []),
    "acs_tni_ng_l_not_elevated": ([lab(TNI, 50, "ng/L", 52)], []),
    "acs_value_ng_ml_ref_ng_l": ([lab(TNI, 0.05, "ng/mL", 26, ref_unit="ng/L")], []),
    "acs_no_unit": ([lab(TNI, 0.5, "", 0.04)], []),
    "acs_unknown_unit": ([lab(TNI, 0.5, "mmol/L", 0.04)], []),
    "acs_no_reference_range": ([lab(TNI, 0.5, "ng/mL")], []),
    "acs_unknown_reference_unit": ([lab(TNI, 0.5, "ng/mL", 0.04, ref_unit="furlongs")], []),
    "acs_zero_reference_high": ([lab(TNI, 0.5, "ng/mL", 0.0)], []),
    "acs_preliminary_elevated": ([lab(TNI, 0.5, "ng/mL", 0.04, status="preliminary")], []),
    "acs_tni_normal_tnt_elevated": ([lab(TNI, 0.01, "ng/mL", 0.04), lab(TNT, 40, "ng/L", 14)], []),
    "acs_tachycardia_only": ([], [vital(HR, 130, "beats/min")]),
    "acs_elevated_with_tachycardia": ([lab(TNI, 0.5, "ng/mL", 0.04)], [vital(HR, 130, "beats/min")]),
    "acs_most_recent_result_used": ([lab(TNI, 0.5, "ng/mL", 0.04, hours_ago=10), lab(TNI, 0.02, "ng/mL", 0.04, hours_ago=1)], []),
    # --- Sepsis
    "sepsis_qsofa3_wbc_high": ([lab(WBC, 15, "K/uL")], [vital(RR, 24, "/min"), vital(SBP, 90, "mmHg"), vital(GCS, 13, "{score}")]),
    "sepsis_rr_only": ([], [vital(RR, 24, "/min")]),
    "sepsis_all_normal": ([lab(WBC, 8, "K/uL")], [vital(RR, 18, "/min"), vital(SBP, 120, "mmHg"), vital(GCS, 15, "{score}")]),
    "sepsis_qsofa1_rr_unknown": ([], [vital(SBP, 95, "mmHg"), vital(GCS, 15, "{score}")]),
    "sepsis_wbc_low_only": ([lab(WBC, 3, "K/uL")], []),
    "sepsis_boundaries_qsofa2": ([lab(WBC, 12, "K/uL")], [vital(RR, 22, "/min"), vital(SBP, 100, "mmHg"), vital(GCS, 15, "{score}")]),
    "sepsis_most_recent_vital_used": ([], [vital(RR, 30, "/min", hours_ago=5), vital(RR, 16, "/min", hours_ago=1)]),
    # --- DKA
    "dka_600_mg_dl_co2_low": ([lab(GLU, 600, "mg/dL"), lab(CO2, 12, "mEq/L")], []),
    "dka_30_mmol_co2_low": ([lab(GLU, 30, "mmol/L"), lab(CO2, 12, "mmol/L")], []),
    "dka_20_mmol_only": ([lab(GLU, 20, "mmol/L")], []),
    "dka_10_mmol_only": ([lab(GLU, 10, "mmol/L")], []),
    "dka_200_mg_dl_co2_normal": ([lab(GLU, 200, "mg/dL"), lab(CO2, 20, "mEq/L")], []),
    "dka_no_glucose_unit": ([lab(GLU, 600, ""), lab(CO2, 12, "mEq/L")], []),
    "dka_unknown_glucose_unit": ([lab(GLU, 600, "g/L"), lab(CO2, 12, "mEq/L")], []),
    "dka_co2_low_only": ([lab(CO2, 12, "mEq/L")], []),
    "dka_glucose_250_boundary": ([lab(GLU, 250, "mg/dL")], []),
    "dka_preliminary_glucose": ([lab(GLU, 300, "mg/dL", status="preliminary"), lab(CO2, 15, "mEq/L")], []),
    # --- Everything abnormal at once
    "all_abnormal": (
        [lab(TNI, 0.5, "ng/mL", 0.04), lab(WBC, 20, "K/uL"), lab(GLU, 600, "mg/dL"), lab(CO2, 10, "mEq/L")],
        [vital(RR, 30, "/min"), vital(SBP, 80, "mmHg"), vital(GCS, 12, "{score}"), vital(HR, 130, "beats/min")],
    ),
}


def patient(name: str) -> PatientData:
    labs, vitals = CASES[name]
    return PatientData(
        patient_id=name, name="Test Patient", age=60, gender="female",
        labs=list(labs), vitals=list(vitals), conditions=[], medications=[], allergies=[],
        retrieval_status={k: "retrieved" for k in ("labs", "vitals", "conditions", "medications", "allergies")},
    )


def _criterion(c) -> dict:
    return {"criterion": c.criterion, "status": c.status.value, "value": c.value,
            "expected": c.expected, "details": c.details}


def serialize(evaluation) -> dict:
    """Fields that must not change when evaluators move into tree criteria."""
    return {
        "probability": round(evaluation.probability, 6),
        "severity": evaluation.severity,
        "severity_reason": evaluation.severity_reason,
        "evaluation_status": evaluation.evaluation_status,
        "status_reason": evaluation.status_reason,
        "missing_tests": list(evaluation.missing_tests),
        "criteria_met": [_criterion(c) for c in evaluation.criteria_met],
        "criteria_not_met": [_criterion(c) for c in evaluation.criteria_not_met],
        "criteria_unknown": [_criterion(c) for c in evaluation.criteria_unknown],
        "supporting_findings": [_criterion(c) for c in evaluation.supporting_findings],
    }


# Legacy evaluator ids -> tree ids that now hold their criteria
LEGACY_TO_TREE = {"CARD-ACS": "CARD-ACUTE-CORONARY-SYNDROME", "ID-SEPSIS": "ID-SEPSIS", "ENDO-DKA": "ENDO-DKA"}


def generate_golden() -> dict:
    """Run the legacy hand-written evaluators (pre-criteria engine) on every case."""
    from backend.services.smart_diagnostic_engine import SmartDiagnosticEngine
    engine = SmartDiagnosticEngine()
    golden = {}
    for name in CASES:
        data = patient(name)
        raw = {
            "CARD-ACS": serialize(engine._evaluate_acs(data)),
            "ID-SEPSIS": serialize(engine._evaluate_sepsis(data)),
            "ENDO-DKA": serialize(engine._evaluate_dka(data)),
        }
        shown = {e.diagnosis_id: serialize(e) for e in engine.evaluate_patient(data)}
        golden[name] = {"raw": raw, "shown": shown}
    return golden


if __name__ == "__main__":
    GOLDEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    GOLDEN_PATH.write_text(json.dumps(generate_golden(), indent=1, sort_keys=True) + "\n")
    print(f"wrote {GOLDEN_PATH}")
