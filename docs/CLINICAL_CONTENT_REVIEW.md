# Clinical Content Review

Items that need clinician sign-off before they are treated as validated.
Each was set during engineering work (tree standardization, PRs
bevroy/RealDiag-Software#16 and #17) and is **not** clinically reviewed yet.

## 1. Decision tree urgency levels

- 260 of 416 trees have an urgency level that was proposed as a default:
  39 emergent, 56 urgent, 165 routine. These are trees whose original
  urgency was missing or was "medium"/"moderate".
- Each affected tree has a change_log entry: "Urgency set to <value>;
  proposed default, pending clinician confirmation."
- The full list is in `docs/tree_standardization_report.csv`
  (`urgency_pending_confirmation` = yes).

## 2. Merged treatment sections

Six trees had two separate `treatment` sections that were merged into one
list (all items kept, original order). Each has a change_log entry
"Merged duplicate treatment sections; needs clinical review.":

ID-BACTERIAL-VAGINOSIS, ID-GASTROENTERITIS-BACTERIAL, ID-GASTROENTERITIS-VIRAL,
ID-HEPATITIS-A, ID-STI-SCREENING, ID-TICK-BITE

## 3. Troponin severity thresholds (SMART chart evaluation)

Set in `backend/services/smart_diagnostic_engine.py`
(`TROPONIN_HIGH_MULTIPLE`, `TROPONIN_CRITICAL_MULTIPLE`). **No cited source.**

| Troponin vs. the lab's upper reference limit (URL) | Severity shown |
|---|---|
| at or below URL | low (ACS not suggested) |
| above URL, below 2.5× URL | moderate |
| 2.5× to below 10× URL | high |
| 10× URL or more | critical |
| no unit, unrecognized unit, or no URL from the lab | unknown (reason shown) |

The 2.5× and 10× multiples mirror the fixed cutoffs used before
(0.1 and 0.4 ng/mL against a 0.04 ng/mL limit). Please confirm them or
replace them with sourced values.

## 4. DKA thresholds (SMART chart evaluation)

Superseded by the 2024 consensus criteria; see "Phase 2 changes" below. Glucose
results are converted before comparison (mmol/L × 18.016 = mg/dL).

## 4a. Chart-evaluation criteria in tree files (SMART on FHIR)

Chart evaluation is driven by the `criteria` section of each tree (see the
format at the top of `backend/services/smart_diagnostic_engine.py`). All of
these trees are `status: draft` and show the "under clinical review" notice.
"Verified" below means checked against the primary guideline document;
everything else was confirmed only from secondary summaries and must be checked
against the primary text.

### Acute (shown even when data is missing)

These moved from code into tree files unchanged in Phase 1 (commit 83c4054),
where tests proved identical results (`backend/tests/test_criteria_equivalence.py`).
Sepsis and DKA were then updated in Phase 2 (below); ACS is unchanged.

| Tree | Criterion | Threshold | Source cited | Notes for reviewers |
|---|---|---|---|---|
| CARD-ACUTE-CORONARY-SYNDROME | Elevated troponin (I: 10839-9, T: 6598-7) | above the lab's upper reference limit; severity high >= 2.5x, critical >= 10x | 2025 ACC/AHA/ACEP/NAEMSP/SCAI ACS Guideline; Fourth Universal Definition of MI (2018) | Severity multiples have no cited source (section 3). |
| CARD-ACUTE-CORONARY-SYNDROME | Heart rate (8867-4), supporting only | > 100/min | same | Never suggests ACS on its own. |
| ID-SEPSIS | qSOFA >= 2 **or** SIRS >= 2 (see Phase 2) | either screen positive suggests evaluation | SSC 2021; Sepsis-3; SIRS (ACCP/SCCM 1992) | Updated in Phase 2. |
| ENDO-DKA | D + K + A per 2024 consensus (see Phase 2) | all three suggests evaluation | 2024 ADA/EASD/JBDS/AACE/DTS consensus | Updated in Phase 2. |

### Chronic (shown only when something is found)

A chronic condition is hidden when its tests were retrieved but not done. If
the lab or vital-sign query failed, a global warning says chronic conditions
could not be assessed. A condition already on the problem list is labelled
"known condition". A single abnormal result where repeats are required is shown
as "possible - needs confirmation".

| Tree | Criterion (LOINC) | Threshold | Lookback | Source cited | To verify |
|---|---|---|---|---|---|
| ENDO-DIABETES | HbA1c (4548-4, 17856-6, 59261-8) | >= 6.5% (48 mmol/mol) | 365 days | ADA Standards of Care in Diabetes-2026, Section 2 | Exact 2026 table wording |
| ENDO-DIABETES | Fasting plasma glucose (1558-6, 14771-0) | >= 126 mg/dL (7.0 mmol/L) | 365 days | same | same |
| ENDO-DIABETES | Confirmation | 2 abnormal results (same or different tests) | | same | Random glucose >= 200 with symptoms is not assessed (no symptom data) |
| ENDO-PREDIABETES | HbA1c | 5.7-6.4% (39-47 mmol/mol) | 365 days | same | |
| ENDO-PREDIABETES | Fasting plasma glucose | 100-125 mg/dL (5.6-6.9 mmol/L) | 365 days | same | |
| CARD-HYPERTENSION | Systolic (8480-6) / diastolic (8462-4) BP, averaged (see Phase 2) | average >= 130 / >= 80 mmHg over >= 2 occasions; stage 2 average >= 140 / 90 rated high | 365 days (3 most recent occasions) | 2025 AHA/ACC High Blood Pressure Guideline | Updated in Phase 2. |
| NEPHRO-CHRONIC-KIDNEY-DISEASE | eGFR (33914-3, 62238-1, 98979-8, 48642-3, 48643-1) | < 60 mL/min/1.73m2 on 2 results >= 90 days apart | 730 days | KDIGO 2024 CKD Guideline | Table 1 wording |
| NEPHRO-CHRONIC-KIDNEY-DISEASE | Urine albumin-creatinine ratio (9318-7, 14959-1) | >= 30 mg/g (3 mg/mmol) on 2 results >= 90 days apart | 730 days | same | same |
| HEME-ANEMIA | Hemoglobin (718-7) | < 13.0 g/dL (men); < 12.0 g/dL (non-pregnant women) | 90 days | WHO Guideline on haemoglobin cutoffs (2024) | Pregnancy status is not known; pregnancy cutoffs differ. Altitude/smoking adjustments not applied. |
| ENDO-HYPOTHYROIDISM | TSH (3016-3, 11580-8) | above the lab's reference range; free T4 (3024-7, 14920-3) below range = overt | 365 days | ATA/AACE Hypothyroidism in Adults (2012); ATA Treatment of Hypothyroidism (2014) | Confirm no newer general ATA/AACE diagnostic guideline supersedes these. |
| NEPHRO-HYPERKALEMIA | Potassium (2823-3, 6298-4) | >= 5.5 mild; >= 6.0 moderate (high); >= 6.5 severe (critical) | 30 days | UK Kidney Association hyperkalaemia guideline (2023) | 6.0 and 6.5 confirmed from secondary sources; **the 5.5 mild cut-off is not yet confirmed** against the final UKKA document. |
| ENDO-DYSLIPIDEMIA | LDL-C (13457-7, 18262-6, 2089-1) | >= 190 mg/dL (4.9 mmol/L) | 730 days | 2026 ACC/AHA/Multisociety Dyslipidemia Guideline | Class/level details |

LOINC codes and unit conversions (`backend/services/lab_units.py`) also need an
informatics check against the EHR's actual result codes.

## 4b. Phase 2 changes: old vs new thresholds

All three trees stay `status: draft`. Each change is recorded in the tree's
change_log.

### Sepsis (ID-SEPSIS): qSOFA no longer used alone

The 2021 Surviving Sepsis Campaign guideline recommends against using qSOFA as a
single screening tool compared with SIRS, NEWS or MEWS (strong recommendation)
because of its low sensitivity.

**Approach chosen: qSOFA OR SIRS.** NEWS2 and MEWS need supplemental-oxygen use
and level of consciousness (ACVPU), which are rarely available as structured
FHIR observations, so they cannot be scored reliably from the chart. SIRS uses
temperature, heart rate, respiratory rate and WBC, which are already fetched.
Screening positive on either score raises sensitivity (the guideline's concern);
qSOFA >= 2 still marks the higher-risk group.

| | Old (Phase 1) | New (Phase 2) | Source |
|---|---|---|---|
| Screen positive | qSOFA >= 2 only | qSOFA >= 2 **or** SIRS >= 2 | SSC 2021 |
| qSOFA items | RR >= 22/min, SBP <= 100 mmHg, GCS < 15 | unchanged | Sepsis-3 (Singer et al., JAMA 2016) |
| SIRS items | (WBC only, not scored) | Temperature > 38.0 or < 36.0 C (8310-5, F converted); heart rate > 90/min (8867-4); respiratory rate > 20/min (9279-1); WBC > 12 or < 4 K/uL (6690-2) | ACCP/SCCM Consensus (Bone et al., Chest 1992) |
| Lactate | not used | > 2 mmol/L (2524-7, 32693-4), supporting only | Sepsis-3; SSC 2021 suggests measuring lactate |
| Severity | qSOFA 1 = high, >= 2 = critical | SIRS >= 2 = high; qSOFA 1 = high; qSOFA >= 2 = critical | |

Reviewer notes: SIRS is sensitive but not specific (2001 International Sepsis
Definitions Conference); the PaCO2 < 32 mmHg and > 10% bands alternatives are not
assessed. Units for heart rate, respiratory rate and WBC are still not checked.

### DKA (ENDO-DKA): 2024 hyperglycemic crises consensus

Source: Hyperglycemic Crises in Adults With Diabetes: A Consensus Report
(ADA/EASD/JBDS/AACE/DTS; Umpierrez et al., Diabetes Care 2024;47:1257-1275;
also Diabetologia 2024).

| | Old (Phase 1) | New (Phase 2) |
|---|---|---|
| D (diabetes/glucose) | glucose > 250 mg/dL | glucose >= 200 mg/dL (11.1 mmol/L) **or** known diabetes on the problem list (covers euglycemic DKA) |
| K (ketones) | not required | beta-hydroxybutyrate >= 3.0 mmol/L (53060-9) |
| A (acidosis) | bicarbonate < 18 mEq/L | pH < 7.3 (2744-1, 2746-5, 11558-4) and/or bicarbonate < 18 mmol/L (2028-9, 1963-8) |
| Suggest evaluation when | glucose and bicarbonate both met | D **and** K **and** A all met |
| Severity | >= 2 criteria = high; glucose > 500 mg/dL = critical | D+K+A = high; pH < 7.0 or bicarbonate < 10 mmol/L = critical (severe range) |

Reviewer notes: urine ketones >= 2+ (an alternative K criterion) are not
assessed because they are reported as ordinal strip results. The consensus also
grades severity by beta-hydroxybutyrate; that is not applied. A published
comment (Diabetes Care 2025;48:e40) argues the pH/bicarbonate cut-offs miss some
cases and proposes adding anion gap >= 16 mEq/L; not applied. The pH < 7.0 /
bicarbonate < 10 severe bands are from secondary summaries and need primary
verification.

### Hypertension (CARD-HYPERTENSION): averaged readings

Source: 2025 AHA/ACC High Blood Pressure Guideline - classify on the average of
>= 2 careful readings obtained on >= 2 occasions.

| | Old (Phase 1) | New (Phase 2) |
|---|---|---|
| Method | count readings >= threshold on >= 2 separate days | average readings per day (one occasion), then average the 3 most recent occasions; >= 2 occasions required |
| Stage 1 | >= 2 readings >= 130 systolic or >= 80 diastolic | average >= 130 systolic or >= 80 diastolic |
| Stage 2 (rated high) | >= 2 readings >= 140 / 90 | average >= 140 systolic or >= 90 diastolic |
| One occasion only | possible | possible (needs a second occasion) |

Reviewer notes: the number of occasions averaged (3 most recent within 365
days) is an implementation choice, not from the guideline. Readings are not
distinguished by setting (office, home, ambulatory); the guideline recommends
out-of-office confirmation, which is now suggested in the output.

## 5. Reworded alert actions

23 alert actions in `frontend/utils/redFlagAlerts.js` and
`frontend/utils/timeSensitiveAlerts.js` that named a drug and dose, a
blood-product quantity, or cath lab activation now defer to the named
guideline or institutional protocol (for example "IM epinephrine is
first-line per anaphylaxis guidelines (WAO/AAAAI); dosing per protocol").
Please confirm the wording and the guideline named for each.

## 6. Today's complaint: term lists (Phase 2)

ACS, sepsis and DKA chart cards are also shown when today's complaint matches
one of these terms (`criteria.complaint_terms` in each tree). Matching is on
whole words or phrases; a term preceded by a negation cue in the same clause
("no", "denies", "without", "negative for", ...) does not match. Hyphens and
"the", "left", "right" are ignored, "radiates/radiation" match "radiating",
and "on exertion" matches "with exertion". All lists are pending clinical review.

| Tree | Complaint terms |
|---|---|
| CARD-ACUTE-CORONARY-SYNDROME | chest pain, chest pressure, chest tightness, chest discomfort, angina, shortness of breath with exertion, epigastric pain, pain radiating to the jaw / neck / back / arm (atypical presentations included on purpose) |
| ID-SEPSIS | fever, chills, rigors, suspected infection, confusion ("hypotension" removed: a finding, not a complaint) |
| ENDO-DKA | hyperglycemia, high blood sugar, vomiting with diabetes, polyuria, polydipsia, DKA, diabetic ketoacidosis |

Reviewer notes: "DKA" also matches a mention of past DKA ("history of DKA").
The card then says the complaint matched and shows what the results do or do
not meet. No new thresholds were added in Phase 2.

The complaint comes from the clinician's typed text, otherwise the EHR's
reason for the current visit (Encounter.reasonCode); the source is shown.

## 7. Red flags: content gap

Only 16 of 416 trees list any `red_flags`. The encounter assessment shows only
listed red flags and says "No red flags listed for this condition." otherwise;
it does not infer red flags from urgency or generate them. Adding reviewed red
flags to the remaining 400 trees is content work.

## 8. AI-generated content

Both AI settings follow one rule: off unless set to exactly "true", and
anything AI-generated is labelled "AI-generated; not clinically validated."

- `ENABLE_AI_GENERATION`: AI-suggested diagnoses added to typed symptom
  search, and new trees generated into `backend/data/generated_trees/pending`
  for admin review (not loaded into the library).
- `ENABLE_AI_ENRICHMENT`: AI fills empty sections of `/search` results.
- Chart-driven requests never use AI, whatever the settings: the encounter
  assessment, the SMART ambulatory differential, and symptom search with
  `emr_patient_id`. EHR data is never sent to an AI provider.

## 9. Can't-miss conditions in ranking

Any **emergent** tree whose presentations, chief complaint or complaint terms
match the complaint is always returned and labelled "Can't-miss condition",
whatever its score or the result cap. This applies to symptom search, the
SMART ambulatory differential and the encounter assessment. Which trees count
depends on each tree's `urgency`, which is itself pending review (section 1).

Regression list (`backend/tests/test_cant_miss_ranking.py`): each complaint
must return these trees.

| Complaint | Must return | Not in the library |
|---|---|---|
| chest pain | CARD-ACUTE-CORONARY-SYNDROME, CARD-PE, PULM-PNEUMOTHORAX, CARD-AORTIC-DISSECTION (new, section 11) | |
| headache | NEU-SAH, ID-BACTERIAL-MENINGITIS | |
| abdominal pain | SURG-ACUTE-APPENDICITIS, OBGYN-ECTOPIC-PREGNANCY (female patients), SURG-AAA-RUPTURED | |
| shortness of breath | CARD-PE, PULM-PNEUMOTHORAX | |

Ranking fixes made with this rule:

- 77 trees had 121 presentations written as `- Chest pain: substernal, ...`,
  which YAML reads as a key-value pair; ranking silently dropped them (this is
  why ACS was missing for "chest pain"). The same problem affected 3,050 list
  items in 219 trees (treatment 1,319, workup 1,061, trace 237, differentials
  143, clinical_pearls 124, presentations 121, referrals 45). Each line is now
  quoted so it loads as the text written; no wording changed. The validator
  rejects list items that are not plain text (a heading over a nested list
  and grouped differentials are still allowed).
- Each tree's `chief_complaint` is now matched like a presentation (this is
  where SURG-ACUTE-APPENDICITIS lists "abdominal pain").
- Searched together (pending review): shortness of breath / short of breath /
  SOB / difficulty breathing with dyspnea; stomach pain and belly pain with
  abdominal pain.

Negation: symptom search, the SMART ambulatory differential and the
encounter assessment all drop negated parts of the input before ranking
("no chest pain", "denies fever", "chest pain without radiation"); negated
terms cannot trigger a can't-miss label. The response lists them as
`negated_terms` (without the cue word), and the symptom-search and encounter
pages show "Not searched (negated): fever". Negation cues: no, not, denies/denied/denying, without,
negative for, free of, absence of, resolved, never; a cue stops at ".", ";",
"but", "however", "although", "except". Phrases that are themselves symptoms
are not treated as negations (pending review): no appetite, not eating, not
drinking, no energy, not sleeping, no urine, not urinating, no bowel
movement, no stool, no period, not feeling well, not moving, no feeling,
not able to.

## 10. Treatment wording: clinician actions reworded, patient advice labelled

Treatment sections are shown as "Treatment information from the decision tree
(reference, not an order)". Of 7,064 treatment lines:

- **56 clinician-directed action lines** (activate, administer, admit, transfuse,
  intubate, give, start or initiate a drug or procedure) in 45 trees are reworded
  into decision-support wording. Drugs, doses, thresholds and citations are unchanged.
- **97 patient self-care lines** in 73 trees are labelled "Patient advice:" and otherwise
  left as written.
- **243 cautions** ("Avoid ...", "Do not ...") in 165 trees are left as written.
- Other clinician lines (treat, continue, add, titrate, monitor, ...; about 450) are
  left as written.

Lines were grouped by their opening verb (also after a heading such as "Disposition:")
and the clinician and patient groups were then checked by hand. Each affected
tree has a change_log entry. Please confirm each rewording.

### Reworded clinician actions

| Tree | Old | New |
|---|---|---|
| CARD-ACUTE-CORONARY-SYNDROME | Activate cardiac catheterization lab immediately | Consider immediate cardiac catheterization lab activation per institutional STEMI protocol |
| CARD-HYPERTENSION | Initiate antihypertensive therapy: stage 1 hypertension (130-139/80-89) if ASCVD risk 10 percent or more or existing ASCVD/diabetes/CKD, stage 2 hypertension (140 or more/90 or more) regardless of risk | Consider antihypertensive therapy: stage 1 hypertension (130-139/80-89) if ASCVD risk 10 percent or more or existing ASCVD/diabetes/CKD, stage 2 hypertension (140 or more/90 or more) regardless of risk |
| CARD-HYPERTENSION | First-line agents (thiazide diuretics, ACE inhibitors, ARBs, CCBs): start monotherapy if BP less than 20/10 above goal, start 2 agents if 20/10 or more above goal | First-line agents (thiazide diuretics, ACE inhibitors, ARBs, CCBs): consider monotherapy if BP less than 20/10 above goal, 2 agents if 20/10 or more above goal |
| CARD-HYPERTENSION | Hypertensive emergency (BP 180 or more/120 or more with end-organ damage): admit ICU, IV antihypertensives (labetalol, nicardipine, clevidipine), reduce BP 10-20 percent first hour, then 5-15 percent over next 23 hours (avoid rapid reduction - cerebral hypoperfusion) | Hypertensive emergency (BP 180 or more/120 or more with end-organ damage): consider ICU admission, IV antihypertensives (labetalol, nicardipine, clevidipine), with BP reduction of 10-20 percent first hour, then 5-15 percent over next 23 hours (avoid rapid reduction - cerebral hypoperfusion) |
| CARD-MYOCARDIAL-INFARCTION-STEMI | ACE inhibitor or ARB: start within 24 hours if no contraindications (lisinopril 5 mg daily, ramipril, especially if anterior MI, LV dysfunction, heart failure, diabetes), reduce mortality and remodeling | ACE inhibitor or ARB: consider starting within 24 hours if no contraindications (lisinopril 5 mg daily, ramipril, especially if anterior MI, LV dysfunction, heart failure, diabetes), reduce mortality and remodeling |
| CARDS-HEART-FAILURE-SYSTOLIC | Start low, titrate slowly (may worsen HF initially) | Consider starting low and titrating slowly (may worsen HF initially) |
| DENT-DENTAL-ABSCESS | Severe/spreading: admit for IV antibiotics (ampicillin-sulbactam) | Severe/spreading: consider admission for IV antibiotics (ampicillin-sulbactam) |
| DERM-ACNE-VULGARIS | Start with lower concentrations, increase gradually to minimize irritation | Consider starting with lower concentrations, increasing gradually to minimize irritation |
| DERM-SUNBURN | Start within 24 hours of burn for maximum benefit | Consider starting within 24 hours of burn for maximum benefit |
| EMERGENCY-HEAT-STROKE | Do NOT wait for laboratory results - start cooling immediately based on clinical diagnosis | Do NOT wait for laboratory results - consider starting cooling immediately based on clinical diagnosis |
| EMERGENCY-HEAT-STROKE | Transfuse PRBCs if anemia and bleeding | Consider PRBC transfusion if anemia and bleeding |
| EMERGENCY-HEAT-STROKE | Transfuse platelets if under 10,000-20,000 or active bleeding | Consider platelet transfusion if under 10,000-20,000 or active bleeding |
| ENDO-DIABETES-HYPERGLYCEMIA | Start 0.1 units/kg for glucose >200 mg/dL | Consider starting 0.1 units/kg for glucose >200 mg/dL |
| ENDO-HYPOGLYCEMIA | If sulfonylurea-induced: Admit for D10W infusion + frequent glucose monitoring (can recur 12-24hrs) (ADA 2024) | If sulfonylurea-induced: consider admission for D10W infusion + frequent glucose monitoring (can recur 12-24hrs) (ADA 2024) |
| ENDO-HYPOTHYROIDISM | Start lower in elderly or cardiac disease: 25-50 mcg daily (ADA 2024) | Consider starting lower in elderly or cardiac disease: 25-50 mcg daily (ADA 2024) |
| ENDO-THYROID-STORM | Iodine (THIRD - give 1 hour AFTER thionamide): Lugol solution 8 drops Q6H OR SSKI 5 drops Q6H OR sodium iodide 0.5-1g IV Q12H (blocks thyroid hormone release) | Iodine (THIRD - 1 hour AFTER thionamide): Lugol solution 8 drops Q6H OR SSKI 5 drops Q6H OR sodium iodide 0.5-1g IV Q12H (blocks thyroid hormone release) |
| ENDO-THYROIDITIS | Start 1.6 mcg/kg/day, adjust to normalize TSH | Consider starting 1.6 mcg/kg/day, adjusting to normalize TSH |
| ENT-EPISTAXIS | Posterior packing: Foley catheter or posterior pack if anterior pack fails - admit for monitoring, O2, IV antibiotics (toxic shock risk) (AAO-HNS 2023) | Posterior packing: Foley catheter or posterior pack if anterior pack fails - consider admission for monitoring, O2, IV antibiotics (toxic shock risk) (AAO-HNS 2023) |
| ENT-VERTIGO | Central causes: admit, neurology consult, treat underlying etiology | Central causes: consider admission, neurology consult, treat underlying etiology |
| GER-DELIRIUM | Disposition: Admit if cannot identify/treat cause outpatient, high fall risk, unable to care for self at home (AGS 2023) | Disposition: consider admission if cannot identify/treat cause outpatient, high fall risk, unable to care for self at home (AGS 2023) |
| GER-FALLS | Disposition: Admit if fall with injury, syncope, unable to mobilize safely; outpatient if low-risk with close follow-up (AGS 2023) | Disposition: consider admission if fall with injury, syncope, unable to mobilize safely; outpatient if low-risk with close follow-up (AGS 2023) |
| GI-HEPATITIS-ACUTE | Acetaminophen overdose: N-acetylcysteine (NAC) - start immediately if suspected | Acetaminophen overdose: N-acetylcysteine (NAC) - consider starting immediately if suspected |
| HEME-SICKLE-CELL-DISEASE | Start 15-20 mg/kg daily, increase by 5 mg/kg every 8-12 weeks to maximum tolerated dose (typically 25-35 mg/kg, max 35 mg/kg) | Consider starting 15-20 mg/kg daily, increasing by 5 mg/kg every 8-12 weeks to maximum tolerated dose (typically 25-35 mg/kg, max 35 mg/kg) |
| ID-CELLULITIS | Severe/systemic: Admit for IV cefazolin 2g q8h or vancomycin 15-20mg/kg q12h if MRSA (IDSA 2024) | Severe/systemic: consider admission for IV cefazolin 2g q8h or vancomycin 15-20mg/kg q12h if MRSA (IDSA 2024) |
| ID-SEPSIS | Administer high-flow oxygen | Consider high-flow oxygen |
| ID-SEPSIS | Administer broad-spectrum antibiotics | Consider broad-spectrum antibiotics |
| ID-SEPSIS | Start IV fluid resuscitation | Consider IV fluid resuscitation |
| ID-SEPSIS | Administer within 1 hour of recognition | Recommended within 1 hour of recognition |
| NEPHRO-HYPOKALEMIA | Admit to monitored setting | Consider admission to a monitored setting |
| NEU-ALS | Riluzole 50mg BID: Start at diagnosis, may slow progression, monitor LFTs (AAN 2024) | Riluzole 50mg BID: consider starting at diagnosis, may slow progression, monitor LFTs (AAN 2024) |
| NEU-BELL-PALSY | Prednisone 60mg daily x5 days, taper over 5 days (10 days total) - START WITHIN 72 HOURS (AAN 2024) | Prednisone 60mg daily x5 days, taper over 5 days (10 days total) - consider starting within 72 hours (AAN 2024) |
| NEU-ENCEPHALITIS | Empiric acyclovir 10mg/kg IV q8h: Start immediately if encephalitis suspected (AAN 2024) | Empiric acyclovir 10mg/kg IV q8h: consider starting immediately if encephalitis suspected (AAN 2024) |
| NEU-PARKINSONS | Start when functional impairment: Carbidopa/levodopa 25/100mg TID, titrate by 25/100mg q3-7days (AAN 2024) | Consider starting when functional impairment: Carbidopa/levodopa 25/100mg TID, titrate by 25/100mg q3-7days (AAN 2024) |
| NEU-SAH | Nimodipine 60mg PO/NG q4h: Start immediately, continue 21 days to prevent vasospasm (AAN 2024) | Nimodipine 60mg PO/NG q4h: consider starting immediately, continue 21 days to prevent vasospasm (AAN 2024) |
| NEU-STATUS-EPILEPTICUS | 20-40 min: Refractory status - intubate, propofol/midazolam drip, ICU, EEG (AAN 2024) | 20-40 min: Refractory status - consider intubation, propofol/midazolam drip, ICU, EEG (AAN 2024) |
| NEU-TIA | Urgent evaluation: Admit high-risk patients (ABCD2 ≥4, crescendo TIAs, symptomatic carotid stenosis) | Urgent evaluation: consider admission for high-risk patients (ABCD2 ≥4, crescendo TIAs, symptomatic carotid stenosis) |
| NEURO-SEIZURE-DISORDER | Start single agent (monotherapy), titrate to seizure control or side effects, if inadequate try alternative monotherapy before polytherapy | Consider starting a single agent (monotherapy), titrating to seizure control or side effects; if inadequate, consider alternative monotherapy before polytherapy |
| OB-PRETERM-LABOR | Admit for observation if preterm labor suspected (less than 37 weeks with contractions and cervical change) | Consider admission for observation if preterm labor suspected (less than 37 weeks with contractions and cervical change) |
| OB-PRETERM-LABOR | Give if 24-34 weeks with threatened preterm delivery within 7 days | Consider if 24-34 weeks with threatened preterm delivery within 7 days |
| OBGYN-MENOPAUSE | Lowest effective dose shortest duration: start low dose, reassess annually, consider stopping after 3-5 years | Lowest effective dose shortest duration: consider starting low dose, reassess annually, consider stopping after 3-5 years |
| ORTHO-LOW-BACK-PAIN | Physical therapy: core strengthening, stretching, postural training - start after acute phase (1-2 weeks), critical for chronic pain | Physical therapy: core strengthening, stretching, postural training - consider starting after acute phase (1-2 weeks), critical for chronic pain |
| ORTHO-RIB-FRACTURE | Admit for - >3 rib fractures - Inadequate pain control - Oxygen requirement - Elderly age (>65 years) - COPD or other lung disease - Pneumothorax or hemothorax - Associated injuries | Consider admission for - >3 rib fractures - Inadequate pain control - Oxygen requirement - Elderly age (>65 years) - COPD or other lung disease - Pneumothorax or hemothorax - Associated injuries |
| PEDS-ADHD | Start low, go slow, titrate to optimal dose based on response and tolerability | Consider starting low, going slow, titrating to optimal dose based on response and tolerability |
| PEDS-AUTISM | Start as early as possible (age 2-3 years ideal) | Consider starting as early as possible (age 2-3 years ideal) |
| PEDS-FEBRILE-SEIZURE | Seizure lasting greater than 5 minutes or ongoing: administer antiseizure medication | Seizure lasting greater than 5 minutes or ongoing: consider antiseizure medication |
| PEDS-FEBRILE-SEIZURE | Admit if: | Consider admission if: |
| PEDS-FEVER | Neonates: admit all | Neonates: consider admission for all |
| PEDS-FEVER | Young infants: admit if high-risk, toxic-appearing, or positive labs | Young infants: consider admission if high-risk, toxic-appearing, or positive labs |
| PEDS-FEVER | Children greater than 3 months: admit if toxic-appearing, dehydrated, unable to tolerate oral, unreliable follow-up | Children greater than 3 months: consider admission if toxic-appearing, dehydrated, unable to tolerate oral, unreliable follow-up |
| PEDS-GASTROENTERITIS | Admit if moderate-severe dehydration, failed oral rehydration trial, age less than 3 months, toxic appearance | Consider admission if moderate-severe dehydration, failed oral rehydration trial, age less than 3 months, toxic appearance |
| PEDS-HAND-FOOT-MOUTH | Admit if severe dehydration, inability to tolerate oral fluids, or complications | Consider admission if severe dehydration, inability to tolerate oral fluids, or complications |
| PSYCH-EATING-ANOREXIA | Start refeeding at 30-40 kcal/kg/day, advance slowly to avoid refeeding syndrome | Consider starting refeeding at 30-40 kcal/kg/day, advancing slowly to avoid refeeding syndrome |
| PSYCH-PSYCHOSIS | First-episode psychosis: start low-dose atypical antipsychotic | First-episode psychosis: consider low-dose atypical antipsychotic |
| RHEUM-RHEUMATOID-ARTHRITIS | Early aggressive DMARD therapy prevents joint damage - start within 3 months of diagnosis | Early aggressive DMARD therapy prevents joint damage - consider starting within 3 months of diagnosis |
| TOX-ACETAMINOPHEN-OD | Disposition: Admit if NAC needed, psychiatry consult if intentional, liver transplant evaluation if fulminant hepatic failure (AAPCC 2023) | Disposition: consider admission if NAC needed, psychiatry consult if intentional, liver transplant evaluation if fulminant hepatic failure (AAPCC 2023) |
| URO-URINARY-RETENTION | Start alpha-blocker: Tamsulosin 0.4mg daily immediately after catheterization (improves voiding trial success) (AUA 2023) | Consider alpha-blocker: Tamsulosin 0.4mg daily immediately after catheterization (improves voiding trial success) (AUA 2023) |

### Labelled patient advice (text after the label unchanged)

| Tree | Line |
|---|---|
| ALLERGY-FOOD-ALLERGY | Call 911 after using epinephrine |
| CARD-PERIPHERAL-ARTERY-DISEASE | Walk until near-maximal pain, rest, repeat - improves symptoms and walking distance |
| CARDS-CV-RISK-ASSESSMENT | Increase fruits, vegetables, whole grains, fish |
| CARDS-STABLE-ANGINA | If not relieved after 3 doses: call 911 (possible ACS) |
| DENT-TMJ-DISORDER | Moist heat: apply to affected area 15-20 minutes several times daily (relaxes muscles) |
| DERM-CONTACT-DERMATITIS | Poison ivy treatment: wash exposed skin immediately with soap and water, launder clothes, wash under nails |
| DERM-IMPETIGO-ADULT | Remove crusts - soak with warm water or saline compresses, gently remove crusts to allow antibiotic penetration |
| DERM-IMPETIGO-ADULT | Wash with antibacterial soap (chlorhexidine, benzoyl peroxide) |
| DERM-IMPETIGO-ADULT | Keep nails short, avoid scratching |
| DERM-SCABIES | Environmental decontamination: wash all clothing, bedding, towels in hot water and dry on high heat, items that cannot be washed seal in plastic bag x72 hours (mites die off host in 2-3 days) |
| DERM-SUNBURN | Apply liberally several times daily |
| DERM-WARTS | Apply daily after soaking in warm water and paring dead tissue |
| DERM-WARTS | Apply 3-5 times per week at bedtime |
| DERM-WARTS | Keep hands and feet dry |
| EMERGENCY-HEAT-STROKE | Wear light, loose clothing |
| EMERGENCY-HEAT-STROKE | Take frequent breaks in shade or air conditioning |
| ENDO-DYSLIPIDEMIA | Limit alcohol (excess increases triglycerides) |
| ENDO-NEUROPATHY-DIABETIC | Educate on foot hygiene: wash and dry thoroughly, moisturize (not between toes), avoid barefoot walking |
| ENDO-OSTEOPENIA | Take on empty stomach with water, remain upright 30-60 min |
| ENDO-OVERWEIGHT | Increase vegetables, fruits, whole grains, lean protein |
| ENDO-OVERWEIGHT | Exercise |
| ENDO-OVERWEIGHT | Reduce sedentary time (stand, walk breaks) |
| ENT-LARYNGITIS | Hydration: Increase fluids (8+ glasses/day), humidified air (AAO-HNS 2023) |
| ENT-PHARYNGITIS-STREP | Return to school/work 24 hours after starting antibiotics (no longer contagious) (AAO-HNS 2023) |
| ENT-PHARYNGITIS-VIRAL | Increase oral fluids, rest, humidified air (AAO-HNS 2023) |
| ENT-TINNITUS | Limit caffeine, alcohol, nicotine |
| ENT-TINNITUS | Exercise |
| GEN-MED-OBESITY | Exercise 150-300 min/week moderate intensity plus strength training |
| ID-GASTROENTERITIS-VIRAL | Return to normal diet as tolerated; avoid prolonged dietary restrictions |
| ID-HEPATITIS-A | Rest as needed; no strict bed rest required |
| ID-MONONUCLEOSIS | Supportive care: Rest, fluids, NSAIDs or acetaminophen for fever/pain (IDSA 2024) |
| ID-TICK-BITE | Return precautions if fever, rash, flu-like illness develop within 30 days |
| NEU-CONCUSSION | Acute: Rest 24-48 hours (physical and cognitive), avoid screens, sleep hygiene (AAN 2024) |
| NEURO-HEADACHE | Non-pharmacologic: sleep hygiene, regular meals, hydration, exercise, stress reduction, biofeedback, trigger avoidance |
| OBGYN-AMENORRHEA | Reduce exercise intensity if excessive |
| OBGYN-ATROPHIC-VAGINITIS | Wear cotton underwear |
| OBGYN-VAGINITIS-UNSPECIFIED | Wear cotton underwear, avoid tight clothing |
| ORTHO-ANKLE-SPRAIN | Return to activities in 1-2 weeks |
| ORTHO-ANKLE-SPRAIN | Return to sports in 4-6 weeks |
| ORTHO-ANKLE-SPRAIN | Return to sports 3-6 months |
| ORTHO-KNEE-SPRAIN | Return to activities 2-4 weeks |
| ORTHO-KNEE-SPRAIN | Return to sports 6-8 weeks |
| ORTHO-LATERAL-EPICONDYLITIS | Wear during activities that provoke symptoms |
| ORTHO-LATERAL-EPICONDYLITIS | Ice: apply 15-20 minutes after aggravating activities |
| ORTHO-RIB-FRACTURE | Rest from strenuous activity for 4-6 weeks |
| ORTHO-RIB-FRACTURE | Return precautions for worsening shortness of breath, fever, productive cough (pneumonia) |
| ORTHO-TROCHANTERIC-BURSITIS | Ice application 15-20 minutes several times daily |
| ORTHO-WRIST-SPRAIN | Return to activities as tolerated (1-2 weeks) |
| ORTHO-WRIST-SPRAIN | Return to activities in 4-6 weeks |
| ORTHO-WRIST-SPRAIN | Return to full activities 3-6 months |
| PED-DEHYDRATION | Return precautions |
| PED-IMPETIGO | Hygiene measures - keep lesions covered, wash hands frequently, separate towels and linens, trim fingernails |
| PED-IMPETIGO | Return to school/daycare after 24 hours of antibiotics and lesions covered |
| PED-RASH | Keep nails short to prevent excoriation |
| PEDS-ADHD | Exercise and physical activity (beneficial for ADHD symptoms) |
| PEDS-ASTHMA | Reduce dust mite exposure (mattress/pillow covers, wash bedding hot water weekly) |
| PEDS-AUTISM | Sleep hygiene, behavioral interventions |
| PEDS-FEBRILE-SEIZURE | If seizure occurs at home: keep safe (side position, do not restrain), call 911 if prolonged greater than 5 minutes |
| PEDS-FEVER | Rest |
| PEDS-STREP-THROAT | Return to school/daycare after 24 hours of antibiotics and fever-free |
| PEDS-VIRAL-URI | Use before feedings and sleep |
| PEDS-VIRAL-URI | Keep child home from daycare/school when ill |
| PSYCH-ACUTE-STRESS-REACTION | Sleep hygiene and self-care |
| PSYCH-CANNABIS-USE-DISORDER | Sleep hygiene, exercise, healthy diet |
| PSYCH-DEPRESSION-ANXIETY-MIXED | Sleep hygiene |
| PSYCH-DEPRESSION-ANXIETY-MIXED | Limit caffeine and alcohol |
| PSYCH-GRIEF-REACTION | Stay connected to social support |
| PSYCH-PERSISTENT-DEPRESSIVE-DISORDER | Sleep hygiene |
| PSYCH-SLEEP-DISTURBANCE | Sleep hygiene education |
| PSYCH-SLEEP-DISTURBANCE | Sleep hygiene (foundational but insufficient alone) |
| PSYCH-SOMATIC-SYMPTOM-DISORDER | Sleep hygiene |
| PSYCH-WORK-STRESS | Limit caffeine and alcohol |
| PSYCH-WORK-STRESS | Take regular breaks during workday |
| PULM-BRONCHITIS-ACUTE | Supportive care: rest, hydration, humidified air |
| PULM-CHRONIC-COUGH | Lifestyle modifications - elevate head of bed, avoid late meals, weight loss |
| RESP-URI | Supportive care (mainstay): rest, hydration, humidified air |
| RHEUM-GOUT | Lifestyle: Limit alcohol, red meat, seafood (high purines). Increase water, low-fat dairy, cherries (ACR 2023) |
| RHEUM-OSTEOPOROSIS | Limit alcohol (<2 drinks/day) |
| SURG-POSTOP-ILEUS | Early ambulation - walk QID |
| TRAUMA-HEAD-INJURY | Mild TBI/concussion: rest, gradual return to activity, avoid re-injury |
| URO-BALANITIS | Improve hygiene: wash daily with water, pat dry |
| URO-DYSURIA | Increase oral fluids |
| URO-INCONTINENCE-STRESS | Perform 10 repetitions, 3 times daily |
| URO-NOCTURIA | Limit fluids 2-3 hours before bedtime |
| URO-NOCTURIA | Elevate legs in afternoon/evening (mobilize edema before bedtime) |
| URO-NOCTURIA | Sleep hygiene |
| URO-OVERACTIVE-BLADDER | Reduce caffeine, alcohol, carbonated drinks, artificial sweeteners, spicy/acidic foods |
| URO-TESTICULAR-PAIN | Rest, avoid heavy lifting and sexual activity until resolved |
| UROLOGY-BENIGN-PROSTATIC-HYPERPLASIA | Lifestyle modifications - limit fluids before bed, reduce caffeine/alcohol, timed voiding, double voiding |
| UROLOGY-ERECTILE-DYSFUNCTION | Take on empty stomach for faster onset, requires sexual stimulation to work |
| UROLOGY-KIDNEY-STONES | Drink 2-3 liters daily to achieve urine output greater than 2 liters (urine specific gravity less than 1.010) |
| GENERAL-FATIGUE | Graded exercise therapy - start low (10-15 min), gradually increase |
| OBGYN-DYSMENORRHEA | Start 1-2 days before expected menses and continue first 2-3 days |
| PED-DEHYDRATION | Give small frequent amounts |
| PULM-TOBACCO-USE | Start 1 week before quit date |
| PULM-TOBACCO-USE | Start 1-2 weeks before quit date |
| URO-INCONTINENCE-URGE | Start voiding every 1-2 hours whether or not urge present |

## 11. New tree: CARD-AORTIC-DISSECTION (draft)

Added because the can't-miss list for chest pain had no aortic dissection
tree. Status draft, urgency emergent. Every presentation, workup, treatment
and referral line cites the section, class of recommendation (COR) and level
of evidence (LOE) of:

Isselbacher EM, et al. 2022 ACC/AHA Guideline for the Diagnosis and
Management of Aortic Disease. Circulation. 2022;146:e334-e482;
J Am Coll Cardiol. 2022;80:e223-e393.

| Content | Guideline basis |
|---|---|
| Presentation: abrupt severe chest/back pain (sharp or stabbing more common than tearing), limb BP difference >20 mm Hg, syncope, stroke symptoms, new AR murmur, shock, malperfusion | §7.1, Table 22, Table 26 |
| ADD-RS risk score (0 low, 1 moderate, 2-3 high) | §7.2, Table 24 |
| D-dimer <500 ng/mL makes AAS unlikely in low-probability patients; not diagnostic | §7.2 (text, no numbered recommendation) |
| CT for initial imaging | §7.2, COR 1, LOE C-LD |
| TEE or MRI as alternatives; echo when too unstable for radiology | §7.2, COR 2a, LOE C-LD |
| Anti-impulse therapy with arterial line in ICU | §7.3.1, COR 1, LOE B-NR |
| SBP <120 mm Hg or lowest BP maintaining end-organ perfusion | §7.3.1, COR 1, LOE C-LD |
| Heart rate 60-80 bpm | §7.3.1, COR 1, LOE C-LD |
| IV beta blockers first; IV non-dihydropyridine CCB if contraindicated | §7.3.1, COR 1 / COR 2a, LOE B-NR |
| IV vasodilators if BP not controlled | §7.3.1, COR 1, LOE C-LD |
| Pain control for hemodynamic management | §7.3.1, COR 1, LOE C-EO |
| Type A: emergency surgical consultation and immediate surgery; immediate repair with malperfusion | §7.4.1, COR 1, LOE B-NR |
| Type A: transfer from low- to high-volume aortic center is reasonable | §7.4.1, COR 2a, LOE B-NR |
| Type B uncomplicated: medical therapy first; endovascular may be considered with high-risk features | §7.4.2, COR 1, LOE B-NR / COR 2b, LOE B-R |
| Type B complicated: intervention; endovascular over open repair for rupture | §7.4.2, COR 1, LOE C-LD / C-EO |
| Surveillance CT/MRI at 1, 6, 12 months, then annually | §7.8.1, COR 1, LOE B-NR |
| Multidisciplinary aortic team for acute aortic disease needing urgent repair | §4, COR 1, LOE C-EO |

D-dimer units: the <500 ng/mL cutoff depends on how the lab reports D-dimer
(fibrinogen-equivalent units, FEU, vs D-dimer units, DDU; 1 DDU is roughly
2 FEU). Confirm the cutoff against the units and assay in use before relying
on it.

Reviewer notes: treatment lines quote the guideline's recommendation wording
("is recommended", "is reasonable", "may be considered") or use "Consider"; no
drug doses are given. The ECG/troponin workup line and the antithrombotic
caution pearl are general practice, not quoted guideline recommendations.
Codes to confirm: ICD-10-CM I71.00, I71.010-I71.019, I71.02, I71.03 (FY2023
expansion of I71.0) and SNOMED CT 308546005 (Dissection of aorta).

## 12. Possible missed items (encounter assessment, Phase 3)

A "Possible missed items" section in the encounter assessment runs three
rule-based checks (no AI). Wording is "consider" / "may be due" with the
source cited; nothing is stated as missed. Each item shows its tree's or
rule's review status and expands to the evidence, the window checked and the
caveats. A check whose data could not be retrieved says "Not checked" instead
of producing items.

1. **Abnormal results without a diagnosis:** a chronic tree's chart criteria
   are met ("consistent") and its `known_condition` codes are not on the
   problem list. A single abnormal result that still needs confirmation
   ("possible") is listed separately under a collapsed line, "Single results
   that may need repeating", with its value, date and source. Acute trees
   (ACS, sepsis, DKA) are excluded; they are shown as chart cards.
2. **Diagnoses without support:** a problem-list condition that maps to one of
   the 8 chronic criteria trees, with no criterion met in the tree's lookback
   and none of its `related_medications` on the active medication list. Both
   sides are shown (problem-list entry, results found or "no results in the
   window", medications on file, medications looked for); the conflict is not
   resolved.
3. **Screenings that may be due:** the rules below (`backend/screening/uspstf_rules.yml`,
   all `status: draft`). Data windows: lab results and procedures/imaging
   10 years, vital signs (BP, BMI) 1 year, latest US Core smoking status
   (LOINC 72166-2). Where a rule needs data RealDiag cannot see, the item says
   so rather than guessing: BMI missing ("may apply"), smoking status missing
   or unknown (AAA, lung), pack-years and quit date (lung, always unavailable).

### Screening rules (checked against uspreventiveservicestaskforce.org, 2026-10-19)

| Rule | Source | Grade | Population | Counts as done (any one) | Excluded if |
|---|---|---|---|---|---|
| Colorectal cancer screening | [USPSTF. Colorectal Cancer: Screening. Final Recommendation Statement, May 2021](https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/colorectal-cancer-screening) | B (45-49), A (50-75) | all, 45-75 | colonoscopy within 10 y [keywords: colonoscopy]; CT colonography within 5 y [keywords: colonography]; flexible sigmoidoscopy within 5 y [keywords: sigmoidoscopy]; FIT or high-sensitivity gFOBT within 1 y [LOINC 29771-3, 56490-6, 56491-4, 57905-2, 2335-8, 14563-1, 14564-9, 14565-6]; stool DNA-FIT within 3 y [LOINC 77353-1, 77354-9] | C18, C19, C20, Z85.03, Z85.04 |
| Breast cancer screening | [USPSTF. Breast Cancer: Screening. Final Recommendation Statement, April 2024](https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/breast-cancer-screening) | B (40-74) | female, 40-74 | mammogram within 2 y [keywords: mammogra, modality: mg, tomosynthesis]; mammogram within 2 y [keywords: mammogra, tomosynthesis] | - |
| Cervical cancer screening | [USPSTF. Cervical Cancer: Screening. Final Recommendation Statement, August 2018](https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/cervical-cancer-screening) | A (21-65) | female, 21-65 | cervical cytology within 3 y [LOINC 10524-7, 19762-4, 19764-0, 19765-7, 19766-5, 47527-7, 47528-5, 33717-0]; high-risk HPV test within 5 y [LOINC 21440-3, 30167-1, 59263-4, 59420-0, 71431-1, 77379-6, 77399-4, 77400-0] | Z90.71, hysterectomy |
| Hypertension screening | [USPSTF. Hypertension in Adults: Screening. Final Recommendation Statement, April 2021](https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/hypertension-in-adults-screening) | A (18-+) | all, 18 | blood pressure reading within 1 y [LOINC 8480-6, 85354-9]; blood pressure reading within 3 y [LOINC 8480-6, 85354-9] | I10, I11, I12, I13, I15, I16 |
| Prediabetes and type 2 diabetes screening | [USPSTF. Prediabetes and Type 2 Diabetes: Screening. Final Recommendation Statement, August 2021](https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/screening-for-prediabetes-and-type-2-diabetes) | B (35-70) | all, 35-70, BMI >= 25 | HbA1c or fasting glucose within 3 y [LOINC 4548-4, 17856-6, 1558-6, 76629-5] | E08, E09, E10, E11, E13, R73.03, R73.09 |
| HIV screening | [USPSTF. Human Immunodeficiency Virus (HIV) Infection: Screening. Final Recommendation Statement, June 2019](https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/human-immunodeficiency-virus-hiv-infection-screening) | A (15-65) | all, 15-65 | HIV test ever [LOINC 75622-1, 56888-1, 7917-8, 7918-6, 68961-2, 5221-7, 48345-6, 58900-2, 80387-4] | B20, Z21 |
| Hepatitis C screening | [USPSTF. Hepatitis C Virus Infection in Adolescents and Adults: Screening. Final Recommendation Statement, March 2020](https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/hepatitis-c-screening) | B (18-79) | all, 18-79 | hepatitis C antibody or RNA test ever [LOINC 16128-1, 13955-0, 40726-3, 11011-4, 20416-4, 29609-5] | B17.1, B18.2, B19.2 |
| Osteoporosis screening | [USPSTF. Osteoporosis to Prevent Fractures: Screening. Final Recommendation Statement, January 2025](https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/osteoporosis-screening) | B (65-+) | female, 65 | bone density (DXA) ever [keywords: dxa, dexa, densitometry, bone density]; bone density (DXA) ever [keywords: dxa, dexa, densitometry, bone density] | M80, M81 |
| Lung cancer screening | [USPSTF. Lung Cancer: Screening. Final Recommendation Statement, March 2021](https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/lung-cancer-screening) | B (50-80) | all, 50-80, ever smoked | low-dose CT of the chest within 1 y [keywords: low dose, low-dose, ldct, lung cancer screening]; low-dose CT of the chest within 1 y [keywords: low dose, low-dose, ldct, lung cancer screening] | C34 |
| Abdominal aortic aneurysm screening | [USPSTF. Abdominal Aortic Aneurysm: Screening. Final Recommendation Statement, December 2019](https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/abdominal-aortic-aneurysm-screening) | B (65-75) | male, 65-75, ever smoked | abdominal aortic ultrasound ever [keywords: aaa, aortic aneurysm, abdominal aorta, aorta ultrasound, aortic ultrasound]; abdominal aortic ultrasound ever [keywords: aaa screening, aortic aneurysm screening, abdominal aorta, aortic ultrasound] | I71.3, I71.4, I71.5, I71.6 |

Reviewer notes:
- LOINC and keyword lists decide what counts as "done"; please confirm them
  (results without LOINC coding, or procedures named differently, will not be
  found and the item will say "may be due").
- Hypertension 18-39: the rule allows 3-5 years but only 1 year of vital signs
  is retrieved; the item says so.
- HIV and hepatitis C "at least once": only 10 years of results are retrieved;
  the item says so.
- Not covered: osteoporosis screening under 65 (needs a clinical risk
  assessment), HIV screening in pregnancy and repeat screening for risk,
  Asian American BMI cut-off of 23 (race is not checked), prior mastectomy.
- Smoking status codes read as current: 449868002, 428041000124106,
  428071000124103, 428061000124105, 77176002; former: 8517006; never:
  266919005; unknown: 266927001.

### Related medications (check 2), pending review

- **CARD-HYPERTENSION:** *pril, *sartan, hydrochlorothiazide, chlorthalidone, indapamide, amlodipine, nifedipine, felodipine, diltiazem, verapamil, *olol, spironolactone, eplerenone, hydralazine, clonidine, minoxidil, doxazosin, terazosin, prazosin
- **ENDO-DIABETES:** metformin, insulin, glipizide, glyburide, glimepiride, sitagliptin, linagliptin, saxagliptin, alogliptin, empagliflozin, dapagliflozin, canagliflozin, ertugliflozin, semaglutide, liraglutide, dulaglutide, exenatide, tirzepatide, pioglitazone
- **ENDO-DYSLIPIDEMIA:** *statin, ezetimibe, evolocumab, alirocumab, inclisiran, bempedoic acid, fenofibrate, gemfibrozil, icosapent ethyl, niacin
- **ENDO-HYPOTHYROIDISM:** levothyroxine, liothyronine, thyroid desiccated, armour thyroid
- **ENDO-PREDIABETES:** metformin
- **HEME-ANEMIA:** ferrous sulfate, ferrous gluconate, ferrous fumarate, iron sucrose, ferric carboxymaltose, iron dextran, ferumoxytol, folic acid, cyanocobalamin, vitamin b12, epoetin, darbepoetin
- **NEPHRO-CHRONIC-KIDNEY-DISEASE:** *pril, *sartan, dapagliflozin, empagliflozin, canagliflozin, finerenone, sodium bicarbonate, sevelamer, calcium acetate, lanthanum, epoetin, darbepoetin, calcitriol
- **NEPHRO-HYPERKALEMIA:** patiromer, sodium zirconium cyclosilicate, sodium polystyrene sulfonate

("*pril", "*sartan", "*olol", "*statin" match any drug name ending that way.)

## 13. Decision trees with a branch to a missing step

Two conditional trees have a branch that points to a step the tree does not
contain. Their content has **not** been changed. Until they are fixed:

- the step-by-step decision tree page (`/diagnose`) does not offer them and
  says they are temporarily unavailable pending content review;
- the tree validator lists them in `KNOWN_MISSING_BRANCH_TARGETS`
  (`backend/scripts/validate_rules.py`) so CI passes; any other tree with a
  missing step fails validation, and a test fails if that list grows.

| Priority | Tree | Step | Branch | Missing step | Effect on a walk |
|---|---|---|---|---|---|
| **High** | PSYCH-PSYCHOSIS (Psychosis) | `safety_assessment` | default (taken when none of the other branches match) | `psychotic_disorder_assessment` | A patient with no emergency features, no medical-emergency features, not a first episode and no substance use stops at the safety assessment with no further guidance. |
| Normal | ID-FEVER (Fever Workup) | `initial_assessment` | default (taken when the sepsis screen does not match) | `localized_infection` | A febrile patient without sepsis features stops at the initial assessment; the source-finding steps are reachable only through the sepsis screen. |

PSYCH-PSYCHOSIS is the priority because it is the safety-assessment step of a
psychiatric presentation: the path that ends silently is the common
non-emergency one.

To fix a tree: add the missing step (or point the branch at an existing step,
or set the default to `null` to end the walk there), add a change_log entry,
then remove the tree from `KNOWN_MISSING_BRANCH_TARGETS` (the validator fails
until it is removed) and from `KNOWN_MISSING_TARGETS` in
`backend/tests/test_tree_walks.py`. The tree then reappears on `/diagnose`
automatically.

## Checked: no action needed

- **Teaching flashcards with drug doses** (`backend/services/education_router.py`,
  e.g. MONA with aspirin 325 mg) are served only by `/education/flashcards`
  and shown only on the Education page. They never appear alongside
  patient results or search results.

## How review status is shown and cleared

- Every tree's `status` is shown to users as a label: `draft` → "Draft - under
  clinical review.", `review` → "In clinical review - not yet approved.",
  `approved` → "Clinically reviewed.", `retired` → "Retired - not for clinical use."
- While any content is unreviewed, every screen and API response that carries
  tree content, urgency, treatment, severity, can't-miss labels, criteria
  results or possible missed items shows this notice (`clinical_review_notice`
  in the API; also in FHIR Condition notes, HL7 NTE segments, JSON/XML/CSV
  exports and PDF reports):
  "Clinical content is under review. Urgency levels, treatment information,
  thresholds, and screening rules are proposed and have not completed
  clinical review. Verify against current guidelines before acting."
- To mark a tree reviewed: set its `status: approved` and add a change_log entry
  naming the reviewer and date. The label updates on the next deploy.
- The notice disappears automatically once **no tree and no screening rule
  (`backend/screening/uspstf_rules.yml`) is `draft` or `review`** and
  `SEVERITY_THRESHOLDS_REVIEWED` in `backend/services/clinical_review.py` is
  set to `True` (only after section 3 and 4 thresholds are signed off).
