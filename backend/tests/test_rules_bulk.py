"""GET /rules/all: every rule in one response, with a content version (offline download)."""
from pathlib import Path

from backend.services import rules_router
from backend.services.rules_engine import RulesEngine

TREES = Path(__file__).resolve().parents[1] / "trees"


def test_all_rules_returns_every_tree_once():
    response = rules_router.get_all_rules(current_user=None)
    ids = [r["id"] for r in response["rules"]]
    assert response["count"] == len(ids) == len(set(ids)) == len(list(TREES.glob("*.yml")))
    assert all(r.get("family") and r.get("label") for r in response["rules"])
    assert response["clinical_review_notice"]
    assert len(response["version"]) == 16


def test_version_changes_with_content(tmp_path):
    source = next(TREES.glob("*.yml"))
    (tmp_path / source.name).write_text(source.read_text())
    first = RulesEngine(tmp_path).version()
    assert RulesEngine(tmp_path).version() == first
    (tmp_path / source.name).write_text(source.read_text().replace("status: draft", "status: draft\n# edited", 1))
    (tmp_path / "EXTRA.yml").write_text("tree_id: EXTRA\nname: Extra\nfamily: test\nstatus: draft\n")
    assert RulesEngine(tmp_path).version() != first


def test_all_rules_route_is_registered():
    assert "/rules/all" in {getattr(r, "path", None) for r in rules_router.router.routes}
