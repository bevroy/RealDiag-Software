"""
Smart Diagnostic Engine with EHR Integration

Enhanced diagnostic engine that evaluates clinical rules against actual patient data
from FHIR/EHR systems. Provides real-time clinical decision support with automated
criteria matching.

Usage:
    from services.fhir_client import FHIRClient, PatientData
    from services.smart_diagnostic_engine import SmartDiagnosticEngine
    
    engine = SmartDiagnosticEngine()
    patient_data = fhir_client.get_patient_data("patient123")
    
    results = engine.evaluate_patient(
        patient_data=patient_data,
        chief_complaint="chest pain"
    )
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import logging

from .fhir_client import PatientData, LabResult, CommonLOINC

logger = logging.getLogger(__name__)


class CriteriaStatus(Enum):
    """Status of diagnostic criteria evaluation."""
    PRESENT = "present"  # Criterion is met
    ABSENT = "absent"  # Criterion is not met
    UNKNOWN = "unknown"  # Cannot determine (missing data)


@dataclass
class CriterionEvaluation:
    """Result of evaluating a single diagnostic criterion."""
    criterion: str
    status: CriteriaStatus
    value: Optional[Any] = None
    expected: Optional[str] = None
    details: Optional[str] = None


@dataclass
class DiagnosisEvaluation:
    """Complete evaluation of a diagnosis against patient data."""
    diagnosis_id: str
    diagnosis_label: str
    family: str
    probability: float  # 0-1 score
    criteria_met: List[CriterionEvaluation]
    criteria_not_met: List[CriterionEvaluation]
    criteria_unknown: List[CriterionEvaluation]
    recommendations: List[str]
    missing_tests: List[str]
    severity: str = "moderate"  # low, moderate, high, critical, unknown
    # "evaluated" | "insufficient data" | "evaluation failed"
    evaluation_status: str = "evaluated"
    status_reason: Optional[str] = None
    # Findings shown for context only; they never raise the probability
    supporting_findings: List[CriterionEvaluation] = field(default_factory=list)
    severity_reason: Optional[str] = None


class SmartDiagnosticEngine:
    """
    Enhanced diagnostic engine with EHR integration.
    
    Evaluates diagnostic rules against actual patient data from FHIR/EHR,
    automatically checking lab values, vital signs, and clinical criteria.

    Decision support only: recommendations describe what findings may
    warrant, never treatment orders (no drug doses, STAT orders or
    procedure activations).
    """

    EVALUATOR_LABELS = {
        "CARD-ACS": "Acute Coronary Syndrome",
        "ID-SEPSIS": "Sepsis",
        "ENDO-DKA": "Diabetic Ketoacidosis",
    }
    EVALUATOR_FAMILIES = {
        "CARD-ACS": "cardiology",
        "ID-SEPSIS": "infectious_disease",
        "ENDO-DKA": "endocrinology",
    }
    
    def __init__(self, rules_dir: str = "backend/rules"):
        """Initialize engine and load all diagnostic rules."""
        self.rules_dir = Path(rules_dir)
        self.rules = self._load_all_rules()
        logger.info(f"Loaded {len(self.rules)} diagnostic rules")
    
    def _load_all_rules(self) -> List[Dict[str, Any]]:
        """Load all rule files from rules directory."""
        all_rules = []
        
        if not self.rules_dir.exists():
            logger.warning(f"Rules directory not found: {self.rules_dir}")
            return all_rules
        
        for rule_file in self.rules_dir.glob("*.yml"):
            try:
                with open(rule_file, 'r') as f:
                    data = yaml.safe_load(f)
                    
                family = data.get("family")
                rules = data.get("rules", [])
                
                # Add family context to each rule
                for rule in rules:
                    rule["family"] = family
                    rule["family_source"] = data.get("source", "")
                    all_rules.append(rule)
                    
            except Exception as e:
                logger.error(f"Failed to load {rule_file}: {e}")
        
        return all_rules
    
    def _check_lab_criterion(
        self,
        patient_data: PatientData,
        loinc_code: str,
        operator: str,
        threshold: float,
        criterion_text: str
    ) -> CriterionEvaluation:
        """
        Check if patient's lab result meets criterion.
        
        Args:
            patient_data: Patient clinical data
            loinc_code: LOINC code for lab test
            operator: Comparison operator (>, <, >=, <=, =)
            threshold: Threshold value
            criterion_text: Human-readable criterion description
            
        Returns:
            CriterionEvaluation with result
        """
        lab = patient_data.get_lab(loinc_code)
        
        if not lab:
            return CriterionEvaluation(
                criterion=criterion_text,
                status=CriteriaStatus.UNKNOWN,
                details=f"Lab test not found (LOINC: {loinc_code})"
            )
        
        value = lab.value
        meets_criterion = False
        
        if operator == ">":
            meets_criterion = value > threshold
        elif operator == "<":
            meets_criterion = value < threshold
        elif operator == ">=":
            meets_criterion = value >= threshold
        elif operator == "<=":
            meets_criterion = value <= threshold
        elif operator == "=":
            meets_criterion = abs(value - threshold) < 0.01
        
        status = CriteriaStatus.PRESENT if meets_criterion else CriteriaStatus.ABSENT
        
        return CriterionEvaluation(
            criterion=criterion_text,
            status=status,
            value=f"{value} {lab.unit}",
            expected=f"{operator} {threshold} {lab.unit}",
            details=f"{lab.display}: {value} {lab.unit} (ref: {lab.reference_range})"
            + (" - PRELIMINARY result" if getattr(lab, "is_preliminary", False) else "")
        )
    
    def _check_vital_criterion(
        self,
        patient_data: PatientData,
        loinc_code: str,
        operator: str,
        threshold: float,
        criterion_text: str
    ) -> CriterionEvaluation:
        """Check if patient's vital sign meets criterion."""
        vital = patient_data.get_vital(loinc_code)
        
        if not vital:
            return CriterionEvaluation(
                criterion=criterion_text,
                status=CriteriaStatus.UNKNOWN,
                details=f"Vital sign not found (LOINC: {loinc_code})"
            )
        
        value = vital.value
        meets_criterion = False
        
        if operator == ">":
            meets_criterion = value > threshold
        elif operator == "<":
            meets_criterion = value < threshold
        elif operator == ">=":
            meets_criterion = value >= threshold
        elif operator == "<=":
            meets_criterion = value <= threshold
        
        status = CriteriaStatus.PRESENT if meets_criterion else CriteriaStatus.ABSENT
        
        return CriterionEvaluation(
            criterion=criterion_text,
            status=status,
            value=f"{value} {vital.unit}",
            expected=f"{operator} {threshold} {vital.unit}",
            details=f"{vital.display}: {value} {vital.unit}"
        )
    
    # Troponin units recognised for comparison, as a factor to ng/L.
    TROPONIN_UNIT_TO_NG_PER_L = {
        "ng/l": 1.0,
        "pg/ml": 1.0,
        "ng/ml": 1000.0,
        "ug/l": 1000.0,
        "µg/l": 1000.0,
        "mcg/l": 1000.0,
    }
    # Severity by multiple of the lab's upper reference limit (URL).
    TROPONIN_HIGH_MULTIPLE = 2.5
    TROPONIN_CRITICAL_MULTIPLE = 10.0

    @classmethod
    def _troponin_unit_factor(cls, unit: Optional[str]) -> Optional[float]:
        if not unit:
            return None
        return cls.TROPONIN_UNIT_TO_NG_PER_L.get(unit.strip().lower().replace(" ", ""))

    @classmethod
    def assess_troponin(cls, lab: LabResult) -> Dict[str, Any]:
        """
        Compare a troponin result with the lab's own upper reference limit.

        Returns {"elevated": True/False/None, "severity": str, "multiple": float|None,
        "reason": str, "expected": str}. "elevated" is None and severity "unknown"
        when the unit is missing/unrecognised or the lab gives no upper limit -
        no fixed cutoff is ever assumed.
        """
        factor = cls._troponin_unit_factor(lab.unit)
        if factor is None:
            reason = (f"troponin unit '{lab.unit}' is not recognised (expected ng/mL or ng/L)"
                      if lab.unit else "troponin result has no unit")
            return {"elevated": None, "severity": "unknown", "multiple": None,
                    "reason": f"Severity unknown: {reason}.", "expected": "lab upper reference limit"}

        high = (lab.reference_range or {}).get("high")
        if high is None:
            return {"elevated": None, "severity": "unknown", "multiple": None,
                    "reason": "Severity unknown: the lab reported no upper reference limit for troponin.",
                    "expected": "lab upper reference limit"}

        ref_factor = cls._troponin_unit_factor(lab.reference_unit) if lab.reference_unit else factor
        if ref_factor is None:
            return {"elevated": None, "severity": "unknown", "multiple": None,
                    "reason": f"Severity unknown: reference range unit '{lab.reference_unit}' is not recognised.",
                    "expected": "lab upper reference limit"}

        value_ng_l = lab.value * factor
        url_ng_l = high * ref_factor
        if url_ng_l <= 0:
            return {"elevated": None, "severity": "unknown", "multiple": None,
                    "reason": "Severity unknown: the lab's upper reference limit is zero or negative.",
                    "expected": "lab upper reference limit"}

        multiple = value_ng_l / url_ng_l
        expected = f"> {high} {lab.reference_unit or lab.unit} (lab upper reference limit)"
        if multiple <= 1:
            return {"elevated": False, "severity": "low", "multiple": multiple,
                    "reason": "Troponin at or below the lab's upper reference limit.", "expected": expected}
        if multiple >= cls.TROPONIN_CRITICAL_MULTIPLE:
            severity = "critical"
        elif multiple >= cls.TROPONIN_HIGH_MULTIPLE:
            severity = "high"
        else:
            severity = "moderate"
        return {"elevated": True, "severity": severity, "multiple": multiple,
                "reason": f"Troponin {multiple:.1f}x the lab's upper reference limit.", "expected": expected}

    def _evaluate_acs(self, patient_data: PatientData) -> DiagnosisEvaluation:
        """
        Specialized evaluator for Acute Coronary Syndrome.

        ACS evaluation is suggested only when troponin is elevated above the
        lab's own upper reference limit. Heart rate is reported as a supporting
        finding and never produces an ACS suggestion on its own.
        """
        criteria_met = []
        criteria_not_met = []
        criteria_unknown = []
        supporting = []
        missing_tests = []

        severity = "unknown"
        severity_reason = None
        results = []
        for loinc, assay_name in ((CommonLOINC.TROPONIN_I, "troponin I"), (CommonLOINC.TROPONIN_T, "troponin T")):
            lab = patient_data.get_lab(loinc)
            if lab:
                results.append((assay_name, lab, self.assess_troponin(lab)))

        if not results:
            criteria_unknown.append(CriterionEvaluation(
                criterion="Elevated troponin",
                status=CriteriaStatus.UNKNOWN,
                details="Troponin not measured"
            ))
            missing_tests.append("Troponin (serial measurements per institutional protocol)")
            severity_reason = "Severity unknown: troponin not measured."
        else:
            # Use the most concerning troponin result available
            rank = {"critical": 4, "high": 3, "moderate": 2, "low": 1, "unknown": 0}
            assay_name, tropo, assessment = max(results, key=lambda r: rank[r[2]["severity"]])
            prelim = " (PRELIMINARY result)" if tropo.is_preliminary else ""
            criterion = CriterionEvaluation(
                criterion="Elevated troponin",
                status=CriteriaStatus.UNKNOWN,
                value=f"{tropo.value} {tropo.unit}".strip(),
                expected=assessment["expected"],
                details=f"{assay_name}: {assessment['reason']}{prelim}",
            )
            if assessment["elevated"] is True:
                criterion.status = CriteriaStatus.PRESENT
                criteria_met.append(criterion)
            elif assessment["elevated"] is False:
                criterion.status = CriteriaStatus.ABSENT
                criteria_not_met.append(criterion)
            else:
                criteria_unknown.append(criterion)
                missing_tests.append("Troponin with lab reference range and units")
            severity = assessment["severity"] if assessment["elevated"] is not False else "low"
            severity_reason = assessment["reason"]

        # Heart rate: context only
        hr = patient_data.get_vital(CommonLOINC.HEART_RATE)
        if hr:
            supporting.append(CriterionEvaluation(
                criterion="Heart rate",
                status=CriteriaStatus.PRESENT if hr.value > 100 else CriteriaStatus.ABSENT,
                value=f"{hr.value} {hr.unit}",
                expected="> 100/min (tachycardia)",
                details="Supporting finding only; tachycardia alone does not suggest ACS.",
            ))

        total_criteria = len(criteria_met) + len(criteria_not_met) + len(criteria_unknown)
        probability = len(criteria_met) / total_criteria if total_criteria else 0.0

        recommendations = []
        if criteria_met:
            recommendations.append(
                "Findings may warrant evaluation for ACS per ACC/AHA guidelines; "
                "consider ECG and serial troponins."
            )
        if missing_tests:
            recommendations.append(f"Data needed to evaluate: {', '.join(missing_tests)}")

        return DiagnosisEvaluation(
            diagnosis_id="CARD-ACS",
            diagnosis_label="Acute Coronary Syndrome",
            family="cardiology",
            probability=probability,
            criteria_met=criteria_met,
            criteria_not_met=criteria_not_met,
            criteria_unknown=criteria_unknown,
            recommendations=recommendations,
            missing_tests=missing_tests,
            severity=severity,
            supporting_findings=supporting,
            severity_reason=severity_reason,
        )
    
    def _evaluate_sepsis(self, patient_data: PatientData) -> DiagnosisEvaluation:
        """Evaluate for sepsis using qSOFA and SIRS criteria."""
        criteria_met = []
        criteria_not_met = []
        criteria_unknown = []
        missing_tests = []
        
        qsofa_score = 0
        
        # Respiratory rate >= 22
        rr = patient_data.get_vital(CommonLOINC.RESPIRATORY_RATE)
        if rr:
            if rr.value >= 22:
                qsofa_score += 1
                criteria_met.append(CriterionEvaluation(
                    criterion="Tachypnea (qSOFA)",
                    status=CriteriaStatus.PRESENT,
                    value=f"{rr.value} {rr.unit}",
                    expected=">= 22/min"
                ))
            else:
                criteria_not_met.append(CriterionEvaluation(
                    criterion="Tachypnea (qSOFA)",
                    status=CriteriaStatus.ABSENT,
                    value=f"{rr.value} {rr.unit}",
                    expected=">= 22/min"
                ))
        else:
            criteria_unknown.append(CriterionEvaluation(
                criterion="Respiratory rate",
                status=CriteriaStatus.UNKNOWN
            ))
        
        # Systolic BP <= 100
        sbp = patient_data.get_vital(CommonLOINC.SYSTOLIC_BP)
        if sbp:
            if sbp.value <= 100:
                qsofa_score += 1
                criteria_met.append(CriterionEvaluation(
                    criterion="Hypotension (qSOFA)",
                    status=CriteriaStatus.PRESENT,
                    value=f"{sbp.value} {sbp.unit}",
                    expected="<= 100 mmHg"
                ))
            else:
                criteria_not_met.append(CriterionEvaluation(
                    criterion="Hypotension (qSOFA)",
                    status=CriteriaStatus.ABSENT,
                    value=f"{sbp.value} {sbp.unit}",
                    expected="<= 100 mmHg"
                ))
        else:
            criteria_unknown.append(CriterionEvaluation(
                criterion="Hypotension (qSOFA)",
                status=CriteriaStatus.UNKNOWN,
                details="Systolic blood pressure not documented"
            ))

        # Altered mentation (GCS < 15)
        gcs = patient_data.get_vital(CommonLOINC.GCS_SCORE)
        if gcs:
            if gcs.value < 15:
                qsofa_score += 1
                criteria_met.append(CriterionEvaluation(
                    criterion="Altered mentation (qSOFA)",
                    status=CriteriaStatus.PRESENT,
                    value=f"GCS {gcs.value}",
                    expected="GCS < 15",
                    details="Altered mental status contributes to qSOFA"
                ))
            else:
                criteria_not_met.append(CriterionEvaluation(
                    criterion="Altered mentation (qSOFA)",
                    status=CriteriaStatus.ABSENT,
                    value=f"GCS {gcs.value}",
                    expected="GCS < 15"
                ))
        else:
            criteria_unknown.append(CriterionEvaluation(
                criterion="Altered mentation (qSOFA)",
                status=CriteriaStatus.UNKNOWN,
                details="GCS not documented - qSOFA cannot be fully scored without it"
            ))
            missing_tests.append("Glasgow Coma Scale / mental status assessment")
        
        # WBC abnormal
        wbc = patient_data.get_lab(CommonLOINC.WBC)
        if wbc:
            if wbc.value > 12 or wbc.value < 4:
                criteria_met.append(CriterionEvaluation(
                    criterion="Abnormal WBC",
                    status=CriteriaStatus.PRESENT,
                    value=f"{wbc.value} {wbc.unit}",
                    expected="4-12 K/uL",
                    details="Leukocytosis or leukopenia"
                ))
            else:
                criteria_not_met.append(CriterionEvaluation(
                    criterion="Abnormal WBC",
                    status=CriteriaStatus.ABSENT,
                    value=f"{wbc.value} {wbc.unit}",
                    expected="< 4 or > 12 K/uL"
                ))
        else:
            criteria_unknown.append(CriterionEvaluation(
                criterion="Abnormal WBC",
                status=CriteriaStatus.UNKNOWN,
                details="WBC not measured"
            ))
            missing_tests.append("CBC with differential")
        
        # Lactate
        # Note: LOINC for lactate is 2524-7, but not in CommonLOINC yet
        
        probability = len(criteria_met) / max(len(criteria_met) + len(criteria_not_met), 1)
        
        severity = "moderate"
        if qsofa_score >= 2:
            severity = "critical"
        elif qsofa_score == 1:
            severity = "high"
        
        recommendations = []
        if qsofa_score >= 2:
            recommendations.extend([
                "qSOFA >= 2: findings may indicate high risk for sepsis.",
                "Consider evaluation per Surviving Sepsis Campaign guidelines, "
                "including blood cultures and lactate.",
                "Antibiotic and fluid management decisions per clinician judgment "
                "and institutional sepsis protocol.",
            ])
        
        return DiagnosisEvaluation(
            diagnosis_id="ID-SEPSIS",
            diagnosis_label="Sepsis",
            family="infectious_disease",
            probability=probability,
            criteria_met=criteria_met,
            criteria_not_met=criteria_not_met,
            criteria_unknown=criteria_unknown,
            recommendations=recommendations,
            missing_tests=missing_tests,
            severity=severity
        )
    
    # Glucose thresholds in mg/dL; mmol/L results are converted first.
    DKA_GLUCOSE_MG_DL = 250
    CRITICAL_GLUCOSE_MG_DL = 500
    GLUCOSE_MG_DL_PER_MMOL_L = 18.016
    GLUCOSE_UNIT_TO_MG_DL = {"mg/dl": 1.0, "mmol/l": GLUCOSE_MG_DL_PER_MMOL_L}

    @classmethod
    def glucose_in_mg_dl(cls, lab: LabResult) -> Tuple[Optional[float], Optional[str]]:
        """Return (glucose in mg/dL, None), or (None, reason) when the unit is unusable."""
        if not lab.unit or not lab.unit.strip():
            return None, "glucose result has no unit."
        factor = cls.GLUCOSE_UNIT_TO_MG_DL.get(lab.unit.strip().lower().replace(" ", ""))
        if factor is None:
            return None, f"glucose unit '{lab.unit}' is not recognised (expected mg/dL or mmol/L)."
        return lab.value * factor, None

    def _evaluate_dka(self, patient_data: PatientData) -> DiagnosisEvaluation:
        """Evaluate for Diabetic Ketoacidosis."""
        criteria_met = []
        criteria_not_met = []
        criteria_unknown = []
        missing_tests = []
        
        # Hyperglycemia - compared in mg/dL after unit conversion
        glucose = patient_data.get_lab(CommonLOINC.GLUCOSE)
        glucose_mg_dl, glucose_unit_problem = self.glucose_in_mg_dl(glucose) if glucose else (None, None)
        if glucose and glucose_unit_problem:
            criteria_unknown.append(CriterionEvaluation(
                criterion="Hyperglycemia",
                status=CriteriaStatus.UNKNOWN,
                value=f"{glucose.value} {glucose.unit}".strip(),
                expected="> 250 mg/dL (13.9 mmol/L)",
                details=glucose_unit_problem,
            ))
            missing_tests.append("Blood glucose with units (mg/dL or mmol/L)")
        elif glucose:
            converted = "" if glucose.unit.strip().lower() == "mg/dl" else f" (= {glucose_mg_dl:.0f} mg/dL)"
            if glucose_mg_dl > self.DKA_GLUCOSE_MG_DL:
                criteria_met.append(CriterionEvaluation(
                    criterion="Hyperglycemia",
                    status=CriteriaStatus.PRESENT,
                    value=f"{glucose.value} {glucose.unit}{converted}",
                    expected="> 250 mg/dL (13.9 mmol/L)"
                ))
            else:
                criteria_not_met.append(CriterionEvaluation(
                    criterion="Hyperglycemia",
                    status=CriteriaStatus.ABSENT,
                    value=f"{glucose.value} {glucose.unit}{converted}",
                    expected="> 250 mg/dL (13.9 mmol/L)"
                ))
        else:
            criteria_unknown.append(CriterionEvaluation(
                criterion="Hyperglycemia",
                status=CriteriaStatus.UNKNOWN,
                details="Blood glucose not measured"
            ))
            missing_tests.append("Blood glucose")
        
        # Metabolic acidosis (low bicarb)
        co2 = patient_data.get_lab(CommonLOINC.CO2)
        if co2:
            if co2.value < 18:
                criteria_met.append(CriterionEvaluation(
                    criterion="Metabolic acidosis",
                    status=CriteriaStatus.PRESENT,
                    value=f"{co2.value} {co2.unit}",
                    expected="< 18 mEq/L",
                    details="Low bicarbonate suggests metabolic acidosis"
                ))
            else:
                criteria_not_met.append(CriterionEvaluation(
                    criterion="Metabolic acidosis",
                    status=CriteriaStatus.ABSENT,
                    value=f"{co2.value} {co2.unit}",
                    expected="< 18 mEq/L"
                ))
        else:
            criteria_unknown.append(CriterionEvaluation(
                criterion="Metabolic acidosis",
                status=CriteriaStatus.UNKNOWN,
                details="Bicarbonate (CO2) not measured"
            ))
            missing_tests.append("Basic metabolic panel (BMP)")
        
        probability = len(criteria_met) / max(len(criteria_met) + len(criteria_not_met), 1)
        
        severity = "moderate"
        severity_reason = None
        if len(criteria_met) >= 2:
            severity = "high"
        if glucose and glucose_unit_problem:
            severity = "unknown"
            severity_reason = f"Severity unknown: {glucose_unit_problem}"
        elif glucose_mg_dl is not None and glucose_mg_dl > self.CRITICAL_GLUCOSE_MG_DL:
            severity = "critical"
            severity_reason = f"Glucose {glucose_mg_dl:.0f} mg/dL (> {self.CRITICAL_GLUCOSE_MG_DL} mg/dL)."
        
        recommendations = []
        if len(criteria_met) >= 2:
            recommendations.extend([
                "Findings may warrant evaluation for DKA per ADA guidelines; "
                "consider serum/urine ketones, VBG or ABG for pH, and potassium.",
                "Fluid and insulin management per clinician judgment and "
                "institutional DKA protocol.",
                "Consider evaluating for a precipitating cause (infection, MI, "
                "medication nonadherence).",
            ])
        
        return DiagnosisEvaluation(
            diagnosis_id="ENDO-DKA",
            diagnosis_label="Diabetic Ketoacidosis",
            family="endocrinology",
            probability=probability,
            criteria_met=criteria_met,
            criteria_not_met=criteria_not_met,
            criteria_unknown=criteria_unknown,
            recommendations=recommendations,
            missing_tests=missing_tests,
            severity=severity,
            severity_reason=severity_reason,
        )
    
    def evaluate_patient(
        self,
        patient_data: PatientData,
        chief_complaint: Optional[str] = None,
        focus_specialties: Optional[List[str]] = None
    ) -> List[DiagnosisEvaluation]:
        """
        Evaluate patient data against diagnostic rules.
        
        Args:
            patient_data: Patient clinical data from FHIR
            chief_complaint: Patient's chief complaint (optional)
            focus_specialties: List of specialties to focus on (optional)
            
        Returns:
            List of DiagnosisEvaluation objects, sorted by probability
        """
        logger.info(
            f"Evaluating patient {patient_data.name} "
            f"(Age: {patient_data.age}, Gender: {patient_data.gender})"
        )
        
        if chief_complaint:
            logger.info(f"Chief complaint: {chief_complaint}")
        
        evaluations = []
        
        # Use specialized evaluators for key conditions
        specialized_evaluations = {
            "CARD-ACS": self._evaluate_acs,
            "ID-SEPSIS": self._evaluate_sepsis,
            "ENDO-DKA": self._evaluate_dka
        }
        
        for diagnosis_id, evaluator_func in specialized_evaluations.items():
            try:
                evaluation = evaluator_func(patient_data)
            except Exception as e:
                logger.error(f"Failed to evaluate {diagnosis_id}: {e}")
                evaluation = DiagnosisEvaluation(
                    diagnosis_id=diagnosis_id,
                    diagnosis_label=self.EVALUATOR_LABELS.get(diagnosis_id, diagnosis_id),
                    family=self.EVALUATOR_FAMILIES.get(diagnosis_id, "unknown"),
                    probability=0.0,
                    criteria_met=[], criteria_not_met=[], criteria_unknown=[],
                    recommendations=[],
                    missing_tests=[],
                    severity="unknown",
                    evaluation_status="evaluation failed",
                    status_reason=f"Evaluation failed: {type(e).__name__}: {e}",
                )
            else:
                if evaluation.criteria_unknown and evaluation.probability <= 0.3:
                    evaluation.evaluation_status = "insufficient data"
                    missing = ", ".join(evaluation.missing_tests) or ", ".join(
                        c.criterion for c in evaluation.criteria_unknown)
                    evaluation.status_reason = f"Insufficient data to evaluate; missing: {missing}"
            evaluations.append(evaluation)
        
        # Sort by probability (highest first)
        evaluations.sort(key=lambda x: x.probability, reverse=True)
        
        # Hide low-probability results only when they were fully evaluated;
        # failed and insufficient-data evaluations are always shown so a gap
        # in the data is never mistaken for a negative finding.
        evaluations = [
            e for e in evaluations
            if e.probability > 0.3
            or e.severity in ["high", "critical"]
            or e.evaluation_status != "evaluated"
        ]
        
        logger.info(f"Generated {len(evaluations)} diagnostic evaluations")
        
        return evaluations
    
    def format_evaluation_report(self, evaluation: DiagnosisEvaluation) -> str:
        """Format evaluation as human-readable report."""
        severity_emoji = {
            "low": "🟢",
            "moderate": "🟡",
            "high": "🟠",
            "critical": "🔴"
        }
        
        report = []
        report.append("=" * 70)
        report.append(f"{severity_emoji.get(evaluation.severity, '')} {evaluation.diagnosis_label}")
        report.append(f"   Family: {evaluation.family.replace('_', ' ').title()}")
        report.append(f"   Probability: {evaluation.probability:.1%}")
        report.append(f"   Severity: {evaluation.severity.upper()}")
        if evaluation.evaluation_status != "evaluated":
            report.append(f"   Status: {evaluation.evaluation_status.upper()} - {evaluation.status_reason}")
        report.append("=" * 70)
        
        if evaluation.criteria_met:
            report.append("\n✓ CRITERIA MET:")
            for criterion in evaluation.criteria_met:
                report.append(f"  • {criterion.criterion}")
                if criterion.value:
                    report.append(f"    Value: {criterion.value} (expected: {criterion.expected})")
                if criterion.details:
                    report.append(f"    {criterion.details}")
        
        if evaluation.criteria_not_met:
            report.append("\n✗ CRITERIA NOT MET:")
            for criterion in evaluation.criteria_not_met:
                report.append(f"  • {criterion.criterion}")
                if criterion.value:
                    report.append(f"    Value: {criterion.value}")
        
        if evaluation.criteria_unknown:
            report.append("\n? INSUFFICIENT DATA:")
            for criterion in evaluation.criteria_unknown:
                report.append(f"  • {criterion.criterion}")
                if criterion.details:
                    report.append(f"    {criterion.details}")
        
        if evaluation.missing_tests:
            report.append("\n🔬 RECOMMENDED TESTS:")
            for test in evaluation.missing_tests:
                report.append(f"  • {test}")
        
        if evaluation.recommendations:
            report.append("\n💡 RECOMMENDATIONS:")
            for rec in evaluation.recommendations:
                report.append(f"  • {rec}")
        
        report.append("=" * 70)
        
        return "\n".join(report)
