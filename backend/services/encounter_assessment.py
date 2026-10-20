"""
Encounter assessment: one chart pull, combined into one decision-support view.

Sections:
  summary            chart summary, per-resource retrieval status, cut-off notes
  complaint          today's complaint and where it came from
  diagnoses          complaint matches across the tree library (no language
                     model) merged with criteria-supported diagnoses; each
                     shows its evidence
  guidance           workup, treatment (reference, not orders), referrals and
                     disposition from each shown tree, with sources and status
  red_flags          red flags listed in each shown tree
  not_assessed       what could not be assessed and why

EHR data is never sent to an AI provider: ranking uses allow_ai=False.
"""

import asyncio
import logging
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional

import yaml

from backend.services.clinical_review import review_fields, review_notice
from backend.services.complaint_matching import (
    NO_COMPLAINT, Complaint, affirmed_phrases, resolve_complaint, split_negated,
)
from backend.services.fhir_client import RESOURCE_LABELS, RETRIEVED, NOT_AVAILABLE, retrieval_warnings
from backend.services.smart_diagnostic_engine import SEVERITY_RANK, DiagnosisEvaluation, SmartDiagnosticEngine
from backend.services.symptom_search import CANT_MISS_LABEL, rank_diagnoses
from backend.services.missed_items import (
    SCREENING_PROCEDURE_LOOKBACK_DAYS, possible_missed_items, screening_requirements,
)

logger = logging.getLogger(__name__)

TREES_PATH = Path(__file__).resolve().parents[1] / "trees"
COMPLAINT_MATCH_LIMIT = 15
# Fetched by FHIRClient for the criteria; the history service skips them.
HISTORY_SKIP = {"demographics", "vital_signs", "diagnostic_tests", "conditions", "medications", "allergies"}
# History data types the encounter assessment uses.
HISTORY_RESOURCES = ("visit_notes", "history_and_physicals", "procedures", "imaging_studies",
                     "immunizations", "family_social_history")

TREATMENT_LABEL = "Treatment information from the decision tree (reference, not an order)"
NO_RED_FLAGS = "No red flags listed for this condition."
DECISION_SUPPORT_NOTICE = (
    "Decision support only. Findings and suggestions are for the treating clinician to "
    "consider; they are not diagnoses or orders."
)


# --------------------------------------------------------------------------- tree content

@lru_cache(maxsize=1)
def _tree_paths() -> Dict[str, Path]:
    paths: Dict[str, Path] = {}
    for path in TREES_PATH.glob("*.yml"):
        paths[path.stem] = path
    return paths


@lru_cache(maxsize=512)
def load_tree(tree_id: str) -> Optional[Dict[str, Any]]:
    path = _tree_paths().get(tree_id)
    if path is None:
        for candidate in _tree_paths().values():   # file name differs from tree_id
            data = yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}
            if data.get("tree_id") == tree_id:
                return data
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _text(value: Any) -> List[str]:
    """Flatten a tree value (str, list, dict) into display lines."""
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (int, float)):
        return [str(value)]
    if isinstance(value, list):
        return [line for item in value for line in _text(item)]
    if isinstance(value, dict):
        lines = []
        for key, inner in value.items():
            inner_lines = _text(inner)
            if len(inner_lines) == 1:
                lines.append(f"{key}: {inner_lines[0]}")
            else:
                lines.extend(f"{key}: {line}" for line in inner_lines)
        return lines
    return [str(value)]


def sections(value: Any) -> List[Dict[str, Any]]:
    """Tree section as [{title, items}]: a dict keeps its keys as titles."""
    if not value:
        return []
    if isinstance(value, dict):
        out = []
        for key, inner in value.items():
            items = _text(inner)
            if items:
                out.append({"title": str(key).replace("_", " "), "items": items})
        return out
    items = _text(value)
    return [{"title": None, "items": items}] if items else []


def _sources(tree: Dict[str, Any]) -> List[str]:
    out = []
    for source in tree.get("sources") or []:
        text = source.get("text") if isinstance(source, dict) else source
        if text and text not in out:
            out.append(str(text))
    return out


def tree_guidance(tree_id: str) -> Optional[Dict[str, Any]]:
    tree = load_tree(tree_id)
    if not tree:
        return None
    return {
        "tree_id": tree_id,
        "name": tree.get("name", tree_id),
        "urgency": tree.get("urgency"),
        "workup": sections(tree.get("workup")),
        "treatment": {"label": TREATMENT_LABEL, "sections": sections(tree.get("treatment"))},
        "referrals": sections(tree.get("referrals")),
        "disposition_guidance": sections(tree.get("disposition_guidance")),
        "sources": _sources(tree),
        **review_fields(tree.get("status")),
    }


def tree_red_flags(tree_id: str) -> Optional[Dict[str, Any]]:
    tree = load_tree(tree_id)
    if not tree:
        return None
    flags = _text(tree.get("red_flags")) + _text(tree.get("red_flags_immediate_action"))
    return {
        "tree_id": tree_id,
        "name": tree.get("name", tree_id),
        "red_flags": flags,
        "note": None if flags else NO_RED_FLAGS,
        **review_fields(tree.get("status")),
    }


# --------------------------------------------------------------------------- diagnoses

def _criteria_rank(evaluation: DiagnosisEvaluation) -> tuple:
    finding = {"consistent": 2, "possible": 1}.get(evaluation.finding or "", 0)
    return (SEVERITY_RANK.get(evaluation.severity, 0), finding, len(evaluation.criteria_met))


def merge_diagnoses(evaluations: List[DiagnosisEvaluation], matches: List[Any],
                    criteria_response: Callable[[DiagnosisEvaluation], Dict[str, Any]],
                    limit: int = COMPLAINT_MATCH_LIMIT) -> Dict[str, Any]:
    """Complaint matches (top `limit`, plus every can't-miss match) merged with
    criteria-supported diagnoses by tree id.

    Order: both kinds of evidence first, then criteria only (by severity),
    then complaint only (by match score).
    """
    by_id = {m.rule_id: m for m in matches}
    top_matches = matches[:limit]
    extra_cant_miss = [m for m in matches[limit:] if getattr(m, "cant_miss", False)]
    shown_matches = top_matches + extra_cant_miss
    entries: Dict[str, Dict[str, Any]] = {}

    for evaluation in evaluations:
        match = by_id.get(evaluation.diagnosis_id)
        entries[evaluation.diagnosis_id] = {
            "tree_id": evaluation.diagnosis_id,
            "name": evaluation.diagnosis_label,
            "family": evaluation.family,
            "complaint_match": _match_evidence(match, evaluation.complaint_matches),
            "criteria": criteria_response(evaluation),
            "cant_miss": bool(getattr(match, "cant_miss", False)) or (
                bool(evaluation.complaint_matches) and _is_emergent(evaluation.diagnosis_id)),
            "review_status": evaluation.review_status,
            "review_status_label": evaluation.review_status_label,
            "_rank": _criteria_rank(evaluation),
            "_score": match.match_score if match else 0.0,
        }
    for match in shown_matches:
        if match.rule_id in entries:
            continue
        entries[match.rule_id] = {
            "tree_id": match.rule_id,
            "name": match.label,
            "family": match.family,
            "complaint_match": _match_evidence(match),
            "criteria": None,
            "cant_miss": bool(getattr(match, "cant_miss", False)),
            "review_status": match.review_status,
            "review_status_label": match.review_status_label,
            "_rank": (-1,),
            "_score": match.match_score,
        }

    for entry in entries.values():
        entry["cant_miss_label"] = CANT_MISS_LABEL if entry["cant_miss"] else None
        has_complaint = entry["complaint_match"] is not None
        has_criteria = entry["criteria"] is not None
        entry["evidence"] = ("complaint and criteria" if has_complaint and has_criteria
                             else "criteria" if has_criteria else "complaint")
        entry["_both"] = has_complaint and has_criteria

    ordered = sorted(entries.values(), key=lambda e: (
        0 if e["_both"] else 1 if e["criteria"] is not None else 2,
        tuple(-x for x in e["_rank"]),
        -e["_score"],
    ))
    for entry in ordered:
        for key in ("_rank", "_score", "_both"):
            entry.pop(key)

    total = len(matches)
    note = None
    if total > len(top_matches):
        note = f"Showing {len(top_matches)} of {total} complaint matches"
        if extra_cant_miss:
            count = len(extra_cant_miss)
            note += f", plus {count} can't-miss condition{'s' if count > 1 else ''} below the cut-off"
        note += "."
    return {
        "items": ordered,
        "complaint_matches_total": total,
        "complaint_matches_shown": len(top_matches),
        "cant_miss_added": len(extra_cant_miss),
        "complaint_matches_note": note,
    }


def _is_emergent(tree_id: str) -> bool:
    tree = load_tree(tree_id) or {}
    return str(tree.get("urgency") or "").lower() == "emergent"


def _match_evidence(match: Any, matched_terms: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    """Complaint evidence: library presentations matched and/or the tree's complaint terms matched."""
    if match is None and not matched_terms:
        return None
    return {"matched_presentations": list(match.matched_presentations or []) if match else [],
            "matched_terms": list(matched_terms or []),
            "match_score": match.match_score if match else None}


# --------------------------------------------------------------------------- summary

def _history_status(history: Any, history_error: Optional[Exception]) -> Dict[str, str]:
    if history_error is not None or history is None:
        return {r: "failed" for r in HISTORY_RESOURCES}
    status = dict(getattr(history, "retrieval_status", {}) or {})
    return {r: status[r] for r in HISTORY_RESOURCES if r in status}


def build_summary(patient_data: Any, history: Any, history_status: Dict[str, str],
                  summary_response: Callable[[Any], Any]) -> Dict[str, Any]:
    from backend.services.patient_history_service import PatientHistoryService, _concept_name

    chart = summary_response(patient_data).dict()
    status = dict(patient_data.retrieval_status or {})
    summary_status = {
        "conditions": status.get("conditions", RETRIEVED),
        "medications": status.get("medications", RETRIEVED),
        "diagnostic_tests": status.get("labs", RETRIEVED),
        "visit_notes": history_status.get("visit_notes", RETRIEVED),
    }
    abnormal = [lab for lab in patient_data.labs if getattr(lab, "is_abnormal", False)]
    text = PatientHistoryService._generate_summary(
        {"name": patient_data.name, "age": patient_data.age, "gender": patient_data.gender},
        [{"code": _concept_name(c.get("code"))} for c in patient_data.conditions],
        patient_data.medications,
        [SimpleNamespace(abnormal=True) for _ in abnormal],
        list(getattr(history, "visit_notes", []) or []),
        summary_status,
    )
    all_status = {**status, **history_status}
    chart.update({
        "summary_text": text,
        "active_problems": [_concept_name(c.get("code")) for c in patient_data.conditions],
        "data_status": all_status,
        "data_status_labels": {r: RESOURCE_LABELS.get(r, r) for r in all_status},
        "data_warnings": list(chart.get("data_warnings") or []) + retrieval_warnings(history_status),
        "cut_off_notes": list(getattr(patient_data, "truncation_warnings", []) or []),
        "visit_note_count": len(getattr(history, "visit_notes", []) or []) if history_status.get(
            "visit_notes") == RETRIEVED else None,
    })
    return chart


# --------------------------------------------------------------------------- not assessed

def not_assessed(all_status: Dict[str, str], assessment_warnings: List[str],
                 evaluations: List[DiagnosisEvaluation], complaint: Complaint) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    for resource, outcome in all_status.items():
        if outcome == RETRIEVED:
            continue
        label = RESOURCE_LABELS.get(resource, resource)
        reason = "not available from this EHR" if outcome == NOT_AVAILABLE else "could not be retrieved"
        items.append({"category": "data", "text": f"{label} {reason}; do not assume none."})
    for warning in assessment_warnings:
        items.append({"category": "condition", "text": warning})
    for e in evaluations:
        if e.evaluation_status == "insufficient data":
            missing = ", ".join(e.missing_tests) or "required results"
            items.append({"category": "condition", "text": f"{e.diagnosis_label}: insufficient data; missing {missing}."})
        elif e.evaluation_status == "evaluation failed":
            items.append({"category": "condition", "text": f"{e.diagnosis_label}: evaluation failed."})
    for warning in complaint.warnings:
        items.append({"category": "complaint", "text": warning})
    if complaint.source == NO_COMPLAINT:
        items.append({"category": "complaint",
                      "text": "No complaint entered or found; complaint matching was skipped."})
    return items


# --------------------------------------------------------------------------- assessment

async def assess_encounter(
    patient_id: str,
    typed_complaint: Optional[str],
    fhir_client: Any,
    history_service: Any,
    engine: SmartDiagnosticEngine,
    criteria_response: Callable[[DiagnosisEvaluation], Any],
    summary_response: Callable[[Any], Any],
    now: Optional[datetime] = None,
    lookback_days: int = 365,
) -> Dict[str, Any]:
    """Pull the chart once (FHIR client and history service run at the same time,
    without overlapping data types) and build every section."""

    async def history_pull():
        return await history_service.get_comprehensive_history(
            patient_id=patient_id, lookback_days=lookback_days, skip=HISTORY_SKIP,
            lookback_overrides={"procedures": SCREENING_PROCEDURE_LOOKBACK_DAYS,
                                "imaging_studies": SCREENING_PROCEDURE_LOOKBACK_DAYS})

    def smoking_pull():
        # US Core smoking status, for the AAA and lung cancer screening rules
        if not hasattr(fhir_client, "get_smoking_status"):
            return NOT_AVAILABLE, None
        try:
            return RETRIEVED, fhir_client.get_smoking_status(patient_id)
        except Exception as e:
            response = getattr(e, "response", None)
            code = getattr(response, "status_code", None)
            return (NOT_AVAILABLE if code in (403, 404, 501) else "failed"), None

    def complaint_pull():
        if typed_complaint and typed_complaint.strip():
            return resolve_complaint(typed_complaint)
        return resolve_complaint(None, lambda: fhir_client.get_current_encounter(patient_id))

    requirements = {**engine.observation_requirements(), **screening_requirements()}
    patient_task = asyncio.to_thread(
        fhir_client.get_patient_data, patient_id, observation_requirements=requirements)
    results = await asyncio.gather(patient_task, history_pull(), asyncio.to_thread(complaint_pull),
                                   asyncio.to_thread(smoking_pull), return_exceptions=True)
    patient_data, history, complaint, smoking_result = results
    smoking_status, smoking = (smoking_result if not isinstance(smoking_result, Exception) else ("failed", None))
    if isinstance(patient_data, Exception):
        raise patient_data
    history_error = history if isinstance(history, Exception) else None
    if history_error is not None:
        logger.warning(f"History retrieval failed for encounter assessment: {history_error}")
        history = None
    if isinstance(complaint, Exception):
        complaint = Complaint(text=typed_complaint, source=NO_COMPLAINT,
                              warnings=["Today's visit reason could not be retrieved from the EHR."])

    assessment = engine.evaluate_encounter(patient_data, now=now, complaint=complaint.text)

    matches: List[Any] = []
    phrases = affirmed_phrases(complaint.text)
    if phrases:
        # Tree library only: EHR data is never sent to an AI provider.
        ranked, _ = await rank_diagnoses(phrases, age=patient_data.age, sex=patient_data.gender,
                                         allow_ai=False, limit=None)
        matches = [m for m in ranked.results if not m.ai_suggested]

    diagnoses = merge_diagnoses(assessment.evaluations, matches,
                                lambda e: _as_dict(criteria_response(e)))
    tree_ids = [d["tree_id"] for d in diagnoses["items"]]
    history_status = _history_status(history, history_error)
    history_status["smoking_status"] = smoking_status
    summary = build_summary(patient_data, history, history_status, summary_response)
    missed = possible_missed_items(engine, patient_data, history, smoking, summary["data_status"], now=now)

    return {
        "patient_id": patient_id,
        "summary": summary,
        "complaint": {"text": complaint.text, "source": complaint.source, "source_label": complaint.source_label,
                      "phrases_used": phrases,
                      "negated_terms": split_negated(complaint.text)[1] if complaint.text else []},
        "diagnoses": diagnoses,
        "guidance": [g for g in (tree_guidance(t) for t in tree_ids) if g],
        "red_flags": [r for r in (tree_red_flags(t) for t in tree_ids) if r],
        "missed_items": missed,
        "not_assessed": not_assessed(summary["data_status"], assessment.warnings,
                                     assessment.evaluations, complaint),
        "decision_support_notice": DECISION_SUPPORT_NOTICE,
        "clinical_review_notice": review_notice(),
    }


def _as_dict(value: Any) -> Dict[str, Any]:
    return value.dict() if hasattr(value, "dict") else dict(value)
