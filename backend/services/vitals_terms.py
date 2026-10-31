"""
Vital signs -> symptom-search terms and red flags.

One mapper shared by symptom search (user-entered vitals, EHR history vitals)
and decision-tree evaluation (EHR history vitals). Temperature is converted
from its recorded unit before it is compared; the thresholds themselves are
stated in degrees Fahrenheit and are unchanged.

Rules (a value meets every rule it satisfies):
  heart rate        >= 100 -> symptom "tachycardia"
                    >= 130 -> red flag "severe tachycardia"
                    <= 50  -> symptom "bradycardia"
  blood pressure    systolic < 90 -> red flag "hypotension"
                    otherwise systolic >= 140 or diastolic >= 90 -> symptom "hypertension"
  temperature (F)   >= 100.4 -> symptom "fever"
                    < 95.0   -> red flag "hypothermia"
  respiratory rate  >= 22 -> symptom "tachypnea"
                    <= 10 -> red flag "bradypnea"
  oxygen saturation < 94 -> symptom "hypoxemia"
                    < 90 -> red flag "severe hypoxemia"
"""
from typing import Any, Dict, List, Optional

from .lab_units import to_canonical

# Units accepted when a temperature carries none: the symptom-search form and
# the manual-history form both label temperature in degrees Fahrenheit.
DEFAULT_TEMPERATURE_UNIT = "F"


def _number(value: Any) -> Optional[float]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def temperature_fahrenheit(value: Any, unit: Optional[str]) -> Optional[float]:
    """Temperature in degrees F, or None when the value or its unit is unusable.

    A missing unit means degrees F (see DEFAULT_TEMPERATURE_UNIT). An
    unrecognised unit is not guessed at: the temperature is skipped.
    """
    number = _number(value)
    if number is None:
        return None
    celsius, _ = to_canonical("temperature", number, unit or DEFAULT_TEMPERATURE_UNIT)
    if celsius is None:
        return None
    return celsius * 9 / 5 + 32


def derive_vital_sign_terms(vitals: Optional[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Map one set of vitals to {"symptoms", "red_flags", "terms"}.

    "terms" is every symptom and red flag in rule order, for callers that use
    them all as search terms.

    `vitals` keys: heart_rate, blood_pressure {systolic, diastolic},
    temperature, temperature_unit, respiratory_rate, oxygen_saturation.
    Missing or non-numeric values are ignored.
    """
    symptoms: List[str] = []
    red_flags: List[str] = []
    terms: List[str] = []

    def symptom(term: str) -> None:
        symptoms.append(term)
        terms.append(term)

    def red_flag(term: str) -> None:
        red_flags.append(term)
        terms.append(term)

    if not vitals:
        return {"symptoms": symptoms, "red_flags": red_flags, "terms": terms}

    heart_rate = _number(vitals.get("heart_rate"))
    if heart_rate is not None:
        if heart_rate >= 100:
            symptom("tachycardia")
            if heart_rate >= 130:
                red_flag("severe tachycardia")
        elif heart_rate <= 50:
            symptom("bradycardia")

    bp = vitals.get("blood_pressure") or {}
    systolic = _number(bp.get("systolic")) if isinstance(bp, dict) else None
    diastolic = _number(bp.get("diastolic")) if isinstance(bp, dict) else None
    if systolic is not None and systolic < 90:
        red_flag("hypotension")
    elif (systolic is not None and systolic >= 140) or (diastolic is not None and diastolic >= 90):
        symptom("hypertension")

    temperature = temperature_fahrenheit(vitals.get("temperature"), vitals.get("temperature_unit"))
    if temperature is not None:
        if temperature >= 100.4:
            symptom("fever")
        elif temperature < 95.0:
            red_flag("hypothermia")

    respiratory_rate = _number(vitals.get("respiratory_rate"))
    if respiratory_rate is not None:
        if respiratory_rate >= 22:
            symptom("tachypnea")
        elif respiratory_rate <= 10:
            red_flag("bradypnea")

    oxygen_saturation = _number(vitals.get("oxygen_saturation"))
    if oxygen_saturation is not None and oxygen_saturation < 94:
        symptom("hypoxemia")
        if oxygen_saturation < 90:
            red_flag("severe hypoxemia")

    return {"symptoms": symptoms, "red_flags": red_flags, "terms": terms}


def vitals_from_history(vital_sign: Any) -> Dict[str, Any]:
    """The mapper's input dict from a patient_history_service.VitalSigns."""
    return {
        "heart_rate": vital_sign.heart_rate,
        "blood_pressure": {
            "systolic": vital_sign.blood_pressure_systolic,
            "diastolic": vital_sign.blood_pressure_diastolic,
        },
        "temperature": vital_sign.temperature,
        "temperature_unit": getattr(vital_sign, "temperature_unit", None),
        "respiratory_rate": vital_sign.respiratory_rate,
        "oxygen_saturation": vital_sign.oxygen_saturation,
    }
