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

# Map family IDs to tree prefixes (multiple prefixes per family due to naming variations)
FAMILY_TO_PREFIX = {
    "neurology": ["NEU", "NEURO"],
    "cardiology": ["CARD", "CARDS"],
    "endocrinology": ["ENDO"],
    "pulmonology": ["PULM"],
    "gastroenterology": ["GI"],
    "infectious_disease": ["ID", "INFECTIOUS"],
    "nephrology": ["NEPHRO", "RENAL"],
    "rheumatology": ["RHEUM"],
    "dermatology": ["DERM"],
    "psychiatry": ["PSYCH"],
    "obstetrics_gynecology": ["OB", "OBGYN"],
    "orthopedics": ["ORTHO"],
    "emergency": ["EMERGENCY"],
    "hematology": ["HEM", "HEME"],
    "allergy": ["ALLERGY"],
    "dentistry": ["DENT"],
    "ent": ["ENT"],
    "general": ["GEN", "GENERAL"],
    "oncology": ["ONCOLOGY"],
    "ophthalmology": ["OPHTHO", "OPTH"],
    "pediatrics": ["PEDS"],
    "surgery": ["SURG"],
    "trauma": ["TRAUMA"],
    "urology": ["URO", "UROLOGY"],
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
  prefixes = FAMILY_TO_PREFIX.get(family)
  if not prefixes:
    return []
  
  trees = []
  if not TREES_PATH.exists():
    return []
  
  # Handle both single prefix and list of prefixes
  if isinstance(prefixes, str):
    prefixes = [prefixes]
  
  # Find all tree files matching any of the prefixes
  for prefix in prefixes:
    for tree_file in TREES_PATH.glob(f"{prefix}-*.yml"):
      try:
        with tree_file.open("r", encoding="utf-8") as f:
          tree_data = yaml.safe_load(f) or {}
          
          # Skip empty or invalid files
          if not tree_data:
            continue
          
          # Convert tree structure to rule-like format for compatibility
          # Support both 'id' and 'tree_id' field names
          tree_id = tree_data.get("id") or tree_data.get("tree_id") or tree_file.stem
          tree_title = tree_data.get("title") or tree_data.get("name") or tree_id
          
          # Extract presentations from chief_complaint and description
          presentations = []
          chief_complaint = tree_data.get("chief_complaint", "")
          description = tree_data.get("description", "")
          
          if chief_complaint:
            # Split by comma and clean up each item
            complaints = [c.strip() for c in chief_complaint.split(",")]
            presentations.extend(complaints)
          
          if description and description not in presentations:
            presentations.append(description)
          
          # Ensure citations are always strings (not objects or dicts)
          citations_raw = tree_data.get("citations", [])
          citations = []
          if isinstance(citations_raw, list):
            for citation in citations_raw:
              if isinstance(citation, str):
                citations.append(citation)
              elif isinstance(citation, dict):
                # Convert dict to string (take first key or value)
                citations.append(str(list(citation.keys())[0]) if citation else "")
              else:
                citations.append(str(citation))
          
          trees.append({
            "id": tree_id,
            "label": tree_title,
            "presentations": presentations,
            "icd10": [tree_data.get("icd10")] if tree_data.get("icd10") else [],
            "snomed": [],
            "citations": citations,
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
  Return endocrinology clinical rules with presentations.
  Rate limit: 100 requests per minute per IP.
  """
  # Load from rules file (has complete presentation data)
  rules_file = RULES_PATH / "endocrinology.yml"
  
  if rules_file.exists():
    try:
      with rules_file.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
        rules = data.get("rules", [])
        
        return {
          "family": "endocrinology",
          "version": data.get("version", "2.0.0"),
          "source": data.get("source", "Clinical Practice Guidelines"),
          "count": len(rules),
          "rules": rules,
        }
    except Exception as e:
      print(f"Error loading endocrinology rules: {e}")
  
  # Fallback to trees if rules file doesn't exist
  trees = _load_trees_by_family("endocrinology")
  
  # Sort alphabetically by label
  trees_sorted = sorted(trees, key=lambda x: x.get("label", "").lower())
  
  return {
    "family": "endocrinology",
    "version": "2.0.0",
    "source": "RealDiag Clinical Decision Trees",
    "count": len(trees_sorted),
    "rules": trees_sorted,
  }


@router.get("/{family}")
@limiter.limit("100/minute") if LIMITER_AVAILABLE else lambda f: f
def get_rules_by_family(request: Request, family: str) -> Dict[str, Any]:
  """
  Generalized endpoint: /reference/{family}
  Loads clinical rules from backend/rules/ with full presentation and SNOMED data.
  Rate limit: 100 requests per minute per IP.
  """
  # Try to load from rules file first (has complete data)
  rules_file = RULES_PATH / f"{family}.yml"
  
  if rules_file.exists():
    try:
      with rules_file.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
        rules = data.get("rules", [])
        
        # Only use rules file if it has content
        if rules:
          # Sort alphabetically by label
          rules_sorted = sorted(rules, key=lambda x: x.get("label", "").lower())
          
          return {
            "family": family,
            "version": data.get("version", "2.0.0"),
            "source": data.get("source", "Clinical Practice Guidelines"),
            "count": len(rules_sorted),
            "rules": rules_sorted,
          }
    except Exception as e:
      print(f"Error loading rules file {rules_file}: {e}")
  
  # Fallback to trees if rules file doesn't exist or is empty
  trees = _load_trees_by_family(family)
  
  # Sort alphabetically by label
  trees_sorted = sorted(trees, key=lambda x: x.get("label", "").lower())
  
  return {
    "family": family,
    "version": "2.0.0",
    "source": "RealDiag Clinical Decision Trees",
    "count": len(trees_sorted),
    "rules": trees_sorted,
  }
