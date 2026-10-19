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
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# Configurable lookback windows for the default (non-"since") chart summary.
# Kept short in production so an active inpatient chart summary stays
# recent; widened via env var for testing against static/historical data
# (e.g. Epic's sandbox test patients, whose records predate any fixed window).
LAB_LOOKBACK_DAYS = int(os.getenv("LAB_LOOKBACK_DAYS", "30"))
VITAL_LOOKBACK_DAYS = int(os.getenv("VITAL_LOOKBACK_DAYS", "7"))
# Pages (of up to 100 results) to follow for the longer criteria lookback
CRITERIA_MAX_PAGES = int(os.getenv("CRITERIA_MAX_PAGES", "10"))


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


LOINC_SYSTEM = "http://loinc.org"

# Observation / resource statuses that must never feed clinical logic.
EXCLUDED_STATUSES = {"entered-in-error", "cancelled"}

# Per-resource retrieval status values carried in PatientData and API responses.
RETRIEVED = "retrieved"          # query succeeded; an empty list means none found
FAILED = "failed"                # query errored; contents unknown
NOT_AVAILABLE = "not available"  # resource type not enabled/supported by this EHR

# Human-readable resource names for retrieval warnings.
RESOURCE_LABELS = {
    "labs": "Lab results",
    "vitals": "Vital signs",
    "conditions": "Conditions",
    "medications": "Medications",
    "allergies": "Allergies",
    # PatientHistoryService data types
    "demographics": "Patient demographics",
    "visit_notes": "Visit notes",
    "vital_signs": "Vital signs",
    "diagnostic_tests": "Diagnostic test results",
    "history_and_physicals": "History and physicals",
    "procedures": "Procedures",
    "imaging_studies": "Imaging studies",
    "immunizations": "Immunizations",
    "family_social_history": "Family and social history",
}


def retrieval_warnings(retrieval_status: Dict[str, str]) -> List[str]:
    """Plain-language warnings for every resource that could not be retrieved."""
    warnings = []
    for resource, status in retrieval_status.items():
        if status != RETRIEVED:
            label = RESOURCE_LABELS.get(resource, resource.capitalize())
            warnings.append(f"{label} could not be retrieved; do not assume none.")
    return warnings


_STATUS_RANK = {RETRIEVED: 0, NOT_AVAILABLE: 1, FAILED: 2}


def truncation_warning(resource: str, event: Dict[str, Any]) -> str:
    """Visible note when the page limit stopped a query before all results were retrieved."""
    label = RESOURCE_LABELS.get(resource, resource.capitalize())
    covered = (f", dated {event['first']} to {event['last']}" if event.get("first") else "")
    window = f" since {event['since']}" if event.get("since") else ""
    return (f"{label} cut off: the page limit was reached after {event['count']} results{covered}. "
            f"Other results{window} were not retrieved and were not assessed.")


def _record_status(status: Dict[str, str], resource: str, outcome: str) -> None:
    """Keep the worst outcome when one resource needs several queries."""
    if resource not in status or _STATUS_RANK[outcome] > _STATUS_RANK[status[resource]]:
        status[resource] = outcome


def _merge_results(existing: List[Any], extra: List[Any]) -> List[Any]:
    """Append results not already present (same code, time, value and unit)."""
    seen = {(r.code, r.effective_date, r.value, r.unit) for r in existing}
    merged = list(existing)
    for r in extra:
        key = (r.code, r.effective_date, r.value, r.unit)
        if key not in seen:
            seen.add(key)
            merged.append(r)
    return merged


def find_loinc_coding(code_obj: Dict[str, Any]) -> Dict[str, Any]:
    """Return the LOINC coding from a CodeableConcept, searching every coding.

    Falls back to the first coding only when it carries no system at all
    (some servers omit it); a coding from another system is never treated
    as LOINC.
    """
    codings = code_obj.get("coding") or []
    for coding in codings:
        if coding.get("system") == LOINC_SYSTEM:
            return coding
    if codings and not codings[0].get("system"):
        return codings[0]
    return {}


def _is_excluded(resource: Dict[str, Any]) -> bool:
    """True for resources marked entered-in-error or cancelled."""
    if str(resource.get("status", "")).lower() in EXCLUDED_STATUSES:
        return True
    verification = resource.get("verificationStatus") or {}
    for coding in verification.get("coding", []) or []:
        if str(coding.get("code", "")).lower() in EXCLUDED_STATUSES:
            return True
    return False


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
    reference_unit: Optional[str] = None  # unit stated on the reference range, if any

    def __post_init__(self):
        """Check if value is outside reference range."""
        if self.reference_range:
            low = self.reference_range.get("low")
            high = self.reference_range.get("high")
            if low is not None and self.value < low:
                self.is_abnormal = True
            if high is not None and self.value > high:
                self.is_abnormal = True

    @property
    def is_preliminary(self) -> bool:
        return self.status == "preliminary"


@dataclass
class VitalSign:
    """Vital sign measurement from FHIR Observation."""
    code: str  # LOINC code
    display: str
    value: float
    unit: str
    effective_date: datetime
    status: str = "final"

    @property
    def is_preliminary(self) -> bool:
        return self.status == "preliminary"


@dataclass
class PatientData:
    """Aggregated patient data from FHIR resources."""
    patient_id: str
    name: str
    age: Optional[int]  # None when the chart has no usable birth date
    gender: str
    labs: List[LabResult]
    vitals: List[VitalSign]
    conditions: List[Dict[str, Any]]
    medications: List[Dict[str, Any]]
    allergies: List[Dict[str, Any]]
    # Per-resource status (RETRIEVED / FAILED / NOT_AVAILABLE) for labs,
    # vitals, conditions, medications and allergies. An empty list is only
    # "none found" when its status is RETRIEVED.
    retrieval_status: Dict[str, str] = field(default_factory=dict)
    # Notes about data that was skipped (blank values, excluded entries, ...)
    data_notes: List[str] = field(default_factory=list)
    # "Lab results cut off: ..." when the page limit stopped a query early
    truncation_warnings: List[str] = field(default_factory=list)

    @property
    def data_warnings(self) -> List[str]:
        return retrieval_warnings(self.retrieval_status) + list(self.truncation_warnings)

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
        self._truncations: List[Dict[str, Any]] = []

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

        # Confidential clients authenticate via HTTP Basic Auth using the Cerner Central System Account secret.
        auth = (self.client_id, self.client_secret) if self.client_secret else None

        response = requests.post(token_url, data=data, auth=auth); logger.error(f"Cerner token exchange {response.status_code}: {response.text}") if not response.ok else None
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
        if not response.ok:
            logger.error(f"FHIR Patient fetch {response.status_code}: {response.text}")
        response.raise_for_status()
        return response.json()

    def get_observations(
        self,
        patient_id: str,
        category: Optional[str] = None,
        code: Optional[str] = None,
        date_range: Optional[str] = None,
        max_pages: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Get patient observations (labs, vitals).

        Args:
            patient_id: Patient ID
            category: laboratory, vital-signs, etc.
            code: LOINC code filter (comma-separated for several)
            date_range: Date range (e.g., "gt2024-01-01")
            max_pages: follow the bundle's `next` links up to this many pages

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

        observations = [entry["resource"] for entry in bundle.get("entry", []) or []]
        pages = 1
        while pages < max_pages:
            next_url = next((link.get("url") for link in bundle.get("link", []) or []
                             if link.get("relation") == "next"), None)
            if not next_url:
                break
            response = requests.get(next_url, headers=self._get_headers())
            response.raise_for_status()
            bundle = response.json()
            observations.extend(entry["resource"] for entry in bundle.get("entry", []) or [])
            pages += 1
        if any(link.get("relation") == "next" for link in bundle.get("link", []) or []):
            dates = sorted(o["effectiveDateTime"][:10] for o in observations if o.get("effectiveDateTime"))
            self._truncations.append({
                "count": len(observations), "pages": pages,
                "first": dates[0] if dates else None, "last": dates[-1] if dates else None,
                "since": date_range[2:] if date_range and len(date_range) > 2 else None,
            })
            logger.warning(f"Observation query cut off at {pages} page(s), {len(observations)} results")
        return observations

    def get_criteria_observations(
        self, patient_id: str, codes: List[str], lookback_days: int, max_pages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Observations for specific LOINC codes over a longer lookback (chart-evaluation criteria)."""
        max_pages = max_pages or CRITERIA_MAX_PAGES
        since = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
        code_param = ",".join(f"{LOINC_SYSTEM}|{c}" for c in codes)
        return self.get_observations(patient_id, code=code_param, date_range=f"ge{since}", max_pages=max_pages)

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

    @staticmethod
    def _observation_name(observation: Dict[str, Any]) -> str:
        code_obj = observation.get("code", {}) or {}
        coding = find_loinc_coding(code_obj)
        first = (code_obj.get("coding") or [{}])[0]
        return coding.get("display") or first.get("display") or code_obj.get("text") or "Unknown"

    def parse_observation(
        self, observation: Dict[str, Any], notes: Optional[List[str]] = None
    ) -> Optional[LabResult]:
        """
        Parse FHIR Observation into LabResult.

        Args:
            observation: FHIR Observation resource
            notes: optional list that receives a note for every result skipped
                (entered-in-error/cancelled, or no numeric value)

        Returns:
            LabResult or None if the observation is excluded or unusable
        """
        notes = notes if notes is not None else []
        name = self._observation_name(observation)
        try:
            if _is_excluded(observation):
                notes.append(f"{name}: excluded (marked {observation.get('status')}).")
                return None

            # Get code: the LOINC coding, wherever it sits in the coding list
            code_obj = observation.get("code", {}) or {}
            coding = find_loinc_coding(code_obj)
            code = coding.get("code")
            display = name

            # Get value - a blank value is skipped, never read as 0
            value_qty = observation.get("valueQuantity", {})
            if not value_qty:
                return None  # No numeric value (coded/text result)
            raw_value = value_qty.get("value")
            if raw_value is None or (isinstance(raw_value, str) and not raw_value.strip()):
                notes.append(f"{name}: result has no value; skipped.")
                return None

            value = float(raw_value)
            unit = value_qty.get("unit") or value_qty.get("code") or ""

            # Get reference range
            reference_range = None
            reference_unit = None
            if observation.get("referenceRange"):
                ref = observation["referenceRange"][0]
                low = ref.get("low", {}) or {}
                high = ref.get("high", {}) or {}
                low_val = low.get("value")
                high_val = high.get("value")
                if low_val is not None or high_val is not None:
                    reference_range = {}
                    if low_val is not None:
                        reference_range["low"] = float(low_val)
                    if high_val is not None:
                        reference_range["high"] = float(high_val)
                    reference_unit = high.get("unit") or low.get("unit") or None

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
                effective_date=effective_date,
                reference_unit=reference_unit,
            )
        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"Failed to parse observation: {e}")
            notes.append(f"{name}: result could not be read ({e}); skipped.")
            return None

    def parse_vitals(
        self, observation: Dict[str, Any], notes: Optional[List[str]] = None
    ) -> List[VitalSign]:
        """Parse a vital-signs Observation into one or more readings.

        Blood pressure is commonly sent as one panel (LOINC 85354-9) whose
        systolic (8480-6) and diastolic (8462-4) values are components rather
        than a top-level valueQuantity; each component becomes a reading.
        """
        notes = notes if notes is not None else []
        components = observation.get("component") or []
        if not components or observation.get("valueQuantity"):
            vital = self.parse_vital(observation, notes)
            return [vital] if vital else []
        if _is_excluded(observation):
            notes.append(f"{self._observation_name(observation)}: excluded (marked {observation.get('status')}).")
            return []
        readings = []
        for component in components:
            part = dict(component)
            part.setdefault("status", observation.get("status", "final"))
            for key in ("effectiveDateTime", "id"):
                if key in observation:
                    part[key] = observation[key]
            vital = self.parse_vital(part, notes)
            if vital:
                readings.append(vital)
        return readings

    def parse_vital(
        self, observation: Dict[str, Any], notes: Optional[List[str]] = None
    ) -> Optional[VitalSign]:
        """Parse a vital-signs Observation; same exclusion/blank rules as labs."""
        notes = notes if notes is not None else []
        name = self._observation_name(observation)
        try:
            if _is_excluded(observation):
                notes.append(f"{name}: excluded (marked {observation.get('status')}).")
                return None
            code = find_loinc_coding(observation.get("code", {}) or {}).get("code")
            value_qty = observation.get("valueQuantity", {}) or {}
            raw_value = value_qty.get("value")
            if raw_value is None or (isinstance(raw_value, str) and not raw_value.strip()):
                if value_qty:
                    notes.append(f"{name}: reading has no value; skipped.")
                return None
            return VitalSign(
                code=code,
                display=name,
                value=float(raw_value),
                unit=value_qty.get("unit") or value_qty.get("code") or "",
                effective_date=datetime.fromisoformat(
                    observation["effectiveDateTime"].replace("Z", "+00:00")
                ),
                status=observation.get("status", "final"),
            )
        except (KeyError, ValueError, TypeError) as e:
            notes.append(f"{name}: reading could not be read ({e}); skipped.")
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
            new_medications, plus retrieval_status (per resource), data_warnings
            and data_notes. A resource whose query failed has an empty list
            and a non-"retrieved" status - never read that as "nothing new".
        """
        since_str = since.strftime("%Y-%m-%d")
        status: Dict[str, str] = {}
        notes: List[str] = []
        truncated: List[str] = []

        lab_observations = self._fetch_tracked(
            "labs", status,
            lambda: self.get_observations(patient_id, category="laboratory", date_range=f"ge{since_str}"),
            truncated,
        )
        new_labs = [lab for lab in (self.parse_observation(o, notes) for o in lab_observations) if lab]
        new_abnormal_labs = [lab for lab in new_labs if lab.is_abnormal]

        vital_observations = self._fetch_tracked(
            "vitals", status,
            lambda: self.get_observations(patient_id, category="vital-signs", date_range=f"ge{since_str}"),
            truncated,
        )
        new_vitals = [v for o in vital_observations for v in self.parse_vitals(o, notes)]

        new_conditions = self._fetch_tracked(
            "conditions", status,
            lambda: self._bundle_resources(self._query_resource("Condition", {
                "patient": patient_id, "_count": 100, "recorded-date": f"ge{since_str}"
            })),
        )
        new_conditions = self._drop_excluded(new_conditions, "condition", notes)

        new_medications = self._fetch_tracked(
            "medications", status,
            lambda: self._bundle_resources(self._query_resource("MedicationRequest", {
                "patient": patient_id, "_count": 100, "authoredon": f"ge{since_str}"
            })),
        )
        new_medications = self._drop_excluded(new_medications, "medication", notes)

        return {
            "new_labs": new_labs,
            "new_abnormal_labs": new_abnormal_labs,
            "new_vitals": new_vitals,
            "new_conditions": new_conditions,
            "new_medications": new_medications,
            "retrieval_status": status,
            "data_warnings": retrieval_warnings(status) + truncated,
            "data_notes": notes,
        }

    @staticmethod
    def _bundle_resources(bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [entry["resource"] for entry in bundle.get("entry", []) or []]

    @staticmethod
    def _drop_excluded(resources: List[Dict[str, Any]], kind: str, notes: List[str]) -> List[Dict[str, Any]]:
        """Remove resources marked entered-in-error or cancelled, noting each."""
        kept = []
        for resource in resources:
            if _is_excluded(resource):
                code_obj = resource.get("code") or resource.get("medicationCodeableConcept") or {}
                name = code_obj.get("text") or (code_obj.get("coding") or [{}])[0].get("display") or f"A {kind}"
                notes.append(f"{name}: excluded (marked entered-in-error or cancelled).")
                continue
            kept.append(resource)
        return kept

    def _fetch_tracked(self, resource: str, status: Dict[str, str], fetch,
                       truncation_warnings: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Run one FHIR fetch and record whether it succeeded.

        403/404/501 mean the resource type isn't enabled or supported for this
        app/EHR ("not available"); any other error is "failed". Either way the
        caller gets [] and must report the gap rather than "none found".
        """
        truncations = getattr(self, "_truncations", None)
        if truncations is None:
            truncations = self._truncations = []
        before = len(truncations)
        try:
            result = fetch()
            _record_status(status, resource, RETRIEVED)
            if truncation_warnings is not None:
                for event in truncations[before:]:
                    message = truncation_warning(resource, event)
                    if message not in truncation_warnings:
                        truncation_warnings.append(message)
            return result
        except requests.RequestException as e:
            code = getattr(getattr(e, "response", None), "status_code", None)
            outcome = NOT_AVAILABLE if code in (403, 404, 501) else FAILED
            _record_status(status, resource, outcome)
            logger.warning(f"FHIR query for {resource} {outcome}: {e}")
            return []

    @staticmethod
    def _age_from_birth_date(birth_date: Optional[str]) -> Optional[int]:
        """Whole years since birth, or None when the birth date is missing or unreadable."""
        if not birth_date:
            return None
        for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
            try:
                born = datetime.strptime(birth_date, fmt)
                break
            except ValueError:
                continue
        else:
            return None
        today = datetime.now()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    def get_patient_data(
        self, patient_id: str, observation_requirements: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> PatientData:
        """
        Get comprehensive patient data for clinical decision support.

        Each resource type is fetched independently and its outcome recorded
        in PatientData.retrieval_status, so a single unavailable resource
        (e.g. a 403 because that API isn't enabled in the app's EHR
        registration) doesn't take down the summary - but is never silently
        reported as "none on file" either.

        Args:
            patient_id: Patient FHIR ID
            observation_requirements: optional {"labs"/"vitals": {"codes": [...],
                "lookback_days": n}} from SmartDiagnosticEngine.observation_requirements();
                those codes are fetched over that lookback in addition to the
                chart-summary windows.

        Returns:
            PatientData object with aggregated clinical information
        """
        logger.info(f"Fetching patient data for {patient_id}")

        # Get patient demographics
        patient = self.get_patient(patient_id)
        name_obj = (patient.get("name") or [{}])[0]
        given = " ".join(name_obj.get("given", []))
        family = name_obj.get("family", "")
        full_name = f"{given} {family}".strip()

        notes: List[str] = []
        age = self._age_from_birth_date(patient.get("birthDate"))
        if age is None:
            notes.append("Birth date missing or unreadable; age is unknown.")

        gender = patient.get("gender", "unknown")
        status: Dict[str, str] = {}
        truncated: List[str] = []

        # Get labs (last LAB_LOOKBACK_DAYS days)
        lab_since = (datetime.now() - timedelta(days=LAB_LOOKBACK_DAYS)).strftime("%Y-%m-%d")
        lab_observations = self._fetch_tracked(
            "labs", status,
            lambda: self.get_observations(patient_id, category="laboratory", date_range=f"gt{lab_since}"),
            truncated,
        )
        labs = [lab for lab in (self.parse_observation(o, notes) for o in lab_observations) if lab]

        # Get vitals (last VITAL_LOOKBACK_DAYS days)
        vital_since = (datetime.now() - timedelta(days=VITAL_LOOKBACK_DAYS)).strftime("%Y-%m-%d")
        vital_observations = self._fetch_tracked(
            "vitals", status,
            lambda: self.get_observations(patient_id, category="vital-signs", date_range=f"gt{vital_since}"),
            truncated,
        )
        vitals = [v for o in vital_observations for v in self.parse_vitals(o, notes)]

        # Chart-evaluation criteria may need specific results over a longer
        # lookback than the chart summary (e.g. HbA1c over a year).
        for resource, need in (observation_requirements or {}).items():
            if not need.get("codes") or resource not in ("labs", "vitals"):
                continue
            extra = self._fetch_tracked(
                resource, status,
                lambda need=need: self.get_criteria_observations(patient_id, need["codes"], need["lookback_days"]),
                truncated,
            )
            if resource == "labs":
                labs = _merge_results(labs, [r for r in (self.parse_observation(o, notes) for o in extra) if r])
            else:
                vitals = _merge_results(vitals, [v for o in extra for v in self.parse_vitals(o, notes)])

        conditions = self._drop_excluded(
            self._fetch_tracked("conditions", status, lambda: self.get_conditions(patient_id)),
            "condition", notes,
        )
        medications = self._drop_excluded(
            self._fetch_tracked("medications", status, lambda: self.get_medications(patient_id)),
            "medication", notes,
        )
        allergies = self._drop_excluded(
            self._fetch_tracked("allergies", status, lambda: self.get_allergies(patient_id)),
            "allergy", notes,
        )

        patient_data = PatientData(
            patient_id=patient_id,
            name=full_name,
            age=age,
            gender=gender,
            labs=labs,
            vitals=vitals,
            conditions=conditions,
            medications=medications,
            allergies=allergies,
            retrieval_status=status,
            data_notes=notes,
            truncation_warnings=truncated,
        )

        logger.info(
            f"Retrieved data for {full_name}: "
            f"{len(labs)} labs, {len(vitals)} vitals, "
            f"{len(conditions)} conditions, {len(medications)} medications; "
            f"status {status}"
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
