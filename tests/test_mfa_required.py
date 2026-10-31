"""
Two-factor authentication for every account (REQUIRE_MFA, on by default):
an account without MFA signs in to a session that can only enroll; after
the first code is verified the session is replaced with a full one; later
sign-ins need a code; sessions without the MFA claim are refused; MFA
cannot be turned off; an admin can reset it.
"""
import time
import uuid

import pyotp
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.auth_service import create_access_token
from backend.services.security import limiter

PASSWORD = "ClassPass123!"
ADMIN_TOKEN = "test-admin-token-" + "g" * 24


@pytest.fixture
def client(monkeypatch):
    limiter.enabled = False
    monkeypatch.delenv("REQUIRE_MFA", raising=False)  # the default: required
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def _new_account(client):
    email = f"mfa-{uuid.uuid4().hex[:10]}@realdiag.com"
    r = client.post("/users/register", json={"email": email, "password": PASSWORD, "full_name": "M"})
    assert r.status_code == 201
    client.cookies.clear()
    return email


def _login(client, email):
    r = client.post("/users/login", json={"email": email, "password": PASSWORD})
    assert r.status_code == 200, r.text
    return r


def _enroll(client, email):
    """Sign in, enroll, verify the first code; returns (secret, full session cookie)."""
    r = _login(client, email)
    assert r.json()["mfa_setup_required"] is True
    setup = r.cookies.get("access_token")
    client.cookies.clear()
    secret = client.post("/mfa/enroll", cookies={"access_token": setup}).json()["secret"]
    r = client.post("/mfa/verify", json={"token": pyotp.TOTP(secret).now()}, cookies={"access_token": setup})
    assert r.status_code == 200 and r.json()["valid"] is True
    full = r.cookies.get("access_token")
    client.cookies.clear()
    assert full and full != setup
    return secret, setup, full


def test_without_mfa_the_session_can_only_enroll(client):
    email = _new_account(client)
    r = _login(client, email)
    assert r.json()["mfa_setup_required"] is True and r.json()["user"]["email"] == email
    setup = {"access_token": r.cookies.get("access_token")}
    client.cookies.clear()
    assert client.get("/users/me", cookies=setup).status_code == 200
    blocked = client.get("/rules/all", cookies=setup)
    assert blocked.status_code == 403 and blocked.json()["mfa_setup_required"] is True
    assert client.get("/offline/bundle/version", cookies=setup).status_code == 403


def test_enrolling_replaces_the_session_and_later_sign_ins_need_a_code(client):
    email = _new_account(client)
    secret, setup, full = _enroll(client, email)
    assert client.get("/rules/all", cookies={"access_token": full}).status_code == 200
    assert client.get("/rules/all", cookies={"access_token": setup}).status_code == 403

    r = _login(client, email)
    body = r.json()
    assert body["mfa_required"] is True and "user" not in body
    assert r.cookies.get("access_token") is None
    client.cookies.clear()
    wrong = client.post("/mfa/login-verify", json={"mfa_token": body["mfa_token"], "token": "000000"})
    assert wrong.status_code == 401 and wrong.json()["detail"] == "Invalid MFA code"
    assert client.post("/mfa/login-verify", json={"mfa_token": full, "token": "000000"}).status_code == 401
    # The next 30-second code: the one just used for enrollment is not accepted twice.
    code = pyotp.TOTP(secret).at(time.time() + 30)
    r = client.post("/mfa/login-verify", json={"mfa_token": body["mfa_token"], "token": code})
    assert r.status_code == 200
    session = r.cookies.get("access_token")
    client.cookies.clear()
    assert client.get("/rules/all", cookies={"access_token": session}).status_code == 200


def test_sessions_without_the_mfa_claim_are_refused(client):
    email = _new_account(client)
    user_id = client.post("/users/login", json={"email": email, "password": PASSWORD}).json()["user"]["user_id"]
    client.cookies.clear()
    old = create_access_token(user_id, email)  # as issued before MFA was required
    r = client.get("/rules/all", cookies={"access_token": old})
    assert r.status_code == 401 and "two-factor" in r.json()["detail"]


def test_mfa_cannot_be_disabled_while_required_and_admin_can_reset_it(client, monkeypatch):
    email = _new_account(client)
    _, _, full = _enroll(client, email)
    assert client.delete("/mfa/disable", cookies={"access_token": full}).status_code == 403

    monkeypatch.setenv("ADMIN_TOKEN", ADMIN_TOKEN)
    admin = {"headers": {"Authorization": f"Bearer {ADMIN_TOKEN}"}, "cookies": {"access_token": full}}
    r = client.post("/admin/users/reset-mfa", json={"email": email, "reason": "lost phone"}, **admin)
    assert r.status_code == 200 and r.json()["mfa_enabled"] is False
    assert _login(client, email).json()["mfa_setup_required"] is True


def test_mfa_can_be_turned_off_per_environment(client, monkeypatch):
    monkeypatch.setenv("REQUIRE_MFA", "0")
    email = _new_account(client)
    r = _login(client, email)
    assert "mfa_setup_required" not in r.json()
    session = r.cookies.get("access_token")
    client.cookies.clear()
    assert client.get("/rules/all", cookies={"access_token": session}).status_code == 200
