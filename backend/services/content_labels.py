"""
User-facing labels for content that has not been clinically validated.

Every API response that carries AI-generated or homeopathic content must
include the matching label so the UI can show it next to that content.
"""

import os

from backend.services.tree_schema import HOMEOPATHY_VALIDATION_STATEMENT

AI_CONTENT_LABEL = "AI-generated; not clinically validated."

__all__ = [
    "AI_CONTENT_LABEL",
    "HOMEOPATHY_VALIDATION_STATEMENT",
    "ai_enrichment_enabled",
]


def ai_enrichment_enabled() -> bool:
    """Runtime AI enrichment of search results is off unless ENABLE_AI_ENRICHMENT=true."""
    return os.getenv("ENABLE_AI_ENRICHMENT", "false").strip().lower() == "true"
