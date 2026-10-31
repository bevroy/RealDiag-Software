"""
Smart Diagnostic Engine with EHR Integration

Evaluates the `criteria` section of each decision tree against patient data
from FHIR/EHR systems (labs and vital signs) and reports which criteria are
met, not met or unknown. Decision support only: outputs describe what the
findings may be consistent with and cite the tree's source; they never issue
treatment orders.

Usage:
    from services.fhir_client import FHIRClient, PatientData
    from services.smart_diagnostic_engine import SmartDiagnosticEngine

    engine = SmartDiagnosticEngine()
    patient_data = fhir_client.get_patient_data(
        "patient123", observation_requirements=engine.observation_requirements())
    results = engine.evaluate_patient(patient_data=patient_data)

Criteria format (documented in docs/CLINICAL_CONTENT_REVIEW.md; checked by
backend/scripts/validate_rules.py):

    criteria:
      finding_label: diabetes mellitus
      source: ADA Standards of Care in Diabetes-2026, Section 2
      display: when_met | when_found | always
                                       # when_met: acute, shown when a criterion is met
                                       # when_found: chronic, shown when consistent/possible
      finding_template: "..."           # optional wording; {label} {source} {screens}
      probability: met_over_all | met_over_known
      suggest_when: {count_met: 1, group: <optional>}
      confirm: {min_abnormal_results: 2}            # optional
      known_condition: {icd10_prefixes: [...], snomed: [...]}   # optional
      suppressed_by: [<tree_id>, ...]   # optional: another tree's known_condition on the
                                       # problem list means this finding is not reported as
                                       # missing (e.g. diabetes suppresses prediabetes)
      severity_default: moderate
      severity: [ ...rules... ]
      next_steps: [ ...decision-support text... ]
      items: [ ...criteria items... ]
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from types import SimpleNamespace
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from .clinical_review import review_fields
from .complaint_matching import match_terms
from .fhir_client import PatientData, RETRIEVED
from .lab_units import analyte_for, analyte_name, analyte_title, to_canonical

logger = logging.getLogger(__name__)

TREES_PATH = Path(__file__).resolve().parents[1] / "trees"

# between: low <= v <= high. at_least_below: low <= v < high, so a range can end exactly
# where the next condition's threshold starts (e.g. prediabetes up to the diabetes cutoff).
OPERATORS = (">", ">=", "<", "<=", "between", "at_least_below", "outside", "above_ref_high", "below_ref_low")
SEVERITY_RANK = {"critical": 4, "high": 3, "moderate": 2, "low": 1, "unknown": 0}


class CriteriaStatus(Enum):
    """Status of diagnostic criteria evaluation."""
    PRESENT = "present"  # Criterion is met
    ABSENT = "absent"  # Criterion is not met
    UNKNOWN = "unknown"  # Cannot determine (missing data)


@dataclass
class CriterionEvaluation:
    """Result of evaluating a single diagnostic criterion."""
    criterion: str
    status: CriteriaStatus
    value: Optional[Any] = None
    expected: Optional[str] = None
    details: Optional[str] = None
    source: Optional[str] = None


@dataclass
class DiagnosisEvaluation:
    """Complete evaluation of a diagnosis against patient data."""
    diagnosis_id: str
    diagnosis_label: str
    family: str
    probability: float  # 0-1 score
    criteria_met: List[CriterionEvaluation]
    criteria_not_met: List[CriterionEvaluation]
    criteria_unknown: List[CriterionEvaluation]
    recommendations: List[str]
    missing_tests: List[str]
    severity: str = "moderate"  # low, moderate, high, critical, unknown, not rated
    # "evaluated" | "insufficient data" | "evaluation failed"
    evaluation_status: str = "evaluated"
    status_reason: Optional[str] = None
    # Findings shown for context only; they never raise the probability
    supporting_findings: List[CriterionEvaluation] = field(default_factory=list)
    severity_reason: Optional[str] = None
    # "consistent" | "possible" (needs a repeat result) | None
    finding: Optional[str] = None
    # Condition already on the patient's problem list
    known_condition: bool = False
    known_condition_text: Optional[str] = None
    # "when_met" (acute: shown when a criterion is met) | "when_found" (chronic:
    # shown when consistent/possible) | "always"
    display: str = "always"
    sources: List[str] = field(default_factory=list)
    review_status: Optional[str] = None
    review_status_label: Optional[str] = None
    # A result exists but could not be compared (unit missing/unrecognised,
    # no reference range): the test was done, so the gap must be shown.
    has_unusable_results: bool = False
    # Terms from the tree's complaint_terms that today's complaint matched
    complaint_matches: List[str] = field(default_factory=list)


@dataclass
class EncounterAssessment:
    """Evaluations to show plus warnings about conditions that could not be assessed."""
    evaluations: List[DiagnosisEvaluation]
    warnings: List[str]


# --------------------------------------------------------------------------- data access

def _naive_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def _sort_key(result) -> datetime:
    return _naive_utc(result.effective_date) or datetime.min


def _results(patient_data: PatientData, item: Dict[str, Any], now: datetime) -> List[Any]:
    """All results for the item's LOINC codes (within its lookback), newest first."""
    codes = set(item["loinc"])
    pool = patient_data.labs if item.get("resource", "lab") == "lab" else patient_data.vitals
    results = [r for r in pool if r.code in codes]
    lookback = item.get("lookback_days")
    if lookback:
        since = now - timedelta(days=int(lookback))
        results = [r for r in results if (_naive_utc(r.effective_date) or datetime.min) >= since]
    return sorted(results, key=_sort_key, reverse=True)


# --------------------------------------------------------------------------- one result vs one item

@dataclass
class _Check:
    """Outcome of comparing one result with one criterion."""
    met: Optional[bool]           # None = could not compare (see problem)
    problem: Optional[str] = None
    canonical: Optional[float] = None
    reason: Optional[str] = None  # explanation (reference-range operators)
    expected: Optional[str] = None
    severity: str = "unknown"     # band for reference-range operators


class _ItemEvaluator:
    """Compares results against one `criteria.items[]` entry."""

    def __init__(self, item: Dict[str, Any]):
        self.item = item
        self.operator = item["operator"]
        self.analyte = item.get("analyte") or analyte_for(item["loinc"][0])
        self.unit_check = item.get("unit_check", True)

    def check(self, result) -> _Check:
        if self.operator in ("above_ref_high", "below_ref_low"):
            return self._check_reference(result)
        canonical = result.value
        if self.unit_check:
            canonical, problem = to_canonical(self.analyte, result.value, result.unit)
            if problem:
                return _Check(met=None, problem=problem)
        threshold = self.item.get("value")
        op = self.operator
        if op == ">":
            met = canonical > threshold
        elif op == ">=":
            met = canonical >= threshold
        elif op == "<":
            met = canonical < threshold
        elif op == "<=":
            met = canonical <= threshold
        elif op == "between":
            met = threshold[0] <= canonical <= threshold[1]
        elif op == "at_least_below":
            met = threshold[0] <= canonical < threshold[1]
        elif op == "outside":
            met = canonical < threshold[0] or canonical > threshold[1]
        else:  # pragma: no cover - the validator rejects unknown operators
            raise ValueError(f"unknown operator {op}")
        return _Check(met=met, canonical=canonical)

    def _check_reference(self, result) -> _Check:
        """Compare with the lab's own reference limit, after unit conversion."""
        name, title = analyte_name(self.analyte), analyte_title(self.analyte)
        upper = self.operator == "above_ref_high"
        bound = "upper" if upper else "lower"
        expected_unknown = f"lab {bound} reference limit"

        value, problem = to_canonical(self.analyte, result.value, result.unit)
        if problem:
            return _Check(met=None, problem=problem, expected=expected_unknown)
        limit = (result.reference_range or {}).get("high" if upper else "low")
        if limit is None:
            return _Check(met=None, problem=f"the lab reported no {bound} reference limit for {name}",
                          expected=expected_unknown)
        ref_unit = getattr(result, "reference_unit", None)
        if ref_unit:
            limit_canonical, ref_problem = to_canonical(self.analyte, limit, ref_unit)
            if ref_problem:
                return _Check(met=None, problem=f"reference range unit '{ref_unit}' is not recognised",
                              expected=expected_unknown)
        else:
            limit_canonical, _ = to_canonical(self.analyte, limit, result.unit)
        if limit_canonical <= 0:
            return _Check(met=None, problem=f"the lab's {bound} reference limit is zero or negative",
                          expected=expected_unknown)

        expected = f"{'>' if upper else '<'} {limit} {ref_unit or result.unit} (lab {bound} reference limit)"
        if upper:
            multiple = value / limit_canonical
            if multiple <= 1:
                return _Check(met=False, canonical=value, expected=expected, severity="low",
                              reason=f"{title} at or below the lab's upper reference limit.")
            return _Check(met=True, canonical=value, expected=expected, severity=self._band(multiple),
                          reason=f"{title} {multiple:.1f}x the lab's upper reference limit.")
        if value >= limit_canonical:
            return _Check(met=False, canonical=value, expected=expected, severity="low",
                          reason=f"{title} at or above the lab's lower reference limit.")
        return _Check(met=True, canonical=value, expected=expected, severity="moderate",
                      reason=f"{title} below the lab's lower reference limit.")

    def _band(self, multiple: float) -> str:
        bands = self.item.get("severity_multiples") or {}
        if "critical" in bands and multiple >= bands["critical"]:
            return "critical"
        if "high" in bands and multiple >= bands["high"]:
            return "high"
        return "moderate"

    def value_text(self, result, check: Optional[_Check]) -> str:
        template = self.item.get("value_format", "{value} {unit}")
        text = template.format(value=result.value, unit=result.unit or "").strip()
        if (self.item.get("show_converted") and check is not None and check.canonical is not None
                and (result.unit or "").strip().lower() != str(self.item.get("unit", "")).strip().lower()):
            text += f" (= {check.canonical:.0f} {self.item.get('unit')})"
        return text

    def fill(self, template: Optional[str], result=None, check: Optional[_Check] = None,
             problem: Optional[str] = None) -> Optional[str]:
        if template is None:
            return None
        names = self.item.get("code_names") or {}
        prelim = ""
        if result is not None and self.item.get("mark_preliminary") and getattr(result, "status", "") == "preliminary":
            prelim = " (PRELIMINARY result)"
        return template.format(
            code_name=names.get(getattr(result, "code", None),
                                analyte_name(self.analyte) if self.analyte else self.item["label"]),
            reason=(check.reason if check else "") or "",
            problem=problem or "",
            prelim=prelim,
        )


@dataclass
class _ItemResult:
    item: Dict[str, Any]
    criterion: Optional[CriterionEvaluation]
    status: Optional[CriteriaStatus]       # None = not applicable / omitted
    partial: bool = False
    abnormal_count: int = 0
    problem: Optional[str] = None
    not_measured: bool = False
    check: Optional[_Check] = None
    missing_test: Optional[str] = None


def _evaluate_item(item: Dict[str, Any], patient_data: PatientData, now: datetime) -> _ItemResult:
    sex = (item.get("applies_to") or {}).get("sex")
    if sex and str(patient_data.gender or "").lower() != sex:
        return _ItemResult(item=item, criterion=None, status=None)

    if item.get("resource") == "problem_list":
        return _evaluate_problem_list(item, patient_data)

    ev = _ItemEvaluator(item)
    label = item["label"]
    source = item.get("source")
    results = _results(patient_data, item, now)

    if not results:
        if item.get("role", "core") == "supporting":
            return _ItemResult(item=item, criterion=None, status=None, not_measured=True)
        return _ItemResult(
            item=item, status=CriteriaStatus.UNKNOWN, not_measured=True, missing_test=item.get("missing_test"),
            criterion=CriterionEvaluation(criterion=item.get("unknown_label", label), status=CriteriaStatus.UNKNOWN,
                                          details=item.get("details_unknown"), source=source),
        )

    if item.get("aggregate") == "daily_mean":
        return _evaluate_daily_mean(item, ev, results)

    min_occ = int(item.get("min_occurrences", 1))
    min_span = int(item.get("min_span_days", 0))
    if min_occ > 1 or min_span > 0 or item.get("count_all"):
        # count_all: every abnormal result in the window counts (e.g. two
        # separate HbA1c results confirm diabetes)
        return _evaluate_repeated(item, ev, results, min_occ, min_span)

    # Single-result criterion: the most recent result, or the most concerning
    # of each code's most recent result.
    if item.get("select") == "most_concerning_per_code":
        latest_per_code: Dict[str, Any] = {}
        for r in results:
            latest_per_code.setdefault(r.code, r)
        ordered = [latest_per_code[c] for c in item["loinc"] if c in latest_per_code]
        checks = [(r, ev.check(r)) for r in ordered]
        result, check = max(checks, key=lambda rc: SEVERITY_RANK[rc[1].severity])
    else:
        result = results[0]
        check = ev.check(result)

    value = ev.value_text(result, check)
    expected = check.expected or item.get("expected")
    if check.met is None:
        details = ev.fill(item.get("details_unusable", "{problem}."), result, check, check.problem)
        return _ItemResult(
            item=item, status=CriteriaStatus.UNKNOWN, problem=check.problem, check=check,
            missing_test=item.get("missing_test_unusable", item.get("missing_test")),
            criterion=CriterionEvaluation(criterion=item.get("unknown_label", label), status=CriteriaStatus.UNKNOWN,
                                          value=value, expected=expected, details=details, source=source),
        )
    status = CriteriaStatus.PRESENT if check.met else CriteriaStatus.ABSENT
    if check.met:
        details = ev.fill(item.get("details_met"), result, check)
    else:
        details = ev.fill(item.get("details_not_met"), result, check)
        expected = check.expected or item.get("expected_not_met", item.get("expected"))
    return _ItemResult(
        item=item, status=status, check=check, abnormal_count=1 if check.met else 0,
        criterion=CriterionEvaluation(criterion=label, status=status, value=value, expected=expected,
                                      details=details, source=source),
    )


def _evaluate_repeated(item, ev: _ItemEvaluator, results, min_occ: int, min_span: int) -> _ItemResult:
    """Criteria that need repeat abnormal results (e.g. 2 readings, >= 90 days apart)."""
    label, source = item["label"], item.get("source")
    qualifying, usable, problems = [], [], []
    for r in results:
        check = ev.check(r)
        if check.met is None:
            problems.append(check.problem)
            continue
        usable.append((r, check))
        if check.met:
            qualifying.append((r, check))

    if not usable:
        return _ItemResult(
            item=item, status=CriteriaStatus.UNKNOWN, problem=problems[0],
            missing_test=item.get("missing_test_unusable", item.get("missing_test")),
            criterion=CriterionEvaluation(criterion=item.get("unknown_label", label), status=CriteriaStatus.UNKNOWN,
                                          expected=item.get("expected"), details=f"{problems[0]}.", source=source),
        )
    if not qualifying:
        latest, latest_check = usable[0]
        return _ItemResult(
            item=item, status=CriteriaStatus.ABSENT, check=latest_check,
            criterion=CriterionEvaluation(criterion=label, status=CriteriaStatus.ABSENT,
                                          value=ev.value_text(latest, latest_check),
                                          expected=item.get("expected"), source=source),
        )

    dates = [_naive_utc(r.effective_date) for r, _ in qualifying if r.effective_date]
    if item.get("distinct_days") and dates:
        count = len({d.date() for d in dates})
    else:
        count = len(qualifying)
    span = (max(dates) - min(dates)).days if len(dates) > 1 else 0
    full = count >= min_occ and span >= min_span
    listing = ", ".join(
        f"{ev.value_text(r, c)} ({_naive_utc(r.effective_date).date().isoformat() if r.effective_date else 'date unknown'})"
        for r, c in qualifying[:6]
    )
    need = []
    if count < min_occ:
        need.append(f"{count} of {min_occ} required abnormal results")
    if span < min_span:
        need.append(f"{span} of {min_span} required days between first and last abnormal result")
    details = f"Abnormal results: {listing}." + ("" if full else f" Confirmation pending: {'; '.join(need)}.")
    first, first_check = qualifying[0]
    return _ItemResult(
        item=item, status=CriteriaStatus.PRESENT, partial=not full, abnormal_count=count, check=first_check,
        criterion=CriterionEvaluation(criterion=label, status=CriteriaStatus.PRESENT,
                                      value=ev.value_text(first, first_check), expected=item.get("expected"),
                                      details=details, source=source),
    )


def _evaluate_problem_list(item: Dict[str, Any], patient_data: PatientData) -> _ItemResult:
    """Criterion met by a condition on the problem list (e.g. known diabetes)."""
    label, source = item["label"], item.get("source")
    status = (patient_data.retrieval_status or {}).get("conditions", RETRIEVED)
    match = known_condition({"known_condition": item}, patient_data.conditions)
    if match:
        return _ItemResult(item=item, status=CriteriaStatus.PRESENT, abnormal_count=1, criterion=CriterionEvaluation(
            criterion=label, status=CriteriaStatus.PRESENT, value=match, expected="on the problem list",
            details=item.get("details_met"), source=source))
    if status != RETRIEVED:
        return _ItemResult(item=item, status=CriteriaStatus.UNKNOWN, problem="problem list could not be retrieved",
                           criterion=CriterionEvaluation(criterion=label, status=CriteriaStatus.UNKNOWN,
                                                         details="Problem list could not be retrieved.", source=source))
    return _ItemResult(item=item, status=CriteriaStatus.ABSENT, criterion=CriterionEvaluation(
        criterion=label, status=CriteriaStatus.ABSENT, value="not on the problem list",
        expected="on the problem list", source=source))


def _evaluate_daily_mean(item, ev: _ItemEvaluator, results) -> _ItemResult:
    """Average readings per day (one occasion), then average the most recent
    occasions; e.g. BP classified on the average of >= 2 readings on >= 2 occasions."""
    label, source = item["label"], item.get("source")
    min_days, max_days = int(item.get("min_days", 2)), int(item.get("max_days", 3))
    by_day: Dict[Any, List[float]] = {}
    problems = []
    for r in results:   # newest first
        canonical, problem = (to_canonical(ev.analyte, r.value, r.unit) if ev.unit_check else (r.value, None))
        if problem:
            problems.append(problem)
            continue
        day = (_naive_utc(r.effective_date) or datetime.min).date()
        by_day.setdefault(day, []).append(canonical)
    if not by_day:
        return _ItemResult(
            item=item, status=CriteriaStatus.UNKNOWN, problem=problems[0] if problems else None,
            missing_test=item.get("missing_test"),
            criterion=CriterionEvaluation(criterion=item.get("unknown_label", label), status=CriteriaStatus.UNKNOWN,
                                          expected=item.get("expected"),
                                          details=f"{problems[0]}." if problems else None, source=source))

    days = sorted(by_day, reverse=True)[:max_days]
    daily = [(d, sum(by_day[d]) / len(by_day[d]), len(by_day[d])) for d in days]
    mean = sum(m for _, m, _ in daily) / len(daily)
    readings = sum(n for _, _, n in daily)
    met = ev.check(SimpleNamespace(value=mean, unit=ev.item.get("unit"), reference_range=None,
                                   reference_unit=None, code=None)).met
    unit = item.get("unit", "")
    value = f"{mean:.0f} {unit} (average of {readings} readings on {len(daily)} day{'s' if len(daily) != 1 else ''})"
    per_day = ", ".join(f"{d.isoformat()}: {m:.0f} ({n} reading{'s' if n != 1 else ''})" for d, m, n in daily)
    enough = len(daily) >= min_days
    if not met:
        return _ItemResult(item=item, status=CriteriaStatus.ABSENT, criterion=CriterionEvaluation(
            criterion=label, status=CriteriaStatus.ABSENT, value=value, expected=item.get("expected"),
            details=f"Daily averages: {per_day}.", source=source))
    details = f"Daily averages: {per_day}."
    if not enough:
        details += f" Confirmation pending: readings on {len(daily)} of {min_days} required occasions."
    return _ItemResult(item=item, status=CriteriaStatus.PRESENT, partial=not enough, abnormal_count=1,
                       criterion=CriterionEvaluation(criterion=label, status=CriteriaStatus.PRESENT, value=value,
                                                     expected=item.get("expected"), details=details, source=source))


# --------------------------------------------------------------------------- tree-level evaluation

def known_condition(criteria: Dict[str, Any], conditions: List[Dict[str, Any]]) -> Optional[str]:
    """Display name of a matching problem-list condition, if any."""
    spec = criteria.get("known_condition") or {}
    prefixes = [str(p).upper() for p in spec.get("icd10_prefixes", [])]
    snomed = {str(s) for s in spec.get("snomed", [])}
    for condition in conditions or []:
        code = condition.get("code") or {}
        for coding in code.get("coding") or []:
            system = str(coding.get("system", "")).lower()
            value = str(coding.get("code", ""))
            if prefixes and ("icd-10" in system or "icd10" in system) and any(value.upper().startswith(p) for p in prefixes):
                return code.get("text") or coding.get("display") or value
            if snomed and "snomed" in system and value in snomed:
                return code.get("text") or coding.get("display") or value
    return None


def suppressing_condition(trees: Dict[str, Dict[str, Any]], criteria: Dict[str, Any],
                          conditions: List[Dict[str, Any]]) -> Optional[str]:
    """Problem-list condition that suppresses this tree's finding, if any.

    `criteria.suppressed_by` names other trees; a problem-list entry matching
    one of their known_condition codes suppresses the finding (e.g. a
    diabetes diagnosis suppresses "prediabetes not on the problem list").
    """
    for tree_id in criteria.get("suppressed_by") or []:
        other = (trees.get(tree_id) or {}).get("criteria") or {}
        text = known_condition(other, conditions)
        if text:
            return text
    return None


def _count_met(item_results: List[_ItemResult], group: Optional[str]) -> int:
    return sum(
        1 for r in item_results
        if r.status == CriteriaStatus.PRESENT and not r.partial
        and r.item.get("role", "core") == "core"
        and (group is None or r.item.get("group") == group)
    )


def _groups_met(item_results: List[_ItemResult], groups: List[str]) -> bool:
    """Every group has at least one fully met core item (e.g. DKA: D and K and A)."""
    return all(_count_met(item_results, g) >= 1 for g in groups)


def _screens_positive(rule: Dict[str, Any], item_results: List[_ItemResult]) -> List[str]:
    """Labels of the `any` sub-rules that hold, e.g. ["SIRS >= 2"]."""
    return [r.get("label", "") for r in rule.get("any", []) if _rule_holds(r, item_results) and r.get("label")]


def _rule_holds(rule: Dict[str, Any], item_results: List[_ItemResult]) -> bool:
    """suggest_when rule: {count_met, group} | {all_groups: [...]} | {any: [rules]}."""
    if "any" in rule:
        return any(_rule_holds(r, item_results) for r in rule["any"])
    if "all_groups" in rule:
        return _groups_met(item_results, rule["all_groups"])
    return _count_met(item_results, rule.get("group")) >= rule.get("count_met", 1)


def _apply_severity(criteria: Dict[str, Any], item_results: List[_ItemResult]) -> Tuple[str, Optional[str]]:
    """Run severity rules in order; a rule that fires overrides earlier ones."""
    severity = criteria.get("severity_default", "not rated")
    reason = criteria.get("severity_default_reason")
    by_id = {r.item["id"]: r for r in item_results}
    for rule in criteria.get("severity") or []:
        kind = rule["type"]
        r = by_id.get(rule.get("item"))
        if kind == "reference_multiple":
            if r is None or r.not_measured or r.status is None:
                severity, reason = "unknown", rule.get("not_measured_reason")
            elif r.problem:
                severity, reason = "unknown", f"Severity unknown: {r.problem}."
            else:
                severity, reason = r.check.severity, r.check.reason
        elif kind == "count_met":
            if _count_met(item_results, rule.get("group")) >= rule["at_least"]:
                severity = rule["level"]
                reason = rule.get("reason", reason)
        elif kind == "unusable":
            if r is not None and r.problem:
                severity, reason = rule.get("level", "unknown"), f"Severity unknown: {r.problem}."
        elif kind == "value":
            if r is not None and r.check is not None and r.check.canonical is not None and not r.problem:
                v, threshold = r.check.canonical, rule["value"]
                hit = {">": v > threshold, ">=": v >= threshold, "<": v < threshold, "<=": v <= threshold}[rule["op"]]
                if hit:
                    severity = rule["level"]
                    reason = rule["reason"].format(value=v) if rule.get("reason") else reason
        elif kind == "all_groups":
            if _groups_met(item_results, rule["groups"]):
                severity = rule["level"]
                reason = rule.get("reason", reason)
        elif kind == "any_met":
            if any(by_id.get(i) is not None and by_id[i].status == CriteriaStatus.PRESENT and not by_id[i].partial
                   for i in rule["items"]):
                severity = rule["level"]
                reason = rule.get("reason", reason)
    return severity, reason


def evaluate_tree(tree: Dict[str, Any], patient_data: PatientData, now: Optional[datetime] = None) -> DiagnosisEvaluation:
    """Evaluate one tree's criteria against the patient's data (no display filtering)."""
    now = now or datetime.utcnow()
    criteria = tree["criteria"]
    item_results = [_evaluate_item(item, patient_data, now) for item in criteria["items"]]

    met, not_met, unknown, supporting, missing_tests = [], [], [], [], []
    for r in item_results:
        if r.status is None:
            continue
        if r.item.get("role", "core") == "supporting":
            supporting.append(r.criterion)
            continue
        {CriteriaStatus.PRESENT: met, CriteriaStatus.ABSENT: not_met,
         CriteriaStatus.UNKNOWN: unknown}[r.status].append(r.criterion)
        if r.status == CriteriaStatus.UNKNOWN and r.missing_test and r.missing_test not in missing_tests:
            missing_tests.append(r.missing_test)

    if criteria.get("probability", "met_over_known") == "met_over_all":
        total = len(met) + len(not_met) + len(unknown)
        probability = len(met) / total if total else 0.0
    else:
        probability = len(met) / max(len(met) + len(not_met), 1)

    severity, severity_reason = _apply_severity(criteria, item_results)

    # Finding: "consistent" when the suggestion rule holds; "possible" when an
    # abnormal result still needs confirmation by a repeat result.
    suggest = criteria.get("suggest_when") or {"count_met": 1}
    confirm = criteria.get("confirm") or {}
    abnormal_total = sum(r.abnormal_count for r in item_results if r.item.get("role", "core") == "core")
    finding = None
    if confirm.get("min_abnormal_results"):
        if abnormal_total >= confirm["min_abnormal_results"]:
            finding = "consistent"
        elif abnormal_total >= 1:
            finding = "possible"
    elif _rule_holds(suggest, item_results):
        finding = "consistent"
    elif any(r.partial for r in item_results):
        finding = "possible"

    known_text = known_condition(criteria, patient_data.conditions)
    label = criteria.get("finding_label", tree.get("name", tree["tree_id"]))
    source = criteria.get("source", "")
    recommendations: List[str] = []
    if known_text:
        recommendations.append(f"Known condition on the problem list ({known_text}).")
    if finding == "consistent":
        template = criteria.get("finding_template")
        if template:
            screens = " and ".join(_screens_positive(suggest, item_results))
            recommendations.append(template.format(label=label, source=source, screens=screens))
        else:
            prefix = "Current findings consistent with" if known_text else "Findings consistent with"
            recommendations.append(f"{prefix} {label}; consider evaluation per {source}.")
        recommendations.extend(criteria.get("next_steps") or [])
    elif finding == "possible":
        need = confirm.get("min_abnormal_results")
        detail = f" ({abnormal_total} of {need} required abnormal results)" if need else ""
        recommendations.append(f"Possible {label}{detail}; confirmation requires a repeat result per {source}.")
    if missing_tests:
        recommendations.append(f"Data needed to evaluate: {', '.join(missing_tests)}")

    sources: List[str] = []
    for s in [source] + [r.item.get("source") for r in item_results if r.status is not None]:
        if s and s not in sources:
            sources.append(s)

    return DiagnosisEvaluation(
        diagnosis_id=tree["tree_id"],
        diagnosis_label=tree.get("name", tree["tree_id"]),
        family=str(tree.get("family", "")).lower().replace(" ", "_"),
        probability=probability,
        criteria_met=met,
        criteria_not_met=not_met,
        criteria_unknown=unknown,
        recommendations=recommendations,
        missing_tests=missing_tests,
        severity=severity,
        supporting_findings=supporting,
        severity_reason=severity_reason,
        finding=finding,
        known_condition=bool(known_text),
        known_condition_text=known_text,
        display=criteria.get("display", "always"),
        sources=sources,
        has_unusable_results=any(r.problem for r in item_results if r.item.get("role", "core") == "core"),
        **review_fields(tree.get("status")),
    )


# --------------------------------------------------------------------------- engine

def _describe_complaint_match(evaluation: DiagnosisEvaluation, criteria: Dict[str, Any]) -> None:
    """Say why a complaint-matched card is shown when no criterion is met."""
    if evaluation.criteria_met or evaluation.finding is not None:
        return
    terms = ", ".join(evaluation.complaint_matches)
    label = criteria.get("finding_label", evaluation.diagnosis_label)
    if evaluation.criteria_not_met:
        text = f"Today's complaint matches ({terms}); available results do not meet criteria for {label}."
    else:
        text = f"Today's complaint matches ({terms}); relevant results are not available."
    evaluation.recommendations.insert(0, text)


def _no_applicable_core_items(tree: Dict[str, Any], patient_data: PatientData) -> bool:
    """True when every core item is restricted to a sex the patient isn't recorded as."""
    core = [i for i in tree["criteria"]["items"] if i.get("role", "core") == "core"]
    gender = str(patient_data.gender or "").lower()
    restricted = [(i.get("applies_to") or {}).get("sex") for i in core]
    return bool(core) and all(sex is not None and sex != gender for sex in restricted)


_CRITERIA_BLOCK = re.compile(r"^criteria:\s*\n\s+\S", re.MULTILINE)


class SmartDiagnosticEngine:
    """
    Evaluates every tree that has a `criteria` section against patient data.

    Decision support only: recommendations describe what findings may be
    consistent with and cite the tree's source; never treatment orders.
    """

    def __init__(self, trees_dir: Optional[Path] = None):
        self.trees_dir = Path(trees_dir) if trees_dir else TREES_PATH
        self.trees = self._load_criteria_trees()
        logger.info(f"Loaded criteria for {len(self.trees)} trees")

    def _load_criteria_trees(self) -> Dict[str, Dict[str, Any]]:
        trees: Dict[str, Dict[str, Any]] = {}
        if not self.trees_dir.exists():
            logger.warning(f"Trees directory not found: {self.trees_dir}")
            return trees
        for path in sorted(self.trees_dir.glob("*.yml")):
            text = path.read_text(encoding="utf-8")
            if not _CRITERIA_BLOCK.search(text):
                continue  # `criteria: []` - nothing to evaluate
            tree = yaml.safe_load(text) or {}
            criteria = tree.get("criteria")
            if isinstance(criteria, dict) and criteria.get("items") and tree.get("status") != "retired":
                trees[tree["tree_id"]] = tree
        return trees

    def observation_requirements(self) -> Dict[str, Dict[str, Any]]:
        """LOINC codes and the longest lookback each resource needs, for the FHIR fetch.

        Only items with lookback_days are included; other items rely on the
        default chart-summary windows.
        """
        needs: Dict[str, Dict[str, Any]] = {}
        for tree in self.trees.values():
            for item in tree["criteria"]["items"]:
                lookback = item.get("lookback_days")
                if not lookback:
                    continue
                resource = "labs" if item.get("resource", "lab") == "lab" else "vitals"
                entry = needs.setdefault(resource, {"codes": set(), "lookback_days": 0})
                entry["codes"].update(item["loinc"])
                entry["lookback_days"] = max(entry["lookback_days"], int(lookback))
        return {k: {"codes": sorted(v["codes"]), "lookback_days": v["lookback_days"]} for k, v in needs.items()}

    def _evaluate_tree(self, tree_id: str, patient_data: PatientData,
                       now: Optional[datetime] = None) -> DiagnosisEvaluation:
        return evaluate_tree(self.trees[tree_id], patient_data, now)

    def evaluate_tree(self, tree_id: str, patient_data: PatientData,
                      now: Optional[datetime] = None) -> DiagnosisEvaluation:
        """One tree's evaluation before any display filtering."""
        return self._evaluate_tree(tree_id, patient_data, now)

    def evaluate_encounter(self, patient_data: PatientData, now: Optional[datetime] = None,
                           complaint: Optional[str] = None) -> EncounterAssessment:
        """Evaluations to show, plus warnings for conditions that could not be assessed.

        An acute card (display: when_met) is shown when a criterion is met, a
        result could not be read, or today's complaint matches the tree's
        complaint_terms.
        """
        evaluations: List[DiagnosisEvaluation] = []
        unassessable: List[str] = []
        not_applicable: List[str] = []

        for tree_id, tree in self.trees.items():
            try:
                evaluation = self._evaluate_tree(tree_id, patient_data, now)
            except Exception as e:
                logger.error(f"Failed to evaluate {tree_id}: {e}")
                evaluations.append(DiagnosisEvaluation(
                    diagnosis_id=tree_id,
                    diagnosis_label=tree.get("name", tree_id),
                    family=str(tree.get("family", "")).lower().replace(" ", "_"),
                    probability=0.0,
                    criteria_met=[], criteria_not_met=[], criteria_unknown=[],
                    recommendations=[], missing_tests=[],
                    severity="unknown",
                    evaluation_status="evaluation failed",
                    status_reason=f"Evaluation failed: {type(e).__name__}: {e}",
                    display=(tree.get("criteria") or {}).get("display", "always"),
                    **review_fields(tree.get("status")),
                ))
                continue

            if (evaluation.display == "when_found" and evaluation.finding is None
                    and _no_applicable_core_items(tree, patient_data)):
                not_applicable.append(
                    f"{tree.get('name', tree_id)} could not be assessed: patient sex is not recorded.")
                continue

            evaluation.complaint_matches = match_terms(
                complaint, (tree["criteria"].get("complaint_terms") or []))[0]
            if evaluation.complaint_matches:
                _describe_complaint_match(evaluation, tree["criteria"])

            nothing_found = (
                (evaluation.display == "when_found" and evaluation.finding is None)
                or (evaluation.display == "when_met" and not evaluation.criteria_met and evaluation.finding is None
                    and not evaluation.complaint_matches)
            )
            if nothing_found and not evaluation.has_unusable_results:
                # Nothing relevant measured or found: hide the card. If the data
                # it needs could not be retrieved, report that once, globally.
                status = patient_data.retrieval_status or {}
                for item in tree["criteria"]["items"]:
                    resource = "labs" if item.get("resource", "lab") == "lab" else "vitals"
                    if status.get(resource, RETRIEVED) != RETRIEVED and resource not in unassessable:
                        unassessable.append(resource)
                continue

            if evaluation.criteria_unknown and evaluation.probability <= 0.3 and evaluation.finding is None:
                evaluation.evaluation_status = "insufficient data"
                missing = ", ".join(evaluation.missing_tests) or ", ".join(
                    c.criterion for c in evaluation.criteria_unknown)
                evaluation.status_reason = f"Insufficient data to evaluate; missing: {missing}"
            evaluations.append(evaluation)

        evaluations.sort(key=lambda x: x.probability, reverse=True)
        # Hide low-probability results only when they were fully evaluated;
        # failed and insufficient-data evaluations are always shown, and so are
        # findings (consistent or possible) and acute cards with a met criterion.
        evaluations = [
            e for e in evaluations
            if e.probability > 0.3
            or e.severity in ["high", "critical"]
            or e.evaluation_status != "evaluated"
            or e.finding is not None
            or (e.display == "when_met" and e.criteria_met)
            or e.complaint_matches
        ]

        labels = {"labs": "lab results", "vitals": "vital signs"}
        warnings = [f"Some conditions could not be assessed: {labels.get(r, r)} could not be retrieved."
                    for r in unassessable] + not_applicable
        logger.info(f"Generated {len(evaluations)} diagnostic evaluations")
        return EncounterAssessment(evaluations=evaluations, warnings=warnings)

    def evaluate_patient(
        self,
        patient_data: PatientData,
        chief_complaint: Optional[str] = None,
        focus_specialties: Optional[List[str]] = None,
        now: Optional[datetime] = None,
    ) -> List[DiagnosisEvaluation]:
        """Evaluations to show, sorted by probability (warnings: evaluate_encounter)."""
        logger.info(f"Evaluating patient {patient_data.name} (Age: {patient_data.age}, Gender: {patient_data.gender})")
        if chief_complaint:
            logger.info(f"Chief complaint: {chief_complaint}")
        return self.evaluate_encounter(patient_data, now, complaint=chief_complaint).evaluations

    def format_evaluation_report(self, evaluation: DiagnosisEvaluation) -> str:
        """Format evaluation as human-readable report."""
        severity_emoji = {"low": "🟢", "moderate": "🟡", "high": "🟠", "critical": "🔴"}

        report = ["=" * 70,
                  f"{severity_emoji.get(evaluation.severity, '')} {evaluation.diagnosis_label}",
                  f"   Family: {evaluation.family.replace('_', ' ').title()}",
                  f"   Probability: {evaluation.probability:.1%}",
                  f"   Severity: {evaluation.severity.upper()}"]
        if evaluation.evaluation_status != "evaluated":
            report.append(f"   Status: {evaluation.evaluation_status.upper()} - {evaluation.status_reason}")
        if evaluation.known_condition:
            report.append(f"   Known condition: {evaluation.known_condition_text}")
        report.append("=" * 70)

        for title, items in (("\n✓ CRITERIA MET:", evaluation.criteria_met),
                             ("\n✗ CRITERIA NOT MET:", evaluation.criteria_not_met),
                             ("\n? INSUFFICIENT DATA:", evaluation.criteria_unknown)):
            if items:
                report.append(title)
                for criterion in items:
                    report.append(f"  • {criterion.criterion}")
                    if criterion.value:
                        report.append(f"    Value: {criterion.value} (expected: {criterion.expected})")
                    if criterion.details:
                        report.append(f"    {criterion.details}")
                    if criterion.source:
                        report.append(f"    Source: {criterion.source}")

        if evaluation.missing_tests:
            report.append("\n🔬 RECOMMENDED TESTS:")
            report.extend(f"  • {test}" for test in evaluation.missing_tests)
        if evaluation.recommendations:
            report.append("\n💡 DECISION SUPPORT:")
            report.extend(f"  • {rec}" for rec in evaluation.recommendations)
        report.append("=" * 70)
        return "\n".join(report)
