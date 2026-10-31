"""
/diagnose endpoints: GET /diagnostic/trees, GET /diagnostic/trees/{id}/inputs
and POST /diagnostic/evaluate/{id}. All require sign-in (the frontend must send
the login cookie), and tree responses carry the review status and notice.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture(scope="module")
def cookies(client):
    response = client.post(
        "/users/register",
        json={
            "email": f"diagnose-walk-{uuid.uuid4().hex[:8]}@realdiag.com",
            "password": "TestPass123!",
            "full_name": "Diagnose Walk Tester",
        },
    )
    assert response.status_code == 201
    return {"access_token": response.cookies.get("access_token")}


@pytest.mark.parametrize("method,path", [
    ("get", "/diagnostic/trees"),
    ("get", "/diagnostic/trees/ENT-SORE-THROAT/inputs"),
    ("post", "/diagnostic/evaluate/ENT-SORE-THROAT"),
])
def test_tree_endpoints_require_sign_in(method, path):
    with TestClient(app, raise_server_exceptions=False) as anonymous:
        kwargs = {"json": {}} if method == "post" else {}
        assert getattr(anonymous, method)(path, **kwargs).status_code == 401


def test_questionnaire_endpoint(client, cookies):
    client.cookies.update(cookies)
    body = client.get("/diagnostic/trees/PULM-COUGH/questionnaire").json()
    assert body["entry"] == "duration" and body["nodes"]["duration"]["kind"] == "question"
    assert client.get("/diagnostic/trees/CARD-CHEST-PAIN/questionnaire").status_code == 400


def test_tree_list_marks_node_format(client, cookies):
    client.cookies.update(cookies)
    trees = client.get("/diagnostic/trees").json()["trees"]
    by_id = {t["id"]: t for t in trees}
    assert by_id["ENT-SORE-THROAT"]["node_format"] == "conditional"
    assert by_id["PULM-COUGH"]["node_format"] == "questionnaire"
    assert sum(t["node_format"] == "conditional" for t in trees) == 17
    assert sum(t["walk_available"] for t in trees if t["node_format"] == "conditional") == 15
    assert sum(t["walk_available"] for t in trees if t["node_format"] == "questionnaire") == 16
    assert by_id["ID-FEVER"]["walk_available"] is False
    assert by_id["PSYCH-PSYCHOSIS"]["unavailable_reason"] == "Temporarily unavailable pending content review."
    assert all("review_status_label" in t for t in trees)


def test_inputs_come_from_the_tree(client, cookies):
    client.cookies.update(cookies)
    body = client.get("/diagnostic/trees/ENT-SORE-THROAT/inputs").json()
    assert body["tree"]["id"] == "ENT-SORE-THROAT"
    assert "review_status" in body["tree"]
    assert "clinical_review_notice" in body
    assert "stridor" in body["inputs"]["symptoms"]
    assert body["inputs"]["findings"]["rapid_strep"] == ["positive"]


def test_inputs_errors(client, cookies):
    client.cookies.update(cookies)
    assert client.get("/diagnostic/trees/PULM-COUGH/inputs").status_code == 400
    assert client.get("/diagnostic/trees/NOPE/inputs").status_code == 404
    assert client.get("/diagnostic/trees/PSYCH-PSYCHOSIS/inputs").status_code == 400


def test_evaluate_walks_on_named_findings(client, cookies):
    client.cookies.update(cookies)
    response = client.post(
        "/diagnostic/evaluate/PSYCH-SUICIDAL-IDEATION",
        json={"symptoms": [], "exam": [], "red_flags": [], "findings": {"recent_attempt": True}},
    )
    assert response.status_code == 200
    result = response.json()["tree_result"]
    assert result["evaluated"] is True
    assert len(result["path"]) > 1
    assert "end_reason" in result
    assert "clinical_review_notice" in result
    assert "review_status" in result["tree"]
