"""
Education Features Tests
Tests for medical training endpoints
"""

import pytest
from fastapi.testclient import TestClient
import uuid


@pytest.fixture(scope="module")
def authenticated_user(test_client: TestClient) -> dict:
    """Register a test user and attach its auth cookie to test_client.

    TestClient drops Secure-flagged cookies on the http:// test host, so the
    token is copied from the response directly instead of relying on the
    client's cookie jar to persist it across requests.
    """
    email = f"edu-test-{uuid.uuid4().hex[:8]}@realdiag.com"
    response = test_client.post(
        "/users/register",
        json={
            "email": email,
            "password": "TestPass123!",
            "full_name": "Education Test User",
        },
    )
    assert response.status_code == 201
    test_client.cookies.set("access_token", response.cookies.get("access_token"))
    return response.json()["user"]


def test_education_cases_endpoint(test_client: TestClient):
    """Test /education/cases endpoint"""
    response = test_client.get("/education/cases")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_education_cases_with_specialty(test_client: TestClient):
    """Test filtering cases by specialty"""
    response = test_client.get("/education/cases?specialty=cardiology")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_education_cases_with_difficulty(test_client: TestClient):
    """Test filtering cases by difficulty"""
    response = test_client.get("/education/cases?difficulty=intermediate")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_education_quiz_questions(test_client: TestClient):
    """Test /education/quiz/questions endpoint"""
    response = test_client.get("/education/quiz/questions?count=5")
    assert response.status_code == 200
    data = response.json()
    assert "questions" in data
    assert "count" in data


def test_education_quiz_submit(test_client: TestClient, authenticated_user: dict):
    """Test submitting a quiz answer"""
    payload = {
        "attempt_id": "test_attempt_001",
        "user_id": "test_user",
        "question_id": "Q001",
        "selected_answers": ["B"],
        "correct": False,
        "time_taken": 30,
        "timestamp": "2025-11-19T12:00:00Z"
    }
    response = test_client.post("/education/quiz/submit", json=payload)
    # May return 404 if question doesn't exist, or 200 if it does
    assert response.status_code in [200, 404]


def test_education_progress(test_client: TestClient, authenticated_user: dict):
    """Test getting user progress"""
    response = test_client.get(f"/education/progress/{authenticated_user['user_id']}")
    assert response.status_code == 200
    data = response.json()
    # Either has progress data or message about no progress
    assert "user_id" in data or "message" in data


def test_education_flashcards_due(test_client: TestClient, authenticated_user: dict):
    """Test getting due flashcards"""
    response = test_client.get("/education/flashcards/due?user_id=test_user&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "flashcards" in data
    assert "count" in data


def test_education_flashcard_review(test_client: TestClient, authenticated_user: dict):
    """Test reviewing a flashcard"""
    payload = {
        "user_id": "test_user",
        "card_id": "FC001",
        "quality": 4,
        "timestamp": "2025-11-19T12:00:00Z"
    }
    response = test_client.post("/education/flashcards/review", json=payload)
    # May return 404 if card doesn't exist
    assert response.status_code in [200, 404]


def test_education_learning_objectives(test_client: TestClient):
    """Test getting learning objectives"""
    response = test_client.get("/education/learning-objectives")
    assert response.status_code == 200
    data = response.json()
    assert "objectives" in data
    assert "count" in data


def test_education_cases_search(test_client: TestClient):
    """Test searching cases"""
    response = test_client.get("/education/cases/search/chest%20pain")
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "results" in data
    assert "count" in data


def test_education_quiz_invalid_count(test_client: TestClient):
    """Test quiz with invalid question count"""
    response = test_client.get("/education/quiz/questions?count=100")
    assert response.status_code in [200, 400]  # May limit to max count


def test_education_flashcard_invalid_quality(test_client: TestClient, authenticated_user: dict):
    """Test flashcard review with invalid quality"""
    payload = {
        "user_id": "test_user",
        "card_id": "FC001",
        "quality": 10,  # Invalid, should be 0-5
        "timestamp": "2025-11-19T12:00:00Z"
    }
    response = test_client.post("/education/flashcards/review", json=payload)
    assert response.status_code in [400, 404, 422]
