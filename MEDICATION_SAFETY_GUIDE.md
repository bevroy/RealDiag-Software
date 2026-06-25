# Medication Safety Integration - User Guide

## 🎯 Overview

RealDiag now includes **comprehensive medication safety checking** integrated into the diagnostic process. The system automatically:

✅ **Detects drug-drug interactions**  
✅ **Identifies contraindications** (medications unsafe for patient's conditions)  
✅ **Alerts to allergen cross-reactivity**  
✅ **Flags duplicate therapy**  
✅ **Provides age-specific warnings** (Beers Criteria for elderly)  
✅ **Recommends renal/hepatic dose adjustments**  
✅ **Warns about pregnancy risks**

---

## 🚨 Why Medication Safety Matters

### Real-World Scenarios

**Scenario 1: Warfarin + NSAIDs**
- Patient on warfarin for atrial fibrillation
- Presents with knee pain, considers ibuprofen
- **❌ Risk**: Major bleeding risk, GI hemorrhage
- **✅ Alert**: "Use acetaminophen instead"

**Scenario 2: Metoprolol + Asthma**
- Patient with asthma and hypertension
- Cardiologist prescribes metoprolol
- **❌ Risk**: Bronchospasm, severe asthma exacerbation
- **✅ Alert**: "Contraindicated - use amlodipine"

**Scenario 3: Penicillin Allergy**
- Patient allergic to penicillin (anaphylaxis history)
- ED considers cephalexin for cellulitis
- **❌ Risk**: Cross-reactivity, possible anaphylaxis
- **✅ Alert**: "5-10% cross-reactivity - use azithromycin"

---

## 📋 How It Works

### 1. **Automatic Integration**

When you evaluate a patient, medication safety is checked automatically:

```python
# Diagnostic evaluation includes medication check
POST /diagnostic/evaluate/CARDS-ACUTE-CORONARY-SYNDROME
{
  "symptoms": ["chest pain"],
  "current_medications": ["warfarin", "aspirin"],  // ← Automatically checked
  "conditions": ["atrial fibrillation"],
  "allergies": ["penicillin"],
  "age": 75
}

# Response includes medication alerts
{
  "tree_result": {...},
  "medication_safety": {
    "alerts": [...],
    "safety_score": 70,
    "summary": "⚠️ Moderate safety concerns"
  },
  "critical_warnings": [
    "🚫 CONTRAINDICATED: metoprolol (asthma)"
  ]
}
```

### 2. **Manual Entry Integration**

When using manual patient history entry (`/patient-history`):

1. **Enter current medications** in the Medications section
2. **Enter allergies** in the Allergies section
3. **Enter active conditions** in the Conditions section
4. **Save patient history**

When diagnostic evaluation runs, the system:
- Pulls current medications from patient history
- Checks against recommended treatments
- Flags interactions, contraindications, and allergen risks

### 3. **Standalone Medication Safety Check**

For focused medication reconciliation:

```bash
POST /diagnostic/medication-safety-check
{
  "current_medications": ["warfarin", "aspirin"],
  "proposed_medications": ["ibuprofen"],
  "patient_conditions": ["atrial fibrillation", "asthma"],
  "patient_allergies": ["penicillin"],
  "age": 75,
  "renal_function": "moderate"
}
```

---

## 🔍 Types of Alerts

### 1. Drug-Drug Interactions

**Severity Levels:**
- 🚫 **Contraindicated**: Never use together
- ⚠️ **Major**: Serious, requires intervention
- ⚡ **Moderate**: Monitor closely
- ℹ️ **Minor**: Usually not clinically significant

**Examples:**

| Interaction | Severity | Effect | Recommendation |
|-------------|----------|--------|----------------|
| Warfarin + Aspirin | Major | Bleeding risk | Use clopidogrel instead |
| Warfarin + NSAIDs | Major | GI bleeding | Use acetaminophen |
| Simvastatin + Gemfibrozil | Contraindicated | Rhabdomyolysis | Use fenofibrate |
| Metoprolol + Diltiazem | Major | Bradycardia | Avoid or monitor closely |
| Clopidogrel + Omeprazole | Moderate | Reduced efficacy | Use pantoprazole |

### 2. Contraindications (Medication + Condition)

Medications that are **unsafe** for specific medical conditions:

| Medication | Condition | Risk | Alternative |
|------------|-----------|------|-------------|
| Metoprolol | Asthma | Bronchospasm | Amlodipine, diltiazem |
| NSAIDs | Kidney disease | Acute kidney injury | Acetaminophen |
| NSAIDs | Heart failure | Fluid retention | Acetaminophen |
| Metformin | Kidney disease (eGFR <30) | Lactic acidosis | Insulin |
| Diphenhydramine | Glaucoma | Acute angle-closure | Cetirizine, loratadine |

### 3. Allergen Cross-Reactivity

**Penicillin Allergies:**
- ✅ **Amoxicillin**: 100% cross-reactivity (same class) → **Avoid**
- ⚠️ **Cephalexin**: 5-10% cross-reactivity → **Avoid if severe allergy**
- ✅ **Azithromycin**: No cross-reactivity → **Safe alternative**

**Sulfa Allergies:**
- ✅ **Bactrim**: Direct sulfonamide → **Avoid**
- ⚠️ **Furosemide**: Low risk (different structure) → **Usually safe**

**Aspirin/NSAID Allergies:**
- ✅ **All NSAIDs**: High cross-reactivity → **Avoid all**
- ✅ **Acetaminophen**: No cross-reactivity → **Safe**

### 4. Duplicate Therapy

Multiple medications from the **same drug class**:

**Examples:**
- 2 beta blockers (metoprolol + atenolol)
- 2 statins (atorvastatin + simvastatin)
- 2 PPIs (omeprazole + pantoprazole)
- 2 anticoagulants (warfarin + apixaban)

**Risk**: Increased adverse effects, no added benefit

**Recommendation**: Use only one medication from the class

### 5. Age-Specific Warnings

**Elderly (≥65 years) - Beers Criteria:**

| Medication | Risk | Alternative |
|------------|------|-------------|
| Diphenhydramine | Confusion, falls, urinary retention | Cetirizine, loratadine |
| Amitriptyline | Anticholinergic effects, sedation | Sertraline, citalopram |
| NSAIDs | GI bleeding, kidney injury | Acetaminophen (short course) |

**Pediatric (<18 years):**

| Medication | Risk | Alternative |
|------------|------|-------------|
| Aspirin | Reye's syndrome | Acetaminophen, ibuprofen |
| Fluoroquinolones | Cartilage damage | Amoxicillin, azithromycin |

### 6. Renal Adjustments

**Medications requiring dose adjustment in kidney disease:**

| Medication | eGFR | Adjustment |
|------------|------|------------|
| Metformin | <30 | Avoid (lactic acidosis risk) |
| Metformin | 30-45 | Reduce dose by 50% |
| Enoxaparin | <30 | Reduce dose by 50% |
| Gabapentin | <60 | Reduce dose by 50% |

### 7. Hepatic Adjustments

**Medications requiring adjustment in liver disease:**

| Medication | Condition | Adjustment |
|------------|-----------|------------|
| Warfarin | Cirrhosis | Reduce dose, monitor INR closely |
| Statins | Active liver disease | Avoid, monitor LFTs |

### 8. Pregnancy Warnings

**Contraindicated medications:**

| Medication | Risk | Alternative |
|------------|------|-------------|
| Warfarin | Fetal warfarin syndrome | Enoxaparin, heparin |
| ACE inhibitors | Fetal renal dysfunction | Labetalol, nifedipine |
| Statins | Possible teratogenicity | Discontinue |

---

## 💊 Using Current Medications in Diagnosis

### Manual Entry Workflow

**Step 1: Enter Patient History**
1. Navigate to `/patient-history`
2. Enter patient demographics
3. **Add current medications:**
   - Click "+ Add Medication"
   - Select from dropdown (20 common medications)
   - Enter dosage: "20mg once daily"
   - Status: Active
   - Date prescribed

**Step 2: Enter Allergies**
1. Navigate to Allergies section
2. **Add allergies:**
   - Click "+ Add Allergy"
   - Select allergen: "Penicillin"
   - Select reaction: "Rash", "Hives", "Anaphylaxis"

**Step 3: Enter Active Conditions**
1. Navigate to Conditions section
2. **Add conditions:**
   - Click "+ Add Condition"
   - Select condition: "Hypertension", "Asthma", "Kidney disease"
   - Status: Active
   - Onset date

**Step 4: Save History**
- Click "💾 Save Patient History"

**Step 5: Run Diagnostic Evaluation**
- Diagnostic engine automatically pulls medications, allergies, conditions
- Medication safety check runs in background
- Alerts displayed with diagnostic results

---

## 📊 Medication Safety Score

**Scale: 0-100** (higher = safer)

| Score | Interpretation | Action |
|-------|----------------|--------|
| **90-100** | ✅ No significant concerns | Proceed with treatment |
| **70-89** | ⚠️ Minor concerns | Monitor as recommended |
| **50-69** | ⚠️ Moderate concerns | Review alternatives |
| **<50** | 🚫 Major concerns | Contraindications identified - do not proceed |

**Score Calculation:**
- **-30 points**: Contraindicated medication
- **-15 points**: Major interaction
- **-5 points**: Moderate interaction
- **-2 points**: Minor interaction

---

## 🔧 API Usage

### Endpoint 1: Integrated with Diagnostic Evaluation

```bash
POST /diagnostic/evaluate/CARDS-ACUTE-CORONARY-SYNDROME
Content-Type: application/json

{
  "symptoms": ["chest pain", "dyspnea"],
  "current_medications": ["aspirin", "atorvastatin", "lisinopril"],
  "conditions": ["hypertension", "hyperlipidemia"],
  "allergies": ["penicillin"],
  "age": 65,
  "renal_function": "normal"
}
```

**Response:**
```json
{
  "tree_result": {
    "diagnosis": "Acute Coronary Syndrome",
    "tests": ["ECG", "Troponin"],
    "management": ["Aspirin 325mg", "Heparin", "Cardiology consult"]
  },
  "medication_safety": {
    "alerts": [
      {
        "alert_type": "drug_interaction",
        "severity": "moderate",
        "medication": "aspirin",
        "description": "Patient already on aspirin 81mg daily",
        "recommendation": "Verify current dose before giving additional aspirin"
      }
    ],
    "safety_score": 95,
    "summary": "✅ No significant safety concerns identified"
  }
}
```

### Endpoint 2: Standalone Medication Safety Check

```bash
POST /diagnostic/medication-safety-check
Content-Type: application/json

{
  "current_medications": ["warfarin", "aspirin", "metoprolol"],
  "proposed_medications": ["ibuprofen"],
  "patient_conditions": ["atrial fibrillation", "asthma"],
  "patient_allergies": ["penicillin"],
  "age": 75,
  "renal_function": "moderate",
  "hepatic_function": "normal",
  "pregnancy": false
}
```

**Response:**
```json
{
  "alerts": [
    {
      "alert_type": "drug_interaction",
      "severity": "major",
      "medication": "warfarin",
      "interacting_medication": "ibuprofen",
      "description": "Interaction between warfarin and ibuprofen",
      "clinical_effect": "Increased bleeding risk, GI bleeding",
      "recommendation": "Use acetaminophen for pain instead",
      "monitoring": "Monitor for bleeding, especially GI",
      "alternatives": ["acetaminophen"]
    },
    {
      "alert_type": "contraindication",
      "severity": "contraindicated",
      "medication": "metoprolol",
      "condition": "asthma",
      "description": "metoprolol is contraindicated in asthma",
      "clinical_effect": "Bronchospasm risk, worsening asthma",
      "recommendation": "Avoid beta blockers in asthma - use alternative",
      "alternatives": ["diltiazem", "amlodipine"]
    }
  ],
  "safety_score": 40,
  "summary": "🚫 Major safety concerns - contraindications identified",
  "contraindicated_medications": ["metoprolol"],
  "major_interactions": [
    {
      "medication": "warfarin",
      "interacting_medication": "ibuprofen",
      "clinical_effect": "Increased bleeding risk, GI bleeding",
      "recommendation": "Use acetaminophen for pain instead"
    }
  ],
  "requires_monitoring": ["warfarin", "aspirin"],
  "alternatives_suggested": true
}
```

---

## 🎯 Clinical Use Cases

### Use Case 1: Emergency Department Chest Pain

**Presentation:**
- 65-year-old male with chest pain
- Current medications: Warfarin (for AFib), aspirin 81mg
- Proposed treatment: Aspirin 325mg, heparin, clopidogrel

**Medication Safety Check:**
```json
{
  "alerts": [
    {
      "severity": "major",
      "medication": "warfarin + aspirin + clopidogrel + heparin",
      "clinical_effect": "Extremely high bleeding risk - quadruple therapy",
      "recommendation": "Cardiology consult for anticoagulation management"
    }
  ],
  "safety_score": 55
}
```

**Clinical Decision:**
- Hold warfarin
- Continue aspirin 81mg (not 325mg)
- Add clopidogrel 300mg load
- Consider anticoagulation bridge with heparin
- Cardiology consult STAT

---

### Use Case 2: Primary Care Hypertension

**Presentation:**
- 70-year-old female with hypertension
- Medical history: Asthma, COPD
- Proposed: Metoprolol 50mg BID

**Medication Safety Check:**
```json
{
  "alerts": [
    {
      "severity": "contraindicated",
      "medication": "metoprolol",
      "condition": "asthma",
      "clinical_effect": "Bronchospasm risk, severe asthma exacerbation",
      "recommendation": "Avoid beta blockers - use calcium channel blocker",
      "alternatives": ["amlodipine", "diltiazem"]
    }
  ],
  "safety_score": 30
}
```

**Clinical Decision:**
- ❌ Do not prescribe metoprolol
- ✅ Use amlodipine 5mg daily instead
- Monitor BP and respiratory status

---

### Use Case 3: Post-Op Infection

**Presentation:**
- 35-year-old female with surgical site infection
- Allergies: Penicillin (rash), sulfa (hives)
- Proposed: Bactrim or amoxicillin

**Medication Safety Check:**
```json
{
  "alerts": [
    {
      "severity": "contraindicated",
      "medication": "amoxicillin",
      "allergen": "penicillin",
      "clinical_effect": "100% cross-reactivity - same drug class",
      "recommendation": "Avoid all penicillins",
      "alternatives": ["azithromycin", "doxycycline"]
    },
    {
      "severity": "contraindicated",
      "medication": "bactrim",
      "allergen": "sulfa",
      "clinical_effect": "Direct sulfonamide allergy",
      "recommendation": "Contraindicated in sulfa allergy",
      "alternatives": ["doxycycline", "fluoroquinolone"]
    }
  ],
  "safety_score": 10
}
```

**Clinical Decision:**
- ❌ Neither amoxicillin nor Bactrim safe
- ✅ Use doxycycline 100mg BID
- Alternative: Fluoroquinolone if severe

---

## 📈 Benefits

### Patient Safety
- ✅ **Prevents adverse drug events**
- ✅ **Reduces medication errors**
- ✅ **Identifies allergen risks**
- ✅ **Catches dangerous combinations**

### Clinical Efficiency
- ✅ **Automatic checking** (no manual lookup)
- ✅ **Real-time alerts** during prescribing
- ✅ **Alternative suggestions** provided
- ✅ **Monitoring recommendations** included

### Medicolegal Protection
- ✅ **Documented safety checks**
- ✅ **Evidence of due diligence**
- ✅ **Reduced liability risk**
- ✅ **Audit trail maintained**

---

## 🔒 Privacy & Compliance

- ✅ All medication data stays within your RealDiag instance
- ✅ HIPAA-compliant processing
- ✅ No external API calls for safety checking
- ✅ Audit logging of all safety alerts
- ✅ User authentication required

---

## 📚 Resources

### Drug Interaction Databases
- Built-in database: 50+ common interactions
- Severity classifications: Contraindicated, Major, Moderate, Minor
- Evidence-based recommendations
- Alternative medication suggestions

### Contraindication Database
- Condition-specific contraindications
- Beers Criteria for elderly
- Pediatric warnings
- Pregnancy categories

### Allergen Cross-Reactivity
- Penicillin/cephalosporin cross-reactivity
- Sulfa drug relationships
- NSAID/aspirin allergies
- Food-drug cross-reactions

---

## 🚀 Future Enhancements

### Planned Features
- [ ] **Expanded drug database** (500+ medications)
- [ ] **Therapeutic drug monitoring** (vancomycin, digoxin levels)
- [ ] **Drug-food interactions** (grapefruit, vitamin K)
- [ ] **Genetic testing integration** (CYP450 polymorphisms)
- [ ] **Real-time formulary checking** (insurance coverage)
- [ ] **Automatic alternative ranking** (efficacy + safety)
- [ ] **Patient-specific risk scoring** (CHADS2, HAS-BLED)
- [ ] **Deprescribing recommendations** (polypharmacy optimization)

---

## 🆘 Troubleshooting

**Q: Alert not showing for known interaction?**
- **A:** Check medication name spelling/format. Database uses generic names (e.g., "ibuprofen" not "Motrin")

**Q: Too many false-positive alerts?**
- **A:** Adjust severity threshold in settings. Start with "Major" and "Contraindicated" only.

**Q: Missing patient's current medications?**
- **A:** Ensure medications entered in manual history form or passed in API call as `current_medications` array

**Q: Allergen cross-reactivity not detected?**
- **A:** Verify allergy name matches database (e.g., "penicillin" not "penicillin allergy")

---

## 📞 Support

For questions or issues:
- **Documentation**: MEDICATION_SAFETY_GUIDE.md (this file)
- **API Docs**: `/docs` endpoint (FastAPI Swagger)
- **GitHub Issues**: https://github.com/bevroy/RealDiag-Software/issues

---

**Version:** 1.0.0  
**Last Updated:** December 2025  
**Status:** ✅ Production Ready
