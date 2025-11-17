"""
Integration Services Router
===========================

Provides integration endpoints for EHR systems, FHIR export, HL7 messaging,
webhooks, and API key management for third-party integrations.
"""

from fastapi import APIRouter, HTTPException, Header, Depends, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import hashlib
import secrets
import json

router = APIRouter(prefix="/integration", tags=["integration"])

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
    """Verify API key from header."""
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


@router.post("/fhir/condition")
async def export_to_fhir_condition(
    request: FHIRConditionRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Convert a RealDiag diagnosis to FHIR R4 Condition resource.
    
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
    api_key: str = Depends(verify_api_key)
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
    api_key: str = Depends(verify_api_key)
):
    """
    Register a webhook endpoint to receive real-time notifications.
    
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
async def list_webhooks(api_key: str = Depends(verify_api_key)):
    """List all registered webhooks."""
    return {
        "webhooks": [
            {k: v for k, v in webhook.items() if k != "secret"}
            for webhook in webhooks_db.values()
        ]
    }


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: str, api_key: str = Depends(verify_api_key)):
    """Delete a registered webhook."""
    if webhook_id not in webhooks_db:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    del webhooks_db[webhook_id]
    return {"message": "Webhook deleted successfully"}


@router.post("/api-keys")
async def create_api_key(key_request: APIKeyCreate):
    """
    Create a new API key for integration access.
    
    NOTE: In production, this endpoint should require admin authentication.
    """
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
async def list_api_keys(x_api_key: str = Header(None)):
    """
    List all API keys (excluding the key values).
    
    NOTE: In production, this should require admin authentication.
    """
    return {
        "api_keys": [
            {k: v for k, v in key_data.items() if k != "key"}
            for key_data in api_keys_db.values()
        ]
    }


@router.post("/export")
async def export_diagnosis(
    export_request: DiagnosisExportRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Export diagnosis in multiple formats for integration with external systems.
    
    Supports: FHIR, HL7, JSON, XML, CSV formats.
    """
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
        return await export_to_fhir_condition(fhir_request, api_key)
    
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
            "api_keys": "available"
        },
        "active_webhooks": len(webhooks_db),
        "active_api_keys": len([k for k in api_keys_db.values() if not k.get("revoked")])
    }
