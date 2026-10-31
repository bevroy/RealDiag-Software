"""
Vital signs -> search terms: temperature is converted from its recorded unit
before it is compared with the degrees-Fahrenheit thresholds.
"""
import pytest

from backend.services.diagnostic_router import _derive_terms_from_history
from backend.services.patient_history_service import ComprehensivePatientHistory, VitalSigns
from backend.services.symptom_search import _derive_terms_from_vitals, derive_search_terms_from_history
from backend.services.vitals_terms import temperature_fahrenheit


def history(**vitals):
    return ComprehensivePatientHistory(patient_id="p1", patient_name="Test",
                                       vital_signs=[VitalSigns(date="2026-10-30", **vitals)])


@pytest.mark.parametrize("value, unit, expected", [
    (98.6, "F", 98.6),
    (98.6, "[degF]", 98.6),
    (98.6, None, 98.6),          # no unit: degrees F, as the forms label it
    (37.0, "C", 98.6),
    (37.0, "Cel", 98.6),
    (38.0, "°C", 100.4),
])
def test_temperature_fahrenheit_converts_recorded_unit(value, unit, expected):
    assert temperature_fahrenheit(value, unit) == pytest.approx(expected)


@pytest.mark.parametrize("value, unit", [(37.0, "K"), (None, "C"), ("37", "C"), (True, "F")])
def test_temperature_fahrenheit_skips_unusable_values(value, unit):
    assert temperature_fahrenheit(value, unit) is None


def test_normal_celsius_temperature_is_not_hypothermia():
    # Before the fix, 37 (°C) was compared as °F and read as hypothermia.
    assert _derive_terms_from_vitals({"temperature": 37.0, "temperature_unit": "C"}) == []
    terms = _derive_terms_from_history(history(temperature=37.0, temperature_unit="C"))
    assert terms == {"symptoms": [], "red_flags": []}
    assert derive_search_terms_from_history(history(temperature=37.0, temperature_unit="C")) == []


def test_celsius_fever_and_hypothermia():
    assert _derive_terms_from_vitals({"temperature": 38.5, "temperature_unit": "C"}) == ["fever"]
    assert _derive_terms_from_vitals({"temperature": 34.0, "temperature_unit": "C"}) == ["hypothermia"]
    assert _derive_terms_from_history(history(temperature=38.5, temperature_unit="C"))["symptoms"] == ["fever"]
    assert _derive_terms_from_history(history(temperature=34.0, temperature_unit="C"))["red_flags"] == ["hypothermia"]


def test_fahrenheit_unchanged():
    assert _derive_terms_from_vitals({"temperature": 101.0}) == ["fever"]
    assert _derive_terms_from_vitals({"temperature": 94.0, "temperature_unit": "F"}) == ["hypothermia"]
    assert _derive_terms_from_history(history(temperature=101.0, temperature_unit="F"))["symptoms"] == ["fever"]


def test_unrecognised_temperature_unit_is_skipped():
    assert _derive_terms_from_vitals({"temperature": 310.0, "temperature_unit": "K"}) == []
