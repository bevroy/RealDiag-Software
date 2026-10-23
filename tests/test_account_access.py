"""
Account access for a class on one network:

- rate limits on the real limiter: 30 students registering and signing in from
  one IP are not blocked;
- wrong passwords lock the account (per account, not per IP);
- admin password reset, deactivation and reactivation;
- email failures are reported instead of silently swallowed.

Runs on the in-memory user store; the database path is covered by
test_account_access_db.py.
"""
import uuid
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services import auth_service
from backend.services.security import limiter

PASSWORD = "ClassPass123!"
ADMIN_TOKEN = "test-admin-token-" + "b" * 24


def _email(prefix="student"):
    return f"{prefix}-{uuid.uuid4().hex[:10]}@realdiag.com"


@pytest.fixture
def real_limits():
    """Turn the real slowapi limits on for one test (other tests disable them)."""
    was = limiter.enabled
    limiter.enabled = True
    limiter.reset()
    yield
    limiter.reset()
    limiter.enabled = was


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def admin(monkeypatch, client):
    """Request kwargs for an admin call: the API needs a signed-in session
    (global gate in main.py) and the admin token (verify_admin_token)."""
    monkeypatch.setenv("ADMIN_TOKEN", ADMIN_TOKEN)
    operator = _email("operator")
    _register(client, operator)
    session = client.post("/users/login", json={"email": operator, "password": PASSWORD}).cookies.get("access_token")
    client.cookies.clear()
    return {"headers": {"Authorization": f"Bearer {ADMIN_TOKEN}"}, "cookies": {"access_token": session}}


def _register(client, email, password=PASSWORD):
    r = client.post("/users/register", json={"email": email, "password": password, "full_name": "Student"})
    assert r.status_code == 201, r.text
    client.cookies.clear()
    return r.json()["user"]["user_id"]


def _login(client, email, password=PASSWORD):
    r = client.post("/users/login", json={"email": email, "password": password})
    client.cookies.clear()
    return r


# --- a class on one network ------------------------------------------------

def test_class_of_30_on_one_ip_can_register_and_sign_in(client, real_limits):
    # TestClient sends every request from the same address, like a campus NAT.
    emails = [_email("class") for _ in range(30)]
    for email in emails:
        _register(client, email)
    for i, email in enumerate(emails):
        if i % 5 == 0:  # some typos along the way
            assert _login(client, email, "wrong-password").status_code == 401
        assert _login(client, email).status_code == 200, email


def test_signed_in_requests_are_limited_per_account(client, real_limits):
    # /reference allows 100/minute; two students on one IP each get their own 100.
    cookies = []
    for _ in range(2):
        email = _email("ref")
        _register(client, email)
        r = client.post("/users/login", json={"email": email, "password": PASSWORD})
        cookies.append({"access_token": r.cookies.get("access_token")})
        client.cookies.clear()
    for jar in cookies:
        for _ in range(60):
            assert client.get("/reference/cardiology", cookies=jar).status_code == 200


# --- per-account lockout ---------------------------------------------------

def test_wrong_passwords_lock_only_that_account(client):
    victim, classmate = _email("victim"), _email("classmate")
    _register(client, victim)
    _register(client, classmate)

    for _ in range(auth_service.LOGIN_MAX_FAILED_ATTEMPTS - 1):
        assert _login(client, victim, "wrong-password").status_code == 401
    locked = _login(client, victim, "wrong-password")
    assert locked.status_code == 429
    assert "administrator" in locked.json()["detail"]
    assert int(locked.headers["Retry-After"]) > 0

    # Even the right password is refused while locked...
    assert _login(client, victim).status_code == 429
    # ...but a classmate on the same network is unaffected.
    assert _login(client, classmate).status_code == 200


def test_lockout_expires_and_success_resets_the_count(client):
    email = _email("expire")
    user_id = _register(client, email)
    for _ in range(auth_service.LOGIN_MAX_FAILED_ATTEMPTS):
        _login(client, email, "wrong-password")
    assert _login(client, email).status_code == 429

    auth_service.users_db[user_id]["locked_until"] = datetime.utcnow() - timedelta(seconds=1)
    assert _login(client, email).status_code == 200
    assert auth_service.users_db[user_id]["failed_login_count"] == 0

    # A successful sign-in resets the count, so earlier typos don't carry over.
    for _ in range(auth_service.LOGIN_MAX_FAILED_ATTEMPTS - 1):
        _login(client, email, "wrong-password")
    assert _login(client, email).status_code == 200
    assert _login(client, email, "wrong-password").status_code == 401


# --- admin tools -----------------------------------------------------------

@pytest.mark.parametrize("path", ["/admin/users/reset-password", "/admin/users/deactivate", "/admin/users/reactivate"])
def test_admin_tools_require_the_admin_token(client, admin, path):
    body = {"email": "x@realdiag.com"}
    assert client.post(path, json=body).status_code == 401                       # no session
    assert client.post(path, json=body, headers=admin["headers"]).status_code == 401  # token alone
    assert client.post(path, json=body, cookies=admin["cookies"]).status_code == 401  # session alone
    assert client.post(path, json=body, cookies=admin["cookies"],
                       headers={"Authorization": "Bearer wrong"}).status_code == 403


def test_admin_tools_need_an_account(client, admin):
    assert client.post("/admin/users/deactivate", json={}, **admin).status_code == 400
    assert client.post("/admin/users/deactivate", json={"email": _email("nobody")}, **admin).status_code == 404


def test_admin_reset_password_generates_a_temporary_password(client, admin):
    email = _email("reset")
    _register(client, email)
    for _ in range(auth_service.LOGIN_MAX_FAILED_ATTEMPTS):
        _login(client, email, "wrong-password")
    assert _login(client, email).status_code == 429

    r = client.post("/admin/users/reset-password", json={"email": email, "reason": "forgot"}, **admin)
    assert r.status_code == 200, r.text
    temporary = r.json()["temporary_password"]
    assert len(temporary) >= 12

    assert _login(client, email).status_code == 401          # old password gone
    assert _login(client, email, temporary).status_code == 200  # lockout cleared too


def test_admin_reset_password_with_chosen_password(client, admin):
    email = _email("chosen")
    user_id = _register(client, email)
    r = client.post("/admin/users/reset-password", json={"user_id": user_id, "new_password": "NewChosen123!"},
                    **admin)
    assert r.status_code == 200
    assert "temporary_password" not in r.json()
    assert _login(client, email, "NewChosen123!").status_code == 200
    short = client.post("/admin/users/reset-password", json={"user_id": user_id, "new_password": "short"},
                        **admin)
    assert short.status_code == 400


def test_deactivate_blocks_sign_in_and_existing_sessions(client, admin):
    email = _email("deact")
    _register(client, email)
    session = client.post("/users/login", json={"email": email, "password": PASSWORD}).cookies.get("access_token")
    client.cookies.clear()
    assert client.get("/users/me", cookies={"access_token": session}).status_code == 200

    r = client.post("/admin/users/deactivate", json={"email": email, "reason": "left course"}, **admin)
    assert r.status_code == 200 and r.json()["is_active"] is False

    denied = _login(client, email)
    assert denied.status_code == 403 and "deactivated" in denied.json()["detail"]
    # A wrong password still just says "incorrect": deactivation isn't revealed to a guesser.
    assert _login(client, email, "wrong-password").status_code == 401
    assert client.get("/users/me", cookies={"access_token": session}).status_code == 403
    assert client.get("/diagnostic/trees", cookies={"access_token": session}).status_code == 403

    assert client.post("/admin/users/reactivate", json={"email": email}, **admin).json()["is_active"] is True
    assert _login(client, email).status_code == 200
    assert client.get("/users/me", cookies={"access_token": session}).status_code == 200


# --- email failures are visible --------------------------------------------

@pytest.mark.parametrize("who", ["existing", "unknown"])
def test_forgot_password_reports_when_email_cannot_be_sent(client, monkeypatch, who):
    from backend.services import email_service
    monkeypatch.setattr(email_service, "SMTP_USER", "")
    monkeypatch.setattr(email_service, "SMTP_PASSWORD", "")
    email = _email("forgot")
    if who == "existing":
        _register(client, email)
    r = client.post("/users/forgot-password", json={"email": email})
    # Same answer whether or not the account exists: no enumeration.
    assert r.status_code == 503
    assert "administrator" in r.json()["detail"]


def test_smtp_failure_returns_false_and_uses_a_timeout(monkeypatch):
    from backend.services import email_service
    monkeypatch.setattr(email_service, "SMTP_USER", "user")
    monkeypatch.setattr(email_service, "SMTP_PASSWORD", "pass")
    seen = {}

    class Blocked:
        def __init__(self, host, port, timeout=None):
            seen["timeout"] = timeout
            raise OSError("[Errno 101] Network is unreachable")

    monkeypatch.setattr(email_service.smtplib, "SMTP", Blocked)
    assert email_service.send_password_reset_email("a@realdiag.com", "tok") is False
    assert email_service.send_welcome_email("a@realdiag.com") is False
    assert email_service.send_verification_email("a@realdiag.org", "tok") is False
    assert seen["timeout"] == email_service.SMTP_TIMEOUT_SECONDS > 0


def test_email_configured_reflects_credentials(monkeypatch):
    from backend.services import email_service
    monkeypatch.setattr(email_service, "SMTP_USER", "")
    assert email_service.email_configured() is False
    monkeypatch.setattr(email_service, "SMTP_USER", "u")
    monkeypatch.setattr(email_service, "SMTP_PASSWORD", "p")
    assert email_service.email_configured() is True
