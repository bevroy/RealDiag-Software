"""Rules-based extraction from clinical notes: sections, problems, medications, allergies
and key findings, each with its DocumentReference source. No AI."""
import base64

from backend.services.note_extraction import LABEL, extract_note, extracted_summary, split_sections
from backend.services.patient_history_service import ComprehensivePatientHistory, VisitNote

NOTE = """Chief Complaint: chest pain x 2 days
HPI: 62M with exertional chest pressure. BP 152/94, HR 112, T 38.6 C, RR 22, SpO2 93%.
Past Medical History:
- Type 2 diabetes
- Hypertension
Medications:
1. Metformin 1000 mg BID
2. Lisinopril 20 mg daily
Allergies: penicillin (rash); sulfa
Labs: HbA1c 8.2%, creatinine 1.4, troponin 0.08
Assessment:
- Chest pain, rule out ACS
- Uncontrolled diabetes
Plan: serial troponins
"""


def note(content=NOTE, doc_id="doc-1", kind="Progress Note", date="2026-10-28T09:15:00Z"):
    return VisitNote(date=date, type=kind, content=content, document_id=doc_id)


def facts(kind, result):
    return [f for f in result["facts"] if f["kind"] == kind]


def test_sections_are_split_by_heading():
    sections = split_sections(NOTE)
    assert {"chief_complaint", "hpi", "past_medical_history", "medications", "allergies", "results",
            "assessment", "plan"} <= set(sections)


def test_problems_medications_allergies_with_sources():
    result = extract_note(note())
    assert [f["text"] for f in facts("problem", result)] == [
        "Chest pain, rule out ACS", "Uncontrolled diabetes", "Type 2 diabetes", "Hypertension"]
    assert [f["text"] for f in facts("medication", result)] == ["Metformin 1000 mg BID", "Lisinopril 20 mg daily"]
    assert [f["text"] for f in facts("allergy", result)] == ["penicillin (rash)", "sulfa"]
    assert facts("chief_complaint", result)[0]["text"] == "chest pain x 2 days"
    source = facts("problem", result)[0]["source"]
    assert source == {"resource_type": "DocumentReference", "document_id": "doc-1",
                      "document_type": "Progress Note", "date": "2026-10-28"}
    assert facts("problem", result)[0]["section"] == "assessment"


def test_key_findings_are_values_written_in_the_text():
    found = {(f["label"], f["value"], f["unit"]) for f in facts("finding", extract_note(note()))}
    assert {("Blood pressure", "152/94", "mmHg"), ("Heart rate", "112", "/min"), ("Temperature", "38.6", "C"),
            ("Respiratory rate", "22", "/min"), ("Oxygen saturation", "93", "%"), ("HbA1c", "8.2", "%"),
            ("Creatinine", "1.4", "mg/dL"), ("Troponin", "0.08", None)} <= found
    # HbA1c is not read as hemoglobin
    assert not [f for f in facts("finding", extract_note(note())) if f["label"] == "Hemoglobin"]


def test_html_notes_are_read_as_text():
    html_note = "<p><b>Assessment:</b></p><ul><li>Community-acquired pneumonia</li></ul>"
    assert [f["text"] for f in facts("problem", extract_note(note(content=html_note)))] == [
        "Community-acquired pneumonia"]


def test_unreadable_notes_are_counted_not_guessed():
    assert extract_note(note(content="Content not available"))["readable"] is False
    assert extract_note(note(content="https://ehr.example/Binary/1"))["readable"] is False
    history = ComprehensivePatientHistory(patient_id="p", patient_name="T",
                                          visit_notes=[note(), note(content="", doc_id="doc-2")])
    summary = extracted_summary(history, "retrieved")
    assert summary["label"] == LABEL and "Not a clinical interpretation" in LABEL
    assert summary["documents_read"] == 1 and summary["documents_unreadable"] == 1
    assert summary["not_read"] == ["1 note(s) had no readable text (no content, or an attachment that could not "
                                   "be retrieved)."]


def test_notes_not_retrieved():
    summary = extracted_summary(None, "failed")
    assert summary["facts"] == [] and summary["not_read"] == [
        "Clinical notes could not be retrieved; nothing was extracted."]


def test_history_service_records_the_document_id():
    import asyncio
    import httpx
    from backend.services.patient_history_service import PatientHistoryService
    doc = {"resourceType": "DocumentReference", "id": "doc-77", "date": "2026-10-28",
           "type": {"coding": [{"display": "Progress Note"}]},
           "content": [{"attachment": {"data": base64.b64encode(NOTE.encode()).decode()}}]}

    def handler(request):
        if request.url.path.endswith("/DocumentReference") and "type" not in request.url.params:
            return httpx.Response(200, json={"resourceType": "Bundle", "entry": [{"resource": doc}]})
        if "/Patient/" in request.url.path:
            return httpx.Response(200, json={"name": [{"family": "X"}], "birthDate": "1970-01-01"})
        return httpx.Response(200, json={"resourceType": "Bundle", "entry": []})

    service = PatientHistoryService("https://fhir.example.test/R4", auth_token="t")
    service.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    history = asyncio.run(service.get_comprehensive_history("p1"))
    assert history.visit_notes[0].document_id == "doc-77"
