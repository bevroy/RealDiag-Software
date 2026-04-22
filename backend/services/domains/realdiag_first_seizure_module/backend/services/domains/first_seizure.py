from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SeizureSignals:
    score: int
    red_flags: list[str]
    provoking_factors: list[str]
    focal_features: list[str]
    recurrent_features: list[str]
    supporting_features: list[str]


SEIZURE_TERMS = {
    "seizure",
    "first seizure",
    "convulsion",
    "convulsions",
    "tonic clonic",
    "tonic-clonic",
    "generalized shaking",
    "loss of consciousness with shaking",
    "post ictal",
    "post-ictal",
    "tongue biting",
    "urinary incontinence",
    "unresponsive spell",
}

SUPPORTING_TERMS = {
    "post ictal": "post-ictal confusion",
    "post-ictal": "post-ictal confusion",
    "tongue biting": "tongue biting",
    "urinary incontinence": "urinary incontinence",
    "aura": "possible aura",
    "rhythmic jerking": "rhythmic jerking",
    "unresponsive": "episode of unresponsiveness",
}

FOCAL_TERMS = {
    "focal weakness": "focal weakness",
    "aphasia": "aphasia",
    "unilateral numbness": "unilateral numbness",
    "gaze deviation": "gaze deviation",
    "focal": "focal onset concern",
}

PROVOKING_TERMS = {
    "alcohol withdrawal": "alcohol withdrawal",
    "withdrawal": "substance/medication withdrawal",
    "sleep deprivation": "sleep deprivation",
    "hypoglycemia": "possible hypoglycemia",
    "electrolyte": "possible electrolyte disturbance",
    "fever": "fever / possible infection",
    "infection": "possible infection",
    "new medication": "new medication exposure",
    "bupropion": "bupropion exposure",
    "tramadol": "tramadol exposure",
    "head trauma": "recent head trauma",
}

RED_FLAG_TERMS = {
    "pregnant": "pregnancy",
    "pregnancy": "pregnancy",
    "immunocompromised": "immunocompromised state",
    "anticoagulant": "anticoagulant use",
    "cancer": "history of cancer",
    "fever": "fever",
    "meningismus": "meningeal signs",
    "worst headache": "severe headache",
    "thunderclap": "thunderclap headache",
    "persistent altered mental status": "persistent altered mental status",
    "focal weakness": "new focal deficit",
    "trauma": "recent trauma",
}

RECURRENT_TERMS = {
    "prior seizure": "prior seizure history",
    "epilepsy": "known epilepsy",
    "multiple episodes": "multiple episodes",
    "recurrent": "recurrent events",
}


def _contains(text: str, term: str) -> bool:
    return term in text


def detect_first_seizure_signals(text: str) -> SeizureSignals:
    score = 0
    red_flags: list[str] = []
    provoking_factors: list[str] = []
    focal_features: list[str] = []
    recurrent_features: list[str] = []
    supporting_features: list[str] = []

    for term in SEIZURE_TERMS:
        if _contains(text, term):
            score += 3

    for term, label in SUPPORTING_TERMS.items():
        if _contains(text, term) and label not in supporting_features:
            supporting_features.append(label)
            score += 1

    for term, label in FOCAL_TERMS.items():
        if _contains(text, term) and label not in focal_features:
            focal_features.append(label)
            score += 2

    for term, label in PROVOKING_TERMS.items():
        if _contains(text, term) and label not in provoking_factors:
            provoking_factors.append(label)
            score += 1

    for term, label in RED_FLAG_TERMS.items():
        if _contains(text, term) and label not in red_flags:
            red_flags.append(label)
            score += 2

    for term, label in RECURRENT_TERMS.items():
        if _contains(text, term) and label not in recurrent_features:
            recurrent_features.append(label)
            score += 1

    return SeizureSignals(
        score=score,
        red_flags=red_flags,
        provoking_factors=provoking_factors,
        focal_features=focal_features,
        recurrent_features=recurrent_features,
        supporting_features=supporting_features,
    )


def evaluate_first_seizure(payload: Any, normalized_text: str) -> dict[str, Any]:
    signals = detect_first_seizure_signals(normalized_text)

    age = getattr(payload, "age", None)
    sex = getattr(payload, "sex", None)
    symptoms = getattr(payload, "symptoms", []) or []
    history = getattr(payload, "history", []) or []

    if signals.score < 3:
        return {}

    red_flag_emergent = bool(signals.red_flags or signals.focal_features)
    concern_level = "high" if red_flag_emergent else "moderate"
    confidence = min(0.9, 0.52 + (signals.score * 0.03))

    primary_label = "First unprovoked seizure"
    if signals.provoking_factors:
        primary_label = "Possible provoked seizure"
    if signals.recurrent_features:
        primary_label = "Seizure disorder / recurrent seizure concern"

    differentials = [
        {
            "diagnosis": primary_label,
            "confidence": round(confidence, 2),
            "rationale": _build_primary_rationale(signals),
        },
        {
            "diagnosis": "Syncope with convulsive features",
            "confidence": round(max(0.18, confidence - 0.28), 2),
            "rationale": "Consider if loss of consciousness was brief with rapid recovery, clear trigger, or limited post-event confusion.",
        },
        {
            "diagnosis": "Psychogenic nonepileptic event",
            "confidence": round(max(0.12, confidence - 0.34), 2),
            "rationale": "Consider if semiology is inconsistent, prolonged, or discordant with typical epileptic features.",
        },
    ]

    if signals.provoking_factors:
        differentials.append(
            {
                "diagnosis": "Metabolic / toxic provoked seizure",
                "confidence": round(max(0.2, confidence - 0.2), 2),
                "rationale": "Provoking factors raise concern for an acute symptomatic seizure requiring directed evaluation.",
            }
        )

    workup = [
        "Detailed witness history and event timeline",
        "Complete neurologic examination",
        "Basic metabolic panel including sodium, calcium, magnesium, and glucose",
        "CBC and targeted toxicology / medication review when clinically indicated",
        "Pregnancy test when relevant",
        "12-lead ECG to help exclude arrhythmic syncope",
        "Brain MRI with epilepsy protocol",
        "EEG as part of first-seizure evaluation",
    ]

    if red_flag_emergent:
        workup.insert(0, "Urgent neuroimaging / emergency evaluation due to red-flag features")
        workup.insert(1, "Head CT if acute intracranial process is a concern")
    elif "recent head trauma" in signals.provoking_factors:
        workup.insert(0, "Neuroimaging due to recent head trauma")

    referral = {
        "specialty": "Neurology",
        "urgency": "Urgent / emergency" if red_flag_emergent else "Urgent outpatient",
        "rationale": _build_referral_rationale(signals),
    }

    codes = {
        "icd10": [
            {"code": "R56.9", "label": "Unspecified convulsions"},
            {"code": "R55", "label": "Syncope and collapse", "context": "differential"},
        ],
        "snomed": [
            {"code": "91175000", "label": "Seizure"},
            {"code": "271594007", "label": "Electroencephalography recommended", "context": "workup"},
        ],
    }

    if signals.recurrent_features:
        codes["icd10"].insert(0, {"code": "G40.909", "label": "Epilepsy, unspecified, not intractable, without status epilepticus"})
        codes["snomed"].insert(0, {"code": "84757009", "label": "Epilepsy"})

    rationale = [
        f"Input pattern is compatible with seizure-spectrum evaluation (score={signals.score}).",
        _patient_context(age=age, sex=sex, symptoms=symptoms, history=history),
    ]
    if signals.supporting_features:
        rationale.append("Supportive seizure features: " + ", ".join(signals.supporting_features) + ".")
    if signals.provoking_factors:
        rationale.append("Possible provoking factors: " + ", ".join(signals.provoking_factors) + ".")
    if signals.red_flags:
        rationale.append("Red flags supporting emergency escalation: " + ", ".join(signals.red_flags) + ".")
    if signals.focal_features:
        rationale.append("Focal features increase concern for structural or localized neurologic pathology.")

    return {
        "domain": "neurology:first_seizure",
        "concern_level": concern_level,
        "differential": differentials,
        "workup": workup,
        "referral": referral,
        "codes": codes,
        "rationale": rationale,
        "matched_signals": {
            "supporting_features": signals.supporting_features,
            "provoking_factors": signals.provoking_factors,
            "red_flags": signals.red_flags,
            "focal_features": signals.focal_features,
            "recurrent_features": signals.recurrent_features,
        },
    }


def _build_primary_rationale(signals: SeizureSignals) -> str:
    parts: list[str] = []
    if signals.supporting_features:
        parts.append("supportive seizure features present")
    if signals.provoking_factors:
        parts.append("possible provoking factor identified")
    if signals.focal_features:
        parts.append("focal features raise concern for localized pathology")
    if signals.recurrent_features:
        parts.append("history suggests recurrent events")
    if not parts:
        return "Presentation contains seizure-related terminology and should be evaluated as a seizure-spectrum event."
    return "; ".join(parts).capitalize() + "."


def _build_referral_rationale(signals: SeizureSignals) -> str:
    if signals.red_flags or signals.focal_features:
        return "Red-flag or focal features warrant emergency-level neurologic assessment and urgent workup."
    if signals.provoking_factors:
        return "Possible acute symptomatic seizure still warrants prompt neurologic review after initial stabilization and provoking-factor assessment."
    return "A first seizure generally requires prompt neurology assessment, EEG, and neuroimaging planning."


def _patient_context(age: Any, sex: Any, symptoms: list[str], history: list[str]) -> str:
    fragments: list[str] = []
    if age is not None:
        fragments.append(f"Age: {age}")
    if sex:
        fragments.append(f"Sex: {sex}")
    if symptoms:
        fragments.append("Symptoms: " + ", ".join(symptoms[:6]))
    if history:
        fragments.append("History: " + ", ".join(history[:6]))
    return " | ".join(fragments) if fragments else "Clinical context available in submitted payload."
