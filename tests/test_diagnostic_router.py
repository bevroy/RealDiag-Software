"""
Diagnostic Router Tests
Focused on the emr_patient_id role gate on POST /diagnostic/evaluate/{tree_id}.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services import diagnostic_router as diagnostic_router_module


@pytest.fixture(autouse=True)
def _stub_broken_tree_info_lookup(monkeypatch):
    """Work around a pre-existing, unrelated bug: evaluate_tree()'s
    subscription-gate block calls _trees.get_tree_info(tree_id), but
    DecisionTreeEngine has no such method (confirmed via `git blame` --
    predates this change, commit 9884b53, 2026-06-25) -- it 500s for ANY
    authenticated caller before the emr_patient_id gate is ever reached.
    Stubbed here (test-only, doesn't touch source) so these tests can
    actually exercise the role gate through the real endpoint; flagged
    separately as an out-of-scope bug worth fixing on its own."""
    monkeypatch.setattr(diagnostic_router_module._trees, "get_tree_info", lambda tree_id: None, raising=False)


def _set_user_role(user_id: str, role: str) -> None:
    """Directly set a role in whichever store auth_service is using (DB or
    in-memory) -- normal /users/register signup only ever produces
    role='user' regardless of email domain, so a provider-role test
    account has to be set up this way. Same helper as test_symptom_search.py
    (kept local rather than shared, matching that file's own conventions)."""
    from backend.services.database import DATABASE_AVAILABLE, get_db_session, User
    if DATABASE_AVAILABLE:
        with get_db_session() as db:
            user = db.query(User).filter_by(user_id=user_id).first()
            if user:
                user.role = role
                return
    from backend.services.auth_service import users_db
    if user_id in users_db:
        users_db[user_id]["role"] = role


def _register_access_token(role: str) -> str:
    """Register exactly one account for the given role and return its
    Bearer token. /users/register is rate-limited (5/15min) across the
    whole test session, so this is called once per role via module-scoped
    fixtures below, not once per test."""
    email = f"diag-emr-gate-{role}-{uuid.uuid4().hex[:8]}@realdiag.com"
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/users/register",
            json={
                "email": email,
                "password": "TestPass123!",
                "full_name": f"Diagnostic EMR Gate {role.title()} Tester",
            },
        )
        assert response.status_code == 201
        user_id = response.json()["user"]["user_id"]
        _set_user_role(user_id, role)
        return response.cookies.get("access_token")


@pytest.fixture(scope="module")
def user_access_token() -> str:
    return _register_access_token("user")


@pytest.fixture(scope="module")
def provider_access_token() -> str:
    return _register_access_token("provider")


def test_evaluate_tree_without_emr_patient_id_unaffected(user_access_token: str):
    """A request with no emr_patient_id at all is unaffected by the role
    gate, for any role (plain 'user' here)."""
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/diagnostic/evaluate/CARD-CHEST-PAIN",
            headers={"Authorization": f"Bearer {user_access_token}"},
            json={"symptoms": ["chest pain"]},
        )
    assert response.status_code == 200
    assert "tree_result" in response.json()


def test_evaluate_tree_emr_patient_id_denied_for_plain_user(user_access_token: str):
    """A plain USER-role account supplying emr_patient_id is rejected with a
    clear 403, not silently ignored."""
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/diagnostic/evaluate/CARD-CHEST-PAIN",
            headers={"Authorization": f"Bearer {user_access_token}"},
            json={"symptoms": ["chest pain"], "emr_patient_id": "test-patient-1"},
        )
    assert response.status_code == 403
    assert "provider-level access" in response.json()["detail"]


def test_evaluate_tree_emr_patient_id_allowed_for_provider(provider_access_token: str):
    """A PROVIDER-role account supplying emr_patient_id is not rejected for
    role reasons."""
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/diagnostic/evaluate/CARD-CHEST-PAIN",
            headers={"Authorization": f"Bearer {provider_access_token}"},
            json={"symptoms": ["chest pain"], "emr_patient_id": "test-patient-1"},
        )
    assert response.status_code == 200
    assert "tree_result" in response.json()
