"""
GET /admin/users: every account with role, active state, MFA, invite state,
how it is allowed to sign in, and last sign-in, so tester access can be
reviewed and removed (deactivation) after validation testing.
"""
import uuid

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.security import limiter

PASSWORD = "ClassPass123!"
ADMIN_TOKEN = "test-admin-token-" + "h" * 24


@pytest.fixture
def client():
    limiter.enabled = False
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def admin(monkeypatch, client):
    monkeypatch.setenv("ADMIN_TOKEN", ADMIN_TOKEN)
    operator = f"op-{uuid.uuid4().hex[:8]}@realdiag.com"
    assert client.post("/users/register", json={"email": operator, "password": PASSWORD, "full_name": "Op"}).status_code == 201
    client.cookies.clear()
    session = client.post("/users/login", json={"email": operator, "password": PASSWORD}).cookies.get("access_token")
    client.cookies.clear()
    return {"headers": {"Authorization": f"Bearer {ADMIN_TOKEN}"}, "cookies": {"access_token": session}}


def _row(client, admin, email):
    body = client.get("/admin/users", **admin).json()
    assert body["count"] == len(body["users"])
    return next(u for u in body["users"] if u["email"] == email)


def test_list_shows_last_sign_in_and_deactivation(client, admin):
    tester = f"tester-{uuid.uuid4().hex[:8]}@gmail.com"
    assert client.post("/admin/allowlist", json={"email": tester}, **admin).status_code == 201
    temp = client.post("/admin/users/create", json={"email": tester, "role": "provider"}, **admin).json()["temporary_password"]
    row = _row(client, admin, tester)
    assert row["last_login"] is None and row["is_active"] is True and row["role"] == "provider"
    assert row["access_by"] == "allowlist" and row["invited_by"] and row["mfa_enabled"] is False

    client.cookies.clear()
    assert client.post("/users/login", json={"email": tester, "password": temp}).status_code == 200
    client.cookies.clear()
    assert _row(client, admin, tester)["last_login"] is not None

    assert client.post("/admin/users/deactivate", json={"email": tester, "reason": "testing done"}, **admin).status_code == 200
    assert _row(client, admin, tester)["is_active"] is False
    assert client.post("/users/login", json={"email": tester, "password": temp}).status_code == 403

    assert client.post("/admin/allowlist/remove", json={"email": tester}, **admin).status_code == 200
    assert _row(client, admin, tester)["access_by"] == "none (sign-in refused)"


def test_list_needs_the_admin_token(client, admin):
    assert client.get("/admin/users", cookies=admin["cookies"]).status_code == 401
