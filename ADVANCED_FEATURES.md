# Advanced Clinical Decision Support Features

## Overview
Comprehensive suite of advanced clinical decision support tools integrated into the RealDiag diagnostic platform. These features transform the system from a good diagnostic tool into an exceptional clinical decision support system.

## Implementation Date
November 18, 2025

---

## 1. Pretest Probability Calculators 🧮

### Purpose
Integrate validated clinical scores to support diagnostic decisions with evidence-based risk stratification.

### Available Calculators

#### Cardiovascular
- **Wells Score (DVT)** - Deep vein thrombosis probability
- **Wells Score (PE)** - Pulmonary embolism probability
- **PERC Rule** - PE rule-out criteria for low-risk patients
- **HEART Score** - Chest pain risk stratification (MACE prediction)
- **CHA₂DS₂-VASc** - Stroke risk in atrial fibrillation
- **HAS-BLED** - Bleeding risk with anticoagulation
- **CHADS₂** - Simplified stroke risk in AFib

#### Pulmonology
- **CURB-65** - Pneumonia severity assessment

#### Infectious Disease
- **Centor/McIsaac Score** - Strep pharyngitis probability

#### Orthopedics
- **Ottawa Ankle Rules** - Determine need for ankle X-ray

### Features
- Complete calculation logic with point scoring
- Risk stratification (Low/Moderate/High)
- Probability percentages
- Clinical interpretation and recommendations
- Easy-to-use UI with calculator selection grid

### Location
- `frontend/utils/pretestCalculators.js` - Calculation logic
- Symptom search page - Calculator selection interface

---

## 2. Drug Interactions Checker 💊

### Purpose
Cross-reference medications in management recommendations with known drug interactions to prevent adverse events.

### Coverage
Over 50+ medications across categories:
- Anticoagulants (warfarin, DOACs)
- Antiplatelets (aspirin, clopidogrel)
- Antibiotics (azithromycin, ciprofloxacin)
- Cardiovascular (beta-blockers, calcium channel blockers)
- Statins
- Diabetes medications
- PPIs
- Antidepressants (SSRIs)

### Interaction Details
Each interaction includes:
- **Severity level**: Major, Moderate, Minor
- **Clinical effect**: Description of the interaction
- **Alternative medications**: Safer options
- **Monitoring recommendations**: What to watch for

### Visual Indicators
- 🚨 Red for major interactions
- ⚡ Orange for moderate interactions
- ℹ️ Blue for minor interactions

### Features
- Automatic extraction of medications from management text
- Color-coded severity badges
- Expandable interaction details
- Alternative medication suggestions
- Monitoring guidelines

### Location
- `frontend/utils/drugInteractions.js` - Interaction database and logic
- Appears in diagnosis cards when management contains interacting medications

---

## 3. Cost-Effectiveness Analysis Engine 💰

### Purpose
Show cheapest/fastest diagnostic pathways to support value-based decision making.

### Pathway Analysis
Compares multiple diagnostic approaches for conditions including:
- Pulmonary embolism
- Deep vein thrombosis
- Acute coronary syndrome
- Stroke/TIA
- Pneumonia
- Appendicitis

### Metrics Tracked
- **Total Cost**: Approximate US dollars for all tests
- **Time to Diagnosis**: Hours/days from initial evaluation
- **Sensitivity**: Diagnostic accuracy (true positive rate)
- **Specificity**: Diagnostic accuracy (true negative rate)
- **Cost Efficiency**: Cost per % sensitivity

### Pathway Recommendations
Automatically identifies:
- 💰 **Cheapest pathway** - Lowest total cost
- ⚡ **Fastest pathway** - Shortest time to diagnosis
- 🎯 **Most efficient pathway** - Best cost-per-sensitivity ratio

### Test Cost Database
Includes ~40+ diagnostic tests:
- Laboratory tests (CBC, troponin, D-dimer, etc.)
- Imaging (X-ray, CT, MRI, ultrasound)
- Procedures (ECG, endoscopy, stress tests)
- Specialist consultations

### Features
- Side-by-side pathway comparison
- Visual badges for optimal pathways
- Detailed test breakdown with timing
- Clinical notes for each pathway

### Location
- `frontend/utils/costEffectiveness.js` - Analysis engine
- Appears in diagnosis cards as expandable section

---

## 4. Differential Diagnosis Comparison Tool 🔬

### Purpose
Side-by-side test characteristics for competing diagnoses to aid in diagnostic differentiation.

### Calculations
- **Likelihood Ratios (LR+, LR-)**: Pre/post-test probability
- **Youden's Index**: Overall test performance
- **Accuracy**: Average of sensitivity and specificity

### Comparison Features
- **Test Characteristics**: Sensitivity, specificity, LR+, LR-
- **Distinguishing Features**: Unique symptoms/findings per diagnosis
- **Common Features**: Overlapping presentations
- **Diagnostic Difficulty Score**: Ease of diagnosis rating
- **Confidence Assessment**: Based on available tests

### Interpretation
- LR+ >10: Large increase in probability
- LR+ 5-10: Moderate increase
- LR+ 2-5: Small increase
- LR- <0.1: Large decrease in probability
- LR- 0.1-0.2: Moderate decrease
- LR- 0.2-0.5: Small decrease

### Features
- Comparison tables for multiple diagnoses
- Color-coded likelihood ratio interpretations
- Gold standard test identification
- Confidence level calculations

### Location
- `frontend/utils/differentialComparison.js` - Comparison logic
- Can be used for advanced differential diagnosis views (future enhancement)

---

## 5. Red Flag Alert System 🚨

### Purpose
Automatically highlight life-threatening conditions requiring immediate action.

### Severity Levels

#### Critical (Red) 🚨
Life-threatening, requires immediate intervention:
- STEMI
- Aortic dissection
- Cardiac tamponade
- Tension pneumothorax
- Hemorrhagic stroke
- Bacterial meningitis
- Status epilepticus
- Septic shock
- Necrotizing fasciitis
- Anaphylaxis
- Massive pulmonary embolism

#### High (Orange) ⚠️
Urgent, significant morbidity if delayed:
- Testicular torsion
- Acute angle-closure glaucoma
- Upper GI bleed
- Perforated viscus

### Alert Information
Each red flag includes:
- **Time window**: Critical treatment timeframe
- **Mortality data**: Outcome if untreated
- **Critical actions**: Step-by-step immediate interventions
- **Visual alerts**: Pulsing animations for critical conditions

### Features
- Automatic keyword detection
- Priority-based sorting (critical first)
- Expandable action checklists
- Color-coded severity badges
- Pulsing animations for critical alerts

### Location
- `frontend/utils/redFlagAlerts.js` - Alert database and detection
- Prominently displayed at top of diagnosis card details

---

## 6. Time-Sensitive Urgency Alerts ⏰

### Purpose
Flag diagnoses requiring immediate action with specific time windows and treatment milestones.

### Urgency Levels

#### IMMEDIATE (< 15 minutes) 🚨
- Cardiac arrest
- Anaphylaxis
- Tension pneumothorax

#### EMERGENT (< 1 hour) ⚡
- STEMI (door-to-balloon < 90 min)
- Ischemic stroke (tPA < 4.5 hours)
- Septic shock
- Bacterial meningitis
- Aortic dissection

#### URGENT (< 6 hours) ⏰
- Testicular torsion
- Retinal artery occlusion
- Ruptured ectopic pregnancy
- Necrotizing fasciitis
- Compartment syndrome

#### SEMI-URGENT (< 24 hours) ⏱️
- Acute angle-closure glaucoma
- Appendicitis
- Bowel obstruction
- Acute cholecystitis

#### ROUTINE (< 1 week) 📋
- Non-urgent conditions

### Timeline Features
Treatment milestones for time-critical conditions:
```
STEMI Example:
├─ 10 min: ECG obtained
├─ 30 min: Cath lab activated
└─ 90 min: Balloon inflation (target)

Stroke Example:
├─ 10 min: Stroke team activated
├─ 25 min: CT completed
├─ 45 min: tPA bolus (if indicated)
└─ 6 hours: Thrombectomy window
```

### Features
- Color-coded urgency badges
- Time window displays
- Outcome-with-delay information
- Step-by-step critical actions
- Treatment milestone tracking

### Location
- `frontend/utils/timeSensitiveAlerts.js` - Urgency classification
- Displayed prominently in diagnosis card when time-sensitive

---

## UI Integration

### Symptom Search Page Enhancements

#### 1. Clinical Calculator Section
- Appears above search results when diagnoses are found
- Grid layout of available calculators by category
- Click to select and use calculator
- Expandable results panel

#### 2. Diagnosis Card Enhancements
Each diagnosis card now includes expandable sections for:

**Red Flag Alerts** (if applicable)
- Pulsing red border for critical conditions
- Emergency alert banner
- Critical action checklist
- Time window and mortality data

**Urgency Alerts** (if applicable)
- Color-coded urgency badge
- Time-to-treatment requirements
- Treatment milestones
- Outcome-with-delay information

**Drug Interactions** (if applicable)
- Automatic detection from management plan
- Severity-coded interaction cards
- Alternative medications
- Monitoring recommendations

**Cost-Effectiveness** (if applicable)
- Diagnostic pathway comparison
- Cost, time, and accuracy metrics
- Optimal pathway recommendations
- Detailed test breakdowns

### Visual Design
- Consistent color coding across all features
- Expandable/collapsible sections to reduce clutter
- Icon system for quick recognition
- Responsive layout for mobile devices

---

## Technical Implementation

### File Structure
```
frontend/
├── utils/
│   ├── pretestCalculators.js      (10 calculators, 460 lines)
│   ├── drugInteractions.js        (50+ drugs, 380 lines)
│   ├── costEffectiveness.js       (6 conditions, 480 lines)
│   ├── differentialComparison.js  (comparison logic, 380 lines)
│   ├── redFlagAlerts.js          (25 conditions, 420 lines)
│   └── timeSensitiveAlerts.js    (30 conditions, 480 lines)
├── pages/
│   └── symptom-search.js         (enhanced with all features)
```

### Bundle Size
- Symptom search page: 29.5 kB (up from 15.7 kB)
- New utilities: ~2,600 lines of code
- Total features: 6 major systems

### Performance
- Lazy loading via expandable sections
- Client-side calculations (no API calls)
- Instant interaction detection
- Cached results per diagnosis

---

## Future Enhancements

### Planned Additions
1. **Interactive Calculator Forms**
   - Full input forms for each calculator
   - Real-time score updates
   - Save/print calculator results

2. **Comparison View**
   - Side-by-side diagnosis comparison tables
   - Distinguishing features highlighting
   - Test recommendation priorities

3. **YAML Rule Enhancements**
   - Add cost data to diagnostic tests
   - Include drug interaction flags
   - Mark red flag conditions
   - Specify urgency levels

4. **Additional Calculators**
   - APACHE II/III (ICU mortality)
   - Glasgow Coma Scale
   - NIHSS (stroke severity)
   - SOFA score (organ failure)
   - qSOFA (sepsis screening)

5. **Personalization**
   - Patient medication list input
   - Institution-specific costs
   - Preferred diagnostic pathways
   - Custom alerts and thresholds

---

## Clinical Impact

### Benefits
1. **Safety**: Red flag alerts prevent missed life-threatening conditions
2. **Efficiency**: Cost analysis supports value-based care
3. **Quality**: Evidence-based calculators improve decision accuracy
4. **Education**: Clinical pearls and management guidance
5. **Compliance**: Time-sensitive alerts ensure timely interventions

### Use Cases
- **Emergency Department**: Rapid triage and risk stratification
- **Primary Care**: Comprehensive diagnostic workup planning
- **Urgent Care**: Decision support for borderline admissions
- **Telemedicine**: Remote clinical decision support
- **Medical Education**: Teaching tool for residents/students

---

## Validation & Evidence Base

All clinical decision tools are based on published, validated scoring systems:
- Wells scores (validated for DVT/PE)
- HEART score (validated for chest pain)
- CURB-65 (validated for pneumonia)
- CHA₂DS₂-VASc (ACC/AHA guidelines)
- Drug interactions (FDA/clinical pharmacology databases)
- Cost data (Medicare/commercial insurance averages)

---

## Deployment Status

✅ **Completed**: All 6 features implemented and integrated  
✅ **Built**: Static export generated (November 18, 2025)  
✅ **Deployed**: Pushed to GitHub for Netlify deployment  
🔄 **Bundle**: symptom-search-3cb83b2772be2c83.js  

### Access
- Production: https://realdiag.netlify.app/symptom-search
- Feature Branch: main (commit b6ef971)

---

## Conclusion

The RealDiag platform now includes comprehensive advanced clinical decision support features that elevate it from a diagnostic tool to a complete clinical decision support system. These features address critical needs for safety, efficiency, and quality in clinical practice while maintaining an intuitive, user-friendly interface.

The modular implementation allows for easy maintenance and future enhancements, with each feature operating independently but integrating seamlessly into the user experience.
