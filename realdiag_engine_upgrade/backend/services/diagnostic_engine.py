from __future__ import annotations

from typing import Callable

from backend.schemas.diagnostic import AnalyzeRequest, AnalyzeResponse
from backend.services.domains.cardiovascular import analyze_cardiovascular_case
from backend.services.domains.neurology import analyze_neurology_case
from backend.services.utils.common import build_default_response, normalize_request

DomainAnalyzer = Callable[[AnalyzeRequest], AnalyzeResponse | None]

DOMAIN_ANALYZERS: list[DomainAnalyzer] = [
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
