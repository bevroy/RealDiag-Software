"""Approving an AI-generated tree must not claim it becomes searchable: approved trees
are kept in backend/data/generated_trees/approved/ and the clinical library loads only
backend/trees/*.yml."""
import inspect
from pathlib import Path

from backend.services import admin_router
from backend.services.decision_tree_engine import TREES_PATH as ENGINE_TREES
from backend.services.rules_engine import RULES_PATH
from backend.services.smart_diagnostic_engine import TREES_PATH as CRITERIA_TREES

LIBRARY = Path(__file__).resolve().parents[1] / "trees"


def test_approval_message_says_what_happens():
    msg = admin_router.APPROVED_TREE_MESSAGE
    assert "not part of the clinical library" in msg and "does not appear in search or /diagnose" in msg
    assert "active database" not in msg and "searchable" not in msg
    doc = inspect.getsource(admin_router.review_tree)
    assert "make it searchable" not in doc and "Tree approved and moved to active database" not in doc


def test_clinical_library_loads_only_backend_trees():
    for path in (ENGINE_TREES, RULES_PATH, CRITERIA_TREES):
        assert Path(path).resolve() == LIBRARY.resolve()
    guide = (Path(__file__).resolve().parents[2] / "AI_TREE_GENERATION_GUIDE.md").read_text()
    assert "become searchable" not in guide and "remain searchable" not in guide
