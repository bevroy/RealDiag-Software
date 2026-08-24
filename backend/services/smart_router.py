"""
SMART on FHIR Router

Implements SMART on FHIR launch sequence and clinical decision support endpoints
for Epic and other EHR integration.

Endpoints:
    GET  /smart/launch           - SMART launch entry point
    GET  /smart/callback         - OAuth callback handler
    POST /smart/evaluate-patient - Evaluate patient with CDS
    GET  /smart/patient/{id}     - Get patient summary

SECURITY NOTE (fixed 2026-08-24): the OAuth callback used to hand the raw
FHIR access token to the browser (embedded in an inline <script> tag and
written to sessionStorage), and evaluate-patient / patient summary took
that same token back as a plain request parameter. A real EHR access token
was sitting in browser storage and traveling on every request. It's now
stored server-side only (see smart_session_store.py); the browser gets
nothing but an opaque, HttpOnly session cookie.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Request, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging
import secrets
import jwt
from datetime import datetime, timedelta
from urllib.parse import urlparse

from ..services.fhir_client import FHIRClient, PatientData, CommonLOINC
from ..services.smart_diagnostic_engine import SmartDiagnosticEngine, DiagnosisEvaluation
from ..services.ehr_adapter import EHRAdapter, EHRVendor
from ..services.smart_session_store import (
    create_smart_session,
    get_smart_session,
    delete_smart_session,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/smart", tags=["SMART on FHIR"])

# Configuration (should be environment variables in production)
# Supports multiple EHR vendors: Epic, Cerner, Allscripts, athenahealth
EHR_VENDOR = os.getenv("EHR_VENDOR", "epic").lower()  # epic, cerner, allscripts, athenahealth
FHIR_BASE_URL = os.getenv("FHIR_BASE_URL", "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4")
CLIENT_ID = os.getenv("SMART_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("SMART_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("SMART_REDIRECT_URI", "http://localhost:8000/smart/callback")
TENANT_ID = os.getenv("EHR_TENANT_ID")  # Required for Cerner

# Where to send the clinician's browser after a successful EHR launch.
# Reuses the same FRONTEND_URL convention as email_service.py.
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://app.realdiag.com")

# SMART session cookie: opaque pointer to the server-side session record in
# smart_session_store.py. Never contains the actual FHIR access token.
SMART_SESSION_COOKIE_NAME = "realdiag_smart_session"
# Upper bound on session lifetime, independent of how long-lived the EHR's
# own access token is - keeps a long-lived EHR token from becoming a
# long-lived RealDiag cookie.
SMART_SESSION_MAX_TTL_SECONDS = int(os.getenv("SMART_SESSION_TTL_MINUTES", "30")) * 60

# State token secret used to sign the SMART launch state (OAuth CSRF protection).
# Falls back to JWT_SECRET_KEY so a single required secret covers both flows.
SMART_STATE_SECRET = os.getenv("SMART_STATE_SECRET") or os.getenv("JWT_SECRET_KEY")
STATE_TOKEN_EXPIRE_MINUTES = 10

# Issuer allowlist: only launch redirects to known/trusted FHIR servers.
# Defaults to the host of the configured FHIR_BASE_URL; extra hosts (e.g. for
# multi-tenant deployments) can be added via SMART_ALLOWED_ISS_HOSTS.
_extra_allowed_hosts = {
    host.strip().lower()
    for host in os.getenv("SMART_ALLOWED_ISS_HOSTS", "").split(",")
    if host.strip()
}
ALLOWED_ISS_HOSTS = _extra_allowed_hosts | {urlparse(FHIR_BASE_URL).netloc.lower()}

# Global instances (in production, use dependency injection)
diagnostic_engine = SmartDiagnosticEngine()


def _validate_iss(iss: str) -> str:
    """Reject issuer URLs that aren't in the trusted allowlist."""
    parsed = urlparse(iss)
    if parsed.scheme != "https" or not parsed.netloc:
        raise HTTPException(status_code=400, detail="Invalid iss: must be an https URL")
    if parsed.netloc.lower() not in ALLOWED_ISS_HOSTS:
        logger.warning(f"Rejected SMART launch from disallowed iss host: {parsed.netloc}")
        raise HTTPException(status_code=400, detail="Unrecognized FHIR issuer")
    return iss


def _create_state_token(iss: str) -> str:
    """Create a signed, short-lived state token to prevent OAuth CSRF."""
    payload = {
        "iss": iss,
        "nonce": secrets.token_urlsafe(16),
        "exp": datetime.utcnow() + timedelta(minutes=STATE_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SMART_STATE_SECRET, algorithm="HS256")


def _verify_state_token(state: str) -> Dict[str, Any]:
    """Verify the state token returned by the EHR authorization server."""
    try:
        return jwt.decode(state, SMART_STATE_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError as e:
        logger.warning(f"SMART callback rejected: invalid state token ({e})")
        raise HTTPException(status_code=400, detail="Invalid or expired state parameter")


def get_active_smart_session(
    realdiag_smart_session: Optional[str] = Cookie(default=None, alias=SMART_SESSION_COOKIE_NAME)
):
    """
    Resolve the caller's SMART session from their session cookie.

    Replaces the old pattern where the frontend held the raw FHIR access
    token and passed it back on every request. The token now lives only in
    the smart_sessions table; the browser just proves which row is theirs
    via this opaque cookie.
    """
    session = get_smart_session(realdiag_smart_session) if realdiag_smart_session else None

    if not session:
        raise HTTPException(status_code=401, detail="No active SMART session. Please relaunch from the EHR.")

    if session.expires_at < datetime.utcnow():
        delete_smart_session(realdiag_smart_session)
        raise HTTPException(status_code=401, detail="SMART session expired. Please relaunch from the EHR.")

    return session


class EvaluatePatientRequest(BaseModel):
    """Request to evaluate patient with clinical decision support."""
    patient_id: str
    chief_complaint: Optional[str] = None
    focus_specialties: Optional[List[str]] = None
    # NOTE: no longer takes access_token - the FHIR access token is
    # resolved server-side from the caller's SMART session cookie
    # (see get_active_smart_session) instead of being passed by the client.


class CriterionResponse(BaseModel):
    """Criterion evaluation result."""
    criterion: str
    status: str  # present, absent, unknown
    value: Optional[str] = None
    expected: Optional[str] = None
    details: Optional[str] = None


class DiagnosisResponse(BaseModel):
    """Diagnosis evaluation result."""
    diagnosis_id: str
    diagnosis_label: str
    family: str
    probability: float
    severity: str
    criteria_met: List[CriterionResponse]
    criteria_not_met: List[CriterionResponse]
    criteria_unknown: List[CriterionResponse]
    recommendations: List[str]
    missing_tests: List[str]


class PatientSummaryResponse(BaseModel):
    """Patient clinical summary."""
    patient_id: str
    name: str
    age: int
    gender: str
    lab_count: int
    vital_count: int
    condition_count: int
    medication_count: int
    abnormal_labs: List[Dict[str, Any]]
    recent_vitals: List[Dict[str, Any]]


def get_ehr_config():
    """Get EHR configuration for current vendor."""
    try:
        return EHRAdapter.get_config(
            vendor=EHR_VENDOR,
            fhir_base_url=FHIR_BASE_URL,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            tenant_id=TENANT_ID
        )
    except ValueError as e:
        logger.error(f"EHR configuration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/launch")
async def smart_launch(
    iss: str = Query(..., description="FHIR server URL"),
    launch: str = Query(..., description="Launch context token")
):
    """
    SMART on FHIR launch endpoint.

    This is the entry point when launching from Epic, Cerner, or another EHR.
    Redirects to EHR authorization page.
    """
    # Reject issuer URLs that aren't in the trusted allowlist before using them.
    iss = _validate_iss(iss)

    logger.info(f"SMART launch initiated from {iss} using {EHR_VENDOR}")

    # Get vendor-specific configuration
    ehr_config = get_ehr_config()

    # Use vendor-specific authorization URL
    auth_url = ehr_config.authorize_url

    # Build authorization URL with vendor-specific scopes
    scopes = ehr_config.scopes

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(scopes),
        "state": _create_state_token(iss),  # Signed, single-use nonce (CSRF protection)
        "aud": iss,
        "launch": launch
    }

    # Build query string
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    full_auth_url = f"{auth_url}?{query_string}"

    return RedirectResponse(url=full_auth_url)


@router.get("/callback")
async def smart_callback(
    code: str = Query(..., description="Authorization code"),
    state: str = Query(..., description="State parameter"),
):
    """
    OAuth callback handler.

    Exchanges the authorization code for an access token, stores it
    server-side in a SMART session, and redirects the clinician's browser
    to the app with nothing but an opaque session cookie - no token is
    ever placed in the URL, the page, or browser storage.
    """
    # Verify the state token to prevent OAuth CSRF (rejects forged/replayed/expired state)
    state_payload = _verify_state_token(state)
    iss = state_payload.get("iss")
    logger.info(f"OAuth callback received with code: {code[:10]}... for iss={iss}")

    try:
        # Initialize FHIR client
        fhir_client = FHIRClient(
            fhir_base_url=FHIR_BASE_URL,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )

        # Exchange code for token
        token_data = fhir_client.authenticate(
            authorization_code=code,
            redirect_uri=REDIRECT_URI
        )

        access_token = token_data["access_token"]
        refresh_token = token_data.get("refresh_token")
        patient_id = token_data.get("patient")  # Patient ID from launch context

        # Bound the session lifetime to whichever is shorter: the EHR
        # token's own expiry, or our TTL cap.
        token_ttl_seconds = int(token_data.get("expires_in", SMART_SESSION_MAX_TTL_SECONDS))
        ttl_seconds = max(60, min(token_ttl_seconds, SMART_SESSION_MAX_TTL_SECONDS))
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)

        session_id = create_smart_session(
            ehr_vendor=EHR_VENDOR,
            iss=iss,
            patient_id=patient_id,
            fhir_access_token=access_token,
            fhir_refresh_token=refresh_token,
            expires_at=expires_at,
        )

        if not session_id:
            # No database configured - there's nowhere safe to hold the
            # token server-side, so refuse rather than falling back to
            # exposing it to the browser.
            logger.error("SMART callback rejected: no database configured, cannot store session server-side")
            raise HTTPException(status_code=503, detail="SMART on FHIR sign-in is temporarily unavailable")

        logger.info(f"SMART session created for patient {patient_id or 'unknown'}, expires in {ttl_seconds}s")

        redirect_url = f"{FRONTEND_URL.rstrip('/')}/symptom?smart=true"
        if patient_id:
            redirect_url += f"&patient_id={patient_id}"

        redirect_response = RedirectResponse(url=redirect_url, status_code=302)
        redirect_response.set_cookie(
            key=SMART_SESSION_COOKIE_NAME,
            value=session_id,
            max_age=ttl_seconds,
            httponly=True,
            secure=True,
            samesite="lax",
            path="/",
        )
        return redirect_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        raise HTTPException(status_code=500, detail="Authentication with the EHR failed")


@router.post("/evaluate-patient", response_model=List[DiagnosisResponse])
async def evaluate_patient(
    request: EvaluatePatientRequest,
    smart_session = Depends(get_active_smart_session),
):
    """
    Evaluate patient data against diagnostic rules.

    Performs real-time clinical decision support by fetching patient data
    from the FHIR server (using the token from the caller's SMART session)
    and evaluating it against diagnostic criteria.
    """
    logger.info(f"Evaluating patient {request.patient_id}")

    try:
        # Initialize FHIR client with the access token from the caller's
        # server-side SMART session (never passed in by the client).
        fhir_client = FHIRClient(
            fhir_base_url=FHIR_BASE_URL,
            client_id=CLIENT_ID,
            access_token=smart_session.fhir_access_token
        )

        # Fetch patient data
        patient_data = fhir_client.get_patient_data(request.patient_id)

        # Evaluate with diagnostic engine
        evaluations = diagnostic_engine.evaluate_patient(
            patient_data=patient_data,
            chief_complaint=request.chief_complaint,
            focus_specialties=request.focus_specialties
        )

        # Convert to response format
        responses = []
        for eval in evaluations:
            responses.append(DiagnosisResponse(
                diagnosis_id=eval.diagnosis_id,
                diagnosis_label=eval.diagnosis_label,
                family=eval.family,
                probability=eval.probability,
                severity=eval.severity,
                criteria_met=[
                    CriterionResponse(
                        criterion=c.criterion,
                        status=c.status.value,
                        value=c.value,
                        expected=c.expected,
                        details=c.details
                    ) for c in eval.criteria_met
                ],
                criteria_not_met=[
                    CriterionResponse(
                        criterion=c.criterion,
                        status=c.status.value,
                        value=c.value,
                        expected=c.expected,
                        details=c.details
                    ) for c in eval.criteria_not_met
                ],
                criteria_unknown=[
                    CriterionResponse(
                        criterion=c.criterion,
                        status=c.status.value,
                        value=c.value,
                        expected=c.expected,
                        details=c.details
                    ) for c in eval.criteria_unknown
                ],
                recommendations=eval.recommendations,
                missing_tests=eval.missing_tests
            ))

        logger.info(f"Returned {len(responses)} evaluations for patient {request.patient_id}")
        return responses

    except Exception as e:
        logger.error(f"Patient evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.get("/patient/{patient_id}", response_model=PatientSummaryResponse)
async def get_patient_summary(
    patient_id: str,
    smart_session = Depends(get_active_smart_session),
):
    """
    Get patient clinical summary.

    Returns high-level overview of patient's clinical data including
    abnormal labs and recent vitals. Uses the access token from the
    caller's server-side SMART session.
    """
    try:
        fhir_client = FHIRClient(
            fhir_base_url=FHIR_BASE_URL,
            client_id=CLIENT_ID,
            access_token=smart_session.fhir_access_token
        )

        patient_data = fhir_client.get_patient_data(patient_id)

        # Find abnormal labs
        abnormal_labs = []
        for lab in patient_data.labs:
            if lab.is_abnormal:
                abnormal_labs.append({
                    "name": lab.display,
                    "value": lab.value,
                    "unit": lab.unit,
                    "reference_range": lab.reference_range,
                    "date": lab.effective_date.isoformat() if lab.effective_date else None
                })

        # Get recent vitals (last 3 of each type)
        vital_summary = []
        vital_types_seen = set()
        for vital in sorted(patient_data.vitals, key=lambda v: v.effective_date, reverse=True):
            if vital.code not in vital_types_seen or len([v for v in vital_summary if v["code"] == vital.code]) < 3:
                vital_summary.append({
                    "code": vital.code,
                    "name": vital.display,
                    "value": vital.value,
                    "unit": vital.unit,
                    "date": vital.effective_date.isoformat()
                })
            vital_types_seen.add(vital.code)

        return PatientSummaryResponse(
            patient_id=patient_data.patient_id,
            name=patient_data.name,
            age=patient_data.age,
            gender=patient_data.gender,
            lab_count=len(patient_data.labs),
            vital_count=len(patient_data.vitals),
            condition_count=len(patient_data.conditions),
            medication_count=len(patient_data.medications),
            abnormal_labs=abnormal_labs[:10],
            recent_vitals=vital_summary[:10]
        )

    except Exception as e:
        logger.error(f"Failed to get patient summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve patient data: {str(e)}")


@router.get("/config")
async def get_smart_config():
    """
    Get SMART on FHIR configuration.

    Returns configuration needed for frontend SMART launch.
    """
    return {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scopes": [
            "launch",
            "patient/*.read",
            "openid",
            "fhirUser"
        ],
        "fhir_base_url": FHIR_BASE_URL
    }
