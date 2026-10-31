"""
Integration API Key Tests
Covers persistence (api_key_store), the create/list/revoke endpoints in
integration_router.py, and that a key survives a simulated backend restart.
"""

import importlib
import os
import uuid

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services import api_key_store


def _register_access_token(label: str) -> str:
    email = f"api-key-test-{label}-{uuid.uuid4().hex[:8]}@realdiag.com"
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/users/register",
            json={
                "email": email,
                "password": "TestPass123!",
                "full_name": f"API Key Test {label.title()}",
            },
        )
        assert response.status_code == 201
        return response.cookies.get("access_token")


@pytest.fixture(scope="module")
def owner_token() -> str:
    return _register_access_token("owner")


@pytest.fixture(scope="module")
def other_user_token() -> str:
    return _register_access_token("other")


def _create_key(token: str, name: str = "test key") -> dict:
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/integration/api-keys",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": name, "scopes": ["read"]},
        )
    assert response.status_code == 200
    return response.json()


def test_create_and_use_api_key_authenticates(owner_token: str):
    """A freshly created key authenticates a real protected endpoint via
    X-API-Key, and the raw key is only ever returned at creation time."""
    created = _create_key(owner_token)
    assert created["api_key"].startswith("rdiag_")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/integration/symptom-search/patient",
            headers={"X-API-Key": created["api_key"]},
            json={"symptoms": ["chest pain"]},
        )
    assert response.status_code == 200


def test_list_api_keys_never_exposes_raw_key_or_hash(owner_token: str):
    created = _create_key(owner_token, name="list-test-key")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get(
            "/integration/api-keys",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
    assert response.status_code == 200
    body = response.json()
    matching = [k for k in body["api_keys"] if k["key_id"] == created["key_id"]]
    assert len(matching) == 1
    key_entry = matching[0]
    assert "key" not in key_entry
    assert "key_hash" not in key_entry
    assert key_entry["key_prefix"] == created["api_key"][:14]


def test_revoke_api_key_by_owner_then_rejected(owner_token: str):
    created = _create_key(owner_token, name="revoke-me")

    with TestClient(app, raise_server_exceptions=False) as client:
        revoke_response = client.delete(
            f"/integration/api-keys/{created['key_id']}",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert revoke_response.status_code == 200

        auth_response = client.post(
            "/integration/symptom-search/patient",
            headers={"X-API-Key": created["api_key"]},
            json={"symptoms": ["chest pain"]},
        )
    assert auth_response.status_code == 401
    assert auth_response.json()["detail"] == "API key revoked"


def test_revoke_api_key_rejected_for_non_owner_non_admin(owner_token: str, other_user_token: str):
    created = _create_key(owner_token, name="not-yours")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.delete(
            f"/integration/api-keys/{created['key_id']}",
            headers={"Authorization": f"Bearer {other_user_token}"},
        )
    assert response.status_code == 403


def test_revoke_nonexistent_key_returns_404(owner_token: str):
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.delete(
            "/integration/api-keys/key_does_not_exist",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
    assert response.status_code == 404


def test_store_create_get_list_revoke_round_trip():
    """Direct unit-level coverage of api_key_store's in-memory fallback
    (exercised here whenever no DATABASE_URL is configured, same as the
    rest of this test suite)."""
    created = api_key_store.create_api_key(
        name="unit-test-key", scopes=["read"], user_id="user_unit_test", expires_at=None,
    )
    assert created["revoked"] is False

    fetched = api_key_store.get_api_key_by_raw(created["raw_key"])
    assert fetched is not None
    assert fetched["key_id"] == created["key_id"]
    assert fetched["user_id"] == "user_unit_test"

    listed = api_key_store.list_api_keys_for_user("user_unit_test")
    assert any(k["key_id"] == created["key_id"] for k in listed)

    assert api_key_store.revoke_api_key(created["key_id"]) is True
    revoked = api_key_store.get_api_key_by_raw(created["raw_key"])
    assert revoked["revoked"] is True

    assert api_key_store.revoke_api_key("key_never_existed") is False


def test_api_key_persists_across_simulated_restart():
    """Reconnects to a real (SQLite) database from scratch, mid-test, to
    prove keys are read from durable storage rather than an in-process
    dict that would be lost on a real backend restart. Must run last in
    this file: reloading backend.services.database/api_key_store rebinds
    process-wide module state, which would otherwise reset the in-memory
    fallback (_api_keys_db) used by the tests above."""
    import tempfile

    original_database_url = os.environ.get("DATABASE_URL")
    tmp_dir = tempfile.mkdtemp()
    db_path = os.path.join(tmp_dir, "api_keys_restart_test.db")
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    from backend.services import database as database_module

    try:
        importlib.reload(database_module)
        importlib.reload(api_key_store)
        assert database_module.DATABASE_AVAILABLE is True
        database_module.init_database()

        created = api_key_store.create_api_key(
            name="restart-test-key", scopes=["read"], user_id="user_restart_test", expires_at=None,
        )
        raw_key = created["raw_key"]

        # Simulate a backend restart: drop all in-process module state and
        # reconnect to the same on-disk database from a clean slate.
        importlib.reload(database_module)
        importlib.reload(api_key_store)
        assert database_module.DATABASE_AVAILABLE is True

        fetched = api_key_store.get_api_key_by_raw(raw_key)
        assert fetched is not None
        assert fetched["user_id"] == "user_restart_test"
        assert fetched["revoked"] is False

        # Revocation also persists across the simulated restart.
        assert api_key_store.revoke_api_key(created["key_id"]) is True
        importlib.reload(database_module)
        importlib.reload(api_key_store)
        revoked = api_key_store.get_api_key_by_raw(raw_key)
        assert revoked is not None
        assert revoked["revoked"] is True
    finally:
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        importlib.reload(database_module)
        importlib.reload(api_key_store)


def test_patient_search_rejects_chart_data(owner_token: str):
    """The patient-facing search never pulls an EHR chart: emr_patient_id is refused
    with a clear 400 (before, it reached the clinician path without a user and failed)."""
    created = _create_key(owner_token, name="no-chart-data")
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/integration/symptom-search/patient",
            headers={"X-API-Key": created["api_key"]},
            json={"symptoms": ["chest pain"], "emr_patient_id": "patient-123"},
        )
        plain = client.post(
            "/integration/symptom-search/patient",
            headers={"X-API-Key": created["api_key"]},
            json={"symptoms": ["chest pain"]},
        )
    assert response.status_code == 400
    assert "emr_patient_id is not accepted on the patient-facing search" in response.json()["detail"]
    assert plain.status_code == 200
