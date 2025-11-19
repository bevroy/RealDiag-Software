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

from backend.main import app


@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, None, None]:
    """
    Create a test client for the FastAPI app.
    Session-scoped to reuse across all tests.
    """
    # Disable rate limiting for tests if it's enabled
    if hasattr(app.state, 'limiter'):
        app.state.limiter = None
    
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client


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
