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
from dataclasses import dataclass
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
    severity: str = "moderate"  # low, moderate, high, critical


class SmartDiagnosticEngine:
    """
    Enhanced diagnostic engine with EHR integration.
    
    Evaluates diagnostic rules against actual patient data from FHIR/EHR,
    automatically checking lab values, vital signs, and clinical criteria.
    """
    
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
    
    def _evaluate_acs(self, patient_data: PatientData) -> DiagnosisEvaluation:
        """
        Specialized evaluator for Acute Coronary Syndrome.
        
        Checks troponin, ECG findings, and risk factors.
        """
        criteria_met = []
        criteria_not_met = []
        criteria_unknown = []
        missing_tests = []
        
        # Check troponin
        troponin_i = patient_data.get_lab(CommonLOINC.TROPONIN_I)
        troponin_t = patient_data.get_lab(CommonLOINC.TROPONIN_T)
        
        if troponin_i or troponin_t:
            tropo = troponin_i or troponin_t
            assay_name = "troponin I" if troponin_i else "troponin T"
            if tropo.reference_range:
                high_ref = tropo.reference_range.get("high")
                is_elevated = tropo.is_abnormal and tropo.value > (high_ref or 0)
                threshold_desc = f"> {high_ref} {tropo.unit} (lab reference range)"
            else:
                fallback_threshold = 0.04 if troponin_i else 0.01
                is_elevated = tropo.value > fallback_threshold
                threshold_desc = (
                    f"> {fallback_threshold} {tropo.unit} "
                    "(assay-specific default, no lab reference range provided)"
                )

            if is_elevated:
                criteria_met.append(CriterionEvaluation(
                    criterion="Elevated troponin",
                    status=CriteriaStatus.PRESENT,
                    value=f"{tropo.value} {tropo.unit}",
                    expected=threshold_desc,
                    details=f"{assay_name} elevated - consistent with myocardial injury"
                ))
            else:
                criteria_not_met.append(CriterionEvaluation(
                    criterion="Elevated troponin",
                    status=CriteriaStatus.ABSENT,
                    value=f"{tropo.value} {tropo.unit}",
                    expected=threshold_desc
                ))
        else:
            criteria_unknown.append(CriterionEvaluation(
                criterion="Elevated troponin",
                status=CriteriaStatus.UNKNOWN,
                details="Troponin not measured"
            ))
            missing_tests.append("Troponin (serial x3 at 0, 3, 6 hours)")
        
        # Check for tachycardia (HR > 100)
        hr = patient_data.get_vital(CommonLOINC.HEART_RATE)
        if hr:
            if hr.value > 100:
                criteria_met.append(CriterionEvaluation(
                    criterion="Tachycardia",
                    status=CriteriaStatus.PRESENT,
                    value=f"{hr.value} {hr.unit}"
                ))
        
        # Calculate probability
        total_criteria = len(criteria_met) + len(criteria_not_met) + len(criteria_unknown)
        if total_criteria > 0:
            probability = len(criteria_met) / total_criteria
        else:
            probability = 0.0
        
        # Determine severity
        severity = "moderate"
        if troponin_i and troponin_i.value > 0.4:
            severity = "critical"
        elif troponin_i and troponin_i.value > 0.1:
            severity = "high"
        
        recommendations = []
        if len(criteria_met) > 0:
            recommendations.extend([
                "Aspirin 325mg STAT (if not contraindicated)",
                "Obtain ECG immediately",
                "Cardiology consultation",
                "Consider cath lab activation if STEMI criteria met"
            ])
        
        if missing_tests:
            recommendations.append(f"Order missing tests: {', '.join(missing_tests)}")
        
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
            severity=severity
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
                "🚨 qSOFA >= 2: HIGH RISK FOR SEPSIS",
                "Obtain blood cultures x2 before antibiotics",
                "Administer broad-spectrum antibiotics within 1 hour",
                "IV fluid resuscitation (30 mL/kg crystalloid)",
                "Measure lactate",
                "Consider ICU admission"
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
    
    def _evaluate_dka(self, patient_data: PatientData) -> DiagnosisEvaluation:
        """Evaluate for Diabetic Ketoacidosis."""
        criteria_met = []
        criteria_not_met = []
        criteria_unknown = []
        missing_tests = []
        
        # Hyperglycemia
        glucose = patient_data.get_lab(CommonLOINC.GLUCOSE)
        if glucose:
            if glucose.value > 250:
                criteria_met.append(CriterionEvaluation(
                    criterion="Hyperglycemia",
                    status=CriteriaStatus.PRESENT,
                    value=f"{glucose.value} {glucose.unit}",
                    expected="> 250 mg/dL"
                ))
            else:
                criteria_not_met.append(CriterionEvaluation(
                    criterion="Hyperglycemia",
                    status=CriteriaStatus.ABSENT,
                    value=f"{glucose.value} {glucose.unit}"
                ))
        else:
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
            missing_tests.append("Basic metabolic panel (BMP)")
        
        probability = len(criteria_met) / max(len(criteria_met) + len(criteria_not_met), 1)
        
        severity = "moderate"
        if len(criteria_met) >= 2:
            severity = "high"
        if glucose and glucose.value > 500:
            severity = "critical"
        
        recommendations = []
        if len(criteria_met) >= 2:
            recommendations.extend([
                "Check serum/urine ketones",
                "Obtain VBG or ABG for pH",
                "Start IV fluids (NS 500-1000 mL/hr initially)",
                "Insulin drip protocol",
                "Monitor potassium closely",
                "Search for precipitating cause (infection, MI, medication noncompliance)"
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
            severity=severity
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
                evaluations.append(evaluation)
            except Exception as e:
                logger.error(f"Failed to evaluate {diagnosis_id}: {e}")
        
        # Sort by probability (highest first)
        evaluations.sort(key=lambda x: x.probability, reverse=True)
        
        # Filter out low probability unless high severity
        evaluations = [
            e for e in evaluations
            if e.probability > 0.3 or e.severity in ["high", "critical"]
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
