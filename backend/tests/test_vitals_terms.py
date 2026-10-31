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


# --- One shared mapper (vitals_terms.derive_vital_sign_terms) ---------------------------------

from backend.services.vitals_terms import derive_vital_sign_terms  # noqa: E402


def test_both_callers_use_the_same_rules():
    vitals = dict(heart_rate=135, blood_pressure_systolic=150, blood_pressure_diastolic=95,
                  temperature=38.6, temperature_unit="C", respiratory_rate=24, oxygen_saturation=88)
    shared = derive_vital_sign_terms({
        "heart_rate": 135, "blood_pressure": {"systolic": 150, "diastolic": 95},
        "temperature": 38.6, "temperature_unit": "C", "respiratory_rate": 24, "oxygen_saturation": 88})
    assert _derive_terms_from_history(history(**vitals)) == {"symptoms": shared["symptoms"],
                                                             "red_flags": shared["red_flags"]}
    assert derive_search_terms_from_history(history(**vitals)) == shared["terms"]
    assert shared["symptoms"] == ["tachycardia", "hypertension", "fever", "tachypnea", "hypoxemia"]
    assert shared["red_flags"] == ["severe tachycardia", "severe hypoxemia"]


@pytest.mark.parametrize("vitals, symptoms, red_flags", [
    # Diastolic >= 90 counts as hypertension (symptom search did this; tree evaluation did not).
    ({"blood_pressure": {"systolic": 130, "diastolic": 92}}, ["hypertension"], []),
    ({"blood_pressure": {"diastolic": 92}}, ["hypertension"], []),
    ({"blood_pressure": {"systolic": 85, "diastolic": 95}}, [], ["hypotension"]),
    # Red-flag tiers (tree evaluation had these; symptom search did not).
    ({"heart_rate": 130}, ["tachycardia"], ["severe tachycardia"]),
    ({"heart_rate": 129}, ["tachycardia"], []),
    ({"oxygen_saturation": 89}, ["hypoxemia"], ["severe hypoxemia"]),
    ({"oxygen_saturation": 90}, ["hypoxemia"], []),
    ({"oxygen_saturation": 94}, [], []),
    ({"respiratory_rate": 10}, [], ["bradypnea"]),
    ({"respiratory_rate": 22}, ["tachypnea"], []),
    ({"heart_rate": 50}, ["bradycardia"], []),
    ({}, [], []),
])
def test_shared_rules(vitals, symptoms, red_flags):
    result = derive_vital_sign_terms(vitals)
    assert result["symptoms"] == symptoms
    assert result["red_flags"] == red_flags


def test_symptom_search_terms_include_red_flags_in_rule_order():
    assert _derive_terms_from_vitals({"heart_rate": 140, "blood_pressure": {"systolic": 80},
                                      "oxygen_saturation": 85}) == [
        "tachycardia", "severe tachycardia", "hypotension", "hypoxemia", "severe hypoxemia"]
