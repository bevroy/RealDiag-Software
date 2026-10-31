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
