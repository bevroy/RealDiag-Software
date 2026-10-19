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

## 4. DKA glucose thresholds (SMART chart evaluation)

These thresholds are unchanged from before, but they now apply after unit conversion
(mmol/L × 18.016 = mg/dL):

- Hyperglycemia criterion: > 250 mg/dL (13.9 mmol/L)
- "Critical" severity: > 500 mg/dL (27.8 mmol/L)

## 4a. Chart-evaluation criteria in tree files (SMART on FHIR)

Chart evaluation is driven by the `criteria` section of each tree (see the
format at the top of `backend/services/smart_diagnostic_engine.py`). All of
these trees are `status: draft` and show the "under clinical review" notice.
"Verified" below means checked against the primary guideline document;
everything else was confirmed only from secondary summaries and must be checked
against the primary text.

### Acute (shown even when data is missing)

These moved from code into tree files unchanged; tests prove identical results
(`backend/tests/test_criteria_equivalence.py`).

| Tree | Criterion | Threshold | Source cited | Notes for reviewers |
|---|---|---|---|---|
| CARD-ACUTE-CORONARY-SYNDROME | Elevated troponin (I: 10839-9, T: 6598-7) | above the lab's upper reference limit; severity high >= 2.5x, critical >= 10x | 2025 ACC/AHA/ACEP/NAEMSP/SCAI ACS Guideline; Fourth Universal Definition of MI (2018) | Severity multiples have no cited source (section 3). |
| CARD-ACUTE-CORONARY-SYNDROME | Heart rate (8867-4), supporting only | > 100/min | same | Never suggests ACS on its own. |
| ID-SEPSIS | qSOFA: RR (9279-1) >= 22/min, SBP (8480-6) <= 100 mmHg, GCS (9269-2) < 15; WBC (6690-2) < 4 or > 12 K/uL | qSOFA >= 2 suggests evaluation | Sepsis-3 (JAMA 2016); Surviving Sepsis Campaign 2021 | **The 2021 Surviving Sepsis Campaign guideline recommends against using qSOFA alone as a screening tool.** Units are not checked for these vitals/WBC (kept as previously coded). |
| ENDO-DKA | Glucose (2345-7) > 250 mg/dL (13.9 mmol/L); bicarbonate (2028-9) < 18 mEq/L; critical > 500 mg/dL | both met suggests evaluation | thresholds as previously coded | **Predates the 2024 ADA/EASD/JBDS/AACE/DTS hyperglycemic-crises consensus (Diabetologia 2024), which changed DKA criteria; review and update.** |

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
| CARD-HYPERTENSION | Systolic (8480-6) / diastolic (8462-4) BP | >= 130 / >= 80 mmHg on >= 2 separate days; stage 2 (>= 140 / 90) rated high | 365 days | 2025 AHA/ACC High Blood Pressure Guideline | Guideline uses the average of >= 2 readings on >= 2 occasions; this counts elevated readings instead. |
| NEPHRO-CHRONIC-KIDNEY-DISEASE | eGFR (33914-3, 62238-1, 98979-8, 48642-3, 48643-1) | < 60 mL/min/1.73m2 on 2 results >= 90 days apart | 730 days | KDIGO 2024 CKD Guideline | Table 1 wording |
| NEPHRO-CHRONIC-KIDNEY-DISEASE | Urine albumin-creatinine ratio (9318-7, 14959-1) | >= 30 mg/g (3 mg/mmol) on 2 results >= 90 days apart | 730 days | same | same |
| HEME-ANEMIA | Hemoglobin (718-7) | < 13.0 g/dL (men); < 12.0 g/dL (non-pregnant women) | 90 days | WHO Guideline on haemoglobin cutoffs (2024) | Pregnancy status is not known; pregnancy cutoffs differ. Altitude/smoking adjustments not applied. |
| ENDO-HYPOTHYROIDISM | TSH (3016-3, 11580-8) | above the lab's reference range; free T4 (3024-7, 14920-3) below range = overt | 365 days | ATA/AACE Hypothyroidism in Adults (2012); ATA Treatment of Hypothyroidism (2014) | Confirm no newer general ATA/AACE diagnostic guideline supersedes these. |
| NEPHRO-HYPERKALEMIA | Potassium (2823-3, 6298-4) | >= 5.5 mild; >= 6.0 moderate (high); >= 6.5 severe (critical) | 30 days | UK Kidney Association hyperkalaemia guideline (2023) | 6.0 and 6.5 confirmed from secondary sources; **the 5.5 mild cut-off is not yet confirmed** against the final UKKA document. |
| ENDO-DYSLIPIDEMIA | LDL-C (13457-7, 18262-6, 2089-1) | >= 190 mg/dL (4.9 mmol/L) | 730 days | 2026 ACC/AHA/Multisociety Dyslipidemia Guideline | Class/level details |

LOINC codes and unit conversions (`backend/services/lab_units.py`) also need an
informatics check against the EHR's actual result codes.

## 5. Reworded alert actions

23 alert actions in `frontend/utils/redFlagAlerts.js` and
`frontend/utils/timeSensitiveAlerts.js` that named a drug and dose, a
blood-product quantity, or cath lab activation now defer to the named
guideline or institutional protocol (for example "IM epinephrine is
first-line per anaphylaxis guidelines (WAO/AAAAI); dosing per protocol").
Please confirm the wording and the guideline named for each.

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
