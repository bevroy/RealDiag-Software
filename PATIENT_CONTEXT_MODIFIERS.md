# Patient Context Modifiers

## Overview

The **Patient Context Modifiers** feature allows clinicians to enter exposure- and lifestyle-based variables (diet, travel, occupational exposures, supplements, etc.) that can modify diagnostic pathways. The system uses these patient-entered facts to provide context-specific considerations for differential diagnosis, workup, risk assessment, and referral guidance.

## Core Principles

### Safety & Ethics

1. **No Demographic Inference**: The system does NOT infer anything from race, ethnicity, or culture
2. **Opt-In Only**: All context variables are optional inputs
3. **Patient-Entered Facts**: Only uses information explicitly provided by the patient or clinician
4. **Guideline-Based**: All suggestions are based on clinical guidelines and evidence
5. **Non-Prescriptive**: Outputs are phrased as "Consider...", "May increase likelihood...", "Ask about..."
6. **Transparent**: Every modification includes reasoning, evidence levels, and citations

### Clinical Use

- Enhance diagnostic accuracy by considering relevant exposures
- Identify region-specific diseases in travelers
- Recognize diet-related conditions
- Detect supplement-drug interactions
- Flag occupational and environmental hazards
- Consider endemic disease risks

## Architecture

### Data Model

The feature consists of two main JSON schemas:

#### 1. Context Variables (`context_variables.json`)

Defines available patient context inputs:

```json
{
  "id": "seafood_frequency_per_week",
  "label": "How many servings of seafood do you consume per week?",
  "category": "Diet",
  "type": "numeric",
  "units": "servings/week",
  "help_text": "Include fish, shellfish, and sea vegetables...",
  "evidence_level": "High",
  "references": [...]
}
```

**Fields:**
- `id`: Unique identifier
- `label`: User-facing question text
- `category`: Grouping (Diet, Supplements, Travel, Occupational, etc.)
- `type`: Input type (boolean, numeric, single_select, multi_select, text)
- `options`: For select types
- `units`: For numeric types
- `help_text`: Explanatory text
- `evidence_level`: High, Moderate, or Low
- `references`: Array of citations

#### 2. Context Rules (`context_rules.json`)

Defines how context affects diagnosis modules:

```json
{
  "id": "ctx_rule_001",
  "diagnosis_module_id": "endocrine_hyperthyroidism",
  "name": "High Iodine Exposure - Hyperthyroidism",
  "triggers": [
    {
      "expression": "seaweed_kelp_supplement == true",
      "description": "Patient takes seaweed/kelp supplements"
    },
    {
      "expression": "seafood_frequency_per_week >= 5",
      "description": "High seafood consumption"
    }
  ],
  "trigger_logic": "any",
  "effects": {
    "add_to_differential": [...],
    "add_questions": [...],
    "add_workup": [...],
    "add_red_flags": [...],
    "adjust_urgency": "consider_urgent_if_cardiac_symptoms",
    "referral_notes": [...],
    "reasoning": "...",
    "clinical_pearls": [...]
  },
  "evidence_level": "High",
  "references": [...]
}
```

**Fields:**
- `id`: Unique rule identifier
- `diagnosis_module_id`: Links to specific diagnosis pathway
- `triggers`: Array of conditional expressions
- `trigger_logic`: "any" (OR) or "all" (AND)
- `effects`: Modifications to apply when triggered
- `reasoning`: Clinical explanation
- `evidence_level`: Quality of evidence
- `references`: Supporting citations

### Trigger Expression Syntax

Supports:
- **Boolean**: `seaweed_kelp_supplement == true`
- **Numeric**: `seafood_frequency_per_week >= 5`
- **String**: `iodized_salt_use == 'often'`
- **Array membership**: `recent_travel_regions includes 'south_asia'`
- **Logical AND**: `salt_use == 'often' AND seafood >= 3`
- **Logical OR**: `kelp == true OR contrast == true`

### Effects Structure

```json
"effects": {
  "add_to_differential": [
    "Iodine-induced hyperthyroidism (Jod-Basedow)",
    "Amiodarone-induced thyrotoxicosis"
  ],
  "add_questions": [
    "When did the high iodine exposure begin?",
    "Any recent CT scans with contrast?"
  ],
  "add_workup": [
    "TSH, free T4, total T3",
    "24-hour urinary iodine excretion"
  ],
  "add_red_flags": [
    "Severe tachycardia or new atrial fibrillation",
    "Signs of thyroid storm"
  ],
  "adjust_urgency": "consider_urgent_if_cardiac_symptoms",
  "referral_notes": [
    "Consider endocrinology referral for severe symptoms"
  ],
  "reasoning": "Excess iodine intake can trigger...",
  "clinical_pearls": [
    "Jod-Basedow is more common in iodine-deficient populations",
    "Thyroid uptake scan shows low uptake"
  ]
}
```

## Backend Implementation

### Context Engine (`context_engine.py`)

Core service that:
1. Loads variable and rule definitions
2. Evaluates trigger expressions
3. Applies matching rules to diagnosis modules
4. Merges context modifications additively
5. Generates human-readable summaries

**Key Methods:**

```python
engine = ContextEngine()

# Get available variables
variables = engine.get_variables(category="Diet")

# Apply context to diagnosis
result = engine.apply_context(
    diagnosis_module_id="endocrine_hyperthyroidism",
    patient_context={
        "seafood_frequency_per_week": 7,
        "seaweed_kelp_supplement": True
    }
)

# Generate summary
summary = engine.get_context_summary(patient_context)
# Returns: ["High iodine exposure", "Frequent raw fish consumption"]
```

### Context Router (`context_router.py`)

FastAPI endpoints:

**GET /context/variables**
- Get context variable definitions
- Optional: filter by category
- Returns variables with help text, evidence, references

**GET /context/categories**
- Get list of categories
- Returns: ["Diet", "Supplements", "Travel", etc.]

**POST /context/evaluate/{diagnosis_module_id}**
- Evaluate patient context against diagnosis module
- Body: `{"patient_context": {...}}`
- Returns: context modifications with reasoning

**POST /context/summary**
- Generate human-readable summary
- Body: `{"patient_context": {...}}`
- Returns: array of summary strings

**GET /context/rules/{diagnosis_module_id}**
- Get all rules for a diagnosis module
- Returns: rule metadata and effect counts

### Integration with Diagnostic Router

Updated `evaluate_tree` endpoint to:
1. Accept optional `patient_context` in request body
2. Apply context rules after base evaluation
3. Merge context results into response
4. Add context summary for UI display

Example request:

```json
POST /diagnostic/evaluate/endocrine_hyperthyroidism
{
  "symptoms": ["palpitations", "weight loss"],
  "age": 45,
  "patient_context": {
    "seafood_frequency_per_week": 7,
    "seaweed_kelp_supplement": true,
    "amiodarone_use": false
  }
}
```

Example response:

```json
{
  "tree_result": {...},
  "context": {
    "has_context": true,
    "context_applied": [
      {
        "rule_id": "ctx_rule_001",
        "rule_name": "High Iodine Exposure - Hyperthyroidism",
        "matched_triggers": ["High seafood consumption", "Seaweed supplements"],
        "evidence_level": "High"
      }
    ],
    "context_differential": [
      "Iodine-induced hyperthyroidism (Jod-Basedow)",
      "Iodine-induced thyroiditis"
    ],
    "context_questions": [
      "When did the high iodine exposure begin?",
      "Any recent CT scans with contrast?"
    ],
    "context_workup": [
      "TSH, free T4, total T3",
      "Thyroid antibodies (TPO, TSI)"
    ],
    "reasoning": [
      {
        "rule": "High Iodine Exposure",
        "explanation": "Excess iodine intake can trigger...",
        "clinical_pearls": [...],
        "evidence_level": "High",
        "references": [...]
      }
    ]
  },
  "context_summary": ["High iodine exposure"]
}
```

## Frontend Implementation

### PatientContext Component (`PatientContext.jsx`)

Collapsible panel for entering context data:

**Features:**
- Dynamic form generation from API variables
- Grouped by category
- Help text and evidence levels displayed
- Context summary chips when collapsed
- Clear all button
- Disclaimer banner

**Props:**
- `value`: Current context data object
- `onChange`: Callback when data changes
- `apiBase`: API base URL

**Usage:**

```jsx
import PatientContext from '@/components/PatientContext'

<PatientContext
  value={patientContext}
  onChange={setPatientContext}
  apiBase={apiBase}
/>
```

### ContextResults Component (`ContextResults.jsx`)

Displays context-based modifications:

**Features:**
- Additional differential diagnoses
- Additional questions to ask
- Additional workup suggestions
- Red flags and warnings
- Urgency adjustments
- Referral guidance
- Detailed reasoning (toggle)
- Clinical pearls
- Evidence levels and citations

**Props:**
- `contextData`: Context result object from API

**Usage:**

```jsx
import ContextResults from '@/components/ContextResults'

{result.context && (
  <ContextResults contextData={result.context} />
)}
```

## Starter Library

### Context Variables (15 total)

**Diet (3):**
1. `seafood_frequency_per_week` - Numeric
2. `iodized_salt_use` - Single select (never/sometimes/often)
3. `raw_fish_consumption` - Single select
4. `unpasteurized_dairy` - Boolean

**Supplements (3):**
5. `seaweed_kelp_supplement` - Boolean
6. `herbal_traditional_meds` - Boolean
7. `biotin_supplement` - Boolean

**Travel (2):**
8. `recent_travel_regions` - Multi-select (South Asia, Southeast Asia, etc.)
9. `country_of_birth` - Text (optional)
10. `years_in_us` - Numeric

**Medical (2):**
11. `recent_iodinated_contrast` - Boolean
12. `amiodarone_use` - Boolean

**Environmental (3):**
13. `occupational_exposure_metals` - Boolean
14. `well_water_use` - Boolean
15. `recreational_water_exposure` - Boolean

### Context Rules (12 total)

#### Endocrine/Thyroid (3 rules)
1. **High Iodine - Hyperthyroidism** (`endocrine_hyperthyroidism`)
   - Triggers: Kelp supplements, high seafood, contrast, amiodarone
   - Adds: Jod-Basedow, amiodarone thyrotoxicosis
   
2. **High Iodine - Goiter** (`endocrine_goiter_nodules`)
   - Triggers: Similar iodine exposures
   - Adds: Iodine-induced goiter, Wolff-Chaikoff effect

3. **Biotin Interference** (`labs_abnormal_thyroid`)
   - Triggers: High-dose biotin supplement
   - Adds: Warning about lab interference

#### Infectious Disease (6 rules)
4. **Raw Fish - GI Illness** (`gi_gastroenteritis`)
   - Triggers: Frequent raw fish consumption
   - Adds: Anisakiasis, scombroid, ciguatera, Vibrio

5. **Travel South Asia - Fever** (`id_travel_fever`)
   - Triggers: Recent travel to South Asia
   - Adds: Malaria, typhoid, dengue, chikungunya
   - Urgency: URGENT

6. **Travel Sub-Saharan Africa - Fever** (`id_travel_fever`)
   - Triggers: Recent travel to Africa
   - Adds: P. falciparum malaria, hemorrhagic fevers
   - Urgency: URGENT

7. **Endemic Fungal Regions** (`id_pneumonia`)
   - Triggers: Travel to Central/South America
   - Adds: Histoplasmosis, coccidioidomycosis

8. **Unpasteurized Dairy - Diarrhea** (`gi_diarrhea_acute`)
   - Triggers: Raw dairy consumption
   - Adds: E. coli O157:H7, Listeria, Salmonella

9. **Well Water - Hepatitis** (`gi_hepatitis`)
   - Triggers: Well water use
   - Adds: Hepatitis A/E, heavy metal toxicity

#### Other (3 rules)
10. **Occupational Metals - Headache** (`neuro_headache_chronic`)
    - Triggers: Metal exposure at work
    - Adds: Lead, mercury, arsenic poisoning

11. **Herbal Supplements - GI** (`gi_diarrhea_chronic`)
    - Triggers: Herbal medicine use
    - Adds: Herb-induced diarrhea, hepatotoxicity

12. **Recreational Water - Meningitis** (`id_meningitis`)
    - Triggers: Swimming in natural water
    - Adds: Naegleria fowleri, leptospirosis
    - Urgency: URGENT

## Testing

Run tests:

```bash
pytest backend/tests/test_context_engine.py -v
```

**Test Coverage:**
- Variable and rule loading
- Trigger expression evaluation (all operators)
- Rule matching logic (any/all)
- Context application to modules
- Deduplication
- Summary generation
- Evidence levels and references
- Multiple rules per module
- Edge cases (empty context, no matches)

## Adding New Variables

1. Edit `backend/data/context/context_variables.json`
2. Add new variable definition:

```json
{
  "id": "new_variable",
  "label": "Question text?",
  "category": "Category Name",
  "type": "boolean|numeric|single_select|multi_select|text",
  "options": [...],  // if select type
  "units": "units",  // if numeric
  "help_text": "Explanation...",
  "evidence_level": "High|Moderate|Low",
  "references": [
    {
      "title": "Reference Title",
      "organization": "Organization",
      "year": 2024,
      "url_or_citation": "URL or citation string"
    }
  ]
}
```

3. Restart backend - changes load automatically

## Adding New Rules

1. Edit `backend/data/context/context_rules.json`
2. Add new rule definition:

```json
{
  "id": "ctx_rule_###",
  "diagnosis_module_id": "module_id",
  "name": "Rule Name",
  "triggers": [
    {
      "expression": "variable_id == value",
      "description": "Human-readable trigger description"
    }
  ],
  "trigger_logic": "any",
  "effects": {
    "add_to_differential": [...],
    "add_questions": [...],
    "add_workup": [...],
    "add_red_flags": [...],
    "adjust_urgency": "none|consider_urgent|urgent",
    "referral_notes": [...],
    "reasoning": "Clinical explanation...",
    "clinical_pearls": [...]
  },
  "evidence_level": "High",
  "references": [...]
}
```

3. Restart backend - changes load automatically

## Best Practices

### Variable Design
- Use clear, jargon-free labels
- Provide helpful explanatory text
- Include evidence levels and citations
- Keep inputs simple (avoid complex multi-part questions)
- Make all variables optional

### Rule Design
- Be specific about triggering conditions
- Use multiple triggers with "any" logic for flexibility
- Phrase effects as considerations, not directives
- Include detailed reasoning and clinical pearls
- Cite authoritative guidelines
- Test trigger expressions thoroughly

### Clinical Use
- Review context summary before finalizing diagnosis
- Consider context-based additions in your DDx
- Use context to guide targeted history and workup
- Remember: these are suggestions, not requirements
- Document context factors in clinical notes

### Safety
- Never auto-populate based on demographics
- Always require explicit user input
- Phrase outputs as "Consider..." not "Do..."
- Include disclaimer: "Does not replace clinical judgment"
- Provide evidence levels for transparency
- Cite guidelines for all recommendations

## Troubleshooting

**Variables not showing:**
- Check JSON syntax in `context_variables.json`
- Verify API endpoint: `GET /context/variables`
- Check browser console for errors

**Rules not triggering:**
- Test trigger expression in isolation
- Verify variable IDs match exactly
- Check trigger_logic (any vs all)
- Verify diagnosis_module_id matches tree ID

**Missing references:**
- Ensure references array is properly formatted
- Include all required fields (title, organization, year)
- Use url_or_citation for links or text citations

## Future Enhancements

Potential additions:
- Vaccination history
- Pregnancy status handling
- Pediatric age-specific rules
- Genetic testing results integration
- Social determinants of health (with extreme care)
- Machine learning for pattern detection
- Multi-language support
- Mobile app integration

## Compliance & Legal

- **HIPAA**: Context data is PHI - handle accordingly
- **Consent**: Obtain patient consent for data collection
- **Documentation**: Document all context factors in medical record
- **Liability**: Tool provides information only, not medical advice
- **Disclaimer**: Always displayed prominently in UI
- **Validation**: Regular review of rules for accuracy
- **Updates**: Keep references current with latest guidelines

## Support & Contact

For questions or issues:
- File GitHub issue: [RealDiag-Software](https://github.com/bevroy/RealDiag-Software)
- Review test cases for examples
- Check API documentation: `/docs` endpoint

---

**Version**: 1.0.0  
**Last Updated**: December 29, 2025  
**License**: See LICENSE file
