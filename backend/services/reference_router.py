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
TREES_PATH = Path(__file__).resolve().parents[1] / "trees"

# Map family IDs to tree prefixes
FAMILY_TO_PREFIX = {
    "neurology": "NEU",
    "cardiology": "CARD",
    "endocrinology": "ENDO",
    "pulmonology": "PULM",
    "gastroenterology": "GI",
    "infectious_disease": "ID",
    "nephrology": "NEPHRO",
    "rheumatology": "RHEUM",
    "dermatology": "DERM",
    "psychiatry": "PSYCH",
    "obstetrics_gynecology": "OB",
    "orthopedics": "ORTHO",
    "emergency": "EMERGENCY",
    "hematology": "HEM",
    "allergy": "ALLERGY",
    "dentistry": "DENT",
    "ent": "ENT",
    "general": "GEN",
    "oncology": "ONCOLOGY",
    "ophthalmology": "OPHTHO",
    "pediatrics": "PEDS",
    "surgery": "SURG",
    "trauma": "TRAUMA",
    "urology": "URO",
}


def _load_rules_file(filename: str) -> Dict[str, Any]:
  """Load a rules YAML file from backend/rules."""
  path = RULES_PATH / filename
  if not path.exists():
    raise HTTPException(status_code=404, detail=f"Rules file not found: {filename}")
  with path.open("r", encoding="utf-8") as f:
    data = yaml.safe_load(f) or {}
  return data


def _load_trees_by_family(family: str) -> List[Dict[str, Any]]:
  """Load all decision trees for a given specialty family from backend/trees."""
  prefix = FAMILY_TO_PREFIX.get(family)
  if not prefix:
    return []
  
  trees = []
  if not TREES_PATH.exists():
    return []
  
  # Find all tree files matching the prefix
  for tree_file in TREES_PATH.glob(f"{prefix}-*.yml"):
    try:
      with tree_file.open("r", encoding="utf-8") as f:
        tree_data = yaml.safe_load(f) or {}
        
        # Convert tree structure to rule-like format for compatibility
        tree_id = tree_data.get("id", tree_file.stem)
        trees.append({
          "id": tree_id,
          "label": tree_data.get("title", tree_id),
          "presentations": [],  # Could extract from nodes if needed
          "icd10": [],
          "snomed": [],
          "citations": tree_data.get("citations", []),
          "source": "Clinical Decision Tree"
        })
    except Exception as e:
      print(f"Error loading tree {tree_file}: {e}")
      continue
  
  return trees


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
  Now loads decision trees from backend/trees/ instead of backend/rules/
  Rate limit: 100 requests per minute per IP.
  """
  # Load trees from the trees directory
  trees = _load_trees_by_family(family)
  
  return {
    "family": family,
    "version": "2.0.0",
    "source": "RealDiag Clinical Decision Trees",
    "count": len(trees),
    "rules": trees,
  }
