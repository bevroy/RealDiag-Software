from __future__ import annotations

from typing import Iterable

from backend.schemas.diagnostic import AnalyzeRequest, AnalyzeResponse


SYMPTOM_SYNONYMS: dict[str, set[str]] = {
    "myocardial infarction": {"mi", "heart attack"},
    "shortness of breath": {"sob", "dyspnea"},
    "loss of consciousness": {"loc", "passed out"},
    "cognitive decline": {"memory loss", "forgetfulness"},
}


def normalize_request(payload: AnalyzeRequest) -> AnalyzeRequest:
    normalized_symptoms = [_expand_and_normalize_text(s) for s in payload.symptoms]
    normalized_history = [_expand_and_normalize_text(h) for h in payload.history]

    payload.symptoms = normalized_symptoms
    payload.history = normalized_history
    return payload



def _expand_and_normalize_text(text: str) -> str:
    value = text.strip().lower()
    expansions = []
    for canonical, synonyms in SYMPTOM_SYNONYMS.items():
        if value == canonical or value in synonyms:
            expansions.append(canonical)
            expansions.extend(sorted(synonyms))
    if expansions:
        value = " ".join(sorted(set([value, *expansions])))
    return value



def extract_symptom_text(payload: AnalyzeRequest) -> str:
    return " ".join(payload.symptoms).lower()



def extract_history_text(payload: AnalyzeRequest) -> str:
    return " ".join(payload.history).lower()



def contains_any(text: str, terms: Iterable[str]) -> bool:
    return any(term.lower() in text for term in terms)



def build_default_response(payload: AnalyzeRequest) -> dict:
    """Fallback response returned when no domain analyzer claims the case.

    Returns a plain dict matching the shape produced by domain modules
    (first_seizure / headache / concussion / cognitive_impairment) rather
    than the strict AnalyzeResponse pydantic schema, whose required field
    shape differs from what these rule modules naturally produce.
    """
    age = getattr(payload, "patient_age", getattr(payload, "age", "unknown"))
    sex = getattr(payload, "patient_sex", getattr(payload, "sex", "unknown"))
    return {
        "primary_assessment": "Undifferentiated presentation",
        "confidence": 0.35,
        "urgency": "routine",
        "differential": [
            {
                "diagnosis": "Undifferentiated presentation",
                "confidence": 0.35,
                "priority": "routine",
            }
        ],
        "workup": [
            "Expand the symptom set and clinical history.",
            "Apply a domain-specific RealDiag pathway module.",
        ],
        "referral": {
            "specialty": "Primary Care / Triage",
            "urgency": "routine",
            "reason": "Additional information is needed before a domain-specific recommendation is made.",
        },
        "codes": [
            {"system": "ICD-10", "code": "R69", "description": "Illness, unspecified"},
            {"system": "SNOMED", "code": "74964007", "description": "Other (qualifier value)"},
        ],
        "rationale": [
            "The modular engine framework is in place, but this case did not match a stronger deployed pathway.",
            f"Age: {age}; sex: {sex}.",
        ],
        "disclaimer": "Decision support only; not a substitute for clinical judgment.",
    }
