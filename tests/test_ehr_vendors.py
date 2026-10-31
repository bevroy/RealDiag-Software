"""Only vendors with a configuration are offered; any other gives a clear error, not a KeyError."""
import pytest
from fastapi import HTTPException

from backend.services import smart_router
from backend.services.ehr_adapter import EHRAdapter, EHRVendor, UnsupportedEHRVendorError, supported_vendors


def test_every_vendor_in_the_enum_has_a_configuration():
    assert set(EHRVendor) == set(EHRAdapter.VENDOR_CONFIGS)
    assert supported_vendors() == ["epic", "cerner", "allscripts", "athenahealth"]


@pytest.mark.parametrize("vendor", ["meditech", "MEDITECH", "nextgen", "", None])
def test_unsupported_vendor_is_a_clear_error(vendor):
    with pytest.raises(UnsupportedEHRVendorError) as exc:
        EHRAdapter.get_config(vendor=vendor, fhir_base_url="https://fhir.example", client_id="c")
    assert "is not supported. Supported vendors: epic, cerner, allscripts, athenahealth." in str(exc.value)


def test_router_returns_503_with_the_reason(monkeypatch):
    monkeypatch.setattr(smart_router, "EHR_VENDOR", "meditech")
    with pytest.raises(HTTPException) as exc:
        smart_router.get_ehr_config()
    assert exc.value.status_code == 503
    assert "SMART on FHIR is not available: EHR vendor 'meditech' is not supported" in exc.value.detail


def test_supported_vendor_still_configures():
    config = EHRAdapter.get_config(vendor=" Epic ", fhir_base_url="https://fhir.example", client_id="c")
    assert config.vendor is EHRVendor.EPIC


# --- Scopes ---------------------------------------------------------------------------

import re  # noqa: E402
from pathlib import Path  # noqa: E402

SERVICES = Path(__file__).resolve().parents[1] / "backend" / "services"


def _queried_resources():
    """FHIR resource types the chart pull queries, read from the source."""
    found = set()
    for name in ("fhir_client.py", "patient_history_service.py"):
        src = (SERVICES / name).read_text()
        found |= set(re.findall(r'\{self\.fhir_base_url\}/([A-Z][A-Za-z]+)[?/]', src))
        found |= set(re.findall(r'_query_resource\("([A-Z][A-Za-z]+)"', src))
    from backend.services.fhir_client import FHIRResourceType
    src = (SERVICES / "fhir_client.py").read_text()
    found |= {FHIRResourceType[m].value for m in re.findall(r"FHIRResourceType\.([A-Z_]+)\.value", src)}
    return found


def test_cerner_requests_a_read_scope_for_every_queried_resource():
    resources = _queried_resources()
    assert {"ImagingStudy", "FamilyMemberHistory", "Patient", "Observation"} <= resources
    scopes = set(EHRAdapter.scopes_for("cerner"))
    missing = sorted(r for r in resources if f"patient/{r}.read" not in scopes)
    assert missing == []


def test_smart_config_reports_the_active_vendors_scopes(monkeypatch):
    import asyncio
    for vendor in ("epic", "cerner"):
        monkeypatch.setattr(smart_router, "EHR_VENDOR", vendor)
        config = asyncio.run(smart_router.get_smart_config())
        assert config["ehr_vendor"] == vendor
        assert config["scopes"] == EHRAdapter.scopes_for(vendor)
    monkeypatch.setattr(smart_router, "EHR_VENDOR", "meditech")
    with pytest.raises(HTTPException) as exc:
        asyncio.run(smart_router.get_smart_config())
    assert exc.value.status_code == 503
