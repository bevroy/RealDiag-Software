"""
Clinical review status of RealDiag's clinical content.

Every API response that carries decision-tree content, urgency levels,
treatment information or severity ratings includes:

  clinical_review_notice  - CLINICAL_REVIEW_NOTICE while any content is
                            unreviewed, otherwise None
  review_status           - the tree's `status` field (per tree/result)
  review_status_label     - human-readable label for that status

The notice is driven by the content itself: it disappears automatically once
no tree is in "draft" or "review" status and the severity thresholds coded in
smart_diagnostic_engine.py are marked reviewed (SEVERITY_THRESHOLDS_REVIEWED).
See docs/CLINICAL_CONTENT_REVIEW.md.
"""

from __future__ import annotations

import re
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

TREES_DIR = Path(__file__).resolve().parents[1] / "trees"

CLINICAL_REVIEW_NOTICE = (
    "Clinical content is under review. Urgency levels, treatment information, "
    "and severity thresholds are proposed and have not completed clinical review. "
    "Verify against current guidelines before acting."
)

STATUS_LABELS = {
    "draft": "Draft - under clinical review.",
    "review": "In clinical review - not yet approved.",
    "approved": "Clinically reviewed.",
    "retired": "Retired - not for clinical use.",
}
UNREVIEWED_STATUSES = {"draft", "review"}

# Troponin severity multiples and DKA glucose thresholds in
# smart_diagnostic_engine.py have no clinical sign-off yet. Set to True only
# after that review is recorded in docs/CLINICAL_CONTENT_REVIEW.md.
SEVERITY_THRESHOLDS_REVIEWED = False

_STATUS_LINE = re.compile(r"^status:\s*['\"]?([A-Za-z-]+)", re.MULTILINE)


def status_label(status: Optional[str]) -> Optional[str]:
    """Label for a tree status, e.g. 'draft' -> 'Draft - under clinical review.'"""
    if not status:
        return None
    return STATUS_LABELS.get(str(status).strip().lower(), f"Status: {status}")


@lru_cache(maxsize=1)
def tree_status_counts(trees_dir: Path = TREES_DIR) -> Dict[str, int]:
    """Count trees by status. Reads only the top-level `status:` line of each
    file, so it is cheap; cached per process (trees change only on deploy)."""
    counts: Counter = Counter()
    for path in sorted(Path(trees_dir).glob("*.yml")):
        match = _STATUS_LINE.search(path.read_text(encoding="utf-8"))
        counts[match.group(1).lower() if match else "unknown"] += 1
    return dict(counts)


def unreviewed_tree_count(trees_dir: Path = TREES_DIR) -> int:
    counts = tree_status_counts(trees_dir)
    return sum(n for status, n in counts.items() if status in UNREVIEWED_STATUSES or status == "unknown")


def review_notice(trees_dir: Path = TREES_DIR) -> Optional[str]:
    """CLINICAL_REVIEW_NOTICE while any clinical content is unreviewed, else None."""
    if unreviewed_tree_count(trees_dir) > 0 or not SEVERITY_THRESHOLDS_REVIEWED:
        return CLINICAL_REVIEW_NOTICE
    return None


def review_fields(status: Optional[str]) -> Dict[str, Any]:
    """Per-tree fields: {'review_status', 'review_status_label'}."""
    return {"review_status": status or None, "review_status_label": status_label(status)}


def with_notice(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Add clinical_review_notice to a response dict (in place) and return it."""
    payload["clinical_review_notice"] = review_notice()
    return payload


def reset_cache() -> None:
    """Forget cached tree status counts (tests, or after trees change on disk)."""
    tree_status_counts.cache_clear()
