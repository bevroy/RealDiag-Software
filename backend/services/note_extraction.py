"""
Rules-based extraction from clinical notes (no AI, no model).

Reads the text of the chart's notes (FHIR DocumentReference: visit notes,
H&Ps, discharge summaries) and extracts, with fixed patterns only:

- sections, by recognised headings (Chief Complaint, HPI, Past Medical
  History, Medications, Allergies, Physical Exam, Assessment, Plan, ...);
- problems: list lines under Assessment / Impression / Problem List /
  Diagnoses / Past Medical History;
- medications: list lines under Medications;
- allergies: list lines under Allergies;
- key findings: vital-sign and lab values written in the text (BP 150/95,
  HR 112, T 38.6 C, RR 24, SpO2 91%, HbA1c 8.2%, ...).

Every fact carries its source: resource type, document id, document type,
date and section. The result is an extracted summary of what the notes say,
not a clinical interpretation; nothing is inferred or ranked.
"""
import html
import re
from typing import Any, Dict, List, Optional

LABEL = "Extracted summary: text taken from the chart's notes by fixed rules. Not a clinical interpretation."

# Section heading -> section key. Matched at the start of a line, followed by ":" or end of line.
SECTION_HEADINGS = [
    (r"chief complaint|cc|reason for visit", "chief_complaint"),
    (r"history of present illness|hpi", "hpi"),
    (r"past medical history|pmh|medical history", "past_medical_history"),
    (r"past surgical history|psh|surgical history", "past_surgical_history"),
    (r"medications?|current medications|home medications|meds", "medications"),
    (r"allerg(?:y|ies)", "allergies"),
    (r"family history|fh", "family_history"),
    (r"social history|sh", "social_history"),
    (r"review of systems|ros", "review_of_systems"),
    (r"vital signs|vitals", "vitals"),
    (r"physical exam(?:ination)?|exam|pe", "physical_exam"),
    (r"labs?|laboratory|results", "results"),
    (r"assessment and plan|a/p|a&p", "assessment_and_plan"),
    (r"assessment|impression", "assessment"),
    (r"problem list|active problems|diagnos[ie]s", "problem_list"),
    (r"plan", "plan"),
]
_HEADING = re.compile(
    r"^\s*(?:#+\s*)?(" + "|".join(p for p, _ in SECTION_HEADINGS) + r")\s*(?::|$)\s*(.*)$", re.IGNORECASE)
PROBLEM_SECTIONS = ("assessment", "assessment_and_plan", "problem_list", "past_medical_history")

# Values written in the text. Each: (kind, label, regex, unit group handling)
_NUM = r"(\d{1,3}(?:\.\d+)?)"
FINDING_PATTERNS = [
    ("vital", "Blood pressure", re.compile(r"\b(?:BP|blood pressure)\s*[:=]?\s*(\d{2,3})\s*/\s*(\d{2,3})", re.I), "mmHg"),
    ("vital", "Heart rate", re.compile(r"\b(?:HR|heart rate|pulse|P)\s*[:=]?\s*" + _NUM + r"\b(?!\s*/)", re.I), "/min"),
    ("vital", "Respiratory rate", re.compile(r"\b(?:RR|resp(?:iratory)? rate)\s*[:=]?\s*" + _NUM + r"\b", re.I), "/min"),
    ("vital", "Temperature", re.compile(r"\b(?:T|temp(?:erature)?)\s*[:=]?\s*" + _NUM + r"\s*°?\s*([CF])\b", re.I), None),
    ("vital", "Oxygen saturation", re.compile(r"\b(?:SpO2|O2 sat(?:uration)?|sats?)\s*[:=]?\s*" + _NUM + r"\s*%", re.I), "%"),
    ("lab", "HbA1c", re.compile(r"\b(?:HbA1c|A1c|hemoglobin A1c)\s*[:=]?\s*(?:of\s*)?" + _NUM + r"\s*%", re.I), "%"),
    ("lab", "Creatinine", re.compile(r"\b(?:creatinine|Cr)\s*[:=]?\s*(?:of\s*)?" + _NUM + r"\b", re.I), "mg/dL"),
    ("lab", "eGFR", re.compile(r"\beGFR\s*[:=]?\s*(?:of\s*)?" + _NUM + r"\b", re.I), "mL/min/1.73m2"),
    ("lab", "Hemoglobin", re.compile(r"\b(?:Hgb|Hb|hemoglobin)\s*[:=]?\s*(?:of\s*)?" + _NUM + r"\b(?!\s*A1c)", re.I), "g/dL"),
    ("lab", "Potassium", re.compile(r"\b(?:K|potassium)\s*[:=]\s*" + _NUM + r"\b", re.I), "mmol/L"),
    ("lab", "Troponin", re.compile(r"\btroponin(?:\s*[IT])?\s*[:=]?\s*(?:of\s*)?(\d+(?:\.\d+)?)\b", re.I), None),
    ("lab", "LDL", re.compile(r"\bLDL(?:-C)?\s*[:=]?\s*(?:of\s*)?" + _NUM + r"\b", re.I), "mg/dL"),
    ("lab", "TSH", re.compile(r"\bTSH\s*[:=]?\s*(?:of\s*)?(\d+(?:\.\d+)?)\b", re.I), "mIU/L"),
]

_UNREADABLE = ("content not available",)
_LIST_ITEM = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s*")


def _plain_text(content: str) -> str:
    text = re.sub(r"<\s*(br|/p|/div|/li|/h\d)\s*/?>", "\n", content or "", flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(text)


def split_sections(text: str) -> Dict[str, str]:
    """{section_key: text} for recognised headings; text before any heading is "preamble"."""
    sections: Dict[str, List[str]] = {}
    current = "preamble"
    for line in text.splitlines():
        m = _HEADING.match(line)
        if m:
            heading = m.group(1).lower()
            current = next(key for pattern, key in SECTION_HEADINGS if re.fullmatch(pattern, heading, re.I))
            sections.setdefault(current, [])
            if m.group(2).strip():
                sections[current].append(m.group(2).strip())
            continue
        sections.setdefault(current, []).append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip()}


def _items(section_text: str) -> List[str]:
    """List lines of a section (bullets, numbers, or one item per line / semicolon)."""
    out = []
    for line in section_text.splitlines():
        line = _LIST_ITEM.sub("", line).strip()
        for part in re.split(r";", line):
            part = part.strip(" .,")
            if part and len(part) <= 200:
                out.append(part)
    return out


def _findings(text: str) -> List[Dict[str, Any]]:
    found, seen = [], set()
    for kind, label, pattern, unit in FINDING_PATTERNS:
        for m in pattern.finditer(text):
            if label == "Blood pressure":
                value, shown_unit = f"{m.group(1)}/{m.group(2)}", unit
            elif label == "Temperature":
                value, shown_unit = m.group(1), m.group(2).upper()
            else:
                value, shown_unit = m.group(1), unit
            key = (label, value)
            if key in seen:
                continue
            seen.add(key)
            found.append({"kind": kind, "label": label, "value": value, "unit": shown_unit,
                          "text": m.group(0).strip()})
    return found


def extract_note(note: Any) -> Dict[str, Any]:
    """Facts from one note, each with its source."""
    source = {"resource_type": "DocumentReference", "document_id": getattr(note, "document_id", None),
              "document_type": getattr(note, "type", None), "date": str(getattr(note, "date", "") or "")[:10] or None}
    content = getattr(note, "content", "") or ""
    if not content.strip() or content.strip().lower().startswith(_UNREADABLE) or content.strip().startswith("http"):
        return {"source": source, "readable": False, "facts": []}
    sections = split_sections(_plain_text(content))
    facts: List[Dict[str, Any]] = []

    def add(kind: str, text: str, section: str, **extra: Any) -> None:
        facts.append({"kind": kind, "text": text, "section": section, "source": source, **extra})

    for key in PROBLEM_SECTIONS:
        for item in _items(sections.get(key, "")):
            add("problem", item, key)
    for item in _items(sections.get("medications", "")):
        add("medication", item, "medications")
    for item in _items(sections.get("allergies", "")):
        add("allergy", item, "allergies")
    if sections.get("chief_complaint"):
        add("chief_complaint", sections["chief_complaint"].splitlines()[0].strip(), "chief_complaint")
    for key, text in sections.items():
        for finding in _findings(text):
            add("finding", finding["text"], key, finding_kind=finding["kind"], label=finding["label"],
                value=finding["value"], unit=finding["unit"])
    return {"source": source, "readable": True, "sections": sorted(sections), "facts": facts}


def extracted_summary(history: Any, history_status: Optional[str], limit: int = 10) -> Dict[str, Any]:
    """Extraction over the chart's most recent notes (up to `limit`)."""
    summary: Dict[str, Any] = {"label": LABEL, "documents_read": 0, "documents_unreadable": 0, "facts": [],
                               "not_read": []}
    if history is None or history_status != "retrieved":
        summary["not_read"].append("Clinical notes could not be retrieved; nothing was extracted.")
        return summary
    notes = list(getattr(history, "visit_notes", []) or [])
    for note in notes[:limit]:
        result = extract_note(note)
        if result["readable"]:
            summary["documents_read"] += 1
            summary["facts"].extend(result["facts"])
        else:
            summary["documents_unreadable"] += 1
    if len(notes) > limit:
        summary["not_read"].append(f"Only the {limit} most recent of {len(notes)} notes were read.")
    if summary["documents_unreadable"]:
        summary["not_read"].append(f"{summary['documents_unreadable']} note(s) had no readable text "
                                   "(no content, or an attachment that could not be retrieved).")
    return summary
