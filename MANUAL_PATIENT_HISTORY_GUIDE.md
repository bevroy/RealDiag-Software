# Manual Patient History Entry - User Guide

## Overview

For **non-EMR instances** where electronic health record integration is not available, RealDiag provides a comprehensive **manual patient history entry system** with dropdown lists and structured forms.

This enables clinicians to enter the same comprehensive patient data that would normally be pulled from an EMR, ensuring diagnostic decision support has complete clinical context.

---

## 🎯 Key Features

### Structured Data Entry with Dropdown Lists

All major fields use **dropdown lists** populated with common clinical values, making data entry:
- ✅ **Fast** - Select from common options rather than typing
- ✅ **Standardized** - Consistent terminology across entries
- ✅ **Accurate** - Reduces spelling errors and variations
- ✅ **Complete** - Comprehensive lists of common clinical values

### 10 Comprehensive Sections

1. **👤 Demographics** - Patient identification and basic info
2. **📋 Visit Notes** - Clinical documentation from encounters
3. **🧪 Diagnostic Tests** - Lab results and diagnostic procedures
4. **📝 H&P** - Complete History & Physical examinations
5. **🔬 Procedures** - Surgical and interventional procedures
6. **🏥 Imaging** - CT, MRI, X-Ray, Ultrasound studies
7. **📊 Conditions** - Active and resolved medical conditions
8. **💊 Medications** - Current and historical medications
9. **⚠️ Allergies** - Drug and food allergies with reactions
10. **👨‍👩‍👧 Family/Social History** - Hereditary and lifestyle factors

---

## 📋 How to Use

### Step 1: Access the Manual Entry Interface

Navigate to: **`/patient-history`** in your RealDiag instance

Or use the main menu: **Patient History → Manual Entry**

### Step 2: Navigate Sections

Click on any section button to jump to that data entry area:

```
👤 Demographics  📋 Visit Notes  🧪 Diagnostic Tests  📝 H&P  🔬 Procedures
🏥 Imaging  📊 Conditions  💊 Medications  ⚠️ Allergies  👨‍👩‍👧 History
```

Each section highlights when active, providing visual navigation feedback.

### Step 3: Enter Demographics

**Required fields:**
- Patient ID / MRN
- Patient Name
- Age
- Gender (dropdown: Male, Female, Other, Unknown)

This establishes the patient identity for all subsequent data.

### Step 4: Add Clinical Data

Each section has an **"+ Add"** button to create new entries:

#### Visit Notes
- Click **"+ Add Visit Note"**
- Select **Note Type** from dropdown:
  - Progress Note
  - Consultation Note
  - Admission Note
  - Discharge Summary
  - Emergency Department Note
  - Procedure Note
  - Follow-up Note
  - Referral Note
- Select **Specialty** from dropdown (14 specialties available)
- Enter author name
- Enter clinical note content

#### Diagnostic Tests
- Click **"+ Add Test"**
- Select **Test Name** from dropdown (20 common lab tests):
  - Complete Blood Count (CBC)
  - Basic Metabolic Panel (BMP)
  - Comprehensive Metabolic Panel (CMP)
  - Liver Function Tests (LFTs)
  - Troponin I/T
  - BNP/NT-proBNP
  - Hemoglobin A1c
  - *...and more*
- Select **Test Type** (Laboratory, Pathology, Genetic, etc.)
- Enter result value
- Check **Abnormal** or **Critical** if applicable
- Enter interpretation

#### History & Physical (H&P)
- Click **"+ Add H&P"**
- Complete structured H&P fields:
  - **Chief Complaint** - Primary reason for visit
  - **HPI** - History of present illness
  - **ROS** - Review of systems
  - **Physical Exam** - Examination findings
  - **Assessment** - Clinical impression
  - **Plan** - Treatment plan

#### Procedures
- Click **"+ Add Procedure"**
- Enter procedure name
- Enter operator/surgeon name
- Describe indication, outcome, and complications

#### Imaging Studies
- Click **"+ Add Imaging"**
- Select **Modality** from dropdown:
  - X-Ray
  - CT Scan
  - MRI
  - Ultrasound
  - PET Scan
  - Echocardiography
  - *...and more*
- Select **Body Site** from dropdown (13 anatomical regions)
- Enter findings and radiologist impression

#### Medical Conditions
- Click **"+ Add Condition"**
- Select **Condition** from dropdown (25 common conditions):
  - Hypertension
  - Type 2 Diabetes Mellitus
  - Coronary Artery Disease
  - Heart Failure
  - Atrial Fibrillation
  - COPD
  - Asthma
  - *...and more*
- Select **Status** (Active, Resolved, Inactive)
- Enter recorded date and onset date

#### Medications
- Click **"+ Add Medication"**
- Select **Medication Name** from dropdown (20 common medications):
  - Aspirin
  - Atorvastatin
  - Lisinopril
  - Metformin
  - Metoprolol
  - Levothyroxine
  - *...and more*
- Enter dosage (e.g., "20mg once daily")
- Select status (Active, Stopped, Completed)
- Enter date prescribed

#### Allergies
- Click **"+ Add Allergy"**
- Select **Allergen** from dropdown (16 common allergens):
  - Penicillin
  - Sulfa drugs
  - Aspirin
  - NSAIDs
  - Shellfish
  - Peanuts
  - Latex
  - *...and more*
- Select **Reaction** from dropdown:
  - Rash
  - Hives
  - Anaphylaxis
  - Swelling
  - Difficulty breathing
  - *...and more*

#### Family/Social History
- Enter **Family History** (free text):
  - "Father: MI at age 62; Mother: Type 2 diabetes"
- Enter **Social History** (free text):
  - "Former smoker (quit 2020, 20 pack-year history); Occasional alcohol"

### Step 5: Remove Entries

Each entry card has a **"✕"** button in the top-right corner to remove that entry if needed.

### Step 6: Save Patient History

Click the large **"💾 Save Patient History"** button at the bottom.

You'll see a success message: **"✓ Patient history saved successfully!"**

---

## 🔍 Dropdown Lists Reference

### Visit Note Types (8 options)
```
Progress Note
Consultation Note
Admission Note
Discharge Summary
Emergency Department Note
Procedure Note
Follow-up Note
Referral Note
```

### Medical Specialties (14 options)
```
Cardiology
Neurology
Pulmonology
Gastroenterology
Endocrinology
Nephrology
Rheumatology
Infectious Disease
Hematology/Oncology
Emergency Medicine
Internal Medicine
Family Medicine
Hospitalist
Critical Care
```

### Common Lab Tests (20 options)
```
Complete Blood Count (CBC)
Basic Metabolic Panel (BMP)
Comprehensive Metabolic Panel (CMP)
Liver Function Tests (LFTs)
Lipid Panel
Hemoglobin A1c
TSH (Thyroid)
Troponin I/T
BNP/NT-proBNP
D-Dimer
Prothrombin Time (PT/INR)
Partial Thromboplastin Time (PTT)
Urinalysis
Urine Culture
Blood Culture
C-Reactive Protein (CRP)
Erythrocyte Sedimentation Rate (ESR)
Creatine Kinase (CK/CK-MB)
Arterial Blood Gas (ABG)
Venous Blood Gas (VBG)
```

### Test Types (9 options)
```
Laboratory
Pathology
Genetic
Culture
Serology
Toxicology
Hematology
Chemistry
Microbiology
```

### Imaging Modalities (10 options)
```
X-Ray
CT Scan
MRI
Ultrasound
PET Scan
Nuclear Medicine
Mammography
DEXA Scan
Angiography
Echocardiography
```

### Body Sites (13 options)
```
Head/Brain
Neck
Chest
Abdomen
Pelvis
Spine
Upper Extremity
Lower Extremity
Heart
Lungs
Kidneys
Liver
Pancreas
```

### Common Medical Conditions (25 options)
```
Hypertension
Type 2 Diabetes Mellitus
Type 1 Diabetes Mellitus
Coronary Artery Disease
Heart Failure
Atrial Fibrillation
Chronic Kidney Disease
COPD
Asthma
Hyperlipidemia
Hypothyroidism
Hyperthyroidism
Osteoarthritis
Rheumatoid Arthritis
Depression
Anxiety Disorder
Sleep Apnea
GERD
Chronic Pain
Cancer (Active)
Cancer (History)
Stroke (CVA)
TIA
Deep Vein Thrombosis (DVT)
Pulmonary Embolism (PE)
```

### Common Medications (20 options)
```
Aspirin
Atorvastatin
Lisinopril
Metformin
Metoprolol
Amlodipine
Levothyroxine
Omeprazole
Furosemide
Warfarin
Apixaban
Insulin (various)
Gabapentin
Sertraline
Clopidogrel
Albuterol
Prednisone
Losartan
Pantoprazole
Hydrochlorothiazide
```

### Common Allergens (16 options)
```
Penicillin
Sulfa drugs
Aspirin
NSAIDs
Codeine
Morphine
Latex
Shellfish
Peanuts
Tree nuts
Eggs
Soy
Wheat
Milk/Dairy
Contrast dye
Iodine
```

### Allergy Reactions (9 options)
```
Rash
Hives
Itching
Anaphylaxis
Swelling
Difficulty breathing
Nausea/Vomiting
Diarrhea
Unknown
```

---

## 🔗 API Endpoints

### Save Manual Patient History
```bash
POST /diagnostic/manual-history
Content-Type: application/json

{
  "patient_id": "MRN12345",
  "patient_name": "John Doe",
  "age": "55",
  "gender": "male",
  "visit_notes": [...],
  "diagnostic_tests": [...],
  "history_and_physicals": [...],
  "procedures": [...],
  "imaging_studies": [...],
  "active_conditions": [...],
  "current_medications": [...],
  "allergies": [...],
  "family_history": "...",
  "social_history": "..."
}
```

**Response:**
```json
{
  "patient_id": "MRN12345",
  "patient_name": "John Doe",
  "demographics": {
    "age": "55",
    "gender": "male"
  },
  "data_summary": {
    "visit_notes_count": 3,
    "diagnostic_tests_count": 12,
    "abnormal_tests_count": 4,
    "critical_tests_count": 0,
    "h_and_p_count": 1,
    "procedures_count": 2,
    "imaging_studies_count": 3,
    "active_conditions_count": 5,
    "current_medications_count": 8,
    "allergies_count": 2
  },
  "message": "Patient history saved successfully"
}
```

### Retrieve Manual Patient History
```bash
GET /diagnostic/manual-history/{patient_id}
```

**Response:**
- Same format as EMR comprehensive history
- Includes all entered data organized by section
- Compatible with diagnostic decision support engine

### List All Manual Patient Histories
```bash
GET /diagnostic/manual-history/list/all
```

**Response:**
```json
{
  "total_patients": 15,
  "patients": [
    {
      "patient_id": "MRN12345",
      "patient_name": "John Doe",
      "age": "55",
      "gender": "male",
      "data_summary": {
        "visit_notes": 3,
        "tests": 12,
        "conditions": 5,
        "medications": 8,
        "allergies": 2
      }
    }
  ]
}
```

---

## 💡 Best Practices

### Complete Data Entry
- Enter as much historical data as available
- More data = better diagnostic decision support
- Trending lab values over time is especially valuable

### Use Dropdowns When Possible
- Select from dropdown lists rather than custom entry
- Maintains standardization across patients
- Enables better analytics and reporting

### Document Abnormal Findings
- Always check "Abnormal" or "Critical" flags on tests
- Add interpretation notes for context
- Helps diagnostic engine identify concerning patterns

### Structured H&P Documentation
- Use all H&P sections (CC, HPI, ROS, PE, A&P)
- Complete physical exam findings
- Document assessment and plan

### Family History Detail
- Include age at diagnosis for relatives
- Specify relationship (father, mother, sibling)
- Note patterns (e.g., "Strong family history of CAD")

### Social History Specifics
- Quantify tobacco use (pack-years)
- Describe alcohol use frequency
- Note occupational exposures
- Living situation if relevant

---

## 🔄 Integration with Diagnostic Engine

Manual patient history integrates seamlessly with RealDiag's diagnostic decision support:

### 1. **Data Format Compatibility**
Manual entries use the **same data structure** as EMR-pulled comprehensive history, ensuring consistent processing.

### 2. **Diagnostic Evaluation**
When evaluating a patient with manual history:
```javascript
// Frontend: Fetch manual history
const history = await fetch(`/diagnostic/manual-history/${patientId}`)

// Pass to diagnostic evaluation
const evaluation = await fetch(`/diagnostic/evaluate/${treeId}`, {
  method: 'POST',
  body: JSON.stringify({
    ...currentPresentation,
    comprehensive_history: history
  })
})
```

### 3. **Clinical Context**
The diagnostic engine uses manual history for:
- **Trending**: Compare current labs to historical values
- **Risk Stratification**: Factor in comorbidities and family history
- **Medication Reconciliation**: Check for drug interactions
- **Pattern Recognition**: Identify recurrent presentations

### 4. **Decision Support**
Manual history enables the same enhanced decision support as EMR integration:
- Trending analysis (is troponin rising?)
- Comorbidity risk adjustment (chest pain + known CAD = higher risk)
- Baseline comparison (is BP 160/95 new or chronic?)
- Prior workup review (avoid repeating recent tests)

---

## 🎯 Use Cases

### Use Case 1: Rural Clinic Without EMR
**Scenario:** Small rural clinic using paper charts

**Solution:**
1. Review paper chart before patient visit
2. Enter key historical data into RealDiag manual entry
3. Use during patient encounter for diagnostic support
4. Update with new findings after visit

**Benefit:** Paper-based practice gets advanced diagnostic decision support

---

### Use Case 2: Emergency Department - Outside Hospital
**Scenario:** Patient from another hospital presents to ED

**Solution:**
1. Request medical records from previous hospital
2. Enter relevant history manually while waiting for records
3. Use for immediate diagnostic decision support
4. Update when complete records arrive

**Benefit:** Immediate access to historical context for urgent decisions

---

### Use Case 3: Telemedicine Encounter
**Scenario:** Virtual visit with patient's self-reported history

**Solution:**
1. Patient provides medication list and medical history
2. Clinician enters into manual entry form during visit
3. Use for diagnostic evaluation in real-time
4. Save for future telemedicine encounters

**Benefit:** Structured documentation for telemedicine visits

---

### Use Case 4: Specialty Consultation
**Scenario:** Consulting physician reviewing referred patient

**Solution:**
1. Enter referral information and outside records
2. Add consultant's examination findings
3. Use diagnostic engine with complete context
4. Document recommendations

**Benefit:** Comprehensive evaluation with full historical context

---

## 🔒 Privacy & Security

### Data Storage
- Manual histories stored securely
- Patient identifiers encrypted
- Access controls enforced
- Audit logging enabled

### HIPAA Compliance
- No PHI transmitted to third parties
- All data stays within your RealDiag instance
- Complies with HIPAA requirements
- Encrypted in transit and at rest

### Access Control
- Optional: Require user authentication
- Role-based access (view vs. edit)
- Per-patient access restrictions
- Activity audit trails

---

## 📊 Data Quality Tips

### Maximize Diagnostic Value

1. **Trend Lab Values**
   - Enter multiple lab results over time
   - Include dates for trending analysis
   - Mark abnormal/critical values

2. **Complete H&P**
   - Don't skip sections
   - Document negative findings ("No chest pain")
   - Include vital signs in physical exam

3. **Medication Details**
   - Include dosages (not just drug names)
   - Note compliance issues if known
   - Document date prescribed

4. **Allergy Specifics**
   - Type of reaction (not just "allergy")
   - Severity (anaphylaxis vs. rash)
   - Date of reaction if known

5. **Family History Patterns**
   - Age at diagnosis matters
   - Multiple affected relatives increases risk
   - Paternal vs. maternal side

---

## 🚀 Future Enhancements

### Planned Features

- **Import from PDF** - Extract data from scanned records
- **Voice Entry** - Dictate history data
- **Templates** - Specialty-specific entry templates
- **Smart Suggestions** - Auto-suggest related data entry
- **Bulk Import** - CSV upload for multiple patients
- **Mobile App** - Manual entry on mobile devices
- **Offline Mode** - Enter data without internet, sync later
- **OCR Integration** - Scan paper charts directly

---

## 🆘 Troubleshooting

### Common Issues

**Q: Dropdown list doesn't have my option**
- **A:** Select "Other" and enter custom value manually

**Q: Can't save - "Patient ID required" error**
- **A:** Demographics section requires Patient ID/MRN before saving

**Q: Data disappeared after clicking section**
- **A:** Data is saved per-section, use "Save Patient History" button to persist

**Q: How to edit saved history?**
- **A:** Retrieve patient using GET endpoint, modify, and POST again

**Q: Can I import from spreadsheet?**
- **A:** Bulk import feature planned for future release

---

## 📞 Support

For questions or issues:
- **Documentation**: See COMPREHENSIVE_HISTORY_GUIDE.md
- **GitHub Issues**: https://github.com/bevroy/RealDiag-Software/issues
- **Email Support**: support@realdiag.com

---

**Version:** 1.0.0  
**Last Updated:** December 2025  
**Status:** ✅ Production Ready
