"""
RealDiag cognitive impairment domain module.

Drop-in location:
    backend/services/domains/cognitive_impairment.py

Expected interface:
    evaluate_cognitive_impairment(payload, normalized_text) -> dict | None

Returns a plain ``dict`` (matching the first_seizure / headache / concussion
convention in this repo) rather than the strict pydantic ``AnalyzeResponse``,
whose required field shape differs from what these rule modules produce.
"""

from __future__ import annotations

from typing import Any


def _make_response(
    *,
    primary_label: str,
    confidence: float,
    urgency: str,
    differential: list[dict[str, Any]],
    workup: list[str],
    referral: dict[str, Any],
    codes: list[dict[str, str]],
    rationale: list[str],
) -> dict[str, Any]:
    return {
        "primary_assessment": primary_label,
        "confidence": confidence,
        "urgency": urgency,
        "differential": differential,
        "workup": workup,
        "referral": referral,
        "codes": codes,
        "rationale": rationale,
        "disclaimer": "Clinical decision-support output only; not a substitute for clinician judgment or emergency care.",
    }


def evaluate_cognitive_impairment(payload: Any, normalized_text: str) -> dict[str, Any] | None:
    text = (normalized_text or "").lower()

    cognitive_terms = [
        "memory loss",
        "memory issues",
        "forgetfulness",
        "confusion",
        "cognitive decline",
        "repetitive questioning",
        "difficulty managing finances",
        "disorientation",
        "dementia",
    ]

    if not any(term in text for term in cognitive_terms):
        return None

    # -------------------------
    # Stroke red flag (evaluated first - emergent takes precedence)
    # -------------------------
    if (
        "weakness" in text
        or "speech changes" in text
        or "facial droop" in text
    ):
        return _make_response(
            primary_label="Acute neurologic event concern (stroke/TIA)",
            confidence=0.85,
            urgency="emergent",
            differential=[
                {"diagnosis": "Stroke", "confidence": 0.78, "priority": "must-not-miss"},
                {"diagnosis": "Transient ischemic attack", "confidence": 0.55, "priority": "must-not-miss"},
                {"diagnosis": "Other intracranial pathology", "confidence": 0.40, "priority": "exclude"},
            ],
            workup=[
                "Immediate non-contrast CT head",
                "MRI brain when stable / per stroke pathway",
                "NIH Stroke Scale and full stroke evaluation",
                "ECG, telemetry, and basic labs",
            ],
            referral={
                "recommended_disposition": "Emergency evaluation immediately",
                "specialty": "Emergency medicine / stroke team / neurology",
                "urgency": "emergent",
                "reason": "Focal neurologic deficit with cognitive change requires urgent stroke evaluation.",
            },
            codes=[
                {"system": "ICD-10", "code": "I63.9", "description": "Cerebral infarction, unspecified"},
                {"system": "SNOMED", "code": "230690007", "description": "Cerebrovascular accident"},
            ],
            rationale=["Neurologic red flags (weakness / speech change / facial droop) detected with cognitive complaint."],
        )

    # -------------------------
    # Delirium pattern
    # -------------------------
    if (
        "sudden confusion" in text
        or "uti" in text
        or "infection" in text
        or "fluctuating mental status" in text
    ):
        return _make_response(
            primary_label="Delirium / acute encephalopathy",
            confidence=0.78,
            urgency="urgent",
            differential=[
                {"diagnosis": "Delirium", "confidence": 0.78, "priority": "high"},
                {"diagnosis": "Infection-related encephalopathy", "confidence": 0.60, "priority": "high"},
                {"diagnosis": "Medication-induced confusion", "confidence": 0.45, "priority": "consider"},
            ],
            workup=[
                "CBC",
                "CMP",
                "Urinalysis",
                "Medication review (anticholinergics, sedatives, opioids)",
                "Targeted infectious workup",
            ],
            referral={
                "recommended_disposition": "Urgent medical evaluation",
                "specialty": "Primary care / hospital medicine; ED if unstable",
                "urgency": "urgent",
                "reason": "Acute fluctuating confusion suggests delirium; identify and treat underlying cause.",
            },
            codes=[
                {"system": "ICD-10", "code": "F05", "description": "Delirium due to known physiological condition"},
                {"system": "SNOMED", "code": "2776000", "description": "Delirium"},
            ],
            rationale=["Acute fluctuating confusion or infectious trigger suggests delirium."],
        )

    # -------------------------
    # Alzheimer / progressive dementia pattern
    # -------------------------
    if (
        "progressive" in text
        or "repetitive questioning" in text
        or "difficulty managing finances" in text
    ):
        return _make_response(
            primary_label="Progressive cognitive decline (Alzheimer-type pattern)",
            confidence=0.72,
            urgency="routine",
            differential=[
                {"diagnosis": "Alzheimer disease", "confidence": 0.72, "priority": "high"},
                {"diagnosis": "Mild cognitive impairment", "confidence": 0.55, "priority": "consider"},
                {"diagnosis": "Vascular dementia", "confidence": 0.45, "priority": "consider"},
            ],
            workup=[
                "CBC",
                "CMP",
                "TSH",
                "Vitamin B12",
                "MRI brain",
                "Formal cognitive testing (MoCA / MMSE)",
            ],
            referral={
                "recommended_disposition": "Outpatient neurology / memory clinic referral",
                "specialty": "Neurology / memory clinic",
                "urgency": "routine",
                "reason": "Progressive functional and memory decline warrants structured cognitive evaluation.",
            },
            codes=[
                {"system": "ICD-10", "code": "G30.9", "description": "Alzheimer's disease, unspecified"},
                {"system": "ICD-10", "code": "F03.90", "description": "Unspecified dementia without behavioral disturbance"},
                {"system": "SNOMED", "code": "26929004", "description": "Alzheimer's disease"},
            ],
            rationale=["Progressive cognitive decline pattern detected."],
        )

    # -------------------------
    # Depression pseudodementia
    # -------------------------
    if (
        "depression" in text
        or "bereavement" in text
        or "poor concentration" in text
    ):
        return _make_response(
            primary_label="Mood-related cognitive impairment",
            confidence=0.65,
            urgency="routine",
            differential=[
                {"diagnosis": "Depression-related cognitive impairment", "confidence": 0.65, "priority": "high"},
                {"diagnosis": "Mild cognitive impairment", "confidence": 0.45, "priority": "consider"},
                {"diagnosis": "Anxiety-related concentration impairment", "confidence": 0.40, "priority": "consider"},
            ],
            workup=[
                "Depression screening (PHQ-9)",
                "Medication review",
                "Basic labs (CBC, CMP, TSH, B12)",
            ],
            referral={
                "recommended_disposition": "Primary care / behavioral health referral",
                "specialty": "Primary care / behavioral health",
                "urgency": "routine",
                "reason": "Mood symptoms can mimic or contribute to cognitive impairment; treat and reassess.",
            },
            codes=[
                {"system": "ICD-10", "code": "F32.A", "description": "Depression, unspecified"},
                {"system": "SNOMED", "code": "35489007", "description": "Depressive disorder"},
            ],
            rationale=["Mood-related contributors detected."],
        )

    # -------------------------
    # General fallback
    # -------------------------
    return _make_response(
        primary_label="Cognitive impairment requiring further classification",
        confidence=0.55,
        urgency="routine",
        differential=[
            {"diagnosis": "Cognitive impairment, unspecified", "confidence": 0.55, "priority": "consider"},
            {"diagnosis": "Dementia syndrome", "confidence": 0.45, "priority": "consider"},
            {"diagnosis": "Reversible / metabolic cause", "confidence": 0.40, "priority": "screen"},
        ],
        workup=[
            "CBC",
            "CMP",
            "TSH",
            "Vitamin B12",
        ],
        referral={
            "recommended_disposition": "Neurology follow-up",
            "specialty": "Neurology / primary care",
            "urgency": "routine",
            "reason": "Cognitive complaint requires baseline workup and further classification.",
        },
        codes=[
            {"system": "ICD-10", "code": "R41.9", "description": "Unspecified symptoms and signs involving cognitive functions and awareness"},
            {"system": "SNOMED", "code": "386807006", "description": "Impaired cognition"},
        ],
        rationale=["General cognitive impairment pathway triggered."],
    )
