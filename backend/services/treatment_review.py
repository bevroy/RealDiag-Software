"""
Patient-aware treatment review for the encounter assessment (rules only, no AI).

For each suggested diagnosis, every treatment line of its decision tree is
checked against the chart. Medications named in the line (drug names and
drug classes the medication safety service knows) are run through:

- the medication safety service: interactions with the chart's active
  medications, duplicate therapy, contraindications with the problem list,
  allergy cross-reactivity, age (Beers), renal and hepatic adjustments and
  pregnancy warnings;
- a direct allergy check: the medication is named in a recorded allergy;
- the medication-history weighting: a prior adverse reaction to the same
  medication or class (stop reason in MedicationRequest.statusReason).

Each line is marked "appropriate" (no conflict found in the checks that
ran), "caution" or "avoid", with every reason and the chart data it came
from. Lines naming no known medication are "not_checked". Lines keep the
tree's order: nothing is ranked, and no line is presented as the choice.

The thresholds and mappings below are pending clinical review.
"""
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from backend.services.fhir_client import RETRIEVED
from backend.services.missed_items import medication_names

NOTICE = ("Each treatment line from the decision tree is checked against this patient's chart by fixed rules. "
          "\"Appropriate\" means no conflict was found in the checks that ran, not that the option is preferred. "
          "Options are listed in the tree's order and are not ranked. The medication knowledge base is limited and "
          "pending clinical review.")

APPROPRIATE, CAUTION, AVOID, NOT_CHECKED = "appropriate", "caution", "avoid", "not_checked"
MARK_LABELS = {APPROPRIATE: "Appropriate (no conflict found)", CAUTION: "Use with caution", AVOID: "Avoid",
               NOT_CHECKED: "Not checked (no known medication named)"}

# Severity from the medication safety service -> mark. Pending clinical review.
SEVERITY_MARK = {"contraindicated": AVOID, "major": CAUTION, "moderate": CAUTION, "minor": CAUTION}

# eGFR (mL/min/1.73m2) -> the renal_function values the safety service acts on. Pending clinical review.
EGFR_LOINC = ("33914-3", "48642-3", "48643-1", "62238-1", "69405-9", "77147-7", "98979-8")
EGFR_STAGES = ((15, "stage 5"), (30, "stage 4"))

# Problem-list text -> renal / hepatic / pregnancy status. Pending clinical review.
RENAL_PROBLEM_PATTERNS = ((r"\b(esrd|end[- ]stage renal|end[- ]stage kidney|stage (5|v)\b)", "stage 5"),
                          (r"\bstage (4|iv)\b", "stage 4"))
RENAL_PROBLEM_CONTEXT = r"\b(kidney|renal|ckd|esrd)\b"
HEPATIC_PROBLEM_PATTERNS = ((r"child[- ]pugh (class )?c\b", "child-pugh c"), (r"\bcirrhosis\b", "cirrhosis"))
PREGNANCY_PATTERN = r"\bpregnan(t|cy)\b"
NOT_PREGNANT_PATTERN = r"\b(not|no longer) pregnant\b|\bhistory of pregnancy\b"


def _vocabulary() -> List[Tuple[str, Optional[str]]]:
    """(term, class) pairs for the drug names and classes the safety service and history weighting know."""
    from backend.services.diagnostic_router import MEDICATION_CLASS_HINTS, _med_safety

    terms: Dict[str, Optional[str]] = {}
    for drug_class, hints in MEDICATION_CLASS_HINTS.items():
        terms.setdefault(drug_class, drug_class)
        for hint in hints:
            terms.setdefault(hint, drug_class)
    for drug, drug_class in _med_safety.duplicate_therapy_classes.items():
        terms[drug] = drug_class.lower()
        terms.setdefault(drug_class.lower(), drug_class.lower())
    for pair in list(_med_safety.drug_interactions) + list(_med_safety.contraindications):
        terms.setdefault(pair[0], None)
    for med, _allergen in _med_safety.allergen_cross_reactivity:
        terms.setdefault(med, None)
    for term in ("warfarin", "enoxaparin", "gabapentin", "statin", "ace inhibitor", "diphenhydramine",
                 "amitriptyline", "fluoroquinolone", "penicillin", "heparin"):
        terms.setdefault(term, _med_safety._get_drug_class(term))
    terms.pop("contrast dye", None)
    return sorted(terms.items(), key=lambda t: -len(t[0]))


def _term_pattern(term: str) -> re.Pattern:
    words = r"\s+".join(re.escape(w) for w in term.split())
    return re.compile(rf"\b{words}(e?s)?\b", re.IGNORECASE)


# "Penicillin allergy: clindamycin ..." names penicillin as context, not as the option.
_CONTEXT_AFTER = re.compile(r"^[\s-]*(allerg|intoleran|hypersensitiv)", re.IGNORECASE)

_VOCAB: Optional[List[Tuple[str, Optional[str], re.Pattern]]] = None


def named_medications(text: str) -> List[Dict[str, Optional[str]]]:
    """Known drug names and classes named in a treatment line, in order of appearance."""
    global _VOCAB
    if _VOCAB is None:
        _VOCAB = [(term, cls, _term_pattern(term)) for term, cls in _vocabulary()]
    found, taken = [], []
    for term, cls, pattern in _VOCAB:
        for m in pattern.finditer(text or ""):
            if any(m.start() < end and start < m.end() for start, end in taken):
                continue
            taken.append((m.start(), m.end()))
            if _CONTEXT_AFTER.match(text[m.end():]):
                continue
            found.append((m.start(), {"name": term, "class": cls if cls != term else None,
                                      "is_class": cls == term}))
            break
    return [f for _, f in sorted(found, key=lambda x: x[0])]


def _concept_names(resources: List[Dict[str, Any]]) -> List[str]:
    from backend.services.medication_review import _concept_names as names
    return names(resources)


def _date(value: Any) -> Optional[str]:
    if isinstance(value, datetime):
        return value.date().isoformat()
    return str(value)[:10] if value else None


def patient_factors(patient_data: Any) -> Dict[str, Any]:
    """Renal, hepatic and pregnancy status from the chart, each with its source."""
    status = dict(getattr(patient_data, "retrieval_status", {}) or {})
    conditions_ok = status.get("conditions", RETRIEVED) == RETRIEVED
    labs_ok = status.get("labs", RETRIEVED) == RETRIEVED
    problems = _concept_names(patient_data.conditions) if conditions_ok else []
    factors: Dict[str, Any] = {"renal": None, "hepatic": None, "pregnancy": None, "not_checked": []}

    egfr = [lab for lab in (patient_data.labs if labs_ok else []) if getattr(lab, "code", None) in EGFR_LOINC]
    egfr.sort(key=lambda lab: getattr(lab, "effective_date", None) or datetime.min, reverse=True)
    if egfr:
        latest = egfr[0]
        stage = next((s for cutoff, s in EGFR_STAGES if latest.value < cutoff), None)
        if stage:
            factors["renal"] = {"value": stage, "source": f"Lab: eGFR {latest.value:g} {latest.unit or ''}".strip()
                                + (f" on {_date(latest.effective_date)}" if latest.effective_date else "")}
    if not factors["renal"]:
        for problem in problems:
            if re.search(RENAL_PROBLEM_CONTEXT, problem, re.I):
                stage = next((s for p, s in RENAL_PROBLEM_PATTERNS if re.search(p, problem, re.I)), None)
                if stage:
                    factors["renal"] = {"value": stage, "source": f"Problem list: {problem}"}
                    break
    for problem in problems:
        value = next((v for p, v in HEPATIC_PROBLEM_PATTERNS if re.search(p, problem, re.I)), None)
        if value:
            factors["hepatic"] = {"value": value, "source": f"Problem list: {problem}"}
            break
    for problem in problems:
        if re.search(PREGNANCY_PATTERN, problem, re.I) and not re.search(NOT_PREGNANT_PATTERN, problem, re.I):
            factors["pregnancy"] = {"value": True, "source": f"Problem list: {problem}"}
            break

    if not labs_ok and not factors["renal"]:
        factors["not_checked"].append("Labs could not be retrieved; renal function was taken from the problem "
                                      "list only.")
    if not conditions_ok:
        factors["not_checked"].append("The problem list could not be retrieved; contraindications, hepatic "
                                      "function and pregnancy were not checked.")
    elif not factors["pregnancy"] and str(getattr(patient_data, "gender", "")).lower() == "female":
        factors["not_checked"].append("Pregnancy is not recorded on the problem list; pregnancy warnings apply "
                                      "only when it is.")
    return factors


ALERT_SOURCES = {"drug_interaction": "Medication list", "duplicate_therapy": "Medication list",
                 "contraindication": "Problem list", "allergen_cross_reactivity": "Allergies",
                 "age_warning": "Patient age"}


def _involves(alert: Dict[str, Any], terms: List[str]) -> bool:
    """The alert pairs the option's medication with something from the chart (not with its own class)."""
    names = [n.strip() for n in (alert.get("medication") or "").split(",")]
    if alert.get("interacting_medication"):
        names.append(alert["interacting_medication"])
    if alert["alert_type"] in ("drug_interaction", "duplicate_therapy"):
        return any(n in terms for n in names) and any(n not in terms for n in names)
    return any(n in terms for n in names)


class TreatmentReviewer:
    """Checks treatment lines against one patient's chart."""

    def __init__(self, patient_data: Any, history: Any, history_medication_status: Optional[str]):
        status = dict(getattr(patient_data, "retrieval_status", {}) or {})
        self.meds_ok = status.get("medications", RETRIEVED) == RETRIEVED
        self.conditions_ok = status.get("conditions", RETRIEVED) == RETRIEVED
        self.allergies_ok = status.get("allergies", RETRIEVED) == RETRIEVED
        self.current = medication_names(patient_data.medications) if self.meds_ok else []
        self.conditions = _concept_names(patient_data.conditions) if self.conditions_ok else []
        self.allergies = _concept_names(patient_data.allergies) if self.allergies_ok else []
        self.age = patient_data.age
        self.factors = patient_factors(patient_data)
        self.history_ok = history is not None and history_medication_status == RETRIEVED
        self.history_records = list(getattr(history, "medication_history", []) or []) if self.history_ok else []
        self.not_checked = list(self.factors["not_checked"])
        if not self.meds_ok:
            self.not_checked.append("The medication list could not be retrieved; interactions were not checked.")
        if not self.allergies_ok:
            self.not_checked.append("Allergies could not be retrieved; allergies were not checked.")
        if self.age is None:
            self.not_checked.append("Age is unknown; age-specific warnings were not checked.")
        if not self.history_ok:
            self.not_checked.append("The medication history could not be retrieved; prior adverse reactions were "
                                    "not checked.")
        self._cache: Dict[str, List[Dict[str, Any]]] = {}

    def _reasons_for(self, med: Dict[str, Any]) -> List[Dict[str, Any]]:
        if med["name"] in self._cache:
            return self._cache[med["name"]]
        from backend.services.diagnostic_router import _classify_medication, _med_safety, is_adverse_stop_reason

        terms = [med["name"]] + ([med["class"]] if med["class"] else [])
        factors = self.factors
        safety = _med_safety.check_medication_safety(
            current_medications=self.current, proposed_medications=terms,
            patient_conditions=self.conditions, patient_allergies=self.allergies, age=self.age,
            renal_function=factors["renal"]["value"] if factors["renal"] else None,
            hepatic_function=factors["hepatic"]["value"] if factors["hepatic"] else None,
            pregnancy=bool(factors["pregnancy"]))
        reasons, seen = [], set()
        for alert in safety["alerts"]:
            kind = alert["alert_type"]
            if not _involves(alert, terms) or alert["description"] in seen:
                continue
            seen.add(alert["description"])
            if kind == "renal_adjustment":
                source = factors["renal"]["source"]
            elif kind == "hepatic_adjustment":
                source = factors["hepatic"]["source"]
            elif kind == "pregnancy_warning":
                source = factors["pregnancy"]["source"]
            else:
                source = ALERT_SOURCES.get(kind, "Medication safety rules")
                if kind == "drug_interaction":
                    other = alert["interacting_medication"] if alert["medication"] in terms else alert["medication"]
                    source = f"Medication list: {other}"
                elif kind == "allergen_cross_reactivity":
                    source = f"Allergies: {alert['allergen']}"
                elif kind == "contraindication":
                    source = f"Problem list: {alert['condition']}"
            reasons.append({"mark": SEVERITY_MARK.get(alert["severity"], CAUTION), "check": kind,
                            "severity": alert["severity"],
                            "reason": " ".join(x for x in (alert["description"] + ".", alert.get("clinical_effect"))
                                               if x),
                            "source": source})

        for allergy in self.allergies:
            if any(_term_pattern(t).search(allergy) for t in terms):
                reasons.append({"mark": AVOID, "check": "recorded_allergy", "severity": None,
                                "reason": f"{med['name']} is named in a recorded allergy.",
                                "source": f"Allergies: {allergy}"})

        # Prior adverse reactions: the history weighting's adverse-stop rule and medication classifier.
        term_class = med["name"] if med["is_class"] else (med["class"] or _classify_medication(med["name"]))
        for record in self.history_records:
            if not is_adverse_stop_reason(record.get("stop_reason")):
                continue
            name = record.get("name") or ""
            record_class = _classify_medication(name)
            same_drug = any(_term_pattern(t).search(name) for t in terms if t != med["class"])
            same_class = record_class != "unknown" and record_class.lower() == (term_class or "").lower()
            if not (same_drug or same_class):
                continue
            relation = "this medication" if same_drug else f"the same class ({record_class})"
            stopped = f" stopped {record['date_stopped']}" if record.get("date_stopped") else ""
            reasons.append({"mark": AVOID, "check": "prior_adverse_reaction", "severity": None,
                            "reason": f"Prior adverse reaction to {relation}: {name}{stopped} "
                                      f"({record.get('stop_reason')}).",
                            "source": "Medication history: MedicationRequest.statusReason"})
        self._cache[med["name"]] = reasons
        return reasons

    def review_line(self, text: str) -> Dict[str, Any]:
        meds = named_medications(text)
        if not meds:
            return {"text": text, "mark": NOT_CHECKED, "mark_label": MARK_LABELS[NOT_CHECKED], "medications": [],
                    "reasons": []}
        reasons = []
        for med in meds:
            for reason in self._reasons_for(med):
                reasons.append({"medication": med["name"], **reason})
        if not self.allergies_ok:
            reasons.append({"medication": None, "mark": CAUTION, "check": "data_missing", "severity": None,
                            "reason": "Allergies could not be retrieved, so allergies were not checked.",
                            "source": "Allergies: not retrieved"})
        if not self.meds_ok:
            reasons.append({"medication": None, "mark": CAUTION, "check": "data_missing", "severity": None,
                            "reason": "The medication list could not be retrieved, so interactions were not checked.",
                            "source": "Medication list: not retrieved"})
        marks = {r["mark"] for r in reasons}
        mark = AVOID if AVOID in marks else CAUTION if CAUTION in marks else APPROPRIATE
        return {"text": text, "mark": mark, "mark_label": MARK_LABELS[mark],
                "medications": [m["name"] for m in meds], "reasons": reasons}

    def review_sections(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {"notice": NOTICE,
                "patient_factors": {k: v for k, v in self.factors.items() if k != "not_checked"},
                "not_checked": self.not_checked,
                "sections": [[self.review_line(item) for item in s.get("items", [])] for s in sections]}
