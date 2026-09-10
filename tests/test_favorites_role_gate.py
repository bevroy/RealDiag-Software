"""
Favorites Role Gate Tests
Covers the provider/admin-only restriction on POST /users/me/favorites
and the can_manage_favorites field on GET /users/me.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from backend.main import app


def _set_user_role(user_id: str, role: str) -> None:
    """Directly set a role in whichever store auth_service is using (DB or
    in-memory) -- normal /users/register signup only ever produces
    role='user' regardless of email domain, so a provider-role test
    account has to be set up this way. Same helper as
    test_diagnostic_router.py/test_symptom_search.py (kept local rather
    than shared, matching those files' own conventions)."""
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
    email = f"favorites-gate-{role}-{uuid.uuid4().hex[:8]}@realdiag.com"
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/users/register",
            json={
                "email": email,
                "password": "TestPass123!",
                "full_name": f"Favorites Gate {role.title()} Tester",
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


@pytest.fixture(scope="module")
def admin_access_token() -> str:
    return _register_access_token("admin")


def _add_favorite(token: str, rule_id: str = "CARD-CHEST-PAIN"):
    with TestClient(app, raise_server_exceptions=False) as client:
        return client.post(
            "/users/me/favorites",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "rule_id": rule_id,
                "diagnosis_label": "Test Diagnosis",
                "family": "cardiology",
            },
        )


def test_plain_user_denied_add_to_favorites(user_access_token: str):
    response = _add_favorite(user_access_token)
    assert response.status_code == 403
    assert response.json()["detail"] == "Favorites require a provider-level account"


def test_provider_can_add_to_favorites(provider_access_token: str):
    response = _add_favorite(provider_access_token, rule_id="provider-fav-1")
    assert response.status_code == 200


def test_admin_can_add_to_favorites(admin_access_token: str):
    response = _add_favorite(admin_access_token, rule_id="admin-fav-1")
    assert response.status_code == 200


def test_profile_can_manage_favorites_reflects_real_role(
    user_access_token: str, provider_access_token: str
):
    """The frontend gates the favorites button on this field rather than
    the `role` display value, since _normalize_ui_role() shows "provider"
    for every realdiag.com/elionyxhealth.com account regardless of the
    actual stored role."""
    with TestClient(app, raise_server_exceptions=False) as client:
        user_profile = client.get(
            "/users/me", headers={"Authorization": f"Bearer {user_access_token}"}
        )
        provider_profile = client.get(
            "/users/me", headers={"Authorization": f"Bearer {provider_access_token}"}
        )

    assert user_profile.status_code == 200
    assert user_profile.json()["can_manage_favorites"] is False
    # Both show role == "provider" via the display-only relabeling -
    # can_manage_favorites is what actually differs.
    assert user_profile.json()["role"] == "provider"

    assert provider_profile.status_code == 200
    assert provider_profile.json()["can_manage_favorites"] is True
    assert provider_profile.json()["role"] == "provider"
