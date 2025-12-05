"""
Integration Services Router
===========================

Provides integration endpoints for EHR systems, FHIR export, HL7 messaging,
webhooks, and API key management for third-party integrations.

AUTHENTICATION:
- API Key (for system-to-system integration): Pass X-API-Key header
- User Authentication (for logged-in users): JWT token in Authorization header or cookie
"""

from fastapi import APIRouter, HTTPException, Header, Depends, Body
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
import hashlib
import secrets
import json
from backend.services.auth_service import get_current_user, get_optional_user
from backend.services.subscription_gate import SubscriptionGate

router = APIRouter(prefix="/integration", tags=["integration"])

# Import user subscriptions
from backend.services.subscription_router import user_subscriptions

# Models
class FHIRConditionRequest(BaseModel):
    """Request to convert a diagnosis to FHIR Condition resource."""
    rule_id: str
    patient_id: str = Field(..., description="Patient identifier")
    encounter_id: Optional[str] = Field(None, description="Encounter identifier")
    clinical_status: str = Field(default="active", description="active | recurrence | relapse | inactive | remission | resolved")
    verification_status: str = Field(default="provisional", description="provisional | differential | confirmed | refuted")
    severity: Optional[str] = Field(None, description="mild | moderate | severe")
    onset_datetime: Optional[str] = Field(None, description="ISO 8601 datetime")
    note: Optional[str] = Field(None, description="Additional clinical notes")


class HL7MessageRequest(BaseModel):
    """Request to generate HL7 v2 message."""
    message_type: str = Field(..., description="ADT, ORU, ORM, etc.")
    rule_id: str
    patient_id: str
    patient_name: str
    patient_dob: Optional[str] = None
    encounter_id: Optional[str] = None
    ordering_provider: Optional[str] = None


class WebhookRegistration(BaseModel):
    """Register a webhook endpoint."""
    url: str = Field(..., description="HTTPS URL to receive webhook notifications")
    events: List[str] = Field(..., description="Event types to subscribe to: ['diagnosis.created', 'diagnosis.updated']")
    secret: Optional[str] = Field(None, description="Secret for webhook signature verification")
    description: Optional[str] = Field(None, description="Description of this webhook")


class APIKeyCreate(BaseModel):
    """Create new API key."""
    name: str = Field(..., description="Descriptive name for this API key")
    scopes: List[str] = Field(default=["read"], description="Permissions: read, write, admin")
    expires_days: Optional[int] = Field(default=365, description="Days until expiration (null = never)")


class DiagnosisExportRequest(BaseModel):
    """Export diagnosis in various formats."""
    rule_id: str
    format: str = Field(..., description="fhir | hl7 | json | xml | csv")
    patient_context: Optional[Dict[str, Any]] = Field(None, description="Patient context for personalized export")


# In-memory storage (replace with database in production)
webhooks_db = {}
api_keys_db = {}


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Verify API key from header (for system-to-system integration)."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    if x_api_key not in api_keys_db:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    key_data = api_keys_db[x_api_key]
    if key_data.get("revoked"):
        raise HTTPException(status_code=401, detail="API key revoked")
    
    # Check expiration
    if key_data.get("expires_at"):
        if datetime.fromisoformat(key_data["expires_at"]) < datetime.now():
            raise HTTPException(status_code=401, detail="API key expired")
    
    return x_api_key


def verify_user_or_api_key(
    x_api_key: Optional[str] = Header(None),
    current_user: Optional[Dict] = Depends(get_optional_user)
) -> Dict[str, Any]:
    """
    Verify either user authentication OR API key.
    
    Returns authentication context:
    - {'type': 'user', 'user_id': '...', 'email': '...'} for logged-in users
    - {'type': 'api_key', 'key': '...'} for API key authentication
    
    Raises 401 if neither authentication method is provided.
    """
    # Check user authentication first
    if current_user:
        return {
            'type': 'user',
            'user_id': current_user.get('user_id'),
            'email': current_user.get('email'),
            'full_name': current_user.get('full_name')
        }
    
    # Fall back to API key
    if x_api_key:
        api_key = verify_api_key(x_api_key)
        return {
            'type': 'api_key',
            'key': api_key,
            'name': api_keys_db.get(api_key, {}).get('name', 'Unknown')
        }
    
    # No authentication provided
    raise HTTPException(
        status_code=401,
        detail="Authentication required: Provide either user login (JWT token) or API key (X-API-Key header)"
    )


@router.post("/fhir/condition")
async def export_to_fhir_condition(
    request: FHIRConditionRequest,
    auth: Dict[str, Any] = Depends(verify_user_or_api_key)
):
    """
    Convert a RealDiag diagnosis to FHIR R4 Condition resource.
    
    ⚠️ REQUIRES AUTHENTICATION (User login OR API key)
    
    Returns a FHIR-compliant JSON Condition resource that can be imported
    into EHR systems supporting FHIR.
    """
    # Load rule (simplified - should use RulesEngine)
    from .rules_engine import RulesEngine
    engine = RulesEngine()
    rule = engine.get_rule(request.rule_id)
    
    if "error" in rule:
        raise HTTPException(status_code=404, detail=f"Rule not found: {request.rule_id}")
    
    # Build FHIR Condition resource
    condition = {
        "resourceType": "Condition",
        "id": f"realdiag-{request.rule_id}-{datetime.now().timestamp()}",
        "meta": {
            "profile": ["http://hl7.org/fhir/StructureDefinition/Condition"],
            "source": "RealDiag Clinical Decision Support System"
        },
        "clinicalStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                "code": request.clinical_status
            }]
        },
        "verificationStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                "code": request.verification_status
            }]
        },
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                "code": "encounter-diagnosis",
                "display": "Encounter Diagnosis"
            }]
        }],
        "code": {
            "coding": [],
            "text": rule.get("label", "Unknown Condition")
        },
        "subject": {
            "reference": f"Patient/{request.patient_id}"
        },
        "recordedDate": datetime.now().isoformat()
    }
    
    # Add ICD-10 codes
    if rule.get("icd10"):
        for icd10_code in rule["icd10"]:
            condition["code"]["coding"].append({
                "system": "http://hl7.org/fhir/sid/icd-10-cm",
                "code": icd10_code
            })
    
    # Add SNOMED codes
    if rule.get("snomed"):
        for snomed_code in rule["snomed"]:
            condition["code"]["coding"].append({
                "system": "http://snomed.info/sct",
                "code": str(snomed_code)
            })
    
    # Add encounter reference
    if request.encounter_id:
        condition["encounter"] = {
            "reference": f"Encounter/{request.encounter_id}"
        }
    
    # Add severity
    if request.severity:
        condition["severity"] = {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "255604002" if request.severity == "mild" else "6736007" if request.severity == "moderate" else "24484000",
                "display": request.severity.capitalize()
            }]
        }
    
    # Add onset
    if request.onset_datetime:
        condition["onsetDateTime"] = request.onset_datetime
    
    # Add note
    if request.note:
        condition["note"] = [{
            "text": request.note
        }]
    
    return {
        "fhir_resource": condition,
        "format": "FHIR R4",
        "resource_type": "Condition"
    }


@router.post("/hl7/message")
async def generate_hl7_message(
    request: HL7MessageRequest,
    auth: Dict[str, Any] = Depends(verify_user_or_api_key)
):
    """
    Generate HL7 v2 message for diagnosis.
    
    Supports common message types for interfacing with legacy clinical systems.
    """
    from .rules_engine import RulesEngine
    engine = RulesEngine()
    rule = engine.get_rule(request.rule_id)
    
    if "error" in rule:
        raise HTTPException(status_code=404, detail=f"Rule not found: {request.rule_id}")
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    message_id = secrets.token_hex(8)
    
    # Build HL7 message (simplified ORU^R01 - Observation Result)
    hl7_segments = []
    
    # MSH - Message Header
    hl7_segments.append(
        f"MSH|^~\\&|RealDiag|RealDiag System|EHR|Hospital|{timestamp}||{request.message_type}^R01|{message_id}|P|2.5"
    )
    
    # PID - Patient Identification
    patient_name_hl7 = request.patient_name.replace(" ", "^")
    dob = request.patient_dob or ""
    hl7_segments.append(
        f"PID|1||{request.patient_id}||{patient_name_hl7}||{dob}|"
    )
    
    # PV1 - Patient Visit (if encounter provided)
    if request.encounter_id:
        provider = request.ordering_provider or ""
        hl7_segments.append(
            f"PV1|1|O|||||{provider}|||||||||||{request.encounter_id}|"
        )
    
    # OBR - Observation Request
    hl7_segments.append(
        f"OBR|1|{request.encounter_id or ''}||DIAG^Diagnosis||{timestamp}|||||||{request.ordering_provider or ''}|"
    )
    
    # OBX - Observation/Result (Diagnosis)
    icd10_codes = rule.get("icd10", [])
    icd10_str = ", ".join(icd10_codes) if icd10_codes else ""
    
    hl7_segments.append(
        f"OBX|1|CE|DIAG^Diagnosis||{request.rule_id}^{rule.get('label', '')}^RealDiag||||||F|||{timestamp}"
    )
    
    # Add ICD-10 codes as additional observations
    for idx, icd10_code in enumerate(icd10_codes, start=2):
        hl7_segments.append(
            f"OBX|{idx}|CE|ICD10^ICD-10 Code||{icd10_code}||||||F|||{timestamp}"
        )
    
    hl7_message = "\r".join(hl7_segments)
    
    return {
        "hl7_message": hl7_message,
        "message_type": request.message_type,
        "version": "HL7 v2.5",
        "encoding": "UTF-8",
        "segments": len(hl7_segments)
    }


@router.post("/webhooks/register")
async def register_webhook(
    webhook: WebhookRegistration,
    auth: Dict[str, Any] = Depends(verify_user_or_api_key)
):
    """
    Register a webhook endpoint to receive real-time notifications.
    
    ⚠️ REQUIRES AUTHENTICATION (User login OR API key)
    
    Supported events:
    - diagnosis.created: New diagnosis generated
    - diagnosis.updated: Existing diagnosis modified
    - search.performed: Symptom search performed
    """
    # Validate URL
    if not webhook.url.startswith("https://"):
        raise HTTPException(status_code=400, detail="Webhook URL must use HTTPS")
    
    # Validate events
    valid_events = ["diagnosis.created", "diagnosis.updated", "search.performed"]
    for event in webhook.events:
        if event not in valid_events:
            raise HTTPException(status_code=400, detail=f"Invalid event type: {event}")
    
    # Generate webhook ID
    webhook_id = secrets.token_hex(16)
    
    # Generate secret if not provided
    if not webhook.secret:
        webhook.secret = secrets.token_hex(32)
    
    webhooks_db[webhook_id] = {
        "id": webhook_id,
        "url": webhook.url,
        "events": webhook.events,
        "secret": webhook.secret,
        "description": webhook.description,
        "created_at": datetime.now().isoformat(),
        "active": True
    }
    
    return {
        "webhook_id": webhook_id,
        "secret": webhook.secret,
        "events": webhook.events,
        "message": "Webhook registered successfully. Use the secret to verify webhook signatures."
    }


@router.get("/webhooks")
async def list_webhooks(auth: Dict[str, Any] = Depends(verify_user_or_api_key)):
    """
    List all registered webhooks.
    
    ⚠️ REQUIRES AUTHENTICATION (User login OR API key)
    """
    return {
        "webhooks": [
            {k: v for k, v in webhook.items() if k != "secret"}
            for webhook in webhooks_db.values()
        ]
    }


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: str, auth: Dict[str, Any] = Depends(verify_user_or_api_key)):
    """
    Delete a registered webhook.
    
    ⚠️ REQUIRES AUTHENTICATION (User login OR API key)
    """
    if webhook_id not in webhooks_db:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    del webhooks_db[webhook_id]
    return {"message": "Webhook deleted successfully"}


@router.post("/api-keys")
async def create_api_key(
    key_request: APIKeyCreate,
    current_user: Dict = Depends(get_current_user)
):
    """
    Create a new API key for integration access.
    
    ⚠️ REQUIRES USER AUTHENTICATION
    
    Creates API keys tied to your user account for third-party integrations.
    """
    # Associate API key with user who created it
    user_id = current_user.get("user_id")
    # Generate API key
    api_key = f"rdiag_{secrets.token_urlsafe(32)}"
    
    # Calculate expiration
    expires_at = None
    if key_request.expires_days:
        from datetime import timedelta
        expires_at = (datetime.now() + timedelta(days=key_request.expires_days)).isoformat()
    
    api_keys_db[api_key] = {
        "key": api_key,
        "name": key_request.name,
        "scopes": key_request.scopes,
        "user_id": user_id,  # Track which user created this key
        "created_at": datetime.now().isoformat(),
        "expires_at": expires_at,
        "revoked": False
    }
    
    return {
        "api_key": api_key,
        "name": key_request.name,
        "scopes": key_request.scopes,
        "expires_at": expires_at,
        "message": "API key created successfully. Store this key securely - it cannot be retrieved again."
    }


@router.get("/api-keys")
async def list_api_keys(current_user: Dict = Depends(get_current_user)):
    """
    List all API keys created by the authenticated user (excluding the key values).
    
    ⚠️ REQUIRES USER AUTHENTICATION
    """
    user_id = current_user.get("user_id")
    
    # Filter to only show user's own API keys
    user_keys = [
        {k: v for k, v in key_data.items() if k != "key"}
        for key_data in api_keys_db.values()
        if key_data.get("user_id") == user_id
    ]
    
    return {
        "api_keys": user_keys,
        "total": len(user_keys)
    }


@router.post("/export")
async def export_diagnosis(
    export_request: DiagnosisExportRequest,
    auth: Dict[str, Any] = Depends(verify_user_or_api_key)
):
    """
    Export diagnosis in multiple formats for integration with external systems.
    
    ⚠️ REQUIRES AUTHENTICATION (User login OR API key)
    🔐 REQUIRES SUBSCRIPTION: Export features based on plan level
    
    Supports: FHIR, HL7, JSON, XML, CSV formats.
    
    Feature Access:
    - JSON Export: All plans
    - FHIR Export: Professional+ and above
    - HL7 Export: Organization and above
    - Bulk Export: Enterprise only
    """
    # Check subscription for export features
    if auth.get("auth_type") == "user":
        user = auth.get("user")
        async with SubscriptionGate(user, user_subscriptions) as gate:
            # Check export format access
            if export_request.format == "fhir":
                gate.require_feature("fhir_export")
            elif export_request.format == "hl7":
                gate.require_feature("ehr_integration")
            elif export_request.format in ["xml", "csv"]:
                gate.require_feature("bulk_export")
    from .rules_engine import RulesEngine
    engine = RulesEngine()
    rule = engine.get_rule(export_request.rule_id)
    
    if "error" in rule:
        raise HTTPException(status_code=404, detail=f"Rule not found: {export_request.rule_id}")
    
    if export_request.format == "fhir":
        # Delegate to FHIR endpoint
        fhir_request = FHIRConditionRequest(
            rule_id=export_request.rule_id,
            patient_id=export_request.patient_context.get("patient_id", "unknown") if export_request.patient_context else "unknown"
        )
        return await export_to_fhir_condition(fhir_request, auth)
    
    elif export_request.format == "json":
        return {
            "format": "JSON",
            "data": rule
        }
    
    elif export_request.format == "xml":
        # Simple XML conversion
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<diagnosis>
  <id>{rule.get('id', '')}</id>
  <label>{rule.get('label', '')}</label>
  <family>{rule.get('family', '')}</family>
  <presentations>
    {''.join(f'<item>{p}</item>' for p in rule.get('presentations', []))}
  </presentations>
  <icd10>
    {''.join(f'<code>{c}</code>' for c in rule.get('icd10', []))}
  </icd10>
</diagnosis>"""
        return {
            "format": "XML",
            "data": xml
        }
    
    elif export_request.format == "csv":
        # CSV row format
        csv_data = {
            "id": rule.get("id", ""),
            "label": rule.get("label", ""),
            "family": rule.get("family", ""),
            "icd10_codes": ", ".join(rule.get("icd10", [])),
            "presentations": " | ".join(rule.get("presentations", []))
        }
        return {
            "format": "CSV",
            "data": csv_data
        }
    
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {export_request.format}")


@router.get("/health")
async def integration_health():
    """Health check for integration services."""
    return {
        "status": "healthy",
        "services": {
            "fhir": "available",
            "hl7": "available",
            "webhooks": "available",
            "api_keys": "available",
            "pdf_export": "available",
            "ehr_integration": "available",
            "cpoe": "available"
        },
        "active_webhooks": len(webhooks_db),
        "active_api_keys": len([k for k in api_keys_db.values() if not k.get("revoked")])
    }


# ========================================
# NEW: PDF Export Endpoints
# ========================================

@router.post("/export/pdf/diagnosis")
async def export_diagnosis_pdf(
    diagnosis_data: Dict[str, Any] = Body(...),
    patient_info: Optional[Dict[str, Any]] = Body(None),
    clinical_context: Optional[str] = Body(None),
    auth: Dict[str, Any] = Depends(verify_user_or_api_key)
):
    """
    Generate PDF report for a single diagnosis.
    
    ⚠️ REQUIRES AUTHENTICATION (User login OR API key)
    
    Request body:
    ```json
    {
      "diagnosis_data": {
        "label": "Acute Coronary Syndrome",
        "family": "cardiology",
        "icd10": ["I21.9"],
        "snomed": ["394659003"],
        "presentations": ["chest pain", "dyspnea"],
        "clinical_pearls": ["Troponin elevation is key"],
        "management": ["Aspirin 325mg", "Heparin"],
        "tests": ["ECG", "Troponin"],
        "referrals": ["Cardiology"]
      },
      "patient_info": {
        "id": "MRN123",
        "name": "John Doe",
        "dob": "1970-01-01",
        "age": 54
      },
      "clinical_context": "Presented with acute chest pain..."
    }
    ```
    """
    from backend.services.pdf_export import PDFReportGenerator
    from fastapi.responses import StreamingResponse
    
    try:
        generator = PDFReportGenerator()
        pdf_buffer = generator.generate_diagnosis_report(
            diagnosis=diagnosis_data,
            patient_info=patient_info,
            clinical_context=clinical_context
        )
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=diagnosis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.post("/export/pdf/differential")
async def export_differential_pdf(
    diagnoses: List[Dict[str, Any]] = Body(...),
    patient_info: Optional[Dict[str, Any]] = Body(None),
    search_criteria: Optional[str] = Body(None),
    auth: Dict[str, Any] = Depends(verify_user_or_api_key)
):
    """
    Generate PDF report for differential diagnoses.
    
    ⚠️ REQUIRES AUTHENTICATION (User login OR API key)
    
    Request body:
    ```json
    {
      "diagnoses": [
        {"label": "ACS", "match_score": 8.5, ...},
        {"label": "PE", "match_score": 7.2, ...}
      ],
      "patient_info": {"id": "MRN123", "name": "John Doe"},
      "search_criteria": "chest pain + dyspnea + diaphoresis"
    }
    ```
    """
    from backend.services.pdf_export import PDFReportGenerator
    from fastapi.responses import StreamingResponse
    
    try:
        generator = PDFReportGenerator()
        pdf_buffer = generator.generate_multi_diagnosis_report(
            diagnoses=diagnoses,
            patient_info=patient_info,
            search_criteria=search_criteria
        )
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=differential_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


# ========================================
# NEW: EHR Data Pull Endpoints
# ========================================

# In-memory FHIR server configurations (replace with database in production)
fhir_configs: Dict[str, Dict[str, Any]] = {}


class FHIRConfigRequest(BaseModel):
    """Configure FHIR server connection."""
    config_name: str
    base_url: str
    auth_type: str = Field(default="none", description="none, basic, bearer, oauth2")
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None


@router.post("/ehr/fhir/configure")
async def configure_fhir_server(
    config: FHIRConfigRequest,
    auth: Dict[str, Any] = Depends(verify_user_or_api_key)
):
    """
    Configure connection to FHIR server for pulling patient data.
    
    ⚠️ REQUIRES AUTHENTICATION (User login OR API key)
    
    Example:
    ```json
    {
      "config_name": "main_ehr",
      "base_url": "https://fhir.hospital.org/api",
      "auth_type": "bearer",
      "token": "eyJhbGc..."
    }
    ```
    """
    fhir_configs[config.config_name] = {
        "base_url": config.base_url,
        "auth_type": config.auth_type,
        "username": config.username,
        "password": config.password,
        "token": config.token,
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "message": f"FHIR server '{config.config_name}' configured successfully",
        "config_name": config.config_name
    }


@router.get("/ehr/fhir/pull/patient/{patient_id}")
async def pull_patient_data(
    patient_id: str,
    config_name: str = "main_ehr",
    auth: Dict[str, Any] = Depends(verify_user_or_api_key)
):
    """
    Pull comprehensive patient data from EHR via FHIR.
    
    ⚠️ REQUIRES AUTHENTICATION (User login OR API key)
    
    Returns patient demographics, conditions, medications, allergies,
    recent vitals, and recent lab results.
    
    Example: GET /ehr/fhir/pull/patient/12345?config_name=main_ehr
    """
    from backend.services.ehr_integration import EHRIntegrationService, FHIRServerConfig
    
    if config_name not in fhir_configs:
        raise HTTPException(
            status_code=404,
            detail=f"FHIR configuration '{config_name}' not found. Configure it first with POST /ehr/fhir/configure"
        )
    
    config_data = fhir_configs[config_name]
    fhir_config = FHIRServerConfig(
        base_url=config_data["base_url"],
        auth_type=config_data["auth_type"],
        username=config_data.get("username"),
        password=config_data.get("password"),
        token=config_data.get("token")
    )
    
    ehr_service = EHRIntegrationService(config=fhir_config)
    
    try:
        patient_data = await ehr_service.pull_patient_data(patient_id)
        return patient_data.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to pull patient data: {str(e)}")


@router.get("/ehr/fhir/search/patients")
async def search_patients(
    name: Optional[str] = None,
    identifier: Optional[str] = None,
    birth_date: Optional[str] = None,
    config_name: str = "main_ehr",
    auth: Dict[str, Any] = Depends(verify_user_or_api_key)
):
    """
    Search for patients in EHR system.
    
    ⚠️ REQUIRES AUTHENTICATION (User login OR API key)
    
    Query parameters:
    - name: Patient name
    - identifier: MRN or other identifier
    - birth_date: Birth date (YYYY-MM-DD)
    - config_name: FHIR configuration to use
    
    Example: GET /ehr/fhir/search/patients?name=John%20Doe&config_name=main_ehr
    """
    from backend.services.ehr_integration import EHRIntegrationService, FHIRServerConfig
    
    if config_name not in fhir_configs:
        raise HTTPException(status_code=404, detail=f"FHIR configuration '{config_name}' not found")
    
    config_data = fhir_configs[config_name]
    fhir_config = FHIRServerConfig(
        base_url=config_data["base_url"],
        auth_type=config_data["auth_type"],
        username=config_data.get("username"),
        password=config_data.get("password"),
        token=config_data.get("token")
    )
    
    ehr_service = EHRIntegrationService(config=fhir_config)
    
    try:
        patients = await ehr_service.search_patients(
            name=name,
            identifier=identifier,
            birth_date=birth_date
        )
        return {"patients": patients, "count": len(patients)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Patient search failed: {str(e)}")


# ========================================
# NEW: CPOE Integration Endpoints
# ========================================

@router.post("/cpoe/order")
async def create_cpoe_order(
    order_type: str = Body(..., description="lab, imaging, referral, medication"),
    description: str = Body(...),
    patient_id: str = Body(...),
    encounter_id: Optional[str] = Body(None),
    priority: str = Body("routine", description="stat, urgent, routine"),
    ordering_provider: str = Body(...),
    clinical_indication: Optional[str] = Body(None),
    diagnosis_codes: List[str] = Body(default=[]),
    config_name: str = Body("main_ehr"),
    auth: Dict[str, Any] = Depends(verify_user_or_api_key)
):
    """
    Create order in CPOE system via FHIR ServiceRequest.
    
    ⚠️ REQUIRES AUTHENTICATION (User login OR API key)
    
    Sends orders for labs, imaging, referrals, or medications to the EHR's
    computerized provider order entry system.
    
    Request body:
    ```json
    {
      "order_type": "lab",
      "description": "Troponin I",
      "patient_id": "12345",
      "encounter_id": "visit-789",
      "priority": "stat",
      "ordering_provider": "Dr. Smith",
      "clinical_indication": "Suspected ACS",
      "diagnosis_codes": ["I21.9"],
      "config_name": "main_ehr"
    }
    ```
    """
    from backend.services.ehr_integration import EHRIntegrationService, FHIRServerConfig, CPOEOrder
    
    if config_name not in fhir_configs:
        raise HTTPException(status_code=404, detail=f"FHIR configuration '{config_name}' not found")
    
    config_data = fhir_configs[config_name]
    fhir_config = FHIRServerConfig(
        base_url=config_data["base_url"],
        auth_type=config_data["auth_type"],
        username=config_data.get("username"),
        password=config_data.get("password"),
        token=config_data.get("token")
    )
    
    ehr_service = EHRIntegrationService(config=fhir_config)
    
    order = CPOEOrder(
        order_type=order_type,
        description=description,
        patient_id=patient_id,
        encounter_id=encounter_id,
        priority=priority,
        ordering_provider=ordering_provider,
        clinical_indication=clinical_indication,
        diagnosis_codes=diagnosis_codes
    )
    
    try:
        service_request = await ehr_service.create_cpoe_order(order)
        return {
            "message": "Order created successfully",
            "order_id": service_request.get("id"),
            "status": service_request.get("status"),
            "service_request": service_request
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")


@router.get("/ehr/fhir/comprehensive-history/{patient_id}")
async def get_comprehensive_patient_history(
    patient_id: str,
    config_name: str = "main_ehr",
    lookback_days: int = 365,
    include_resolved: bool = True,
    auth: Dict[str, Any] = Depends(verify_user_or_api_key)
):
    """
    Retrieve comprehensive patient history including visit notes, diagnostic tests, H&Ps, and more.
    
    ⚠️ REQUIRES AUTHENTICATION (User login OR API key)
    
    This endpoint provides complete patient history for comprehensive diagnostic decision support:
    
    **Retrieved Data:**
    - **Visit Notes**: All clinical documentation from prior encounters
    - **Diagnostic Tests**: Lab results, imaging reports, diagnostic procedures
    - **History & Physicals**: Complete H&P examinations with structured sections
    - **Procedures**: Surgical and interventional procedures performed
    - **Imaging Studies**: CT, MRI, X-Ray, Ultrasound reports with findings
    - **Problem List**: Active and resolved medical conditions
    - **Medications**: Current and historical medication lists
    - **Allergies**: All documented allergies and intolerances
    - **Family History**: Hereditary conditions and risk factors
    - **Social History**: Smoking, alcohol, occupation, living situation
    
    **Parameters:**
    - `patient_id`: FHIR Patient resource ID
    - `config_name`: Name of configured FHIR server (default: "main_ehr")
    - `lookback_days`: Number of days to look back for historical data (default: 365)
    - `include_resolved`: Include resolved/inactive conditions (default: true)
    
    **Example:**
    ```bash
    curl -X GET "https://api.realdiag.com/integration/ehr/fhir/comprehensive-history/patient-12345?lookback_days=730" \\
      -H "X-API-Key: your_api_key"
    ```
    
    **Response includes:**
    - Complete patient demographics
    - Chronological visit notes with content
    - All diagnostic test results with abnormal flags
    - Structured H&P documents
    - Procedure history
    - Imaging study results
    - Active and past problem lists
    - Comprehensive medication history
    - Clinical summary narrative
    
    **Use Case:**
    Use this endpoint to pull complete patient context before diagnostic evaluation,
    enabling the decision support system to consider:
    - Prior similar presentations
    - Trending lab values
    - Comorbidities and risk factors
    - Previous diagnostic workups
    - Treatment history and responses
    """
    from backend.services.patient_history_service import PatientHistoryService
    
    if config_name not in fhir_configs:
        raise HTTPException(status_code=404, detail=f"FHIR configuration '{config_name}' not found")
    
    config_data = fhir_configs[config_name]
    
    # Initialize patient history service
    history_service = PatientHistoryService(
        fhir_base_url=config_data["base_url"],
        auth_token=config_data.get("token")
    )
    
    try:
        comprehensive_history = await history_service.get_comprehensive_history(
            patient_id=patient_id,
            lookback_days=lookback_days,
            include_resolved=include_resolved
        )
        
        return {
            "patient_id": comprehensive_history.patient_id,
            "patient_name": comprehensive_history.patient_name,
            "demographics": {
                "date_of_birth": comprehensive_history.date_of_birth,
                "age": comprehensive_history.age,
                "gender": comprehensive_history.gender
            },
            "visit_notes": [note.dict() for note in comprehensive_history.visit_notes],
            "diagnostic_tests": [test.dict() for test in comprehensive_history.diagnostic_tests],
            "history_and_physicals": [hp.dict() for hp in comprehensive_history.history_and_physicals],
            "procedures": [proc.dict() for proc in comprehensive_history.procedures],
            "imaging_studies": [img.dict() for img in comprehensive_history.imaging_studies],
            "problem_list": {
                "active": comprehensive_history.active_conditions,
                "resolved": comprehensive_history.past_conditions
            },
            "medications": {
                "current": comprehensive_history.current_medications,
                "historical": comprehensive_history.medication_history
            },
            "allergies": comprehensive_history.allergies,
            "family_history": comprehensive_history.family_history,
            "social_history": comprehensive_history.social_history,
            "summary": comprehensive_history.summary,
            "data_quality": {
                "visit_notes_count": len(comprehensive_history.visit_notes),
                "diagnostic_tests_count": len(comprehensive_history.diagnostic_tests),
                "abnormal_tests_count": len([t for t in comprehensive_history.diagnostic_tests if t.abnormal]),
                "critical_tests_count": len([t for t in comprehensive_history.diagnostic_tests if t.critical]),
                "h_and_p_count": len(comprehensive_history.history_and_physicals),
                "procedures_count": len(comprehensive_history.procedures),
                "imaging_studies_count": len(comprehensive_history.imaging_studies),
                "lookback_days": lookback_days
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve patient history: {str(e)}")
