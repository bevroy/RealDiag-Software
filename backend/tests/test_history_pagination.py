"""PatientHistoryService follows FHIR `next` links up to HISTORY_MAX_PAGES and reports
searches the cap cut off, the same way FHIRClient does."""
import asyncio

import httpx
import pytest

from backend.services import patient_history_service as phs
from backend.services.patient_history_service import PatientHistoryService

BASE = "https://fhir.example.test/R4"
EMPTY = {"resourceType": "Bundle", "entry": []}


def immunization(i):
    return {"resource": {"resourceType": "Immunization", "status": "completed",
                         "vaccineCode": {"text": f"Vaccine {i}"}, "occurrenceDateTime": f"2026-0{1 + i % 9}-15"}}


def paged_server(pages, fail_page=None):
    """Immunization search split over `pages` pages of 2 entries; other searches empty."""
    def handler(request):
        path = request.url.path
        if "/Patient/" in path:
            return httpx.Response(200, json={"name": [{"family": "X"}], "birthDate": "1970-01-01"})
        if path.endswith("/Immunization"):
            page = int(request.url.params.get("page", "1"))
            if fail_page and page == fail_page:
                return httpx.Response(500, json={})
            bundle = {"resourceType": "Bundle", "entry": [immunization(2 * page), immunization(2 * page + 1)]}
            if page < pages:
                bundle["link"] = [{"relation": "next", "url": f"{BASE}/Immunization?patient=p1&page={page + 1}"}]
            return httpx.Response(200, json=bundle)
        return httpx.Response(200, json=EMPTY)

    service = PatientHistoryService(BASE, auth_token="t")
    service.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return service


def history(service):
    return asyncio.run(service.get_comprehensive_history("p1"))


def test_all_pages_are_read_within_the_cap(monkeypatch):
    monkeypatch.setattr(phs, "HISTORY_MAX_PAGES", 5)
    h = history(paged_server(pages=3))
    assert len(h.immunizations) == 6
    assert h.retrieval_status["immunizations"] == "retrieved"
    assert not [w for w in h.data_warnings if "cut off" in w]


def test_cap_reached_is_reported_as_cut_off(monkeypatch):
    monkeypatch.setattr(phs, "HISTORY_MAX_PAGES", 2)
    h = history(paged_server(pages=4))
    assert len(h.immunizations) == 4
    warning = next(w for w in h.data_warnings if "cut off" in w)
    assert warning.startswith("Immunizations cut off: the page limit was reached after 4 results")
    assert "were not retrieved and were not assessed" in warning


def test_a_failed_later_page_marks_the_data_type_failed(monkeypatch):
    monkeypatch.setattr(phs, "HISTORY_MAX_PAGES", 5)
    h = history(paged_server(pages=4, fail_page=2))
    assert h.retrieval_status["immunizations"] == "failed"
    assert "Immunizations could not be retrieved; do not assume none." in h.data_warnings


def test_default_cap_is_configurable():
    assert phs.HISTORY_MAX_PAGES == 5
