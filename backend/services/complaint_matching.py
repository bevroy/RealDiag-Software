"""
Today's complaint: where it comes from and whether it matches a condition.

The complaint is the clinician's typed text when given, otherwise the EHR's
reason for the current visit (Encounter.reasonCode), otherwise none. The
source is always reported.

Matching is on whole words or phrases from a reviewable term list
(criteria.complaint_terms in the tree). A term preceded by a negation cue in
the same clause ("no chest pain", "denies fever, chills") does not match.
No language model is involved.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

ENTERED = "entered"
EHR_VISIT_REASON = "ehr_visit_reason"
NO_COMPLAINT = "none"

SOURCE_LABELS = {
    ENTERED: "Entered by clinician",
    EHR_VISIT_REASON: "EHR visit reason",
    NO_COMPLAINT: "No complaint entered or found",
}

NEGATION_CUES = ("no", "not", "denies", "denied", "denying", "without", "negative for", "free of",
                 "absence of", "resolved", "never")
# Negation does not carry past these.
_CLAUSE_BREAK = re.compile(r"[.;!?\n]|\bbut\b|\bhowever\b|\balthough\b|\bexcept\b", re.IGNORECASE)
_NORMALIZE = [
    (re.compile(r"[-/]"), " "),
    (re.compile(r"\b(radiates|radiation|radiating|radiate)\b"), "radiating"),
    (re.compile(r"\bon exertion\b"), "with exertion"),
    (re.compile(r"\b(the|a|an|left|right)\b"), " "),
    (re.compile(r"[^a-z0-9 ]"), " "),
    (re.compile(r"\s+"), " "),
]
_NEGATION = re.compile(r"\b(" + "|".join(re.escape(c) for c in NEGATION_CUES) + r")\b")


@dataclass
class Complaint:
    text: Optional[str]
    source: str
    warnings: List[str] = field(default_factory=list)

    @property
    def source_label(self) -> str:
        return SOURCE_LABELS[self.source]


def normalize(text: str) -> str:
    text = (text or "").lower()
    for pattern, replacement in _NORMALIZE:
        text = pattern.sub(replacement, text)
    return text.strip()


def match_terms(complaint: Optional[str], terms: List[str]) -> Tuple[List[str], List[str]]:
    """(matched terms, negated terms) for a complaint against a term list."""
    matched: List[str] = []
    negated: List[str] = []
    if not complaint or not terms:
        return matched, negated
    clauses = [normalize(c) for c in _CLAUSE_BREAK.split(complaint)]
    for term in terms:
        pattern = re.compile(r"(?<![a-z0-9])" + re.escape(normalize(term)) + r"(?![a-z0-9])")
        found = was_negated = False
        for clause in clauses:
            for m in pattern.finditer(clause):
                if _NEGATION.search(clause[:m.start()]):
                    was_negated = True
                else:
                    found = True
        if found:
            matched.append(term)
        elif was_negated:
            negated.append(term)
    return matched, negated


def affirmed_phrases(complaint: Optional[str]) -> List[str]:
    """Complaint split into phrases for library ranking, with negated parts removed.

    "chest pain and nausea, no fever" -> ["chest pain", "nausea"].
    """
    phrases: List[str] = []
    for clause in _CLAUSE_BREAK.split(complaint or ""):
        lowered = clause.lower()
        cue = _NEGATION.search(lowered)
        kept = clause[:cue.start()] if cue else clause
        for part in re.split(r",|\band\b|\bor\b", kept, flags=re.IGNORECASE):
            part = part.strip(" \t-:")
            if part and part.lower() not in (p.lower() for p in phrases):
                phrases.append(part)
    return phrases


def encounter_reason(encounter: Optional[Dict[str, Any]]) -> Optional[str]:
    """Reason for the visit from a FHIR Encounter (reasonCode text, else coding display)."""
    reasons: List[str] = []
    for concept in (encounter or {}).get("reasonCode") or []:
        text = concept.get("text") or next(
            (c.get("display") for c in concept.get("coding") or [] if c.get("display")), None)
        if text and text not in reasons:
            reasons.append(text)
    return "; ".join(reasons) or None


def resolve_complaint(typed: Optional[str],
                      fetch_encounter: Optional[Callable[[], Optional[Dict[str, Any]]]] = None) -> Complaint:
    """Typed complaint first, then the EHR visit reason, else none (with the source)."""
    if typed and typed.strip():
        return Complaint(text=typed.strip(), source=ENTERED)
    warnings: List[str] = []
    if fetch_encounter is not None:
        try:
            reason = encounter_reason(fetch_encounter())
        except Exception:
            reason = None
            warnings.append("Today's visit reason could not be retrieved from the EHR.")
        if reason:
            return Complaint(text=reason, source=EHR_VISIT_REASON)
    return Complaint(text=None, source=NO_COMPLAINT, warnings=warnings)
