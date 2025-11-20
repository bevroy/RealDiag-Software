# Phase 3: Additional Medical Specialties - Implementation Plan

## Current Status

**Existing Specialties** (20 diagnostic trees):
- ✅ Cardiology (3): Chest pain, Palpitations, Syncope
- ✅ Dermatology (1): Rash
- ✅ Endocrinology (2): Diabetes, Thyroid disorders
- ✅ Gastroenterology (2): Abdominal pain, GI bleeding
- ✅ Hematology (1): Bleeding disorders
- ✅ Infectious Disease (1): Fever
- ✅ Neurology (6): Confusion, Headache, Seizure, Vertigo, Weakness, Altered mental status
- ✅ Orthopedics (2): Back pain, Joint pain
- ✅ Pulmonology (1): Dyspnea
- ✅ Trauma (1): Head injury

## New Specialties to Add (Priority Order)

### High Priority (Common Conditions)

1. **Psychiatry** (3-4 trees)
   - PSYCH-DEPRESSION.yml
   - PSYCH-ANXIETY.yml
   - PSYCH-PSYCHOSIS.yml
   - PSYCH-SUICIDAL-IDEATION.yml

2. **Ophthalmology** (2-3 trees)
   - OPHTHO-RED-EYE.yml
   - OPHTHO-VISION-LOSS.yml
   - OPHTHO-EYE-PAIN.yml

3. **ENT** (2-3 trees)
   - ENT-SORE-THROAT.yml
   - ENT-HEARING-LOSS.yml
   - ENT-VERTIGO.yml (enhance existing)

4. **Urology** (2-3 trees)
   - URO-HEMATURIA.yml
   - URO-DYSURIA.yml
   - URO-KIDNEY-STONES.yml

5. **OB/GYN** (3-4 trees)
   - OBGYN-ABD-PAIN.yml
   - OBGYN-VAGINAL-BLEEDING.yml
   - OBGYN-PREGNANCY-COMPLICATIONS.yml
   - OBGYN-PELVIC-PAIN.yml

### Medium Priority (Expanding Coverage)

6. **Rheumatology** (2 trees)
   - RHEUM-ARTHRITIS.yml
   - RHEUM-AUTOIMMUNE.yml

7. **Nephrology** (2 trees)
   - NEPHRO-AKI.yml
   - NEPHRO-CKD.yml

8. **Vascular Surgery** (2 trees)
   - VASC-DVT.yml
   - VASC-PERIPHERAL-ARTERY.yml

9. **Toxicology** (2 trees)
   - TOX-OVERDOSE.yml
   - TOX-POISONING.yml

10. **Allergy/Immunology** (2 trees)
    - ALLERGY-ANAPHYLAXIS.yml
    - ALLERGY-REACTIONS.yml

## Implementation Strategy

### Phase 3A: Psychiatry (Week 1)

**Priority**: Highest - Very common in primary care and emergency settings

**Files to Create**:
1. `backend/trees/PSYCH-DEPRESSION.yml`
2. `backend/trees/PSYCH-ANXIETY.yml`
3. `backend/trees/PSYCH-PSYCHOSIS.yml`
4. `backend/trees/PSYCH-SUICIDAL-IDEATION.yml`

**Key Features**:
- PHQ-9 integration for depression
- GAD-7 for anxiety
- Safety risk assessment
- Crisis intervention protocols
- Referral recommendations

**Timeline**: 2-3 days

### Phase 3B: Ophthalmology (Week 1-2)

**Priority**: High - Visual symptoms are common chief complaints

**Files to Create**:
1. `backend/trees/OPHTHO-RED-EYE.yml`
2. `backend/trees/OPHTHO-VISION-LOSS.yml`
3. `backend/trees/OPHTHO-EYE-PAIN.yml`

**Key Features**:
- Visual acuity criteria
- Intraocular pressure
- Ophthalmoscopy findings
- Urgent vs emergent triage

**Timeline**: 2 days

### Phase 3C: ENT (Week 2)

**Priority**: High - Very common in primary care

**Files to Create**:
1. `backend/trees/ENT-SORE-THROAT.yml`
2. `backend/trees/ENT-HEARING-LOSS.yml`
3. `backend/trees/ENT-TINNITUS.yml`

**Key Features**:
- Centor criteria for pharyngitis
- Audiometry integration
- Weber/Rinne test interpretation

**Timeline**: 2 days

### Phase 3D: Urology (Week 2-3)

**Priority**: High - Common in ER and primary care

**Files to Create**:
1. `backend/trees/URO-HEMATURIA.yml`
2. `backend/trees/URO-DYSURIA.yml`
3. `backend/trees/URO-KIDNEY-STONES.yml`

**Key Features**:
- Urinalysis criteria
- CT stone protocol
- UTI diagnostics

**Timeline**: 2 days

### Phase 3E: OB/GYN (Week 3)

**Priority**: High - 50% of population

**Files to Create**:
1. `backend/trees/OBGYN-ABD-PAIN.yml`
2. `backend/trees/OBGYN-VAGINAL-BLEEDING.yml`
3. `backend/trees/OBGYN-PREGNANCY-COMPLICATIONS.yml`

**Key Features**:
- Pregnancy test integration
- Ectopic pregnancy screening
- Obstetric emergency protocols

**Timeline**: 2-3 days

## Template for New Diagnostic Tree

```yaml
family: "Psychiatry"  # or Ophthalmology, ENT, Urology, OBGYN
version: "1.0"
last_updated: "2025-11-20"
source: "DSM-5, UpToDate, Clinical Guidelines"

metadata:
  specialty: "Psychiatry"
  chief_complaint: "Depression"
  keywords:
    - "low mood"
    - "anhedonia"
    - "suicidal thoughts"
    - "PHQ-9"
  
  icd10_codes:
    - "F32.9"  # Major depressive disorder, single episode
    - "F33.1"  # Major depressive disorder, recurrent
  
  urgency_level: "urgent"  # routine, urgent, emergent
  
  references:
    - "DSM-5 Diagnostic Criteria"
    - "US Preventive Services Task Force Depression Screening"
    - "APA Practice Guidelines for Depression"

rules:
  - rule_id: "PSYCH-DEPRESSION-001"
    diagnosis_label: "Major Depressive Disorder"
    
    criteria:
      required_all:
        - "Depressed mood most of the day, nearly every day"
        - "Duration: Symptoms present for at least 2 weeks"
        - "Functional impairment present"
      
      required_any_5:
        - "Depressed mood"
        - "Anhedonia (loss of interest/pleasure)"
        - "Significant weight change (>5% in 1 month)"
        - "Insomnia or hypersomnia"
        - "Psychomotor agitation or retardation"
        - "Fatigue or loss of energy"
        - "Feelings of worthlessness or guilt"
        - "Diminished concentration"
        - "Recurrent thoughts of death or suicidal ideation"
      
      exclusions:
        - "Manic or hypomanic episode (lifetime)"
        - "Psychotic disorder"
        - "Substance-induced mood disorder"
    
    clinical_pearls:
      - "Screen with PHQ-9 (score ≥10 suggests major depression)"
      - "Always assess suicide risk (PHQ-9 question 9)"
      - "Screen for bipolar disorder before starting antidepressants"
      - "Consider medical causes: hypothyroidism, vitamin deficiencies"
    
    red_flags:
      - "Active suicidal ideation with plan"
      - "Psychotic symptoms"
      - "Severe functional impairment"
      - "Catatonia"
    
    workup:
      labs:
        - "TSH (rule out hypothyroidism)"
        - "CBC (rule out anemia)"
        - "Vitamin B12, folate"
        - "Consider: Toxicology screen"
      
      assessments:
        - "PHQ-9 depression screening"
        - "Columbia Suicide Severity Rating Scale (C-SSRS)"
        - "Screen for anxiety (GAD-7)"
        - "Screen for bipolar (MDQ)"
    
    management:
      initial:
        - "Safety assessment and planning"
        - "Psychoeducation about depression"
        - "Consider starting SSRI (sertraline, escitalopram)"
        - "Refer to psychotherapy (CBT, IPT)"
      
      follow_up:
        - "Follow up in 1-2 weeks after starting medication"
        - "Monitor for suicidal ideation"
        - "Reassess PHQ-9 at each visit"
        - "Consider psychiatry referral if no improvement"
    
    disposition:
      - "Outpatient management if low suicide risk"
      - "Emergency psychiatric evaluation if high risk"
      - "Voluntary or involuntary hospitalization if imminent danger"
```

## Quality Standards

Each new diagnostic tree must include:

1. **Evidence-Based Criteria**
   - DSM-5, ICD-10, or guideline-based
   - Clear inclusion/exclusion criteria
   - Sensitivity/specificity data when available

2. **Clinical Pearls**
   - 3-5 practical tips
   - Common pitfalls to avoid
   - Red flags requiring immediate action

3. **Workup Recommendations**
   - First-line labs/imaging
   - Validated assessment tools
   - Specialist referral criteria

4. **Management Protocols**
   - Initial treatment recommendations
   - Follow-up intervals
   - Disposition guidelines

5. **Safety Considerations**
   - Red flags
   - Emergency criteria
   - When to escalate care

## Testing Requirements

For each new specialty:

1. **Unit Tests**
   - Test rule matching
   - Test exclusion criteria
   - Validate scoring algorithms

2. **Integration Tests**
   - Search by specialty
   - Filter by family
   - Symptom matching

3. **Clinical Validation**
   - Review by subject matter expert
   - Compare against clinical guidelines
   - Verify ICD-10/SNOMED codes

## Timeline

| Week | Specialty | Trees | Status |
|------|-----------|-------|--------|
| 1 | Psychiatry | 4 | 🔄 Next |
| 1-2 | Ophthalmology | 3 | ⏳ Pending |
| 2 | ENT | 3 | ⏳ Pending |
| 2-3 | Urology | 3 | ⏳ Pending |
| 3 | OB/GYN | 3 | ⏳ Pending |
| 3-4 | Rheumatology | 2 | ⏳ Pending |
| 4 | Nephrology | 2 | ⏳ Pending |
| 4 | Remaining | 5 | ⏳ Pending |

**Total**: ~25 new diagnostic trees over 4 weeks

## Success Metrics

- ✅ 45+ total diagnostic trees (from 20)
- ✅ 15+ medical specialties (from 10)
- ✅ All trees evidence-based with references
- ✅ All trees tested and validated
- ✅ Frontend updated with new families
- ✅ Documentation complete

## Resources Needed

1. **Clinical Guidelines**
   - DSM-5 for psychiatry
   - AAO guidelines for ophthalmology
   - AUA guidelines for urology
   - ACOG guidelines for OB/GYN

2. **Validation**
   - Subject matter expert review
   - Medical student/resident testing
   - Comparison with UpToDate/DynaMed

3. **Testing**
   - Unit test templates
   - Integration test suite
   - Clinical case validation

## Next Steps

1. **Start with Psychiatry** (Week 1)
   - Create 4 psychiatric diagnostic trees
   - High impact, common conditions
   - Clear diagnostic criteria (DSM-5)

2. **Update Frontend**
   - Add new specialties to dropdown
   - Update color coding
   - Add specialty descriptions

3. **Deploy and Test**
   - Push to production
   - Validate search functionality
   - Monitor usage analytics

**Ready to start?** Let's begin with Psychiatry - Depression, Anxiety, Psychosis, and Suicidal Ideation.
