"""
Admin-managed email allowlist: individual emails from other domains (e.g.
testers) can be invited and sign in; the domain rule still applies to
everyone else; removing an email refuses new sign-ins.
"""
import uuid

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services import access_policy
from backend.services.security import limiter

PASSWORD = "ClassPass123!"
ADMIN_TOKEN = "test-admin-token-" + "f" * 24


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


def test_rule_is_domain_or_allowlist():
    tester = f"Tester-{uuid.uuid4().hex[:8]}@Gmail.com"
    assert access_policy.email_allowed("someone@realdiag.com")
    assert access_policy.email_allowed("someone@ELIONYXHEALTH.com")
    assert not access_policy.email_allowed(tester)
    access_policy.add_to_allowlist(tester, "validation tester", "admin")
    assert access_policy.email_allowed(tester.lower())
    assert access_policy.remove_from_allowlist(tester)
    assert not access_policy.email_allowed(tester)
    with pytest.raises(ValueError):
        access_policy.add_to_allowlist("not-an-email", None, "admin")


def test_allowlisted_tester_can_be_created_and_removed(client, admin):
    tester = f"tester-{uuid.uuid4().hex[:8]}@gmail.com"
    assert client.post("/admin/users/create", json={"email": tester}, **admin).status_code == 403

    r = client.post("/admin/allowlist", json={"email": tester, "note": "validation"}, **admin)
    assert r.status_code == 201 and r.json()["email"] == tester
    listed = client.get("/admin/allowlist", **admin).json()
    assert "realdiag.com" in listed["approved_domains"]
    assert any(e["email"] == tester and e["note"] == "validation" for e in listed["emails"])

    temp = client.post("/admin/users/create", json={"email": tester}, **admin).json()["temporary_password"]
    client.cookies.clear()
    assert client.post("/users/login", json={"email": tester, "password": temp}).status_code == 200
    client.cookies.clear()

    assert client.post("/admin/allowlist/remove", json={"email": tester}, **admin).status_code == 200
    r = client.post("/users/login", json={"email": tester, "password": temp})
    assert r.status_code == 403 and "allowlist" in r.json()["detail"]
    assert client.post("/admin/allowlist/remove", json={"email": tester}, **admin).status_code == 404


def test_allowlist_needs_the_admin_token(client, admin):
    assert client.get("/admin/allowlist", cookies=admin["cookies"]).status_code == 401
    assert client.post("/admin/allowlist", json={"email": "x@gmail.com"}, cookies=admin["cookies"]).status_code == 401
