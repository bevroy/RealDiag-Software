"""
User-facing labels for content that has not been clinically validated.

Every API response that carries AI-generated or homeopathic content must
include the matching label so the UI can show it next to that content.
"""

import os

from backend.services.tree_schema import HOMEOPATHY_VALIDATION_STATEMENT

AI_CONTENT_LABEL = "AI-generated; not clinically validated."

# Every language-model feature is behind one of these settings, and every
# one follows the same rule: off unless the setting is exactly "true"
# (case and surrounding spaces ignored), and anything it produces carries
# AI_CONTENT_LABEL.
#   ENABLE_AI_GENERATION  AI-suggested diagnoses added to symptom rankings,
#                         and new decision trees generated for pending review
#   ENABLE_AI_ENRICHMENT  empty sections of search results filled by AI
AI_SETTINGS = ("ENABLE_AI_GENERATION", "ENABLE_AI_ENRICHMENT")

__all__ = [
    "AI_CONTENT_LABEL",
    "AI_SETTINGS",
    "HOMEOPATHY_VALIDATION_STATEMENT",
    "ai_enrichment_enabled",
    "ai_generation_enabled",
    "ai_setting_enabled",
]


def ai_setting_enabled(name: str) -> bool:
    """True only when the AI setting `name` is explicitly "true"; off by default."""
    if name not in AI_SETTINGS:
        raise ValueError(f"Unknown AI setting: {name}")
    return (os.getenv(name) or "").strip().lower() == "true"


def ai_generation_enabled() -> bool:
    """AI-suggested diagnoses and AI tree generation (ENABLE_AI_GENERATION)."""
    return ai_setting_enabled("ENABLE_AI_GENERATION")


def ai_enrichment_enabled() -> bool:
    """AI enrichment of search results (ENABLE_AI_ENRICHMENT)."""
    return ai_setting_enabled("ENABLE_AI_ENRICHMENT")
