"""
Which routes answer without signing in (main.py PUBLIC_PATHS / PUBLIC_PREFIXES).
Everything else, including the API docs, metrics, the reference library,
education content and the offline bundle, needs a signed-in session.
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import PUBLIC_PATHS, PUBLIC_PREFIXES, app

NEEDS_LOGIN = ["/docs", "/redoc", "/openapi.json", "/metrics", "/reference/cardiology", "/reference/endocrinology",
               "/education/cases", "/education/quiz/questions", "/education/learning-objectives",
               "/offline/bundle", "/offline/bundle/version", "/diagnostic/trees", "/rules/all", "/admin/users"]


@pytest.fixture
def anonymous():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.mark.parametrize("path", NEEDS_LOGIN)
def test_needs_a_signed_in_session(anonymous, path):
    assert anonymous.get(path).status_code == 401


def test_the_public_list_is_only_sign_in_health_and_ehr_launch():
    assert PUBLIC_PATHS == {
        "/health", "/health/version", "/version", "/",
        "/users/login", "/users/register", "/users/forgot-password", "/users/reset-password",
        "/users/verify-email", "/users/resend-verification", "/mfa/login-verify",
        "/integration/symptom-search/patient",
    }
    assert PUBLIC_PREFIXES == ("/static/", "/smart/")


def test_public_routes_still_answer(anonymous, monkeypatch):
    monkeypatch.delenv("ALLOW_SELF_REGISTRATION", raising=False)
    assert anonymous.get("/health").status_code == 200
    assert anonymous.get("/version").status_code == 200
    assert anonymous.post("/users/login", json={}).status_code == 422  # reached the route, not the gate
    assert anonymous.post("/mfa/login-verify", json={}).status_code == 422
    assert anonymous.post("/users/register", json={"email": "a@realdiag.com", "password": "Passw0rd!!",
                                                    "full_name": "A"}).status_code == 403
    assert anonymous.get("/smart/session/status").status_code == 200
