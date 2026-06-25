"""
Patient Context Modifiers Engine

This module evaluates patient context variables (diet, exposures, travel, etc.)
and applies context-specific rules to modify diagnostic pathways.

SAFETY PRINCIPLES:
- No inference from race/ethnicity/culture
- Context modifiers are opt-in only
- Outputs phrased as "Consider..." not prescriptive
- All modifications include explainable reasoning and citations
- Never prescribe specific medications
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

CONTEXT_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "context"


class ContextEngine:
    """
    Evaluates patient context and applies relevant rules to diagnostic pathways.
    """
    
    def __init__(self):
        self.variables = self._load_variables()
        self.rules = self._load_rules()
        logger.info(f"Loaded {len(self.variables)} context variables and {len(self.rules)} rules")
    
    def _load_variables(self) -> List[Dict[str, Any]]:
        """Load context variable definitions."""
        variables_file = CONTEXT_DATA_PATH / "context_variables.json"
        if not variables_file.exists():
            logger.warning(f"Context variables file not found: {variables_file}")
            return []
        
        try:
            with open(variables_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("variables", [])
        except Exception as e:
            logger.error(f"Failed to load context variables: {e}")
            return []
    
    def _load_rules(self) -> List[Dict[str, Any]]:
        """Load context rules."""
        rules_file = CONTEXT_DATA_PATH / "context_rules.json"
        if not rules_file.exists():
            logger.warning(f"Context rules file not found: {rules_file}")
            return []
        
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("rules", [])
        except Exception as e:
            logger.error(f"Failed to load context rules: {e}")
            return []
    
    def get_variables(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get context variables, optionally filtered by category.
        
        Args:
            category: Filter by category (Diet, Supplements, Travel, etc.)
        
        Returns:
            List of variable definitions
        """
        if category:
            return [v for v in self.variables if v.get("category") == category]
        return self.variables
    
    def get_categories(self) -> List[str]:
        """Get list of unique categories."""
        categories = set(v.get("category") for v in self.variables if v.get("category"))
        return sorted(categories)
    
    def _evaluate_trigger(self, trigger_expr: str, patient_context: Dict[str, Any]) -> bool:
        """
        Evaluate a single trigger expression against patient context.
        
        Supports expressions like:
        - "seaweed_kelp_supplement == true"
        - "seafood_frequency_per_week >= 5"
        - "recent_travel_regions includes 'south_asia'"
        - "iodized_salt_use == 'often' AND seafood_frequency_per_week >= 3"
        
        Args:
            trigger_expr: Expression string
            patient_context: Patient context data
        
        Returns:
            True if trigger matches, False otherwise
        """
        try:
            # Handle "includes" operator for arrays
            if " includes " in trigger_expr:
                parts = trigger_expr.split(" includes ")
                if len(parts) != 2:
                    return False
                var_name = parts[0].strip()
                value = parts[1].strip().strip("'\"")
                var_value = patient_context.get(var_name, [])
                if isinstance(var_value, list):
                    return value in var_value
                return False
            
            # Handle AND operator
            if " AND " in trigger_expr:
                parts = trigger_expr.split(" AND ")
                return all(self._evaluate_trigger(p.strip(), patient_context) for p in parts)
            
            # Handle OR operator
            if " OR " in trigger_expr:
                parts = trigger_expr.split(" OR ")
                return any(self._evaluate_trigger(p.strip(), patient_context) for p in parts)
            
            # Handle comparison operators
            for op in [">=", "<=", "==", "!=", ">", "<"]:
                if op in trigger_expr:
                    parts = trigger_expr.split(op)
                    if len(parts) != 2:
                        continue
                    
                    var_name = parts[0].strip()
                    expected_value = parts[1].strip().strip("'\"")
                    
                    actual_value = patient_context.get(var_name)
                    if actual_value is None:
                        return False
                    
                    # Type conversion
                    try:
                        if expected_value.lower() == "true":
                            expected_value = True
                        elif expected_value.lower() == "false":
                            expected_value = False
                        elif expected_value.replace(".", "").isdigit():
                            expected_value = float(expected_value)
                    except:
                        pass
                    
                    # Comparison
                    if op == "==":
                        return actual_value == expected_value
                    elif op == "!=":
                        return actual_value != expected_value
                    elif op == ">=":
                        return float(actual_value) >= float(expected_value)
                    elif op == "<=":
                        return float(actual_value) <= float(expected_value)
                    elif op == ">":
                        return float(actual_value) > float(expected_value)
                    elif op == "<":
                        return float(actual_value) < float(expected_value)
            
            return False
        
        except Exception as e:
            logger.error(f"Error evaluating trigger '{trigger_expr}': {e}")
            return False
    
    def _evaluate_rule_triggers(self, rule: Dict[str, Any], patient_context: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Evaluate all triggers for a rule.
        
        Args:
            rule: Rule definition
            patient_context: Patient context data
        
        Returns:
            Tuple of (matched: bool, matched_descriptions: List[str])
        """
        triggers = rule.get("triggers", [])
        trigger_logic = rule.get("trigger_logic", "any")
        
        matched_descriptions = []
        
        if trigger_logic == "any":
            # Any trigger matches
            for trigger in triggers:
                expr = trigger.get("expression", "")
                if self._evaluate_trigger(expr, patient_context):
                    matched_descriptions.append(trigger.get("description", expr))
            return len(matched_descriptions) > 0, matched_descriptions
        
        elif trigger_logic == "all":
            # All triggers must match
            for trigger in triggers:
                expr = trigger.get("expression", "")
                if self._evaluate_trigger(expr, patient_context):
                    matched_descriptions.append(trigger.get("description", expr))
                else:
                    return False, []
            return len(matched_descriptions) == len(triggers), matched_descriptions
        
        return False, []
    
    def apply_context(
        self,
        diagnosis_module_id: str,
        patient_context: Dict[str, Any],
        base_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Apply context rules to a diagnosis module.
        
        Args:
            diagnosis_module_id: ID of the diagnosis module being evaluated
            patient_context: Patient's context data (diet, travel, etc.)
            base_result: Optional base diagnostic result to merge with
        
        Returns:
            Context modifications to apply to the diagnostic output
        """
        if not patient_context:
            return {"has_context": False, "context_applied": []}
        
        # Find applicable rules
        applicable_rules = [
            rule for rule in self.rules
            if rule.get("diagnosis_module_id") == diagnosis_module_id
        ]
        
        if not applicable_rules:
            return {"has_context": False, "context_applied": []}
        
        # Evaluate each rule
        context_result = {
            "has_context": True,
            "context_applied": [],
            "context_differential": [],
            "context_questions": [],
            "context_workup": [],
            "context_red_flags": [],
            "context_referral_notes": [],
            "urgency_adjustment": None,
            "reasoning": []
        }
        
        for rule in applicable_rules:
            matched, matched_descriptions = self._evaluate_rule_triggers(rule, patient_context)
            
            if matched:
                rule_name = rule.get("name", rule.get("id"))
                effects = rule.get("effects", {})
                
                # Track which rule was applied
                context_result["context_applied"].append({
                    "rule_id": rule.get("id"),
                    "rule_name": rule_name,
                    "matched_triggers": matched_descriptions,
                    "evidence_level": rule.get("evidence_level"),
                    "references": rule.get("references", [])
                })
                
                # Merge effects
                if effects.get("add_to_differential"):
                    context_result["context_differential"].extend(effects["add_to_differential"])
                
                if effects.get("add_questions"):
                    context_result["context_questions"].extend(effects["add_questions"])
                
                if effects.get("add_workup"):
                    context_result["context_workup"].extend(effects["add_workup"])
                
                if effects.get("add_red_flags"):
                    context_result["context_red_flags"].extend(effects["add_red_flags"])
                
                if effects.get("referral_notes"):
                    context_result["context_referral_notes"].extend(effects["referral_notes"])
                
                if effects.get("adjust_urgency"):
                    # Keep most urgent adjustment
                    current_urgency = context_result.get("urgency_adjustment")
                    new_urgency = effects["adjust_urgency"]
                    if current_urgency is None or "urgent" in new_urgency:
                        context_result["urgency_adjustment"] = new_urgency
                
                if effects.get("reasoning"):
                    context_result["reasoning"].append({
                        "rule": rule_name,
                        "explanation": effects["reasoning"],
                        "clinical_pearls": effects.get("clinical_pearls", []),
                        "evidence_level": rule.get("evidence_level"),
                        "references": rule.get("references", [])
                    })
        
        # Deduplicate lists
        for key in ["context_differential", "context_questions", "context_workup", 
                    "context_red_flags", "context_referral_notes"]:
            context_result[key] = list(dict.fromkeys(context_result[key]))  # Preserve order
        
        return context_result
    
    def get_context_summary(self, patient_context: Dict[str, Any]) -> List[str]:
        """
        Generate a human-readable summary of active context modifiers.
        
        Args:
            patient_context: Patient's context data
        
        Returns:
            List of summary strings (e.g., ["High iodine exposure", "Recent travel: South Asia"])
        """
        summary = []
        
        # Check for high iodine exposure
        if (patient_context.get("seaweed_kelp_supplement") or 
            patient_context.get("seafood_frequency_per_week", 0) >= 5 or
            patient_context.get("amiodarone_use")):
            summary.append("High iodine exposure")
        
        # Check for travel
        travel_regions = patient_context.get("recent_travel_regions", [])
        if travel_regions and "none" not in travel_regions:
            region_labels = {
                "south_asia": "South Asia",
                "southeast_asia": "Southeast Asia",
                "sub_saharan_africa": "Sub-Saharan Africa",
                "central_south_america": "Central/South America",
                "middle_east": "Middle East",
                "east_asia": "East Asia",
                "caribbean": "Caribbean"
            }
            regions = [region_labels.get(r, r) for r in travel_regions]
            summary.append(f"Recent travel: {', '.join(regions)}")
        
        # Check for dietary exposures
        if patient_context.get("raw_fish_consumption") == "frequently":
            summary.append("Frequent raw fish consumption")
        
        if patient_context.get("unpasteurized_dairy"):
            summary.append("Unpasteurized dairy consumption")
        
        # Check for supplements
        if patient_context.get("herbal_traditional_meds"):
            summary.append("Herbal/traditional medicines")
        
        if patient_context.get("biotin_supplement"):
            summary.append("High-dose biotin supplement")
        
        # Check for environmental exposures
        if patient_context.get("occupational_exposure_metals"):
            summary.append("Occupational metal exposure")
        
        if patient_context.get("well_water_use"):
            summary.append("Well water use")
        
        if patient_context.get("recreational_water_exposure"):
            summary.append("Recreational water exposure")
        
        return summary


# Global instance
_context_engine = None


def get_context_engine() -> ContextEngine:
    """Get or create the global context engine instance."""
    global _context_engine
    if _context_engine is None:
        _context_engine = ContextEngine()
    return _context_engine
