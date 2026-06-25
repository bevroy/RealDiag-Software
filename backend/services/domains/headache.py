"""
RealDiag Headache / TAC / Trigeminal Neuralgia Domain Module

Purpose:
    Evaluates headache presentations and returns structured diagnostic-support output
    for high-yield headache conditions, including:
      - thunderclap / subarachnoid hemorrhage concern
      - migraine
      - cluster headache / trigeminal autonomic cephalalgia (TAC)
      - trigeminal neuralgia
      - temporal arteritis / giant cell arteritis concern
      - meningitis / encephalitis concern
      - secondary headache red flags

Clinical safety note:
    This module is for clinical decision support prototyping and workflow logic.
    It does not replace clinician judgment or emergency evaluation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def _get_field(payload: Any, name: str, default: Any = None) -> Any:
    if hasattr(payload, name):
        return getattr(payload, name)
    if isinstance(payload, dict):
        return payload.get(name, default)
    return default


def _contains_any(text: str, terms: List[str]) -> bool:
    return any(term in text for term in terms)


def _score_terms(text: str, terms: List[str], weight: int = 1) -> int:
    return sum(weight for term in terms if term in text)


def _make_response(
    *,
    primary_label: str,
    confidence: float,
    urgency: str,
    differential: List[Dict[str, Any]],
    workup: List[str],
    referral: Dict[str, Any],
    codes: List[Dict[str, str]],
    rationale: List[str],
) -> Any:
    """Return dict compatible with common RealDiag starter schemas.

    If your AnalyzeResponse schema uses field names that differ, adjust this function
    once rather than changing every rule below.
    """
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


def evaluate_headache(payload: Any, normalized_text: str) -> Optional[Dict[str, Any]]:
    """Evaluate headache-related presentations.

    Args:
        payload: AnalyzeRequest-like object or dict.
        normalized_text: lowercased normalized clinical input string.

    Returns:
        structured response dict if headache pattern detected; otherwise None.
    """

    text = (normalized_text or "").lower()
    age = _get_field(payload, "age")

    headache_terms = [
        "headache", "head pain", "cephalgia", "migraine", "cluster", "tac",
        "trigeminal neuralgia", "facial pain", "temporal pain", "thunderclap",
    ]
    if not _contains_any(text, headache_terms):
        return None

    rationale: List[str] = []

    # Red flags / secondary headache signals
    thunderclap = _contains_any(text, ["thunderclap", "worst headache", "sudden onset", "maximal at onset", "explosive onset"])
    neuro_deficit = _contains_any(text, ["weakness", "numbness", "aphasia", "slurred speech", "vision loss", "diplopia", "focal deficit", "confusion", "altered mental status"])
    fever_meningismus = _contains_any(text, ["fever", "neck stiffness", "meningismus", "rash", "photophobia with fever", "encephalitis", "meningitis"])
    pregnancy_postpartum = _contains_any(text, ["pregnant", "pregnancy", "postpartum", "preeclampsia", "eclampsia"])
    cancer_immunosuppression = _contains_any(text, ["cancer", "malignancy", "immunosuppressed", "hiv", "transplant", "chemotherapy"])
    trauma_anticoag = _contains_any(text, ["trauma", "fall", "head injury", "anticoagulant", "warfarin", "apixaban", "rivaroxaban", "heparin"])
    age_over_50 = bool(age and isinstance(age, (int, float)) and age >= 50) or _contains_any(text, ["age 50", "over 50", "older adult", "elderly"])
    new_progressive = _contains_any(text, ["new headache", "new onset", "progressive", "worsening", "changed pattern", "new pattern"])

    # Syndrome-specific signals
    migraine_score = _score_terms(text, ["migraine", "unilateral", "pulsating", "throbbing", "photophobia", "phonophobia", "nausea", "vomiting", "aura", "worse with activity"])
    cluster_score = _score_terms(text, ["cluster", "periorbital", "orbital", "unilateral", "tearing", "lacrimation", "rhinorrhea", "nasal congestion", "ptosis", "miosis", "restlessness", "circadian", "attacks", "15 minutes", "180 minutes"])
    tn_score = _score_terms(text, ["trigeminal neuralgia", "electric shock", "shock-like", "stabbing facial pain", "triggered by touch", "chewing", "brushing teeth", "talking", "v2", "v3", "facial pain"])
    gca_score = _score_terms(text, ["temporal arteritis", "giant cell", "scalp tenderness", "jaw claudication", "vision loss", "temporal pain", "elevated esr", "elevated crp"])

    # Emergency secondary headache branch first.
    if thunderclap or neuro_deficit or fever_meningismus or pregnancy_postpartum or trauma_anticoag:
        if thunderclap:
            rationale.append("Thunderclap or sudden maximal-onset headache is a high-risk secondary headache signal.")
        if neuro_deficit:
            rationale.append("Focal neurologic symptoms or altered mental status require urgent secondary-cause evaluation.")
        if fever_meningismus:
            rationale.append("Fever, meningismus, or infectious symptoms raise concern for meningitis/encephalitis.")
        if pregnancy_postpartum:
            rationale.append("Pregnancy/postpartum headache can reflect hypertensive, vascular, or thrombotic emergencies.")
        if trauma_anticoag:
            rationale.append("Trauma or anticoagulant use increases concern for intracranial hemorrhage.")

        differential = [
            {"diagnosis": "Secondary headache requiring urgent evaluation", "confidence": 0.88, "priority": "emergent"},
            {"diagnosis": "Subarachnoid hemorrhage / intracranial hemorrhage", "confidence": 0.76 if thunderclap or trauma_anticoag else 0.58, "priority": "must-not-miss"},
            {"diagnosis": "Meningitis / encephalitis", "confidence": 0.72 if fever_meningismus else 0.40, "priority": "must-not-miss"},
            {"diagnosis": "Cerebrovascular event / venous sinus thrombosis", "confidence": 0.66 if neuro_deficit or pregnancy_postpartum else 0.45, "priority": "must-not-miss"},
            {"diagnosis": "Migraine or primary headache disorder", "confidence": 0.30, "priority": "lower after red flags excluded"},
        ]
        workup = [
            "Immediate vital signs and focused neurologic examination.",
            "Emergency evaluation if thunderclap onset, focal deficit, fever/meningismus, pregnancy/postpartum state, trauma, or anticoagulant use is present.",
            "Non-contrast head CT when hemorrhage or acute intracranial process is a concern.",
            "CTA/CTV or MRI/MRA/MRV as clinically indicated for vascular causes or venous sinus thrombosis.",
            "Lumbar puncture if infection or subarachnoid hemorrhage remains a concern after initial imaging, per clinician judgment.",
            "CBC, CMP, coagulation studies, pregnancy test when applicable; ESR/CRP if giant cell arteritis is plausible.",
        ]
        referral = {
            "recommended_disposition": "Emergency evaluation",
            "specialty": "Emergency medicine / neurology; neurosurgery or infectious disease depending on findings",
            "urgency": "emergent",
            "reason": "Red-flag headache features require urgent exclusion of secondary causes.",
        }
        codes = [
            {"system": "ICD-10", "code": "R51.9", "description": "Headache, unspecified"},
            {"system": "ICD-10", "code": "I60.9", "description": "Nontraumatic subarachnoid hemorrhage, unspecified"},
            {"system": "SNOMED", "code": "25064002", "description": "Headache"},
        ]
        return _make_response(
            primary_label="Red-flag headache / secondary headache concern",
            confidence=0.88,
            urgency="emergent",
            differential=differential,
            workup=workup,
            referral=referral,
            codes=codes,
            rationale=rationale,
        )

    # Giant cell arteritis branch
    if (age_over_50 and new_progressive) or gca_score >= 2:
        rationale.append("Age over 50 with new/progressive temporal headache pattern raises concern for giant cell arteritis.")
        if gca_score >= 2:
            rationale.append("Matched features such as scalp tenderness, jaw claudication, temporal pain, or visual symptoms support GCA consideration.")
        return _make_response(
            primary_label="Giant cell arteritis concern",
            confidence=0.78,
            urgency="urgent",
            differential=[
                {"diagnosis": "Giant cell arteritis / temporal arteritis", "confidence": 0.78, "priority": "urgent"},
                {"diagnosis": "Migraine or primary headache disorder", "confidence": 0.42, "priority": "consider after secondary causes"},
                {"diagnosis": "Intracranial mass or other secondary headache", "confidence": 0.35, "priority": "evaluate based on exam/history"},
            ],
            workup=[
                "ESR and CRP urgently when GCA is suspected.",
                "CBC and CMP as baseline labs.",
                "Assess for jaw claudication, scalp tenderness, visual symptoms, polymyalgia rheumatica symptoms.",
                "Urgent ophthalmology/rheumatology evaluation if visual symptoms or high clinical concern.",
                "Temporal artery ultrasound/biopsy or vascular imaging per local pathway.",
            ],
            referral={
                "recommended_disposition": "Urgent specialty evaluation",
                "specialty": "Rheumatology and ophthalmology; emergency evaluation for visual symptoms",
                "urgency": "urgent",
                "reason": "Vision-threatening vasculitis must be evaluated rapidly.",
            },
            codes=[
                {"system": "ICD-10", "code": "M31.6", "description": "Other giant cell arteritis"},
                {"system": "ICD-10", "code": "R51.9", "description": "Headache, unspecified"},
                {"system": "SNOMED", "code": "414341000", "description": "Giant cell arteritis"},
            ],
            rationale=rationale,
        )

    # Trigeminal neuralgia branch
    if tn_score >= 2:
        rationale.append("Paroxysmal electric/shock-like facial pain with triggers is suggestive of trigeminal neuralgia.")
        return _make_response(
            primary_label="Trigeminal neuralgia pattern",
            confidence=0.82,
            urgency="routine-to-urgent depending on severity or atypical features",
            differential=[
                {"diagnosis": "Trigeminal neuralgia", "confidence": 0.82, "priority": "high"},
                {"diagnosis": "Dental/TMJ pathology", "confidence": 0.38, "priority": "alternative"},
                {"diagnosis": "Secondary trigeminal neuropathy", "confidence": 0.34, "priority": "evaluate if sensory deficit, bilateral symptoms, young age, or atypical features"},
            ],
            workup=[
                "Characterize pain distribution, duration, triggers, refractory period, and sensory findings.",
                "Focused cranial nerve examination including facial sensation and corneal reflex if clinically appropriate.",
                "Brain MRI with attention to trigeminal nerve pathway if atypical features, neurologic deficits, young onset, bilateral symptoms, or pre-procedural evaluation.",
                "Dental/TMJ assessment if symptoms overlap with odontogenic pain.",
            ],
            referral={
                "recommended_disposition": "Neurology referral",
                "specialty": "Neurology; neurosurgery/pain specialist if refractory",
                "urgency": "routine-to-urgent",
                "reason": "Pattern is consistent with cranial neuralgia and may require targeted therapy and imaging depending on features.",
            },
            codes=[
                {"system": "ICD-10", "code": "G50.0", "description": "Trigeminal neuralgia"},
                {"system": "SNOMED", "code": "31681005", "description": "Trigeminal neuralgia"},
            ],
            rationale=rationale,
        )

    # Cluster/TAC branch
    if cluster_score >= 3 or "cluster headache" in text or "trigeminal autonomic" in text:
        rationale.append("Strictly unilateral orbital/periorbital pain with autonomic signs suggests cluster headache or TAC spectrum.")
        return _make_response(
            primary_label="Cluster headache / trigeminal autonomic cephalalgia pattern",
            confidence=0.80,
            urgency="urgent outpatient unless atypical/red flags",
            differential=[
                {"diagnosis": "Cluster headache", "confidence": 0.80, "priority": "high"},
                {"diagnosis": "Other trigeminal autonomic cephalalgia", "confidence": 0.62, "priority": "consider"},
                {"diagnosis": "Migraine", "confidence": 0.42, "priority": "alternative"},
                {"diagnosis": "Secondary orbital/cavernous sinus process", "confidence": 0.25, "priority": "exclude if atypical features"},
            ],
            workup=[
                "Confirm attack duration, frequency, laterality, orbital/periorbital location, and autonomic symptoms.",
                "Assess for ptosis, miosis, lacrimation, rhinorrhea, nasal congestion, agitation/restlessness.",
                "Screen for red flags or atypical features that should prompt neuroimaging.",
                "Consider brain MRI/MRA if first presentation, atypical features, abnormal examination, or concern for secondary TAC mimic.",
            ],
            referral={
                "recommended_disposition": "Neurology referral",
                "specialty": "Neurology/headache specialist",
                "urgency": "urgent outpatient",
                "reason": "TAC patterns often require prompt diagnosis and targeted acute/preventive strategy.",
            },
            codes=[
                {"system": "ICD-10", "code": "G44.0", "description": "Cluster headache syndrome"},
                {"system": "SNOMED", "code": "193031009", "description": "Cluster headache"},
            ],
            rationale=rationale,
        )

    # Migraine / primary headache branch
    if migraine_score >= 3 or "migraine" in text:
        rationale.append("Photophobia/phonophobia, nausea, aura, unilateral throbbing pain, or activity worsening supports migraine pattern.")
        return _make_response(
            primary_label="Migraine / primary headache pattern",
            confidence=0.74,
            urgency="routine unless red flags develop",
            differential=[
                {"diagnosis": "Migraine", "confidence": 0.74, "priority": "high"},
                {"diagnosis": "Tension-type headache", "confidence": 0.40, "priority": "alternative"},
                {"diagnosis": "Cluster headache/TAC", "confidence": 0.28, "priority": "consider if autonomic unilateral attacks"},
                {"diagnosis": "Secondary headache", "confidence": 0.20, "priority": "screen with red flags"},
            ],
            workup=[
                "Screen for red flags: thunderclap onset, neurologic deficit, fever/meningismus, cancer/immunosuppression, pregnancy/postpartum, trauma, anticoagulants, new headache after age 50, or progressive pattern.",
                "Characterize frequency, disability, aura symptoms, triggers, medication use, and prior response to therapy.",
                "Neuroimaging is generally guided by red flags, abnormal neurologic examination, or atypical headache features.",
                "Review medication-overuse risk if frequent analgesic or triptan use.",
            ],
            referral={
                "recommended_disposition": "Primary care management or neurology referral depending on severity/frequency",
                "specialty": "Neurology/headache specialist if frequent, disabling, atypical, refractory, or diagnostically uncertain",
                "urgency": "routine",
                "reason": "Primary headache pattern without emergency red flags.",
            },
            codes=[
                {"system": "ICD-10", "code": "G43.909", "description": "Migraine, unspecified, not intractable, without status migrainosus"},
                {"system": "ICD-10", "code": "R51.9", "description": "Headache, unspecified"},
                {"system": "SNOMED", "code": "37796009", "description": "Migraine"},
            ],
            rationale=rationale,
        )

    # General headache fallback when headache detected but not classifiable.
    rationale.append("Headache-related presentation detected, but available features are insufficient for a specific syndrome classification.")
    if cancer_immunosuppression or new_progressive:
        rationale.append("Cancer, immunosuppression, new onset, or progressive pattern may warrant lower threshold for imaging or urgent evaluation.")

    return _make_response(
        primary_label="Headache syndrome requiring classification",
        confidence=0.55,
        urgency="routine-to-urgent based on red flags",
        differential=[
            {"diagnosis": "Primary headache disorder", "confidence": 0.55, "priority": "consider"},
            {"diagnosis": "Migraine", "confidence": 0.42, "priority": "consider"},
            {"diagnosis": "Tension-type headache", "confidence": 0.38, "priority": "consider"},
            {"diagnosis": "Secondary headache", "confidence": 0.32, "priority": "screen carefully"},
        ],
        workup=[
            "Clarify onset, peak intensity, duration, frequency, laterality, associated neurologic symptoms, systemic symptoms, and triggers.",
            "Perform focused neurologic examination and vital signs.",
            "Screen for red flags requiring urgent evaluation or neuroimaging.",
            "Consider headache diary and medication-overuse assessment for recurrent presentations.",
        ],
        referral={
            "recommended_disposition": "Primary care or neurology depending on severity and red flags",
            "specialty": "Neurology/headache specialist if atypical, refractory, frequent, or diagnostically uncertain",
            "urgency": "case-dependent",
            "reason": "Headache syndrome requires further classification and red-flag screening.",
        },
        codes=[
            {"system": "ICD-10", "code": "R51.9", "description": "Headache, unspecified"},
            {"system": "SNOMED", "code": "25064002", "description": "Headache"},
        ],
        rationale=rationale,
    )
