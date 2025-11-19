# Backend Utility Scripts

This directory contains utility scripts for maintaining and validating the RealDiag medical knowledge base.

## Scripts

### validate_rules.py

Validates medical rules for completeness, consistency, and currency.

**Usage:**

```bash
# Basic validation (structure and required fields)
python validate_rules.py

# Check for outdated rules (>1 year old)
python validate_rules.py --check-dates

# Check for missing citations
python validate_rules.py --check-citations

# Generate detailed report
python validate_rules.py --report

# Run all checks with report
python validate_rules.py --all

# Custom maximum age threshold (in days)
python validate_rules.py --check-dates --max-age 180
```

**What it checks:**

✅ YAML syntax errors  
✅ Required metadata fields (family, version, source, rules)  
✅ Individual rule fields (id, label, icd10, snomed, presentations)  
✅ Version format (semantic versioning)  
✅ Empty arrays in required fields  
✅ Optional: Last update dates (flags rules >1 year old)  
✅ Optional: Missing citations  
✅ Decision tree structure validation  

**Exit codes:**
- `0`: All checks passed (warnings are OK)
- `1`: Errors found (must be fixed)

**Recommended schedule:**
- Run `--all` before committing medical content changes
- Run `--check-dates` monthly to identify outdated rules
- Run `--check-citations` quarterly to ensure proper source attribution

## Adding New Scripts

When adding new utility scripts:

1. Add appropriate docstrings and help text
2. Follow the same error/warning/info structure
3. Document in this README
4. Include in CI/CD pipeline if relevant

## Related Documentation

- [MEDICAL_UPDATE_PROCESS.md](../../MEDICAL_UPDATE_PROCESS.md): Complete medical content update workflow
- [CONTRIBUTING.md](../../CONTRIBUTING.md): General contribution guidelines
- [backend/rules/README.md](../rules/README.md): Rule file format specification
- [backend/trees/README.md](../trees/README.md): Decision tree syntax guide
