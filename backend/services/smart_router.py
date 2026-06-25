"""
SMART on FHIR Router

Implements SMART on FHIR launch sequence and clinical decision support endpoints
for Epic and other EHR integration.

Endpoints:
    GET  /smart/launch           - SMART launch entry point
    GET  /smart/callback         - OAuth callback handler
    POST /smart/evaluate-patient - Evaluate patient with CDS
    GET  /smart/patient/{id}     - Get patient summary
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging
from datetime import datetime

from ..services.fhir_client import FHIRClient, PatientData, CommonLOINC
from ..services.smart_diagnostic_engine import SmartDiagnosticEngine, DiagnosisEvaluation
from ..services.ehr_adapter import EHRAdapter, EHRVendor

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

# Global instances (in production, use dependency injection)
diagnostic_engine = SmartDiagnosticEngine()


class EvaluatePatientRequest(BaseModel):
    """Request to evaluate patient with clinical decision support."""
    patient_id: str
    chief_complaint: Optional[str] = None
    focus_specialties: Optional[List[str]] = None
    access_token: str


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
    
    Args:
        iss: FHIR server issuer URL
        launch: Launch context token from EHR
        
    Returns:
        Redirect to EHR authorization page
    """
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
        "state": f"iss={iss}",  # Include issuer in state
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
    state: Optional[str] = Query(None, description="State parameter")
):
    """
    OAuth callback handler.
    
    Exchanges authorization code for access token and launches the app.
    
    Args:
        code: Authorization code from EHR
        state: State parameter (contains issuer)
        
    Returns:
        HTML page that launches the SMART app
    """
    logger.info(f"OAuth callback received with code: {code[:10]}...")
    
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
        patient_id = token_data.get("patient")  # Patient ID from launch context
        
        # In production, store token securely and redirect to app
        # For now, return simple HTML with token
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>RealDiag SMART Launch</title>
            <style>
                body {{
                    font-family: system-ui, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }}
                .container {{
                    background: white;
                    color: #333;
                    padding: 30px;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                }}
                h1 {{ color: #667eea; }}
                .success {{ color: #10b981; font-weight: 600; }}
                .token {{ 
                    background: #f3f4f6; 
                    padding: 10px; 
                    border-radius: 6px;
                    word-break: break-all;
                    font-family: monospace;
                    font-size: 12px;
                }}
                button {{
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 16px;
                    margin-top: 20px;
                }}
                button:hover {{ background: #5568d3; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎉 RealDiag SMART Launch Successful</h1>
                <p class="success">✓ Connected to Epic FHIR Server</p>
                <p><strong>Patient ID:</strong> {patient_id or 'Not provided'}</p>
                <p><strong>Access Token:</strong></p>
                <div class="token">{access_token[:50]}...</div>
                
                <button onclick="launchDiagnostics()">
                    Launch Clinical Decision Support
                </button>
                
                <script>
                    function launchDiagnostics() {{
                        // Store token and patient ID
                        sessionStorage.setItem('fhir_token', '{access_token}');
                        sessionStorage.setItem('patient_id', '{patient_id}');
                        
                        // Redirect to main app with patient context
                        window.location.href = '/symptom?patient_id={patient_id}&smart=true';
                    }}
                </script>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.post("/evaluate-patient", response_model=List[DiagnosisResponse])
async def evaluate_patient(request: EvaluatePatientRequest):
    """
    Evaluate patient data against diagnostic rules.
    
    This endpoint performs real-time clinical decision support by:
    1. Fetching patient data from FHIR server
    2. Evaluating against diagnostic criteria
    3. Returning matched diagnoses with recommendations
    
    Args:
        request: Patient evaluation request with patient_id and access_token
        
    Returns:
        List of diagnosis evaluations sorted by probability
    """
    logger.info(f"Evaluating patient {request.patient_id}")
    
    try:
        # Initialize FHIR client with access token
        fhir_client = FHIRClient(
            fhir_base_url=FHIR_BASE_URL,
            client_id=CLIENT_ID,
            access_token=request.access_token
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
    access_token: str = Query(..., description="FHIR access token")
):
    """
    Get patient clinical summary.
    
    Returns high-level overview of patient's clinical data including
    abnormal labs and recent vitals.
    
    Args:
        patient_id: Patient FHIR ID
        access_token: FHIR access token
        
    Returns:
        Patient summary with key clinical information
    """
    try:
        fhir_client = FHIRClient(
            fhir_base_url=FHIR_BASE_URL,
            client_id=CLIENT_ID,
            access_token=access_token
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
            abnormal_labs=abnormal_labs[:10],  # Top 10 abnormal labs
            recent_vitals=vital_summary[:10]  # Recent vitals
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
