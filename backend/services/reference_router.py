from pathlib import Path
from typing import Any, Dict, List

import yaml
from fastapi import APIRouter, HTTPException, Request

# Import rate limiter
try:
    from backend.services.security import limiter
    LIMITER_AVAILABLE = True
except ImportError:
    LIMITER_AVAILABLE = False
    limiter = None

router = APIRouter(prefix="/reference", tags=["reference"])

RULES_PATH = Path(__file__).resolve().parents[1] / "rules"


def _load_rules_file(filename: str) -> Dict[str, Any]:
  """Load a rules YAML file from backend/rules."""
  path = RULES_PATH / filename
  if not path.exists():
    raise HTTPException(status_code=404, detail=f"Rules file not found: {filename}")
  with path.open("r", encoding="utf-8") as f:
    data = yaml.safe_load(f) or {}
  return data


@router.get("/endocrinology")
@limiter.limit("100/minute") if LIMITER_AVAILABLE else lambda f: f
def get_endocrinology_rules(request: Request) -> Dict[str, Any]:
  """
  Return the full endocrinology rules document as JSON.
  Rate limit: 100 requests per minute per IP.
  """
  data = _load_rules_file("endocrinology.yml")
  family = data.get("family", "endocrinology")
  rules: List[Dict[str, Any]] = data.get("rules", [])
  return {
    "family": family,
    "version": data.get("version", "1.0.0"),
    "source": data.get("source", "Clinical Practice Guidelines"),
    "count": len(rules),
    "rules": rules,
  }


@router.get("/{family}")
@limiter.limit("100/minute") if LIMITER_AVAILABLE else lambda f: f
def get_rules_by_family(request: Request, family: str) -> Dict[str, Any]:
  """
  Generalized endpoint: /reference/{family}
  Looks for {family}.yml in backend/rules.
  Rate limit: 100 requests per minute per IP.
  """
  filename = f"{family}.yml"
  data = _load_rules_file(filename)
  rules: List[Dict[str, Any]] = data.get("rules", [])
  return {
    "family": data.get("family", family),
    "version": data.get("version", "1.0.0"),
    "source": data.get("source", "Clinical Practice Guidelines"),
    "count": len(rules),
    "rules": rules,
  }
