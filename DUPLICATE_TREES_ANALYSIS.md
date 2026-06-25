# Duplicate Trees Analysis

## Problem
Backend has 400 tree files, but only 380 rules display on the rules page due to over-aggressive deduplication.

## Root Cause
The `normalize_name()` function in reference_router.py strips out important clinical distinctions:
- Removes "acute" and "chronic" prefixes → merges distinct conditions
- Removes content in parentheses → merges pediatric/adult versions

## Duplicate Groups Found (28 groups, 31 extra files)

### TRUE DUPLICATES (Should be removed - 11 files)
These are identical conditions with different file prefixes:

1. **Anaphylaxis** (prefix variants)
   - Keep: `EMERGENCY-ANAPHYLAXIS.yml`
   - DELETE: `EM-ANAPHYLAXIS.yml`

2. **Constipation (Pediatric)** (PED vs PEDS)
   - Keep: `PEDS-CONSTIPATION.yml`
   - DELETE: `PED-CONSTIPATION.yml`

3. **Developmental Delay** (PED vs PEDS)
   - Keep: `PEDS-DEVELOPMENTAL-DELAY.yml`
   - DELETE: `PED-DEVELOPMENTAL-DELAY.yml`

4. **Fever** (PED vs PEDS)
   - Keep: `PEDS-FEVER.yml`
   - DELETE: `PED-FEVER-UNSPECIFIED.yml`

5. **Gastroenteritis (Pediatric)** (PED vs PEDS)
   - Keep: `PEDS-GASTROENTERITIS.yml`
   - DELETE: `PED-GASTROENTERITIS.yml`

6. **Kidney Disease (CKD)** (same condition, different abbreviation)
   - Keep: `NEPHRO-CHRONIC-KIDNEY-DISEASE.yml`
   - DELETE: `NEPHRO-CKD.yml`

7. **Squamous Cell Carcinoma** (SCC abbreviation)
   - Keep: `DERM-SQUAMOUS-CELL-CARCINOMA.yml`
   - DELETE: `DERM-SCC.yml`

8. **Thyroid Storm** (prefix variants)
   - Keep: `ENDO-THYROID_STORM.yml`
   - DELETE: `EM-THYROID-STORM.yml`

9. **Viral URI (Pediatric)** (PED vs PEDS)
   - Keep: `PEDS-VIRAL-URI.yml`
   - DELETE: `PED-VIRAL-URI.yml`

10. **Interstitial Cystitis** (URO vs UROLOGY)
    - Keep: `UROLOGY-INTERSTITIAL-CYSTITIS.yml`
    - DELETE: `URO-INTERSTITIAL-CYSTITIS.yml`

11. **Benign Prostatic Hyperplasia** (URO vs UROLOGY)
    - Keep: `UROLOGY-BENIGN-PROSTATIC-HYPERPLASIA.yml`
    - DELETE: `URO-PROSTATE-HYPERPLASIA-BENIGN.yml`

### CLINICALLY DISTINCT (Should be kept - fix normalization logic)
These represent different conditions that should NOT be merged:

1. **Bronchitis** - Acute vs Chronic (different pathophysiology)
   - `PULM-BRONCHITIS-ACUTE.yml` - Acute viral/bacterial infection
   - `PULM-CHRONIC-BRONCHITIS.yml` - COPD component

2. **Conjunctivitis** - Adult vs Pediatric (different approach)
   - `OPHTHO-CONJUNCTIVITIS.yml` - General ophthalmology
   - `PED-CONJUNCTIVITIS.yml` - Pediatric-specific evaluation

3. **Cough** - Acute vs Chronic (different workup)
   - `PULM-COUGH.yml` - General cough evaluation
   - `PULM-CHRONIC-COUGH.yml` - Chronic cough (>8 weeks)

4. **DVT** - May have specialty-specific approaches
   - `CARDIO-DVT.yml` - Cardiovascular approach
   - `HEME-DVT.yml` - Hematology/thrombosis approach

5. **Dehydration** - Adult vs Pediatric (different fluid management)
   - `GENERAL-DEHYDRATION-ADULT.yml` - Adult dehydration
   - `PED-DEHYDRATION.yml` - Pediatric dehydration

6. **Diarrhea** - Acute vs Chronic (different differential)
   - `GI-DIARRHEA.yml` - Acute diarrhea
   - `GI-CHRONIC-DIARRHEA.yml` - Chronic diarrhea (>4 weeks)

7. **Gastroenteritis** - Multiple distinct entities
   - `GI-GASTROENTERITIS-ACUTE.yml` - Acute viral/general
   - `ID-GASTROENTERITIS-BACTERIAL.yml` - Bacterial gastroenteritis (ID workup)

8. **Hepatitis** - Acute vs Chronic
   - `GI-HEPATITIS.yml` - General hepatitis
   - `GI-HEPATITIS-ACUTE.yml` - Acute hepatitis

9. **Impetigo** - Adult vs Pediatric
   - `DERM-IMPETIGO-ADULT.yml` - Adult impetigo
   - `PED-IMPETIGO.yml` - Pediatric impetigo

10. **Lower GI Bleeding**
    - `GASTRO-LOWER-GI-BLEEDING.yml`
    - `GI-LOWER-GI-BLEED.yml` (likely duplicate - review content)

11. **Lung Cancer**
    - `ONCO-LUNG-CANCER.yml` - Oncology approach
    - `PULM-LUNG-CA.yml` - Pulmonology approach

12. **Otitis Media** - Pediatric variants
    - `ENT-OTITIS-MEDIA.yml` - General ENT
    - `PED-OTITIS-MEDIA.yml` - Pediatric
    - `PEDS-ACUTE-OTITIS-MEDIA.yml` - Acute OM (likely duplicate with PED version)

13. **Pancreatitis** - Acute vs Chronic
    - `GASTRO-ACUTE-PANCREATITIS.yml` - Acute pancreatitis
    - `GI-PANCREATITIS.yml` - General pancreatitis

14. **Prostatitis** - Acute vs Chronic
    - `URO-PROSTATITIS-ACUTE.yml` - Acute bacterial prostatitis
    - `URO-PROSTATITIS.yml` - General prostatitis

15. **Sinusitis** - Acute vs Chronic
    - `ENT-SINUSITIS.yml` - Acute sinusitis
    - `ENT-CHRONIC-SINUSITIS.yml` - Chronic sinusitis

16. **Strep Throat** - Adult vs Pediatric
    - `ENT-PHARYNGITIS-STREP.yml` - General ENT
    - `PED-STREP-THROAT.yml` - Pediatric strep

17. **Urticaria** - Acute vs Chronic
    - `ALLERGY-URTICARIA.yml` - Acute allergic urticaria
    - `DERM-URTICARIA-CHRONIC.yml` - Chronic urticaria (>6 weeks)

18. **Vertigo** - ENT vs Neuro
    - `ENT-VERTIGO.yml` - ENT/vestibular approach
    - `NEURO-VERTIGO.yml` - Neurologic approach

## Recommended Action

### Step 1: Delete True Duplicates (11 files)
This will bring us from 400 to 389 trees.

### Step 2: Review Borderline Cases (9 files potentially)
- GASTRO-LOWER-GI-BLEEDING vs GI-LOWER-GI-BLEED (check if different)
- PEDS-ACUTE-OTITIS-MEDIA vs PED-OTITIS-MEDIA (check if different)
- DVT variants (check if specialty approaches differ)
- Lung Cancer variants (check if approaches differ)
- Hepatitis variants (check if one covers both acute/chronic)
- Pancreatitis variants (check if general covers acute)
- Lower GI bleeding variants (likely same - delete one)
- Prostatitis general (might cover acute already)

This could reduce to approximately 380-385 trees, matching what the rules page currently shows.

## Alternative: Fix Normalization Logic
Instead of deleting clinically distinct files, improve the `normalize_name()` function to:
1. Keep "acute" vs "chronic" distinction
2. Keep "pediatric" vs "adult" distinction  
3. Keep specialty-specific approaches

This would allow all 389 trees (after removing true duplicates) to display.
