# Decision Process Steps in Symptom Search (UPDATED)

## Complete Flow with Sex-Based Filtering ✅

When you query the symptom search software, here are the EXACT steps it now takes:

### Step 1: Input Validation & Parsing
**Location:** [symptom_search.py:53-105](backend/services/symptom_search.py#L53-L105)

```python
# Request received
{
  "symptoms": ["frequency", "urgency", "nocturia"],
  "age": 55,
  "sex": "F"
}
```

**Actions:**
- ✅ Validates symptoms (max 50, sanitized)
- ✅ Validates age (0-120)
- ✅ Validates sex ('M', 'F', 'male', 'female')
- ✅ Normalizes sex to lowercase internal format

---

### Step 2: Load Diagnostic Trees
**Location:** [symptom_search.py:134-300](backend/services/symptom_search.py#L134-L300)

**Actions:**
- Loads 676 diagnostic trees from `backend/trees/` directory
- Extracts metadata including:
  - `id`, `label`, `family`, `presentations`
  - **NEW:** `applies_to` field (male/female)
- Groups by medical specialty (54 families)

**Example tree loaded:**
```yaml
tree_id: UROLOGY-BENIGN-PROSTATIC-HYPERPLASIA
name: Benign Prostatic Hyperplasia (BPH)
family: Nephrology
applies_to: male  # ← NEW METADATA
presentations:
  - Obstructive symptoms: hesitancy, weak stream
  - Frequency, urgency, nocturia
```

---

### Step 3: Apply Sex-Based Filters ⭐ **THIS IS THE FIX**
**Location:** [symptom_search.py:628-683](backend/services/symptom_search.py#L628-L683)

**OLD CODE (BROKEN):**
```python
def apply_filters(rules, age, sex):
    return rules  # ❌ Returns everything!
```

**NEW CODE (FIXED):**
```python
def apply_filters(rules, age, sex):
    filtered = []
    
    # Normalize sex input
    if sex and sex.upper() in ['M', 'MALE']:
        normalized_sex = 'male'
    elif sex and sex.upper() in ['F', 'FEMALE']:
        normalized_sex = 'female'
    
    for rule in rules:
        # Check explicit metadata
        applies_to = rule.get('applies_to')
        if applies_to and normalized_sex:
            if applies_to != normalized_sex:
                continue  # ✅ Skip wrong-sex condition
        
        # Check keyword-based filtering
        if normalized_sex == 'female':
            # Filter out male-only keywords
            if any(keyword in rule_id for keyword in 
                   ['PROSTAT', 'TESTIC', 'ERECTILE', ...]):
                continue  # ✅ Skip male-only
        
        if normalized_sex == 'male':
            # Filter out OBGYN family
            if 'OBGYN' in family:
                continue  # ✅ Skip female-only
            # Filter out female-only keywords
            if any(keyword in rule_id for keyword in 
                   ['PREGNAN', 'OVARIAN', 'MENSTRUAL', ...]):
                continue  # ✅ Skip female-only
        
        filtered.append(rule)
    
    return filtered
```

**For Female Patient (sex='F'):**
- ❌ Filters out: BPH, Prostate Cancer, Erectile Dysfunction, Testicular conditions
- ✅ Keeps: UTI, Overactive Bladder, Interstitial Cystitis, Bladder Cancer

**For Male Patient (sex='M'):**
- ❌ Filters out: Pregnancy, Ovarian conditions, Menstrual disorders, all OBGYN conditions
- ✅ Keeps: UTI, Kidney stones, BPH, Prostate conditions

---

### Step 4: Symptom Matching & Scoring
**Location:** [symptom_search.py:785-830](backend/services/symptom_search.py#L785-L830)

**Actions:**
- Normalizes input symptoms (lowercase, remove punctuation)
- Compares against `presentations` in each **filtered** tree
- Calculates match score:
  - +1.0 for each exact symptom match
  - +0.5 for partial matches
  - Adjusts by clinical sensitivity if available

**Example for Female Patient:**
```
Input: ["frequency", "urgency", "nocturia"]

Overactive Bladder:
  Presentations: ["Urgency", "Frequency", "Nocturia"]
  Matches: 3/3 exact
  Score: 2.86 (includes sensitivity modifier)

BPH (FILTERED OUT ✅):
  Would have matched 3/3
  But never reaches scoring because apply_filters() removed it!
```

---

### Step 5: Sort & Rank Results
**Location:** [symptom_search.py:833-836](backend/services/symptom_search.py#L833-L836)

**Actions:**
- Sorts all matches by score (descending)
- Returns top 20 results

---

### Step 6: AI Enhancement (Optional)
**Location:** [symptom_search.py:839-890](backend/services/symptom_search.py#L839-L890)

**Triggered when:**
- Less than 5 tree results, OR
- Best score < 3.0

**Actions:**
- Queries Claude/GPT with symptoms + age + **sex**
- AI respects sex context in prompt
- Adds non-duplicate AI suggestions to results

**Example prompt to AI:**
```
Given these symptoms, list the top 10 most likely diagnoses.

Patient presenting with: frequency, urgency, nocturia
Age: 55 years
Sex: F  # ← AI uses this context

Return only JSON array...
```

---

### Step 7: Return Results
**Location:** [symptom_search.py:912-931](backend/services/symptom_search.py#L912-L931)

**Returns:**
```json
{
  "results": [
    {
      "rule_id": "URO-OVERACTIVE-BLADDER",
      "label": "Overactive Bladder",
      "family": "urology",
      "match_score": 2.86,
      "matched_presentations": ["Urgency", "Frequency", "Nocturia"],
      "icd10": ["N32.81"],
      "clinical_pearls": ["Most common in women over 40"],
      "tests": ["Urinalysis", "Post-void residual"],
      "management": ["Behavioral therapy", "Anticholinergics"]
    }
    // BPH NOT in results ✅
  ],
  "total": 34,
  "search_time": 0.15
}
```

---

## Before vs After Comparison

### BEFORE (Broken) 🔴
```
Female patient with urinary symptoms
  ↓
Load all 676 trees
  ↓
apply_filters() - DOES NOTHING ❌
  ↓
Match symptoms against ALL trees (including BPH)
  ↓
BPH scores high (3+ symptoms match)
  ↓
RESULT: BPH suggested for female patient ❌
```

### AFTER (Fixed) ✅
```
Female patient with urinary symptoms
  ↓
Load all 676 trees (with applies_to metadata)
  ↓
apply_filters() - FILTERS BY SEX ✅
  - Checks applies_to='male' → REMOVE
  - Checks keywords (PROSTAT, TESTIC) → REMOVE
  - 676 trees → 660 trees (16 male-only removed)
  ↓
Match symptoms against FILTERED trees (BPH excluded)
  ↓
Only appropriate conditions scored
  ↓
RESULT: Overactive Bladder, UTI, etc. ✅
```

---

## Validation Test Results

### Test: Female Patient with Urinary Symptoms
```bash
python test_bph_female.py
```

**Input:**
- Sex: Female
- Age: 55
- Symptoms: frequency, urgency, nocturia, urinary hesitancy

**Results:**
```
✓ BPH was filtered out for female patient
✓ Top suggestions:
  1. Overactive Bladder (Score: 2.86)
  2. Interstitial Cystitis (Score: 2.5)
  3. Bladder Cancer (Score: 2.0)
  4. UTI (Score: 1.67)
```

---

## Technical Implementation Details

### Files Modified
1. **backend/services/symptom_search.py**
   - `apply_filters()` - Lines 628-683 (complete rewrite)
   - `load_all_families()` - Lines 276-279 (added applies_to extraction)

2. **41 Diagnostic Tree Files**
   - Added `applies_to: male` to 11 male-specific conditions
   - Added `applies_to: female` to 30 female-specific conditions

### Filtering Logic Priority
1. **Explicit metadata** (`applies_to` field) - Highest priority
2. **Keyword detection** (in rule_id, label) - Fallback
3. **Family-based** (entire OBGYN family) - Broadest filter

### Performance Impact
- ✅ Minimal overhead (simple list filtering)
- ✅ Reduces unnecessary scoring (fewer trees to check)
- ✅ Faster results for users (fewer irrelevant matches)

---

## Summary

The software now takes these steps for every symptom search:

1. ✅ Validate input (symptoms, age, sex)
2. ✅ Load diagnostic trees with metadata
3. ✅ **Filter by sex** (new step - the fix!)
4. ✅ Match symptoms to presentations
5. ✅ Calculate relevance scores
6. ✅ Sort and rank results
7. ✅ (Optional) AI enhancement
8. ✅ Return top matches

**Result:** Female patients no longer receive impossible diagnoses like BPH or prostate cancer, and male patients no longer receive pregnancy or ovarian-related diagnoses.

---

*Updated: January 8, 2026*
*Issue: Resolved ✅*
