"""
Possible missed items (encounter assessment, Phase 3).

Three rule-based checks; no language model is involved:

  abnormal_without_diagnosis   chart criteria met for a chronic condition that
                               is not on the problem list
  diagnosis_without_support    problem-list condition with no supporting
                               result and no related medication in the window
                               (both sides shown; the conflict is not resolved)
  overdue_screening            USPSTF grade A/B screenings that may be due
                               (backend/screening/uspstf_rules.yml)

Wording is "consider" / "may be due" with the source cited; nothing is ever
stated as missed. Every item carries its tree's or rule's review status.
A check that could not run because data was not retrieved says so instead
of producing items.
"""

import re
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import yaml

from backend.services.clinical_review import SCREENING_RULES_PATH, review_fields
from backend.services.fhir_client import NOT_AVAILABLE, RESOURCE_LABELS, RETRIEVED
from backend.services.smart_diagnostic_engine import SmartDiagnosticEngine, known_condition

# How far back the encounter assessment pulls screening evidence
SCREENING_LAB_LOOKBACK_DAYS = 3650
SCREENING_PROCEDURE_LOOKBACK_DAYS = 3650
VITAL_LOOKBACK_DAYS = 365
BMI_LOINC = "39156-5"

EVIDENCE_RESOURCE = {"lab": "labs", "vital": "vitals", "procedure": "procedures", "imaging": "imaging_studies"}
EVIDENCE_WINDOW_DAYS = {"lab": SCREENING_LAB_LOOKBACK_DAYS, "vital": VITAL_LOOKBACK_DAYS,
                        "procedure": SCREENING_PROCEDURE_LOOKBACK_DAYS, "imaging": SCREENING_PROCEDURE_LOOKBACK_DAYS}
NOT_VISIBLE = "Tests, results or prescriptions from other organizations may not be in this chart."

SINGLE_RESULTS_TITLE = "Single results that may need repeating"

CHECK_TITLES = {
    "abnormal_without_diagnosis": "Abnormal results without a diagnosis",
    "diagnosis_without_support": "Diagnoses without supporting results or medication",
    "overdue_screening": "Screenings that may be due",
}


# --------------------------------------------------------------------------- rules

@lru_cache(maxsize=2)
def load_screening_rules(path: Path = SCREENING_RULES_PATH) -> List[Dict[str, Any]]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return [r for r in data.get("rules") or [] if r.get("status") != "retired"]


def screening_requirements(path: Path = SCREENING_RULES_PATH) -> Dict[str, Dict[str, Any]]:
    """Extra observation groups the FHIR fetch needs for the screening rules."""
    lab_codes = sorted({c for rule in load_screening_rules(path) for ev in rule.get("evidence") or []
                        if ev.get("kind") == "lab" for c in ev.get("loinc") or []})
    return {
        "labs:screening": {"codes": lab_codes, "lookback_days": SCREENING_LAB_LOOKBACK_DAYS},
        "vitals:screening": {"codes": [BMI_LOINC], "lookback_days": VITAL_LOOKBACK_DAYS},
    }


# --------------------------------------------------------------------------- helpers

def _naive(dt: Any) -> Optional[datetime]:
    if dt is None:
        return None
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except ValueError:
            try:
                dt = datetime.strptime(dt[:10], "%Y-%m-%d")
            except ValueError:
                return None
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def _date_text(dt: Any) -> str:
    d = _naive(dt)
    return d.strftime("%Y-%m-%d") if d else "date unknown"


def _years_text(days: int) -> str:
    years = round(days / 365)
    return f"{years} year{'s' if years != 1 else ''}" if days >= 365 else f"{days} days"


def _status(all_status: Dict[str, str], resource: str) -> str:
    return all_status.get(resource, RETRIEVED)


def _label(resource: str) -> str:
    return RESOURCE_LABELS.get(resource, resource)


def _not_retrieved_text(resource: str, outcome: str) -> str:
    reason = "is not available from this EHR" if outcome == NOT_AVAILABLE else "could not be retrieved"
    return f"{_label(resource)} {reason}"


def medication_names(medications: Iterable[Dict[str, Any]]) -> List[str]:
    names = []
    for med in medications or []:
        concept = med.get("medicationCodeableConcept") or {}
        name = concept.get("text") or next((c.get("display") for c in concept.get("coding") or [] if c.get("display")), None)
        name = name or (med.get("medicationReference") or {}).get("display")
        if name:
            names.append(name)
    return names


def _medication_pattern(entry: str) -> re.Pattern:
    entry = entry.strip().lower()
    if entry.startswith("*"):
        return re.compile(r"\b[a-z]+" + re.escape(entry[1:]) + r"\b")
    return re.compile(r"\b" + re.escape(entry) + r"\b")


def matching_medications(names: List[str], related: List[str]) -> List[str]:
    patterns = [_medication_pattern(r) for r in related]
    return [n for n in names if any(p.search(n.lower()) for p in patterns)]


def _condition_codes(conditions: Iterable[Dict[str, Any]]) -> List[str]:
    codes = []
    for condition in conditions or []:
        for coding in (condition.get("code") or {}).get("coding") or []:
            system = str(coding.get("system", "")).lower()
            if "icd-10" in system or "icd10" in system:
                codes.append(str(coding.get("code", "")).upper())
    return codes


_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def _single_result_text(criterion: Any) -> str:
    """'HbA1c >= 6.5%: 7.0 % on 2026-09-19' (value and date of the single result)."""
    dates = _DATE.findall(criterion.details or "")
    when = f" on {dates[-1]}" if dates else ""
    return f"{criterion.criterion}: {criterion.value}{when}"


def _item(summary: str, source: str, status: Optional[str], evidence: List[str], window: str,
          caveats: List[str], **extra: Any) -> Dict[str, Any]:
    return {"summary": summary, "source": source, **review_fields(status),
            "details": {"evidence": evidence, "window": window, "caveats": caveats}, **extra}


# --------------------------------------------------------------------------- check 1

def abnormal_without_diagnosis(engine: SmartDiagnosticEngine, evaluations: Dict[str, Any],
                               patient_data: Any, all_status: Dict[str, str]) -> Dict[str, Any]:
    check = {"type": "abnormal_without_diagnosis", "title": CHECK_TITLES["abnormal_without_diagnosis"],
             "items": [], "not_checked": [],
             "scope": "Chronic conditions with chart criteria; acute conditions are shown as chart cards instead.",
             # Single abnormal results that need confirmation, shown collapsed
             "single_results": {"title": SINGLE_RESULTS_TITLE, "items": []}}
    if _status(all_status, "conditions") != RETRIEVED:
        check["not_checked"].append(
            f"{_not_retrieved_text('conditions', _status(all_status, 'conditions'))}; abnormal results "
            "could not be compared with it.")
        return check
    for tree_id, tree in engine.trees.items():
        criteria = tree["criteria"]
        evaluation = evaluations.get(tree_id)
        if (criteria.get("display") == "when_met" or evaluation is None
                or evaluation.finding not in ("consistent", "possible") or evaluation.known_condition):
            continue
        label = criteria.get("finding_label", tree.get("name", tree_id))
        source = criteria.get("source", "")
        lookback = max(int(i.get("lookback_days") or 0) for i in criteria["items"]) or None
        caveats = ["The problem list may record this condition under a code RealDiag does not map to it.",
                   NOT_VISIBLE]
        if evaluation.finding == "possible":
            results = [_single_result_text(c) for c in evaluation.criteria_met]
            check["single_results"]["items"].append(_item(
                summary=(f"{'; '.join(results)}: a single result above the {label} threshold. A repeat result "
                         f"is needed to meet criteria; consider repeating per {source}."),
                source=source, status=tree.get("status"),
                evidence=[f"{c.criterion}: {c.value}" + (f" ({c.details})" if c.details else "")
                          for c in evaluation.criteria_met],
                window=f"Results from the last {_years_text(lookback)}" if lookback else "Most recent results retrieved",
                caveats=["Not on the problem list.", NOT_VISIBLE], tree_id=tree_id, name=tree.get("name", tree_id)))
            continue
        check["items"].append(_item(
            summary=f"Results may be consistent with {label}, which is not on the problem list. Consider evaluation per {source}.",
            source=source, status=tree.get("status"),
            evidence=[f"{c.criterion}: {c.value}" + (f" ({c.details})" if c.details else "")
                      for c in evaluation.criteria_met],
            window=f"Results from the last {_years_text(lookback)}" if lookback else "Most recent results retrieved",
            caveats=caveats, tree_id=tree_id, name=tree.get("name", tree_id)))
    return check


# --------------------------------------------------------------------------- check 2

def diagnosis_without_support(engine: SmartDiagnosticEngine, evaluations: Dict[str, Any],
                              patient_data: Any, all_status: Dict[str, str]) -> Dict[str, Any]:
    check = {"type": "diagnosis_without_support", "title": CHECK_TITLES["diagnosis_without_support"],
             "items": [], "not_checked": [],
             "scope": "Problem-list conditions that map to a chronic condition with chart criteria and a "
                      "reviewed medication list; other conditions are not checked."}
    for resource in ("conditions", "medications"):
        if _status(all_status, resource) != RETRIEVED:
            check["not_checked"].append(
                f"{_not_retrieved_text(resource, _status(all_status, resource))}; problem-list conditions "
                "were not checked for supporting results or medication.")
            return check
    on_file = medication_names(patient_data.medications)
    for tree_id, tree in engine.trees.items():
        criteria = tree["criteria"]
        related = criteria.get("related_medications")
        if criteria.get("display") == "when_met" or not related or not criteria.get("known_condition"):
            continue
        known_text = known_condition(criteria, patient_data.conditions)
        if not known_text:
            continue
        evaluation = evaluations.get(tree_id)
        resources = {"labs" if i.get("resource", "lab") == "lab" else "vitals"
                     for i in criteria["items"] if i.get("resource", "lab") != "problem_list"}
        missing = [r for r in sorted(resources) if _status(all_status, r) != RETRIEVED]
        if missing:
            check["not_checked"].append(
                f"{known_text}: {', '.join(_not_retrieved_text(r, _status(all_status, r)) for r in missing)}; "
                "supporting results could not be checked.")
            continue
        if evaluation is not None and (evaluation.criteria_met or evaluation.finding):
            continue
        meds = matching_medications(on_file, related)
        if meds:
            continue
        lookback = max(int(i.get("lookback_days") or 0) for i in criteria["items"]) or VITAL_LOOKBACK_DAYS
        results = [f"{c.criterion}: {c.value}" for c in (evaluation.criteria_not_met if evaluation else []) if c.value]
        unreadable = [f"{c.criterion}: {c.value}" + (f" ({c.details})" if c.details else "")
                      for c in (evaluation.criteria_unknown if evaluation else []) if c.value]
        result_lines = []
        if results:
            result_lines.append("Results found, not meeting criteria: " + "; ".join(results))
        if unreadable:
            result_lines.append("Results found that could not be compared: " + "; ".join(unreadable))
        if not result_lines:
            result_lines.append(f"No relevant results in the {_years_text(lookback)} retrieved.")
        check["items"].append(_item(
            summary=(f"{known_text} is on the problem list, with no supporting result in the last "
                     f"{_years_text(lookback)} and no related medication on the medication list. Consider reviewing."),
            source=criteria.get("source", ""), status=tree.get("status"),
            evidence=[f"Problem list: {known_text}", *result_lines,
                      "Medication list: " + (", ".join(on_file) if on_file else "no active medications on file"),
                      "Related medications looked for: " + ", ".join(related)],
            window=f"Results from the last {_years_text(lookback)}; active medication list",
            caveats=["The condition may be resolved, controlled without medication, or treated with a "
                     "medication not on this list.", NOT_VISIBLE],
            tree_id=tree_id, name=tree.get("name", tree_id)))
    return check


# --------------------------------------------------------------------------- check 3

def _grade(rule: Dict[str, Any], age: int) -> Optional[str]:
    for band in rule.get("grades") or []:
        if (band.get("age_min") is None or age >= band["age_min"]) and (band.get("age_max") is None or age <= band["age_max"]):
            return band.get("grade")
    return None


def _population_text(rule: Dict[str, Any]) -> str:
    pop = rule.get("population") or {}
    who = {"female": "women", "male": "men"}.get(pop.get("sex"), "adults")
    ages = (f"aged {pop['age_min']} to {pop['age_max']}" if pop.get("age_max")
            else f"aged {pop.get('age_min')} or older")
    extra = []
    if pop.get("bmi_min"):
        extra.append(f"BMI {pop['bmi_min']} or more")
    if pop.get("smoking") == "ever":
        extra.append("who have ever smoked")
    return " ".join([who, ages] + extra)


def _latest_bmi(vitals: Iterable[Any]) -> Optional[Any]:
    readings = [v for v in vitals or [] if getattr(v, "code", None) == BMI_LOINC and getattr(v, "value", None) is not None]
    return max(readings, key=lambda v: _naive(v.effective_date) or datetime.min) if readings else None


def _find_evidence(option: Dict[str, Any], data: Dict[str, Any], now: datetime) -> Optional[str]:
    """A matching record within the option's window, described for display."""
    days = option.get("within_years")
    cutoff = now - timedelta(days=round(days * 365.25)) if days else None
    kind = option["kind"]
    if kind in ("lab", "vital"):
        codes = set(option.get("loinc") or [])
        for result in data["labs" if kind == "lab" else "vitals"]:
            when = _naive(getattr(result, "effective_date", None))
            if getattr(result, "code", None) in codes and (cutoff is None or (when and when >= cutoff)):
                return f"{getattr(result, 'display', None) or option['label']} on {_date_text(when)}"
        return None
    keywords = [k.lower() for k in option.get("keywords") or []]
    records = data["procedures" if kind == "procedure" else "imaging_studies"]
    for record in records:
        text = " ".join(f"{k}: {v}" for k, v in (record.dict() if hasattr(record, "dict") else dict(record)).items()
                        if isinstance(v, str)).lower()
        when = _naive(getattr(record, "date", None))
        if any(k in text for k in keywords) and (cutoff is None or (when and when >= cutoff)):
            name = getattr(record, "procedure_name", None) or getattr(record, "modality", None) or option["label"]
            return f"{name} on {_date_text(when)}"
    return None


def overdue_screenings(patient_data: Any, history: Any, smoking: Optional[Dict[str, Any]],
                       all_status: Dict[str, str], now: Optional[datetime] = None,
                       rules: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    now = now or datetime.utcnow()
    check = {"type": "overdue_screening", "title": CHECK_TITLES["overdue_screening"], "items": [],
             "not_checked": [], "scope": "USPSTF grade A and B screening recommendations "
                                         "(backend/screening/uspstf_rules.yml)."}
    age = patient_data.age
    sex = str(patient_data.gender or "").lower()
    if age is None:
        check["not_checked"].append("Age is unknown; screenings were not checked.")
        return check
    data = {
        "labs": list(patient_data.labs or []), "vitals": list(patient_data.vitals or []),
        "procedures": list(getattr(history, "procedures", []) or []),
        "imaging_studies": list(getattr(history, "imaging_studies", []) or []),
    }
    condition_codes = _condition_codes(patient_data.conditions)
    for rule in rules if rules is not None else load_screening_rules():
        pop = rule.get("population") or {}
        if (pop.get("age_min") is not None and age < pop["age_min"]) or (
                pop.get("age_max") is not None and age > pop["age_max"]):
            continue
        title, source = rule["title"], rule["source"]["citation"]
        if pop.get("sex"):
            if sex not in ("male", "female"):
                check["not_checked"].append(f"{title}: sex is not recorded.")
                continue
            if sex != pop["sex"]:
                continue
        caveats = list(rule.get("caveats") or [])
        # Known disease takes the patient out of the screened population
        if rule.get("exclude_conditions"):
            if _status(all_status, "conditions") == RETRIEVED:
                if any(code.startswith(p.upper()) for code in condition_codes for p in rule["exclude_conditions"]):
                    continue
            else:
                caveats.append("Problem list not retrieved; known disease was not checked.")
        if rule.get("exclude_procedures"):
            if _status(all_status, "procedures") == RETRIEVED:
                words = [w.lower() for w in rule["exclude_procedures"]]
                if any(any(w in (p.procedure_name or "").lower() for w in words) for p in data["procedures"]):
                    continue
            else:
                caveats.append(f"Procedures not retrieved; {', '.join(rule['exclude_procedures'])} was not checked.")

        grade = _grade(rule, age)
        cite = f"{source} (Grade {grade})" if grade else source
        population = _population_text(rule)

        # Population criteria that need data RealDiag may not have
        if pop.get("bmi_min"):
            bmi = _latest_bmi(data["vitals"])
            if bmi is None:
                check["items"].append(_item(
                    summary=(f"{title} may apply: it is recommended for {population}, and no BMI was found in the "
                             f"last {_years_text(VITAL_LOOKBACK_DAYS)}. Consider checking BMI, per {cite}."),
                    source=source, status=rule.get("status"),
                    evidence=["No BMI result (LOINC 39156-5) in the vital signs retrieved."],
                    window=f"Vital signs from the last {_years_text(VITAL_LOOKBACK_DAYS)}",
                    caveats=caveats + [NOT_VISIBLE], rule_id=rule["id"], name=title, missing_data=["BMI"]))
                continue
            if bmi.value < pop["bmi_min"]:
                continue
        unavailable = list(rule.get("needs_unavailable") or [])
        if pop.get("smoking") == "ever":
            status = (smoking or {}).get("status")
            if status == "never":
                continue
            if status not in ("current", "former"):
                why = ("smoking status could not be retrieved" if _status(all_status, "smoking_status") not in (RETRIEVED,)
                       else "no smoking status is recorded" if smoking is None else "smoking status is recorded as unknown")
                check["items"].append(_item(
                    summary=(f"{title} may apply: it is recommended for {population}, and {why}. "
                             f"Consider whether it applies, per {cite}."),
                    source=source, status=rule.get("status"),
                    evidence=["Smoking status (LOINC 72166-2): not available."] +
                             [f"Also needed and not available: {u}." for u in unavailable],
                    window="Most recent smoking status on file",
                    caveats=caveats, rule_id=rule["id"], name=title,
                    missing_data=["smoking status"] + unavailable))
                continue
            caveats.insert(0, f"Smoking status: {smoking.get('text') or status}"
                              + (f" ({smoking['date']})" if smoking.get("date") else "") + ".")

        options = [o for o in rule.get("evidence") or []
                   if (o.get("age_min") is None or age >= o["age_min"]) and (o.get("age_max") is None or age <= o["age_max"])]
        found = None
        unretrieved = []
        for option in options:
            resource = EVIDENCE_RESOURCE[option["kind"]]
            if _status(all_status, resource) != RETRIEVED:
                if resource not in unretrieved:
                    unretrieved.append(resource)
                continue
            found = _find_evidence(option, data, now)
            if found:
                break
        if found:
            continue
        checked = [o for o in options if EVIDENCE_RESOURCE[o["kind"]] not in unretrieved]
        if not checked:
            check["not_checked"].append(
                f"{title}: {', '.join(_not_retrieved_text(r, _status(all_status, r)) for r in unretrieved)}.")
            continue
        looked_for = []
        for o in checked:
            window = f"within {o['within_years']} year{'s' if o['within_years'] != 1 else ''}" if o.get("within_years") else "ever"
            entry = f"{o['label']} ({window})"
            if entry not in looked_for:
                looked_for.append(entry)
            retrieved_days = EVIDENCE_WINDOW_DAYS[o["kind"]]
            wanted_days = round(o["within_years"] * 365.25) if o.get("within_years") else None
            if wanted_days is None or wanted_days > retrieved_days + 30:
                note = f"Only the last {_years_text(retrieved_days)} of {_label(EVIDENCE_RESOURCE[o['kind']]).lower()} were retrieved."
                if note not in caveats:
                    caveats.append(note)
        for resource in unretrieved:
            caveats.append(f"{_not_retrieved_text(resource, _status(all_status, resource))}; it was not checked.")
        eligibility = (f" Eligibility also depends on {' and '.join(u.split(' (')[0] for u in unavailable)}, "
                       "which RealDiag cannot see.") if unavailable else ""
        check["items"].append(_item(
            summary=(f"{title} may be due{' if eligible' if unavailable else ''}: no record of "
                     f"{'; '.join(looked_for)}.{eligibility} Consider screening per {cite}."),
            source=source, status=rule.get("status"),
            evidence=[f"Recommended for {population}."] + [f"Looked for {x}: not found." for x in looked_for]
                     + [f"Not available in RealDiag: {u}." for u in unavailable],
            window=("Lab results and procedures/imaging from the last "
                    f"{_years_text(SCREENING_LAB_LOOKBACK_DAYS)}; vital signs from the last "
                    f"{_years_text(VITAL_LOOKBACK_DAYS)}"),
            caveats=caveats + [NOT_VISIBLE], rule_id=rule["id"], name=title,
            missing_data=unavailable, url=rule["source"].get("url")))
    return check


# --------------------------------------------------------------------------- all checks

def possible_missed_items(engine: SmartDiagnosticEngine, patient_data: Any, history: Any,
                          smoking: Optional[Dict[str, Any]], all_status: Dict[str, str],
                          now: Optional[datetime] = None) -> Dict[str, Any]:
    evaluations = {}
    for tree_id in engine.trees:
        try:
            evaluations[tree_id] = engine.evaluate_tree(tree_id, patient_data, now)
        except Exception:
            evaluations[tree_id] = None
    checks = [
        abnormal_without_diagnosis(engine, evaluations, patient_data, all_status),
        diagnosis_without_support(engine, evaluations, patient_data, all_status),
        overdue_screenings(patient_data, history, smoking, all_status, now),
    ]
    return {
        "title": "Possible missed items",
        "notice": ("Possible items to consider, from chart data only. They may already be addressed elsewhere; "
                   "none is a finding that something was missed."),
        "checks": checks,
        "item_count": sum(len(c["items"]) for c in checks),
        "single_result_count": sum(len((c.get("single_results") or {}).get("items", [])) for c in checks),
    }
