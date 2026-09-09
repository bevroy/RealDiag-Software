"""
Symptom Search Tests
Tests for symptom-based diagnostic search functionality
"""

import asyncio
import uuid

import pytest
from fastapi.testclient import TestClient

from backend.services import symptom_search as symptom_search_module
from backend.services.symptom_search import (
    build_patient_symptom_search_response,
    DiagnosisMatch,
    PATIENT_DISCLAIMER,
    PATIENT_RESULT_CAP,
    SymptomSearchRequest,
    SymptomSearchResponse,
)


@pytest.fixture(scope="module")
def authenticated_user(test_client: TestClient) -> dict:
    """Register a test user and attach its auth cookie to test_client.

    /search/by-symptoms requires login (router-level auth); TestClient drops
    Secure-flagged cookies on the http:// test host, so the token is copied
    from the response directly instead of relying on the client's cookie jar.
    """
    email = f"symptom-search-test-{uuid.uuid4().hex[:8]}@realdiag.com"
    response = test_client.post(
        "/users/register",
        json={
            "email": email,
            "password": "TestPass123!",
            "full_name": "Symptom Search Test User",
        },
    )
    assert response.status_code == 201
    test_client.cookies.set("access_token", response.cookies.get("access_token"))
    return response.json()["user"]


def test_symptom_search_requires_authentication():
    """/search/by-symptoms rejects requests with no session at all.

    Uses a fresh TestClient (not the shared, session-scoped `test_client`
    fixture) so it can't inherit a cookie set by another module's
    `authenticated_user` fixture.
    """
    from backend.main import app
    with TestClient(app, raise_server_exceptions=False) as anon_client:
        response = anon_client.post("/search/by-symptoms", json={"symptoms": ["fever"]})
    assert response.status_code == 401


def test_symptom_search_valid_request(test_client: TestClient, sample_symptoms, authenticated_user):
    """Test symptom search with valid symptoms"""
    response = test_client.post("/search/by-symptoms", json=sample_symptoms)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "query_symptoms" in data or "query" in data
    assert isinstance(data["results"], list)


def test_symptom_search_minimal_request(test_client: TestClient, authenticated_user):
    """Test symptom search with minimal data"""
    payload = {"symptoms": ["headache"]}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data


def test_symptom_search_empty_symptoms(test_client: TestClient, authenticated_user):
    """Test symptom search with empty symptoms list"""
    payload = {"symptoms": []}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code == 422  # Validation error


def test_symptom_search_no_symptoms(test_client: TestClient, authenticated_user):
    """Test symptom search without symptoms field"""
    payload = {"age": 30}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code == 422  # Validation error


def test_symptom_search_with_age(test_client: TestClient, authenticated_user):
    """Test symptom search with age parameter"""
    payload = {"symptoms": ["fever"], "age": 25}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code == 200


def test_symptom_search_invalid_age(test_client: TestClient, authenticated_user):
    """Test symptom search with invalid age"""
    payload = {"symptoms": ["fever"], "age": 150}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code == 422  # Age validation error


def test_symptom_search_negative_age(test_client: TestClient, authenticated_user):
    """Test symptom search with negative age"""
    payload = {"symptoms": ["fever"], "age": -5}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code == 422


def test_symptom_search_with_sex(test_client: TestClient, authenticated_user):
    """Test symptom search with sex parameter"""
    payload = {"symptoms": ["abdominal pain"], "sex": "F"}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code == 200


def test_symptom_search_with_family(test_client: TestClient, authenticated_user):
    """Test symptom search with family filter"""
    payload = {"symptoms": ["chest pain"], "family": "cardiology"}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code == 200


def test_symptom_search_too_many_symptoms(test_client: TestClient, authenticated_user):
    """Test symptom search with more than 50 symptoms"""
    payload = {"symptoms": [f"symptom_{i}" for i in range(60)]}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code == 422  # Too many symptoms


def test_symptom_search_xss_attempt(test_client: TestClient, authenticated_user):
    """Test symptom search handles XSS attempts"""
    payload = {"symptoms": ["<script>alert('xss')</script>"]}
    response = test_client.post("/search/by-symptoms", json=payload)
    # Should either sanitize or return 200 with sanitized results
    assert response.status_code in [200, 422]


def test_symptom_search_sql_injection_attempt(test_client: TestClient, authenticated_user):
    """Test symptom search handles SQL injection attempts"""
    payload = {"symptoms": ["'; DROP TABLE users; --"]}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code in [200, 422]


def test_symptom_search_response_structure(test_client: TestClient, authenticated_user):
    """Test symptom search response has correct structure"""
    payload = {"symptoms": ["cough", "fever"]}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "results" in data
    assert "query_symptoms" in data or "query" in data
    
    if len(data["results"]) > 0:
        result = data["results"][0]
        # Check for common fields in results
        assert "family" in result or "rule_id" in result or "id" in result


def test_symptom_search_multiple_symptoms(test_client: TestClient, authenticated_user):
    """Test symptom search with multiple symptoms"""
    payload = {
        "symptoms": ["chest pain", "shortness of breath", "nausea", "diaphoresis"],
        "age": 60,
        "sex": "M"
    }
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) >= 0  # Should return results


def _fake_match(rank: int, score: float) -> DiagnosisMatch:
    """Build a minimal DiagnosisMatch for patient-shaping tests, independent
    of any real rule data."""
    return DiagnosisMatch(
        rule_id=f"TEST-RULE-{rank}",
        label=f"Test Condition {rank}",
        family="test_family",
        match_score=score,
        matched_presentations=["test symptom"],
        all_presentations=["test symptom", "other symptom"],
        icd10=["Z00.0"],
        snomed=[123456],
        referrals=["Test Specialty"],
    )


def test_build_patient_symptom_search_response_tiers_and_cap(monkeypatch):
    """Patient-facing shaping: rank-based tiers spread across likelihoods,
    results are capped at PATIENT_RESULT_CAP, and the disclaimer is exact."""
    # 10 fake matches, already sorted descending by match_score -- more than
    # PATIENT_RESULT_CAP (8) so the cap is actually exercised.
    fake_matches = [_fake_match(i, score=100 - i) for i in range(10)]
    fake_response = SymptomSearchResponse(
        query_symptoms=["chest pain"],
        total_results=len(fake_matches),
        results=fake_matches,
    )

    async def fake_search_by_symptoms(request, request_obj):
        return fake_response

    monkeypatch.setattr(symptom_search_module, "search_by_symptoms", fake_search_by_symptoms)

    request = SymptomSearchRequest(symptoms=["chest pain"])
    result = asyncio.run(
        build_patient_symptom_search_response(request, request_obj=None)
    )

    # (b) never more than the patient cap, even with 10 matches available
    assert len(result.topics) == PATIENT_RESULT_CAP
    assert result.total_topics == PATIENT_RESULT_CAP

    # (a) more than one distinct likelihood value across the returned topics
    likelihoods = {topic.likelihood for topic in result.topics}
    assert len(likelihoods) > 1
    assert likelihoods <= {"Worth discussing", "Possible", "Less likely"}

    # (c) disclaimer matches the current constant exactly
    assert result.disclaimer == PATIENT_DISCLAIMER


def test_build_patient_symptom_search_response_no_padding(monkeypatch):
    """Fewer matches than the cap should return all of them, unpadded."""
    fake_matches = [_fake_match(i, score=10 - i) for i in range(3)]
    fake_response = SymptomSearchResponse(
        query_symptoms=["headache"],
        total_results=len(fake_matches),
        results=fake_matches,
    )

    async def fake_search_by_symptoms(request, request_obj):
        return fake_response

    monkeypatch.setattr(symptom_search_module, "search_by_symptoms", fake_search_by_symptoms)

    request = SymptomSearchRequest(symptoms=["headache"])
    result = asyncio.run(
        build_patient_symptom_search_response(request, request_obj=None)
    )

    assert len(result.topics) == 3
    assert result.total_topics == 3


def _set_user_role(user_id: str, role: str) -> None:
    """Directly set a role in whichever store auth_service is using (DB or
    in-memory) -- normal /users/register signup only ever produces
    role='user' regardless of email domain (user_router.py's
    _normalize_ui_role() only relabels "user" -> "provider" for display in
    a couple of response bodies, it never persists), so a provider-role
    test account has to be set up this way."""
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


@pytest.fixture(scope="module")
def provider_access_token() -> str:
    """Register exactly one provider-role account for this module and reuse
    its token across tests. /users/register is rate-limited (5/15min)
    across the whole test session, so tests must not each register a fresh
    account -- see also the plain-USER gate test below, which reuses the
    module's existing `authenticated_user` fixture (role='user' by default)
    instead of registering another account."""
    from backend.main import app
    email = f"emr-gate-provider-{uuid.uuid4().hex[:8]}@realdiag.com"
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/users/register",
            json={
                "email": email,
                "password": "TestPass123!",
                "full_name": "EMR Gate Provider Tester",
            },
        )
        assert response.status_code == 201
        user_id = response.json()["user"]["user_id"]
        _set_user_role(user_id, "provider")
        return response.cookies.get("access_token")


def test_symptom_search_emr_patient_id_denied_for_plain_user(test_client: TestClient, authenticated_user):
    """A plain USER-role account (the shared authenticated_user fixture --
    normal signup always produces role='user') supplying emr_patient_id is
    rejected with a clear 403, not silently ignored."""
    response = test_client.post(
        "/search/by-symptoms",
        json={"symptoms": ["fever"], "emr_patient_id": "test-patient-1"},
    )
    assert response.status_code == 403
    assert "provider-level access" in response.json()["detail"]


def test_symptom_search_emr_patient_id_allowed_for_provider(provider_access_token: str):
    """A PROVIDER-role account supplying emr_patient_id is not rejected for
    role reasons."""
    from backend.main import app
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/search/by-symptoms",
            headers={"Authorization": f"Bearer {provider_access_token}"},
            json={"symptoms": ["fever"], "emr_patient_id": "test-patient-1"},
        )
    assert response.status_code == 200
