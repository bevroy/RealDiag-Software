# RealDiag First Seizure Module

This package adds a dedicated **first seizure** module to the RealDiag backend.

## Files
- `backend/services/domains/first_seizure.py` — dedicated first-seizure logic
- `backend/services/diagnostic_engine.py` — minimal orchestrator that routes to first-seizure logic first

## Install in GitHub Codespaces
1. Upload `realdiag_first_seizure_module_package.zip` into the repo root.
2. Run:
   ```bash
   unzip realdiag_first_seizure_module_package.zip
   ```
3. Copy `realdiag_first_seizure_module/backend/services/domains/first_seizure.py` into your real repo at:
   `backend/services/domains/first_seizure.py`
4. Replace your real repo file:
   `backend/services/diagnostic_engine.py`
   with the version from this package **only if** you want the minimal seizure-first orchestrator.

## Safer option
If you already have a larger orchestrator with other domains, do not fully replace it.
Instead, only:
- add `first_seizure.py`
- import `evaluate_first_seizure`
- call it near the top of `analyze_case()`

Example:
```python
from backend.services.domains.first_seizure import evaluate_first_seizure

first_seizure_result = evaluate_first_seizure(payload, normalized_text)
if first_seizure_result:
    return first_seizure_result
```

## What it returns
- ranked seizure-focused differential
- workup recommendations
- referral urgency
- ICD-10 / SNOMED starter mapping
- rationale and matched signals

## Trigger examples
- first seizure
- witnessed convulsion
- tongue biting
- post-ictal confusion
- urinary incontinence
- focal weakness after event
- seizure with fever / trauma / pregnancy / anticoagulants
