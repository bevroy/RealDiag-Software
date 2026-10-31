
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List
import yaml

from .tree_schema import applies_to, icd10_codes, snomed_codes
from .clinical_review import review_fields
from .icpc2 import icpc2_for

# Updated to use trees directory (individual tree files, not family-grouped rules)
RULES_PATH = Path(__file__).resolve().parents[1] / "trees"

class RulesEngine:
    """Engine for loading and searching clinical rule sets."""
    
    def __init__(self, rules_path: Path | None = None):
        self.rules_path = rules_path or RULES_PATH
        self.rule_sets = self._load_rules()
    
    def _load_rules(self) -> Dict[str, Any]:
        """Load all YAML tree files and group by family."""
        rules_by_family = {}
        if not self.rules_path.exists():
            return rules_by_family
        
        for f in sorted(self.rules_path.glob("*.yml")):
            try:
                tree_data = yaml.safe_load(f.read_text())
                if not tree_data:
                    continue
                
                family = tree_data.get('family', 'general')
                population = applies_to(tree_data)
                
                # Convert tree format to rule format
                rule = {
                    'id': tree_data.get('tree_id', f.stem),
                    'label': tree_data.get('name', f.stem),
                    'presentations': tree_data.get('presentations', []),
                    'icd10': icd10_codes(tree_data),
                    **icpc2_for(tree_data, tree_data.get('tree_id', f.stem)),
                    'snomed': snomed_codes(tree_data),
                    'sensitivity': tree_data.get('sensitivity'),
                    'specificity': tree_data.get('specificity'),
                    'clinical_pearls': tree_data.get('clinical_pearls', []),
                    'management': tree_data.get('treatment', []),
                    'tests': tree_data.get('workup', []),
                    'applies_to': population['sex'],
                    'age_min': population['age_min'],
                    'age_max': population['age_max'],
                    'urgency': tree_data.get('urgency', ''),
                    'status': tree_data.get('status', ''),
                    **review_fields(tree_data.get('status')),
                }
                
                # Group by family
                if family not in rules_by_family:
                    rules_by_family[family] = {
                        'family': family,
                        'rules': [],
                        'version': '2.0',
                        'source': 'RealDiag Clinical Database'
                    }
                
                rules_by_family[family]['rules'].append(rule)
            except Exception as e:
                # Skip invalid files
                continue
        
        return rules_by_family
    
    def list_families(self) -> List[Dict[str, str]]:
        """List all available rule families."""
        return [
            {
                "family": doc["family"],
                "version": doc.get("version", "unknown"),
                "source": doc.get("source", ""),
                "rule_count": len(doc.get("rules", []))
            }
            for doc in self.rule_sets.values()
        ]
    
    def get_family(self, family: str) -> Dict[str, Any]:
        """Get all rules for a specific family."""
        return self.rule_sets.get(family, {"error": f"family '{family}' not found"})
    
    def search(self, query: str, family: str | None = None) -> List[Dict[str, Any]]:
        """Search rules by keyword in labels, presentations, or ICD-10 codes."""
        query = query.lower()
        results = []
        
        families_to_search = [family] if family else list(self.rule_sets.keys())
        
        for fam in families_to_search:
            if fam not in self.rule_sets:
                continue
            
            for rule in self.rule_sets[fam].get("rules", []):
                # Search in label
                if query in rule.get("label", "").lower():
                    results.append({
                        "family": fam,
                        "id": rule.get("id"),
                        "label": rule.get("label"),
                        "presentations": rule.get("presentations", []),
                        "icd10": rule.get("icd10", []),
                        "review_status": rule.get("review_status"),
                        "review_status_label": rule.get("review_status_label"),
                    })
                    continue
                
                # Search in presentations
                # Items may be "Key: value" pairs parsed as dicts; join them as text
                presentations_text = " ".join(
                    " ".join(f"{k}: {v}" for k, v in p.items()) if isinstance(p, dict) else str(p)
                    for p in rule.get("presentations", []) or []
                ).lower()
                if query in presentations_text:
                    results.append({
                        "family": fam,
                        "id": rule.get("id"),
                        "label": rule.get("label"),
                        "presentations": rule.get("presentations", []),
                        "icd10": rule.get("icd10", []),
                        "review_status": rule.get("review_status"),
                        "review_status_label": rule.get("review_status_label"),
                    })
                    continue
                
                # Search in ICD-10 codes
                icd10_text = " ".join(str(c) for c in rule.get("icd10", []) or []).lower()
                if query in icd10_text:
                    results.append({
                        "family": fam,
                        "id": rule.get("id"),
                        "label": rule.get("label"),
                        "presentations": rule.get("presentations", []),
                        "icd10": rule.get("icd10", []),
                        "review_status": rule.get("review_status"),
                        "review_status_label": rule.get("review_status_label"),
                    })
        
        return results
    
    def all_rules(self) -> List[Dict[str, Any]]:
        """Every rule with its family, in family then id order (for offline download)."""
        return [{"family": fam, **rule}
                for fam in sorted(self.rule_sets)
                for rule in sorted(self.rule_sets[fam].get("rules", []), key=lambda r: str(r.get("id")))]

    def version(self) -> str:
        """Short content hash of the loaded rules; changes whenever any rule changes."""
        payload = json.dumps(self.rule_sets, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()[:16]

    def get_rule(self, rule_id: str) -> Dict[str, Any]:
        """Get a specific rule by ID."""
        for fam, doc in self.rule_sets.items():
            for rule in doc.get("rules", []):
                if rule.get("id") == rule_id:
                    return {
                        "family": fam,
                        **rule  # Return all rule fields
                    }
        return {"error": f"rule '{rule_id}' not found"}
