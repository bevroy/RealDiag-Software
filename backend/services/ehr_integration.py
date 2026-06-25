"""
EHR Integration Service
=======================

Pull patient data from EHR systems via FHIR API, integrate with CPOE systems
for ordering tests and referrals.
"""

from fastapi import HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
from pydantic import BaseModel, Field


class FHIRServerConfig(BaseModel):
    """Configuration for FHIR server connection."""
    base_url: str
    auth_type: str = Field(default="none", description="none, basic, bearer, oauth2")
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None


class PatientData(BaseModel):
    """Structured patient data from FHIR."""
    patient_id: str
    name: str
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    age: Optional[int] = None
    allergies: List[str] = []
    conditions: List[Dict[str, Any]] = []
    medications: List[Dict[str, Any]] = []
    recent_vitals: Dict[str, Any] = {}
    recent_labs: List[Dict[str, Any]] = []


class CPOEOrder(BaseModel):
    """CPOE order for tests or referrals."""
    order_type: str = Field(description="lab, imaging, referral, medication")
    description: str
    patient_id: str
    encounter_id: Optional[str] = None
    priority: str = Field(default="routine", description="stat, urgent, routine")
    ordering_provider: str
    clinical_indication: Optional[str] = None
    diagnosis_codes: List[str] = []


class EHRIntegrationService:
    """Service for integrating with EHR systems via FHIR."""
    
    def __init__(self, config: Optional[FHIRServerConfig] = None):
        self.config = config
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authentication."""
        headers = {
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json"
        }
        
        if not self.config:
            return headers
        
        if self.config.auth_type == "bearer" and self.config.token:
            headers["Authorization"] = f"Bearer {self.config.token}"
        elif self.config.auth_type == "basic" and self.config.username:
            import base64
            credentials = f"{self.config.username}:{self.config.password or ''}"
            encoded = base64.b64encode(credentials.encode()).decode()
            headers["Authorization"] = f"Basic {encoded}"
        
        return headers
    
    async def pull_patient_data(self, patient_id: str) -> PatientData:
        """
        Pull comprehensive patient data from FHIR server.
        
        Args:
            patient_id: FHIR Patient resource ID
            
        Returns:
            PatientData with demographics, conditions, medications, vitals, labs
        """
        if not self.config:
            raise HTTPException(status_code=500, detail="FHIR server not configured")
        
        headers = await self._get_headers()
        base_url = self.config.base_url.rstrip('/')
        
        # Fetch patient demographics
        patient_response = await self.client.get(
            f"{base_url}/Patient/{patient_id}",
            headers=headers
        )
        
        if patient_response.status_code != 200:
            raise HTTPException(
                status_code=patient_response.status_code,
                detail=f"Failed to fetch patient: {patient_response.text}"
            )
        
        patient_resource = patient_response.json()
        
        # Extract demographics
        name = "Unknown"
        if patient_resource.get('name'):
            name_obj = patient_resource['name'][0]
            given = ' '.join(name_obj.get('given', []))
            family = name_obj.get('family', '')
            name = f"{given} {family}".strip()
        
        birth_date = patient_resource.get('birthDate')
        age = None
        if birth_date:
            from datetime import date
            birth = datetime.strptime(birth_date, "%Y-%m-%d").date()
            today = date.today()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        
        # Fetch conditions
        conditions = []
        try:
            conditions_response = await self.client.get(
                f"{base_url}/Condition?patient={patient_id}&_count=20",
                headers=headers
            )
            if conditions_response.status_code == 200:
                bundle = conditions_response.json()
                for entry in bundle.get('entry', []):
                    condition = entry.get('resource', {})
                    if condition:
                        conditions.append({
                            'code': condition.get('code', {}).get('text', 'Unknown'),
                            'status': condition.get('clinicalStatus', {}).get('coding', [{}])[0].get('code', 'unknown'),
                            'recorded_date': condition.get('recordedDate')
                        })
        except Exception as e:
            print(f"Error fetching conditions: {e}")
        
        # Fetch allergies
        allergies = []
        try:
            allergies_response = await self.client.get(
                f"{base_url}/AllergyIntolerance?patient={patient_id}",
                headers=headers
            )
            if allergies_response.status_code == 200:
                bundle = allergies_response.json()
                for entry in bundle.get('entry', []):
                    allergy = entry.get('resource', {})
                    if allergy:
                        allergen = allergy.get('code', {}).get('text') or \
                                 allergy.get('code', {}).get('coding', [{}])[0].get('display')
                        if allergen:
                            allergies.append(allergen)
        except Exception as e:
            print(f"Error fetching allergies: {e}")
        
        # Fetch medications
        medications = []
        try:
            meds_response = await self.client.get(
                f"{base_url}/MedicationRequest?patient={patient_id}&status=active&_count=20",
                headers=headers
            )
            if meds_response.status_code == 200:
                bundle = meds_response.json()
                for entry in bundle.get('entry', []):
                    med = entry.get('resource', {})
                    if med:
                        med_name = med.get('medicationCodeableConcept', {}).get('text') or \
                                  med.get('medicationCodeableConcept', {}).get('coding', [{}])[0].get('display')
                        if med_name:
                            medications.append({
                                'name': med_name,
                                'status': med.get('status', 'unknown')
                            })
        except Exception as e:
            print(f"Error fetching medications: {e}")
        
        # Fetch recent vitals
        recent_vitals = {}
        try:
            vitals_response = await self.client.get(
                f"{base_url}/Observation?patient={patient_id}&category=vital-signs&_count=10&_sort=-date",
                headers=headers
            )
            if vitals_response.status_code == 200:
                bundle = vitals_response.json()
                for entry in bundle.get('entry', []):
                    obs = entry.get('resource', {})
                    code = obs.get('code', {}).get('coding', [{}])[0].get('display', '')
                    value = obs.get('valueQuantity', {})
                    if code and value:
                        recent_vitals[code] = f"{value.get('value')} {value.get('unit', '')}"
        except Exception as e:
            print(f"Error fetching vitals: {e}")
        
        # Fetch recent labs
        recent_labs = []
        try:
            labs_response = await self.client.get(
                f"{base_url}/Observation?patient={patient_id}&category=laboratory&_count=20&_sort=-date",
                headers=headers
            )
            if labs_response.status_code == 200:
                bundle = labs_response.json()
                for entry in bundle.get('entry', []):
                    obs = entry.get('resource', {})
                    test_name = obs.get('code', {}).get('text') or \
                               obs.get('code', {}).get('coding', [{}])[0].get('display')
                    value = obs.get('valueQuantity', {}) or obs.get('valueString', '')
                    if test_name:
                        recent_labs.append({
                            'test': test_name,
                            'value': f"{value.get('value', '')} {value.get('unit', '')}" if isinstance(value, dict) else str(value),
                            'date': obs.get('effectiveDateTime', 'Unknown')
                        })
        except Exception as e:
            print(f"Error fetching labs: {e}")
        
        return PatientData(
            patient_id=patient_id,
            name=name,
            gender=patient_resource.get('gender'),
            birth_date=birth_date,
            age=age,
            allergies=allergies,
            conditions=conditions,
            medications=medications,
            recent_vitals=recent_vitals,
            recent_labs=recent_labs
        )
    
    async def create_cpoe_order(self, order: CPOEOrder) -> Dict[str, Any]:
        """
        Create order in CPOE system via FHIR ServiceRequest.
        
        Args:
            order: CPOE order details
            
        Returns:
            Created ServiceRequest resource
        """
        if not self.config:
            raise HTTPException(status_code=500, detail="FHIR server not configured")
        
        headers = await self._get_headers()
        base_url = self.config.base_url.rstrip('/')
        
        # Build FHIR ServiceRequest
        service_request = {
            "resourceType": "ServiceRequest",
            "status": "active",
            "intent": "order",
            "priority": order.priority,
            "code": {
                "text": order.description
            },
            "subject": {
                "reference": f"Patient/{order.patient_id}"
            },
            "authoredOn": datetime.now().isoformat(),
            "requester": {
                "display": order.ordering_provider
            }
        }
        
        if order.encounter_id:
            service_request["encounter"] = {
                "reference": f"Encounter/{order.encounter_id}"
            }
        
        if order.clinical_indication:
            service_request["reasonCode"] = [{
                "text": order.clinical_indication
            }]
        
        if order.diagnosis_codes:
            service_request["reasonCode"] = service_request.get("reasonCode", [])
            for code in order.diagnosis_codes:
                service_request["reasonCode"].append({
                    "coding": [{
                        "system": "http://hl7.org/fhir/sid/icd-10-cm",
                        "code": code
                    }]
                })
        
        # Post to FHIR server
        response = await self.client.post(
            f"{base_url}/ServiceRequest",
            headers=headers,
            json=service_request
        )
        
        if response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to create order: {response.text}"
            )
        
        return response.json()
    
    async def search_patients(
        self,
        name: Optional[str] = None,
        identifier: Optional[str] = None,
        birth_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for patients in EHR.
        
        Args:
            name: Patient name
            identifier: Medical record number or other identifier
            birth_date: Birth date (YYYY-MM-DD)
            
        Returns:
            List of matching patient resources
        """
        if not self.config:
            raise HTTPException(status_code=500, detail="FHIR server not configured")
        
        headers = await self._get_headers()
        base_url = self.config.base_url.rstrip('/')
        
        params = []
        if name:
            params.append(f"name={name}")
        if identifier:
            params.append(f"identifier={identifier}")
        if birth_date:
            params.append(f"birthdate={birth_date}")
        
        query_string = "&".join(params) if params else "_count=10"
        
        response = await self.client.get(
            f"{base_url}/Patient?{query_string}",
            headers=headers
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Patient search failed: {response.text}"
            )
        
        bundle = response.json()
        patients = []
        
        for entry in bundle.get('entry', []):
            patient = entry.get('resource', {})
            if patient:
                patients.append({
                    'id': patient.get('id'),
                    'name': self._extract_name(patient),
                    'gender': patient.get('gender'),
                    'birth_date': patient.get('birthDate')
                })
        
        return patients
    
    def _extract_name(self, patient_resource: Dict) -> str:
        """Extract formatted name from FHIR Patient resource."""
        if not patient_resource.get('name'):
            return "Unknown"
        
        name_obj = patient_resource['name'][0]
        given = ' '.join(name_obj.get('given', []))
        family = name_obj.get('family', '')
        return f"{given} {family}".strip()
