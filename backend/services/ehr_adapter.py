"""
Multi-EHR Adapter for FHIR Integration

Provides vendor-specific configurations and adaptations for Epic, Cerner, and other EHR systems.
The core FHIRClient works with all FHIR R4-compliant systems, but this adapter handles
vendor-specific quirks, OAuth endpoints, and configuration differences.

Usage:
    # Automatically detect EHR vendor and configure
    config = EHRAdapter.get_config("epic")
    client = FHIRClient(
        fhir_base_url=config.fhir_base_url,
        client_id=config.client_id,
        client_secret=config.client_secret
    )
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class EHRVendor(Enum):
    """Supported EHR vendors."""
    EPIC = "epic"
    CERNER = "cerner"
    ALLSCRIPTS = "allscripts"
    ATHENAHEALTH = "athenahealth"
    MEDITECH = "meditech"


@dataclass
class EHRConfig:
    """EHR vendor-specific configuration."""
    vendor: EHRVendor
    name: str
    fhir_base_url: str
    token_url: str
    authorize_url: str
    client_id: str
    client_secret: Optional[str] = None
    scopes: list[str] = None
    
    # Vendor-specific quirks
    requires_tenant_id: bool = False
    supports_smart_launch: bool = True
    supports_cds_hooks: bool = True
    patient_id_system: Optional[str] = None
    
    # FHIR implementation details
    fhir_version: str = "R4"
    supports_batch_requests: bool = True
    max_page_size: int = 100
    
    # Lab/observation quirks
    uses_component_observations: bool = False  # Some systems nest values in components
    requires_category_filter: bool = False  # Some require explicit category filtering


class EHRAdapter:
    """
    Adapter for vendor-specific EHR configurations and behaviors.
    
    Handles differences in:
    - OAuth endpoints and flows
    - FHIR resource structure variations
    - Vendor-specific extensions
    - Search parameter requirements
    """
    
    # Pre-configured vendor settings
    VENDOR_CONFIGS = {
        EHRVendor.EPIC: {
            "name": "Epic",
            "token_url": "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token",
            "authorize_url": "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/authorize",
            "scopes": ["launch", "patient/*.read", "openid", "fhirUser"],
            "supports_smart_launch": True,
            "supports_cds_hooks": True,
            "patient_id_system": "urn:oid:1.2.840.114350.1.13.0.1.7.5.737384.0",
            "uses_component_observations": False,
            "requires_category_filter": False,
        },
        EHRVendor.CERNER: {
            "name": "Cerner/Oracle Health",
            "token_url": "https://authorization.cerner.com/tenants/{tenant_id}/protocols/oauth2/profiles/smart-v1/token",
            "authorize_url": "https://authorization.cerner.com/tenants/{tenant_id}/protocols/oauth2/profiles/smart-v1/personas/provider/authorize",
            "scopes": ["launch", "patient/Patient.read", "patient/Observation.read", "patient/Condition.read", "patient/MedicationRequest.read", "patient/AllergyIntolerance.read", "patient/Encounter.read", "patient/Immunization.read", "patient/Procedure.read", "patient/DocumentReference.read", "patient/DiagnosticReport.read", "openid", "fhirUser"],            "requires_tenant_id": True,
            "supports_smart_launch": True,
            "supports_cds_hooks": True,
            "patient_id_system": None,  # Varies by tenant
            "uses_component_observations": True,  # Cerner often uses components for BP, etc.
            "requires_category_filter": True,  # Cerner requires explicit category in searches
        },
        EHRVendor.ALLSCRIPTS: {
            "name": "Allscripts",
            "token_url": "https://cloud.allscripts.com/fhir/token",
            "authorize_url": "https://cloud.allscripts.com/fhir/authorize",
            "scopes": ["launch", "patient/*.read", "openid"],
            "supports_smart_launch": True,
            "supports_cds_hooks": False,
            "uses_component_observations": False,
            "requires_category_filter": False,
        },
        EHRVendor.ATHENAHEALTH: {
            "name": "athenahealth",
            "token_url": "https://api.platform.athenahealth.com/oauth2/v1/token",
            "authorize_url": "https://api.platform.athenahealth.com/oauth2/v1/authorize",
            "scopes": ["launch", "patient/*.read", "openid"],
            "supports_smart_launch": True,
            "supports_cds_hooks": False,
            "uses_component_observations": False,
            "requires_category_filter": False,
        },
    }
    
    @classmethod
    def get_config(
        cls,
        vendor: str,
        fhir_base_url: str,
        client_id: str,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> EHRConfig:
        """
        Get vendor-specific configuration.
        
        Args:
            vendor: EHR vendor name (epic, cerner, allscripts, athenahealth)
            fhir_base_url: FHIR base URL for this instance
            client_id: OAuth client ID
            client_secret: OAuth client secret
            tenant_id: Tenant ID (required for Cerner)
            
        Returns:
            EHRConfig with vendor-specific settings
            
        Example:
            # Epic
            config = EHRAdapter.get_config(
                vendor="epic",
                fhir_base_url="https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
                client_id="abc123",
                client_secret="secret"
            )
            
            # Cerner
            config = EHRAdapter.get_config(
                vendor="cerner",
                fhir_base_url="https://fhir-myrecord.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d",
                client_id="xyz789",
                client_secret="secret",
                tenant_id="ec2458f2-1e24-41c8-b71b-0e701af7583d"
            )
        """
        vendor_enum = EHRVendor(vendor.lower())
        vendor_settings = cls.VENDOR_CONFIGS[vendor_enum]
        
        # Handle tenant ID for Cerner
        token_url = vendor_settings["token_url"]
        authorize_url = vendor_settings["authorize_url"]
        
        if vendor_settings.get("requires_tenant_id") and tenant_id:
            token_url = token_url.format(tenant_id=tenant_id)
            authorize_url = authorize_url.format(tenant_id=tenant_id)
        elif vendor_settings.get("requires_tenant_id") and not tenant_id:
            raise ValueError(f"{vendor_settings['name']} requires tenant_id parameter")
        
        return EHRConfig(
            vendor=vendor_enum,
            name=vendor_settings["name"],
            fhir_base_url=fhir_base_url,
            token_url=token_url,
            authorize_url=authorize_url,
            client_id=client_id,
            client_secret=client_secret,
            scopes=vendor_settings["scopes"],
            requires_tenant_id=vendor_settings.get("requires_tenant_id", False),
            supports_smart_launch=vendor_settings.get("supports_smart_launch", True),
            supports_cds_hooks=vendor_settings.get("supports_cds_hooks", False),
            patient_id_system=vendor_settings.get("patient_id_system"),
            uses_component_observations=vendor_settings.get("uses_component_observations", False),
            requires_category_filter=vendor_settings.get("requires_category_filter", False),
        )
    
    @classmethod
    def parse_observation(
        cls,
        observation: Dict[str, Any],
        vendor: EHRVendor
    ) -> Optional[Dict[str, Any]]:
        """
        Parse observation with vendor-specific logic.
        
        Handles differences in how vendors structure observations:
        - Epic: Direct valueQuantity
        - Cerner: Often uses component for multi-part results (BP, etc.)
        
        Args:
            observation: FHIR Observation resource
            vendor: EHR vendor
            
        Returns:
            Parsed observation data or None if can't parse
        """
        vendor_config = cls.VENDOR_CONFIGS[vendor]
        
        # Standard parsing (works for Epic, Allscripts, athenahealth)
        if not vendor_config.get("uses_component_observations"):
            return cls._parse_standard_observation(observation)
        
        # Cerner-specific parsing (handle components)
        if vendor == EHRVendor.CERNER:
            return cls._parse_cerner_observation(observation)
        
        return cls._parse_standard_observation(observation)
    
    @staticmethod
    def _parse_standard_observation(observation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse standard FHIR observation (Epic, Allscripts, athenahealth)."""
        # Get value
        value_quantity = observation.get("valueQuantity")
        if not value_quantity:
            return None
        
        return {
            "value": value_quantity.get("value"),
            "unit": value_quantity.get("unit"),
            "code": observation.get("code", {}).get("coding", [{}])[0].get("code"),
            "display": observation.get("code", {}).get("text"),
            "effective_date": observation.get("effectiveDateTime"),
        }
    
    @staticmethod
    def _parse_cerner_observation(observation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse Cerner observation (may have components for BP, etc.).
        
        Cerner often structures blood pressure as:
        - Observation with components:
          - component[0]: Systolic BP
          - component[1]: Diastolic BP
        """
        # Try standard parsing first
        if "valueQuantity" in observation:
            return EHRAdapter._parse_standard_observation(observation)
        
        # Check for components (common for vital signs in Cerner)
        components = observation.get("component", [])
        if components:
            # Return first component (or could return all)
            component = components[0]
            value_quantity = component.get("valueQuantity")
            if value_quantity:
                return {
                    "value": value_quantity.get("value"),
                    "unit": value_quantity.get("unit"),
                    "code": component.get("code", {}).get("coding", [{}])[0].get("code"),
                    "display": component.get("code", {}).get("text"),
                    "effective_date": observation.get("effectiveDateTime"),
                    "component_type": "multiple",  # Flag that this has components
                }
        
        return None
    
    @classmethod
    def build_observation_query(
        cls,
        patient_id: str,
        vendor: EHRVendor,
        category: Optional[str] = None,
        code: Optional[str] = None,
        date_from: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Build vendor-specific observation query parameters.
        
        Args:
            patient_id: Patient ID
            vendor: EHR vendor
            category: Observation category (laboratory, vital-signs)
            code: LOINC code
            date_from: Start date (YYYY-MM-DD)
            
        Returns:
            Query parameters dict
        """
        params = {"patient": patient_id}
        
        vendor_config = cls.VENDOR_CONFIGS[vendor]
        
        # Cerner requires explicit category in searches
        if vendor_config.get("requires_category_filter") and category:
            params["category"] = category
        elif category:
            params["category"] = category
        
        if code:
            params["code"] = code
        
        if date_from:
            params["date"] = f"ge{date_from}"
        
        # Cerner-specific: Add _count for pagination
        if vendor == EHRVendor.CERNER:
            params["_count"] = "100"
        
        return params


# Environment variable mapping for easy configuration
ENV_VAR_MAPPING = {
    "epic": {
        "fhir_base_url": "EPIC_FHIR_BASE_URL",
        "client_id": "EPIC_CLIENT_ID",
        "client_secret": "EPIC_CLIENT_SECRET",
    },
    "cerner": {
        "fhir_base_url": "CERNER_FHIR_BASE_URL",
        "client_id": "CERNER_CLIENT_ID",
        "client_secret": "CERNER_CLIENT_SECRET",
        "tenant_id": "CERNER_TENANT_ID",
    },
    "allscripts": {
        "fhir_base_url": "ALLSCRIPTS_FHIR_BASE_URL",
        "client_id": "ALLSCRIPTS_CLIENT_ID",
        "client_secret": "ALLSCRIPTS_CLIENT_SECRET",
    },
    "athenahealth": {
        "fhir_base_url": "ATHENAHEALTH_FHIR_BASE_URL",
        "client_id": "ATHENAHEALTH_CLIENT_ID",
        "client_secret": "ATHENAHEALTH_CLIENT_SECRET",
    },
}
