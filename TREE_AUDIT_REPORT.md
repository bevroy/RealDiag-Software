# Diagnostic Decision Tree Audit Report
*Date: December 16, 2025*

## Executive Summary

**Total Trees:** 364 diagnostic decision trees  
**Duplicates Found:** 11 confirmed duplicates (22 files)  
**Critical Gaps:** 12 missing common diagnoses  
**Coverage:** Comprehensive coverage across 20+ medical specialties

---

## 1. Coverage by Specialty

### Strong Coverage (30+ trees)
- **Cardiology:** 48 trees (Cardiology, Cardiovascular, Cardiac combined)
- **Unknown/General:** 38 trees (need categorization)
- **Dermatology:** 24 trees
- **Rheumatology:** 15 trees
- **Gastroenterology:** 17 trees

### Moderate Coverage (10-29 trees)
- **Neurology:** 23 trees (Neurology, Neurologic, Neurological combined)
- **Endocrinology:** 18 trees
- **Pulmonology:** 20 trees
- **Hematology:** 16 trees
- **Nephrology:** 12 trees
- **Infectious Disease:** 15 trees
- **Orthopedics:** 15 trees

### Limited Coverage (<10 trees)
- **Pediatrics:** 9 trees
- **Ophthalmology:** 6 trees
- **ENT:** 6 trees
- **Obstetrics/Gynecology:** 6 trees
- **Psychiatry:** 9 trees
- **Urology:** 9 trees
- **Trauma:** 5 trees
- **Emergency Medicine:** 6 trees
- **Dentistry:** 3 trees
- **Oncology:** 2 trees

---

## 2. Confirmed Duplicates (NEEDS ATTENTION)

### High Priority - Merge or Remove

1. **Acute Appendicitis** (2 files)
   - `SURG-ACUTE-APPENDICITIS.yml` (Surgery)
   - `SURG-APPENDICITIS.yml` (surgical)
   - **Recommendation:** Keep SURG-ACUTE-APPENDICITIS.yml, remove other

2. **Acute Coronary Syndrome** (2 files)
   - `CARD-ACUTE-CORONARY-SYNDROME.yml` (cardiovascular)
   - `CARDS-ACUTE-CORONARY-SYNDROME.yml` (Cardiology)
   - **Recommendation:** Merge into CARD-ACUTE-CORONARY-SYNDROME.yml

3. **Acute Diverticulitis** (2 files)
   - `GI-DIVERTICULITIS-ACUTE.yml` (Gastroenterology)
   - `GI-DIVERTICULITIS.yml` (Gastrointestinal)
   - **Recommendation:** Keep GI-DIVERTICULITIS-ACUTE.yml

4. **Acute Ischemic Stroke** (2 files)
   - `NEURO-ISCHEMIC-STROKE.yml` (Neurology)
   - `NEURO-STROKE-ISCHEMIC.yml` (Neurologic)
   - **Recommendation:** Keep NEURO-STROKE-ISCHEMIC.yml

5. **Allergic Rhinitis** (2 files)
   - `ENT-ALLERGIC-RHINITIS.yml` (ENT)
   - `ENT-RHINITIS-ALLERGIC.yml` (Otolaryngology)
   - **Recommendation:** Keep ENT-ALLERGIC-RHINITIS.yml

6. **Anaphylaxis** (2 files)
   - `ALLERGY-ANAPHYLAXIS.yml` (allergic)
   - `EMERGENCY-ANAPHYLAXIS.yml` (Emergency Medicine)
   - **Recommendation:** Keep EMERGENCY-ANAPHYLAXIS.yml (more appropriate category)

7. **Aortic Stenosis** (2 files)
   - `CARD-AORTIC-STENOSIS.yml` (cardiovascular)
   - `CARDS-AORTIC-STENOSIS.yml` (Cardiology)
   - **Recommendation:** Keep CARD-AORTIC-STENOSIS.yml

8. **Chronic Kidney Disease** (2 files)
   - `NEPHRO-CKD.yml` (Renal)
   - `NEPHRO-KIDNEY-DISEASE-CHRONIC.yml` (Nephrology)
   - **Recommendation:** Keep NEPHRO-KIDNEY-DISEASE-CHRONIC.yml (more descriptive)

9. **Generalized Anxiety Disorder** (3 files!) ⚠️
   - `PSYCH-ANXIETY-DISORDER.yml` (Psychiatric)
   - `PSYCH-ANXIETY-GENERALIZED.yml` (Psychiatry)
   - `PSYCH-GENERALIZED-ANXIETY-DISORDER.yml` (Psychiatry)
   - **Recommendation:** Keep PSYCH-GENERALIZED-ANXIETY-DISORDER.yml, remove others

10. **Pulmonary Hypertension** (2 files)
    - `CARDS-PULMONARY-HYPERTENSION.yml` (Cardiology)
    - `PULM-PULMONARY-HYPERTENSION.yml` (Pulmonology)
    - **Recommendation:** Keep PULM-PULMONARY-HYPERTENSION.yml (more appropriate specialty)

11. **Thrombocytopenia Evaluation** (2 files)
    - `HEM-THROMBOCYTOPENIA.yml` (Hematology)
    - `HEME-THROMBOCYTOPENIA.yml` (HEMATOLOGY)
    - **Recommendation:** Keep HEME-THROMBOCYTOPENIA.yml

**Total files to remove:** 13 duplicate files

---

## 3. Critical Gaps - Missing Common Diagnoses

### HIGH PRIORITY (Very Common in Primary Care/ER)

1. **Upper Respiratory Infection (URI/Common Cold)**
   - Most common outpatient diagnosis
   - Should include: viral URI, supportive care, when to consider antibiotics

2. **COVID-19**
   - Still highly prevalent
   - Should include: testing, treatment (Paxlovid, etc.), isolation guidelines

3. **Type 2 Diabetes Mellitus**
   - Have Type 1 DM but missing Type 2 (much more common)
   - Should include: diagnosis criteria, oral agents, insulin, complications

4. **Major Depressive Disorder (MDD)**
   - Have GAD but missing depression (equally common)
   - Should include: DSM-5 criteria, PHQ-9, SSRIs, therapy

5. **Urinary Tract Infection (UTI)**
   - Have "UTI Evaluation" but seems focused on workup, need complete tree
   - Should include: cystitis vs pyelonephritis, treatment, recurrent UTI

6. **GERD (Gastroesophageal Reflux Disease)**
   - Extremely common in primary care
   - Should include: PPI therapy, lifestyle, complications (Barrett's)

### MEDIUM PRIORITY (Common Presentations)

7. **Headache (General Evaluation)**
   - Have migraine and cluster, but missing general headache workup
   - Should include: tension headache, red flags, when to image

8. **Vertigo/Dizziness**
   - Common ER/primary care chief complaint
   - Should include: BPPV, vestibular neuritis, central vs peripheral

9. **Conjunctivitis (Pink Eye)**
   - Common pediatric and adult complaint
   - Should include: viral vs bacterial vs allergic, treatment

10. **Low Back Pain (Acute/Chronic)**
    - Have general "back pain" but needs comprehensive tree
    - Should include: mechanical vs radicular, red flags, management

11. **Neck Pain**
    - Common musculoskeletal complaint
    - Should include: cervical strain, radiculopathy, whiplash

12. **Constipation**
    - Common GI complaint, especially in elderly
    - Should include: causes, medications, treatments

---

## 4. Data Quality Issues

### Naming Inconsistencies
- Family field varies: "Cardiology" vs "CARDIOLOGY" vs "cardiovascular" vs "Cardiac"
- Need standardized family names across all trees
- 38 trees marked as "Unknown" family - need categorization

### File Naming Conventions
- Multiple prefixes: CARD-, CARDS-, NEURO-, etc.
- Inconsistent hyphenation: ACUTE-CORONARY vs CORONARY-ACUTE
- **Recommendation:** Standardize to PREFIX-CONDITION format

### Missing ICD-10 Codes
- Some trees may have incomplete or outdated ICD-10 codes
- **Recommendation:** Audit all ICD-10 codes for accuracy

---

## 5. Recommendations

### Immediate Actions (Priority 1)
1. **Remove 13 duplicate files** - prevents confusion and search issues
2. **Add 5 critical missing diagnoses:**
   - Upper Respiratory Infection
   - COVID-19
   - Type 2 Diabetes
   - Major Depressive Disorder
   - UTI (comprehensive)

### Short-term Actions (Priority 2)
3. **Standardize family/specialty names** across all 364 trees
4. **Categorize 38 "Unknown" family trees**
5. **Add 7 common diagnoses:**
   - GERD, Headache, Vertigo, Conjunctivitis, Low Back Pain, Neck Pain, Constipation

### Long-term Actions (Priority 3)
6. **Expand pediatric coverage** (only 9 trees currently)
7. **Add more psychiatry trees** (anxiety/depression are top 10 diagnoses)
8. **Add more OB/GYN trees** (only 6 trees currently)
9. **Standardize file naming convention**
10. **Audit all ICD-10 codes for accuracy**
11. **Add SNOMED codes to all trees** (currently many missing)
12. **Add homeopathic remedies** to additional common diagnoses

---

## 6. Summary Statistics

| Metric | Count |
|--------|-------|
| Total Trees | 364 |
| Unique Diagnoses | ~350 (after removing duplicates) |
| Confirmed Duplicates | 11 diagnoses (22 files) |
| Trees to Remove | 13 files |
| Specialties Covered | 20+ |
| Critical Gaps | 12 diagnoses |
| Trees with Homeopathy | 5 (after recent additions) |
| Unknown Family Trees | 38 |

---

## Conclusion

The diagnostic decision tree library is **comprehensive** with 364 trees covering most major conditions. However, there are **quality issues** that need attention:

✅ **Strengths:**
- Excellent cardiology, dermatology, and rheumatology coverage
- Good specialty distribution
- Detailed clinical information in most trees

⚠️ **Issues:**
- 13 duplicate files causing potential confusion
- 12 critical common diagnoses missing
- Inconsistent naming and categorization
- Limited pediatrics and psychiatry coverage

**Priority:** Address duplicates first, then add missing common diagnoses, then improve data quality.
