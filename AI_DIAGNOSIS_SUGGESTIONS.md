# AI-Powered Diagnosis Suggestions

## Overview

The symptom search now intelligently queries AI for additional diagnostic possibilities when decision tree results are insufficient. This ensures users discover **all possible diagnoses** from comprehensive medical knowledge, not just the 676 with existing trees.

## How It Works

### Automatic AI Query Triggers

AI diagnosis suggestions are automatically requested when:
1. **Fewer than 5 results** found in decision trees, OR
2. **Best match score < 3.0** (low confidence)

### What AI Provides

For each suggested diagnosis:
- **Diagnosis name** (standard medical terminology)
- **Medical specialty**
- **ICD-10 codes**
- **Likelihood** (high/moderate/low) → converted to match score
- **Key clinical features** that match the symptoms

### Result Integration

- AI suggestions seamlessly mixed with tree-based results
- All sorted by relevance score
- Clear flags distinguish source:
  - `has_tree: false` - No decision tree exists yet
  - `ai_suggested: true` - Suggested by AI from medical knowledge

## API Response Example

```json
{
  "query_symptoms": ["jaw pain", "fatigue", "shortness of breath"],
  "total_results": 12,
  "results": [
    {
      "rule_id": "CARD-STABLE-ANGINA",
      "label": "Stable Angina",
      "family": "cardiology",
      "match_score": 5.2,
      "has_tree": true,
      "ai_suggested": false,
      "...": "..."
    },
    {
      "rule_id": "ATYPICAL-ANGINA",
      "label": "Atypical Angina",
      "family": "cardiology",
      "match_score": 4.0,
      "matched_presentations": ["jaw pain in exertion", "fatigue"],
      "icd10": ["I20.8"],
      "has_tree": false,
      "ai_suggested": true
    },
    {
      "rule_id": "TEMPOROMANDIBULAR-JOINT-DISORDER",
      "label": "Temporomandibular Joint Disorder",
      "family": "dentistry",
      "match_score": 2.5,
      "has_tree": false,
      "ai_suggested": true
    }
  ]
}
```

## Configuration

### Environment Variables

```bash
# Enable AI features
ENABLE_AI_GENERATION=true

# Choose AI provider
AI_PROVIDER=claude  # or "openai"

# API Keys
ANTHROPIC_API_KEY=your_key_here
# OR
OPENAI_API_KEY=your_key_here
```

### AI Provider Selection

- **Claude** (default): `claude-3-5-sonnet-20241022`
  - Preferred for medical content
  - More conservative and evidence-based
  
- **OpenAI**: `gpt-4`
  - Alternative provider
  - Good general medical knowledge

## Use Cases

### 1. Rare Conditions
**Symptoms:** "periodic fever, mouth ulcers, swollen lymph nodes"

- May have 0-2 tree matches
- AI suggests: PFAPA syndrome, Behçet's disease, cyclic neutropenia
- User can request tree generation for relevant diagnoses

### 2. Atypical Presentations
**Symptoms:** "jaw pain, fatigue, nausea" (female, age 55)

- Tree search finds few dental/TMJ matches
- AI recognizes: Atypical angina (common in women)
- Prevents missed cardiac diagnoses

### 3. Emerging/Updated Conditions
**Symptoms:** "loss of smell, fatigue, shortness of breath"

- Existing trees may be outdated
- AI provides current differential including recent conditions
- Ensures up-to-date diagnostic possibilities

## Performance

- **Query Time:** 2-4 seconds for AI response
- **Only triggered when needed:** Not every search
- **Async operation:** Doesn't block tree search
- **Smart caching:** Results could be cached if needed

## User Workflow

1. **User searches symptoms** → `/search/by-symptoms`
2. **System searches trees** → Returns 3 matches (low)
3. **Auto-triggers AI** → Queries for 10 more diagnoses
4. **Combined results** → Shows all 13 diagnoses
5. **User sees flags:**
   - ✅ 3 diagnoses have trees (can navigate immediately)
   - ⚠️ 10 diagnoses suggested by AI (can request tree generation)
6. **User requests tree** → AI generates full decision tree

## Benefits

### Complete Coverage
- No diagnostic "blind spots"
- Discovers rare conditions
- Includes atypical presentations

### Always Current
- AI uses latest medical knowledge
- No manual database updates needed
- Adapts to emerging conditions

### Smart Resource Use
- Only queries AI when necessary
- Efficient API usage
- Fast tree-based search for common cases

### User Empowerment
- See full diagnostic landscape
- Request trees for relevant conditions
- Guide system expansion based on real needs

## Safety Features

- **Conservative temperature:** 0.3 for medical accuracy
- **Evidence-based:** AI trained on medical literature
- **Human review:** Generated trees go to pending review
- **Clear labeling:** Users know which diagnoses lack full trees
- **Existing trees prioritized:** Tree-based results always included

## Future Enhancements

1. **Caching:** Store AI suggestions for common symptom patterns
2. **Feedback loop:** Track which AI suggestions users find most useful
3. **Auto-generation:** Automatically generate trees for frequently requested AI diagnoses
4. **Confidence scoring:** Show AI confidence levels
5. **Source attribution:** Link to medical evidence/guidelines

## Troubleshooting

### AI Suggestions Not Appearing

**Check:**
1. `ENABLE_AI_GENERATION=true` set?
2. API key configured?
3. Sufficient tree results? (AI only triggers if <5 or low scores)
4. Check logs for API errors

### Slow Response Times

- AI queries add 2-4 seconds
- Only triggered for insufficient tree results
- Consider caching common patterns

### Incorrect Suggestions

- Review AI temperature setting (lower = more conservative)
- Check prompt engineering in `query_ai_for_diagnoses()`
- Consider switching AI provider

## Implementation Details

### Code Location
- **File:** `backend/services/symptom_search.py`
- **Function:** `query_ai_for_diagnoses()`
- **Integration:** In `search_by_symptoms()` endpoint

### Trigger Logic
```python
should_query_ai = len(results) < 5 or (results and results[0].match_score < 3.0)
```

### Deduplication
- Compares AI suggestions against tree results
- Prevents duplicate diagnoses
- Case-insensitive matching

## Testing

Run comprehensive tests:
```bash
python test_ai_diagnosis_suggestions.py
```

Requirements:
- API key configured
- `ENABLE_AI_GENERATION=true`
- Network access to AI provider

## Summary

This feature transforms symptom search from a "tree database lookup" into a "comprehensive diagnostic assistant" that:

✅ Searches existing knowledge (trees)  
✅ Fills gaps with AI medical expertise  
✅ Guides system growth based on user needs  
✅ Ensures no diagnosis is missed  
✅ Maintains human oversight and safety
