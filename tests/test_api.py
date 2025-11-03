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
    # TestClient follows redirects by default; request as non-HTML client and
    # assert the final URL is the docs page.
    r = client.get("/", headers={"Accept": "application/json"})
    assert r.status_code == 200
    # final URL should be the docs page
    assert r.url.path == "/docs"


def test_version_endpoint():
    r = client.get("/version")
    assert r.status_code == 200
    j = r.json()
    assert j["app"] == Config.APP_NAME
    assert j["version"] == Config.APP_VERSION
