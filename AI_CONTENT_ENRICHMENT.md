# AI Content Enrichment for RealDiag

## Overview

RealDiag now supports **AI-powered content enrichment** for diagnostic search results. When a user searches for a diagnosis that exists in the database but lacks complete clinical information (treatment, clinical pearls, referrals, homeopathic remedies), the system can automatically generate this missing content using AI.

## Features

- **Automatic Detection**: The system detects which clinical sections are missing from each diagnosis
- **On-Demand Generation**: Content is generated in real-time when a user searches for a diagnosis
- **Evidence-Based**: AI prompts are designed to generate evidence-based medical content following current guidelines
- **Clear Labeling**: AI-generated content is clearly marked with a disclaimer in the UI
- **Conservative Approach**: Uses low temperature (0.3) for more conservative, guideline-based responses

## Enriched Content Sections

The AI can generate the following missing sections:

1. **Workup**: Diagnostic tests, lab values, imaging, physical exam findings
2. **Treatment**: Evidence-based treatment recommendations with specific medications and dosages
3. **Clinical Pearls**: Key diagnostic insights, red flags, and practice tips
4. **Referrals**: Specialty referral criteria with specific indications
5. **Homeopathic Remedies**: Classical homeopathic remedies with constitutional indications
6. **Presentations**: Common symptom patterns and clinical presentations

## Setup

### 1. Install Dependencies

```bash
pip install anthropic openai
```

### 2. Configure API Keys

Add one of the following to your `.env` file:

```bash
# Option 1: Use Claude (recommended for medical content)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
AI_PROVIDER=claude

# Option 2: Use OpenAI GPT-4
OPENAI_API_KEY=your_openai_api_key_here
AI_PROVIDER=openai
```

### 3. Enable Feature

The feature is automatically enabled when valid API keys are detected. No additional configuration needed.

To **disable** AI enrichment:
- Simply don't set the API keys, or
- Remove the API keys from environment variables

## How It Works

### Backend Flow

1. **Search Request**: User searches for a diagnosis (e.g., "pneumonia")
2. **Data Extraction**: System extracts available clinical data from tree files
3. **Gap Detection**: Identifies which sections are missing or empty
4. **AI Generation**: If gaps exist and AI is enabled:
   - Creates evidence-based prompt for missing sections
   - Calls AI provider (Claude or OpenAI)
   - Parses JSON response
   - Merges with existing data
5. **Response**: Returns enriched diagnosis with metadata

### Frontend Display

- Results with AI-generated content show a blue banner with 🤖 icon
- Banner lists which sections were AI-enhanced
- Includes disclaimer about verifying with medical guidelines
- All enriched content appears with standard formatting

## API Response Format

```json
{
  "query": "pneumonia",
  "count": 3,
  "ai_enrichment_enabled": true,
  "results": [
    {
      "name": "Pneumonia",
      "icd10": "J18.9",
      "treatment": [
        "Community-acquired pneumonia (CAP): amoxicillin 1g TID or doxycycline 100mg BID x5-7 days for outpatient",
        "CURB-65 score ≥2: consider hospitalization"
      ],
      "clinical_pearls": [
        "Viral URI symptoms preceding bacterial pneumonia is common",
        "CXR may lag behind clinical improvement by several days"
      ],
      "ai_enriched": true,
      "ai_enriched_sections": ["treatment", "clinical_pearls", "referrals"]
    }
  ]
}
```

## Prompt Engineering

The AI enricher uses carefully crafted prompts that:

- Request evidence-based content following current guidelines
- Specify exact JSON format for consistent parsing
- Include medication names, dosages, and durations
- Require specific referral criteria
- Follow classical homeopathic prescribing principles
- Use professional medical terminology

Example prompt structure:
```
You are a medical expert. Generate comprehensive clinical content for:

Diagnosis: [Name]
ICD-10: [Code]

Generate these MISSING sections: treatment, clinical_pearls, referrals

[Detailed instructions for each section...]

Return ONLY valid JSON with no additional text.
```

## Cost Considerations

### Claude (Anthropic)
- **Model**: claude-3-5-sonnet-20241022
- **Cost**: ~$0.003 per enriched diagnosis (4K tokens)
- **Speed**: 2-3 seconds per diagnosis
- **Quality**: Excellent for medical content

### OpenAI GPT-4
- **Model**: gpt-4
- **Cost**: ~$0.03-0.06 per enriched diagnosis
- **Speed**: 3-5 seconds per diagnosis
- **Quality**: Very good

### Optimization Strategies

1. **Cache Results**: Once enriched, data is returned from the existing tree files on subsequent searches (no re-generation)
2. **Batch Processing**: Consider pre-enriching all incomplete diagnoses during off-peak hours
3. **Selective Enrichment**: Only enriches diagnoses that are actually searched by users
4. **Conservative Temperature**: Lower temperature (0.3) reduces token usage

## Safety & Disclaimers

### Medical Disclaimer

All AI-generated content includes prominent disclaimers:
- Clear labeling that content is AI-generated
- Instruction to verify with current medical guidelines
- Recommendation to consult healthcare providers
- List of which specific sections were AI-generated

### Quality Control

- **Evidence-Based Prompts**: Designed to follow established guidelines
- **Conservative Temperature**: Low temperature for more deterministic, guideline-based responses
- **JSON Validation**: Responses must parse as valid JSON or enrichment fails gracefully
- **Fallback**: If AI enrichment fails, returns original (incomplete) data without error

### Limitations

- AI-generated content should not replace clinical decision trees created by medical professionals
- Content is based on training data which may not include the most recent guidelines (check model training cutoff)
- Best used as supplementary information for rare diagnoses lacking complete tree files
- Healthcare providers must verify all recommendations independently

## Future Enhancements

### Potential Improvements

1. **Persistent Storage**: Save AI-enriched content back to tree files for future use
2. **Admin Review Queue**: Allow administrators to review and approve AI-generated content
3. **Version Control**: Track when content was generated and by which model
4. **Citation Generation**: Add references to specific guidelines mentioned
5. **Specialty-Specific Prompts**: Customize prompts based on medical specialty
6. **Batch Enrichment**: CLI tool to pre-enrich all incomplete trees
7. **User Feedback**: Allow users to rate AI-generated content quality

### Admin Dashboard

Consider adding:
- Toggle to enable/disable AI enrichment per specialty
- Statistics on which diagnoses have been enriched
- Model and provider selection
- Cost tracking per diagnosis
- Quality metrics from user feedback

## Monitoring

### Logs to Monitor

```python
# Success
"✓ Enriched diagnosis: [name] with [sections]"

# Warnings
"Warning: Could not enrich [name]: [error]"

# Info
"AI enrichment enabled with provider: [claude|openai]"
"AI enrichment disabled: no API keys found"
```

### Metrics to Track

- Number of diagnoses enriched per day
- Most frequently enriched diagnoses
- Average enrichment time
- Enrichment success rate
- Cost per enriched diagnosis

## Troubleshooting

### AI Enrichment Not Working

1. **Check API Keys**: Verify `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` is set
2. **Check Imports**: Ensure `anthropic` and `openai` packages are installed
3. **Check Logs**: Look for initialization errors in backend logs
4. **Test Manually**: Try importing AIContentEnricher in Python console

### Content Quality Issues

1. **Lower Temperature**: Already at 0.3 (conservative)
2. **Refine Prompts**: Edit prompt in `ai_content_enricher.py`
3. **Switch Providers**: Try Claude if using OpenAI or vice versa
4. **Add Examples**: Include few-shot examples in prompt

### Performance Issues

1. **Cache at CDN**: Cache search API responses for popular queries
2. **Pre-Enrich**: Run batch enrichment during off-peak hours
3. **Increase Timeout**: Adjust API timeout in enricher
4. **Use Faster Model**: Try claude-3-haiku for speed over quality

## API Documentation

### Endpoint: `GET /api/search?q={query}`

**Response includes AI enrichment metadata:**

```typescript
{
  query: string;
  count: number;
  ai_enrichment_enabled: boolean;  // NEW
  results: Array<{
    name: string;
    // ... existing fields ...
    ai_enriched?: boolean;          // NEW
    ai_enriched_sections?: string[]; // NEW
  }>;
}
```

## Examples

### Example 1: Complete Diagnosis (No Enrichment Needed)

Search: "pneumonia" with existing comprehensive tree
- System finds complete tree with all sections
- Returns data as-is, no AI generation
- `ai_enriched: false`

### Example 2: Partial Diagnosis (Enrichment Applied)

Search: "pityriasis rosea" with minimal tree data
- System finds tree with only basic info
- Detects missing: treatment, clinical_pearls, referrals
- Calls AI to generate missing sections
- Merges AI content with existing data
- Returns enriched result with `ai_enriched: true`

### Example 3: ICD-10 Search (Enrichment Applied)

Search: "M79.3" (ICD-10 code for panniculitis)
- System finds ICD-10 code but no tree file
- Creates basic result from ICD-10 database
- Detects all clinical sections missing
- Enriches with AI-generated comprehensive content
- Returns enriched ICD-10 result

## Conclusion

AI content enrichment significantly enhances the diagnostic search feature by:
- Providing comprehensive information even for rare diagnoses
- Maintaining high-quality, evidence-based content
- Clearly distinguishing AI-generated from human-curated content
- Operating seamlessly without user intervention

This feature is **production-ready** but should be used as a supplement to, not replacement for, expert-curated diagnostic trees.
