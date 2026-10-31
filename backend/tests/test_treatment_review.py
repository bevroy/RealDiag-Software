"""Patient-aware treatment review: each treatment line of a tree checked against the chart
(medication safety service + medication-history rules), marked appropriate / caution / avoid
with reasons and sources, never ranked."""
from datetime import datetime

from backend.services.fhir_client import LabResult, PatientData
from backend.services.patient_history_service import ComprehensivePatientHistory
from backend.services.treatment_review import (AVOID, APPROPRIATE, CAUTION, NOT_CHECKED, TreatmentReviewer,
                                               named_medications, patient_factors)

OK = {k: "retrieved" for k in ("labs", "vitals", "conditions", "medications", "allergies")}


def med(name):
    return {"medicationCodeableConcept": {"text": name}}


def coded(text):
    return {"code": {"text": text}}


def egfr(value, when=datetime(2026, 10, 1)):
    return LabResult(code="62238-1", display="eGFR", value=value, unit="mL/min/1.73m2", effective_date=when)


def patient(meds=(), conditions=(), allergies=(), labs=(), age=50, gender="male", status=None):
    return PatientData(patient_id="p", name="T", age=age, gender=gender, labs=list(labs), vitals=[],
                       conditions=list(conditions), medications=list(meds), allergies=list(allergies),
                       retrieval_status=dict(OK, **(status or {})))


def history(records=(), status="retrieved"):
    return ComprehensivePatientHistory(patient_id="p", patient_name="T", medication_history=list(records),
                                       retrieval_status={"medications": status})


def review(line, p=None, h=None, h_status="retrieved"):
    return TreatmentReviewer(p or patient(), h if h is not None else history(), h_status).review_line(line)


def test_named_medications_finds_drugs_and_classes_in_order():
    names = [m["name"] for m in named_medications("ACE inhibitors: lisinopril 10-40 mg daily, then NSAIDs")]
    assert names == ["ace inhibitor", "lisinopril", "nsaid"]
    assert named_medications("Lifestyle modifications: DASH diet") == []


def test_allergy_word_after_a_drug_is_context_not_the_option():
    assert [m["name"] for m in named_medications("Penicillin allergy: clindamycin 300mg")] == []


def test_line_without_a_known_medication_is_not_checked():
    out = review("Saline nasal irrigation")
    assert out["mark"] == NOT_CHECKED and out["reasons"] == []


def test_no_conflict_is_appropriate():
    out = review("Calcium channel blockers: amlodipine 5-10 mg daily")
    assert out["mark"] == APPROPRIATE and out["medications"] == ["calcium channel blocker", "amlodipine"]


def test_interaction_with_a_current_medication_is_caution_with_source():
    out = review("Pain control: ibuprofen 600mg PO q6h", patient(meds=[med("Warfarin 5 mg")]))
    assert out["mark"] == CAUTION
    reason = out["reasons"][0]
    assert reason["check"] == "drug_interaction" and reason["medication"] == "ibuprofen"
    assert reason["source"] == "Medication list: warfarin 5 mg"


def test_interactions_among_current_medications_are_not_attributed_to_the_option():
    out = review("amlodipine 5 mg daily", patient(meds=[med("Warfarin 5 mg"), med("Aspirin 81 mg")]))
    assert out["mark"] == APPROPRIATE and out["reasons"] == []


def test_cross_reactivity_and_named_allergy_are_avoid():
    p = patient(allergies=[coded("Penicillin")])
    out = review("Antibiotics: amoxicillin 500mg PO TID", p)
    assert out["mark"] == AVOID
    assert out["reasons"][0]["check"] == "allergen_cross_reactivity"
    assert out["reasons"][0]["source"] == "Allergies: penicillin"
    out = review("Desensitization for penicillin", p)
    assert out["mark"] == AVOID and out["reasons"][0]["check"] == "recorded_allergy"


def test_pregnancy_from_problem_list_marks_ace_inhibitors_avoid():
    p = patient(conditions=[coded("Pregnancy, second trimester")], gender="female")
    out = review("ACE inhibitors: lisinopril 10-40 mg daily", p)
    assert out["mark"] == AVOID
    assert {r["check"] for r in out["reasons"]} == {"pregnancy_warning"}
    assert out["reasons"][0]["source"] == "Problem list: Pregnancy, second trimester"
    assert review("ACE inhibitors: lisinopril", patient(conditions=[coded("Not pregnant")], gender="female"))[
        "mark"] == APPROPRIATE


def test_renal_function_from_egfr_and_problem_list():
    factors = patient_factors(patient(labs=[egfr(25)]))
    assert factors["renal"] == {"value": "stage 4", "source": "Lab: eGFR 25 mL/min/1.73m2 on 2026-10-01"}
    assert patient_factors(patient(labs=[egfr(12)]))["renal"]["value"] == "stage 5"
    assert patient_factors(patient(labs=[egfr(55)]))["renal"] is None
    # Most recent eGFR wins.
    factors = patient_factors(patient(labs=[egfr(20, datetime(2025, 1, 1)), egfr(60, datetime(2026, 1, 1))]))
    assert factors["renal"] is None
    factors = patient_factors(patient(conditions=[coded("Chronic kidney disease stage 4")]))
    assert factors["renal"] == {"value": "stage 4", "source": "Problem list: Chronic kidney disease stage 4"}
    out = review("Metformin 500 mg daily", patient(labs=[egfr(25)]))
    assert out["mark"] == CAUTION and out["reasons"][0]["check"] == "renal_adjustment"
    assert out["reasons"][0]["source"].startswith("Lab: eGFR 25")


def test_hepatic_function_from_problem_list():
    p = patient(conditions=[coded("Alcoholic cirrhosis of liver")])
    assert patient_factors(p)["hepatic"] == {"value": "cirrhosis", "source": "Problem list: Alcoholic cirrhosis of liver"}
    out = review("Warfarin per INR", p)
    assert out["mark"] == CAUTION and any(r["check"] == "hepatic_adjustment" for r in out["reasons"])


def test_prior_adverse_reaction_same_drug_and_same_class_is_avoid():
    h = history([{"name": "enalapril 10 mg", "status": "stopped", "date_stopped": "2026-02-01",
                  "stop_reason": "Allergy: angioedema"}])
    out = review("enalapril 5-20 mg BID", h=h)
    assert out["mark"] == AVOID and out["reasons"][0]["reason"].startswith("Prior adverse reaction to this medication")
    out = review("lisinopril 10-40 mg daily", h=h)
    assert out["mark"] == AVOID and "the same class (ACE inhibitor)" in out["reasons"][0]["reason"]
    assert out["reasons"][0]["source"] == "Medication history: MedicationRequest.statusReason"
    # A stop without an adverse reason is not an adverse reaction.
    h = history([{"name": "enalapril 10 mg", "status": "completed", "stop_reason": "course finished"}])
    assert review("enalapril 5-20 mg BID", h=h)["mark"] == APPROPRIATE


def test_missing_data_is_caution_and_reported_not_appropriate():
    reviewer = TreatmentReviewer(patient(status={"allergies": "failed"}), None, None)
    out = reviewer.review_line("amlodipine 5 mg daily")
    assert out["mark"] == CAUTION and out["reasons"][0]["check"] == "data_missing"
    assert "Allergies could not be retrieved; allergies were not checked." in reviewer.not_checked
    assert any("medication history could not be retrieved" in n for n in reviewer.not_checked)


def test_sections_keep_tree_order_and_nothing_is_ranked_or_chosen():
    p = patient(meds=[med("Warfarin 5 mg")], allergies=[coded("Penicillin")])
    sections = [{"title": None, "items": ["Saline irrigation", "amoxicillin 500 mg", "ibuprofen 400 mg",
                                          "amlodipine 5 mg"]}]
    result = TreatmentReviewer(p, history(), "retrieved").review_sections(sections)
    lines = result["sections"][0]
    assert [o["text"] for o in lines] == sections[0]["items"]
    assert [o["mark"] for o in lines] == [NOT_CHECKED, AVOID, CAUTION, APPROPRIATE]
    for o in lines:
        assert set(o) == {"text", "mark", "mark_label", "medications", "reasons"}
    assert "not ranked" in result["notice"]
