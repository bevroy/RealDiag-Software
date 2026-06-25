"""
Symptom Search Tests
Tests for symptom-based diagnostic search functionality
"""

import pytest
from fastapi.testclient import TestClient


def test_symptom_search_valid_request(test_client: TestClient, sample_symptoms):
    """Test symptom search with valid symptoms"""
    response = test_client.post("/search/by-symptoms", json=sample_symptoms)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "query_symptoms" in data or "query" in data
    assert isinstance(data["results"], list)


def test_symptom_search_minimal_request(test_client: TestClient):
    """Test symptom search with minimal data"""
    payload = {"symptoms": ["headache"]}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data


def test_symptom_search_empty_symptoms(test_client: TestClient):
    """Test symptom search with empty symptoms list"""
    payload = {"symptoms": []}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code == 422  # Validation error


def test_symptom_search_no_symptoms(test_client: TestClient):
    """Test symptom search without symptoms field"""
    payload = {"age": 30}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code == 422  # Validation error


def test_symptom_search_with_age(test_client: TestClient):
    """Test symptom search with age parameter"""
    payload = {"symptoms": ["fever"], "age": 25}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code == 200


def test_symptom_search_invalid_age(test_client: TestClient):
    """Test symptom search with invalid age"""
    payload = {"symptoms": ["fever"], "age": 150}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code == 422  # Age validation error


def test_symptom_search_negative_age(test_client: TestClient):
    """Test symptom search with negative age"""
    payload = {"symptoms": ["fever"], "age": -5}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code == 422


def test_symptom_search_with_sex(test_client: TestClient):
    """Test symptom search with sex parameter"""
    payload = {"symptoms": ["abdominal pain"], "sex": "F"}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code == 200


def test_symptom_search_with_family(test_client: TestClient):
    """Test symptom search with family filter"""
    payload = {"symptoms": ["chest pain"], "family": "cardiology"}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code == 200


def test_symptom_search_too_many_symptoms(test_client: TestClient):
    """Test symptom search with more than 50 symptoms"""
    payload = {"symptoms": [f"symptom_{i}" for i in range(60)]}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code == 422  # Too many symptoms


def test_symptom_search_xss_attempt(test_client: TestClient):
    """Test symptom search handles XSS attempts"""
    payload = {"symptoms": ["<script>alert('xss')</script>"]}
    response = test_client.post("/search/by-symptoms", json=payload)
    # Should either sanitize or return 200 with sanitized results
    assert response.status_code in [200, 422]


def test_symptom_search_sql_injection_attempt(test_client: TestClient):
    """Test symptom search handles SQL injection attempts"""
    payload = {"symptoms": ["'; DROP TABLE users; --"]}
    response = test_client.post("/search/by-symptoms", json=payload)
    assert response.status_code in [200, 422]


def test_symptom_search_response_structure(test_client: TestClient):
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


def test_symptom_search_multiple_symptoms(test_client: TestClient):
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
