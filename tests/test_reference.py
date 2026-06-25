"""
Reference API Tests
Tests for diagnostic rules and reference endpoints
"""

import pytest
from fastapi.testclient import TestClient


VALID_FAMILIES = [
    "neurology",
    "cardiology",
    "endocrinology",
    "pulmonology",
    "gastroenterology",
    "infectious_disease",
    "nephrology",
    "rheumatology",
    "dermatology",
    "psychiatry",
    "obstetrics_gynecology"
]


@pytest.mark.parametrize("family", VALID_FAMILIES)
def test_reference_valid_families(test_client: TestClient, family: str):
    """Test /reference/{family} endpoints for all valid families"""
    response = test_client.get(f"/reference/{family}")
    assert response.status_code == 200
    data = response.json()
    assert "family" in data
    assert "rules" in data
    assert "count" in data
    assert isinstance(data["rules"], list)
    assert data["count"] == len(data["rules"])


def test_reference_invalid_family(test_client: TestClient):
    """Test /reference/{family} with invalid family"""
    response = test_client.get("/reference/invalid_family")
    assert response.status_code == 404


def test_reference_cardiology_structure(test_client: TestClient):
    """Test cardiology rules have correct structure"""
    response = test_client.get("/reference/cardiology")
    assert response.status_code == 200
    data = response.json()
    
    if len(data["rules"]) > 0:
        rule = data["rules"][0]
        assert "id" in rule
        assert "label" in rule
        assert "presentations" in rule
        assert isinstance(rule["presentations"], list)


def test_reference_neurology_not_empty(test_client: TestClient):
    """Test neurology rules exist"""
    response = test_client.get("/reference/neurology")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] > 0
    assert len(data["rules"]) > 0


def test_reference_endocrinology_endpoint(test_client: TestClient):
    """Test specific endocrinology endpoint"""
    response = test_client.get("/reference/endocrinology")
    assert response.status_code == 200
    data = response.json()
    assert "family" in data
    assert "rules" in data


def test_reference_rules_have_icd10(test_client: TestClient):
    """Test that rules contain ICD-10 codes"""
    response = test_client.get("/reference/cardiology")
    assert response.status_code == 200
    data = response.json()
    
    if len(data["rules"]) > 0:
        # At least some rules should have ICD-10 codes
        has_icd10 = any("icd10" in rule for rule in data["rules"])
        assert has_icd10


def test_reference_rules_have_snomed(test_client: TestClient):
    """Test that rules contain SNOMED codes"""
    response = test_client.get("/reference/neurology")
    assert response.status_code == 200
    data = response.json()
    
    if len(data["rules"]) > 0:
        # At least some rules should have SNOMED codes
        has_snomed = any("snomed" in rule for rule in data["rules"])
        assert has_snomed


def test_reference_multiple_families(test_client: TestClient):
    """Test fetching multiple families in sequence"""
    families = ["cardiology", "neurology", "pulmonology"]
    results = []
    
    for family in families:
        response = test_client.get(f"/reference/{family}")
        assert response.status_code == 200
        data = response.json()
        results.append(data)
    
    # All should have returned data
    assert all(len(r["rules"]) > 0 for r in results)
    
    # Each family should be different
    assert results[0]["family"] != results[1]["family"]
