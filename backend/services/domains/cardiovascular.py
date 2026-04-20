from __future__ import annotations

from backend.schemas.diagnostic import AnalyzeRequest, AnalyzeResponse
from backend.services.utils.common import (
    contains_any,
    extract_history_text,
    extract_symptom_text,
)


CHEST_PAIN_TERMS = {
    "chest pain",
    "chest pressure",
    "angina",
    "tightness",
    "pressure",
    "left arm pain",
}

ACS_HIGH_RISK_TERMS = {
    "diaphoresis",
    "sweating",
    "shortness of breath",
    "sob",
    "radiation to arm",
    "jaw pain",
    "exertional",
    "nausea",
}

PE_TERMS = {
    "pleuritic pain",
    "hemoptysis",
    "tachycardia",
    "leg swelling",
    "recent travel",
    "immobility",
}

CARDIO_HISTORY_TERMS = {
    "hypertension",
    "hyperlipidemia",
    "diabetes",
    "smoker",
    "coronary artery disease",
    "cad",
    "family history of mi",
}



def analyze_cardiovascular_case(payload: AnalyzeRequest) -> AnalyzeResponse | None:
    symptom_text = extract_symptom_text(payload)
    history_text = extract_history_text(payload)

    if not contains_any(symptom_text, CHEST_PAIN_TERMS):
        return None

    acs_score = 0
    pe_score = 0
    musculoskeletal_score = 0
    reflux_score = 0

    if contains_any(symptom_text, CHEST_PAIN_TERMS):
        acs_score += 3
        musculoskeletal_score += 1
        reflux_score += 1

    if contains_any(symptom_text, ACS_HIGH_RISK_TERMS):
        acs_score += 4

    if contains_any(history_text, CARDIO_HISTORY_TERMS):
        acs_score += 3

    if contains_any(symptom_text, PE_TERMS) or contains_any(history_text, PE_TERMS):
        pe_score += 4

    if "reproducible" in symptom_text or "movement" in symptom_text:
        musculoskeletal_score += 3

    if "burning" in symptom_text or "after meals" in symptom_text or "reflux" in history_text:
        reflux_score += 3

    differentials = [
        {
            "name": "Acute coronary syndrome",
            "confidence": min(95, 40 + acs_score * 8),
            "rationale": "Chest pain with cardiovascular risk profiling and associated symptom review raises concern for ACS.",
        },
        {
            "name": "Pulmonary embolism",
            "confidence": min(90, 15 + pe_score * 10),
            "rationale": "Pleuritic features, dyspnea, tachycardia, and thromboembolic risk indicators increase PE concern.",
        },
        {
            "name": "Costochondritis / musculoskeletal chest pain",
            "confidence": min(80, 10 + musculoskeletal_score * 10),
            "rationale": "Pain reproducibility or movement-related symptoms can support musculoskeletal etiologies.",
        },
        {
            "name": "GERD / esophageal pain",
            "confidence": min(75, 10 + reflux_score * 10),
            "rationale": "Burning discomfort, meal association, or reflux history may suggest esophageal sources.",
        },
    ]

    differentials = sorted(differentials, key=lambda x: x["confidence"], reverse=True)

    urgent = differentials[0]["name"] in {"Acute coronary syndrome", "Pulmonary embolism"} and differentials[0]["confidence"] >= 50

    return AnalyzeResponse(
        summary="Cardiovascular chest-pain pathway triggered.",
        differentials=differentials,
        workup=[
            "Obtain vital signs and focused cardiovascular/respiratory exam.",
            "ECG and troponin testing for suspected ACS.",
            "Chest imaging as clinically indicated.",
            "Consider D-dimer or CT pulmonary angiography when PE risk is supported.",
        ],
        referral={
            "specialty": "Emergency evaluation" if urgent else "Cardiology / Primary Care",
            "urgency": "emergent" if urgent else "urgent outpatient",
            "reason": "Potential high-risk cardiopulmonary causes of chest pain require rapid exclusion.",
        },
        codes={
            "icd10": ["R07.9", "I20.9", "I24.9"],
            "snomed": ["29857009", "194828000", "394659003"],
            "cpt": ["93000", "84484"],
        },
        rationale=[
            "The cardiovascular module prioritized can’t-miss diagnoses before lower-risk causes.",
            "Confidence values are heuristic starter scores and should be replaced with your validated RealDiag logic.",
        ],
    )
