"""
RealDiag concussion / mild traumatic brain injury domain module.

Drop-in location:
    backend/services/domains/concussion.py

Expected interface:
    evaluate_concussion(payload, normalized_text) -> dict | None

This module is intentionally rule-based and transparent so it can be refined
with RealDiag's validated clinical pathways over time.

Note: returns a plain ``dict`` (not the pydantic ``AnalyzeResponse``) to stay
consistent with the other domain modules in this repo (``first_seizure``,
``headache``), whose output shape differs from the strict ``AnalyzeResponse``
schema. The orchestrator passes the dict through to FastAPI for serialization.
"""

from __future__ import annotations

from typing import Any


def _contains_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def _count_matches(text: str, terms: list[str]) -> int:
    return sum(1 for term in terms if term in text)


def evaluate_concussion(payload: Any, normalized_text: str) -> dict[str, Any] | None:
    """Evaluate concussion / mild TBI patterns from normalized clinical text.

    Returns a structured dict when the case strongly resembles concussion,
    post-concussive syndrome, or traumatic intracranial red-flag concern.
    Returns ``None`` when the module should not handle the case.
    """

    text = normalized_text.lower()

    trauma_terms = [
        "head injury",
        "hit head",
        "head trauma",
        "fell and hit",
        "fall with head strike",
        "motor vehicle accident",
        "mva",
        "collision",
        "sports injury",
        "football injury",
        "soccer injury",
        "concussion",
        "mild traumatic brain injury",
        "mild tbi",
        "tbi",
        "whiplash",
    ]

    concussion_features = [
        "headache",
        "dizziness",
        "nausea",
        "vomiting",
        "photophobia",
        "phonophobia",
        "light sensitivity",
        "sound sensitivity",
        "confusion",
        "foggy",
        "brain fog",
        "difficulty concentrating",
        "memory problem",
        "amnesia",
        "sleep disturbance",
        "fatigue",
        "balance problem",
        "blurred vision",
        "irritability",
    ]

    red_flags = [
        "worsening headache",
        "repeated vomiting",
        "persistent vomiting",
        "seizure",
        "focal weakness",
        "weakness",
        "numbness",
        "slurred speech",
        "unequal pupils",
        "altered mental status",
        "persistent confusion",
        "loss of consciousness",
        "loc",
        "anticoagulant",
        "blood thinner",
        "warfarin",
        "apixaban",
        "rivaroxaban",
        "clopidogrel",
        "elderly",
        "age over 65",
        "skull fracture",
        "clear fluid from nose",
        "clear fluid from ear",
    ]

    post_concussion_terms = [
        "persistent symptoms",
        "weeks after",
        "months after",
        "post concussion",
        "post-concussion",
        "postconcussive",
        "ongoing headache",
        "ongoing dizziness",
        "continued symptoms",
    ]

    has_trauma = _contains_any(text, trauma_terms)
    feature_count = _count_matches(text, concussion_features)
    red_flag_count = _count_matches(text, red_flags)
    is_post_concussion = _contains_any(text, post_concussion_terms)

    # Avoid over-routing generic headache/dizziness cases without trauma signal.
    if not has_trauma and not is_post_concussion:
        return None

    if feature_count == 0 and not red_flag_count:
        return None

    emergency = red_flag_count >= 1
    confidence = min(92, 62 + (feature_count * 5) + (10 if has_trauma else 0) + (8 if is_post_concussion else 0))

    differentials: list[dict[str, Any]] = []

    if emergency:
        differentials.append(
            {
                "diagnosis": "Traumatic intracranial injury / complicated mild TBI concern",
                "confidence": min(94, confidence + 5),
                "rationale": "Head trauma with red-flag features requires urgent evaluation for intracranial hemorrhage, skull fracture, or other complicated traumatic brain injury.",
            }
        )

    differentials.append(
        {
            "diagnosis": "Concussion / mild traumatic brain injury",
            "confidence": confidence,
            "rationale": "Head trauma plus acute symptoms such as headache, dizziness, nausea, confusion, memory disturbance, or sensory sensitivity supports concussion/mild TBI.",
        }
    )

    if is_post_concussion:
        differentials.append(
            {
                "diagnosis": "Persistent post-concussive symptoms",
                "confidence": max(70, confidence - 5),
                "rationale": "Ongoing cognitive, vestibular, sleep, mood, or headache symptoms after concussion suggest persistent post-concussive syndrome.",
            }
        )

    differentials.extend(
        [
            {
                "diagnosis": "Cervicogenic headache / whiplash-associated disorder",
                "confidence": 48,
                "rationale": "Neck strain or whiplash after trauma can overlap with post-concussive headache and dizziness.",
            },
            {
                "diagnosis": "Vestibular dysfunction after head injury",
                "confidence": 45,
                "rationale": "Dizziness, imbalance, or visual-motion sensitivity after head injury may reflect vestibular involvement.",
            },
        ]
    )

    if emergency:
        urgency = "Emergency evaluation"
        referral = "Emergency department / urgent neurotrauma evaluation; consider neurology or neurosurgery depending on imaging and clinical findings."
        workup = [
            "Immediate neurologic assessment including mental status, cranial nerves, motor/sensory exam, gait, and pupils.",
            "Assess Glasgow Coma Scale, loss of consciousness, amnesia, vomiting, anticoagulant use, age-related risk, and mechanism of injury.",
            "Non-contrast head CT if red flags, high-risk mechanism, anticoagulant use, focal neurologic deficits, seizure, persistent altered mental status, or worsening symptoms are present.",
            "Cervical spine assessment and imaging if neck pain, high-risk mechanism, neurologic deficit, or concerning exam.",
            "Medication review for anticoagulants/antiplatelets and bleeding risk.",
        ]
    else:
        urgency = "Outpatient management with clear return precautions"
        referral = "Primary care or sports medicine follow-up; neurology, concussion clinic, vestibular therapy, or neuropsychology if symptoms persist or impair function."
        workup = [
            "Focused neurologic exam, cognitive screen, balance/vestibular assessment, ocular-motor assessment, and symptom inventory.",
            "No routine neuroimaging for uncomplicated concussion without red flags; image if clinical risk features develop.",
            "Provide return precautions for worsening headache, repeated vomiting, seizure, confusion, focal deficits, severe drowsiness, or behavioral change.",
            "Recommend brief relative rest followed by gradual return to cognitive and physical activity as tolerated.",
            "Assess return-to-work, return-to-school, return-to-play, sleep, mood, and vestibular symptoms.",
        ]

    codes = [
        {"system": "ICD-10-CM", "code": "S06.0X0A", "description": "Concussion without loss of consciousness, initial encounter"},
        {"system": "ICD-10-CM", "code": "S06.0X9A", "description": "Concussion with loss of consciousness of unspecified duration, initial encounter"},
        {"system": "ICD-10-CM", "code": "F07.81", "description": "Postconcussional syndrome"},
        {"system": "SNOMED CT", "code": "110030002", "description": "Concussion injury of brain"},
    ]

    return {
        "primary_assessment": (
            "Traumatic intracranial injury / complicated mild TBI concern"
            if emergency
            else (
                "Persistent post-concussive symptoms"
                if is_post_concussion
                else "Concussion / mild traumatic brain injury"
            )
        ),
        "confidence": round(confidence / 100, 2),
        "urgency": "emergent" if emergency else ("subacute" if is_post_concussion else "outpatient"),
        "differential": differentials,
        "workup": workup,
        "referral": {
            "recommended_disposition": urgency,
            "specialty": referral,
            "urgency": "emergent" if emergency else "routine",
            "reason": (
                "Red-flag head trauma features require urgent neuroimaging and evaluation."
                if emergency
                else "Symptom-directed concussion management with return precautions."
            ),
        },
        "codes": codes,
        "rationale": [
            f"Matched trauma signal: {has_trauma}",
            f"Concussion feature count: {feature_count}",
            f"Red flag count: {red_flag_count}",
            f"Persistent/post-concussive signal: {is_post_concussion}",
        ],
        "disclaimer": "Clinical decision-support output only; not a substitute for clinician judgment or emergency care.",
    }
