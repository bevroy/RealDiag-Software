# AI Tree Generation Setup Guide

## Overview
RealDiag can automatically generate diagnostic decision trees for symptom combinations not covered by existing trees using AI (Claude or GPT-4).

## Setup Steps

### 1. Install Required Packages

```bash
pip install openai anthropic
```

### 2. Configure Environment Variables

Copy the example configuration:
```bash
cp .env.ai.example .env
```

Edit `.env` and set your API keys:

```env
# Enable AI generation
ENABLE_AI_GENERATION=true

# Choose provider (claude recommended for medical)
AI_PROVIDER=claude

# Add your API keys
ANTHROPIC_API_KEY=sk-ant-xxx...
# OR
OPENAI_API_KEY=sk-xxx...

# Set secure admin token for review
ADMIN_TOKEN=your_secure_random_token
```

### 3. Generate Admin Token

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Use the output as your `ADMIN_TOKEN`.

### 4. Configure Additional Settings (Optional)

```env
AI_TEMPERATURE=0.3          # Lower = more conservative
AI_MAX_TOKENS=4000          # Max tree size
MIN_SYMPTOMS_FOR_AI=2       # Minimum symptoms to trigger
MIN_CONFIDENCE_THRESHOLD=2.0 # Trigger if best match < this score
```

## How It Works

### Automatic Generation
1. User searches for symptoms
2. If no good matches found (score < 2.0), system detects gap
3. Response includes message about AI generation
4. User can trigger generation via API call

### Generation Process
1. AI analyzes symptoms
2. Generates complete decision tree with:
   - Diagnostic questions
   - Workup recommendations
   - Treatment plans
   - Differential diagnoses
   - Clinical pearls
   - ICD-10 and SNOMED codes
3. Tree saved to `backend/data/generated_trees/pending/`
4. Status: "pending_review"

### Medical Review Workflow
1. Admin accesses `/admin-review` page
2. Logs in with admin token
3. Reviews pending trees
4. Approves or rejects with notes
5. Approved trees move to `approved/` and become searchable
6. Rejected trees move to `rejected/` with reason

## API Endpoints

### Symptom Search (returns AI generation info)
```http
POST /symptom-search/search
Content-Type: application/json

{
  "symptoms": ["headache", "fever", "neck stiffness"]
}
```

Response (if no matches):
```json
{
  "query_symptoms": ["headache", "fever", "neck stiffness"],
  "total_results": 0,
  "results": [],
  "ai_generation": {
    "generation_triggered": true,
    "status": "pending",
    "message": "AI is generating a diagnostic tree..."
  }
}
```

### Generate Tree
```http
POST /symptom-search/generate-tree
Content-Type: application/json

{
  "symptoms": ["headache", "fever", "neck stiffness"],
  "age": 35,
  "sex": "F"
}
```

### Admin - List Pending Trees
```http
GET /admin/trees/pending
Authorization: Bearer YOUR_ADMIN_TOKEN
```

### Admin - Get Tree Details
```http
GET /admin/trees/pending/ai_generated_123
Authorization: Bearer YOUR_ADMIN_TOKEN
```

### Admin - Review Tree
```http
POST /admin/trees/review
Authorization: Bearer YOUR_ADMIN_TOKEN
Content-Type: application/json

{
  "tree_id": "ai_generated_123",
  "action": "approve",  // or "reject"
  "reviewer_notes": "Accurate diagnosis, comprehensive workup",
  "rejection_reason": null  // required for rejection
}
```

## Security Considerations

1. **Admin Token**: Keep secret, rotate regularly
2. **API Keys**: Protect Claude/OpenAI keys
3. **Medical Review**: Always require professional review before approval
4. **Rate Limiting**: Monitor API usage to control costs
5. **Audit Trail**: All generations are logged

## Cost Management

- Claude Sonnet 3.5: ~$0.30 per tree (4k tokens)
- GPT-4 Turbo: ~$0.40 per tree (4k tokens)
- Limit generations with `MIN_SYMPTOMS_FOR_AI`
- Cache common symptom combinations
- Monitor usage in Anthropic/OpenAI dashboards

## Frontend Integration

### Admin Review Page
Access at: `https://your-domain.com/admin-review`

Features:
- List pending trees
- View full tree details
- Add review notes
- Approve or reject
- View statistics

### Symptom Search Integration
The symptom search page automatically:
- Detects low/no matches
- Shows AI generation message
- Provides button to trigger generation

## Troubleshooting

### AI Generation Not Working
1. Check `ENABLE_AI_GENERATION=true`
2. Verify API key is set correctly
3. Check backend logs for errors
4. Ensure OpenAI/Anthropic packages installed

### Admin Page 403 Error
1. Check admin token is set in env
2. Verify token matches in frontend localStorage
3. Check backend logs for auth errors

### Trees Not Appearing in Search
1. Verify tree was approved (not just generated)
2. Check tree is in `approved/` directory
3. Restart backend to reload trees

## File Structure

```
backend/
├── data/
│   └── generated_trees/
│       ├── pending/       # Awaiting review
│       ├── approved/      # Ready for use
│       └── rejected/      # Rejected with reason
└── services/
    ├── ai_tree_generator.py    # Core generation logic
    ├── symptom_search.py       # Gap detection
    └── admin_router.py         # Review API

frontend/
└── pages/
    └── admin-review.js         # Review interface
```

## Best Practices

1. **Start Small**: Test with a few symptom combinations first
2. **Review Quality**: Have medical professional review first 10-20 trees
3. **Monitor Costs**: Set up billing alerts in OpenAI/Anthropic
4. **Regular Audits**: Review approved trees periodically
5. **User Feedback**: Allow users to report issues with AI trees
6. **Version Control**: Track which trees are AI-generated vs human-created

## Disabling AI Generation

To disable:
```env
ENABLE_AI_GENERATION=false
```

Existing approved trees remain searchable. Pending trees can still be reviewed but no new trees will be generated.
