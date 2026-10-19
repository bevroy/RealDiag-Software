"""
One-off migration: convert backend/trees/*.yml to the standard tree template.

Clinical wording is never altered. Fields are renamed, moved, or wrapped in
lists; anything the template does not name is kept as-is. See
backend/services/tree_schema.py for the template definition.

Usage:
    python backend/scripts/standardize_trees.py            # rewrite trees in place
    python backend/scripts/standardize_trees.py --dry-run  # report only
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections import Counter
from pathlib import Path

import yaml
from yaml.constructor import SafeConstructor

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.tree_schema import (  # noqa: E402
    HOMEOPATHY_VALIDATION_STATEMENT,
    TEMPLATE_FIELDS,
)

TREES_DIR = Path(__file__).resolve().parents[1] / "trees"
TODAY = dt.date.today().isoformat()

# Explicit urgency mapping (case-insensitive, exact match).
URGENCY_MAP = {
    "emergent": "emergent", "emergency": "emergent", "critical": "emergent",
    "urgent": "urgent", "high": "urgent", "routine-to-urgent": "urgent",
    "routine-to-emergency": "urgent",
    "routine": "routine", "non-urgent": "routine", "low": "routine",
    "medium": "routine", "moderate": "routine", "variable": "routine",
}
# Used only for wording that names more than one level: take the highest.
LEVEL_WORDS = [
    ("emergent", r"\bemergen|\bcritical\b"),
    ("urgent", r"(?<!non-)\burgent\b|\bhigh\b"),
    ("routine", r"\broutine\b|\bnon-urgent\b|\blow\b|\bmedium\b|\bmoderate\b|\bvariable\b"),
]

# Specialty strings that contain "/" but name a single specialty.
COMPOUND_SPECIALTIES = ["Allergy/Immunology", "OB/GYN", "Hematology / Oncology"]

EMPTY_DICT_FIELDS = {"applies_to", "codes", "disposition_guidance", "special_populations", "homeopathy"}


# --------------------------------------------------------------------------- loading

class DupKeyLoader(yaml.SafeLoader):
    """SafeLoader that records duplicate top-level keys instead of silently dropping them."""


def load_with_duplicates(text: str):
    node = yaml.compose(text, Loader=DupKeyLoader)
    loader = DupKeyLoader("")
    data, dups = {}, {}
    for k_node, v_node in node.value:
        key = loader.construct_object(k_node, deep=True)
        val = loader.construct_object(v_node, deep=True)
        if key in data:
            dups.setdefault(key, [data[key]]).append(val)
        data[key] = val  # last wins, same as yaml.safe_load
    return data, dups


def fix_colon_artifacts(value, counter: Counter, where: str):
    """Restore list items that YAML mis-parsed as one-key mappings because the
    unquoted text contained ': '. {'A': 'b'} inside a list of text becomes 'A: b'
    — exactly the original line. Used for citations only (every citation is
    text); other sections already display such items as 'key: value'."""
    if not isinstance(value, list):
        return value
    out = []
    for item in value:
        if (isinstance(item, dict) and len(item) == 1
                and not isinstance(next(iter(item.values())), (dict, list))):
            k, v = next(iter(item.items()))
            out.append(f"{k}: {v}")
            counter[where] += 1
        else:
            out.append(item)
    return out


# --------------------------------------------------------------------------- helpers

def as_list(value):
    if value is None or value == "" or value == []:
        return []
    return list(value) if isinstance(value, list) else [value]


def split_codes(value):
    out = []
    for v in as_list(value):
        if isinstance(v, str):
            out.extend(p.strip() for p in re.split(r"[,;]", v) if p.strip())
        else:
            out.append(str(v))
    return out


def split_specialties(spec: str):
    placeholders = {}
    s = spec
    for i, comp in enumerate(COMPOUND_SPECIALTIES):
        if comp in s:
            token = f"\x00{i}\x00"
            placeholders[token] = comp
            s = s.replace(comp, token)
    parts = [p.strip() for p in re.split(r"[,/;]", s) if p.strip()]
    for token, comp in placeholders.items():
        parts = [p.replace(token, comp) for p in parts]
    return parts


def map_urgency(raw):
    """Return (urgency, explanation_addition, mapping_note, category)."""
    if raw is None or raw == "" or raw == []:
        return "", None, None, "missing"
    if isinstance(raw, list):
        return "", None, None, "red_flag_list"
    text = str(raw).strip()
    key = text.lower()
    if key in URGENCY_MAP:
        mapped = URGENCY_MAP[key]
        note = None if mapped == text else f"urgency '{text}' mapped to '{mapped}'"
        return mapped, None, note, "mapped"
    found = [lvl for lvl, pat in LEVEL_WORDS if re.search(pat, key)]
    if found:
        mapped = found[0]  # LEVEL_WORDS is ordered highest first
        return (mapped, f"Original urgency value: {text}",
                f"urgency '{text}' mapped to '{mapped}' (highest level named)", "highest")
    return ("routine", f"Original urgency value: {text}",
            f"urgency '{text}' mapped to 'routine' (non-standard wording)", "other")


def source_entries(data: dict, artifacts: Counter):
    sources = []
    for c in fix_colon_artifacts(as_list(data.get("citations")), artifacts, "citations"):
        sources.append({"text": c, "origin": "citations"} if isinstance(c, str)
                       else {"text": json.dumps(c, ensure_ascii=False), "origin": "citations"})
    trace = data.get("trace")
    if isinstance(trace, dict) and trace.get("source"):
        sources.append({"text": trace["source"], "origin": "trace.source"})
    for r in as_list(data.get("references")):
        sources.append({"text": r, "origin": "references"})
    if data.get("evidence_level"):
        sources.append({"text": data["evidence_level"], "origin": "evidence_level"})
    meta = data.get("metadata")
    if isinstance(meta, dict):
        for g in as_list(meta.get("guidelines")):
            if isinstance(g, dict):
                entry = {"text": g.get("name", ""), "origin": "metadata.guidelines"}
                entry.update({k: v for k, v in g.items() if k != "name"})
            else:
                entry = {"text": g, "origin": "metadata.guidelines"}
            sources.append(entry)
    return sources


def differential_entries(data: dict):
    out = list(as_list(data.get("differentials")))
    for key in ("differential_diagnosis", "causes_and_differential_diagnosis"):
        val = data.get(key)
        if isinstance(val, dict):
            for category, items in val.items():
                out.append({"category": category, "diagnoses": items, "origin": key})
        else:
            out.extend(as_list(val))
    return out


# --------------------------------------------------------------------------- conversion

CONSUMED = {
    "id", "title", "entry", "icd10", "snomed", "citations", "references", "evidence_level",
    "differential_diagnosis", "causes_and_differential_diagnosis", "age_min", "age_max",
}


def convert(path: Path):
    text = path.read_text(encoding="utf-8")
    data, dups = load_with_duplicates(text)
    issues = {"duplicate_treatment": None, "urgency_category": None, "notes": []}
    artifacts = Counter()

    out = {}
    out["tree_id"] = data.get("tree_id") or data.get("id") or path.stem
    out["name"] = data.get("name") or data.get("title") or out["tree_id"]
    legacy_title = data.get("title") if data.get("title") and data.get("title") != out["name"] else None

    trace = data.get("trace")
    trace_dict = trace if isinstance(trace, dict) else {}
    version = data.get("version") or trace_dict.get("version") or "1.0"
    out["version"] = str(version)
    out["status"] = "draft"
    out["family"] = data.get("family", "")

    specs = split_specialties(str(data.get("specialty") or ""))
    out["specialty"] = specs[0] if specs else ""
    out["secondary_specialties"] = specs[1:]

    urgency, expl_add, urgency_note, ucat = map_urgency(data.get("urgency"))
    issues["urgency_category"] = ucat
    out["urgency"] = urgency
    explanation = data.get("urgency_explanation") or ""
    if expl_add:
        explanation = f"{explanation} ({expl_add})" if explanation else expl_add
    out["urgency_explanation"] = explanation

    out["chief_complaint"] = data.get("chief_complaint", "")
    out["description"] = data.get("description", "")

    applies_raw = data.get("applies_to")
    applies = dict(applies_raw) if isinstance(applies_raw, dict) else {"sex": applies_raw}
    applies.setdefault("sex", None)
    applies.setdefault("age_min", data.get("age_min"))
    applies.setdefault("age_max", data.get("age_max"))
    out["applies_to"] = {"sex": applies.pop("sex"), "age_min": applies.pop("age_min"),
                         "age_max": applies.pop("age_max"), **applies}

    out["codes"] = {"icd10": split_codes(data.get("icd10")),
                    "snomed": split_codes(data.get("snomed")),
                    "icpc2": []}
    out["sources"] = source_entries(data, artifacts)

    out["presentations"] = data.get("presentations", [])
    out["differentials"] = differential_entries(data)
    out["workup"] = data.get("workup", [])

    treatment_dup = None
    if "treatment" in dups:
        versions = dups["treatment"]
        non_empty = [v for v in versions if v not in (None, [], {})]
        if len(non_empty) <= 1:
            out["treatment"] = non_empty[0] if non_empty else []
            issues["duplicate_treatment"] = "empty duplicate removed"
        else:
            out["treatment"] = versions[-1]  # the section the app has been showing
            treatment_dup = versions[:-1] if len(versions) > 2 else versions[0]
            issues["duplicate_treatment"] = "two non-empty sections; manual merge needed"
    else:
        out["treatment"] = data.get("treatment", [])
    if treatment_dup is not None:
        out["treatment_duplicate"] = treatment_dup

    out["clinical_pearls"] = data.get("clinical_pearls", [])
    red_flags = list(as_list(data.get("red_flags")))
    if ucat == "red_flag_list":
        red_flags.extend(f for f in data["urgency"] if f not in red_flags)
    out["red_flags"] = red_flags
    out["disposition_guidance"] = data.get("disposition_guidance", {})
    out["referrals"] = data.get("referrals", [])
    out["special_populations"] = data.get("special_populations", {})
    out["crisis_resources"] = data.get("crisis_resources", [])

    homeo = data.get("homeopathy")
    if isinstance(homeo, dict):
        remedies = as_list(homeo.get("remedies"))
    else:
        remedies = as_list(homeo)
    out["homeopathy"] = {"validation_statement": HOMEOPATHY_VALIDATION_STATEMENT, "remedies": remedies}

    out["entry_point"] = data.get("entry_point") or data.get("entry") or ""
    out["nodes"] = data.get("nodes", [])
    out["criteria"] = data.get("criteria", [])

    # Everything else is carried over unchanged.
    extras = {}
    if legacy_title:
        extras["legacy_title"] = legacy_title
    for k, v in data.items():
        if k in TEMPLATE_FIELDS or k in CONSUMED or k in out:
            continue
        if k == "trace":
            if isinstance(v, dict):
                rest = {kk: vv for kk, vv in v.items() if kk not in ("source", "version", "last_updated")}
                if rest:
                    extras["trace"] = rest
            else:
                extras["trace"] = v  # case vignette text, not source metadata
            continue
        if k == "metadata" and isinstance(v, dict):
            rest = {kk: vv for kk, vv in v.items() if kk != "guidelines"}
            if rest:
                extras["metadata"] = rest
            continue
        if k == "urgency_explanation":
            continue
        extras[k] = v
    out.update(extras)

    change_log = list(as_list(data.get("change_log")))
    if trace_dict.get("version") or trace_dict.get("last_updated"):
        change_log.append({"date": str(trace_dict.get("last_updated", "")),
                           "version": str(trace_dict.get("version", "")),
                           "change": "Version recorded in trace metadata before standardization"})
    entry = {"date": TODAY, "version": out["version"], "change": "Standardized to template"}
    notes = []
    if urgency_note:
        notes.append(urgency_note)
    if ucat == "red_flag_list":
        notes.append("urgency held a list of red flags; moved to red_flags, urgency left empty")
    if ucat == "missing":
        notes.append("urgency missing; left empty")
    if issues["duplicate_treatment"] == "empty duplicate removed":
        notes.append("duplicate treatment key: empty section removed, populated section kept")
    elif issues["duplicate_treatment"]:
        notes.append("duplicate treatment key: section the app displayed kept as treatment, "
                     "the other kept as treatment_duplicate; merge by hand")
    if legacy_title:
        notes.append("former title kept as legacy_title")
    if notes:
        entry["notes"] = "; ".join(notes)
    change_log.append(entry)
    out["change_log"] = change_log

    issues["notes"] = notes
    issues["artifacts"] = dict(artifacts)
    issues["legacy_title"] = legacy_title
    issues["original_urgency"] = data.get("urgency")
    return out, issues, data, dups


# --------------------------------------------------------------------------- dumping

class TreeDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def _str_representer(dumper, value):
    style = "|" if "\n" in value else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


TreeDumper.add_representer(str, _str_representer)


def dump(data: dict) -> str:
    return yaml.dump(data, Dumper=TreeDumper, sort_keys=False, allow_unicode=True,
                     width=10**9, default_flow_style=False, indent=2)


# --------------------------------------------------------------------------- content check

def leaves(value, acc: Counter):
    if isinstance(value, dict):
        for k, v in value.items():
            acc[str(k)] += 1
            leaves(v, acc)
    elif isinstance(value, list):
        for v in value:
            leaves(v, acc)
    elif value is not None and value != "":
        acc[str(value)] += 1
    return acc


def verify_no_content_lost(original: dict, dups: dict, converted: dict, path: Path):
    """Every text value in the original must still be present after conversion."""
    orig = dict(original)
    orig["citations"] = fix_colon_artifacts(as_list(orig.get("citations")), Counter(), "citations")
    before = leaves(orig, Counter())
    for extra in dups.get("treatment", [])[:-1]:
        leaves(extra, before)
    after = leaves(converted, Counter())
    missing = before - after
    # Keys that were renamed/restructured away are expected to disappear as keys.
    expected_gone = {"id", "title", "entry", "icd10", "snomed", "citations", "references",
                     "evidence_level", "differential_diagnosis", "causes_and_differential_diagnosis",
                     "trace", "source", "last_updated", "guidelines", "metadata", "age_min", "age_max",
                     "name", "version", "urgency", "urgency_explanation", "treatment", "homeopathy",
                     "applies_to", "red_flags", "differentials"}
    # Category keys of differential_diagnosis become values; equal id/title/entry values collapse.
    for k in expected_gone:
        missing.pop(k, None)
    for k in ("id", "title", "entry"):
        if k in original:
            missing.pop(str(original[k]), None)
    if "version" in original or isinstance(original.get("trace"), dict):
        for v in (original.get("version"), (original.get("trace") or {}).get("version") if isinstance(original.get("trace"), dict) else None):
            if v is not None:
                missing.pop(str(v), None)
    # Specialty strings are split into parts; urgency/explanation text is kept
    # inside a longer explanation or change_log note. Accept a value if its
    # wording survives verbatim somewhere in the converted tree.
    haystack = "\n".join(after)
    spec = str(original.get("specialty") or "")
    if spec in missing and all(p in after for p in split_specialties(spec)):
        missing.pop(spec)
    return {k: v for k, v in missing.items() if v > 0 and k not in haystack}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--issues-out", type=Path, help="write per-file conversion notes as JSON")
    args = ap.parse_args()

    all_issues, problems = {}, []
    for path in sorted(TREES_DIR.glob("*.yml")):
        converted, issues, original, dups = convert(path)
        rendered = dump(converted)
        if yaml.safe_load(rendered) != converted:
            problems.append(f"{path.name}: round-trip mismatch")
        lost = verify_no_content_lost(original, dups, converted, path)
        if lost:
            problems.append(f"{path.name}: content missing after conversion: {lost}")
        all_issues[path.name] = issues
        if not args.dry_run:
            path.write_text(rendered, encoding="utf-8")

    if args.issues_out:
        args.issues_out.write_text(json.dumps(all_issues, indent=1, default=str, ensure_ascii=False))
    for p in problems:
        print("PROBLEM:", p)
    print(f"{len(all_issues)} trees processed, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
