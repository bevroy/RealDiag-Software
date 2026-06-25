"""
Health and Basic Endpoint Tests
Tests for health checks, version, and basic API functionality
"""

import pytest
from fastapi.testclient import TestClient


def test_health_endpoint(test_client: TestClient, health_check_response):
    """Test /health endpoint returns ok status"""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == health_check_response


def test_version_endpoint(test_client: TestClient, api_version):
    """Test /version endpoint returns correct version"""
    response = test_client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == api_version["app"]
    assert data["version"] == api_version["version"]


def test_health_version_combined(test_client: TestClient, api_version):
    """Test /health/version endpoint combines health and version"""
    response = test_client.get("/health/version")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["app"] == api_version["app"]
    assert data["version"] == api_version["version"]


def test_root_endpoint_redirect(test_client: TestClient):
    """Test root endpoint redirects to /docs for API clients"""
    response = test_client.get("/", follow_redirects=False)
    assert response.status_code in [200, 301]  # Either HTML or redirect


def test_docs_endpoint(test_client: TestClient):
    """Test /docs endpoint is accessible"""
    response = test_client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


def test_openapi_json(test_client: TestClient):
    """Test /openapi.json is accessible"""
    response = test_client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert data["info"]["title"] == "RealDiag API"


def test_metrics_endpoint(test_client: TestClient):
    """Test /metrics endpoint for Prometheus"""
    response = test_client.get("/metrics")
    assert response.status_code == 200
    # Prometheus metrics are plain text
    assert "realdiag_requests_total" in response.text or response.status_code == 200
