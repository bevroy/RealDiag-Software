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
