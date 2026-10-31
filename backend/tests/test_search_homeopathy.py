"""/search shows the remedies stored in trees (homeopathy.remedies), always with the
"not clinically validated" statement."""
from pathlib import Path

import yaml

from backend.services.search_router import _extract_clinical_info
from backend.services.tree_schema import HOMEOPATHY_VALIDATION_STATEMENT, homeopathy_remedies

TREES = Path(__file__).resolve().parents[1] / "trees"


def _trees_with_remedies():
    for path in sorted(TREES.glob("*.yml")):
        tree = yaml.safe_load(path.read_text())
        if homeopathy_remedies(tree):
            yield path.stem, tree


def test_every_stored_remedy_is_shown_with_the_validation_statement():
    trees = list(_trees_with_remedies())
    assert len(trees) == 20
    total = 0
    for tree_id, tree in trees:
        info = _extract_clinical_info(tree)
        stored = homeopathy_remedies(tree)
        total += len(stored)
        assert len(info["homeopathic_remedies"]) == len({r["remedy"] for r in stored}), tree_id
        for remedy in stored:
            assert any(r.startswith(remedy["remedy"]) for r in info["homeopathic_remedies"]), tree_id
        assert info["homeopathy_validation_statement"] == HOMEOPATHY_VALIDATION_STATEMENT
    assert total == 100


def test_no_remedies_means_no_statement():
    info = _extract_clinical_info({"tree_id": "X", "name": "X", "homeopathy": {"remedies": []}})
    assert info["homeopathic_remedies"] == []
    assert info["homeopathy_validation_statement"] is None


def test_remedy_text_includes_indications():
    info = _extract_clinical_info({"tree_id": "X", "name": "X", "homeopathy": {
        "validation_statement": HOMEOPATHY_VALIDATION_STATEMENT,
        "remedies": [{"remedy": "Arnica 30C", "indications": "bruising"}]}})
    assert info["homeopathic_remedies"] == ["Arnica 30C: bruising"]
