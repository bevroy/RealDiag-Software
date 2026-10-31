import pytest
from fastapi.testclient import TestClient

from backend.main import app
from config import Config


client = TestClient(app)


def test_root_html_renders_template():
    r = client.get("/", headers={"Accept": "text/html"})
    assert r.status_code == 200
    # Should contain app name in rendered HTML
    assert Config.APP_NAME in r.text


def test_root_non_html_redirects_to_docs():
    # Non-HTML clients are redirected to the docs page, which needs a
    # signed-in session (main.py PUBLIC_PATHS).
    r = client.get("/", headers={"Accept": "application/json"}, follow_redirects=False)
    assert r.status_code == 301 and r.headers["location"] == "/docs"
    assert client.get("/docs").status_code == 401


def test_version_endpoint():
    r = client.get("/version")
    assert r.status_code == 200
    j = r.json()
    assert j["app"] == Config.APP_NAME
    assert j["version"] == Config.APP_VERSION
