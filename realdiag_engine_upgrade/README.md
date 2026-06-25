# RealDiag engine upgrade scaffold

This package converts the backend from a single starter rule set into a modular service layout.

## Files
- `backend/services/diagnostic_engine.py` - orchestration layer
- `backend/services/domains/cardiovascular.py` - starter chest pain pathway
- `backend/services/domains/neurology.py` - starter headache / seizure / cognitive pathway
- `backend/services/utils/common.py` - normalization and utility functions

## How to wire it in
1. Replace your existing `backend/services/diagnostic_engine.py` with the new file.
2. Add the `domains` and `utils` folders under `backend/services/`.
3. Restart the backend.
4. Test the `/analyze` endpoint and the frontend `/demo` page.

## Next recommended upgrades
- Split neurology into separate files for headache, seizure, concussion, trigeminal neuralgia, and cognitive impairment.
- Replace heuristic confidence scores with your validated RealDiag rule logic.
- Expand symptom normalization using your ICD-10 / SNOMED concept mappings.
- Add a `red_flags.py` utility to centralize can’t-miss escalation logic.
