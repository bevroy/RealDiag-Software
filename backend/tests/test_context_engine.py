"""
Tests for Patient Context Modifiers Engine
"""

import pytest
from backend.services.context_engine import ContextEngine


@pytest.fixture
def engine():
    """Create a context engine instance."""
    return ContextEngine()


@pytest.fixture
def sample_context():
    """Sample patient context data."""
    return {
        "seafood_frequency_per_week": 7,
        "seaweed_kelp_supplement": True,
        "recent_travel_regions": ["south_asia", "southeast_asia"],
        "raw_fish_consumption": "frequently",
        "amiodarone_use": False,
        "biotin_supplement": True
    }


def test_load_variables(engine):
    """Test that variables are loaded correctly."""
    assert len(engine.variables) > 0
    assert any(v["id"] == "seafood_frequency_per_week" for v in engine.variables)


def test_load_rules(engine):
    """Test that rules are loaded correctly."""
    assert len(engine.rules) > 0
    assert any(r["id"] == "ctx_rule_001" for r in engine.rules)


def test_get_categories(engine):
    """Test getting categories."""
    categories = engine.get_categories()
    assert "Diet" in categories
    assert "Supplements" in categories
    assert "Travel" in categories


def test_get_variables_by_category(engine):
    """Test filtering variables by category."""
    diet_vars = engine.get_variables(category="Diet")
    assert all(v["category"] == "Diet" for v in diet_vars)
    assert len(diet_vars) > 0


def test_evaluate_simple_trigger(engine):
    """Test evaluating a simple boolean trigger."""
    trigger = "seaweed_kelp_supplement == true"
    context = {"seaweed_kelp_supplement": True}
    
    result = engine._evaluate_trigger(trigger, context)
    assert result is True


def test_evaluate_numeric_trigger(engine):
    """Test evaluating a numeric comparison trigger."""
    trigger = "seafood_frequency_per_week >= 5"
    context = {"seafood_frequency_per_week": 7}
    
    result = engine._evaluate_trigger(trigger, context)
    assert result is True
    
    context2 = {"seafood_frequency_per_week": 3}
    result2 = engine._evaluate_trigger(trigger, context2)
    assert result2 is False


def test_evaluate_includes_trigger(engine):
    """Test evaluating an 'includes' trigger for arrays."""
    trigger = "recent_travel_regions includes 'south_asia'"
    context = {"recent_travel_regions": ["south_asia", "southeast_asia"]}
    
    result = engine._evaluate_trigger(trigger, context)
    assert result is True
    
    context2 = {"recent_travel_regions": ["east_asia"]}
    result2 = engine._evaluate_trigger(trigger, context2)
    assert result2 is False


def test_evaluate_and_trigger(engine):
    """Test evaluating an AND trigger."""
    trigger = "iodized_salt_use == 'often' AND seafood_frequency_per_week >= 3"
    context = {
        "iodized_salt_use": "often",
        "seafood_frequency_per_week": 5
    }
    
    result = engine._evaluate_trigger(trigger, context)
    assert result is True
    
    context2 = {
        "iodized_salt_use": "never",
        "seafood_frequency_per_week": 5
    }
    result2 = engine._evaluate_trigger(trigger, context2)
    assert result2 is False


def test_apply_context_hyperthyroidism_high_iodine(engine, sample_context):
    """Test applying context to hyperthyroidism module with high iodine exposure."""
    result = engine.apply_context(
        diagnosis_module_id="endocrine_hyperthyroidism",
        patient_context=sample_context
    )
    
    assert result["has_context"] is True
    assert len(result["context_applied"]) > 0
    
    # Check that iodine-related differential is added
    assert any("Iodine" in dx or "iodine" in dx for dx in result["context_differential"])
    
    # Check that questions are added
    assert len(result["context_questions"]) > 0
    
    # Check that workup is added
    assert len(result["context_workup"]) > 0
    
    # Check that reasoning is provided
    assert len(result["reasoning"]) > 0


def test_apply_context_travel_fever(engine, sample_context):
    """Test applying context to travel fever module."""
    result = engine.apply_context(
        diagnosis_module_id="id_travel_fever",
        patient_context=sample_context
    )
    
    assert result["has_context"] is True
    
    # Check for malaria and dengue in differential
    differential_str = " ".join(result["context_differential"]).lower()
    assert "malaria" in differential_str
    
    # Check for urgency adjustment
    assert result["urgency_adjustment"] is not None


def test_apply_context_no_matching_rules(engine):
    """Test applying context when no rules match."""
    minimal_context = {"well_water_use": False}
    
    result = engine.apply_context(
        diagnosis_module_id="endocrine_hyperthyroidism",
        patient_context=minimal_context
    )
    
    # No rules should match
    assert result["has_context"] is False or len(result["context_applied"]) == 0


def test_apply_context_empty_context(engine):
    """Test applying context with empty patient context."""
    result = engine.apply_context(
        diagnosis_module_id="endocrine_hyperthyroidism",
        patient_context={}
    )
    
    assert result["has_context"] is False


def test_context_summary(engine, sample_context):
    """Test generating context summary."""
    summary = engine.get_context_summary(sample_context)
    
    assert len(summary) > 0
    assert any("iodine" in s.lower() for s in summary)
    assert any("travel" in s.lower() for s in summary)
    assert any("fish" in s.lower() for s in summary)


def test_context_summary_empty(engine):
    """Test context summary with no active modifiers."""
    summary = engine.get_context_summary({})
    assert len(summary) == 0


def test_deduplication(engine):
    """Test that context results are deduplicated."""
    context = {
        "seaweed_kelp_supplement": True,
        "seafood_frequency_per_week": 10,
        "amiodarone_use": True  # Multiple triggers for same rule
    }
    
    result = engine.apply_context(
        diagnosis_module_id="endocrine_hyperthyroidism",
        patient_context=context
    )
    
    # Should not have duplicate differential items
    differential = result["context_differential"]
    assert len(differential) == len(set(differential))


def test_trigger_logic_any(engine):
    """Test that 'any' trigger logic works correctly."""
    # Rule ctx_rule_001 has trigger_logic: "any"
    # Should match if ANY trigger is satisfied
    
    context_kelp_only = {"seaweed_kelp_supplement": True}
    result1 = engine.apply_context(
        diagnosis_module_id="endocrine_hyperthyroidism",
        patient_context=context_kelp_only
    )
    assert result1["has_context"] is True
    
    context_seafood_only = {"seafood_frequency_per_week": 10}
    result2 = engine.apply_context(
        diagnosis_module_id="endocrine_hyperthyroidism",
        patient_context=context_seafood_only
    )
    assert result2["has_context"] is True


def test_evidence_levels_included(engine, sample_context):
    """Test that evidence levels are included in results."""
    result = engine.apply_context(
        diagnosis_module_id="endocrine_hyperthyroidism",
        patient_context=sample_context
    )
    
    if result["has_context"] and len(result["context_applied"]) > 0:
        rule = result["context_applied"][0]
        assert "evidence_level" in rule
        assert rule["evidence_level"] in ["High", "Moderate", "Low"]


def test_references_included(engine, sample_context):
    """Test that references are included in reasoning."""
    result = engine.apply_context(
        diagnosis_module_id="endocrine_hyperthyroidism",
        patient_context=sample_context
    )
    
    if result["has_context"] and len(result["reasoning"]) > 0:
        reasoning_item = result["reasoning"][0]
        assert "references" in reasoning_item
        assert len(reasoning_item["references"]) > 0
        
        ref = reasoning_item["references"][0]
        assert "title" in ref
        assert "organization" in ref
        assert "year" in ref


def test_biotin_interference_rule(engine):
    """Test biotin supplement interference rule."""
    context = {"biotin_supplement": True}
    
    result = engine.apply_context(
        diagnosis_module_id="labs_abnormal_thyroid",
        patient_context=context
    )
    
    assert result["has_context"] is True
    
    # Should add differential about biotin interference
    differential_str = " ".join(result["context_differential"]).lower()
    assert "biotin" in differential_str


def test_raw_fish_gi_rule(engine):
    """Test raw fish consumption GI illness rule."""
    context = {"raw_fish_consumption": "frequently"}
    
    result = engine.apply_context(
        diagnosis_module_id="gi_gastroenteritis",
        patient_context=context
    )
    
    assert result["has_context"] is True
    
    # Should add parasitic infections to differential
    differential_str = " ".join(result["context_differential"]).lower()
    assert "anisakiasis" in differential_str or "anisakis" in differential_str


def test_multiple_rules_same_module(engine):
    """Test that multiple rules can apply to the same module."""
    context = {
        "seaweed_kelp_supplement": True,
        "recent_iodinated_contrast": True,
        "amiodarone_use": True
    }
    
    result = engine.apply_context(
        diagnosis_module_id="endocrine_hyperthyroidism",
        patient_context=context
    )
    
    # All triggers should be captured
    applied_rule = result["context_applied"][0]
    assert len(applied_rule["matched_triggers"]) >= 3


def test_clinical_pearls_included(engine, sample_context):
    """Test that clinical pearls are included in reasoning."""
    result = engine.apply_context(
        diagnosis_module_id="endocrine_hyperthyroidism",
        patient_context=sample_context
    )
    
    if result["has_context"] and len(result["reasoning"]) > 0:
        reasoning_item = result["reasoning"][0]
        assert "clinical_pearls" in reasoning_item


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
