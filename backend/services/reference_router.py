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
    "pulmonology": ["PULM", "RESP"],
    "gastroenterology": ["GI"],
    "infectious_disease": ["ID", "INFECTIOUS", "INFECT"],
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
          
          # Extract SNOMED code (can be string, number, or list)
          snomed_codes = []
          snomed_raw = tree_data.get("snomed")
          if snomed_raw:
            if isinstance(snomed_raw, list):
              snomed_codes = [str(code) for code in snomed_raw]
            else:
              snomed_codes = [str(snomed_raw)]
          
          # Extract source from trace section or use default
          trace_info = tree_data.get("trace", {})
          # Handle both old format (trace as list) and new format (trace as dict with source)
          if isinstance(trace_info, dict):
            source = trace_info.get("source", "Clinical Decision Tree")
          else:
            # Old format - trace is a list (case study), no source field
            source = "Clinical Decision Tree"
          if not source:
            source = "Clinical Decision Tree"
          
          trees.append({
            "id": tree_id,
            "label": tree_title,
            "presentations": presentations,
            "icd10": [tree_data.get("icd10")] if tree_data.get("icd10") else [],
            "snomed": snomed_codes,
            "citations": citations,
            "source": source
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
  Loads all clinical decision trees from backend/trees/ for the given specialty family.
  Deduplicates entries that refer to the same condition.
  Rate limit: 100 requests per minute per IP.
  """
  # Load all trees for this family
  trees = _load_trees_by_family(family)
  all_rules = []
  
  # Load all trees for this family
  trees = _load_trees_by_family(family)
  all_rules = []
  
  # Deduplication: track IDs and normalized names
  existing_ids = set()
  existing_names = {}
  
  # Normalize name for duplicate detection
  def normalize_name(name):
    """Normalize condition name for duplicate detection."""
    if not name:
      return ""
    import re
    normalized = name.lower().strip()
    
    # Remove content in parentheses
    normalized = re.sub(r'\s*\([^)]*\)', '', normalized)
    
    # Remove common prefixes
    prefixes_to_remove = ["acute ", "bacterial ", "chronic "]
    for prefix in prefixes_to_remove:
      if normalized.startswith(prefix):
        normalized = normalized[len(prefix):]
    
    # Remove common suffixes
    suffixes_to_remove = [
      " evaluation", " evaluation and management", " management",
      " diagnostic tree", " - general evaluation", " disorder/epilepsy",
      " and dizziness", " disorder", "/epilepsy"
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
  }
