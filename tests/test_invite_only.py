"""
Invite-only accounts: self-registration is refused by default; an admin
invites (one-time setup link) or creates an account (temporary password).
The email-domain rule still applies. The database path (completing an invite)
is in test_invite_only_db.py.
"""
import uuid

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.security import limiter

PASSWORD = "ClassPass123!"
ADMIN_TOKEN = "test-admin-token-" + "d" * 24


def _email(prefix="tester", domain="realdiag.com"):
    return f"{prefix}-{uuid.uuid4().hex[:10]}@{domain}"


@pytest.fixture
def client():
    limiter.enabled = False
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def admin(monkeypatch, client):
    monkeypatch.setenv("ADMIN_TOKEN", ADMIN_TOKEN)
    operator = _email("operator")
    assert client.post("/users/register", json={"email": operator, "password": PASSWORD, "full_name": "Op"}).status_code == 201
    client.cookies.clear()
    session = client.post("/users/login", json={"email": operator, "password": PASSWORD}).cookies.get("access_token")
    client.cookies.clear()
    return {"headers": {"Authorization": f"Bearer {ADMIN_TOKEN}"}, "cookies": {"access_token": session}}


def test_self_registration_is_refused_by_default(client, monkeypatch):
    monkeypatch.delenv("ALLOW_SELF_REGISTRATION", raising=False)
    r = client.post("/users/register", json={"email": _email(), "password": PASSWORD, "full_name": "X"})
    assert r.status_code == 403
    assert "invitation only" in r.json()["detail"]
    monkeypatch.setenv("ALLOW_SELF_REGISTRATION", "0")
    assert client.post("/users/register", json={"email": _email(), "password": PASSWORD, "full_name": "X"}).status_code == 403


def test_admin_invite_returns_the_setup_link_when_email_cannot_be_sent(client, admin, monkeypatch):
    monkeypatch.delenv("ALLOW_SELF_REGISTRATION", raising=False)
    email = _email("invited")
    r = client.post("/admin/users/invite", json={"email": email, "full_name": "Invited", "role": "provider"}, **admin)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["email"] == email and body["role"] == "provider"
    assert body["email_sent"] is False and "/reset-password?token=" in body["setup_url"]
    assert body["setup_link_expires_in_hours"] == 72
    # The invited account has no usable password until setup.
    assert client.post("/users/login", json={"email": email, "password": PASSWORD}).status_code == 401


def test_admin_create_returns_a_temporary_password_that_signs_in(client, admin, monkeypatch):
    monkeypatch.delenv("ALLOW_SELF_REGISTRATION", raising=False)
    email = _email("created")
    r = client.post("/admin/users/create", json={"email": email, "full_name": "Created"}, **admin)
    assert r.status_code == 201, r.text
    temp = r.json()["temporary_password"]
    client.cookies.clear()
    assert client.post("/users/login", json={"email": email, "password": temp}).status_code == 200


def test_invites_need_an_admin_and_an_allowed_email(client, admin):
    signed_in_only = {"cookies": admin["cookies"]}
    assert client.post("/admin/users/invite", json={"email": _email()}, **signed_in_only).status_code == 401
    r = client.post("/admin/users/invite", json={"email": _email(domain="gmail.com")}, **admin)
    assert r.status_code == 403
    assert client.post("/admin/users/invite", json={"email": _email(), "role": "superuser"}, **admin).status_code == 400
