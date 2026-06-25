"""
Medication Safety Service

Provides comprehensive medication safety checking including:
- Drug-drug interactions
- Contraindications based on patient conditions
- Allergen cross-reactivity alerts
- Renal/hepatic dosing adjustments
- Age-specific warnings

Integrates with diagnostic decision support to enhance patient safety.
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum


class InteractionSeverity(Enum):
    """Severity levels for drug interactions"""
    CONTRAINDICATED = "contraindicated"  # Never use together
    MAJOR = "major"  # Serious, requires intervention
    MODERATE = "moderate"  # Monitor closely
    MINOR = "minor"  # Usually not clinically significant


class AlertType(Enum):
    """Types of medication alerts"""
    DRUG_INTERACTION = "drug_interaction"
    CONTRAINDICATION = "contraindication"
    ALLERGEN_CROSS_REACTIVITY = "allergen_cross_reactivity"
    RENAL_ADJUSTMENT = "renal_adjustment"
    HEPATIC_ADJUSTMENT = "hepatic_adjustment"
    AGE_WARNING = "age_warning"
    PREGNANCY_WARNING = "pregnancy_warning"
    DUPLICATE_THERAPY = "duplicate_therapy"


@dataclass
class MedicationAlert:
    """Medication safety alert"""
    alert_type: AlertType
    severity: InteractionSeverity
    medication: str
    interacting_medication: Optional[str] = None
    condition: Optional[str] = None
    allergen: Optional[str] = None
    description: str = ""
    clinical_effect: str = ""
    recommendation: str = ""
    monitoring: str = ""
    alternatives: List[str] = None
    
    def __post_init__(self):
        if self.alternatives is None:
            self.alternatives = []


class MedicationSafetyService:
    """
    Comprehensive medication safety checking service.
    
    Analyzes current medications against:
    - Proposed new medications (from diagnostic recommendations)
    - Patient conditions (contraindications)
    - Patient allergies (cross-reactivity)
    - Patient demographics (age, renal function, etc.)
    """
    
    def __init__(self):
        self.drug_interactions = self._load_drug_interactions()
        self.contraindications = self._load_contraindications()
        self.allergen_cross_reactivity = self._load_allergen_cross_reactivity()
        self.duplicate_therapy_classes = self._load_duplicate_therapy_classes()
    
    def check_medication_safety(
        self,
        current_medications: List[str],
        proposed_medications: List[str],
        patient_conditions: List[str] = None,
        patient_allergies: List[str] = None,
        age: Optional[int] = None,
        renal_function: Optional[str] = None,
        hepatic_function: Optional[str] = None,
        pregnancy: bool = False
    ) -> Dict[str, Any]:
        """
        Comprehensive medication safety check.
        
        Returns:
            Dictionary with alerts, safety score, and recommendations
        """
        alerts = []
        
        # Normalize inputs
        current_medications = [self._normalize_drug_name(m) for m in (current_medications or [])]
        proposed_medications = [self._normalize_drug_name(m) for m in (proposed_medications or [])]
        patient_conditions = [c.lower() for c in (patient_conditions or [])]
        patient_allergies = [a.lower() for a in (patient_allergies or [])]
        
        # All medications (current + proposed)
        all_medications = current_medications + proposed_medications
        
        # 1. Drug-drug interactions
        interaction_alerts = self._check_drug_interactions(all_medications)
        alerts.extend(interaction_alerts)
        
        # 2. Contraindications (medications vs conditions)
        contraindication_alerts = self._check_contraindications(
            proposed_medications, patient_conditions
        )
        alerts.extend(contraindication_alerts)
        
        # 3. Allergen cross-reactivity
        allergen_alerts = self._check_allergen_cross_reactivity(
            proposed_medications, patient_allergies
        )
        alerts.extend(allergen_alerts)
        
        # 4. Duplicate therapy
        duplicate_alerts = self._check_duplicate_therapy(all_medications)
        alerts.extend(duplicate_alerts)
        
        # 5. Age-specific warnings
        if age is not None:
            age_alerts = self._check_age_warnings(proposed_medications, age)
            alerts.extend(age_alerts)
        
        # 6. Renal adjustments
        if renal_function:
            renal_alerts = self._check_renal_adjustments(proposed_medications, renal_function)
            alerts.extend(renal_alerts)
        
        # 7. Hepatic adjustments
        if hepatic_function:
            hepatic_alerts = self._check_hepatic_adjustments(proposed_medications, hepatic_function)
            alerts.extend(hepatic_alerts)
        
        # 8. Pregnancy warnings
        if pregnancy:
            pregnancy_alerts = self._check_pregnancy_warnings(proposed_medications)
            alerts.extend(pregnancy_alerts)
        
        # Calculate safety score
        safety_score = self._calculate_safety_score(alerts)
        
        # Generate summary
        summary = self._generate_safety_summary(alerts, safety_score)
        
        return {
            "alerts": [self._alert_to_dict(a) for a in alerts],
            "safety_score": safety_score,
            "summary": summary,
            "contraindicated_medications": [
                a.medication for a in alerts 
                if a.severity == InteractionSeverity.CONTRAINDICATED
            ],
            "major_interactions": [
                a for a in alerts 
                if a.severity == InteractionSeverity.MAJOR
            ],
            "requires_monitoring": [
                a.medication for a in alerts 
                if a.severity in [InteractionSeverity.MODERATE, InteractionSeverity.MAJOR]
            ],
            "alternatives_suggested": any(a.alternatives for a in alerts)
        }
    
    def _check_drug_interactions(self, medications: List[str]) -> List[MedicationAlert]:
        """Check for drug-drug interactions"""
        alerts = []
        
        for i, med1 in enumerate(medications):
            for med2 in medications[i+1:]:
                interaction = self._get_interaction(med1, med2)
                if interaction:
                    alerts.append(MedicationAlert(
                        alert_type=AlertType.DRUG_INTERACTION,
                        severity=interaction['severity'],
                        medication=med1,
                        interacting_medication=med2,
                        description=f"Interaction between {med1} and {med2}",
                        clinical_effect=interaction['effect'],
                        recommendation=interaction['recommendation'],
                        monitoring=interaction.get('monitoring', ''),
                        alternatives=interaction.get('alternatives', [])
                    ))
        
        return alerts
    
    def _check_contraindications(
        self, medications: List[str], conditions: List[str]
    ) -> List[MedicationAlert]:
        """Check for medication contraindications based on patient conditions"""
        alerts = []
        
        for med in medications:
            for condition in conditions:
                contraindication = self._get_contraindication(med, condition)
                if contraindication:
                    alerts.append(MedicationAlert(
                        alert_type=AlertType.CONTRAINDICATION,
                        severity=contraindication['severity'],
                        medication=med,
                        condition=condition,
                        description=f"{med} is contraindicated in {condition}",
                        clinical_effect=contraindication['reason'],
                        recommendation=contraindication['recommendation'],
                        alternatives=contraindication.get('alternatives', [])
                    ))
        
        return alerts
    
    def _check_allergen_cross_reactivity(
        self, medications: List[str], allergies: List[str]
    ) -> List[MedicationAlert]:
        """Check for allergen cross-reactivity"""
        alerts = []
        
        for med in medications:
            for allergy in allergies:
                cross_reactivity = self._get_cross_reactivity(med, allergy)
                if cross_reactivity:
                    alerts.append(MedicationAlert(
                        alert_type=AlertType.ALLERGEN_CROSS_REACTIVITY,
                        severity=cross_reactivity['severity'],
                        medication=med,
                        allergen=allergy,
                        description=f"Possible cross-reactivity: {med} and {allergy} allergy",
                        clinical_effect=cross_reactivity['risk'],
                        recommendation=cross_reactivity['recommendation'],
                        alternatives=cross_reactivity.get('alternatives', [])
                    ))
        
        return alerts
    
    def _check_duplicate_therapy(self, medications: List[str]) -> List[MedicationAlert]:
        """Check for duplicate therapy (same drug class)"""
        alerts = []
        drug_classes: Dict[str, List[str]] = {}
        
        # Group medications by class
        for med in medications:
            drug_class = self._get_drug_class(med)
            if drug_class:
                if drug_class not in drug_classes:
                    drug_classes[drug_class] = []
                drug_classes[drug_class].append(med)
        
        # Find duplicates
        for drug_class, meds in drug_classes.items():
            if len(meds) > 1:
                alerts.append(MedicationAlert(
                    alert_type=AlertType.DUPLICATE_THERAPY,
                    severity=InteractionSeverity.MODERATE,
                    medication=", ".join(meds),
                    description=f"Duplicate therapy: Multiple {drug_class}s",
                    clinical_effect=f"Increased risk of adverse effects from {drug_class} class",
                    recommendation="Consider using only one medication from this class",
                    alternatives=[]
                ))
        
        return alerts
    
    def _check_age_warnings(self, medications: List[str], age: int) -> List[MedicationAlert]:
        """Check for age-specific warnings"""
        alerts = []
        
        for med in medications:
            # Elderly warnings (≥65 years)
            if age >= 65:
                elderly_warning = self._get_elderly_warning(med)
                if elderly_warning:
                    alerts.append(MedicationAlert(
                        alert_type=AlertType.AGE_WARNING,
                        severity=elderly_warning['severity'],
                        medication=med,
                        description=f"Caution in elderly: {med}",
                        clinical_effect=elderly_warning['risk'],
                        recommendation=elderly_warning['recommendation'],
                        monitoring=elderly_warning.get('monitoring', ''),
                        alternatives=elderly_warning.get('alternatives', [])
                    ))
            
            # Pediatric warnings (<18 years)
            if age < 18:
                pediatric_warning = self._get_pediatric_warning(med)
                if pediatric_warning:
                    alerts.append(MedicationAlert(
                        alert_type=AlertType.AGE_WARNING,
                        severity=pediatric_warning['severity'],
                        medication=med,
                        description=f"Pediatric consideration: {med}",
                        clinical_effect=pediatric_warning['risk'],
                        recommendation=pediatric_warning['recommendation'],
                        alternatives=pediatric_warning.get('alternatives', [])
                    ))
        
        return alerts
    
    def _check_renal_adjustments(
        self, medications: List[str], renal_function: str
    ) -> List[MedicationAlert]:
        """Check for renal dose adjustments"""
        alerts = []
        
        for med in medications:
            adjustment = self._get_renal_adjustment(med, renal_function)
            if adjustment:
                alerts.append(MedicationAlert(
                    alert_type=AlertType.RENAL_ADJUSTMENT,
                    severity=adjustment['severity'],
                    medication=med,
                    description=f"Renal dose adjustment needed for {med}",
                    clinical_effect=adjustment['reason'],
                    recommendation=adjustment['adjustment'],
                    monitoring=adjustment.get('monitoring', ''),
                    alternatives=adjustment.get('alternatives', [])
                ))
        
        return alerts
    
    def _check_hepatic_adjustments(
        self, medications: List[str], hepatic_function: str
    ) -> List[MedicationAlert]:
        """Check for hepatic dose adjustments"""
        alerts = []
        
        for med in medications:
            adjustment = self._get_hepatic_adjustment(med, hepatic_function)
            if adjustment:
                alerts.append(MedicationAlert(
                    alert_type=AlertType.HEPATIC_ADJUSTMENT,
                    severity=adjustment['severity'],
                    medication=med,
                    description=f"Hepatic dose adjustment needed for {med}",
                    clinical_effect=adjustment['reason'],
                    recommendation=adjustment['adjustment'],
                    monitoring=adjustment.get('monitoring', ''),
                    alternatives=adjustment.get('alternatives', [])
                ))
        
        return alerts
    
    def _check_pregnancy_warnings(self, medications: List[str]) -> List[MedicationAlert]:
        """Check for pregnancy warnings"""
        alerts = []
        
        for med in medications:
            warning = self._get_pregnancy_warning(med)
            if warning:
                alerts.append(MedicationAlert(
                    alert_type=AlertType.PREGNANCY_WARNING,
                    severity=warning['severity'],
                    medication=med,
                    description=f"Pregnancy warning: {med}",
                    clinical_effect=warning['risk'],
                    recommendation=warning['recommendation'],
                    alternatives=warning.get('alternatives', [])
                ))
        
        return alerts
    
    def _calculate_safety_score(self, alerts: List[MedicationAlert]) -> int:
        """
        Calculate overall safety score (0-100).
        Lower score = more safety concerns
        """
        if not alerts:
            return 100
        
        # Deduct points based on severity
        score = 100
        for alert in alerts:
            if alert.severity == InteractionSeverity.CONTRAINDICATED:
                score -= 30
            elif alert.severity == InteractionSeverity.MAJOR:
                score -= 15
            elif alert.severity == InteractionSeverity.MODERATE:
                score -= 5
            elif alert.severity == InteractionSeverity.MINOR:
                score -= 2
        
        return max(0, score)
    
    def _generate_safety_summary(self, alerts: List[MedicationAlert], score: int) -> str:
        """Generate human-readable safety summary"""
        if score >= 90:
            return "✅ No significant safety concerns identified"
        elif score >= 70:
            return "⚠️ Minor safety concerns - monitor as recommended"
        elif score >= 50:
            return "⚠️ Moderate safety concerns - review alternatives"
        else:
            return "🚫 Major safety concerns - contraindications identified"
    
    def _normalize_drug_name(self, drug: str) -> str:
        """Normalize drug name for matching"""
        return drug.lower().strip()
    
    def _alert_to_dict(self, alert: MedicationAlert) -> Dict[str, Any]:
        """Convert alert to dictionary"""
        return {
            "alert_type": alert.alert_type.value,
            "severity": alert.severity.value,
            "medication": alert.medication,
            "interacting_medication": alert.interacting_medication,
            "condition": alert.condition,
            "allergen": alert.allergen,
            "description": alert.description,
            "clinical_effect": alert.clinical_effect,
            "recommendation": alert.recommendation,
            "monitoring": alert.monitoring,
            "alternatives": alert.alternatives
        }
    
    # Database loading methods (would typically load from database or files)
    
    def _load_drug_interactions(self) -> Dict[str, Dict]:
        """Load drug interaction database"""
        return {
            # Anticoagulants
            ("warfarin", "aspirin"): {
                "severity": InteractionSeverity.MAJOR,
                "effect": "Increased bleeding risk",
                "recommendation": "Consider clopidogrel as alternative or reduce aspirin dose",
                "monitoring": "Monitor for signs of bleeding, check INR frequently",
                "alternatives": ["clopidogrel"]
            },
            ("warfarin", "nsaid"): {
                "severity": InteractionSeverity.MAJOR,
                "effect": "Increased bleeding risk, GI bleeding",
                "recommendation": "Use acetaminophen for pain instead",
                "monitoring": "Monitor for bleeding, especially GI",
                "alternatives": ["acetaminophen"]
            },
            ("warfarin", "amiodarone"): {
                "severity": InteractionSeverity.MAJOR,
                "effect": "Increased warfarin effect, elevated INR",
                "recommendation": "Reduce warfarin dose by 30-50%",
                "monitoring": "Check INR 3-5 days after starting amiodarone",
                "alternatives": []
            },
            ("apixaban", "aspirin"): {
                "severity": InteractionSeverity.MODERATE,
                "effect": "Increased bleeding risk",
                "recommendation": "Use lowest effective aspirin dose (81mg)",
                "monitoring": "Monitor for bleeding",
                "alternatives": []
            },
            ("rivaroxaban", "ketoconazole"): {
                "severity": InteractionSeverity.CONTRAINDICATED,
                "effect": "Severe increase in rivaroxaban levels",
                "recommendation": "Avoid combination - use alternative antifungal",
                "monitoring": "If unavoidable, monitor closely for bleeding",
                "alternatives": ["fluconazole with dose reduction"]
            },
            
            # Antiplatelets
            ("clopidogrel", "omeprazole"): {
                "severity": InteractionSeverity.MODERATE,
                "effect": "Decreased clopidogrel efficacy, reduced antiplatelet effect",
                "recommendation": "Use pantoprazole or H2 blocker instead",
                "monitoring": "Monitor for cardiovascular events",
                "alternatives": ["pantoprazole", "ranitidine"]
            },
            ("aspirin", "ibuprofen"): {
                "severity": InteractionSeverity.MODERATE,
                "effect": "Decreased aspirin antiplatelet effect, increased GI bleeding",
                "recommendation": "Take aspirin 2 hours before ibuprofen, or use acetaminophen",
                "monitoring": "Monitor for GI bleeding",
                "alternatives": ["acetaminophen"]
            },
            
            # Statins
            ("simvastatin", "gemfibrozil"): {
                "severity": InteractionSeverity.CONTRAINDICATED,
                "effect": "Severe rhabdomyolysis risk",
                "recommendation": "Use fenofibrate or alternative statin (pravastatin)",
                "monitoring": "Never combine - use alternative",
                "alternatives": ["fenofibrate", "pravastatin"]
            },
            ("atorvastatin", "clarithromycin"): {
                "severity": InteractionSeverity.MAJOR,
                "effect": "Increased statin levels, rhabdomyolysis risk",
                "recommendation": "Hold statin during antibiotic course or use azithromycin",
                "monitoring": "Monitor for muscle pain/weakness",
                "alternatives": ["azithromycin"]
            },
            
            # Beta blockers
            ("metoprolol", "diltiazem"): {
                "severity": InteractionSeverity.MAJOR,
                "effect": "Severe bradycardia, heart block, hypotension",
                "recommendation": "Avoid combination or monitor HR/BP closely",
                "monitoring": "Check HR and BP frequently, ECG if symptomatic",
                "alternatives": ["amlodipine instead of diltiazem"]
            },
            ("metoprolol", "insulin"): {
                "severity": InteractionSeverity.MODERATE,
                "effect": "Masks hypoglycemia symptoms (tachycardia, tremor)",
                "recommendation": "Monitor blood glucose more frequently",
                "monitoring": "Check glucose regularly, counsel on hypoglycemia signs",
                "alternatives": []
            },
            
            # Antibiotics
            ("ciprofloxacin", "warfarin"): {
                "severity": InteractionSeverity.MAJOR,
                "effect": "Increased INR, bleeding risk",
                "recommendation": "Monitor INR closely or use alternative antibiotic",
                "monitoring": "Check INR 2-3 days after starting ciprofloxacin",
                "alternatives": ["azithromycin", "doxycycline"]
            },
            ("azithromycin", "amiodarone"): {
                "severity": InteractionSeverity.MAJOR,
                "effect": "QT prolongation, torsades de pointes risk",
                "recommendation": "Use alternative antibiotic (doxycycline)",
                "monitoring": "ECG monitoring if combination unavoidable",
                "alternatives": ["doxycycline", "cephalexin"]
            },
            
            # Diabetes medications
            ("metformin", "contrast dye"): {
                "severity": InteractionSeverity.MAJOR,
                "effect": "Lactic acidosis risk with renal dysfunction",
                "recommendation": "Hold metformin 48 hours before and after contrast",
                "monitoring": "Check renal function before restarting",
                "alternatives": []
            },
            
            # Antidepressants
            ("ssri", "tramadol"): {
                "severity": InteractionSeverity.MAJOR,
                "effect": "Serotonin syndrome risk",
                "recommendation": "Use alternative analgesic (acetaminophen, NSAIDs)",
                "monitoring": "Monitor for agitation, confusion, tachycardia",
                "alternatives": ["acetaminophen", "ibuprofen"]
            }
        }
    
    def _load_contraindications(self) -> Dict[str, Dict]:
        """Load contraindication database (medication vs condition)"""
        return {
            # Beta blockers
            ("metoprolol", "asthma"): {
                "severity": InteractionSeverity.CONTRAINDICATED,
                "reason": "Bronchospasm risk, worsening asthma",
                "recommendation": "Avoid beta blockers in asthma - use alternative",
                "alternatives": ["diltiazem", "amlodipine"]
            },
            ("metoprolol", "heart block"): {
                "severity": InteractionSeverity.CONTRAINDICATED,
                "reason": "Complete heart block risk",
                "recommendation": "Absolute contraindication - do not use",
                "alternatives": ["amlodipine"]
            },
            
            # NSAIDs
            ("ibuprofen", "kidney disease"): {
                "severity": InteractionSeverity.MAJOR,
                "reason": "Acute kidney injury risk, worsening renal function",
                "recommendation": "Avoid NSAIDs in CKD stage 3+ - use acetaminophen",
                "alternatives": ["acetaminophen"]
            },
            ("ibuprofen", "heart failure"): {
                "severity": InteractionSeverity.MAJOR,
                "reason": "Fluid retention, worsening heart failure",
                "recommendation": "Avoid NSAIDs in heart failure",
                "alternatives": ["acetaminophen"]
            },
            
            # Anticholinergics
            ("diphenhydramine", "glaucoma"): {
                "severity": InteractionSeverity.CONTRAINDICATED,
                "reason": "Acute angle-closure glaucoma risk",
                "recommendation": "Avoid anticholinergics - use alternative antihistamine",
                "alternatives": ["cetirizine", "loratadine"]
            },
            ("oxybutynin", "urinary retention"): {
                "severity": InteractionSeverity.CONTRAINDICATED,
                "reason": "Worsening urinary retention",
                "recommendation": "Contraindicated - do not use",
                "alternatives": []
            },
            
            # Antibiotics
            ("fluoroquinolone", "tendinitis"): {
                "severity": InteractionSeverity.MAJOR,
                "reason": "Tendon rupture risk",
                "recommendation": "Avoid fluoroquinolones with tendon problems",
                "alternatives": ["azithromycin", "doxycycline"]
            },
            
            # Anticoagulants
            ("warfarin", "active bleeding"): {
                "severity": InteractionSeverity.CONTRAINDICATED,
                "reason": "Worsening hemorrhage",
                "recommendation": "Contraindicated during active bleeding",
                "alternatives": []
            },
            
            # Metformin
            ("metformin", "kidney disease"): {
                "severity": InteractionSeverity.MAJOR,
                "reason": "Lactic acidosis risk with eGFR <30",
                "recommendation": "Avoid if eGFR <30, reduce dose if eGFR 30-45",
                "alternatives": ["insulin", "DPP-4 inhibitor"]
            },
            ("metformin", "liver disease"): {
                "severity": InteractionSeverity.MAJOR,
                "reason": "Lactic acidosis risk",
                "recommendation": "Avoid in hepatic impairment",
                "alternatives": ["insulin"]
            }
        }
    
    def _load_allergen_cross_reactivity(self) -> Dict[str, Dict]:
        """Load allergen cross-reactivity database"""
        return {
            # Penicillin cross-reactivity
            ("amoxicillin", "penicillin"): {
                "severity": InteractionSeverity.CONTRAINDICATED,
                "risk": "100% cross-reactivity - same drug class",
                "recommendation": "Avoid all penicillins - use macrolide or fluoroquinolone",
                "alternatives": ["azithromycin", "doxycycline"]
            },
            ("cephalexin", "penicillin"): {
                "severity": InteractionSeverity.MODERATE,
                "risk": "5-10% cross-reactivity risk",
                "recommendation": "Avoid if severe penicillin allergy (anaphylaxis). OK for rash only.",
                "alternatives": ["azithromycin", "doxycycline"]
            },
            ("cefuroxime", "penicillin"): {
                "severity": InteractionSeverity.MODERATE,
                "risk": "5-10% cross-reactivity risk",
                "recommendation": "Avoid if severe penicillin allergy (anaphylaxis)",
                "alternatives": ["azithromycin", "fluoroquinolone"]
            },
            
            # Sulfa cross-reactivity
            ("bactrim", "sulfa"): {
                "severity": InteractionSeverity.CONTRAINDICATED,
                "risk": "Direct sulfonamide allergy - avoid",
                "recommendation": "Contraindicated in sulfa allergy",
                "alternatives": ["doxycycline", "fluoroquinolone"]
            },
            ("furosemide", "sulfa"): {
                "severity": InteractionSeverity.MINOR,
                "risk": "Low cross-reactivity risk (different structure)",
                "recommendation": "Usually safe - monitor for rash",
                "alternatives": ["bumetanide", "torsemide"]
            },
            
            # Aspirin/NSAID cross-reactivity
            ("ibuprofen", "aspirin"): {
                "severity": InteractionSeverity.MAJOR,
                "risk": "High cross-reactivity - all NSAIDs",
                "recommendation": "Avoid all NSAIDs if aspirin allergy",
                "alternatives": ["acetaminophen"]
            },
            ("naproxen", "aspirin"): {
                "severity": InteractionSeverity.MAJOR,
                "risk": "High cross-reactivity - all NSAIDs",
                "recommendation": "Avoid all NSAIDs if aspirin allergy",
                "alternatives": ["acetaminophen"]
            },
            
            # Shellfish/iodine (controversial)
            ("contrast dye", "shellfish"): {
                "severity": InteractionSeverity.MINOR,
                "risk": "No proven cross-reactivity (myth), but document allergy",
                "recommendation": "Safe to use with premedication (steroids, antihistamines)",
                "alternatives": []
            },
            
            # Codeine/morphine
            ("hydrocodone", "codeine"): {
                "severity": InteractionSeverity.MAJOR,
                "risk": "High cross-reactivity - same opioid class",
                "recommendation": "Avoid all opioids if severe allergy",
                "alternatives": ["tramadol", "acetaminophen"]
            }
        }
    
    def _load_duplicate_therapy_classes(self) -> Dict[str, str]:
        """Map medications to drug classes for duplicate therapy checking"""
        return {
            # Beta blockers
            "metoprolol": "beta blocker",
            "atenolol": "beta blocker",
            "carvedilol": "beta blocker",
            "bisoprolol": "beta blocker",
            
            # ACE inhibitors
            "lisinopril": "ACE inhibitor",
            "enalapril": "ACE inhibitor",
            "ramipril": "ACE inhibitor",
            
            # ARBs
            "losartan": "ARB",
            "valsartan": "ARB",
            "irbesartan": "ARB",
            
            # Statins
            "atorvastatin": "statin",
            "simvastatin": "statin",
            "rosuvastatin": "statin",
            "pravastatin": "statin",
            
            # Calcium channel blockers
            "amlodipine": "calcium channel blocker",
            "diltiazem": "calcium channel blocker",
            "verapamil": "calcium channel blocker",
            
            # PPIs
            "omeprazole": "PPI",
            "pantoprazole": "PPI",
            "esomeprazole": "PPI",
            "lansoprazole": "PPI",
            
            # Anticoagulants
            "warfarin": "anticoagulant",
            "apixaban": "anticoagulant",
            "rivaroxaban": "anticoagulant",
            "dabigatran": "anticoagulant",
            
            # Antiplatelets
            "aspirin": "antiplatelet",
            "clopidogrel": "antiplatelet",
            "ticagrelor": "antiplatelet"
        }
    
    # Helper methods for checking specific interactions
    
    def _get_interaction(self, med1: str, med2: str) -> Optional[Dict]:
        """Get interaction between two medications"""
        # Check both directions
        key1 = (med1, med2)
        key2 = (med2, med1)
        
        # Check exact match
        if key1 in self.drug_interactions:
            return self.drug_interactions[key1]
        if key2 in self.drug_interactions:
            return self.drug_interactions[key2]
        
        # Check class matches (e.g., "nsaid" matches "ibuprofen", "naproxen")
        for (drug1, drug2), interaction in self.drug_interactions.items():
            if (med1 in drug1 or drug1 in med1) and (med2 in drug2 or drug2 in med2):
                return interaction
            if (med2 in drug1 or drug1 in med2) and (med1 in drug2 or drug2 in med1):
                return interaction
        
        return None
    
    def _get_contraindication(self, medication: str, condition: str) -> Optional[Dict]:
        """Get contraindication for medication + condition"""
        key = (medication, condition)
        
        # Check exact match
        if key in self.contraindications:
            return self.contraindications[key]
        
        # Check partial matches
        for (med, cond), contraindication in self.contraindications.items():
            if (medication in med or med in medication) and (condition in cond or cond in condition):
                return contraindication
        
        return None
    
    def _get_cross_reactivity(self, medication: str, allergen: str) -> Optional[Dict]:
        """Get allergen cross-reactivity"""
        key = (medication, allergen)
        
        # Check exact match
        if key in self.allergen_cross_reactivity:
            return self.allergen_cross_reactivity[key]
        
        # Check partial matches
        for (med, allergy), reactivity in self.allergen_cross_reactivity.items():
            if (medication in med or med in medication) and (allergen in allergy or allergy in allergen):
                return reactivity
        
        return None
    
    def _get_drug_class(self, medication: str) -> Optional[str]:
        """Get drug class for duplicate therapy checking"""
        for med, drug_class in self.duplicate_therapy_classes.items():
            if medication in med or med in medication:
                return drug_class
        return None
    
    def _get_elderly_warning(self, medication: str) -> Optional[Dict]:
        """Get elderly-specific warning (Beers Criteria)"""
        elderly_warnings = {
            "diphenhydramine": {
                "severity": InteractionSeverity.MAJOR,
                "risk": "Anticholinergic effects: confusion, falls, urinary retention",
                "recommendation": "Avoid in elderly - use cetirizine or loratadine",
                "monitoring": "Monitor for confusion, falls",
                "alternatives": ["cetirizine", "loratadine"]
            },
            "amitriptyline": {
                "severity": InteractionSeverity.MAJOR,
                "risk": "Strong anticholinergic, sedation, orthostatic hypotension",
                "recommendation": "Avoid - use SSRI or nortriptyline",
                "alternatives": ["sertraline", "citalopram"]
            },
            "nsaid": {
                "severity": InteractionSeverity.MODERATE,
                "risk": "GI bleeding, acute kidney injury, falls risk",
                "recommendation": "Use lowest dose for shortest duration, add PPI",
                "monitoring": "Monitor renal function, signs of bleeding",
                "alternatives": ["acetaminophen"]
            }
        }
        
        for med, warning in elderly_warnings.items():
            if medication in med or med in medication:
                return warning
        return None
    
    def _get_pediatric_warning(self, medication: str) -> Optional[Dict]:
        """Get pediatric warning"""
        pediatric_warnings = {
            "aspirin": {
                "severity": InteractionSeverity.CONTRAINDICATED,
                "risk": "Reye's syndrome risk in children <16 with viral illness",
                "recommendation": "Contraindicated in children - use acetaminophen or ibuprofen",
                "alternatives": ["acetaminophen", "ibuprofen"]
            },
            "fluoroquinolone": {
                "severity": InteractionSeverity.MAJOR,
                "risk": "Cartilage damage, tendon problems",
                "recommendation": "Avoid in children unless no alternatives",
                "alternatives": ["amoxicillin", "azithromycin"]
            }
        }
        
        for med, warning in pediatric_warnings.items():
            if medication in med or med in medication:
                return warning
        return None
    
    def _get_renal_adjustment(self, medication: str, renal_function: str) -> Optional[Dict]:
        """Get renal dose adjustment"""
        # Simplified - would be more complex in production
        renal_adjustments = {
            "metformin": {
                "severity": InteractionSeverity.MAJOR,
                "reason": "Lactic acidosis risk with reduced renal clearance",
                "adjustment": "Avoid if eGFR <30, reduce dose if eGFR 30-45",
                "monitoring": "Monitor renal function every 3-6 months"
            },
            "enoxaparin": {
                "severity": InteractionSeverity.MAJOR,
                "reason": "Accumulation with renal impairment",
                "adjustment": "Reduce dose by 50% if CrCl <30",
                "monitoring": "Monitor anti-Xa levels if available"
            },
            "gabapentin": {
                "severity": InteractionSeverity.MODERATE,
                "reason": "Renally cleared - accumulation risk",
                "adjustment": "Adjust dose based on CrCl: <60 reduce by 50%",
                "monitoring": "Monitor for sedation, dizziness"
            }
        }
        
        if renal_function.lower() in ["severe", "stage 4", "stage 5", "esrd"]:
            for med, adjustment in renal_adjustments.items():
                if medication in med or med in medication:
                    return adjustment
        return None
    
    def _get_hepatic_adjustment(self, medication: str, hepatic_function: str) -> Optional[Dict]:
        """Get hepatic dose adjustment"""
        hepatic_adjustments = {
            "warfarin": {
                "severity": InteractionSeverity.MAJOR,
                "reason": "Decreased clotting factor synthesis, increased bleeding risk",
                "adjustment": "Reduce dose, monitor INR closely",
                "monitoring": "Check INR every 3-5 days initially"
            },
            "statin": {
                "severity": InteractionSeverity.MODERATE,
                "reason": "Hepatotoxicity risk",
                "adjustment": "Avoid in active liver disease, monitor LFTs",
                "monitoring": "Check LFTs baseline and periodically"
            }
        }
        
        if hepatic_function.lower() in ["severe", "cirrhosis", "child-pugh c"]:
            for med, adjustment in hepatic_adjustments.items():
                if medication in med or med in medication:
                    return adjustment
        return None
    
    def _get_pregnancy_warning(self, medication: str) -> Optional[Dict]:
        """Get pregnancy warning"""
        pregnancy_warnings = {
            "warfarin": {
                "severity": InteractionSeverity.CONTRAINDICATED,
                "risk": "Teratogenic - fetal warfarin syndrome",
                "recommendation": "Contraindicated in pregnancy - use heparin or LMWH",
                "alternatives": ["enoxaparin", "heparin"]
            },
            "ace inhibitor": {
                "severity": InteractionSeverity.CONTRAINDICATED,
                "risk": "Fetal renal dysfunction, oligohydramnios",
                "recommendation": "Contraindicated - use labetalol or nifedipine",
                "alternatives": ["labetalol", "nifedipine"]
            },
            "statin": {
                "severity": InteractionSeverity.CONTRAINDICATED,
                "risk": "Possible teratogenicity",
                "recommendation": "Contraindicated in pregnancy",
                "alternatives": []
            }
        }
        
        for med, warning in pregnancy_warnings.items():
            if medication in med or med in medication:
                return warning
        return None
