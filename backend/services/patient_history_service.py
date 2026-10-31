"""
Patient History Service
=======================

Comprehensive patient history retrieval including prior visit notes,
diagnostic tests, H&Ps, procedures, and imaging for complete diagnostic context.
"""

from contextvars import ContextVar
from fastapi import HTTPException
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import os

import httpx
from pydantic import BaseModel, Field

from backend.services.fhir_client import FAILED, NOT_AVAILABLE, RETRIEVED, retrieval_warnings, truncation_warning

# Per-request retrieval tracking. ContextVars keep concurrent requests that
# share one PatientHistoryService instance from mixing up each other's status.
_current_resource: ContextVar[Optional[str]] = ContextVar("history_current_resource", default=None)
_retrieval_status: ContextVar[Optional[Dict[str, str]]] = ContextVar("history_retrieval_status", default=None)
# Per-request list of searches cut off at the page cap (see _get).
_truncations: ContextVar[Optional[List[Dict[str, Any]]]] = ContextVar("history_truncations", default=None)

# FHIR searches follow the bundle's `next` links up to this many pages in total;
# anything beyond is reported as cut off, the same way FHIRClient reports it.
HISTORY_MAX_PAGES = int(os.getenv("HISTORY_MAX_PAGES", "5"))

_ENTRY_DATE_FIELDS = ("effectiveDateTime", "date", "authoredOn", "recordedDate", "started",
                      "occurrenceDateTime", "performedDateTime", "onsetDateTime", "issued")


def _entry_date(resource: Dict[str, Any]) -> Optional[str]:
    for field_name in _ENTRY_DATE_FIELDS:
        value = resource.get(field_name)
        if isinstance(value, str) and len(value) >= 10:
            return value[:10]
    period = resource.get("effectivePeriod") or resource.get("performedPeriod") or {}
    start = period.get("start") if isinstance(period, dict) else None
    return start[:10] if isinstance(start, str) and len(start) >= 10 else None


def _next_link(bundle: Dict[str, Any]) -> Optional[str]:
    return next((link.get("url") for link in bundle.get("link", []) or []
                 if link.get("relation") == "next" and link.get("url")), None)

# Worst outcome wins when one data type needs several queries.
_STATUS_RANK = {RETRIEVED: 0, NOT_AVAILABLE: 1, FAILED: 2}



def _cut_off_warnings(events: List[Dict[str, Any]]) -> List[str]:
    """One "cut off" warning per search the page cap stopped (same wording as FHIRClient)."""
    warnings: List[str] = []
    for event in events:
        message = truncation_warning(event.get("resource") or "results", event)
        if message not in warnings:
            warnings.append(message)
    return warnings


def _concept_name(concept: Optional[Dict[str, Any]]) -> str:
    """A CodeableConcept's text, else its first coding display, else its code."""
    concept = concept or {}
    if concept.get('text'):
        return concept['text']
    for coding in concept.get('coding') or []:
        if coding.get('display'):
            return coding['display']
    for coding in concept.get('coding') or []:
        if coding.get('code'):
            return coding['code']
    return 'Unnamed condition'

class VisitNote(BaseModel):
    """Clinical visit note."""
    date: str
    type: str  # Progress Note, H&P, Discharge Summary, etc.
    author: Optional[str] = None
    specialty: Optional[str] = None
    content: str
    encounter_id: Optional[str] = None
    document_id: Optional[str] = None  # DocumentReference.id the note came from


class DiagnosticTest(BaseModel):
    """Diagnostic test result."""
    date: str
    test_name: str
    test_type: str  # Lab, Imaging, Pathology, etc.
    result: str
    interpretation: Optional[str] = None
    abnormal: bool = False
    critical: bool = False
    reference_range: Optional[str] = None
    loinc_code: Optional[str] = None


class HistoryAndPhysical(BaseModel):
    """History and Physical Examination."""
    date: str
    author: Optional[str] = None
    chief_complaint: Optional[str] = None
    history_of_present_illness: Optional[str] = None
    past_medical_history: List[str] = []
    past_surgical_history: List[str] = []
    medications: List[str] = []
    allergies: List[str] = []
    family_history: Optional[str] = None
    social_history: Optional[str] = None
    review_of_systems: Optional[str] = None
    physical_exam: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None


class Procedure(BaseModel):
    """Procedure performed."""
    date: str
    procedure_name: str
    procedure_code: Optional[str] = None
    indication: Optional[str] = None
    outcome: Optional[str] = None
    complications: Optional[str] = None
    operator: Optional[str] = None


class ImagingStudy(BaseModel):
    """Imaging study result."""
    date: str
    modality: str  # CT, MRI, X-Ray, Ultrasound, etc.
    body_site: str
    indication: Optional[str] = None
    findings: Optional[str] = None
    impression: Optional[str] = None
    radiologist: Optional[str] = None


class Immunization(BaseModel):
    """Immunization record."""
    date: str
    vaccine: str
    vaccine_code: Optional[str] = None
    status: Optional[str] = None
    dose_number: Optional[str] = None
    lot_number: Optional[str] = None
    site: Optional[str] = None
    performer: Optional[str] = None


class VitalSigns(BaseModel):
    """Vital signs measurement."""
    date: str
    time: Optional[str] = None
    temperature: Optional[float] = None
    temperature_unit: Optional[str] = 'F'
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    respiratory_rate: Optional[int] = None
    oxygen_saturation: Optional[float] = None
    weight: Optional[float] = None
    weight_unit: Optional[str] = 'lbs'
    height: Optional[float] = None
    height_unit: Optional[str] = 'inches'
    bmi: Optional[float] = None
    pain_scale: Optional[int] = None
    notes: Optional[str] = None


class ComprehensivePatientHistory(BaseModel):
    """Complete patient history for diagnosis."""
    patient_id: str
    patient_name: str
    date_of_birth: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None

    # Current visit
    current_chief_complaint: Optional[str] = None
    current_symptoms: List[str] = []

    # Historical data
    visit_notes: List[VisitNote] = []
    vital_signs: List[VitalSigns] = []
    diagnostic_tests: List[DiagnosticTest] = []
    history_and_physicals: List[HistoryAndPhysical] = []
    procedures: List[Procedure] = []
    imaging_studies: List[ImagingStudy] = []
    immunizations: List[Immunization] = []

    # Problem list
    active_conditions: List[Dict[str, Any]] = []
    past_conditions: List[Dict[str, Any]] = []

    # Medications and allergies
    current_medications: List[Dict[str, Any]] = []
    medication_history: List[Dict[str, Any]] = []
    allergies: List[str] = []

    # Family and social history
    family_history: Optional[str] = None
    social_history: Optional[str] = None

    # Summary
    summary: Optional[str] = None

    # Per data type: "retrieved" | "failed" | "not available". An empty list
    # means "none found" only when its status is "retrieved".
    retrieval_status: Dict[str, str] = {}
    data_warnings: List[str] = []


def medication_stop_date(med: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """(stop date, FHIR element it came from) for an R4 MedicationRequest.

    R4 has no "date stopped" element (statusChanged is R5), so the end of the
    intended therapy period is used, in this order:
      1. dosageInstruction[].timing.repeat.boundsPeriod.end (latest)
      2. dispenseRequest.validityPeriod.end
    Returns (None, None) when neither is present.
    """
    ends = []
    for dosage in med.get('dosageInstruction') or []:
        bounds = (((dosage or {}).get('timing') or {}).get('repeat') or {}).get('boundsPeriod') or {}
        if bounds.get('end'):
            ends.append(str(bounds['end']))
    if ends:
        return max(ends), 'dosageInstruction.timing.repeat.boundsPeriod.end'
    validity = ((med.get('dispenseRequest') or {}).get('validityPeriod') or {}).get('end')
    if validity:
        return str(validity), 'dispenseRequest.validityPeriod.end'
    return None, None


def medication_stop_reason(med: Dict[str, Any]) -> Optional[str]:
    """Why an R4 MedicationRequest was stopped, from statusReason (text, else coding)."""
    reason = med.get('statusReason') or {}
    if reason.get('text'):
        return str(reason['text'])
    for coding in reason.get('coding') or []:
        if coding.get('display') or coding.get('code'):
            return str(coding.get('display') or coding.get('code'))
    return None


class PatientHistoryService:
    """Service for comprehensive patient history retrieval."""

    def __init__(self, fhir_base_url: str, auth_token: Optional[str] = None):
        self.fhir_base_url = fhir_base_url.rstrip('/')
        self.auth_token = auth_token
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authentication."""
        headers = {
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json"
        }

        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        return headers

    @staticmethod
    def _mark(status: str, resource: Optional[str] = None) -> None:
        """Record an outcome for the data type being fetched (worst outcome wins)."""
        resource = resource or _current_resource.get()
        tracker = _retrieval_status.get()
        if resource is None or tracker is None:
            return
        previous = tracker.get(resource)
        if previous is None or _STATUS_RANK[status] > _STATUS_RANK[previous]:
            tracker[resource] = status

    async def _get(self, url: str, **kwargs) -> httpx.Response:
        """GET a FHIR query and record whether it succeeded for the current data type.

        200 = retrieved; 403/404/501 = not available (resource type not enabled
        or supported); any other status or a transport error = failed.
        """
        try:
            response = await self.client.get(url, **kwargs)
        except Exception:
            self._mark(FAILED)
            raise
        if response.status_code == 200:
            self._mark(RETRIEVED)
        elif response.status_code in (403, 404, 501):
            self._mark(NOT_AVAILABLE)
        else:
            self._mark(FAILED)
            return response
        return await self._follow_pages(response, **kwargs)

    async def _follow_pages(self, response: httpx.Response, **kwargs) -> httpx.Response:
        """A search Bundle with every page up to HISTORY_MAX_PAGES merged into one.

        A page that fails marks the data type failed and keeps the entries
        already read. When the cap stops before the last page, the cut-off is
        recorded and reported in data_warnings.
        """
        try:
            bundle = response.json()
        except ValueError:
            return response
        if not isinstance(bundle, dict) or bundle.get("resourceType") != "Bundle" or not _next_link(bundle):
            return response
        entries = list(bundle.get("entry") or [])
        pages, last = 1, bundle
        while pages < HISTORY_MAX_PAGES and _next_link(last):
            try:
                page = await self.client.get(_next_link(last), **kwargs)
            except Exception:
                self._mark(FAILED)
                break
            if page.status_code != 200:
                self._mark(FAILED)
                break
            last = page.json()
            entries.extend(last.get("entry") or [])
            pages += 1
        if _next_link(last) and pages >= HISTORY_MAX_PAGES:
            dates = sorted(d for d in (_entry_date(e.get("resource") or {}) for e in entries) if d)
            event = {"resource": _current_resource.get(), "count": len(entries), "pages": pages,
                     "first": dates[0] if dates else None, "last": dates[-1] if dates else None, "since": None}
            tracker = _truncations.get()
            if tracker is not None:
                tracker.append(event)
        merged = {**bundle, "entry": entries, "link": [l for l in bundle.get("link", []) or []
                                                        if l.get("relation") != "next"]}
        return httpx.Response(200, json=merged, request=response.request)

    async def _tracked(self, resource: str, fetch):
        """Run one fetcher with `resource` as the data type its queries count toward."""
        token = _current_resource.set(resource)
        try:
            return await fetch
        finally:
            _current_resource.reset(token)

    async def get_comprehensive_history(
        self,
        patient_id: str,
        lookback_days: Optional[int] = 365,
        include_resolved: bool = True,
        skip: Optional[set] = None,
        lookback_overrides: Optional[Dict[str, Optional[int]]] = None
    ) -> ComprehensivePatientHistory:
        """
        Retrieve comprehensive patient history for diagnostic decision support.

        Args:
            patient_id: FHIR Patient resource ID
            lookback_days: Number of days to look back for historical data.
                Pass None or a value <= 0 for an unbounded pull - no date
                filter is applied, so notes/vitals/labs/H&Ps/procedures/
                imaging/immunizations of any age are returned. (Problem
                list, medications, allergies, and family/social history are
                always unbounded regardless of this setting - the FHIR
                queries backing them don't support meaningful date scoping.)
            include_resolved: Include resolved/inactive conditions
            lookback_overrides: per-data-type lookback in days (e.g.
                {"procedures": 3650}) used instead of lookback_days
            skip: data types not to query (e.g. {"vital_signs", "conditions"})
                because the caller fetched them already; they come back empty
                with no retrieval status.

        Returns:
            ComprehensivePatientHistory with all available patient data
        """
        headers = await self._get_headers()
        def since(days: Optional[int]) -> Optional[str]:
            if days is None or days <= 0:
                return None
            return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        lookback_date = since(lookback_days)
        overrides = lookback_overrides or {}
        lookback_for = {r: since(d) for r, d in overrides.items()}

        status_token = _retrieval_status.set({})
        truncation_token = _truncations.set([])
        try:
            skip = set(skip or ())

            async def fetch(resource: str, make, empty):
                # A skipped data type is not queried and gets no status: the
                # caller already fetched it with its own client.
                if resource in skip:
                    return empty
                return await self._tracked(resource, make())

            patient_data = await fetch(
                "demographics", lambda: self._fetch_patient_demographics(patient_id, headers), {})
            visit_notes = await fetch(
                "visit_notes", lambda: self._fetch_visit_notes(patient_id, lookback_date, headers), [])
            vital_signs = await fetch(
                "vital_signs", lambda: self._fetch_vital_signs(patient_id, lookback_date, headers), [])
            diagnostic_tests = await fetch(
                "diagnostic_tests", lambda: self._fetch_diagnostic_tests(patient_id, lookback_date, headers), [])
            history_and_physicals = await fetch(
                "history_and_physicals",
                lambda: self._fetch_history_and_physicals(patient_id, lookback_date, headers), [])
            procedures = await fetch(
                "procedures", lambda: self._fetch_procedures(
                    patient_id, lookback_for.get("procedures", lookback_date), headers), [])
            imaging_studies = await fetch(
                "imaging_studies", lambda: self._fetch_imaging_studies(
                    patient_id, lookback_for.get("imaging_studies", lookback_date), headers), [])
            immunizations = await fetch(
                "immunizations", lambda: self._fetch_immunizations(patient_id, lookback_date, headers), [])
            active_conditions, past_conditions = await fetch(
                "conditions", lambda: self._fetch_conditions(patient_id, include_resolved, headers), ([], []))
            current_meds, med_history = await fetch(
                "medications", lambda: self._fetch_medications(patient_id, headers), ([], []))
            allergies = await fetch("allergies", lambda: self._fetch_allergies(patient_id, headers), [])
            family_history, social_history = await fetch(
                "family_social_history", lambda: self._fetch_family_social_history(patient_id, headers),
                (None, None))
            retrieval_status = dict(_retrieval_status.get() or {})
            cut_off = list(_truncations.get() or [])
        finally:
            _retrieval_status.reset(status_token)
            _truncations.reset(truncation_token)

        # Generate summary
        summary = self._generate_summary(
            patient_data,
            active_conditions,
            current_meds,
            diagnostic_tests,
            visit_notes,
            retrieval_status,
        )

        return ComprehensivePatientHistory(
            patient_id=patient_id,
            patient_name=patient_data.get('name', 'Unknown'),
            date_of_birth=patient_data.get('birth_date'),
            age=patient_data.get('age'),
            gender=patient_data.get('gender'),
            visit_notes=visit_notes,
            vital_signs=vital_signs,
            diagnostic_tests=diagnostic_tests,
            history_and_physicals=history_and_physicals,
            procedures=procedures,
            imaging_studies=imaging_studies,
            immunizations=immunizations,
            active_conditions=active_conditions,
            past_conditions=past_conditions,
            current_medications=current_meds,
            medication_history=med_history,
            allergies=allergies,
            family_history=family_history,
            social_history=social_history,
            summary=summary,
            retrieval_status=retrieval_status,
            data_warnings=retrieval_warnings(retrieval_status) + _cut_off_warnings(cut_off),
        )

    async def _fetch_patient_demographics(self, patient_id: str, headers: Dict) -> Dict[str, Any]:
        """Fetch patient demographics."""
        try:
            response = await self._get(
                f"{self.fhir_base_url}/Patient/{patient_id}",
                headers=headers
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch patient")

            patient = response.json()

            # Extract name
            name = "Unknown"
            if patient.get('name'):
                name_obj = patient['name'][0]
                given = ' '.join(name_obj.get('given', []))
                family = name_obj.get('family', '')
                name = f"{given} {family}".strip()

            # Calculate age
            birth_date = patient.get('birthDate')
            age = None
            if birth_date:
                from datetime import date
                birth = datetime.strptime(birth_date, "%Y-%m-%d").date()
                today = date.today()
                age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))

            return {
                'name': name,
                'birth_date': birth_date,
                'age': age,
                'gender': patient.get('gender')
            }
        except Exception as e:
            print(f"Error fetching patient demographics: {e}")
            self._mark(FAILED)
            return {}

    async def _fetch_attachment_content(self, url: str, headers: Dict) -> str:
        """
        Fetch DocumentReference attachment content when only a URL
        reference is provided (common for real EHR documents) instead of
        inline base64 data. The URL may be relative (e.g. "Binary/123")
        or absolute; some servers respond with a raw text/html/xml body,
        others wrap it in a FHIR Binary resource (base64 'data' field) -
        this handles both. Falls back to a placeholder on any failure so
        callers never see an exception.
        """
        try:
            full_url = url if url.startswith('http') else f"{self.fhir_base_url}/{url.lstrip('/')}"
            fetch_headers = dict(headers)
            fetch_headers['Accept'] = 'text/plain, text/html, application/xml, application/fhir+json;q=0.5, */*;q=0.3'

            response = await self.client.get(full_url, headers=fetch_headers)  # document body, not tracked

            if response.status_code != 200:
                return f"[Document URL: {url}]"

            content_type = response.headers.get('content-type', '')

            if 'json' in content_type:
                # Server returned the Binary resource wrapper instead of raw content
                binary = response.json()
                data = binary.get('data')
                if data:
                    import base64
                    return base64.b64decode(data).decode('utf-8', errors='replace')
                return f"[Document URL: {url}]"

            # Raw text/html/xml content
            return response.text

        except Exception as e:
            print(f"Error fetching attachment content from {url}: {e}")
            return f"[Document URL: {url}]"

    async def _fetch_visit_notes(self, patient_id: str, lookback_date: Optional[str], headers: Dict) -> List[VisitNote]:
        """Fetch clinical visit notes via DocumentReference."""
        visit_notes = []

        try:
            url = f"{self.fhir_base_url}/DocumentReference?patient={patient_id}&_sort=-date&_count=50"
            if lookback_date:
                url += f"&date=ge{lookback_date}"

            response = await self._get(url, headers=headers)

            if response.status_code == 200:
                bundle = response.json()

                for entry in bundle.get('entry', []):
                    doc = entry.get('resource', {})

                    # Get document type
                    doc_type = "Clinical Note"
                    if doc.get('type', {}).get('coding'):
                        doc_type = doc['type']['coding'][0].get('display', 'Clinical Note')

                    # Get date
                    date = doc.get('date', doc.get('created', 'Unknown'))

                    # Get author
                    author = None
                    if doc.get('author'):
                        author_ref = doc['author'][0].get('display', 'Unknown Author')
                        author = author_ref

                    # Get content
                    content = ""
                    if doc.get('content'):
                        for content_item in doc['content']:
                            attachment = content_item.get('attachment', {})
                            if attachment.get('data'):
                                # Base64 encoded content
                                import base64
                                try:
                                    content = base64.b64decode(attachment['data']).decode('utf-8')
                                except:
                                    content = attachment.get('url', 'Content not available')
                            elif attachment.get('url'):
                                content = await self._fetch_attachment_content(attachment['url'], headers)

                    # Get specialty from context
                    specialty = None
                    if doc.get('context', {}).get('practiceSetting', {}).get('coding'):
                        specialty = doc['context']['practiceSetting']['coding'][0].get('display')

                    visit_notes.append(VisitNote(
                        date=date,
                        type=doc_type,
                        author=author,
                        specialty=specialty,
                        content=content,
                        encounter_id=doc.get('context', {}).get('encounter', [{}])[0].get('reference'),
                        document_id=doc.get('id'),
                    ))

        except Exception as e:
            print(f"Error fetching visit notes: {e}")
            self._mark(FAILED)

        return visit_notes

    async def _fetch_vital_signs(self, patient_id: str, lookback_date: Optional[str], headers: Dict) -> List[VitalSigns]:
        """Fetch vital signs from FHIR Observations with vital-signs category."""
        vital_signs_list = []

        try:
            url = f"{self.fhir_base_url}/Observation?patient={patient_id}&category=vital-signs&_sort=-date&_count=100"
            if lookback_date:
                url += f"&date=ge{lookback_date}"

            response = await self._get(url, headers=headers)

            if response.status_code == 200:
                bundle = response.json()

                # Group observations by date/time
                vitals_by_datetime = {}

                for entry in bundle.get('entry', []):
                    obs = entry.get('resource', {})

                    # Get date and time
                    effective_datetime = obs.get('effectiveDateTime', '')
                    if not effective_datetime:
                        continue

                    # Parse date and time
                    try:
                        dt = datetime.fromisoformat(effective_datetime.replace('Z', '+00:00'))
                        date_key = dt.strftime('%Y-%m-%d')
                        time_key = dt.strftime('%H:%M')
                        datetime_key = f"{date_key}_{time_key}"
                    except:
                        date_key = effective_datetime.split('T')[0] if 'T' in effective_datetime else effective_datetime
                        time_key = effective_datetime.split('T')[1][:5] if 'T' in effective_datetime else ''
                        datetime_key = f"{date_key}_{time_key}"

                    # Initialize vital signs record if not exists
                    if datetime_key not in vitals_by_datetime:
                        vitals_by_datetime[datetime_key] = {
                            'date': date_key,
                            'time': time_key
                        }

                    # Get vital sign type and value
                    code_coding = obs.get('code', {}).get('coding', [{}])[0]
                    loinc_code = code_coding.get('code', '')
                    display = code_coding.get('display', '').lower()

                    value_quantity = obs.get('valueQuantity', {})
                    value = value_quantity.get('value')
                    unit = value_quantity.get('unit', '')

                    if not value:
                        continue

                    # Map LOINC codes and display names to vital sign fields
                    vitals = vitals_by_datetime[datetime_key]

                    # Temperature
                    if loinc_code in ['8310-5', '8331-1'] or 'temperature' in display:
                        vitals['temperature'] = float(value)
                        vitals['temperature_unit'] = 'F' if 'f' in unit.lower() or 'fahrenheit' in unit.lower() else 'C'

                    # Blood Pressure
                    elif loinc_code == '8480-6' or 'systolic' in display:
                        vitals['blood_pressure_systolic'] = int(value)
                    elif loinc_code == '8462-4' or 'diastolic' in display:
                        vitals['blood_pressure_diastolic'] = int(value)

                    # Heart Rate
                    elif loinc_code == '8867-4' or 'heart rate' in display or 'pulse' in display:
                        vitals['heart_rate'] = int(value)

                    # Respiratory Rate
                    elif loinc_code == '9279-1' or 'respiratory rate' in display:
                        vitals['respiratory_rate'] = int(value)

                    # Oxygen Saturation
                    elif loinc_code in ['2708-6', '59408-5'] or 'oxygen saturation' in display or 'spo2' in display:
                        vitals['oxygen_saturation'] = float(value)

                    # Weight
                    elif loinc_code in ['29463-7', '3141-9'] or 'body weight' in display or 'weight' in display:
                        vitals['weight'] = float(value)
                        vitals['weight_unit'] = 'kg' if 'kg' in unit.lower() else 'lbs'

                    # Height
                    elif loinc_code in ['8302-2', '8306-3'] or 'body height' in display or 'height' in display:
                        vitals['height'] = float(value)
                        vitals['height_unit'] = 'cm' if 'cm' in unit.lower() else 'inches'

                    # BMI
                    elif loinc_code == '39156-5' or 'bmi' in display or 'body mass index' in display:
                        vitals['bmi'] = float(value)

                    # Pain Scale
                    elif 'pain' in display and 'scale' in display:
                        vitals['pain_scale'] = int(value)

                # Convert grouped vitals to VitalSigns objects
                for datetime_key, vitals in vitals_by_datetime.items():
                    vital_signs_list.append(VitalSigns(**vitals))

        except Exception as e:
            print(f"Error fetching vital signs: {e}")
            self._mark(FAILED)

        return vital_signs_list

    async def _fetch_diagnostic_tests(self, patient_id: str, lookback_date: Optional[str], headers: Dict) -> List[DiagnosticTest]:
        """Fetch diagnostic test results (labs, etc.)."""
        diagnostic_tests = []

        try:
            # Fetch Observations (lab results)
            url = f"{self.fhir_base_url}/Observation?patient={patient_id}&_sort=-date&_count=100"
            if lookback_date:
                url += f"&date=ge{lookback_date}"

            response = await self._get(url, headers=headers)

            if response.status_code == 200:
                bundle = response.json()

                for entry in bundle.get('entry', []):
                    obs = entry.get('resource', {})

                    # Get test name
                    test_name = obs.get('code', {}).get('text', 'Unknown Test')
                    if not test_name or test_name == 'Unknown Test':
                        if obs.get('code', {}).get('coding'):
                            test_name = obs['code']['coding'][0].get('display', 'Unknown Test')

                    # Get test type from category
                    test_type = "Laboratory"
                    if obs.get('category'):
                        for cat in obs['category']:
                            if cat.get('coding'):
                                test_type = cat['coding'][0].get('display', 'Laboratory')

                    # Get result value
                    result = "No result"
                    if obs.get('valueQuantity'):
                        val = obs['valueQuantity']
                        result = f"{val.get('value')} {val.get('unit', '')}"
                    elif obs.get('valueString'):
                        result = obs['valueString']
                    elif obs.get('valueCodeableConcept'):
                        result = obs['valueCodeableConcept'].get('text', 'See report')

                    # Get interpretation
                    interpretation = None
                    abnormal = False
                    critical = False
                    if obs.get('interpretation'):
                        for interp in obs['interpretation']:
                            if interp.get('coding'):
                                code = interp['coding'][0].get('code', '')
                                interpretation = interp['coding'][0].get('display')
                                abnormal = code in ['A', 'H', 'L', 'AA', 'HH', 'LL']
                                critical = code in ['AA', 'HH', 'LL']

                    # Get reference range
                    reference_range = None
                    if obs.get('referenceRange'):
                        ref = obs['referenceRange'][0]
                        low = ref.get('low', {}).get('value', '')
                        high = ref.get('high', {}).get('value', '')
                        unit = ref.get('low', {}).get('unit', '')
                        if low and high:
                            reference_range = f"{low}-{high} {unit}"

                    # Get LOINC code
                    loinc_code = None
                    if obs.get('code', {}).get('coding'):
                        for coding in obs['code']['coding']:
                            if coding.get('system', '').endswith('loinc'):
                                loinc_code = coding.get('code')

                    diagnostic_tests.append(DiagnosticTest(
                        date=obs.get('effectiveDateTime', obs.get('issued', 'Unknown')),
                        test_name=test_name,
                        test_type=test_type,
                        result=result,
                        interpretation=interpretation,
                        abnormal=abnormal,
                        critical=critical,
                        reference_range=reference_range,
                        loinc_code=loinc_code
                    ))

            # Also fetch DiagnosticReport resources
            report_url = f"{self.fhir_base_url}/DiagnosticReport?patient={patient_id}&_sort=-date&_count=50"
            if lookback_date:
                report_url += f"&date=ge{lookback_date}"

            response = await self._get(report_url, headers=headers)

            if response.status_code == 200:
                bundle = response.json()

                for entry in bundle.get('entry', []):
                    report = entry.get('resource', {})

                    test_name = report.get('code', {}).get('text', 'Diagnostic Report')
                    test_type = report.get('category', [{}])[0].get('coding', [{}])[0].get('display', 'Diagnostic')

                    conclusion = report.get('conclusion', 'See full report')

                    diagnostic_tests.append(DiagnosticTest(
                        date=report.get('effectiveDateTime', report.get('issued', 'Unknown')),
                        test_name=test_name,
                        test_type=test_type,
                        result=conclusion,
                        interpretation=report.get('conclusionCode', [{}])[0].get('text')
                    ))

        except Exception as e:
            print(f"Error fetching diagnostic tests: {e}")
            self._mark(FAILED)

        return diagnostic_tests

    async def _fetch_history_and_physicals(self, patient_id: str, lookback_date: Optional[str], headers: Dict) -> List[HistoryAndPhysical]:
        """Fetch History and Physical examinations."""
        h_and_ps = []

        try:
            # Query for H&P document type (LOINC code 34117-2)
            url = f"{self.fhir_base_url}/DocumentReference?patient={patient_id}&type=34117-2&_sort=-date&_count=20"
            if lookback_date:
                url += f"&date=ge{lookback_date}"

            response = await self._get(url, headers=headers)

            if response.status_code == 200:
                bundle = response.json()

                for entry in bundle.get('entry', []):
                    doc = entry.get('resource', {})

                    date = doc.get('date', doc.get('created', 'Unknown'))
                    author = None
                    if doc.get('author'):
                        author = doc['author'][0].get('display', 'Unknown Author')

                    # Parse H&P content (this would need custom parsing based on EHR format)
                    content = ""
                    if doc.get('content'):
                        for content_item in doc['content']:
                            attachment = content_item.get('attachment', {})
                            if attachment.get('data'):
                                import base64
                                try:
                                    content = base64.b64decode(attachment['data']).decode('utf-8')
                                except:
                                    pass
                            elif attachment.get('url'):
                                content = await self._fetch_attachment_content(attachment['url'], headers)

                    # Parse sections from content (simplified - actual parsing would be more complex)
                    h_and_p = self._parse_h_and_p_content(content, date, author)
                    h_and_ps.append(h_and_p)

        except Exception as e:
            print(f"Error fetching H&Ps: {e}")
            self._mark(FAILED)

        return h_and_ps

    def _parse_h_and_p_content(self, content: str, date: str, author: Optional[str]) -> HistoryAndPhysical:
        """Parse H&P content into structured sections."""
        # Simplified parser - real implementation would use NLP or structured data
        sections = {
            'chief_complaint': None,
            'history_of_present_illness': None,
            'past_medical_history': [],
            'past_surgical_history': [],
            'medications': [],
            'allergies': [],
            'family_history': None,
            'social_history': None,
            'review_of_systems': None,
            'physical_exam': None,
            'assessment': None,
            'plan': None
        }

        # Basic section extraction (would be more sophisticated in production)
        lines = content.split('\n')
        current_section = None

        for line in lines:
            line_lower = line.lower().strip()

            if 'chief complaint' in line_lower or 'cc:' in line_lower:
                current_section = 'chief_complaint'
                sections[current_section] = line.split(':', 1)[-1].strip() if ':' in line else ''
            elif 'history of present illness' in line_lower or 'hpi:' in line_lower:
                current_section = 'history_of_present_illness'
                sections[current_section] = line.split(':', 1)[-1].strip() if ':' in line else ''
            elif 'past medical history' in line_lower or 'pmh:' in line_lower:
                current_section = 'past_medical_history'
            elif 'past surgical history' in line_lower or 'psh:' in line_lower:
                current_section = 'past_surgical_history'
            elif 'physical exam' in line_lower or 'pe:' in line_lower:
                current_section = 'physical_exam'
                sections[current_section] = ''
            elif 'assessment' in line_lower or 'a:' == line_lower:
                current_section = 'assessment'
                sections[current_section] = ''
            elif 'plan' in line_lower or 'p:' == line_lower:
                current_section = 'plan'
                sections[current_section] = ''
            elif current_section and line.strip():
                if current_section in ['past_medical_history', 'past_surgical_history']:
                    if line.strip().startswith(('-', '•', '*', str(len(sections[current_section]) + 1))):
                        sections[current_section].append(line.strip().lstrip('-•*0123456789. '))
                elif isinstance(sections[current_section], str):
                    sections[current_section] += ' ' + line.strip()

        return HistoryAndPhysical(
            date=date,
            author=author,
            **sections
        )

    async def _fetch_procedures(self, patient_id: str, lookback_date: Optional[str], headers: Dict) -> List[Procedure]:
        """Fetch procedures performed."""
        procedures = []

        try:
            url = f"{self.fhir_base_url}/Procedure?patient={patient_id}&_sort=-date&_count=50"
            if lookback_date:
                url += f"&date=ge{lookback_date}"

            response = await self._get(url, headers=headers)

            if response.status_code == 200:
                bundle = response.json()

                for entry in bundle.get('entry', []):
                    proc = entry.get('resource', {})

                    procedure_name = proc.get('code', {}).get('text', 'Unknown Procedure')
                    if not procedure_name or procedure_name == 'Unknown Procedure':
                        if proc.get('code', {}).get('coding'):
                            procedure_name = proc['code']['coding'][0].get('display', 'Unknown Procedure')

                    procedure_code = None
                    if proc.get('code', {}).get('coding'):
                        procedure_code = proc['code']['coding'][0].get('code')

                    indication = proc.get('reasonCode', [{}])[0].get('text')
                    outcome = proc.get('outcome', {}).get('text')

                    operator = None
                    if proc.get('performer'):
                        operator = proc['performer'][0].get('actor', {}).get('display')

                    procedures.append(Procedure(
                        date=proc.get('performedDateTime', proc.get('performedPeriod', {}).get('start', 'Unknown')),
                        procedure_name=procedure_name,
                        procedure_code=procedure_code,
                        indication=indication,
                        outcome=outcome,
                        operator=operator
                    ))

        except Exception as e:
            print(f"Error fetching procedures: {e}")
            self._mark(FAILED)

        return procedures

    async def _fetch_imaging_studies(self, patient_id: str, lookback_date: Optional[str], headers: Dict) -> List[ImagingStudy]:
        """Fetch imaging studies."""
        imaging_studies = []

        try:
            url = f"{self.fhir_base_url}/ImagingStudy?patient={patient_id}&_sort=-started&_count=50"
            if lookback_date:
                url += f"&started=ge{lookback_date}"

            response = await self._get(url, headers=headers)

            if response.status_code == 200:
                bundle = response.json()

                for entry in bundle.get('entry', []):
                    study = entry.get('resource', {})

                    modality = study.get('modality', [{}])[0].get('code', 'Unknown')
                    body_site = study.get('series', [{}])[0].get('bodySite', {}).get('display', 'Unknown')

                    # Get associated diagnostic report for findings
                    study_uid = study.get('id')
                    findings = None
                    impression = None
                    radiologist = None

                    if study_uid:
                        # Fetch associated DiagnosticReport
                        report_response = await self._get(
                            f"{self.fhir_base_url}/DiagnosticReport?imagingStudy={study_uid}",
                            headers=headers
                        )

                        if report_response.status_code == 200:
                            report_bundle = report_response.json()
                            if report_bundle.get('entry'):
                                report = report_bundle['entry'][0].get('resource', {})
                                findings = report.get('presentedForm', [{}])[0].get('data', '')
                                impression = report.get('conclusion')
                                if report.get('resultsInterpreter'):
                                    radiologist = report['resultsInterpreter'][0].get('display')

                    imaging_studies.append(ImagingStudy(
                        date=study.get('started', 'Unknown'),
                        modality=modality,
                        body_site=body_site,
                        indication=study.get('reasonCode', [{}])[0].get('text'),
                        findings=findings,
                        impression=impression,
                        radiologist=radiologist
                    ))

        except Exception as e:
            print(f"Error fetching imaging studies: {e}")
            self._mark(FAILED)

        return imaging_studies

    async def _fetch_immunizations(self, patient_id: str, lookback_date: Optional[str], headers: Dict) -> List[Immunization]:
        """Fetch immunization history."""
        immunizations = []

        try:
            url = f"{self.fhir_base_url}/Immunization?patient={patient_id}&_sort=-date&_count=50"
            if lookback_date:
                url += f"&date=ge{lookback_date}"

            response = await self._get(url, headers=headers)

            if response.status_code == 200:
                bundle = response.json()

                for entry in bundle.get('entry', []):
                    imm = entry.get('resource', {})

                    vaccine_code = imm.get('vaccineCode', {})
                    vaccine_name = vaccine_code.get('text', 'Unknown Vaccine')
                    if not vaccine_name or vaccine_name == 'Unknown Vaccine':
                        if vaccine_code.get('coding'):
                            vaccine_name = vaccine_code['coding'][0].get('display', 'Unknown Vaccine')

                    code = None
                    if vaccine_code.get('coding'):
                        code = vaccine_code['coding'][0].get('code')

                    dose_number = None
                    protocol_applied = imm.get('protocolApplied', [{}])
                    if protocol_applied:
                        dose_number = protocol_applied[0].get('doseNumberPositiveInt') or protocol_applied[0].get('doseNumberString')

                    performer = None
                    if imm.get('performer'):
                        performer = imm['performer'][0].get('actor', {}).get('display')

                    immunizations.append(Immunization(
                        date=imm.get('occurrenceDateTime', imm.get('recorded', 'Unknown')),
                        vaccine=vaccine_name,
                        vaccine_code=code,
                        status=imm.get('status'),
                        dose_number=str(dose_number) if dose_number is not None else None,
                        lot_number=imm.get('lotNumber'),
                        site=imm.get('site', {}).get('text'),
                        performer=performer
                    ))

        except Exception as e:
            print(f"Error fetching immunizations: {e}")
            self._mark(FAILED)

        return immunizations

    async def _fetch_conditions(self, patient_id: str, include_resolved: bool, headers: Dict) -> tuple:
        """Fetch active and resolved conditions."""
        active_conditions = []
        past_conditions = []

        try:
            # Fetch active conditions
            response = await self._get(
                f"{self.fhir_base_url}/Condition?patient={patient_id}&clinical-status=active&_count=50",
                headers=headers
            )

            if response.status_code == 200:
                bundle = response.json()

                for entry in bundle.get('entry', []):
                    condition = entry.get('resource', {})
                    active_conditions.append({
                        'code': _concept_name(condition.get('code')),
                        'status': 'active',
                        'recorded_date': condition.get('recordedDate'),
                        'onset': condition.get('onsetDateTime')
                    })

            # Fetch resolved conditions if requested
            if include_resolved:
                response = await self._get(
                    f"{self.fhir_base_url}/Condition?patient={patient_id}&clinical-status=resolved,inactive&_count=50",
                    headers=headers
                )

                if response.status_code == 200:
                    bundle = response.json()

                    for entry in bundle.get('entry', []):
                        condition = entry.get('resource', {})
                        past_conditions.append({
                            'code': _concept_name(condition.get('code')),
                            'status': condition.get('clinicalStatus', {}).get('coding', [{}])[0].get('code', 'resolved'),
                            'recorded_date': condition.get('recordedDate'),
                            'abatement': condition.get('abatementDateTime')
                        })

        except Exception as e:
            print(f"Error fetching conditions: {e}")
            self._mark(FAILED)

        return active_conditions, past_conditions

    async def _fetch_medications(self, patient_id: str, headers: Dict) -> tuple:
        """Fetch current and historical medications."""
        current_meds = []
        med_history = []

        try:
            # Current medications
            response = await self._get(
                f"{self.fhir_base_url}/MedicationRequest?patient={patient_id}&status=active&_count=50",
                headers=headers
            )

            if response.status_code == 200:
                bundle = response.json()

                for entry in bundle.get('entry', []):
                    med = entry.get('resource', {})
                    med_name = med.get('medicationCodeableConcept', {}).get('text', 'Unknown')
                    if not med_name or med_name == 'Unknown':
                        if med.get('medicationCodeableConcept', {}).get('coding'):
                            med_name = med['medicationCodeableConcept']['coding'][0].get('display', 'Unknown')

                    current_meds.append({
                        'name': med_name,
                        'status': 'active',
                        'dosage': med.get('dosageInstruction', [{}])[0].get('text', 'See prescription'),
                        'date_prescribed': med.get('authoredOn')
                    })

            # Historical medications
            response = await self._get(
                f"{self.fhir_base_url}/MedicationRequest?patient={patient_id}&status=completed,stopped&_count=50&_sort=-authoredon",
                headers=headers
            )

            if response.status_code == 200:
                bundle = response.json()

                for entry in bundle.get('entry', []):
                    med = entry.get('resource', {})
                    med_name = med.get('medicationCodeableConcept', {}).get('text', 'Unknown')
                    if not med_name or med_name == 'Unknown':
                        if med.get('medicationCodeableConcept', {}).get('coding'):
                            med_name = med['medicationCodeableConcept']['coding'][0].get('display', 'Unknown')

                    date_stopped, date_stopped_source = medication_stop_date(med)
                    med_history.append({
                        'name': med_name,
                        'status': med.get('status'),
                        'date_prescribed': med.get('authoredOn'),
                        'date_stopped': date_stopped,
                        'date_stopped_source': date_stopped_source,
                        'stop_reason': medication_stop_reason(med),
                    })

        except Exception as e:
            print(f"Error fetching medications: {e}")
            self._mark(FAILED)

        return current_meds, med_history

    async def _fetch_allergies(self, patient_id: str, headers: Dict) -> List[str]:
        """Fetch patient allergies."""
        allergies = []

        try:
            response = await self._get(
                f"{self.fhir_base_url}/AllergyIntolerance?patient={patient_id}&_count=50",
                headers=headers
            )

            if response.status_code == 200:
                bundle = response.json()

                for entry in bundle.get('entry', []):
                    allergy = entry.get('resource', {})
                    allergen = allergy.get('code', {}).get('text', 'Unknown')
                    if not allergen or allergen == 'Unknown':
                        if allergy.get('code', {}).get('coding'):
                            allergen = allergy['code']['coding'][0].get('display', 'Unknown')

                    if allergen and allergen != 'Unknown':
                        allergies.append(allergen)

        except Exception as e:
            print(f"Error fetching allergies: {e}")
            self._mark(FAILED)

        return allergies

    async def _fetch_family_social_history(self, patient_id: str, headers: Dict) -> tuple:
        """Fetch family and social history."""
        family_history = None
        social_history = None

        try:
            # Family history (FamilyMemberHistory or Observation with category)
            response = await self._get(
                f"{self.fhir_base_url}/FamilyMemberHistory?patient={patient_id}&_count=20",
                headers=headers
            )

            if response.status_code == 200:
                bundle = response.json()
                family_items = []

                for entry in bundle.get('entry', []):
                    fmh = entry.get('resource', {})
                    relationship = fmh.get('relationship', {}).get('text', 'Unknown relation')
                    condition = fmh.get('condition', [{}])[0].get('code', {}).get('text', 'Unknown condition')
                    family_items.append(f"{relationship}: {condition}")

                if family_items:
                    family_history = '; '.join(family_items)

            # Social history (Observation with category=social-history)
            response = await self._get(
                f"{self.fhir_base_url}/Observation?patient={patient_id}&category=social-history&_count=20",
                headers=headers
            )

            if response.status_code == 200:
                bundle = response.json()
                social_items = []

                for entry in bundle.get('entry', []):
                    obs = entry.get('resource', {})
                    code = obs.get('code', {}).get('text', '')
                    value = obs.get('valueString', obs.get('valueCodeableConcept', {}).get('text', ''))
                    if code and value:
                        social_items.append(f"{code}: {value}")

                if social_items:
                    social_history = '; '.join(social_items)

        except Exception as e:
            print(f"Error fetching family/social history: {e}")
            self._mark(FAILED)

        return family_history, social_history

    @staticmethod
    def _generate_summary(
        patient_data: Dict,
        active_conditions: List[Dict],
        current_meds: List[Dict],
        diagnostic_tests: List[DiagnosticTest],
        visit_notes: List[VisitNote],
        retrieval_status: Optional[Dict[str, str]] = None,
        abnormal_window: Optional[str] = None,
    ) -> str:
        """Plain template summary of the history (no language model).

        Only states what was retrieved: a data type that could not be
        retrieved is reported as such, never as "none on file".
        `abnormal_window` (e.g. "in the last 30 days") is appended to the
        abnormal-result count to say which results it covers.
        """
        status = retrieval_status or {}

        def gap(resource: str, label: str) -> Optional[str]:
            outcome = status.get(resource, RETRIEVED)
            if outcome == NOT_AVAILABLE:
                return f"{label} is not available from this EHR."
            if outcome != RETRIEVED:
                return f"{label} could not be retrieved."
            return None

        name = patient_data.get('name') or 'Patient'
        age = patient_data.get('age')
        gender = patient_data.get('gender') or 'unknown sex'
        intro = f"{name} is a {age}-year-old {gender}." if age is not None else f"{name}, age unknown, {gender}."
        summary_parts = [intro]

        if gap("conditions", "Problem list"):
            summary_parts.append(gap("conditions", "Problem list"))
        elif active_conditions:
            names = [c['code'] for c in active_conditions[:5]]
            more = f" and {len(active_conditions) - 5} more" if len(active_conditions) > 5 else ""
            summary_parts.append(f"Active problems on file: {', '.join(names)}{more}.")
        else:
            summary_parts.append("No active problems on file.")

        if gap("visit_notes", "Visit notes"):
            summary_parts.append(gap("visit_notes", "Visit notes").replace(" is ", " are "))
        elif visit_notes:
            summary_parts.append(f"Recent visits: {len(visit_notes)} clinical encounters on file.")

        if gap("diagnostic_tests", "Test results"):
            summary_parts.append(gap("diagnostic_tests", "Test results").replace(" is ", " are "))
        else:
            abnormal_tests = [t for t in diagnostic_tests if t.abnormal]
            if abnormal_tests:
                window = f" {abnormal_window}" if abnormal_window else ""
                summary_parts.append(f"{len(abnormal_tests)} test results flagged abnormal{window}.")

        if gap("medications", "Medication list"):
            summary_parts.append(gap("medications", "Medication list"))
        elif current_meds:
            summary_parts.append(f"{len(current_meds)} active medications on file.")
        else:
            summary_parts.append("No active medications on file.")

        return " ".join(summary_parts)
