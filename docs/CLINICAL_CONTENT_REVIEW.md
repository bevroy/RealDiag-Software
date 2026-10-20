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
  tree content, urgency, treatment or severity ratings shows this notice
  (`clinical_review_notice` in the API):
  "Clinical content is under review. Urgency levels, treatment information, and
  severity thresholds are proposed and have not completed clinical review.
  Verify against current guidelines before acting."
- To mark a tree reviewed: set its `status: approved` and add a change_log entry
  naming the reviewer and date. The label updates on the next deploy.
- The notice disappears automatically once **no tree is `draft` or `review`**
  and `SEVERITY_THRESHOLDS_REVIEWED` in `backend/services/clinical_review.py` is
  set to `True` (only after section 3 and 4 thresholds are signed off).
