"""
Matching chart medications to the trees' related_medications entries.

backend/data/medication_rxnorm.json (built by
backend/scripts/build_medication_rxnorm.py from NLM RxNav) resolves each
related_medications entry to RxNorm ingredients, with their brand names and
product codes. Class patterns ("*statin", "*olol", ...) are resolved through
ATC classes, so "*olol" covers carvedilol and labetalol and "*statin" does
not match nystatin. A medication is matched:

1. by RxNorm code: any RxNorm coding on the MedicationRequest (product,
   ingredient or brand RxCUI) found in the file; otherwise
2. by name: the medication text/display contains an ingredient or brand
   name as whole words.

An entry RxNorm could not resolve keeps the old name pattern ("*x" = a word
ending in x). Nothing here calls an external service at runtime.
"""
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "medication_rxnorm.json"


def _words(text: str) -> re.Pattern:
    return re.compile(r"(?<![a-z0-9])" + re.escape(text.lower()) + r"(?![a-z0-9])")


def legacy_pattern(entry: str) -> re.Pattern:
    """The original related_medications name pattern ('*x' = a word ending in x)."""
    entry = entry.strip().lower()
    if entry.startswith("*"):
        return re.compile(r"\b[a-z]+" + re.escape(entry[1:]) + r"\b")
    return re.compile(r"\b" + re.escape(entry) + r"\b")


@lru_cache(maxsize=1)
def _index(path: str = str(DATA_PATH)) -> Dict[str, Any]:
    data = json.loads(Path(path).read_text())
    by_code: Dict[str, Set[str]] = {}
    ingredients: Dict[str, Dict[str, Any]] = {}
    for entry, record in (data.get("entries") or {}).items():
        for ing in record.get("ingredients") or []:
            info = ingredients.setdefault(ing["rxcui"], {
                "rxcui": ing["rxcui"], "name": ing["name"], "entries": set(),
                "patterns": [_words(ing["name"])] + [_words(b) for b in ing.get("brands") or []]})
            info["entries"].add(entry)
            for code in [ing["rxcui"], *(ing.get("product_rxcuis") or [])]:
                by_code.setdefault(str(code), set()).add(ing["rxcui"])
    resolved = {e for e, r in (data.get("entries") or {}).items() if r.get("ingredients")}
    return {"by_code": by_code, "ingredients": ingredients, "resolved": resolved,
            "source": data.get("source"), "generated": data.get("generated")}


def medication_name(med: Dict[str, Any]) -> Optional[str]:
    concept = med.get("medicationCodeableConcept") or {}
    return (concept.get("text")
            or next((c.get("display") for c in concept.get("coding") or [] if c.get("display")), None)
            or (med.get("medicationReference") or {}).get("display"))


def _rxnorm_codes(med: Dict[str, Any]) -> List[str]:
    concept = med.get("medicationCodeableConcept") or {}
    return [str(c.get("code")) for c in concept.get("coding") or []
            if "rxnorm" in str(c.get("system", "")).lower() and c.get("code")]


def medication_ingredients(med: Dict[str, Any]) -> List[Dict[str, Any]]:
    """RealDiag-known ingredients of a MedicationRequest: [{rxcui, name, entries, via}]."""
    index = _index()
    found: Dict[str, str] = {}
    for code in _rxnorm_codes(med):
        for rxcui in index["by_code"].get(code, ()):
            found.setdefault(rxcui, f"RxNorm code {code}")
    if not found:
        name = (medication_name(med) or "").lower()
        for rxcui, info in index["ingredients"].items():
            if name and any(p.search(name) for p in info["patterns"]):
                found.setdefault(rxcui, "name")
    return [{"rxcui": rxcui, "name": index["ingredients"][rxcui]["name"],
             "entries": sorted(index["ingredients"][rxcui]["entries"]), "via": via}
            for rxcui, via in sorted(found.items())]


def matches_entry(med: Dict[str, Any], entry: str) -> bool:
    """True when the medication is covered by a related_medications entry."""
    key = entry.strip().lower()
    if key in _index()["resolved"]:
        return any(key in ing["entries"] for ing in medication_ingredients(med))
    name = (medication_name(med) or "").lower()
    return bool(name) and bool(legacy_pattern(key).search(name))


def matching_medications(meds: Iterable[Dict[str, Any]], related: List[str]) -> List[str]:
    """Names of the medications covered by any of the related_medications entries."""
    return [medication_name(m) or "Unnamed medication" for m in meds or []
            if any(matches_entry(m, entry) for entry in related)]


def data_source() -> str:
    index = _index()
    return f"{index['source']} (built {index['generated']})"
