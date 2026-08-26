"""
SMART on FHIR Router

Implements SMART on FHIR launch sequence and clinical decision support endpoints
for Epic and other EHR integration.

Endpoints:
    GET  /smart/launch                 - SMART launch entry point
    GET  /smart/callback               - OAuth callback handler
    POST /smart/evaluate-patient       - Evaluate patient with CDS
    GET  /smart/patient/{id}           - Get patient chart summary
    GET  /smart/patient/{id}/handoff   - Chart summary + updates since admission/shift start
    GET  /smart/patient/{id}/differential - Full-chart pull -> ranked differential (ambulatory/ER)
    GET  /smart/config                 - Frontend SMART launch config

SECURITY NOTE (fixed 2026-08-24): the OAuth callback used to hand the raw
FHIR access token to the browser (embedded in an inline <script> tag and
written to sessionStorage), and evaluate-patient / patient summary took
that same token back as a plain request parameter. It's now stored
server-side only (see smart_session_store.py); the browser gets nothing
but an opaque, HttpOnly session cookie.
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

from ..services.fhir_client import FHIRClient, PatientData, CommonLOINC
from ..services.smart_diagnostic_engine import SmartDiagnosticEngine, DiagnosisEvaluation
from ..services.patient_history_service import PatientHistoryService
from ..services.symptom_search import (
    rank_diagnoses,
    derive_search_terms_from_history,
    _append_unique_terms,
    SymptomSearchResponse,
    AuditLogger,
)
from urllib.parse import urlparse, urlencode
from ..services.ehr_adapter import EHRAdapter
from ..services.smart_session_store import (create_smart_session,
    get_smart_session,
    delete_smart_session,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/smart", tags=["SMART on FHIR"])

# Configuration (should be environment variables in production)
EHR_VENDOR = os.getenv("EHR_VENDOR", "epic").lower()
FHIR_BASE_URL = os.getenv("FHIR_BASE_URL", "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4")
CLIENT_ID = os.getenv("SMART_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("SMART_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("SMART_REDIRECT_URI", "http://localhost:8000/smart/callback")
TENANT_ID = os.getenv("EHR_TENANT_ID")

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://app.realdiag.com")

SMART_SESSION_COOKIE_NAME = "realdiag_smart_session"
SMART_SESSION_MAX_TTL_SECONDS = int(os.getenv("SMART_SESSION_TTL_MINUTES", "30")) * 60

SMART_STATE_SECRET = os.getenv("SMART_STATE_SECRET") or os.getenv("JWT_SECRET_KEY")
STATE_TOKEN_EXPIRE_MINUTES = 10

_extra_allowed_hosts = {
    host.strip().lower()
    for host in os.getenv("SMART_ALLOWED_ISS_HOSTS", "").split(",")
    if host.strip()
}
ALLOWED_ISS_HOSTS = _extra_allowed_hosts | {urlparse(FHIR_BASE_URL).netloc.lower()}

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
    """
    session = get_smart_session(realdiag_smart_session) if realdiag_smart_session else None

    if not session:
        raise HTTPException(status_code=401, detail="No active SMART session. Please relaunch from the EHR.")

    if session.expires_at < datetime.utcnow():
        delete_smart_session(realdiag_smart_session)
        raise HTTPException(status_code=401, detail="SMART session expired. Please relaunch from the EHR.")

    return session


def _verify_patient_match(smart_session, requested_patient_id: str) -> None:
    """
    Defense-in-depth check: confirm the patient_id being requested matches
    the patient the EHR actually launched this session for.

    In a normal EHR-launch flow, the FHIR access token itself is scoped
    server-side (by Epic/Cerner) to the one patient in the launch context,
    so a mismatched patient_id would typically be rejected by the FHIR
    server regardless. This check doesn't rely on that vendor-side
    enforcement - it stops a mismatched request at RealDiag's own boundary
    before it's ever sent to the FHIR server.
    """
    if smart_session.patient_id and smart_session.patient_id != requested_patient_id:
        logger.warning(
            f"Session/patient mismatch: session launched for patient "
            f"{smart_session.patient_id}, request was for {requested_patient_id}"
        )
        raise HTTPException(
            status_code=403,
            detail="This session is not authorized for the requested patient. Please relaunch from the EHR."
        )


class EvaluatePatientRequest(BaseModel):
    """Request to evaluate patient with clinical decision support."""
    patient_id: str
    chief_complaint: Optional[str] = None
    focus_specialties: Optional[List[str]] = None


class CriterionResponse(BaseModel):
    """Criterion evaluation result."""
    criterion: str
    status: str
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


class HandoffUpdateItem(BaseModel):
    """A single new/changed item since the handoff timeframe started."""
    name: str
    detail: Optional[str] = None
    date: Optional[str] = None


class HandoffUpdatesResponse(BaseModel):
    """Structured delta: what's new since the timeframe boundary."""
    new_lab_count: int
    new_abnormal_labs: List[Dict[str, Any]]
    new_vital_count: int
    new_conditions: List[HandoffUpdateItem]
    new_medications: List[HandoffUpdateItem]


class HandoffSummaryResponse(BaseModel):
    """
    Shift-handoff / admission-to-date summary: the full chart summary
    plus what's changed since a timeframe boundary (admission start by
    default, or a manually specified shift-change time).
    """
    patient_id: str
    admission_start: Optional[str]
    timeframe_start: Optional[str]
    timeframe_source: str  # "admission" | "manual" | "none"
    full_summary: PatientSummaryResponse
    updates: Optional[HandoffUpdatesResponse]
    narrative: str


class SmartSessionStatusResponse(BaseModel):
    """Non-throwing SMART session check, used by the main app's nav
    (RoleBasedNavigation) to decide whether to show an Inpatient link.
    Unlike get_active_smart_session, this never 401s - it just reports
    whether a session exists, since the main nav renders for users who may
    not have one."""
    active: bool
    patient_id: Optional[str] = None
    ehr_vendor: Optional[str] = None


class AmbulatoryDifferentialResponse(BaseModel):
    """
    Full-chart pull -> concise summary -> ranked differential, for the
    ambulatory/ER use case: a patient with no active admission, where the
    goal is pulling as much of the available chart as exists (however
    old) rather than a bounded inpatient window, and feeding it into the
    core ranked-differential engine.
    """
    patient_id: str
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    chart_summary: str
    data_pulled: Dict[str, int]
    search_terms_used: List[str]
    differential: SymptomSearchResponse


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


def _build_patient_summary(fhir_client: FHIRClient, patient_id: str) -> PatientSummaryResponse:
    """
    Shared chart-summary logic, used by both GET /patient/{id} and
    GET /patient/{id}/handoff so they can never drift out of sync.
    """
    patient_data = fhir_client.get_patient_data(patient_id)

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


def _generate_handoff_narrative(
    full_summary: PatientSummaryResponse,
    updates: Optional[Dict[str, Any]],
    timeframe_start: Optional[datetime],
    timeframe_source: str
) -> str:
    """
    Build a plain-language handoff narrative from structured data.

    Deliberately template-based rather than AI-generated: every sentence
    here traces directly back to a specific FHIR value, so there's nothing
    for a clinician to fact-check against the underlying chart - it's a
    formatted restatement of the structured data, not a synthesized one.
    """
    if timeframe_start is None or updates is None:
        return (
            f"No active admission found for {full_summary.name}. Showing the "
            f"standard chart summary only; time-bounded updates require an "
            f"active encounter or a manually specified start time."
        )

    when = timeframe_start.strftime("%b %d, %Y at %H:%M")
    basis = "since admission" if timeframe_source == "admission" else "since the specified handoff time"

    parts = [f"{full_summary.name} ({full_summary.age}yo {full_summary.gender}) - updates {basis} ({when}):"]

    abnormal = updates["new_abnormal_labs"]
    new_lab_count = len(updates["new_labs"])
    if new_lab_count:
        if abnormal:
            names = ", ".join(f"{lab.display} {lab.value}{lab.unit}" for lab in abnormal[:5])
            more = f" and {len(abnormal) - 5} more" if len(abnormal) > 5 else ""
            parts.append(f"{new_lab_count} new lab result(s), including {len(abnormal)} abnormal: {names}{more}.")
        else:
            parts.append(f"{new_lab_count} new lab result(s), all within normal range.")
    else:
        parts.append("No new labs.")

    new_vital_count = len(updates["new_vitals"])
    parts.append(f"{new_vital_count} new vital sign reading(s) recorded." if new_vital_count else "No new vitals recorded.")

    new_conditions = updates["new_conditions"]
    if new_conditions:
        names = ", ".join(
            c.get("code", {}).get("text") or c.get("code", {}).get("coding", [{}])[0].get("display", "Unspecified condition")
            for c in new_conditions[:5]
        )
        parts.append(f"{len(new_conditions)} new condition(s) added to the problem list: {names}.")
    else:
        parts.append("No new conditions added.")

    new_meds = updates["new_medications"]
    if new_meds:
        names = ", ".join(
            m.get("medicationCodeableConcept", {}).get("text")
            or m.get("medicationCodeableConcept", {}).get("coding", [{}])[0].get("display", "Unspecified medication")
            for m in new_meds[:5]
        )
        parts.append(f"{len(new_meds)} new medication(s) ordered: {names}.")
    else:
        parts.append("No new medications ordered.")

    return " ".join(parts)


@router.get("/launch")
async def smart_launch(
    iss: str = Query(..., description="FHIR server URL"),
    launch: str = Query(..., description="Launch context token")
):
    """
    SMART on FHIR launch endpoint. Entry point when launching from Epic,
    Cerner, or another EHR. Redirects to the EHR authorization page.
    """
    iss = _validate_iss(iss)

    logger.info(f"SMART launch initiated from {iss} using {EHR_VENDOR}")

    ehr_config = get_ehr_config()
    auth_url = ehr_config.authorize_url
    scopes = ehr_config.scopes

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(scopes),
        "state": _create_state_token(iss),
        "aud": iss,
        "launch": launch
    }

    query_string = urlencode(params)
    full_auth_url = f"{auth_url}?{query_string}"
    return RedirectResponse(url=full_auth_url)
@router.get("/callback")
async def smart_callback(
        code: str = Query(..., description="Authorization code"),
        state: str = Query(..., description="State parameter"),
):
    """
    OAuth callback handler. Exchanges the code for an access token, stores
    it server-side in a SMART session, and redirects to /smart-launch with
    nothing but an opaque session cookie - no token in the URL, page, or
    browser storage.
    """
    state_payload = _verify_state_token(state)
    iss = state_payload.get("iss")
    logger.info(f"OAuth callback received with code: {code[:10]}... for iss={iss}")

    try:
        ehr_config = get_ehr_config()

        fhir_client = FHIRClient(
            fhir_base_url=FHIR_BASE_URL,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            token_url=ehr_config.token_url
        )

        token_data = fhir_client.authenticate(
            authorization_code=code,
            redirect_uri=REDIRECT_URI
        )

        access_token = token_data["access_token"]
        refresh_token = token_data.get("refresh_token")
        patient_id = token_data.get("patient")
        logger.info(f"Cerner token response scope granted: {token_data.get('scope')}")

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
            logger.error("SMART callback rejected: no database configured, cannot store session server-side")
            raise HTTPException(status_code=503, detail="SMART on FHIR sign-in is temporarily unavailable")

        logger.info(f"SMART session created for patient {patient_id or 'unknown'}, expires in {ttl_seconds}s")

        # /inpatient is the consolidated chart-summary + handoff view (tabs).
        # It reads patient_id from the URL and authenticates via the SMART
        # session cookie set below - same auth model as the standalone
        # smart-launch/handoff pages it now replaces as the landing spot.
        redirect_url = f"{FRONTEND_URL.rstrip('/')}/inpatient"
        if patient_id:
            redirect_url += f"?patient_id={patient_id}"

        redirect_response = RedirectResponse(url=redirect_url, status_code=302)
        redirect_response.set_cookie(
            key=SMART_SESSION_COOKIE_NAME,
            value=session_id,
            max_age=ttl_seconds,
            httponly=True,
            secure=True,
            samesite="none",
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
    Evaluate patient data against diagnostic rules using the token from
    the caller's server-side SMART session.
    """
    logger.info(f"Evaluating patient {request.patient_id}")
    _verify_patient_match(smart_session, request.patient_id)

    try:
        fhir_client = FHIRClient(
            fhir_base_url=FHIR_BASE_URL,
            client_id=CLIENT_ID,
            access_token=smart_session.fhir_access_token
        )

        patient_data = fhir_client.get_patient_data(request.patient_id)

        evaluations = diagnostic_engine.evaluate_patient(
            patient_data=patient_data,
            chief_complaint=request.chief_complaint,
            focus_specialties=request.focus_specialties
        )

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
                        criterion=c.criterion, status=c.status.value,
                        value=c.value, expected=c.expected, details=c.details
                    ) for c in eval.criteria_met
                ],
                criteria_not_met=[
                    CriterionResponse(
                        criterion=c.criterion, status=c.status.value,
                        value=c.value, expected=c.expected, details=c.details
                    ) for c in eval.criteria_not_met
                ],
                criteria_unknown=[
                    CriterionResponse(
                        criterion=c.criterion, status=c.status.value,
                        value=c.value, expected=c.expected, details=c.details
                    ) for c in eval.criteria_unknown
                ],
                recommendations=eval.recommendations,
                missing_tests=eval.missing_tests
            ))

        logger.info(f"Returned {len(responses)} evaluations for patient {request.patient_id}")
        return responses

    except Exception as e:
        logger.error(f"Patient evaluation failed: {e}")
        raise HTTPException(status_code=500, detail="Evaluation failed. Please try relaunching from the EHR.")


@router.get("/patient/{patient_id}", response_model=PatientSummaryResponse)
async def get_patient_summary(
    patient_id: str,
    smart_session = Depends(get_active_smart_session),
):
    """
    Get patient clinical summary: high-level overview including abnormal
    labs and recent vitals, using the access token from the caller's
    server-side SMART session.
    """
    _verify_patient_match(smart_session, patient_id)
    try:
        fhir_client = FHIRClient(
            fhir_base_url=FHIR_BASE_URL,
            client_id=CLIENT_ID,
            access_token=smart_session.fhir_access_token
        )
        return _build_patient_summary(fhir_client, patient_id)

    except Exception as e:
        logger.error(f"Failed to get patient summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve patient data. Please try relaunching from the EHR.")


@router.get("/patient/{patient_id}/handoff", response_model=HandoffSummaryResponse)
async def get_patient_handoff_summary(
    patient_id: str,
    since: Optional[str] = Query(
        None,
        description="ISO timestamp to use as the update boundary instead of admission start (e.g. for a specific shift change). Defaults to the current admission's start time."
    ),
    smart_session = Depends(get_active_smart_session),
):
    """
    Shift-handoff summary: the full chart summary plus a delta of what's
    changed (labs, vitals, conditions, medications) since a timeframe
    boundary - the current admission's start by default, or a manually
    specified handoff time (e.g., start of the prior shift).
    """
    _verify_patient_match(smart_session, patient_id)
    try:
        fhir_client = FHIRClient(
            fhir_base_url=FHIR_BASE_URL,
            client_id=CLIENT_ID,
            access_token=smart_session.fhir_access_token
        )

        full_summary = _build_patient_summary(fhir_client, patient_id)

        admission_start_iso = None
        try:
            encounter = fhir_client.get_current_encounter(patient_id)
            if encounter:
                admission_start_iso = encounter.get("period", {}).get("start")
        except Exception as e:
            # Don't let an Encounter-query failure (e.g. unsupported by a
            # given sandbox) break the whole handoff view - fall back to
            # "none" and let a manual `since` still work.
            logger.warning(f"Could not fetch current encounter for {patient_id}: {e}")

        timeframe_start = None
        timeframe_source = "none"

        if since:
            try:
                timeframe_start = datetime.fromisoformat(since.replace("Z", "+00:00"))
                timeframe_source = "manual"
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid 'since' timestamp - use ISO 8601 format")
        elif admission_start_iso:
            try:
                timeframe_start = datetime.fromisoformat(admission_start_iso.replace("Z", "+00:00"))
                timeframe_source = "admission"
            except ValueError:
                timeframe_start = None

        updates_response = None
        raw_updates = None
        if timeframe_start is not None:
            raw_updates = fhir_client.get_patient_updates_since(patient_id, timeframe_start)

            updates_response = HandoffUpdatesResponse(
                new_lab_count=len(raw_updates["new_labs"]),
                new_abnormal_labs=[
                    {
                        "name": lab.display, "value": lab.value, "unit": lab.unit,
                        "reference_range": lab.reference_range,
                        "date": lab.effective_date.isoformat() if lab.effective_date else None
                    } for lab in raw_updates["new_abnormal_labs"]
                ],
                new_vital_count=len(raw_updates["new_vitals"]),
                new_conditions=[
                    HandoffUpdateItem(
                        name=(
                            c.get("code", {}).get("text")
                            or c.get("code", {}).get("coding", [{}])[0].get("display", "Unspecified condition")
                        ),
                        date=c.get("recordedDate")
                    ) for c in raw_updates["new_conditions"]
                ],
                new_medications=[
                    HandoffUpdateItem(
                        name=(
                            m.get("medicationCodeableConcept", {}).get("text")
                            or m.get("medicationCodeableConcept", {}).get("coding", [{}])[0].get("display", "Unspecified medication")
                        ),
                        date=m.get("authoredOn")
                    ) for m in raw_updates["new_medications"]
                ],
            )

        narrative = _generate_handoff_narrative(full_summary, raw_updates, timeframe_start, timeframe_source)

        return HandoffSummaryResponse(
            patient_id=patient_id,
            admission_start=admission_start_iso,
            timeframe_start=timeframe_start.isoformat() if timeframe_start else None,
            timeframe_source=timeframe_source,
            full_summary=full_summary,
            updates=updates_response,
            narrative=narrative
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get handoff summary for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve handoff summary. Please try relaunching from the EHR.")


@router.get("/patient/{patient_id}/differential", response_model=AmbulatoryDifferentialResponse)
async def get_ambulatory_differential(
    patient_id: str,
    symptoms: Optional[str] = Query(
        None,
        description="Comma-separated presenting symptoms/chief complaint to seed the search, in addition to whatever is extracted from the chart."
    ),
    lookback_days: Optional[int] = Query(
        None,
        description="Days of chart history to pull. Omit, or pass 0, for an unbounded pull covering the patient's full available chart regardless of age."
    ),
    smart_session = Depends(get_active_smart_session),
):
    """
    Ambulatory / ER full-chart differential.

    Unlike /patient/{id} and /patient/{id}/handoff (which serve the
    inpatient chart-summary flow and pull a handful of FHIR resource
    types over a bounded recency window), this endpoint pulls the
    patient's complete available chart - visit notes, H&Ps, procedures,
    immunizations, imaging, problem list, medications, allergies, and
    family/social history, unbounded by age unless lookback_days is
    explicitly set - via PatientHistoryService, authenticated with the
    same live SMART session token as every other /smart/* endpoint.

    The extracted chief complaints and vitals (plus any symptoms passed
    explicitly) are fed into the same rules-first, AI-fallback ranked
    differential engine used by the standalone symptom search feature
    (rank_diagnoses in symptom_search.py), so this is the same core
    diagnostic engine - just chart-driven instead of manually typed.
    """
    _verify_patient_match(smart_session, patient_id)

    client_host = None
    try:
        history_service = PatientHistoryService(
            fhir_base_url=FHIR_BASE_URL,
            auth_token=smart_session.fhir_access_token
        )

        patient_history = await history_service.get_comprehensive_history(
            patient_id=patient_id,
            lookback_days=lookback_days if lookback_days and lookback_days > 0 else None
        )

        search_terms: List[str] = []
        if symptoms:
            search_terms.extend(s.strip() for s in symptoms.split(",") if s.strip())

        _append_unique_terms(search_terms, derive_search_terms_from_history(patient_history))

        # Fall back to the active problem list if the chart yielded no
        # chief complaint/vitals-derived terms and the caller didn't pass
        # any symptoms directly - better than a bare 400 with nothing to
        # search from.
        if not search_terms and patient_history.active_conditions:
            _append_unique_terms(
                search_terms,
                [c.get("code") for c in patient_history.active_conditions if c.get("code")]
            )

        if not search_terms:
            raise HTTPException(
                status_code=422,
                detail="No symptoms available to search from. Pass ?symptoms=... or ensure the chart has chief complaints, vitals, or active conditions on file."
            )

        AuditLogger.log_security_event(
            "ambulatory_differential",
            {
                "patient_id": patient_id,
                "search_term_count": len(search_terms),
                "lookback_days": lookback_days,
            }
        )

        differential, ai_tree_info = await rank_diagnoses(
            search_terms,
            age=patient_history.age,
            sex=patient_history.gender,
        )

        data_pulled = {
            "visit_notes": len(patient_history.visit_notes),
            "history_and_physicals": len(patient_history.history_and_physicals),
            "vital_signs": len(patient_history.vital_signs),
            "diagnostic_tests": len(patient_history.diagnostic_tests),
            "procedures": len(patient_history.procedures),
            "imaging_studies": len(patient_history.imaging_studies),
            "immunizations": len(patient_history.immunizations),
            "active_conditions": len(patient_history.active_conditions),
            "past_conditions": len(patient_history.past_conditions),
            "current_medications": len(patient_history.current_medications),
            "allergies": len(patient_history.allergies),
        }

        return AmbulatoryDifferentialResponse(
            patient_id=patient_id,
            name=patient_history.patient_name,
            age=patient_history.age,
            gender=patient_history.gender,
            chart_summary=patient_history.summary or "",
            data_pulled=data_pulled,
            search_terms_used=search_terms,
            differential=differential,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to build ambulatory differential for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to build differential. Please try relaunching from the EHR.")


@router.get("/session/status", response_model=SmartSessionStatusResponse)
async def get_smart_session_status(
    realdiag_smart_session: Optional[str] = Cookie(default=None, alias=SMART_SESSION_COOKIE_NAME)
):
    """
    Lightweight, non-throwing check for whether the caller has an active
    SMART session. The main app's nav polls this (credentials: 'include')
    to decide whether to show the Inpatient link - most users won't have
    an active SMART session, and that's an expected, non-error state here.
    """
    session = get_smart_session(realdiag_smart_session) if realdiag_smart_session else None
    if not session or session.expires_at < datetime.utcnow():
        return SmartSessionStatusResponse(active=False)
    return SmartSessionStatusResponse(
        active=True,
        patient_id=session.patient_id,
        ehr_vendor=session.ehr_vendor,
    )


@router.get("/config")
async def get_smart_config():
    """
    Get SMART on FHIR configuration needed for frontend SMART launch.
    """
    return {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scopes": ["launch", "patient/*.read", "openid", "fhirUser"],
        "fhir_base_url": FHIR_BASE_URL
    }
