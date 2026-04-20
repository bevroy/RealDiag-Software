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



def build_default_response(payload: AnalyzeRequest) -> AnalyzeResponse:
    return AnalyzeResponse(
        summary="General diagnostic pathway triggered.",
        differentials=[
            {
                "name": "Undifferentiated presentation",
                "confidence": 35,
                "rationale": "No domain-specific module was triggered strongly enough to take ownership of the case.",
            }
        ],
        workup=[
            "Expand the symptom set and clinical history.",
            "Apply a domain-specific RealDiag pathway module.",
        ],
        referral={
            "specialty": "Primary Care / Triage",
            "urgency": "routine",
            "reason": "Additional information is needed before a domain-specific recommendation is made.",
        },
        codes={"icd10": ["R69"], "snomed": ["74964007"], "cpt": []},
        rationale=[
            "The modular engine framework is in place, but this case did not match a stronger deployed pathway.",
            f"Age: {payload.age}; sex: {payload.sex}.",
        ],
    )
