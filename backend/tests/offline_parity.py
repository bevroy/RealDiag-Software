"""Server-side results for the offline-search parity fixture.

frontend/__tests__/fixtures/offline-search-parity.json holds synthetic test
rules (not clinical content), queries, and the results the server ranking
(symptom_search.rank_diagnoses, allow_ai=False) gives for them. The backend
test checks the server still gives those results; the frontend test checks
utils/offlineSearch.js gives the same. To refresh after a deliberate ranking
change: python -m backend.tests.offline_parity --write
"""
import asyncio
import json
import sys
from pathlib import Path
from unittest import mock

FIXTURE = Path(__file__).resolve().parents[2] / "frontend" / "__tests__" / "fixtures" / "offline-search-parity.json"


def server_results(fixture):
    from backend.services import symptom_search
    from backend.services.complaint_matching import NEGATION_CUES, NEGATION_EXCEPTIONS

    families = {}
    for rule in fixture["rules"]:
        families.setdefault(rule["family"], []).append(rule)
    out = []
    with mock.patch.object(symptom_search, "load_all_families", return_value=families):
        for q in fixture["queries"]:
            response, _ = asyncio.run(symptom_search.rank_diagnoses(
                q["symptoms"], age=q.get("age"), sex=q.get("sex"), family=q.get("family"), allow_ai=False,
                limit=q.get("limit", fixture["search"]["result_limit"])))
            out.append({"results": [[r.rule_id, r.match_score, r.matched_presentations, r.cant_miss]
                                    for r in response.results],
                        "negated_terms": response.negated_terms})
    settings = {"synonyms": symptom_search.SYMPTOM_SYNONYMS, "negation_cues": list(NEGATION_CUES),
                "negation_exceptions": list(NEGATION_EXCEPTIONS)}
    return out, settings


if __name__ == "__main__" and "--write" in sys.argv:
    data = json.loads(FIXTURE.read_text())
    data["expected"], settings = server_results(data)
    data["search"].update(settings)
    FIXTURE.write_text(json.dumps(data, indent=1) + "\n")
