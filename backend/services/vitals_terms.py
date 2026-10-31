"""
Vital-sign helpers shared by symptom search and decision-tree evaluation.

Temperature is converted from its recorded unit before it is compared with
the (unchanged) degrees-Fahrenheit thresholds.
"""
from typing import Any, Optional

from .lab_units import to_canonical

# Units accepted when a temperature carries none: the symptom-search form and
# the manual-history form both label temperature in degrees Fahrenheit.
DEFAULT_TEMPERATURE_UNIT = "F"


def _number(value: Any) -> Optional[float]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def temperature_fahrenheit(value: Any, unit: Optional[str]) -> Optional[float]:
    """Temperature in degrees F, or None when the value or its unit is unusable.

    A missing unit means degrees F (see DEFAULT_TEMPERATURE_UNIT). An
    unrecognised unit is not guessed at: the temperature is skipped.
    """
    number = _number(value)
    if number is None:
        return None
    celsius, _ = to_canonical("temperature", number, unit or DEFAULT_TEMPERATURE_UNIT)
    if celsius is None:
        return None
    return celsius * 9 / 5 + 32
