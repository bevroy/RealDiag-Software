"""
Search terms derived from the chart for the encounter assessment's ranking.

- Vital signs: the latest reading of each vital in the FHIR pull is mapped
  with the shared vital-sign rules (vitals_terms.derive_vital_sign_terms),
  one vital at a time, so every term names the reading that produced it.
- H&P chief complaints: the three most recent histories and physicals, split
  into phrases with negated parts removed (complaint_matching).

Each term carries its source and date. Rules only; the terms are matched
against the tree library and never sent to an AI provider.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.services.complaint_matching import affirmed_phrases
from backend.services.vitals_terms import derive_vital_sign_terms

# LOINC -> (vitals key, label)
VITAL_CODES = {
    "8867-4": ("heart_rate", "Heart rate"),
    "8480-6": ("systolic", "Systolic blood pressure"),
    "8462-4": ("diastolic", "Diastolic blood pressure"),
    "8310-5": ("temperature", "Body temperature"),
    "8331-1": ("temperature", "Oral temperature"),
    "9279-1": ("respiratory_rate", "Respiratory rate"),
    "2708-6": ("oxygen_saturation", "Oxygen saturation"),
    "59408-5": ("oxygen_saturation", "Oxygen saturation (pulse oximetry)"),
}


def _date(value: Any) -> Optional[str]:
    if isinstance(value, datetime):
        return value.date().isoformat()
    return str(value)[:10] if value else None


def _latest_vitals(vitals: List[Any]) -> Dict[str, Any]:
    latest: Dict[str, Any] = {}
    for v in vitals or []:
        key = VITAL_CODES.get(getattr(v, "code", None), (None,))[0]
        if key is None or getattr(v, "value", None) is None:
            continue
        current = latest.get(key)
        if current is None or (v.effective_date or datetime.min) > (current.effective_date or datetime.min):
            latest[key] = v
    return latest


def _single_vital_input(key: str, reading: Any) -> Dict[str, Any]:
    if key in ("systolic", "diastolic"):
        return {"blood_pressure": {key: reading.value}}
    if key == "temperature":
        return {"temperature": reading.value, "temperature_unit": reading.unit}
    return {key: reading.value}


def chart_terms(patient_data: Any, history: Any) -> List[Dict[str, Any]]:
    """[{"term", "source", "date"}] in source order, one entry per distinct term."""
    out: List[Dict[str, Any]] = []
    seen = set()

    def add(term: str, source: str, date: Optional[str]) -> None:
        if term and term.lower() not in seen:
            seen.add(term.lower())
            out.append({"term": term, "source": source, "date": date})

    status = dict(getattr(patient_data, "retrieval_status", {}) or {})
    if status.get("vitals", "retrieved") == "retrieved":
        for key, reading in sorted(_latest_vitals(getattr(patient_data, "vitals", [])).items()):
            label = VITAL_CODES[reading.code][1]
            for term in derive_vital_sign_terms(_single_vital_input(key, reading))["terms"]:
                add(term, f"Vital signs: {label} {reading.value:g} {reading.unit or ''}".strip(),
                    _date(reading.effective_date))
    hp_status = (getattr(history, "retrieval_status", None) or {}).get("history_and_physicals") if history else None
    if history is not None and hp_status == "retrieved":
        for hp in list(getattr(history, "history_and_physicals", []) or [])[:3]:
            for phrase in affirmed_phrases(getattr(hp, "chief_complaint", None)):
                add(phrase, "History and physical: chief complaint", _date(getattr(hp, "date", None)))
    return out
