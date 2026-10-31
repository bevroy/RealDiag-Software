"""Offline bundle (GET /offline/bundle): tree library search fields and walkable questionnaires,
versioned, with ranking parity between the server and the browser port (utils/offlineSearch.js)."""
import json

from backend.services import offline_bundle
from backend.services.diagnostic_router import _trees
from backend.services.symptom_search import load_all_families
from backend.tests.offline_parity import FIXTURE, server_results

MAX_BYTES = 10 * 1024 * 1024


def test_server_ranking_matches_the_shared_parity_fixture():
    fixture = json.loads(FIXTURE.read_text())
    results, settings = server_results(fixture)
    assert results == fixture["expected"]
    # The fixture's ranking settings are the server's, as the bundle carries them.
    assert {k: fixture["search"][k] for k in settings} == json.loads(json.dumps(settings))


def test_bundle_has_every_tree_and_the_server_settings():
    bundle = offline_bundle.build_bundle()
    rules = bundle["search"]["rules"]
    server = [r for family in load_all_families().values() for r in family]
    assert [r["id"] for r in rules] == [r["id"] for r in server]
    assert bundle["tree_count"] == len(rules)
    first = rules[0]
    assert set(offline_bundle.RULE_FIELDS) <= set(first) and "review_status_label" in first
    fixture = json.loads(FIXTURE.read_text())
    for key in ("synonyms", "negation_cues", "negation_exceptions"):
        assert bundle["search"][key] == fixture["search"][key]


def test_questionnaires_are_the_walk_endpoint_payloads():
    bundle = offline_bundle.build_bundle()
    walkable = [t["id"] for t in _trees.list() if t["node_format"] == "questionnaire" and t.get("walk_available")]
    assert sorted(bundle["questionnaires"]) == sorted(walkable) and walkable
    tree_id = walkable[0]
    expected = {k: v for k, v in _trees.questionnaire(tree_id).items() if k != "clinical_review_notice"}
    assert bundle["questionnaires"][tree_id] == json.loads(json.dumps(expected, default=str))


def test_version_is_a_content_hash_and_size_is_reported():
    bundle = offline_bundle.build_bundle()
    assert len(bundle["version"]) == 16
    assert 0 < bundle["size_bytes"] < MAX_BYTES
    assert "patient" not in json.dumps(bundle["search"]["rules"][0]).lower()


def test_routes_require_login_and_return_the_version():
    from fastapi.testclient import TestClient
    from backend.main import app

    assert app.url_path_for("bundle") == "/offline/bundle"
    assert app.url_path_for("bundle_version") == "/offline/bundle/version"
    assert TestClient(app).get("/offline/bundle/version").status_code == 401
    assert any(d.dependency is offline_bundle.require_approved_user for d in offline_bundle.router.dependencies)


def test_only_approved_roles_get_the_bundle():
    from fastapi import HTTPException
    import pytest
    ok = [{"email": "a@gmail.com", "role": "provider"}, {"email": "a@gmail.com", "role": "admin"},
          {"email": "a@realdiag.com", "role": "user"}]
    for user in ok:
        assert offline_bundle.require_approved_user(user) is user
    for user in ({"email": "a@gmail.com", "role": "user"}, {"email": "a@gmail.com", "role": "patient"},
                 {"email": "a@realdiag.com", "role": "student"}):
        with pytest.raises(HTTPException) as err:
            offline_bundle.require_approved_user(user)
        assert err.value.status_code == 403


def test_bundle_is_compact_uncached_and_expires(monkeypatch):
    from datetime import datetime
    monkeypatch.setenv("OFFLINE_BUNDLE_TTL_HOURS", "12")
    response = offline_bundle.bundle()
    assert response.headers["cache-control"] == "no-store, private"
    text = response.body.decode()
    body = json.loads(text)
    assert text == json.dumps(body, separators=(",", ":"))  # compact: no whitespace between tokens
    issued, expires = datetime.fromisoformat(body["issued_at"]), datetime.fromisoformat(body["expires_at"])
    assert (expires - issued).total_seconds() == 12 * 3600
    assert body["version"] == offline_bundle.build_bundle()["version"]
    from starlette.responses import Response
    version_response = Response()
    assert offline_bundle.bundle_version(version_response)["ttl_hours"] == 12
    assert version_response.headers["cache-control"] == "no-store, private"
