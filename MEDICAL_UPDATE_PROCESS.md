# Medical Knowledge Update Process

## Overview

This document establishes the process for reviewing, updating, and maintaining the medical diagnostic rules and clinical guidelines in RealDiag to ensure accuracy and alignment with current evidence-based medicine.

---

## 🔄 Update Schedule

### Routine Reviews
- **Quarterly (Every 3 months)**: Review major guideline updates from specialty societies
- **Annually (Each year)**: Comprehensive review of all diagnostic rules and decision trees
- **Ad-hoc**: Critical updates for safety alerts, drug recalls, or major guideline changes

### Monitoring Sources
Continuously monitor these sources for guideline updates:
- American College of Cardiology (ACC/AHA)
- American Diabetes Association (ADA)
- American Academy of Neurology (AAN)
- Infectious Diseases Society of America (IDSA)
- National Institute for Health and Care Excellence (NICE)
- UpToDate clinical updates
- Cochrane Reviews
- FDA Safety Alerts
- CDC MMWR (Morbidity and Mortality Weekly Report)

---

## 📋 Update Process

### 1. Identification Phase

**Trigger Events:**
- New clinical practice guideline published
- Major drug approval or recall
- ICD-10 or SNOMED code updates
- Safety alert from FDA, CDC, or WHO
- User-reported inaccuracy
- Systematic annual review

**Documentation:**
Create an issue in GitHub with:
```
Title: [UPDATE] <Specialty> - <Condition> - <Source>
Example: [UPDATE] Cardiology - Atrial Fibrillation - 2025 AHA/ACC Guidelines

Body:
- Source: [Link to guideline]
- Publication Date: [Date]
- Summary of Changes:
  - Key change 1
  - Key change 2
- Affected Files:
  - backend/rules/cardiology.yml
  - backend/trees/CARD-CHEST-PAIN.yml
- Priority: [Low/Medium/High/Critical]
```

### 2. Review Phase

**Clinical Review Requirements:**
- All updates must be reviewed by a qualified healthcare professional
- Critical updates (safety alerts, major diagnostic criteria changes) require dual review
- Document reviewer credentials and date in the pull request

**Version Control:**
Each rule file maintains version metadata:
```yaml
family: cardiology
version: 2.1.0  # Increment on update
last_updated: "2025-11-19"
source: "2025 AHA/ACC Guidelines for AFib Management"
guideline_version: "2025"
evidence_level: "A"  # A=Strong evidence, B=Moderate, C=Limited
```

**Review Checklist:**
- [ ] Guideline source verified and current
- [ ] Evidence level assessed (A/B/C)
- [ ] Changes aligned with current standard of care
- [ ] ICD-10 and SNOMED codes verified
- [ ] Clinical presentations updated
- [ ] Management/treatment protocols updated
- [ ] Drug information current and accurate
- [ ] Contraindications reviewed
- [ ] Referral criteria appropriate
- [ ] Decision tree logic validated (if applicable)
- [ ] Version number incremented
- [ ] `last_updated` date set

### 3. Implementation Phase

**File Updates:**

For rule files (`backend/rules/*.yml`):
```yaml
# Example: backend/rules/cardiology.yml
family: cardiology
version: 2.1.0
last_updated: "2025-11-19"
source: "2025 AHA/ACC Guidelines for Atrial Fibrillation Management"

rules:
  - id: CARD-AFIB
    label: Atrial Fibrillation
    version: 2.0.0  # Rule-specific version
    last_reviewed: "2025-11-19"
    guideline_source: "2025 AHA/ACC AFib Guidelines"
    evidence_level: "A"
    
    presentations:
      - Palpitations
      - Irregular heartbeat
      # ... updated per guidelines
    
    clinical_pearls:
      - "CHA₂DS₂-VASc score guides anticoagulation (2025 guidelines)"
      # ... updated recommendations
    
    management:
      - "Rate control vs rhythm control based on symptoms"
      - "Anticoagulation per 2025 AHA/ACC guidelines"
      # ... updated protocols
    
    tests:
      - "12-lead ECG (irregularly irregular rhythm, no P waves)"
      - "TSH (exclude thyroid dysfunction)"
      # ... updated testing recommendations
    
    citations:
      - "2025 AHA/ACC/ACCP/HRS Guideline for Management of AFib (Circulation. 2025;XX:XXX)"
      - "DOAC preferred over warfarin for stroke prevention (Grade 1A)"
      # ... specific references
```

For decision trees (`backend/trees/*.yml`):
```yaml
id: CARD-CHEST-PAIN
title: Chest Pain Evaluation
version: 1.2.0
last_updated: "2025-11-19"
guideline_source: "2025 ACC/AHA Chest Pain Guidelines"

entry: cp_start
nodes:
  - id: cp_start
    version: 1.1.0
    last_reviewed: "2025-11-19"
    # ... updated decision logic
```

**Change Documentation:**
Update `CHANGELOG.md`:
```markdown
## [2.1.0] - 2025-11-19

### Medical Updates
#### Cardiology
- **Atrial Fibrillation (CARD-AFIB)**: Updated per 2025 AHA/ACC Guidelines
  - Modified CHA₂DS₂-VASc scoring recommendations
  - Updated anticoagulation protocols (DOAC preferences)
  - Added new stroke risk stratification
  - Source: 2025 AHA/ACC/ACCP/HRS AFib Management Guidelines
  
### Technical Changes
- Updated backend/rules/cardiology.yml version 2.0.0 → 2.1.0
- Added citations to CARD-AFIB rule
```

### 4. Testing Phase

**Validation Tests:**
```bash
# Run rule validation
cd backend
python -m pytest tests/test_rules_validation.py

# Verify YAML syntax
python -c "import yaml; yaml.safe_load(open('rules/cardiology.yml'))"

# Check decision tree logic
python -m pytest tests/test_decision_trees.py

# Run integration tests
python -m pytest tests/test_api_reference.py
```

**Manual Testing:**
- [ ] Rule appears correctly in /rules page
- [ ] Citations display properly
- [ ] Search functionality works
- [ ] Decision tree logic functions correctly (if modified)
- [ ] Sources page displays updated information
- [ ] Mobile display correct

### 5. Deployment Phase

**Pull Request Requirements:**
```
Title: [MEDICAL UPDATE] <Specialty> - <Summary>
Example: [MEDICAL UPDATE] Cardiology - AFib Guidelines 2025

Description:
## Clinical Update Summary
- **Specialty**: Cardiology
- **Condition**: Atrial Fibrillation
- **Guideline Source**: 2025 AHA/ACC/ACCP/HRS AFib Management Guidelines
- **Publication Date**: November 2025
- **Evidence Level**: A (Strong Evidence)

## Changes Made
- Updated CHA₂DS₂-VASc scoring recommendations
- Modified anticoagulation protocols
- Added DOAC preference statements
- Updated stroke risk stratification

## Clinical Reviewer
- Name: [Reviewer Name, MD/DO/NP/PA]
- Credentials: [Board Certification, Specialty]
- Review Date: 2025-11-19
- Approval: ✅ Approved

## Testing Completed
- [x] YAML validation passed
- [x] Rule displays correctly
- [x] Citations render properly
- [x] Manual testing completed

## Files Modified
- backend/rules/cardiology.yml
- CHANGELOG.md
```

**Approval Process:**
1. Clinical reviewer approval (required)
2. Technical review for code quality
3. Automated tests passing
4. Documentation updated
5. Merge to main branch
6. Deploy to production

### 6. Communication Phase

**Notify Users:**
- Update banner on homepage (for major changes)
- Add to sources page "Recent Updates" section
- Include in release notes
- Email notification to registered users (future feature)

---

## 🔍 Quality Assurance

### Data Integrity Checks

**Automated Validation Script** (`backend/scripts/validate_rules.py`):
```python
"""Validate medical rules for completeness and consistency."""

def validate_rule_file(file_path):
    """Validate a single rule YAML file."""
    required_fields = {
        'family': str,
        'version': str,
        'last_updated': str,
        'source': str,
        'rules': list
    }
    
    rule_required_fields = {
        'id': str,
        'label': str,
        'icd10': list,
        'snomed': list,
        'presentations': list
    }
    
    # Validation logic...
    
def check_for_outdated_rules(rule_file, max_age_days=365):
    """Flag rules not reviewed within specified time period."""
    # Check last_updated dates...
    
def verify_citations(rule_file):
    """Ensure all rules have proper citations."""
    # Check for citations field...
```

**Run monthly:**
```bash
cd backend
python scripts/validate_rules.py --check-dates --check-citations --report
```

### Evidence Grading

All clinical recommendations should include evidence level:
- **Grade A**: Strong evidence from multiple RCTs or strong observational evidence
- **Grade B**: Moderate evidence from one or more RCTs or strong observational studies
- **Grade C**: Limited evidence, based on expert opinion or case reports

---

## 📊 Tracking & Metrics

### Update Dashboard (Future Enhancement)

Track in `/admin/medical-updates` page:
- Rules updated in last quarter
- Rules requiring review (>1 year old)
- Pending guideline updates
- Evidence levels for all rules
- Source guideline versions

### Metrics to Monitor:
- Average rule age (target: <1 year)
- % of rules with citations (target: 100%)
- % of rules with evidence levels (target: 100%)
- Time from guideline publication to implementation (target: <90 days)
- Number of critical safety updates per year

---

## 🚨 Critical Updates

### Expedited Process for Safety-Critical Changes

**Trigger Events:**
- FDA safety alert (drug recall, black box warning)
- CDC emergency guideline
- Major diagnostic criteria change affecting patient safety

**Fast-Track Process:**
1. **Immediate notification** to technical team
2. **Emergency clinical review** (within 24-48 hours)
3. **Rapid implementation** (within 1 week)
4. **Priority deployment**
5. **User notification** via homepage banner

**Example:**
```yaml
# backend/rules/infectious_disease.yml
rules:
  - id: ID-COVID19
    label: COVID-19
    version: 3.5.0  # Rapid version increment
    last_updated: "2025-11-20"
    critical_update: true  # Flag for user attention
    update_reason: "CDC updated treatment guidelines"
    
    management:
      - "⚠️ UPDATED 2025-11: New antiviral protocols per CDC"
      - "Nirmatrelvir/ritonavir (Paxlovid) for high-risk patients"
      # ... updated protocols
```

---

## 👥 Roles & Responsibilities

### Clinical Review Board (Recommended)
- **Medical Director**: Oversees all clinical updates, final approval
- **Specialty Champions**: 1-2 clinicians per specialty (cardiology, neurology, etc.)
- **Evidence Reviewer**: Assesses evidence quality and grades recommendations
- **Safety Officer**: Monitors for critical safety updates

### Technical Team
- **Backend Developer**: Implements rule updates, maintains data structure
- **QA Engineer**: Validates changes, runs test suites
- **DevOps**: Manages deployments, version control

### Process Owner
- **Medical Informatics Lead**: Coordinates update process, tracks metrics, ensures compliance

---

## 📅 Annual Review Cycle

### Q1 (January-March)
- Review Neurology, Cardiology, Endocrinology rules
- Update decision trees for these specialties
- Assess new guidelines from AAN, ACC/AHA, ADA

### Q2 (April-June)
- Review Pulmonology, GI, Infectious Disease rules
- Update decision trees
- Assess IDSA, ACG guidelines

### Q3 (July-September)
- Review Nephrology, Rheumatology, Dermatology, Psychiatry rules
- Update decision trees
- Assess specialty society guidelines

### Q4 (October-December)
- Review OB/GYN, Hematology/Oncology, Orthopedics rules
- Update decision trees
- Comprehensive system-wide review
- Plan next year's priorities

---

## 🔗 Integration with Development Workflow

### Git Workflow for Medical Updates

```bash
# Create feature branch for medical update
git checkout -b medical-update/cardiology-afib-2025

# Make changes to rule files
# backend/rules/cardiology.yml
# CHANGELOG.md

# Commit with clear message
git commit -m "Medical Update: Cardiology - AFib per 2025 AHA/ACC Guidelines

- Updated CHA₂DS₂-VASc recommendations
- Modified anticoagulation protocols
- Added DOAC preference statements
- Clinical Reviewer: Dr. John Smith, MD (Board Certified Cardiologist)
- Evidence Level: A
- Source: 2025 AHA/ACC/ACCP/HRS AFib Guidelines"

# Push and create PR
git push origin medical-update/cardiology-afib-2025
```

### PR Labels
- `medical-update`: All clinical content changes
- `critical-safety`: Urgent safety-related updates
- `guideline-update`: Routine guideline updates
- `evidence-level-A/B/C`: Evidence quality indicator

---

## 📚 Resources

### Internal Documentation
- `MEDICAL_KNOWLEDGE_STATUS.md`: Current coverage overview
- `CONTRIBUTING.md`: General contribution guidelines
- `backend/rules/README.md`: Rule file structure
- `backend/trees/README.md`: Decision tree syntax

### External Resources
- [UpToDate](https://www.uptodate.com/)
- [Cochrane Library](https://www.cochranelibrary.com/)
- [NICE Guidelines](https://www.nice.org.uk/guidance)
- [Guidelines.gov](https://www.guidelines.gov/) (archived reference)
- [PubMed](https://pubmed.ncbi.nlm.nih.gov/)

### Guideline Aggregators
- [Agency for Healthcare Research and Quality (AHRQ)](https://www.ahrq.gov/)
- [National Guideline Clearinghouse](https://www.ahrq.gov/gam/index.html)

---

## ⚠️ Legal & Compliance

### Medical Disclaimer
All rules must maintain appropriate disclaimers:
- Not a substitute for professional medical judgment
- For educational purposes only
- Not FDA-approved for clinical decision-making
- Users must verify information with current guidelines

### Liability Protection
- Document all sources and evidence levels
- Maintain audit trail of all updates
- Ensure clinical review process documented
- Keep records of reviewer credentials

### Version Control
- All updates tracked in Git
- Previous versions accessible via Git history
- Ability to roll back if errors discovered

---

## 🎯 Success Criteria

### Short-term (3-6 months)
- [ ] All existing rules have `version`, `last_updated`, and `source` fields
- [ ] Clinical review board established (or external reviewers identified)
- [ ] Validation scripts implemented
- [ ] Quarterly review cycle initiated
- [ ] CHANGELOG maintained

### Medium-term (6-12 months)
- [ ] All rules include evidence levels (A/B/C)
- [ ] All rules have citations
- [ ] Automated alerts for rules >1 year old
- [ ] Update dashboard implemented
- [ ] User notification system for major updates

### Long-term (12-24 months)
- [ ] Average rule age <6 months
- [ ] 100% citation coverage
- [ ] Automated guideline monitoring system
- [ ] API versioning for medical content
- [ ] Integration with clinical guideline APIs (if available)

---

## 📞 Contact

For questions about the medical update process:
- Create an issue: [GitHub Issues](https://github.com/bevroy/RealDiag-Software/issues)
- Tag: `@clinical-review-team` (once established)
- Email: medical-updates@realdiag.com (if established)

---

**Document Version**: 1.0.0  
**Last Updated**: November 19, 2025  
**Next Review**: February 19, 2026  
**Owner**: Medical Informatics Lead / Clinical Review Board
