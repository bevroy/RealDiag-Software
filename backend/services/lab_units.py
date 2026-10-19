"""
Unit handling for criteria evaluation, keyed by LOINC code.

Each analyte has a canonical unit and the units it can be converted from.
A result whose unit is missing or not listed is never compared against a
threshold: the criterion is "unknown" and the reason says why.
"""

from __future__ import annotations

import re
from typing import Callable, Dict, Optional, Tuple, Union

Factor = Union[float, Callable[[float], float]]


def _normalize(unit: Optional[str]) -> str:
    """Lower-case, drop spaces, braces and underscores: 'mL/min/{1.73_m2}' -> 'ml/min/1.73m2'."""
    if not unit:
        return ""
    unit = unit.strip().lower().replace("µ", "u").replace("μ", "u")
    return re.sub(r"[\s{}_]", "", unit)


# analyte -> (canonical unit, {normalized unit: factor or function to canonical}, hint for messages)
ANALYTES: Dict[str, Tuple[str, Dict[str, Factor], str]] = {
    "troponin": ("ng/L", {"ng/l": 1.0, "pg/ml": 1.0, "ng/ml": 1000.0, "ug/l": 1000.0, "mcg/l": 1000.0},
                 "ng/mL or ng/L"),
    "glucose": ("mg/dL", {"mg/dl": 1.0, "mmol/l": 18.016}, "mg/dL or mmol/L"),
    # NGSP % from IFCC mmol/mol: NGSP = 0.09148 * IFCC + 2.152
    "hba1c": ("%", {"%": 1.0, "percent": 1.0, "mmol/mol": lambda v: 0.09148 * v + 2.152}, "% or mmol/mol"),
    "egfr": ("mL/min/1.73m2", {"ml/min/1.73m2": 1.0, "ml/min/1.73m^2": 1.0, "ml/min": 1.0}, "mL/min/1.73m2"),
    "uacr": ("mg/g", {"mg/g": 1.0, "ug/mg": 1.0, "mg/gcreat": 1.0, "mg/mmol": 8.84}, "mg/g or mg/mmol"),
    "hemoglobin": ("g/dL", {"g/dl": 1.0, "g/l": 0.1, "mmol/l": 1.611}, "g/dL, g/L or mmol/L"),
    "tsh": ("mIU/L", {"miu/l": 1.0, "uiu/ml": 1.0, "mu/l": 1.0, "uu/ml": 1.0, "miu/ml": 1000.0}, "mIU/L or uIU/mL"),
    "free_t4": ("ng/dL", {"ng/dl": 1.0, "pmol/l": 1 / 12.87}, "ng/dL or pmol/L"),
    "potassium": ("mmol/L", {"mmol/l": 1.0, "meq/l": 1.0}, "mmol/L or mEq/L"),
    "ldl": ("mg/dL", {"mg/dl": 1.0, "mmol/l": 38.67}, "mg/dL or mmol/L"),
    "blood_pressure": ("mmHg", {"mmhg": 1.0, "mm[hg]": 1.0}, "mmHg"),
}

ANALYTE_BY_LOINC: Dict[str, str] = {
    "10839-9": "troponin", "6598-7": "troponin", "89579-7": "troponin", "67151-1": "troponin",
    "2345-7": "glucose", "1558-6": "glucose", "14771-0": "glucose",
    "4548-4": "hba1c", "17856-6": "hba1c", "59261-8": "hba1c",
    "33914-3": "egfr", "62238-1": "egfr", "98979-8": "egfr", "48642-3": "egfr", "48643-1": "egfr",
    "9318-7": "uacr", "14959-1": "uacr",
    "718-7": "hemoglobin",
    "3016-3": "tsh", "11580-8": "tsh",
    "3024-7": "free_t4", "14920-3": "free_t4",
    "2823-3": "potassium", "6298-4": "potassium",
    "13457-7": "ldl", "18262-6": "ldl", "2089-1": "ldl",
    "8480-6": "blood_pressure", "8462-4": "blood_pressure",
}


# Prose names used in messages ("troponin result has no unit", "TSH 3.2x ...")
ANALYTE_NAMES: Dict[str, str] = {
    "troponin": "troponin", "glucose": "glucose", "hba1c": "HbA1c", "egfr": "eGFR",
    "uacr": "urine albumin-creatinine ratio", "hemoglobin": "hemoglobin", "tsh": "TSH",
    "free_t4": "free T4", "potassium": "potassium", "ldl": "LDL cholesterol",
    "blood_pressure": "blood pressure",
}


def analyte_name(analyte: str) -> str:
    return ANALYTE_NAMES.get(analyte, analyte.replace("_", " "))


def analyte_title(analyte: str) -> str:
    """Name for the start of a sentence: 'Troponin', 'HbA1c', 'TSH'."""
    name = analyte_name(analyte)
    return name[0].upper() + name[1:]


def analyte_for(loinc: str) -> Optional[str]:
    return ANALYTE_BY_LOINC.get(loinc)


def unit_hint(analyte: str) -> str:
    return ANALYTES[analyte][2]


def canonical_unit(analyte: str) -> str:
    return ANALYTES[analyte][0]


def is_known_unit(analyte: str, unit: Optional[str]) -> bool:
    return analyte in ANALYTES and _normalize(unit) in ANALYTES[analyte][1]


def to_canonical(analyte: str, value: float, unit: Optional[str]) -> Tuple[Optional[float], Optional[str]]:
    """Convert to the analyte's canonical unit.

    Returns (value, None), or (None, reason) when the unit is missing or not
    recognised. The reason has no trailing period, e.g.
    "glucose unit 'g/L' is not recognised (expected mg/dL or mmol/L)".
    """
    name = analyte_name(analyte)
    if not unit or not unit.strip():
        return None, f"{name} result has no unit"
    factors = ANALYTES[analyte][1]
    factor = factors.get(_normalize(unit))
    if factor is None:
        return None, f"{name} unit '{unit}' is not recognised (expected {unit_hint(analyte)})"
    return (factor(value) if callable(factor) else value * factor), None
