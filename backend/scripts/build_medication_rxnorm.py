#!/usr/bin/env python3
"""
Build backend/data/medication_rxnorm.json from the trees' related_medications.

Each related_medications entry (a name such as "metformin", or a class
pattern such as "*statin") is resolved once, here, against NLM RxNav
(https://rxnav.nlm.nih.gov/REST) into RxNorm ingredients with their brand
names and product codes. At runtime RealDiag matches medications against
this file only; no medication or chart data is sent anywhere.

Class patterns are resolved through ATC classes instead of name suffixes
(CLASS_ENTRIES), so "*olol" includes carvedilol and labetalol and "*statin"
excludes nystatin. Which ATC class stands for each pattern is a clinical
mapping choice, pending clinical review.

Usage:  python backend/scripts/build_medication_rxnorm.py
Re-run after related_medications change in any tree; commit the JSON.
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
TREES = ROOT / "backend" / "trees"
OUT = ROOT / "backend" / "data" / "medication_rxnorm.json"
RXNAV = "https://rxnav.nlm.nih.gov/REST"

# related_medications class patterns -> ATC class (pending clinical review)
CLASS_ENTRIES = {
    "*pril": ("C09AA", "ACE inhibitors, plain"),
    "*sartan": ("C09CA", "Angiotensin II receptor blockers (ARBs), plain"),
    "*olol": ("C07A", "Beta blocking agents"),
    "*statin": ("C10AA", "HMG CoA reductase inhibitors"),
    "insulin": ("A10A", "Insulins and analogues"),
}
PRODUCT_TTYS = ("SCD", "SBD", "GPCK", "BPCK")


def get(path: str, **params) -> dict:
    url = f"{RXNAV}/{path}" + (("?" + urllib.parse.urlencode(params)) if params else "")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                time.sleep(0.06)  # stay well under RxNav's 20 requests/second
                return json.load(response)
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1 + attempt)
    return {}


def ingredient_details(rxcui: str, name: str) -> dict:
    related = get(f"rxcui/{rxcui}/related.json", tty=" ".join(("BN",) + PRODUCT_TTYS))
    brands, products = set(), set()
    for group in (related.get("relatedGroup") or {}).get("conceptGroup") or []:
        for concept in group.get("conceptProperties") or []:
            if group.get("tty") == "BN":
                brands.add(concept["name"].lower())
            else:
                products.add(concept["rxcui"])
    return {"rxcui": rxcui, "name": name.lower(), "brands": sorted(brands), "product_rxcuis": sorted(products)}


def resolve_name(name: str) -> list:
    """Ingredient(s) for a medication name; a brand name resolves to its ingredient(s)."""
    ids = ((get("rxcui.json", name=name, search=2).get("idGroup") or {}).get("rxnormId")) or []
    ingredients = {}
    for rxcui in ids:
        props = (get(f"rxcui/{rxcui}/properties.json").get("properties") or {})
        if props.get("tty") in ("IN", "PIN", "MIN"):
            ingredients[rxcui] = props["name"]
        else:
            related = get(f"rxcui/{rxcui}/related.json", tty="IN")
            for group in (related.get("relatedGroup") or {}).get("conceptGroup") or []:
                for concept in group.get("conceptProperties") or []:
                    ingredients[concept["rxcui"]] = concept["name"]
    return [ingredient_details(rxcui, n) for rxcui, n in sorted(ingredients.items())]


def resolve_class(class_id: str) -> list:
    members = get("rxclass/classMembers.json", classId=class_id, relaSource="ATC")
    found = {m["minConcept"]["rxcui"]: m["minConcept"]["name"]
             for m in (members.get("drugMemberGroup") or {}).get("drugMember") or []}
    return [ingredient_details(rxcui, n) for rxcui, n in sorted(found.items())]


def related_medication_entries() -> dict:
    entries = {}
    for path in sorted(TREES.glob("*.yml")):
        tree = yaml.safe_load(path.read_text()) or {}
        criteria = tree.get("criteria")
        if isinstance(criteria, dict):
            for entry in criteria.get("related_medications") or []:
                entries.setdefault(entry.strip().lower(), []).append(tree["tree_id"])
    return entries


def main() -> int:
    entries = related_medication_entries()
    out = {"source": f"NLM RxNav REST API ({RXNAV}), RxNorm version "
                     f"{get('version.json').get('version', 'unknown')}",
           "generated": date.today().isoformat(),
           "note": "Built by backend/scripts/build_medication_rxnorm.py from the trees' related_medications; "
                   "class patterns resolved through ATC classes (pending clinical review).",
           "entries": {}, "unresolved": []}
    for entry, trees in sorted(entries.items()):
        if entry in CLASS_ENTRIES:
            class_id, class_name = CLASS_ENTRIES[entry]
            ingredients = resolve_class(class_id)
            record = {"trees": sorted(trees), "atc_class": class_id, "atc_class_name": class_name}
        else:
            ingredients = resolve_name(entry.lstrip("*"))
            record = {"trees": sorted(trees)}
        if not ingredients:
            out["unresolved"].append(entry)
        record["ingredients"] = ingredients
        out["entries"][entry] = record
        print(f"{entry}: {len(ingredients)} ingredient(s)", file=sys.stderr)
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(out['entries'])} entries, unresolved: {out['unresolved']}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
