from __future__ import annotations

from typing import Any

from backend.services.domains.first_seizure import evaluate_first_seizure


FALLBACK_RESPONSE = {
    "domain": "general",
    "concern_level": "moderate",
    "differential": [
        {
            "diagnosis": "General diagnostic review required",
            "confidence": 0.35,
            "rationale": "Case did not strongly match a specialized module, so fallback review was returned.",
        }
    ],
    "workup": [
        "Expand symptom characterization",
        "Review red-flag symptoms",
        "Obtain focused history and examination",
    ],
    "referral": {
        "specialty": "Primary care / triage",
        "urgency": "Routine",
        "rationale": "No specialized module match was detected.",
    },
    "codes": {
        "icd10": [],
        "snomed": [],
    },
    "rationale": [
        "Fallback response generated because no domain-specific module reached threshold.",
    ],
}


def _normalize_payload(payload: Any) -> str:
    fields: list[str] = []
    for attr in ("chief_complaint", "summary", "free_text"):
        value = getattr(payload, attr, None)
        if isinstance(value, str) and value.strip():
            fields.append(value.strip())

    for attr in ("symptoms", "history", "risk_factors"):
        value = getattr(payload, attr, None) or []
        if isinstance(value, list):
            fields.extend([str(v) for v in value if v])

    normalized = " | ".join(fields).lower()
    normalized = normalized.replace("myocardial infarction", "mi")
    normalized = normalized.replace("post ictal", "post-ictal")
    normalized = normalized.replace("first-time seizure", "first seizure")
    return normalized


def analyze_case(payload: Any) -> dict[str, Any]:
    normalized_text = _normalize_payload(payload)

    first_seizure_result = evaluate_first_seizure(payload, normalized_text)
    if first_seizure_result:
        return first_seizure_result

    return FALLBACK_RESPONSE
