from pathlib import Path
from typing import Any, Dict, List

import yaml
from fastapi import APIRouter, HTTPException, Request

from .clinical_review import review_fields, review_notice
from .tree_schema import icd10_codes, primary_source, snomed_codes, source_texts, tree_id as get_tree_id, tree_name

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
# Updated: 2025-01-05 to include immunology trees under allergy family
FAMILY_TO_PREFIX = {
    "neurology": ["NEU", "NEURO"],
    "cardiology": ["CARD", "CARDS"],
    "endocrinology": ["ENDO"],
    "pulmonology": ["PULM", "RESP"],
    "gastroenterology": ["GI", "GASTRO"],
    "infectious_disease": ["ID", "INFECTIOUS", "INFECT"],
    "nephrology": ["NEPHRO", "RENAL"],
    "rheumatology": ["RHEUM"],
    "dermatology": ["DERM"],
    "psychiatry": ["PSYCH"],
    "obstetrics_gynecology": ["OB", "OBGYN"],
    "orthopedics": ["ORTHO"],
    "emergency": ["EMERGENCY", "EM"],
    "hematology": ["HEM", "HEME"],
    "allergy": ["ALLERGY", "IMMUNO"],
    "dentistry": ["DENT"],
    "ent": ["ENT"],
    "general": ["GEN", "GENERAL", "PREV"],
    "oncology": ["ONCOLOGY", "ONCO"],
    "ophthalmology": ["OPHTHO", "OPTH"],
    "pediatrics": ["PEDS", "PED"],
    "surgery": ["SURG"],
    "toxicology": ["TOX"],
    "trauma": ["TRAUMA"],
    "urology": ["URO", "UROLOGY"],
    "geriatrics": ["GER"],
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
          tree_id = get_tree_id(tree_data, tree_file.stem)
          tree_title = tree_name(tree_data, tree_id)
          
          # Extract presentations from multiple possible sources
          presentations = []
          
          # Primary source: presentations list (new tree format)
          presentations_list = tree_data.get("presentations", [])
          if isinstance(presentations_list, list):
            presentations.extend([str(p).strip() for p in presentations_list if p])
          
          # Fallback: chief_complaint and description (older format)
          if not presentations:
            chief_complaint = tree_data.get("chief_complaint", "")
            description = tree_data.get("description", "")
            
            if chief_complaint:
              # Split by comma and clean up each item
              complaints = [c.strip() for c in chief_complaint.split(",")]
              presentations.extend(complaints)
            
            if description and description not in presentations:
              presentations.append(description)
          
          # trace.source is reported separately as "source"
          citations = source_texts(tree_data, exclude_origins=("trace.source",))
          snomed = snomed_codes(tree_data)
          source = primary_source(tree_data)
          
          trees.append({
            "id": tree_id,
            "label": tree_title,
            "presentations": presentations,
            "icd10": icd10_codes(tree_data),
            "snomed": snomed,
            "citations": citations,
            "source": source,
            "urgency": tree_data.get("urgency", ""),
            "status": tree_data.get("status", ""),
            **review_fields(tree_data.get("status")),
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
          "clinical_review_notice": review_notice(),
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
    "clinical_review_notice": review_notice(),
  }


@router.get("/{family}")
@limiter.limit("100/minute") if LIMITER_AVAILABLE else lambda f: f
def get_rules_by_family(request: Request, family: str) -> Dict[str, Any]:
  """
  Generalized endpoint: /reference/{family}
  Loads all clinical decision trees from backend/trees/ for the given specialty family.
  Deduplicates entries that refer to the same condition.
  Rate limit: 100 requests per minute per IP.
  """
  # Load all trees for this family
  trees = _load_trees_by_family(family)
  if not trees:
    raise HTTPException(status_code=404, detail=f"Family not found: {family}")
  all_rules = []
  
  # Load all trees for this family
  trees = _load_trees_by_family(family)
  all_rules = []
  
  # Deduplication: track IDs and normalized names
  existing_ids = set()
  existing_names = {}
  
  # Normalize name for duplicate detection
  def normalize_name(name):
    """
    Normalize condition name for duplicate detection.
    
    Updated 2026-01-08: Preserve clinically important distinctions:
    - Keep "acute" vs "chronic" (different conditions)
    - Keep "(pediatric)" vs "(adult)" (different approaches)
    - Keep specialty prefixes in parentheses
    """
    if not name:
      return ""
    import re
    normalized = name.lower().strip()
    
    # Preserve important clinical distinctions in parentheses
    # These terms indicate clinically distinct conditions that should NOT be merged
    preserved_parenthetical_terms = [
      "stress", "urge", "overflow", "mixed", "functional", "geriatric",
      "pediatric", "adult", "encounter", "bph", "copd", "dvt", "aki", "ckd",
      "hay fever", "hives", "pink eye", "heart attack", "stye", "tennis elbow",
      "sciatica", "athlete's foot", "ringworm", "warts", "cold sores",
      "swimmer's ear", "strep throat", "yeast infection", "epilepsy"
    ]
    
    # Keep parenthetical content if it contains preserved terms
    if any(term in normalized for term in preserved_parenthetical_terms):
      # Keep the full name including important parentheses
      pass
    else:
      # Only remove generic descriptive parentheticals
      # But preserve specialty indicators like (suspected), (confirmed), etc.
      normalized = re.sub(r'\s*\(encounter\)', '', normalized, flags=re.IGNORECASE)
    
    # DO NOT remove "acute" or "chronic" - these are clinically distinct
    # DO NOT remove "bacterial" prefix - indicates different condition
    
    # Only remove truly redundant suffixes
    suffixes_to_remove = [
      " evaluation and management",
      " - general evaluation", 
      " diagnostic tree",
      " - comprehensive evaluation"
    ]
    for suffix in suffixes_to_remove:
      if normalized.endswith(suffix):
        normalized = normalized[:-len(suffix)]
    
    return normalized.strip()
  
  # Add trees while deduplicating
  for tree in trees:
    tree_id = tree.get("id")
    tree_label = tree.get("label", "")
    tree_name_normalized = normalize_name(tree_label)
    
    # Skip if ID already exists
    if tree_id and tree_id in existing_ids:
      continue
    
    # Skip if normalized name already exists
    if tree_name_normalized and tree_name_normalized in existing_names:
      existing_id = existing_names[tree_name_normalized]
      print(f"Skipping duplicate tree {tree_id} ('{tree_label}') - already have {existing_id}")
      continue
    
    # Add this tree
    all_rules.append(tree)
    if tree_id:
      existing_ids.add(tree_id)
    if tree_name_normalized:
      existing_names[tree_name_normalized] = tree_id
  
  # Sort alphabetically by label
  all_rules_sorted = sorted(all_rules, key=lambda x: x.get("label", "").lower())
  
  return {
    "family": family,
    "version": "2.0.0",
    "source": "RealDiag Clinical Decision Trees",
    "count": len(all_rules_sorted),
    "rules": all_rules_sorted,
    "clinical_review_notice": review_notice(),
  }
