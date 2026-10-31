"""
Pytest Configuration and Fixtures
Shared test fixtures for all test modules
"""

import pytest
import sys
import os
from pathlib import Path
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Disable rate limiting for tests
os.environ["TESTING"] = "1"

# auth_service refuses to start without a real JWT_SECRET_KEY; provide a
# non-placeholder test-only value if one isn't already set in the environment.
os.environ.setdefault("JWT_SECRET_KEY", "test-only-" + "a" * 32)

# Production is invite-only (access_policy). Most tests create their accounts
# through /users/register, so the suite turns self-registration back on;
# tests/test_invite_only.py checks the invite-only default.
os.environ.setdefault("ALLOW_SELF_REGISTRATION", "1")
# Likewise MFA is required in production; tests sign in with a password only
# and tests/test_mfa_required.py checks the requirement.
os.environ.setdefault("REQUIRE_MFA", "0")

from backend.main import app


@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, None, None]:
    """
    Create a test client for the FastAPI app.
    Session-scoped to reuse across all tests.
    """
    # Disable rate limiting for tests if it's enabled. app.state.limiter is
    # only consulted by the RateLimitExceeded handler -- the @limiter.limit(...)
    # decorators on individual routes (e.g. /users/register) are bound to the
    # security.py module-level Limiter singleton directly, so it has to be
    # disabled there too or multi-registration tests hit the real 5/15min cap.
    if hasattr(app.state, 'limiter'):
        app.state.limiter = None
    try:
        from backend.services.security import limiter as _security_limiter
        _security_limiter.enabled = False
    except ImportError:
        pass

    with TestClient(app, raise_server_exceptions=False) as client:
        yield client


@pytest.fixture(scope="session")
def session_token(test_client: TestClient) -> str:
    """A signed-in session for tests of routes that need login."""
    import uuid
    email = f"suite-{uuid.uuid4().hex[:8]}@realdiag.com"
    response = test_client.post("/users/register", json={"email": email, "password": "SuitePass123!", "full_name": "Suite"})
    assert response.status_code == 201, response.text
    test_client.cookies.clear()
    return response.cookies.get("access_token")


@pytest.fixture
def signed_in(test_client: TestClient, session_token: str):
    """Attach the suite's signed-in session to test_client for one test."""
    test_client.cookies.set("access_token", session_token)
    yield
    test_client.cookies.clear()


@pytest.fixture(scope="session")
def sample_symptoms() -> Dict[str, Any]:
    """Sample symptom data for testing"""
    return {
        "symptoms": ["chest pain", "shortness of breath", "diaphoresis"],
        "age": 55,
        "sex": "M"
    }


@pytest.fixture(scope="session")
def sample_clinical_case() -> Dict[str, Any]:
    """Sample clinical case for education testing"""
    return {
        "case_id": "TEST-001",
        "title": "Test Case: Acute Chest Pain",
        "specialty": "cardiology",
        "difficulty": "intermediate",
        "presentation": "55-year-old man with chest pain",
        "correct_diagnosis": "CARD-STEMI"
    }


@pytest.fixture(scope="function")
def mock_user() -> Dict[str, str]:
    """Mock user for authentication tests"""
    return {
        "user_id": "test_user_001",
        "email": "test@example.com",
        "username": "testuser"
    }


@pytest.fixture(scope="function")
def health_check_response() -> Dict[str, bool]:
    """Expected health check response"""
    return {"ok": True}


@pytest.fixture(scope="session")
def api_version() -> Dict[str, str]:
    """Expected API version response"""
    return {
        "app": "RealDiag",
        "version": "1.4.0"
    }


@pytest.fixture(autouse=True)
def reset_test_data():
    """Reset test data before each test"""
    # Add any cleanup logic here
    yield
    # Cleanup after test
    pass
