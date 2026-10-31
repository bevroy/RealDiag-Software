"""Medication review section of the encounter assessment: the medication safety service and
the medication-history analysis run on the chart's data (rules only)."""
from backend.services.fhir_client import PatientData
from backend.services.medication_review import medication_review
from backend.services.patient_history_service import ComprehensivePatientHistory

OK = {k: "retrieved" for k in ("labs", "vitals", "conditions", "medications", "allergies")}


def med(name):
    return {"medicationCodeableConcept": {"text": name}}


def coded(text):
    return {"code": {"text": text}}


def patient(meds=(), conditions=(), allergies=(), age=70, status=None):
    return PatientData(patient_id="p", name="T", age=age, gender="female", labs=[], vitals=[],
                       conditions=list(conditions), medications=list(meds), allergies=list(allergies),
                       retrieval_status=dict(OK, **(status or {})))


def history(records=(), status="retrieved"):
    return ComprehensivePatientHistory(patient_id="p", patient_name="T", medication_history=list(records),
                                       retrieval_status={"medications": status})


def test_interaction_between_active_medications():
    review = medication_review(patient(meds=[med("Warfarin 5 mg"), med("Aspirin 81 mg")]), history(), "retrieved")
    alert = next(a for a in review["alerts"] if a["type"] == "drug_interaction")
    assert {alert["medication"], alert["other"]} == {"warfarin 5 mg", "aspirin 81 mg"}
    assert alert["severity"] == "major" and alert["data_sources"] == ["Medication list"]
    assert review["medications"] == ["Warfarin 5 mg", "Aspirin 81 mg"]


def test_contraindication_with_the_problem_list():
    review = medication_review(patient(meds=[med("Metoprolol 50 mg")], conditions=[coded("Asthma")]),
                               history(), "retrieved")
    alert = next(a for a in review["alerts"] if a["type"] == "contraindication")
    assert alert["other"] == "asthma" and alert["data_sources"] == ["Medication list", "Problem list"]


def test_prior_adverse_reaction_from_the_medication_history():
    records = [{"name": "lisinopril 10 mg", "status": "stopped", "date_stopped": "2026-01-09",
                "date_stopped_source": "dosageInstruction.timing.repeat.boundsPeriod.end",
                "stop_reason": "Allergy: angioedema"},
               {"name": "amlodipine 5 mg", "status": "completed", "date_stopped": "2025-05-01", "stop_reason": None}]
    review = medication_review(patient(meds=[med("Losartan 50 mg")]), history(records), "retrieved")
    assert review["history"]["prior_adverse_reactions"] == [{
        "medication": "lisinopril 10 mg", "stopped": "2026-01-09", "reason": "Allergy: angioedema",
        "source": "MedicationRequest.statusReason, dosageInstruction.timing.repeat.boundsPeriod.end"}]
    assert review["history"]["stopped_medications_on_file"] == 2


def test_missing_data_is_not_checked_not_clear():
    review = medication_review(patient(meds=[med("Warfarin 5 mg")], status={"medications": "failed"}),
                               history(), "retrieved")
    assert review["alerts"] == [] and review["not_checked"] == [
        "The medication list could not be retrieved; medications were not reviewed."]
    review = medication_review(patient(meds=[med("Warfarin 5 mg")], status={"allergies": "not available"}, age=None),
                               None, None)
    assert "Allergies could not be retrieved; allergy cross-reactivity was not checked." in review["not_checked"]
    assert "Age is unknown; age-specific warnings were not checked." in review["not_checked"]
    assert any("medication history could not be retrieved" in n for n in review["not_checked"])
    assert review["history"] is None
