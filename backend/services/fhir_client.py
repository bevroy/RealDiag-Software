"""
FHIR Client for Epic EHR Integration

Implements FHIR R4 API client for reading patient data from Epic and other
EHR systems. Supports OAuth 2.0 authentication and SMART on FHIR launch.

Usage:
    client = FHIRClient(
        fhir_base_url="https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
        client_id="your_client_id",
        client_secret="your_client_secret"
    )

    patient_data = client.get_patient_data(patient_id="eXg4k...")
"""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class FHIRResourceType(Enum):
    """FHIR resource types used in clinical decision support."""
    PATIENT = "Patient"
    OBSERVATION = "Observation"
    CONDITION = "Condition"
    MEDICATION_REQUEST = "MedicationRequest"
    DIAGNOSTIC_REPORT = "DiagnosticReport"
    PROCEDURE = "Procedure"
    ALLERGY_INTOLERANCE = "AllergyIntolerance"
    ENCOUNTER = "Encounter"


@dataclass
class LabResult:
    """Structured lab result from FHIR Observation."""
    code: str  # LOINC code
    display: str  # Human-readable name
    value: float
    unit: str
    reference_range: Optional[Dict[str, float]] = None
    status: str = "final"
    effective_date: Optional[datetime] = None
    is_abnormal: bool = False

    def __post_init__(self):
        """Check if value is outside reference range."""
        if self.reference_range:
            low = self.reference_range.get("low")
            high = self.reference_range.get("high")
            if low and self.value < low:
                self.is_abnormal = True
            if high and self.value > high:
                self.is_abnormal = True


@dataclass
class VitalSign:
    """Vital sign measurement from FHIR Observation."""
    code: str  # LOINC code
    display: str
    value: float
    unit: str
    effective_date: datetime


@dataclass
class PatientData:
    """Aggregated patient data from FHIR resources."""
    patient_id: str
    name: str
    age: int
    gender: str
    labs: List[LabResult]
    vitals: List[VitalSign]
    conditions: List[Dict[str, Any]]
    medications: List[Dict[str, Any]]
    allergies: List[Dict[str, Any]]

    def get_lab(self, loinc_code: str) -> Optional[LabResult]:
        """Get most recent lab result by LOINC code."""
        matching_labs = [lab for lab in self.labs if lab.code == loinc_code]
        if not matching_labs:
            return None
        # Return most recent
        return sorted(matching_labs, key=lambda x: x.effective_date or datetime.min, reverse=True)[0]

    def get_vital(self, loinc_code: str) -> Optional[VitalSign]:
        """Get most recent vital sign by LOINC code."""
        matching_vitals = [v for v in self.vitals if v.code == loinc_code]
        if not matching_vitals:
            return None
        return sorted(matching_vitals, key=lambda x: x.effective_date, reverse=True)[0]


class FHIRClient:
    """
    FHIR R4 API client for Epic and other EHR systems.

    Handles OAuth 2.0 authentication, resource queries, and data parsing.
    """

    def __init__(
        self,
        fhir_base_url: str,
        client_id: str,
        client_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        token_url: Optional[str] = None
    ):
        """
        Initialize FHIR client.

        Args:
            fhir_base_url: Base URL for FHIR API (e.g., https://fhir.epic.com/...)
            client_id: OAuth client ID
            client_secret: OAuth client secret (for backend apps)
            access_token: Pre-obtained access token (for SMART launch)
            token_url: Explicit OAuth token endpoint override (vendor-specific;
                falls back to guessing "{fhir_base_url}/oauth2/token" if omitted)
        """
        self.fhir_base_url = fhir_base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = access_token
        self._token_expiry = None
        self._token_url = token_url

    def authenticate(self, authorization_code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token (SMART on FHIR).

        Args:
            authorization_code: Authorization code from OAuth flow
            redirect_uri: Redirect URI used in authorization request

        Returns:
            Token response with access_token, refresh_token, etc.
        """
        token_url = self._token_url or f"{self.fhir_base_url}/oauth2/token"

        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id
        }

        # Cerner/Oracle Health's EHR-launch token exchange doesn't send the
        # confidential-client secret - just client_id, per Oracle's own docs.

        response = requests.post(token_url, data=data); logger.error(f"Cerner token exchange {response.status_code}: {response.text}") if not response.ok else None
        response.raise_for_status()

        token_data = response.json()
        self._access_token = token_data["access_token"]

        if "expires_in" in token_data:
            self._token_expiry = datetime.now() + timedelta(seconds=token_data["expires_in"])

        logger.info(f"Authenticated successfully. Token expires at {self._token_expiry}")
        return token_data

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authorization."""
        if not self._access_token:
            raise ValueError("No access token available. Call authenticate() first.")

        return {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json"
        }

    def _query_resource(
        self,
        resource_type: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query FHIR resource.

        Args:
            resource_type: FHIR resource type (Patient, Observation, etc.)
            params: Query parameters

        Returns:
            FHIR Bundle with results
        """
        url = f"{self.fhir_base_url}/{resource_type}"

        try:
            response = requests.get(url, params=params, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"FHIR query failed: {e}")
            raise

    def get_patient(self, patient_id: str) -> Dict[str, Any]:
        """Get patient demographics."""
        url = f"{self.fhir_base_url}/Patient/{patient_id}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_observations(
        self,
        patient_id: str,
        category: Optional[str] = None,
        code: Optional[str] = None,
        date_range: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get patient observations (labs, vitals).

        Args:
            patient_id: Patient ID
            category: laboratory, vital-signs, etc.
            code: LOINC code filter
            date_range: Date range (e.g., "gt2024-01-01")

        Returns:
            List of Observation resources
        """
        params = {"patient": patient_id, "_count": 100}

        if category:
            params["category"] = category
        if code:
            params["code"] = code
        if date_range:
            params["date"] = date_range

        bundle = self._query_resource(FHIRResourceType.OBSERVATION.value, params)

        observations = []
        if bundle.get("entry"):
            observations = [entry["resource"] for entry in bundle["entry"]]

        return observations

    def get_conditions(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get patient's active conditions/problems."""
        params = {
            "patient": patient_id,
            "clinical-status": "active",
            "_count": 100
        }

        bundle = self._query_resource(FHIRResourceType.CONDITION.value, params)

        conditions = []
        if bundle.get("entry"):
            conditions = [entry["resource"] for entry in bundle["entry"]]

        return conditions

    def get_medications(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get patient's active medications."""
        params = {
            "patient": patient_id,
            "status": "active",
            "_count": 100
        }

        bundle = self._query_resource(FHIRResourceType.MEDICATION_REQUEST.value, params)

        medications = []
        if bundle.get("entry"):
            medications = [entry["resource"] for entry in bundle["entry"]]

        return medications

    def get_allergies(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get patient allergies."""
        params = {"patient": patient_id, "_count": 100}

        bundle = self._query_resource(FHIRResourceType.ALLERGY_INTOLERANCE.value, params)

        allergies = []
        if bundle.get("entry"):
            allergies = [entry["resource"] for entry in bundle["entry"]]

        return allergies

    def parse_observation(self, observation: Dict[str, Any]) -> Optional[LabResult]:
        """
        Parse FHIR Observation into LabResult.

        Args:
            observation: FHIR Observation resource

        Returns:
            LabResult or None if parsing fails
        """
        try:
            # Get code (LOINC)
            code_obj = observation.get("code", {})
            coding = code_obj.get("coding", [{}])[0]
            code = coding.get("code")
            display = coding.get("display", code_obj.get("text", "Unknown"))

            # Get value
            value_qty = observation.get("valueQuantity", {})
            if not value_qty:
                return None  # No numeric value

            value = float(value_qty.get("value", 0))
            unit = value_qty.get("unit", "")

            # Get reference range
            reference_range = None
            if observation.get("referenceRange"):
                ref = observation["referenceRange"][0]
                low_val = ref.get("low", {}).get("value")
                high_val = ref.get("high", {}).get("value")
                if low_val or high_val:
                    reference_range = {}
                    if low_val:
                        reference_range["low"] = float(low_val)
                    if high_val:
                        reference_range["high"] = float(high_val)

            # Get effective date
            effective_date = None
            if observation.get("effectiveDateTime"):
                effective_date = datetime.fromisoformat(
                    observation["effectiveDateTime"].replace("Z", "+00:00")
                )

            status = observation.get("status", "final")

            return LabResult(
                code=code,
                display=display,
                value=value,
                unit=unit,
                reference_range=reference_range,
                status=status,
                effective_date=effective_date
            )
        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"Failed to parse observation: {e}")
            return None

    def get_encounters(
        self,
        patient_id: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get patient encounters (visits/admissions), optionally filtered by status."""
        params = {"patient": patient_id, "_count": 20, "_sort": "-date"}
        if status:
            params["status"] = status

        bundle = self._query_resource("Encounter", params)

        encounters = []
        if bundle.get("entry"):
            encounters = [entry["resource"] for entry in bundle["entry"]]

        return encounters

    def get_current_encounter(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the patient's current (in-progress) encounter/admission, if any.

        Returns:
            The FHIR Encounter resource for the active admission, or None if
            the patient has no in-progress encounter (e.g., not currently
            admitted).
        """
        encounters = self.get_encounters(patient_id, status="in-progress")

        if not encounters:
            return None

        def _start(enc):
            return enc.get("period", {}).get("start") or ""

        encounters.sort(key=_start, reverse=True)
        return encounters[0]

    def get_patient_updates_since(
        self,
        patient_id: str,
        since: datetime
    ) -> Dict[str, Any]:
        """
        Get everything new for a patient since a given timestamp - the basis
        for shift-handoff / "what's changed since admission" summaries.

        Unlike get_patient_data(), this is NOT limited to a fixed 7/30-day
        lookback window - it queries from the exact timestamp given, however
        long ago that was (e.g., the start of a multi-week admission).

        Returns:
            Dict with new_labs, new_abnormal_labs, new_vitals, new_conditions,
            new_medications.
        """
        since_str = since.strftime("%Y-%m-%d")

        lab_observations = self.get_observations(
            patient_id, category="laboratory", date_range=f"ge{since_str}"
        )
        new_labs = []
        for obs in lab_observations:
            lab = self.parse_observation(obs)
            if lab:
                new_labs.append(lab)
        new_abnormal_labs = [lab for lab in new_labs if lab.is_abnormal]

        vital_observations = self.get_observations(
            patient_id, category="vital-signs", date_range=f"ge{since_str}"
        )
        new_vitals = []
        for obs in vital_observations:
            try:
                code_obj = obs.get("code", {})
                coding = code_obj.get("coding", [{}])[0]
                code = coding.get("code")
                display = coding.get("display", "Unknown")

                value_qty = obs.get("valueQuantity", {})
                value = float(value_qty.get("value", 0))
                unit = value_qty.get("unit", "")

                effective_date = datetime.fromisoformat(
                    obs["effectiveDateTime"].replace("Z", "+00:00")
                )

                new_vitals.append(VitalSign(
                    code=code, display=display, value=value,
                    unit=unit, effective_date=effective_date
                ))
            except (KeyError, ValueError):
                continue

        condition_bundle = self._query_resource("Condition", {
            "patient": patient_id, "_count": 100, "recorded-date": f"ge{since_str}"
        })
        new_conditions = []
        if condition_bundle.get("entry"):
            new_conditions = [entry["resource"] for entry in condition_bundle["entry"]]

        medication_bundle = self._query_resource("MedicationRequest", {
            "patient": patient_id, "_count": 100, "authoredon": f"ge{since_str}"
        })
        new_medications = []
        if medication_bundle.get("entry"):
            new_medications = [entry["resource"] for entry in medication_bundle["entry"]]

        return {
            "new_labs": new_labs,
            "new_abnormal_labs": new_abnormal_labs,
            "new_vitals": new_vitals,
            "new_conditions": new_conditions,
            "new_medications": new_medications,
        }

    def _safe_fetch_list(self, fetch_fn, patient_id: str, label: str) -> List[Dict[str, Any]]:
        """Call a per-resource-type FHIR fetch; return [] instead of
        raising if that resource type is unavailable (e.g. a 403 because
        the API isn't enabled in the app's EHR registration)."""
        try:
            return fetch_fn(patient_id)
        except requests.RequestException as e:
            logger.warning(f"Skipping {label} - FHIR query failed: {e}")
            return []

    def get_patient_data(self, patient_id: str) -> PatientData:
        """
        Get comprehensive patient data for clinical decision support.

        Args:
            patient_id: Patient FHIR ID

        Returns:
            PatientData object with aggregated clinical information
        """
        logger.info(f"Fetching patient data for {patient_id}")

        # Get patient demographics
        patient = self.get_patient(patient_id)
        name_obj = patient.get("name", [{}])[0]
        given = " ".join(name_obj.get("given", []))
        family = name_obj.get("family", "")
        full_name = f"{given} {family}".strip()

        # Calculate age from birthDate
        age = 0
        if patient.get("birthDate"):
            birth_date = datetime.strptime(patient["birthDate"], "%Y-%m-%d")
            age = (datetime.now() - birth_date).days // 365

        gender = patient.get("gender", "unknown")

        # Get labs (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        lab_observations = self.get_observations(
            patient_id,
            category="laboratory",
            date_range=f"gt{thirty_days_ago}"
        )

        labs = []
        for obs in lab_observations:
            lab = self.parse_observation(obs)
            if lab:
                labs.append(lab)

        # Get vitals (last 7 days)
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        vital_observations = self.get_observations(
            patient_id,
            category="vital-signs",
            date_range=f"gt{seven_days_ago}"
        )

        vitals = []
        for obs in vital_observations:
            try:
                code_obj = obs.get("code", {})
                coding = code_obj.get("coding", [{}])[0]
                code = coding.get("code")
                display = coding.get("display", "Unknown")

                value_qty = obs.get("valueQuantity", {})
                value = float(value_qty.get("value", 0))
                unit = value_qty.get("unit", "")

                effective_date = datetime.fromisoformat(
                    obs["effectiveDateTime"].replace("Z", "+00:00")
                )

                vitals.append(VitalSign(
                    code=code,
                    display=display,
                    value=value,
                    unit=unit,
                    effective_date=effective_date
                ))
            except (KeyError, ValueError):
                continue

        # Get conditions, medications, allergies - each independently, so a
        # single resource type being unavailable (e.g. a 403 because that
        # API isn't enabled in the app's EHR registration) doesn't take
        # down the whole patient summary.
        conditions = self._safe_fetch_list(self.get_conditions, patient_id, "conditions")
        medications = self._safe_fetch_list(self.get_medications, patient_id, "medications")
        allergies = self._safe_fetch_list(self.get_allergies, patient_id, "allergies")

        patient_data = PatientData(
            patient_id=patient_id,
            name=full_name,
            age=age,
            gender=gender,
            labs=labs,
            vitals=vitals,
            conditions=conditions,
            medications=medications,
            allergies=allergies
        )

        logger.info(
            f"Retrieved data for {full_name}: "
            f"{len(labs)} labs, {len(vitals)} vitals, "
            f"{len(conditions)} conditions, {len(medications)} medications"
        )

        return patient_data


# Common LOINC codes for quick reference
class CommonLOINC:
    """Commonly used LOINC codes for clinical decision support."""

    # Cardiac markers
    TROPONIN_I = "10839-9"
    TROPONIN_T = "6598-7"
    BNP = "30934-4"
    CK_MB = "13969-1"

    # Complete blood count
    WBC = "6690-2"
    HEMOGLOBIN = "718-7"
    HEMATOCRIT = "4544-3"
    PLATELETS = "777-3"

    # Metabolic panel
    SODIUM = "2951-2"
    POTASSIUM = "2823-3"
    CHLORIDE = "2075-0"
    CO2 = "2028-9"
    BUN = "3094-0"
    CREATININE = "2160-0"
    GLUCOSE = "2345-7"

    # Liver function
    AST = "1920-8"
    ALT = "1742-6"
    ALKALINE_PHOS = "6768-6"
    BILIRUBIN_TOTAL = "1975-2"
    ALBUMIN = "1751-7"

    # Coagulation
    PT = "5902-2"
    INR = "6301-6"
    PTT = "3173-2"

    # Vitals (LOINC codes)
    SYSTOLIC_BP = "8480-6"
    DIASTOLIC_BP = "8462-4"
    HEART_RATE = "8867-4"
    RESPIRATORY_RATE = "9279-1"
    TEMPERATURE = "8310-5"
    OXYGEN_SAT = "59408-5"
    WEIGHT = "29463-7"
    HEIGHT = "8302-2"
    BMI = "39156-5"
    GCS_SCORE = "9269-2"
