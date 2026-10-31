"""
Medication review for the encounter assessment (rules only, no AI).

Runs the existing medication safety service and medication-history analysis
on the chart's data, which the encounter assessment already pulls:

- safety: every active medication is checked against the others
  (interactions, duplicate therapy), the problem list (contraindications),
  the recorded allergies (cross-reactivity) and the patient's age (Beers);
- history: stopped medications with an adverse stop reason (statusReason)
  and discontinuations in the last 30 days, from the medication history.

Each alert names the chart data it came from. A data type that could not be
retrieved is reported as not checked, never as "no alerts".
"""
from typing import Any, Dict, List, Optional

from backend.services.fhir_client import RETRIEVED
from backend.services.missed_items import medication_names

NOTICE = ("Rules-based checks of the chart's active medications against each other, the problem list, recorded "
          "allergies and age, and of the stopped-medication history. Reference only, not an order; the "
          "medication knowledge base is limited and pending clinical review.")


def _concept_names(resources: List[Dict[str, Any]]) -> List[str]:
    names = []
    for resource in resources or []:
        code = resource.get("code") or {}
        name = code.get("text") or next((c.get("display") for c in code.get("coding") or [] if c.get("display")), None)
        if name:
            names.append(str(name))
    return names


def _alert(alert: Dict[str, Any]) -> Dict[str, Any]:
    kind = alert.get("alert_type")
    other = alert.get("interacting_medication") or alert.get("condition") or alert.get("allergen")
    sources = ["Medication list"] + {"contraindication": ["Problem list"],
                                     "allergen_cross_reactivity": ["Allergies"],
                                     "age_warning": ["Patient age"]}.get(kind, [])
    return {"type": kind, "severity": alert.get("severity"), "medication": alert.get("medication"), "other": other,
            "description": alert.get("description"), "clinical_effect": alert.get("clinical_effect"),
            "recommendation": alert.get("recommendation"), "monitoring": alert.get("monitoring") or None,
            "data_sources": sources}


def medication_review(patient_data: Any, history: Any, history_medication_status: Optional[str]) -> Dict[str, Any]:
    from backend.services.diagnostic_router import _extract_med_history_features, _med_safety, is_adverse_stop_reason

    status = dict(getattr(patient_data, "retrieval_status", {}) or {})
    review: Dict[str, Any] = {"title": "Medication review", "notice": NOTICE, "medications": [], "alerts": [],
                              "history": None, "not_checked": []}
    if status.get("medications", RETRIEVED) != RETRIEVED:
        review["not_checked"].append("The medication list could not be retrieved; medications were not reviewed.")
        return review
    names = medication_names(patient_data.medications)
    review["medications"] = names
    conditions_ok = status.get("conditions", RETRIEVED) == RETRIEVED
    allergies_ok = status.get("allergies", RETRIEVED) == RETRIEVED
    if not conditions_ok:
        review["not_checked"].append("The problem list could not be retrieved; contraindications were not checked.")
    if not allergies_ok:
        review["not_checked"].append("Allergies could not be retrieved; allergy cross-reactivity was not checked.")
    if patient_data.age is None:
        review["not_checked"].append("Age is unknown; age-specific warnings were not checked.")
    if names:
        # The service checks contraindications, allergies and age for the
        # "proposed" list, so the active medications are passed there.
        safety = _med_safety.check_medication_safety(
            current_medications=[], proposed_medications=names,
            patient_conditions=_concept_names(patient_data.conditions) if conditions_ok else [],
            patient_allergies=_concept_names(patient_data.allergies) if allergies_ok else [],
            age=patient_data.age)
        review["alerts"] = [_alert(a) for a in safety.get("alerts", [])]
    if history is None or history_medication_status != RETRIEVED:
        review["not_checked"].append("The medication history could not be retrieved; prior adverse reactions "
                                     "and recent discontinuations were not checked.")
        return review
    records = list(getattr(history, "medication_history", []) or [])
    features = _extract_med_history_features(records, [{"name": n} for n in names], "general", {}, [])
    adverse = [{"medication": r.get("name"), "stopped": r.get("date_stopped"), "reason": r.get("stop_reason"),
                "source": "MedicationRequest.statusReason" + (f", {r['date_stopped_source']}"
                                                            if r.get("date_stopped_source") else "")}
               for r in records if is_adverse_stop_reason(r.get("stop_reason"))]
    review["history"] = {"prior_adverse_reactions": adverse,
                         "recent_discontinuations_30d": features["features"]["recent_discontinuations_30d"],
                         "stopped_medications_on_file": len(records)}
    return review
