"""
Patient History Service
=======================

Comprehensive patient history retrieval including prior visit notes,
diagnostic tests, H&Ps, procedures, and imaging for complete diagnostic context.
"""

from fastapi import HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import httpx
from pydantic import BaseModel, Field


class VisitNote(BaseModel):
    """Clinical visit note."""
    date: str
    type: str  # Progress Note, H&P, Discharge Summary, etc.
    author: Optional[str] = None
    specialty: Optional[str] = None
    content: str
    encounter_id: Optional[str] = None


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
    
    async def get_comprehensive_history(
        self,
        patient_id: str,
        lookback_days: int = 365,
        include_resolved: bool = True
    ) -> ComprehensivePatientHistory:
        """
        Retrieve comprehensive patient history for diagnostic decision support.
        
        Args:
            patient_id: FHIR Patient resource ID
            lookback_days: Number of days to look back for historical data
            include_resolved: Include resolved/inactive conditions
            
        Returns:
            ComprehensivePatientHistory with all available patient data
        """
        headers = await self._get_headers()
        lookback_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
        
        # Fetch patient demographics
        patient_data = await self._fetch_patient_demographics(patient_id, headers)
        
        # Fetch visit notes (DocumentReference)
        visit_notes = await self._fetch_visit_notes(patient_id, lookback_date, headers)
        
        # Fetch vital signs (Observation with vital-signs category)
        vital_signs = await self._fetch_vital_signs(patient_id, lookback_date, headers)
        
        # Fetch diagnostic tests (Observation + DiagnosticReport)
        diagnostic_tests = await self._fetch_diagnostic_tests(patient_id, lookback_date, headers)
        
        # Fetch H&Ps (specific DocumentReference type)
        history_and_physicals = await self._fetch_history_and_physicals(patient_id, lookback_date, headers)
        
        # Fetch procedures (Procedure)
        procedures = await self._fetch_procedures(patient_id, lookback_date, headers)
        
        # Fetch imaging studies (ImagingStudy + DiagnosticReport)
        imaging_studies = await self._fetch_imaging_studies(patient_id, lookback_date, headers)
        
        # Fetch conditions (active and resolved)
        active_conditions, past_conditions = await self._fetch_conditions(patient_id, include_resolved, headers)
        
        # Fetch medications (current and historical)
        current_meds, med_history = await self._fetch_medications(patient_id, headers)
        
        # Fetch allergies
        allergies = await self._fetch_allergies(patient_id, headers)
        
        # Fetch family and social history
        family_history, social_history = await self._fetch_family_social_history(patient_id, headers)
        
        # Generate summary
        summary = self._generate_summary(
            patient_data,
            active_conditions,
            current_meds,
            diagnostic_tests,
            visit_notes
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
            active_conditions=active_conditions,
            past_conditions=past_conditions,
            current_medications=current_meds,
            medication_history=med_history,
            allergies=allergies,
            family_history=family_history,
            social_history=social_history,
            summary=summary
        )
    
    async def _fetch_patient_demographics(self, patient_id: str, headers: Dict) -> Dict[str, Any]:
        """Fetch patient demographics."""
        try:
            response = await self.client.get(
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
            return {}
    
    async def _fetch_visit_notes(self, patient_id: str, lookback_date: str, headers: Dict) -> List[VisitNote]:
        """Fetch clinical visit notes via DocumentReference."""
        visit_notes = []
        
        try:
            response = await self.client.get(
                f"{self.fhir_base_url}/DocumentReference?patient={patient_id}&date=ge{lookback_date}&_sort=-date&_count=50",
                headers=headers
            )
            
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
                                content = f"[Document URL: {attachment['url']}]"
                    
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
                        encounter_id=doc.get('context', {}).get('encounter', [{}])[0].get('reference')
                    ))
        
        except Exception as e:
            print(f"Error fetching visit notes: {e}")
        
        return visit_notes
    
    async def _fetch_vital_signs(self, patient_id: str, lookback_date: str, headers: Dict) -> List[VitalSigns]:
        """Fetch vital signs from FHIR Observations with vital-signs category."""
        vital_signs_list = []
        
        try:
            response = await self.client.get(
                f"{self.fhir_base_url}/Observation?patient={patient_id}&category=vital-signs&date=ge{lookback_date}&_sort=-date&_count=100",
                headers=headers
            )
            
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
        
        return vital_signs_list
    
    async def _fetch_diagnostic_tests(self, patient_id: str, lookback_date: str, headers: Dict) -> List[DiagnosticTest]:
        """Fetch diagnostic test results (labs, etc.)."""
        diagnostic_tests = []
        
        try:
            # Fetch Observations (lab results)
            response = await self.client.get(
                f"{self.fhir_base_url}/Observation?patient={patient_id}&date=ge{lookback_date}&_sort=-date&_count=100",
                headers=headers
            )
            
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
            response = await self.client.get(
                f"{self.fhir_base_url}/DiagnosticReport?patient={patient_id}&date=ge{lookback_date}&_sort=-date&_count=50",
                headers=headers
            )
            
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
        
        return diagnostic_tests
    
    async def _fetch_history_and_physicals(self, patient_id: str, lookback_date: str, headers: Dict) -> List[HistoryAndPhysical]:
        """Fetch History and Physical examinations."""
        h_and_ps = []
        
        try:
            # Query for H&P document type (LOINC code 34117-2)
            response = await self.client.get(
                f"{self.fhir_base_url}/DocumentReference?patient={patient_id}&type=34117-2&date=ge{lookback_date}&_sort=-date&_count=20",
                headers=headers
            )
            
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
                    
                    # Parse sections from content (simplified - actual parsing would be more complex)
                    h_and_p = self._parse_h_and_p_content(content, date, author)
                    h_and_ps.append(h_and_p)
        
        except Exception as e:
            print(f"Error fetching H&Ps: {e}")
        
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
    
    async def _fetch_procedures(self, patient_id: str, lookback_date: str, headers: Dict) -> List[Procedure]:
        """Fetch procedures performed."""
        procedures = []
        
        try:
            response = await self.client.get(
                f"{self.fhir_base_url}/Procedure?patient={patient_id}&date=ge{lookback_date}&_sort=-date&_count=50",
                headers=headers
            )
            
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
        
        return procedures
    
    async def _fetch_imaging_studies(self, patient_id: str, lookback_date: str, headers: Dict) -> List[ImagingStudy]:
        """Fetch imaging studies."""
        imaging_studies = []
        
        try:
            response = await self.client.get(
                f"{self.fhir_base_url}/ImagingStudy?patient={patient_id}&started=ge{lookback_date}&_sort=-started&_count=50",
                headers=headers
            )
            
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
                        report_response = await self.client.get(
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
        
        return imaging_studies
    
    async def _fetch_conditions(self, patient_id: str, include_resolved: bool, headers: Dict) -> tuple:
        """Fetch active and resolved conditions."""
        active_conditions = []
        past_conditions = []
        
        try:
            # Fetch active conditions
            response = await self.client.get(
                f"{self.fhir_base_url}/Condition?patient={patient_id}&clinical-status=active&_count=50",
                headers=headers
            )
            
            if response.status_code == 200:
                bundle = response.json()
                
                for entry in bundle.get('entry', []):
                    condition = entry.get('resource', {})
                    active_conditions.append({
                        'code': condition.get('code', {}).get('text', 'Unknown'),
                        'status': 'active',
                        'recorded_date': condition.get('recordedDate'),
                        'onset': condition.get('onsetDateTime')
                    })
            
            # Fetch resolved conditions if requested
            if include_resolved:
                response = await self.client.get(
                    f"{self.fhir_base_url}/Condition?patient={patient_id}&clinical-status=resolved,inactive&_count=50",
                    headers=headers
                )
                
                if response.status_code == 200:
                    bundle = response.json()
                    
                    for entry in bundle.get('entry', []):
                        condition = entry.get('resource', {})
                        past_conditions.append({
                            'code': condition.get('code', {}).get('text', 'Unknown'),
                            'status': condition.get('clinicalStatus', {}).get('coding', [{}])[0].get('code', 'resolved'),
                            'recorded_date': condition.get('recordedDate'),
                            'abatement': condition.get('abatementDateTime')
                        })
        
        except Exception as e:
            print(f"Error fetching conditions: {e}")
        
        return active_conditions, past_conditions
    
    async def _fetch_medications(self, patient_id: str, headers: Dict) -> tuple:
        """Fetch current and historical medications."""
        current_meds = []
        med_history = []
        
        try:
            # Current medications
            response = await self.client.get(
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
            response = await self.client.get(
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
                    
                    med_history.append({
                        'name': med_name,
                        'status': med.get('status'),
                        'date_prescribed': med.get('authoredOn'),
                        'date_stopped': med.get('statusChanged')
                    })
        
        except Exception as e:
            print(f"Error fetching medications: {e}")
        
        return current_meds, med_history
    
    async def _fetch_allergies(self, patient_id: str, headers: Dict) -> List[str]:
        """Fetch patient allergies."""
        allergies = []
        
        try:
            response = await self.client.get(
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
        
        return allergies
    
    async def _fetch_family_social_history(self, patient_id: str, headers: Dict) -> tuple:
        """Fetch family and social history."""
        family_history = None
        social_history = None
        
        try:
            # Family history (FamilyMemberHistory or Observation with category)
            response = await self.client.get(
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
            response = await self.client.get(
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
        
        return family_history, social_history
    
    def _generate_summary(
        self,
        patient_data: Dict,
        active_conditions: List[Dict],
        current_meds: List[Dict],
        diagnostic_tests: List[DiagnosticTest],
        visit_notes: List[VisitNote]
    ) -> str:
        """Generate a clinical summary of patient history."""
        summary_parts = []
        
        # Patient intro
        name = patient_data.get('name', 'Patient')
        age = patient_data.get('age', 'unknown age')
        gender = patient_data.get('gender', 'unknown gender')
        summary_parts.append(f"{name} is a {age}-year-old {gender} with")
        
        # Active conditions
        if active_conditions:
            conditions_list = [c['code'] for c in active_conditions[:5]]
            summary_parts.append(f"history of {', '.join(conditions_list)}")
        else:
            summary_parts.append("no significant past medical history")
        
        # Recent visits
        if visit_notes:
            summary_parts.append(f"Recent visits: {len(visit_notes)} clinical encounters in the past year")
        
        # Abnormal labs
        abnormal_tests = [t for t in diagnostic_tests if t.abnormal]
        if abnormal_tests:
            summary_parts.append(f"{len(abnormal_tests)} abnormal test results noted")
        
        # Current medications
        if current_meds:
            summary_parts.append(f"Currently on {len(current_meds)} medications")
        
        return ". ".join(summary_parts) + "."
