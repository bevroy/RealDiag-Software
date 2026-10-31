"""Chart-derived search terms (latest vital signs, H&P chief complaints), with sources."""
from datetime import datetime, timedelta

from backend.services.chart_terms import chart_terms
from backend.services.fhir_client import PatientData, VitalSign
from backend.services.patient_history_service import ComprehensivePatientHistory, HistoryAndPhysical

NOW = datetime(2026, 10, 31, 8, 0)


def vital(code, value, unit, hours_ago=1):
    return VitalSign(code=code, display=code, value=value, unit=unit, effective_date=NOW - timedelta(hours=hours_ago))


def patient(vitals=(), status="retrieved"):
    return PatientData(patient_id="p", name="T", age=60, gender="male", labs=[], vitals=list(vitals), conditions=[],
                       medications=[], allergies=[], retrieval_status={"vitals": status})


def test_latest_vital_of_each_kind_is_used():
    terms = chart_terms(patient([vital("8867-4", 80, "/min", 30), vital("8867-4", 132, "/min", 1)]), None)
    assert [(t["term"], t["source"]) for t in terms] == [
        ("tachycardia", "Vital signs: Heart rate 132 /min"), ("severe tachycardia", "Vital signs: Heart rate 132 /min")]
    assert terms[0]["date"] == "2026-10-31"


def test_celsius_temperature_and_blood_pressure_parts():
    terms = chart_terms(patient([vital("8310-5", 37.0, "Cel"), vital("8462-4", 95, "mm[Hg]"),
                                 vital("2708-6", 88, "%")]), None)
    assert [t["term"] for t in terms] == ["hypertension", "hypoxemia", "severe hypoxemia"]


def test_hp_chief_complaints_with_negations_removed():
    history = ComprehensivePatientHistory(
        patient_id="p", patient_name="T", retrieval_status={"history_and_physicals": "retrieved"},
        history_and_physicals=[HistoryAndPhysical(date="2026-10-20", chief_complaint="cough and wheeze, no fever")])
    terms = chart_terms(patient(), history)
    assert [(t["term"], t["source"], t["date"]) for t in terms] == [
        ("cough", "History and physical: chief complaint", "2026-10-20"),
        ("wheeze", "History and physical: chief complaint", "2026-10-20")]


def test_unretrieved_data_gives_no_terms():
    history = ComprehensivePatientHistory(
        patient_id="p", patient_name="T", retrieval_status={"history_and_physicals": "failed"},
        history_and_physicals=[HistoryAndPhysical(date="2026-10-20", chief_complaint="cough")])
    assert chart_terms(patient([vital("8867-4", 140, "/min")], status="failed"), history) == []
