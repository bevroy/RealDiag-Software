"""
Write a CSV of remaining content issues, one row per decision tree.

Usage:
    python backend/scripts/tree_report.py [output.csv]
    (default: docs/tree_standardization_report.csv)
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
TREES_DIR = ROOT / "backend" / "trees"
DEFAULT_OUT = ROOT / "docs" / "tree_standardization_report.csv"

# Clinical sections every tree is expected to fill in.
CORE_SECTIONS = [
    "chief_complaint", "description", "presentations", "differentials", "workup",
    "treatment", "clinical_pearls", "red_flags", "referrals", "sources",
]
YEAR = re.compile(r"\b(19|20)\d{2}\b")
CITATION_ORIGINS = {"citations", "references", "trace.source", "metadata.guidelines"}


def standardization_notes(tree: dict) -> str:
    for entry in reversed(tree.get("change_log") or []):
        if isinstance(entry, dict) and entry.get("change") == "Standardized to template":
            return entry.get("notes", "")
    return ""


def row_for(path: Path) -> dict:
    tree = yaml.safe_load(path.read_text(encoding="utf-8"))
    codes = tree.get("codes") or {}
    sources = [s for s in tree.get("sources") or [] if isinstance(s, dict)]
    citations = [s for s in sources if s.get("origin") in CITATION_ORIGINS]
    no_year = [s for s in citations if not YEAR.search(str(s.get("text", "")) + str(s.get("description", "")))]
    uptodate = any("uptodate" in str(s.get("text", "")).lower() for s in sources)

    missing = [f for f in CORE_SECTIONS if not tree.get(f)]
    if not codes.get("icd10"):
        missing.append("codes.icd10")
    if not codes.get("snomed"):
        missing.append("codes.snomed")

    notes = standardization_notes(tree)
    if "treatment_duplicate" in tree:
        duplicate = "yes - merge by hand"
    elif "duplicate treatment key" in notes:
        duplicate = "resolved - empty duplicate removed"
    else:
        duplicate = ""

    mapping = next((n.strip() for n in notes.split(";") if n.strip().startswith("urgency '")), "")

    issues = []
    if not tree.get("urgency"):
        issues.append("missing urgency")
    if not codes.get("icpc2"):
        issues.append("no ICPC-2 code")
    if no_year:
        issues.append("citations without year")
    if uptodate:
        issues.append("cites UpToDate")
    if missing:
        issues.append("missing sections")
    if duplicate.startswith("yes"):
        issues.append("duplicate treatment")
    if tree.get("tree_id") != path.stem:
        issues.append("tree_id differs from file name")

    return {
        "file": path.name,
        "tree_id": tree.get("tree_id", ""),
        "issues_remaining": "; ".join(issues),
        "missing_urgency": "yes" if not tree.get("urgency") else "",
        "no_icpc2_code": "yes" if not codes.get("icpc2") else "",
        "citations_without_year": len(no_year),
        "cites_uptodate": "yes" if uptodate else "",
        "missing_sections": "; ".join(missing),
        "duplicate_treatment": duplicate,
        "urgency": tree.get("urgency", ""),
        "urgency_mapping": mapping,
        "status": tree.get("status", ""),
    }


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    rows = [row_for(p) for p in sorted(TREES_DIR.glob("*.yml"))]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
