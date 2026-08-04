
from fastapi import APIRouter, Body, Depends, Request, HTTPException
from typing import Any, Dict, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import math
import os
from .decision_tree_engine import DecisionTreeEngine
from .auth_service import get_current_user, get_optional_user, add_search_to_history
from .search_limiter import check_search_limit, get_search_limit_info
from .subscription_gate import SubscriptionGate
from .medication_safety_service import MedicationSafetyService
from .patient_history_service import PatientHistoryService
from .context_engine import get_context_engine

router = APIRouter(prefix="/diagnostic", tags=["diagnostic"], dependencies=[Depends(get_current_user)])
_trees = DecisionTreeEngine()
_med_safety = MedicationSafetyService()
_context_engine = get_context_engine()

# Medication-history tuning (phase 3): defaults can be overridden per site/specialty.
DEFAULT_MED_HISTORY_WEIGHTS = {
    "base_weight": float(os.getenv("MED_HISTORY_BASE_WEIGHT", "1.0")),
    "outcome_learning_weight": float(os.getenv("MED_HISTORY_OUTCOME_LEARNING_WEIGHT", "0.6")),
    "adverse_penalty_multiplier": float(os.getenv("MED_HISTORY_ADVERSE_PENALTY_MULTIPLIER", "2.0")),
    "half_life_days": float(os.getenv("MED_HISTORY_HALF_LIFE_DAYS", "90")),
}

DX_FAMILY_KEYWORDS = {
    "cardiology": ["card", "acs", "mi", "arrhythm", "heart", "htn", "hypertension"],
    "endocrine": ["endo", "diab", "dka", "thyroid", "glucose"],
    "infectious": ["id", "sepsis", "infect", "pneum", "uti"],
    "pulmonary": ["pulm", "copd", "asthma", "resp", "hypox"],
    "neurology": ["neuro", "stroke", "seizure", "migraine"],
}

MEDICATION_CLASS_HINTS = {
    "statin": ["atorvastatin", "simvastatin", "rosuvastatin", "pravastatin"],
    "beta blocker": ["metoprolol", "atenolol", "carvedilol", "bisoprolol"],
    "ace inhibitor": ["lisinopril", "enalapril", "ramipril"],
    "arb": ["losartan", "valsartan", "irbesartan"],
    "anticoagulant": ["warfarin", "apixaban", "rivaroxaban", "dabigatran", "enoxaparin"],
    "antiplatelet": ["aspirin", "clopidogrel", "ticagrelor"],
    "insulin": ["insulin", "glargine", "lispro", "aspart"],
    "antidiabetic": ["metformin", "glipizide", "empagliflozin", "sitagliptin"],
    "nsaid": ["ibuprofen", "naproxen", "diclofenac", "ketorolac"],
    "ssri": ["sertraline", "fluoxetine", "escitalopram", "citalopram", "paroxetine"],
}

THERAPY_CLASS_TO_FAMILY = {
    "statin": ["cardiology"],
    "beta blocker": ["cardiology", "neurology"],
    "ace inhibitor": ["cardiology"],
    "arb": ["cardiology"],
    "anticoagulant": ["cardiology", "neurology"],
    "antiplatelet": ["cardiology", "neurology"],
    "insulin": ["endocrine"],
    "antidiabetic": ["endocrine"],
    "nsaid": ["infectious", "pulmonary", "neurology"],
    "ssri": ["neurology"],
}

# Simple in-memory outcome-learning store.
_medication_outcomes_store: Dict[str, Dict[str, int]] = {}

# Initialize patient history service for EMR integration
# FHIR server configuration from environment variables
FHIR_BASE_URL = os.getenv("FHIR_BASE_URL", "http://localhost:8080/fhir")
FHIR_AUTH_TOKEN = os.getenv("FHIR_AUTH_TOKEN", None)
_patient_history = None  # Will be initialized on first use

# Import user subscriptions from subscription_router
# In production, this would be a database connection
from .subscription_router import user_subscriptions

async def get_patient_history_service() -> PatientHistoryService:
    """Get or initialize patient history service for EMR integration."""
    global _patient_history
    if _patient_history is None:
        _patient_history = PatientHistoryService(
            fhir_base_url=FHIR_BASE_URL,
            auth_token=FHIR_AUTH_TOKEN
        )
    return _patient_history


class MedicationOutcomeFeedback(BaseModel):
    """Outcome feedback used to tune medication-history weighting over time."""
    medication: str
    outcome: str = Field(..., description="success | failure | adverse")
    specialty: Optional[str] = None
    site_id: Optional[str] = None


def _normalize_text(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def _parse_iso_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def _days_since(reference_dt: Optional[datetime]) -> Optional[float]:
    if reference_dt is None:
        return None
    now = datetime.now(timezone.utc)
    delta = now - reference_dt
    return max(0.0, delta.total_seconds() / 86400.0)


def _recency_weight(days_ago: Optional[float], half_life_days: float) -> float:
    """Exponential decay where weight halves every half_life_days."""
    if days_ago is None:
        return 0.2
    if half_life_days <= 0:
        return 1.0
    return math.exp(-math.log(2) * (days_ago / half_life_days))


def _classify_medication(med_name: Optional[str]) -> str:
    med = _normalize_text(med_name)
    if not med:
        return "unknown"

    direct_class = _med_safety._get_drug_class(med)
    if direct_class:
        return direct_class

    for class_name, hints in MEDICATION_CLASS_HINTS.items():
        if any(hint in med for hint in hints):
            return class_name

    return "unknown"


def _infer_dx_family(tree_id: str, result: Dict[str, Any]) -> str:
    """Infer diagnosis family from tree metadata/id for medication-history scoring."""
    family_raw = _normalize_text(result.get("tree", {}).get("title"))
    tree_key = _normalize_text(tree_id)
    haystack = f"{family_raw} {tree_key}"

    for family, keywords in DX_FAMILY_KEYWORDS.items():
        if any(keyword in haystack for keyword in keywords):
            return family
    return "general"


def _get_effective_weights(patient_context: Dict[str, Any]) -> Dict[str, float]:
    """Merge default weight config with optional site/specialty overrides."""
    effective = dict(DEFAULT_MED_HISTORY_WEIGHTS)
    if not isinstance(patient_context, dict):
        return effective

    med_cfg = patient_context.get("med_history_weights") or {}
    if isinstance(med_cfg, dict):
        for key in ["base_weight", "outcome_learning_weight", "adverse_penalty_multiplier", "half_life_days"]:
            if key in med_cfg:
                try:
                    effective[key] = float(med_cfg[key])
                except Exception:
                    pass
    return effective


def _get_outcome_bias(med_class: str, outcome_learning_weight: float) -> float:
    bucket = _medication_outcomes_store.get(med_class, {})
    success = int(bucket.get("success", 0))
    failure = int(bucket.get("failure", 0))
    adverse = int(bucket.get("adverse", 0))
    total = success + failure + adverse
    if total == 0:
        return 0.0

    raw = (success - failure - (2 * adverse)) / total
    return raw * outcome_learning_weight


def _extract_med_history_features(
    medication_history: List[Dict[str, Any]],
    current_medications: List[Dict[str, Any]],
    dx_family: str,
    weights: Dict[str, float],
    proposed_medications: List[str],
) -> Dict[str, Any]:
    """Build medication timeline features and explainability signals for diagnosis support."""
    half_life_days = float(weights.get("half_life_days", 90.0))
    adverse_penalty_multiplier = float(weights.get("adverse_penalty_multiplier", 2.0))

    features = {
        "recent_discontinuations_30d": 0,
        "prior_adverse_reaction_flags": 0,
        "failed_trials_by_class": {},
        "duplicate_therapy_history": {},
        "high_risk_withdrawal_risk": False,
    }

    support_score = 0.0
    conflict_score = 0.0
    supported_signals: List[str] = []
    conflicting_signals: List[str] = []
    blocked_recommendations: List[Dict[str, str]] = []

    current_classes: List[str] = []
    for med in current_medications or []:
        cls = _classify_medication(med.get("name"))
        if cls != "unknown":
            current_classes.append(cls)

    class_frequency: Dict[str, int] = {}
    therapy_matches = THERAPY_CLASS_TO_FAMILY

    for med in medication_history or []:
        med_name = med.get("name")
        med_class = _classify_medication(med_name)
        if med_class == "unknown":
            continue

        class_frequency[med_class] = class_frequency.get(med_class, 0) + 1

        status = _normalize_text(med.get("status"))
        stop_dt = _parse_iso_date(med.get("date_stopped")) or _parse_iso_date(med.get("date_prescribed"))
        days_ago = _days_since(stop_dt)
        recency = _recency_weight(days_ago, half_life_days)
        outcome_bias = _get_outcome_bias(med_class, float(weights.get("outcome_learning_weight", 0.6)))

        reason_text = _normalize_text(med.get("stop_reason") or med.get("reason") or med.get("note"))
        adverse_stop = any(tok in reason_text for tok in ["adverse", "allergy", "rash", "anaphyl", "intoler", "side effect"])

        is_discontinued = status in ["stopped", "completed", "cancelled"]
        if is_discontinued and days_ago is not None and days_ago <= 30:
            features["recent_discontinuations_30d"] += 1

        if adverse_stop:
            features["prior_adverse_reaction_flags"] += 1
            conflict_increment = recency * adverse_penalty_multiplier
            conflict_score += conflict_increment
            conflicting_signals.append(f"Prior adverse reaction to {med_name or med_class}")

        if is_discontinued and not adverse_stop:
            failed = features["failed_trials_by_class"].get(med_class, 0)
            features["failed_trials_by_class"][med_class] = failed + 1
            conflict_score += recency
            conflicting_signals.append(f"Prior failed trial in class: {med_class}")

        mapped_families = therapy_matches.get(med_class, [])
        if dx_family in mapped_families:
            support_delta = recency + outcome_bias
            support_score += support_delta
            supported_signals.append(f"Medication class {med_class} supports {dx_family} context")
        elif mapped_families:
            # Non-matching class can weakly conflict with current family focus.
            conflict_score += max(0.0, recency * 0.25)

    for med_class, count in class_frequency.items():
        if count > 1:
            features["duplicate_therapy_history"][med_class] = count

    withdrawal_classes = {"beta blocker", "ssri", "anticoagulant", "insulin"}
    features["high_risk_withdrawal_risk"] = any(
        med_class in withdrawal_classes and freq >= 2
        for med_class, freq in class_frequency.items()
    )

    # Recommendation blocking based on prior adverse reactions by class/name.
    adverse_markers = {sig.split(" to ")[-1].lower() for sig in conflicting_signals if "Prior adverse reaction" in sig}
    filtered_proposals: List[str] = []
    for proposed in proposed_medications:
        proposed_norm = _normalize_text(proposed)
        proposed_class = _classify_medication(proposed_norm)
        blocked = False
        for marker in adverse_markers:
            marker_class = _classify_medication(marker)
            if proposed_norm == marker or (marker_class != "unknown" and proposed_class == marker_class):
                blocked = True
                blocked_recommendations.append({
                    "medication": proposed,
                    "reason": f"Blocked due to prior adverse history ({marker})"
                })
                conflict_score += 0.5
                break
        if not blocked:
            filtered_proposals.append(proposed)

    return {
        "features": features,
        "support_score": round(support_score * float(weights.get("base_weight", 1.0)), 3),
        "conflict_score": round(conflict_score * float(weights.get("base_weight", 1.0)), 3),
        "history_supported_signals": supported_signals[:20],
        "history_conflicting_signals": conflicting_signals[:20],
        "blocked_recommendations": blocked_recommendations,
        "filtered_proposed_medications": filtered_proposals,
    }


def _append_unique_terms(target: List[str], values: List[str]) -> List[str]:
    """Append non-empty strings while preserving insertion order."""
    seen = {str(v).lower() for v in target if isinstance(v, str)}
    for value in values:
        if not isinstance(value, str):
            continue
        clean = value.strip()
        if not clean:
            continue
        key = clean.lower()
        if key not in seen:
            target.append(clean)
            seen.add(key)
    return target


def _derive_terms_from_history(patient_history) -> Dict[str, List[str]]:
    """Derive clinically relevant symptom/red-flag terms from encounter/history data."""
    derived_symptoms: List[str] = []
    derived_red_flags: List[str] = []

    for hp in patient_history.history_and_physicals[:3]:
        if hp.chief_complaint:
            derived_symptoms.append(hp.chief_complaint)

    if patient_history.vital_signs:
        v = patient_history.vital_signs[0]

        if v.heart_rate is not None:
            if v.heart_rate >= 130:
                derived_red_flags.append("severe tachycardia")
            if v.heart_rate >= 100:
                derived_symptoms.append("tachycardia")
            elif v.heart_rate <= 50:
                derived_symptoms.append("bradycardia")

        if v.blood_pressure_systolic is not None:
            if v.blood_pressure_systolic < 90:
                derived_red_flags.append("hypotension")
            elif v.blood_pressure_systolic >= 140:
                derived_symptoms.append("hypertension")

        if v.temperature is not None:
            if v.temperature >= 100.4:
                derived_symptoms.append("fever")
            elif v.temperature < 95.0:
                derived_red_flags.append("hypothermia")

        if v.respiratory_rate is not None:
            if v.respiratory_rate >= 22:
                derived_symptoms.append("tachypnea")
            elif v.respiratory_rate <= 10:
                derived_red_flags.append("bradypnea")

        if v.oxygen_saturation is not None:
            if v.oxygen_saturation < 90:
                derived_red_flags.append("severe hypoxemia")
            elif v.oxygen_saturation < 94:
                derived_symptoms.append("hypoxemia")

    return {
        "symptoms": derived_symptoms,
        "red_flags": derived_red_flags,
    }

@router.get("/search-limit")
def get_search_limit_status(
    request: Request,
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """
    Check search limit status for the current user/IP.
    
    Returns information about remaining free searches for anonymous users,
    or unlimited status for authenticated users.
    
    Useful for displaying a banner/warning before users hit their limit.
    """
    limit_info = get_search_limit_info(request, user_authenticated=bool(current_user))
    return limit_info

@router.get("/trees")
def list_trees(
    request: Request,
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """
    List all available diagnostic trees.
    
    Public endpoint - authentication optional.
    Authenticated users get personalized recommendations.
    """
    trees = _trees.list()
    
    result = {"trees": trees}
    
    # Add personalized data for authenticated users
    if current_user:
        result["user_id"] = current_user.get("user_id")
        result["search_limit"] = "unlimited"
        # Could add: recently used trees, recommended trees based on specialty, etc.
    else:
        # Show search limit info for anonymous users
        limit_info = get_search_limit_info(request, user_authenticated=False)
        result["free_trial"] = limit_info
    
    return result

@router.post("/evaluate/{tree_id}")
async def evaluate_tree(
    tree_id: str,
    request: Request,
    patient: Dict[str, Any] = Body(...),
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """
    Evaluate a patient against a diagnostic tree.
    
    🆓 FREE TRIAL: 10 searches per week for anonymous users
    🔐 UNLIMITED: Create account for unlimited searches based on your plan
    
    Public endpoint - authentication optional but recommended.
    Authenticated users get searches based on their subscription plan.
    Anonymous users limited to 10 searches per 7 days.
    """
    # Check subscription-based limits for authenticated users
    if current_user:
        async with SubscriptionGate(current_user, user_subscriptions) as gate:
            # Check if user has module access
            tree_info = _trees.get_tree_info(tree_id)
            if tree_info and tree_info.get("module"):
                module_name = tree_info["module"]
                
                # Check module access based on subscription
                feature_key = f"modules_{module_name.lower()}"
                if not gate.has_feature(feature_key):
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "error": "Module access restricted",
                            "module": module_name,
                            "tree_id": tree_id,
                            "current_plan": gate.plan.value,
                            "upgrade_required": True,
                            "message": f"Upgrade your plan to access {module_name} module"
                        }
                    )
    
    # For anonymous users or free plan users, check free trial limits
    if not current_user or (current_user and str(user_subscriptions.get(current_user["user_id"], {}).get("plan_type", "free")) == "free"):
        # Check search limits (raises 429 if limit exceeded for anonymous users)
        limit_check = check_search_limit(
            request=request,
            tree_id=tree_id,
            user_authenticated=bool(current_user)
        )
    else:
        # Paid users have unlimited searches (handled by subscription)
        limit_check = {"searches_used": 0, "searches_remaining": float('inf')}
    
    # Normalize primary tree input lists to avoid type edge cases.
    if "symptoms" in patient and not isinstance(patient["symptoms"], list):
        patient["symptoms"] = [patient["symptoms"]]
    if "red_flags" in patient and not isinstance(patient["red_flags"], list):
        patient["red_flags"] = [patient["red_flags"]]

    medication_history_records: List[Dict[str, Any]] = []
    if isinstance(patient.get("medication_history"), list):
        medication_history_records = patient.get("medication_history", [])

    # Pull patient history from EMR if patient_id provided (EMR instances)
    emr_data_pulled = False
    if patient.get("emr_patient_id"):
        try:
            history_service = await get_patient_history_service()
            patient_history = await history_service.get_comprehensive_history(
                patient_id=patient["emr_patient_id"],
                lookback_days=patient.get("lookback_days", 365)
            )
            
            # Merge EMR data into patient object
            if patient_history.current_medications:
                # Convert medication objects to simple medication names
                emr_medications = [med.get("name") for med in patient_history.current_medications if med.get("name")]
                patient["current_medications"] = emr_medications
                emr_data_pulled = True

            # Preserve full medication records for timeline-aware scoring.
            medication_history_records = patient_history.medication_history or []
            patient["medication_history"] = medication_history_records
            
            if patient_history.allergies:
                patient["allergies"] = patient_history.allergies
            
            if patient_history.active_conditions:
                patient["conditions"] = [cond.get("code") for cond in patient_history.active_conditions if cond.get("code")]

            # Attach latest encounter vitals in a machine-readable form.
            if patient_history.vital_signs:
                latest_vitals = patient_history.vital_signs[0]
                patient["vital_signs"] = {
                    "heart_rate": latest_vitals.heart_rate,
                    "blood_pressure": {
                        "systolic": latest_vitals.blood_pressure_systolic,
                        "diastolic": latest_vitals.blood_pressure_diastolic,
                    },
                    "temperature": latest_vitals.temperature,
                    "respiratory_rate": latest_vitals.respiratory_rate,
                    "oxygen_saturation": latest_vitals.oxygen_saturation,
                }

            # Convert encounter/history context into decision-tree compatible terms.
            derived_terms = _derive_terms_from_history(patient_history)
            if "symptoms" not in patient or not isinstance(patient.get("symptoms"), list):
                patient["symptoms"] = []
            if "red_flags" not in patient or not isinstance(patient.get("red_flags"), list):
                patient["red_flags"] = []
            _append_unique_terms(patient["symptoms"], derived_terms["symptoms"])
            _append_unique_terms(patient["red_flags"], derived_terms["red_flags"])

            # Persist a compact context block for downstream explainability.
            patient["patient_context"] = patient.get("patient_context", {}) or {}
            patient["patient_context"]["emr_summary"] = {
                "history_notes_count": len(patient_history.visit_notes),
                "history_h_and_p_count": len(patient_history.history_and_physicals),
                "history_test_count": len(patient_history.diagnostic_tests),
                "history_imaging_count": len(patient_history.imaging_studies),
                "history_condition_count": len(patient_history.active_conditions),
                "history_medication_count": len(patient_history.current_medications),
                "history_discontinued_med_count": len(patient_history.medication_history),
            }
            
            # Add patient demographics if not provided
            if not patient.get("age") and patient_history.age:
                patient["age"] = patient_history.age
            
            if not patient.get("gender") and patient_history.gender:
                patient["gender"] = patient_history.gender

            emr_data_pulled = True
            
        except Exception as e:
            # Log error but continue with diagnostic evaluation
            print(f"Warning: Could not fetch EMR data for patient {patient.get('emr_patient_id')}: {e}")
    
    # Perform the evaluation
    result = _trees.evaluate(tree_id, patient)

    # Medication-history intelligence (phases 1-3): features, weights, explainability.
    med_history_analysis = None
    if result and not result.get("error"):
        current_med_records = [{"name": med} for med in patient.get("current_medications", []) if med]
        proposed_from_payload = patient.get("proposed_medications")
        if not isinstance(proposed_from_payload, list):
            proposed_from_payload = []

        patient_context = patient.get("patient_context", {}) if isinstance(patient.get("patient_context", {}), dict) else {}
        effective_weights = _get_effective_weights(patient_context)
        dx_family = _infer_dx_family(tree_id, result)
        med_history_analysis = _extract_med_history_features(
            medication_history=medication_history_records,
            current_medications=current_med_records,
            dx_family=dx_family,
            weights=effective_weights,
            proposed_medications=[str(m) for m in proposed_from_payload],
        )

        result["medication_history_analysis"] = {
            "diagnosis_family": dx_family,
            "weights": effective_weights,
            "features": med_history_analysis["features"],
            "support_score": med_history_analysis["support_score"],
            "conflict_score": med_history_analysis["conflict_score"],
            "history_supported_signals": med_history_analysis["history_supported_signals"],
            "history_conflicting_signals": med_history_analysis["history_conflicting_signals"],
            "blocked_recommendations": med_history_analysis["blocked_recommendations"],
        }
    
    # Check medication safety if medications provided
    medication_alerts = None
    if result and not result.get("error"):
        current_medications = patient.get("current_medications", [])
        proposed_medications = patient.get("proposed_medications", []) if isinstance(patient.get("proposed_medications"), list) else []
        
        # Extract proposed medications from management recommendations
        if result.get("management"):
            # Parse management text for medication recommendations
            for mgmt in result.get("management", []):
                if any(keyword in mgmt.lower() for keyword in ["aspirin", "statin", "beta blocker", "ace inhibitor", "metformin", "insulin"]):
                    # Extract medication names (simplified - would be more sophisticated)
                    if "aspirin" in mgmt.lower():
                        proposed_medications.append("aspirin")
                    if "statin" in mgmt.lower() or "atorvastatin" in mgmt.lower():
                        proposed_medications.append("atorvastatin")
                    if "metoprolol" in mgmt.lower() or "beta blocker" in mgmt.lower():
                        proposed_medications.append("metoprolol")
                    if "lisinopril" in mgmt.lower() or "ace inhibitor" in mgmt.lower():
                        proposed_medications.append("lisinopril")
        
        # Apply medication-history recommendation blocking before safety checks.
        if med_history_analysis and med_history_analysis.get("filtered_proposed_medications") is not None:
            proposed_medications = med_history_analysis["filtered_proposed_medications"]

        # Run medication safety check if we have medications
        if current_medications or proposed_medications:
            medication_alerts = _med_safety.check_medication_safety(
                current_medications=current_medications,
                proposed_medications=proposed_medications,
                patient_conditions=patient.get("conditions", []),
                patient_allergies=patient.get("allergies", []),
                age=patient.get("age"),
                renal_function=patient.get("renal_function"),
                hepatic_function=patient.get("hepatic_function"),
                pregnancy=patient.get("pregnancy", False)
            )
    
    # Add EMR data source indicator
    if emr_data_pulled:
        result["emr_data_source"] = "FHIR"
        result["emr_data_pulled"] = True

    # Surface explainability fields at top level for consumers/UI.
    if med_history_analysis:
        result["history_supported_signals"] = med_history_analysis.get("history_supported_signals", [])
        result["history_conflicting_signals"] = med_history_analysis.get("history_conflicting_signals", [])
        result["prior_medication_failures_considered"] = bool(
            med_history_analysis.get("features", {}).get("failed_trials_by_class")
        )
    
    # Save to search history for authenticated users
    if current_user and result:
        try:
            # Extract symptoms from patient data
            symptoms = []
            if "symptoms" in patient:
                symptoms = patient["symptoms"] if isinstance(patient["symptoms"], list) else [patient["symptoms"]]
            
            # Get top diagnosis from result
            top_diagnosis = None
            if isinstance(result, dict) and "diagnoses" in result and result["diagnoses"]:
                top_diagnosis = result["diagnoses"][0].get("label") if isinstance(result["diagnoses"][0], dict) else None
            
            # Save to history
            add_search_to_history(
                user_id=current_user["user_id"],
                symptoms=symptoms,
                result_count=len(result.get("diagnoses", [])) if isinstance(result, dict) else 0,
                age=patient.get("age"),
                sex=patient.get("sex"),
                family=patient.get("family"),
                top_diagnosis=top_diagnosis
            )
        except Exception as e:
            # Don't fail the evaluation if history saving fails
            print(f"Failed to save search history: {e}")
    
    # Return result with search limit info and medication alerts
    response = {"tree_result": result}
    
    # Apply patient context modifiers if provided
    patient_context = patient.get("patient_context", {})
    if patient_context and tree_id:
        try:
            context_result = _context_engine.apply_context(
                diagnosis_module_id=tree_id,
                patient_context=patient_context,
                base_result=result
            )
            
            if context_result.get("has_context"):
                response["context"] = context_result
                response["context_summary"] = _context_engine.get_context_summary(patient_context)
        except Exception as e:
            print(f"Error applying context: {e}")
            # Continue without context if there's an error
    
    # Add medication safety alerts if available
    if medication_alerts:
        response["medication_safety"] = medication_alerts
        
        # Add prominent warnings for critical issues
        if medication_alerts.get("contraindicated_medications"):
            response["critical_warnings"] = [
                f"🚫 CONTRAINDICATED: {med}" 
                for med in medication_alerts["contraindicated_medications"]
            ]
        
        # Add major interaction warnings
        major_interactions = medication_alerts.get("major_interactions", [])
        if major_interactions:
            if "warnings" not in response:
                response["warnings"] = []
            for alert in major_interactions:
                response["warnings"].append({
                    "type": "major_drug_interaction",
                    "message": f"⚠️ Major interaction: {alert['medication']} + {alert['interacting_medication']}",
                    "details": alert['clinical_effect'],
                    "recommendation": alert['recommendation']
                })

    # Add medication-history specific recommendation penalties/blocks to warnings.
    if med_history_analysis:
        blocked = med_history_analysis.get("blocked_recommendations", [])
        if blocked:
            if "warnings" not in response:
                response["warnings"] = []
            for item in blocked:
                response["warnings"].append({
                    "type": "historical_medication_block",
                    "message": f"⛔ Blocked by medication history: {item.get('medication')}",
                    "details": item.get("reason", "prior adverse history"),
                    "recommendation": "Choose an alternative medication class."
                })
    
    # Add search limit info to response
    if not current_user:
        response["search_limit"] = {
            "searches_used": limit_check["searches_used"],
            "searches_remaining": limit_check["searches_remaining"],
            "message": limit_check.get("warning") or limit_check.get("message", "")
        }
        
        if limit_check["searches_remaining"] <= 2:
            response["search_limit"]["upgrade_message"] = "Create a free account for unlimited searches!"
            response["search_limit"]["register_url"] = "/users/register"
    
    return response


@router.post("/medication-outcomes")
async def record_medication_outcome_feedback(
    payload: MedicationOutcomeFeedback,
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """
    Capture medication outcome feedback to continuously tune history-based weighting.

    Outcome values:
    - success: medication supported expected clinical improvement
    - failure: medication was ineffective
    - adverse: medication caused clinically relevant adverse event
    """
    outcome = _normalize_text(payload.outcome)
    if outcome not in {"success", "failure", "adverse"}:
        raise HTTPException(status_code=400, detail="outcome must be one of: success, failure, adverse")

    med_class = _classify_medication(payload.medication)
    if med_class == "unknown":
        med_class = _normalize_text(payload.medication)

    if med_class not in _medication_outcomes_store:
        _medication_outcomes_store[med_class] = {"success": 0, "failure": 0, "adverse": 0}
    _medication_outcomes_store[med_class][outcome] += 1

    return {
        "status": "recorded",
        "medication": payload.medication,
        "medication_class": med_class,
        "outcome": outcome,
        "totals": _medication_outcomes_store[med_class],
    }


# Data models for manual patient history
from datetime import date


class ManualVisitNote(BaseModel):
    date: Optional[str] = None
    type: Optional[str] = None
    author: Optional[str] = None
    specialty: Optional[str] = None
    content: Optional[str] = None


class ManualDiagnosticTest(BaseModel):
    date: Optional[str] = None
    test_name: Optional[str] = None
    test_type: Optional[str] = None
    result: Optional[str] = None
    abnormal: bool = False
    critical: bool = False
    interpretation: Optional[str] = None


class ManualHP(BaseModel):
    date: Optional[str] = None
    author: Optional[str] = None
    chief_complaint: Optional[str] = None
    history_of_present_illness: Optional[str] = None
    past_medical_history: List[str] = []
    past_surgical_history: List[str] = []
    medications: List[str] = []
    allergies: List[str] = []
    family_history: Optional[str] = None
    social_history: Optional[str] = None
    review_of_systems: Optional[str] = None
    physical_exam: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None


class ManualProcedure(BaseModel):
    date: Optional[str] = None
    procedure_name: Optional[str] = None
    indication: Optional[str] = None
    outcome: Optional[str] = None
    complications: Optional[str] = None
    operator: Optional[str] = None


class ManualImagingStudy(BaseModel):
    date: Optional[str] = None
    modality: Optional[str] = None
    body_site: Optional[str] = None
    indication: Optional[str] = None
    findings: Optional[str] = None
    impression: Optional[str] = None
    radiologist: Optional[str] = None


class ManualCondition(BaseModel):
    code: Optional[str] = None
    status: str = "active"
    recorded_date: Optional[str] = None
    onset: Optional[str] = None


class ManualMedication(BaseModel):
    name: Optional[str] = None
    status: str = "active"
    dosage: Optional[str] = None
    date_prescribed: Optional[str] = None


class ManualAllergy(BaseModel):
    allergen: Optional[str] = None
    reaction: Optional[str] = None


class ManualPatientHistory(BaseModel):
    patient_id: str
    patient_name: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None
    visit_notes: List[ManualVisitNote] = []
    diagnostic_tests: List[ManualDiagnosticTest] = []
    history_and_physicals: List[ManualHP] = []
    procedures: List[ManualProcedure] = []
    imaging_studies: List[ManualImagingStudy] = []
    active_conditions: List[ManualCondition] = []
    current_medications: List[ManualMedication] = []
    allergies: List[ManualAllergy] = []
    family_history: Optional[str] = None
    social_history: Optional[str] = None


# In-memory storage for manual patient histories (in production, use database)
_manual_patient_histories: Dict[str, ManualPatientHistory] = {}


@router.post("/manual-history")
async def save_manual_patient_history(
    history: ManualPatientHistory,
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """
    Save manually entered patient history for non-EMR instances.
    
    This endpoint allows clinicians to enter comprehensive patient history
    using dropdown lists and text fields when EMR integration is not available.
    
    **Features:**
    - Demographics entry
    - Visit notes documentation
    - Diagnostic test results
    - History & Physical examinations
    - Procedures performed
    - Imaging studies
    - Active medical conditions
    - Current medications
    - Allergies and intolerances
    - Family and social history
    
    **Returns:**
    - Confirmation of saved data
    - Patient ID for future retrieval
    - Summary of entered data
    """
    # Validate patient_id
    if not history.patient_id:
        raise HTTPException(status_code=400, detail="Patient ID is required")
    
    # Store in memory (in production, save to database)
    _manual_patient_histories[history.patient_id] = history
    
    # Generate summary
    summary = {
        "patient_id": history.patient_id,
        "patient_name": history.patient_name,
        "demographics": {
            "age": history.age,
            "gender": history.gender
        },
        "data_summary": {
            "visit_notes_count": len(history.visit_notes),
            "diagnostic_tests_count": len(history.diagnostic_tests),
            "abnormal_tests_count": sum(1 for test in history.diagnostic_tests if test.abnormal),
            "critical_tests_count": sum(1 for test in history.diagnostic_tests if test.critical),
            "h_and_p_count": len(history.history_and_physicals),
            "procedures_count": len(history.procedures),
            "imaging_studies_count": len(history.imaging_studies),
            "active_conditions_count": len(history.active_conditions),
            "current_medications_count": len(history.current_medications),
            "allergies_count": len(history.allergies)
        },
        "message": "Patient history saved successfully"
    }
    
    return summary


@router.get("/manual-history/{patient_id}")
async def get_manual_patient_history(
    patient_id: str,
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """
    Retrieve manually entered patient history.
    
    Returns comprehensive patient history previously entered through
    the manual entry interface.
    
    **Parameters:**
    - `patient_id`: Patient identifier
    
    **Returns:**
    - Complete patient history including all entered data
    - Same format as EMR-pulled comprehensive history for consistency
    """
    # Retrieve from memory (in production, fetch from database)
    if patient_id not in _manual_patient_histories:
        raise HTTPException(status_code=404, detail=f"No manual history found for patient {patient_id}")
    
    history = _manual_patient_histories[patient_id]
    
    # Format response similar to EMR comprehensive history
    response = {
        "patient_id": history.patient_id,
        "patient_name": history.patient_name,
        "demographics": {
            "age": history.age,
            "gender": history.gender
        },
        "visit_notes": [note.dict() for note in history.visit_notes],
        "diagnostic_tests": [test.dict() for test in history.diagnostic_tests],
        "history_and_physicals": [hp.dict() for hp in history.history_and_physicals],
        "procedures": [proc.dict() for proc in history.procedures],
        "imaging_studies": [img.dict() for img in history.imaging_studies],
        "problem_list": {
            "active": [cond.dict() for cond in history.active_conditions if cond.status == "active"],
            "resolved": [cond.dict() for cond in history.active_conditions if cond.status == "resolved"]
        },
        "medications": {
            "current": [med.dict() for med in history.current_medications if med.status == "active"],
            "historical": [med.dict() for med in history.current_medications if med.status != "active"]
        },
        "allergies": [f"{allergy.allergen} ({allergy.reaction})" for allergy in history.allergies],
        "family_history": history.family_history,
        "social_history": history.social_history,
        "data_source": "manual_entry",
        "data_quality": {
            "visit_notes_count": len(history.visit_notes),
            "diagnostic_tests_count": len(history.diagnostic_tests),
            "abnormal_tests_count": sum(1 for test in history.diagnostic_tests if test.abnormal),
            "critical_tests_count": sum(1 for test in history.diagnostic_tests if test.critical),
            "h_and_p_count": len(history.history_and_physicals),
            "procedures_count": len(history.procedures),
            "imaging_studies_count": len(history.imaging_studies)
        }
    }
    
    return response


@router.get("/manual-history/list/all")
async def list_manual_patient_histories(
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """
    List all manually entered patient histories.
    
    Returns a summary of all patients with manual history entries.
    Useful for browsing and selecting patients for evaluation.
    
    **Returns:**
    - List of patient summaries with basic demographics and data counts
    """
    patients = []
    
    for patient_id, history in _manual_patient_histories.items():
        patients.append({
            "patient_id": history.patient_id,
            "patient_name": history.patient_name,
            "age": history.age,
            "gender": history.gender,
            "data_summary": {
                "visit_notes": len(history.visit_notes),
                "tests": len(history.diagnostic_tests),
                "conditions": len(history.active_conditions),
                "medications": len(history.current_medications),
                "allergies": len(history.allergies)
            }
        })
    
    return {
        "total_patients": len(patients),
        "patients": patients
    }


@router.get("/emr/patient/{patient_id}/medications")
async def get_emr_patient_medications(
    patient_id: str,
    include_safety_check: bool = True,
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """
    Retrieve current medications from EMR for a patient.
    
    **EMR Integration Endpoint**
    
    Pulls patient medications directly from FHIR-compliant EMR system.
    Optionally performs comprehensive medication safety checking.
    
    **Use Cases:**
    - View patient's current medication list
    - Pre-diagnostic medication reconciliation
    - Pharmacy review before adding new medications
    - Clinical decision support with automatic safety checking
    
    **Parameters:**
    - `patient_id`: FHIR Patient resource ID
    - `include_safety_check`: Run medication safety analysis (default: true)
    
    **Returns:**
    - `patient_id`: FHIR patient identifier
    - `medications`: List of active medications with dosage
    - `conditions`: Active medical conditions
    - `allergies`: Known allergies
    - `medication_safety`: Safety analysis (if requested)
    
    **Example Response:**
    ```json
    {
      "patient_id": "12345",
      "patient_name": "John Doe",
      "age": 65,
      "medications": [
        {
          "name": "warfarin",
          "dosage": "5mg once daily",
          "date_prescribed": "2024-01-15"
        },
        {
          "name": "aspirin",
          "dosage": "81mg once daily",
          "date_prescribed": "2024-02-01"
        }
      ],
      "conditions": ["atrial fibrillation", "hypertension"],
      "allergies": ["penicillin"],
      "medication_safety": {
        "alerts": [
          {
            "alert_type": "drug_interaction",
            "severity": "major",
            "medication": "warfarin",
            "interacting_medication": "aspirin",
            "clinical_effect": "Increased bleeding risk"
          }
        ],
        "safety_score": 70,
        "summary": "⚠️ Major interaction identified"
      }
    }
    ```
    
    **Configuration:**
    - Set `FHIR_BASE_URL` environment variable (default: http://localhost:8080/fhir)
    - Set `FHIR_AUTH_TOKEN` for authenticated FHIR access (optional)
    """
    try:
        # Get patient history service
        history_service = await get_patient_history_service()
        
        # Fetch comprehensive patient history
        patient_history = await history_service.get_comprehensive_history(
            patient_id=patient_id,
            lookback_days=365
        )
        
        # Extract medication names
        medication_names = [med.get("name") for med in patient_history.current_medications if med.get("name")]
        condition_names = [cond.get("code") for cond in patient_history.active_conditions if cond.get("code")]
        
        response = {
            "patient_id": patient_id,
            "patient_name": patient_history.patient_name,
            "age": patient_history.age,
            "gender": patient_history.gender,
            "medications": patient_history.current_medications,
            "conditions": condition_names,
            "allergies": patient_history.allergies,
            "data_source": "FHIR EMR"
        }
        
        # Run medication safety check if requested
        if include_safety_check and medication_names:
            medication_safety = _med_safety.check_medication_safety(
                current_medications=medication_names,
                proposed_medications=[],
                patient_conditions=condition_names,
                patient_allergies=patient_history.allergies,
                age=patient_history.age,
                renal_function=None,  # Would be extracted from observations if available
                hepatic_function=None,
                pregnancy=False
            )
            response["medication_safety"] = medication_safety
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching patient medications from EMR: {str(e)}"
        )


@router.post("/medication-safety-check")
async def check_medication_safety(
    current_medications: List[str] = Body(...),
    proposed_medications: List[str] = Body(default=[]),
    patient_conditions: List[str] = Body(default=[]),
    patient_allergies: List[str] = Body(default=[]),
    age: Optional[int] = Body(default=None),
    renal_function: Optional[str] = Body(default=None),
    hepatic_function: Optional[str] = Body(default=None),
    pregnancy: bool = Body(default=False),
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """
    Comprehensive medication safety check.
    
    Analyzes current and proposed medications for:
    - **Drug-drug interactions** - Dangerous combinations
    - **Contraindications** - Medications unsafe for patient's conditions
    - **Allergen cross-reactivity** - Risk of allergic reactions
    - **Duplicate therapy** - Multiple drugs from same class
    - **Age-specific warnings** - Elderly (Beers Criteria) and pediatric
    - **Renal adjustments** - Dose modifications for kidney disease
    - **Hepatic adjustments** - Dose modifications for liver disease
    - **Pregnancy warnings** - Teratogenic medications
    
    **Use Cases:**
    - Before prescribing new medication
    - During diagnostic evaluation
    - Medication reconciliation
    - Pharmacy consult
    
    **Parameters:**
    - `current_medications`: List of current medications (e.g., ["aspirin", "warfarin"])
    - `proposed_medications`: List of medications being considered (e.g., ["ibuprofen"])
    - `patient_conditions`: List of medical conditions (e.g., ["asthma", "kidney disease"])
    - `patient_allergies`: List of known allergies (e.g., ["penicillin", "sulfa"])
    - `age`: Patient age in years
    - `renal_function`: Kidney function ("normal", "mild", "moderate", "severe", "esrd")
    - `hepatic_function`: Liver function ("normal", "mild", "moderate", "severe", "cirrhosis")
    - `pregnancy`: Whether patient is pregnant
    
    **Returns:**
    - `alerts`: List of all medication safety alerts
    - `safety_score`: Overall safety score (0-100, higher = safer)
    - `summary`: Human-readable safety summary
    - `contraindicated_medications`: List of absolutely contraindicated medications
    - `major_interactions`: List of major drug interactions requiring intervention
    - `requires_monitoring`: Medications requiring close monitoring
    
    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/diagnostic/medication-safety-check" \\
      -H "Content-Type: application/json" \\
      -d '{
        "current_medications": ["warfarin", "aspirin"],
        "proposed_medications": ["ibuprofen"],
        "patient_conditions": ["atrial fibrillation"],
        "patient_allergies": ["penicillin"],
        "age": 75,
        "renal_function": "moderate"
      }'
    ```
    
    **Response:**
    ```json
    {
      "alerts": [
        {
          "alert_type": "drug_interaction",
          "severity": "major",
          "medication": "warfarin",
          "interacting_medication": "ibuprofen",
          "description": "Interaction between warfarin and ibuprofen",
          "clinical_effect": "Increased bleeding risk, GI bleeding",
          "recommendation": "Use acetaminophen for pain instead",
          "monitoring": "Monitor for bleeding, especially GI",
          "alternatives": ["acetaminophen"]
        }
      ],
      "safety_score": 70,
      "summary": "⚠️ Moderate safety concerns - review alternatives",
      "contraindicated_medications": [],
      "major_interactions": [...],
      "requires_monitoring": ["warfarin", "aspirin"]
    }
    ```
    """
    result = _med_safety.check_medication_safety(
        current_medications=current_medications,
        proposed_medications=proposed_medications,
        patient_conditions=patient_conditions,
        patient_allergies=patient_allergies,
        age=age,
        renal_function=renal_function,
        hepatic_function=hepatic_function,
        pregnancy=pregnancy
    )
    
    return result

