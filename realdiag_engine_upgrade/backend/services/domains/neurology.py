from __future__ import annotations

from backend.schemas.diagnostic import AnalyzeRequest, AnalyzeResponse
from backend.services.utils.common import (
    contains_any,
    extract_history_text,
    extract_symptom_text,
)


HEADACHE_TERMS = {
    "headache",
    "migraine",
    "cluster headache",
    "facial pain",
    "trigeminal pain",
    "head pain",
}

RED_FLAG_TERMS = {
    "thunderclap",
    "worst headache",
    "focal weakness",
    "vision loss",
    "confusion",
    "fever",
    "stiff neck",
    "new neurologic deficit",
}

SEIZURE_TERMS = {
    "seizure",
    "loss of consciousness",
    "convulsion",
    "postictal",
}

COGNITIVE_TERMS = {
    "memory loss",
    "confusion",
    "cognitive decline",
    "forgetfulness",
}



def analyze_neurology_case(payload: AnalyzeRequest) -> AnalyzeResponse | None:
    symptom_text = extract_symptom_text(payload)
    history_text = extract_history_text(payload)

    if not (
        contains_any(symptom_text, HEADACHE_TERMS)
        or contains_any(symptom_text, SEIZURE_TERMS)
        or contains_any(symptom_text, COGNITIVE_TERMS)
    ):
        return None

    emergent = contains_any(symptom_text, RED_FLAG_TERMS)
    seizure_case = contains_any(symptom_text, SEIZURE_TERMS)
    cognitive_case = contains_any(symptom_text, COGNITIVE_TERMS)

    if seizure_case:
        summary = "Neurology seizure pathway triggered."
        differentials = [
            {"name": "First unprovoked seizure", "confidence": 78, "rationale": "Reported convulsive or postictal features support seizure evaluation."},
            {"name": "Syncope", "confidence": 35, "rationale": "Transient loss of consciousness may overlap clinically and should be distinguished."},
            {"name": "Psychogenic nonepileptic event", "confidence": 22, "rationale": "Behavioral event differentials remain secondary considerations pending clinical details."},
        ]
        workup = [
            "Focused neurologic exam and vitals.",
            "Basic metabolic evaluation and glucose.",
            "Brain imaging as indicated by context and red flags.",
            "EEG and neurology follow-up.",
        ]
        referral = {
            "specialty": "Emergency evaluation" if emergent else "Neurology",
            "urgency": "emergent" if emergent else "urgent outpatient",
            "reason": "Seizure-like episodes require evaluation for structural, metabolic, and neurologic causes.",
        }
        codes = {
            "icd10": ["R56.9", "G40.909"],
            "snomed": ["91175000", "84757009"],
            "cpt": ["95816", "70551"],
        }
    elif cognitive_case:
        summary = "Neurology cognitive pathway triggered."
        differentials = [
            {"name": "Mild cognitive impairment", "confidence": 58, "rationale": "Progressive memory concerns without enough detail for major impairment may fit MCI."},
            {"name": "Delirium / secondary medical cause", "confidence": 45 if emergent else 25, "rationale": "Acute confusion or fluctuating symptoms require exclusion of secondary causes."},
            {"name": "Major neurocognitive disorder", "confidence": 42, "rationale": "Functional decline and progression would increase concern for dementing illness."},
        ]
        workup = [
            "Medication review and screening for reversible contributors.",
            "CBC, CMP, TSH, B12, and other targeted labs.",
            "Cognitive screening assessment.",
            "Brain imaging when indicated.",
        ]
        referral = {
            "specialty": "Emergency evaluation" if emergent else "Neurology / Memory Clinic",
            "urgency": "emergent" if emergent else "routine to urgent outpatient",
            "reason": "Cognitive change requires differentiation between reversible causes and neurodegenerative processes.",
        }
        codes = {
            "icd10": ["R41.3", "G31.84", "F03.90"],
            "snomed": ["386807006", "230265002", "52448006"],
            "cpt": ["96116", "70551"],
        }
    else:
        summary = "Neurology headache pathway triggered."
        differentials = [
            {"name": "Migraine", "confidence": 62, "rationale": "Primary headache syndromes remain common absent focal red flags."},
            {"name": "Cluster headache / TAC", "confidence": 40, "rationale": "Severe unilateral headache with autonomic features would raise TAC concern."},
            {"name": "Secondary headache requiring exclusion", "confidence": 55 if emergent else 25, "rationale": "Thunderclap onset, fever, meningismus, or neurologic deficits raise concern for secondary causes."},
            {"name": "Trigeminal neuralgia", "confidence": 30, "rationale": "Brief shock-like facial pain can indicate trigeminal neuralgia rather than primary headache."},
        ]
        workup = [
            "Focused neurologic exam and review of onset pattern.",
            "Assess for meningismus, vision changes, focal deficits, and systemic symptoms.",
            "Neuroimaging when red flags or atypical features are present.",
            "Targeted headache management once secondary causes are addressed.",
        ]
        referral = {
            "specialty": "Emergency evaluation" if emergent else "Neurology / Headache Specialist",
            "urgency": "emergent" if emergent else "outpatient",
            "reason": "Red-flag headache features require urgent exclusion of secondary neurologic causes.",
        }
        codes = {
            "icd10": ["R51.9", "G43.909", "G44.009", "G50.0"],
            "snomed": ["25064002", "37796009", "193031009", "31681005"],
            "cpt": ["99284", "70551"],
        }

    return AnalyzeResponse(
        summary=summary,
        differentials=differentials,
        workup=workup,
        referral=referral,
        codes=codes,
        rationale=[
            "This neurology module is a structured implementation scaffold for your previously defined RealDiag trees.",
            "Replace heuristic confidence values with your validated pathway logic and clinical thresholds.",
        ],
    )
