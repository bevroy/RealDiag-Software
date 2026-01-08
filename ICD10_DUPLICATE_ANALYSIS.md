# ICD-10 Code Duplicate Analysis

## Summary
- **Total trees:** 389
- **Unique ICD-10 codes:** 462 (some trees have multiple codes)
- **Duplicate ICD-10 codes:** 29 groups

## Analysis of Duplicates by Category

### TRUE DUPLICATES - Should Remove (3 files)

1. **PED-OTITIS-MEDIA.yml** - H66.90
   - **KEEP:** PEDS-ACUTE-OTITIS-MEDIA.yml (newer, more specific)
   - **REMOVE:** PED-OTITIS-MEDIA.yml
   - Note: ENT-OTITIS-MEDIA.yml is general/adult version - KEEP

2. **PED-ADHD.yml** - F90.9
   - **KEEP:** PEDS-ADHD.yml
   - **REMOVE:** PED-ADHD.yml (duplicate of PEDS version)

3. **PED-STREP-THROAT.yml** - J02.0
   - **KEEP:** PEDS-STREP-THROAT.yml (newer naming)
   - **REMOVE:** PED-STREP-THROAT.yml
   - Note: ENT-PHARYNGITIS-STREP.yml is general/adult version - KEEP

### CLINICALLY DISTINCT - Keep Both (26 groups)

Most of these represent legitimately different clinical entities:

#### Pediatric vs Adult Variants (Keep Both)
- **Gastroenteritis** (A09): ID-bacterial vs PEDS-general - Different etiologies
- **Dehydration** (E86.0): Adult vs Pediatric - Different fluid management
- **Conjunctivitis** (H10.9): General vs Pediatric - Different approaches
- **Constipation** (K59.00): General vs Pediatric - Different causes/treatment
- **Impetigo** (L01.0): Adult vs Pediatric - Different considerations
- **Fever** (R50.9): ID workup vs Pediatric - Different differential
- **URI** (J06.9): Pediatric vs General - Keep both

#### Acute vs Chronic (Keep Both)
- **Diarrhea** (K59.1): Acute vs Chronic - Different workup
- **Asthma** (J45.901): Exacerbation vs Chronic management
- **Pharyngitis** (J02.9): Viral vs General - Keep both

#### Specialty-Specific Approaches (Keep Both)
- **DVT** (I82.40): Cardio vs Heme approach
- **Lung Cancer** (C34.90): Oncology vs Pulmonology
- **Septic Shock** (A41.9, R65.21): EM vs ID approach

#### Related but Distinct Conditions (Keep Both)
- **Hepatitis** (B15.9): General viral vs specific Hep A
- **Thyroid** (E07.9): Storm vs General disorders
- **Diabetes** (E11.9): Emergency vs Chronic management
- **Hyperlipidemia** (E78.5): Cardiology vs Endocrine metabolic
- **IBD** (K51.90): General IBD vs specific UC
- **Biliary** (K80.20): Colic vs Cholelithiasis (different presentations)
- **GI Bleeding** (K92.1): Upper vs Lower (DIFFERENT code - error in data?)
- **Abscess** (L02.91): Dermatology vs Surgical I&D
- **Osteoarthritis** (M17.9): Knee-specific vs General OA
- **Kidney Stones** (N20.0): Urology general vs Nephrology
- **Prostatitis** (N41.1): Chronic pelvic pain vs Prostatitis (overlapping)
- **Vaginosis** (N76.0): Bacterial specific vs General vaginitis

## Recommendation

**Remove 3 true duplicate files:**
1. PED-OTITIS-MEDIA.yml
2. PED-ADHD.yml  
3. PED-STREP-THROAT.yml

This will bring us from **389 to 386 trees**.

With improved normalization logic preserving clinical distinctions, the rules page should display **~382 rules** (accounting for the few remaining name-based duplicates that are also ICD-10 duplicates).

## Note on ICD-10 Code Sharing

It's NORMAL and APPROPRIATE for multiple trees to share ICD-10 codes when they represent:
- Different age groups (pediatric vs adult)
- Different specialties' approaches to the same condition
- Different phases/severity (acute vs chronic, stable vs exacerbation)
- Different etiologies of the same diagnosis (viral vs bacterial)

The ICD-10 system doesn't always distinguish these nuances, but clinical decision trees should.
