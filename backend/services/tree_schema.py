"""
Standard decision-tree template and read helpers.

Every file in backend/trees/ follows TEMPLATE_FIELDS (see
backend/scripts/standardize_trees.py for the migration). Code that reads trees
should go through the helpers below instead of reaching for raw keys, so that
trees still waiting in backend/data/generated_trees (older layout) keep working.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

TEMPLATE_FIELDS = [
    "tree_id", "name", "version", "status", "family", "specialty", "secondary_specialties",
    "urgency", "urgency_explanation", "chief_complaint", "description", "applies_to", "codes",
    "sources", "presentations", "differentials", "workup", "treatment", "clinical_pearls",
    "red_flags", "disposition_guidance", "referrals", "special_populations", "crisis_resources",
    "homeopathy", "entry_point", "nodes", "criteria", "change_log",
]

# Fields that must be present (they may be empty) in every standardized tree.
REQUIRED_FIELDS = TEMPLATE_FIELDS
REQUIRED_NON_EMPTY = ["tree_id", "name", "version", "status", "family", "specialty"]

URGENCY_VALUES = ("emergent", "urgent", "routine")
STATUS_VALUES = ("draft", "review", "approved", "retired")

HOMEOPATHY_VALIDATION_STATEMENT = "This content has not been clinically validated."


def _as_list(value: Any) -> List[Any]:
    if value is None or value == "":
        return []
    return list(value) if isinstance(value, list) else [value]


def tree_id(tree: Dict[str, Any], default: str = "") -> str:
    return tree.get("tree_id") or tree.get("id") or default


def tree_name(tree: Dict[str, Any], default: str = "") -> str:
    return tree.get("name") or tree.get("title") or default


def entry_point(tree: Dict[str, Any]) -> Optional[str]:
    return tree.get("entry_point") or tree.get("entry")


def _codes(tree: Dict[str, Any]) -> Dict[str, Any]:
    codes = tree.get("codes")
    return codes if isinstance(codes, dict) else {}


def icd10_codes(tree: Dict[str, Any]) -> List[str]:
    codes = _codes(tree)
    raw = codes["icd10"] if "icd10" in codes else (tree.get("icd10") or tree.get("icd10_code"))
    return [str(c) for c in _as_list(raw) if c]


def primary_icd10(tree: Dict[str, Any]) -> str:
    codes = icd10_codes(tree)
    return codes[0] if codes else ""


def snomed_codes(tree: Dict[str, Any]) -> List[str]:
    codes = _codes(tree)
    raw = codes["snomed"] if "snomed" in codes else tree.get("snomed")
    return [str(c) for c in _as_list(raw) if c is not None and c != ""]


def icpc2_codes(tree: Dict[str, Any]) -> List[str]:
    return [str(c) for c in _as_list(_codes(tree).get("icpc2")) if c]


def applies_to(tree: Dict[str, Any]) -> Dict[str, Any]:
    """Return {'sex', 'age_min', 'age_max'} regardless of layout."""
    raw = tree.get("applies_to")
    if isinstance(raw, dict):
        return {"sex": raw.get("sex"), "age_min": raw.get("age_min"), "age_max": raw.get("age_max")}
    return {"sex": raw, "age_min": tree.get("age_min"), "age_max": tree.get("age_max")}


def specialties(tree: Dict[str, Any]) -> List[str]:
    primary = tree.get("specialty") or ""
    return ([primary] if primary else []) + [s for s in _as_list(tree.get("secondary_specialties")) if s]


def specialty_display(tree: Dict[str, Any]) -> str:
    """Specialties joined for display, e.g. 'Cardiology, Emergency Medicine'."""
    return ", ".join(specialties(tree))


def source_texts(tree: Dict[str, Any], exclude_origins: tuple = ()) -> List[str]:
    """Plain-text citation strings from `sources` (or legacy `citations`)."""
    if "sources" in tree:
        out = []
        for s in _as_list(tree.get("sources")):
            if isinstance(s, dict) and s.get("origin") in exclude_origins:
                continue
            if isinstance(s, dict):
                text = s.get("text") or s.get("name") or ""
                if s.get("origin") == "evidence_level" and text:
                    text = f"Evidence level: {text}"
                if text:
                    out.append(str(text))
            elif s:
                out.append(str(s))
        return out
    out = []
    for c in _as_list(tree.get("citations")):
        if isinstance(c, dict):
            out.extend(f"{k}: {v}" for k, v in c.items())
        else:
            out.append(str(c))
    return out


def primary_source(tree: Dict[str, Any], default: str = "Clinical Decision Tree") -> str:
    """The guideline source line previously stored at trace.source."""
    for s in _as_list(tree.get("sources")):
        if isinstance(s, dict) and s.get("origin") == "trace.source" and s.get("text"):
            return str(s["text"])
    trace = tree.get("trace")
    if isinstance(trace, dict) and trace.get("source"):
        return str(trace["source"])
    return default


def homeopathy_remedies(tree: Dict[str, Any]) -> List[Any]:
    homeo = tree.get("homeopathy")
    if isinstance(homeo, dict):
        return _as_list(homeo.get("remedies"))
    return _as_list(homeo)


def differential_names(tree: Dict[str, Any]) -> List[str]:
    """Flatten differentials (plain strings and {category, diagnoses} groups) to strings."""
    out: List[str] = []
    raw = tree.get("differentials")
    if raw is None and isinstance(tree.get("differential_diagnosis"), dict):
        raw = [{"category": k, "diagnoses": v} for k, v in tree["differential_diagnosis"].items()]
    for d in _as_list(raw):
        if isinstance(d, dict) and "diagnoses" in d:
            out.extend(str(x) for x in _as_list(d.get("diagnoses")))
        elif isinstance(d, dict):
            out.extend(f"{k}: {v}" for k, v in d.items())
        elif d:
            out.append(str(d))
    return out


# Node formats (see node_format):
#   none          - no nodes; presentation-based tree only
#   conditional   - nodes branch on `when` / `next` predicates the engine evaluates
#   questionnaire - nodes ask questions with `options` (label/next) a clinician answers
#   content       - nodes hold content only, with no branching
#   mixed         - both conditional and questionnaire nodes
NODE_FORMATS = ("none", "conditional", "questionnaire", "content", "mixed")


def node_list(tree: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Nodes as a list of dicts, whether stored as a list or an id -> node mapping."""
    nodes = tree.get("nodes") or []
    if isinstance(nodes, dict):
        return [{"id": k, **(v or {})} for k, v in nodes.items()]
    return [n for n in nodes if isinstance(n, dict)]


def node_format(tree: Dict[str, Any]) -> str:
    nodes = node_list(tree)
    if not nodes:
        return "none"
    has_options = any("options" in n for n in nodes)
    has_conditions = any("when" in n or "next" in n for n in nodes)
    if has_options and has_conditions:
        return "mixed"
    if has_options:
        return "questionnaire"
    if has_conditions:
        return "conditional"
    return "content"
