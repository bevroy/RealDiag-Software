"""
Offline bundle: what Symptom Search and /diagnose need to run without a network.

One versioned JSON document, built from the same data the server uses:

- search: every tree's ranking fields (as load_all_families() returns them:
  presentations, complaint terms, urgency, age/sex limits, sensitivity,
  ICD-10, review status) and the ranking settings (synonyms, negation cues
  and exceptions), so the browser can rank with the same rules as
  POST /search/by-symptoms (tree library only: no AI, no chart data);
- questionnaires: every walkable questionnaire tree, exactly as
  GET /diagnostic/trees/{id}/questionnaire returns it, for the
  question-by-question walk on /diagnose.

`version` is a content hash, so a client refreshes only when the library
changed. No patient data is in the bundle.

Access: signed in (with MFA when required) and an approved role
(access_policy.has_approved_role). Each download is stamped with
issued_at/expires_at (OFFLINE_BUNDLE_TTL_HOURS, default 24); the browser
discards an expired bundle, deletes it at sign-out and replaces it at
sign-in. Served as compact JSON with Cache-Control: no-store.
"""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Response

from backend.services.auth_service import get_current_user
from backend.services.clinical_review import review_fields, review_notice

FORMAT = 1
RULE_FIELDS = ("id", "label", "family", "urgency", "presentations", "complaint_terms", "applies_to", "age_min",
               "age_max", "sensitivity", "icd10")


@lru_cache(maxsize=1)
def build_bundle() -> Dict[str, Any]:
    from backend.services import complaint_matching
    from backend.services.diagnostic_router import _trees
    from backend.services.symptom_search import SYMPTOM_SYNONYMS, load_all_families

    rules = []
    # Server order kept: ties in score rank in this order, as on the server.
    for family_rules in load_all_families().values():
        for rule in family_rules:
            entry = {k: rule.get(k) for k in RULE_FIELDS}
            entry["presentations"] = [p for p in rule.get("presentations") or [] if isinstance(p, str)]
            entry.update(review_fields(rule.get("status")))
            rules.append(entry)
    questionnaires = {}
    for tree in sorted(_trees.list(), key=lambda t: t["id"]):
        if tree["node_format"] == "questionnaire" and tree.get("walk_available"):
            payload = _trees.questionnaire(tree["id"])
            if "error" not in payload:
                questionnaires[tree["id"]] = {k: v for k, v in payload.items() if k != "clinical_review_notice"}
    content = {
        "format": FORMAT,
        "search": {
            "synonyms": SYMPTOM_SYNONYMS,
            "negation_cues": list(complaint_matching.NEGATION_CUES),
            "negation_exceptions": list(complaint_matching.NEGATION_EXCEPTIONS),
            "result_limit": 20,
            "rules": rules,
        },
        "questionnaires": questionnaires,
        "clinical_review_notice": review_notice(),
    }
    text = json.dumps(content, sort_keys=True, separators=(",", ":"), default=str)
    version = hashlib.sha256(text.encode()).hexdigest()[:16]
    return {"version": version, "size_bytes": len(text.encode()), "tree_count": len(rules),
            "questionnaire_count": len(questionnaires), **json.loads(text)}


APPROVED_ROLE_DETAIL = "The offline library is available to approved clinical accounts only."
NO_STORE = {"Cache-Control": "no-store, private"}


def require_approved_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    from backend.services.access_policy import has_approved_role
    if not has_approved_role(current_user):
        raise HTTPException(status_code=403, detail=APPROVED_ROLE_DETAIL)
    return current_user


router = APIRouter(prefix="/offline", tags=["offline"], dependencies=[Depends(require_approved_user)])


@router.get("/bundle/version")
def bundle_version(response: Response):
    """The current bundle's version and size, so a client can tell whether to refresh."""
    from backend.services.access_policy import offline_bundle_ttl_hours
    bundle = build_bundle()
    response.headers.update(NO_STORE)
    return {**{k: bundle[k] for k in ("version", "size_bytes", "tree_count", "questionnaire_count")},
            "ttl_hours": offline_bundle_ttl_hours()}


@router.get("/bundle")
def bundle():
    """The full offline bundle (tree library search fields + walkable questionnaires), compact JSON,
    stamped with when it was issued and when the device must discard it."""
    from backend.services.access_policy import offline_bundle_ttl_hours
    now = datetime.now(timezone.utc)
    body = {**build_bundle(), "issued_at": now.isoformat(),
            "expires_at": (now + timedelta(hours=offline_bundle_ttl_hours())).isoformat()}
    return Response(content=json.dumps(body, separators=(",", ":")), media_type="application/json",
                    headers=NO_STORE)
