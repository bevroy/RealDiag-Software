
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import yaml

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
                
                # Convert tree format to rule format
                rule = {
                    'id': tree_data.get('tree_id', f.stem),
                    'label': tree_data.get('name', f.stem),
                    'presentations': tree_data.get('presentations', []),
                    'icd10': tree_data.get('icd10', []),
                    'snomed': tree_data.get('snomed', []),
                    'sensitivity': tree_data.get('sensitivity'),
                    'specificity': tree_data.get('specificity'),
                    'clinical_pearls': tree_data.get('clinical_pearls', []),
                    'management': tree_data.get('treatment', []),
                    'tests': tree_data.get('workup', []),
                    'applies_to': tree_data.get('applies_to'),
                    'age_min': tree_data.get('age_min'),
                    'age_max': tree_data.get('age_max')
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
                        "icd10": rule.get("icd10", [])
                    })
                    continue
                
                # Search in presentations
                presentations_text = " ".join(rule.get("presentations", [])).lower()
                if query in presentations_text:
                    results.append({
                        "family": fam,
                        "id": rule.get("id"),
                        "label": rule.get("label"),
                        "presentations": rule.get("presentations", []),
                        "icd10": rule.get("icd10", [])
                    })
                    continue
                
                # Search in ICD-10 codes
                icd10_text = " ".join(rule.get("icd10", [])).lower()
                if query in icd10_text:
                    results.append({
                        "family": fam,
                        "id": rule.get("id"),
                        "label": rule.get("label"),
                        "presentations": rule.get("presentations", []),
                        "icd10": rule.get("icd10", [])
                    })
        
        return results
    
    def get_rule(self, rule_id: str) -> Dict[str, Any]:
        """Get a specific rule by ID."""
        for fam, doc in self.rule_sets.items():
            for rule in doc.get("rules", []):
                if rule.get("id") == rule_id:
                    return {
                        "family": fam,
                        "id": rule.get("id"),
                        "label": rule.get("label"),
                        "presentations": rule.get("presentations", []),
                        "icd10": rule.get("icd10", [])
                    }
        return {"error": f"rule '{rule_id}' not found"}
