from __future__ import annotations

from typing import Any, Callable

from backend.schemas.diagnostic import AnalyzeRequest, AnalyzeResponse
from backend.services.domains.cardiovascular import analyze_cardiovascular_case
from backend.services.domains.concussion import evaluate_concussion
from backend.services.domains.first_seizure import evaluate_first_seizure
from backend.services.domains.headache import evaluate_headache
from backend.services.domains.neurology import analyze_neurology_case
from backend.services.utils.common import (
    build_default_response,
    extract_history_text,
    extract_symptom_text,
    normalize_request,
)

DomainAnalyzer = Callable[[AnalyzeRequest], AnalyzeResponse | None]


def _normalized_text(payload: AnalyzeRequest) -> str:
    """Build the lowercased, whitespace-joined text the (payload, normalized_text)
    domain modules expect."""
    return f"{extract_symptom_text(payload)} {extract_history_text(payload)}".strip()


def _headache_adapter(payload: AnalyzeRequest) -> Any:
    """Adapt evaluate_headache's (payload, normalized_text) signature to the
    single-argument DomainAnalyzer contract used by the orchestrator."""
    return evaluate_headache(payload, _normalized_text(payload))


def _concussion_adapter(payload: AnalyzeRequest) -> Any:
    """Adapt evaluate_concussion's (payload, normalized_text) signature to the
    single-argument DomainAnalyzer contract used by the orchestrator."""
    return evaluate_concussion(payload, _normalized_text(payload))


DOMAIN_ANALYZERS: list[DomainAnalyzer] = [
    evaluate_first_seizure,
    _headache_adapter,
    _concussion_adapter,
    analyze_cardiovascular_case,
    analyze_neurology_case,
]


def analyze_case(payload: AnalyzeRequest) -> AnalyzeResponse:
    """
    Orchestrates RealDiag diagnostic analysis.

    This starter production structure is designed to replace a single hard-coded
    function with domain-specific analyzers. Each analyzer can accept the case,
    score its own differential logic, and either return a response or defer.
    """
    normalized_payload = normalize_request(payload)

    for analyzer in DOMAIN_ANALYZERS:
        response = analyzer(normalized_payload)
        if response is not None:
            return response

    return build_default_response(normalized_payload)
