# Epic/EHR Integration Guide for RealDiag

## Overview

RealDiag now supports **Epic EHR integration** via **SMART on FHIR** and **FHIR R4 APIs**. This transforms RealDiag from a standalone reference tool into a real-time clinical decision support system that reads patient data directly from the EHR.

---

## 🎯 What This Enables

### Before Integration (Standalone)
- ❌ Clinician manually enters symptoms
- ❌ Clinician switches to Epic to check labs
- ❌ Clinician manually interprets results
- ❌ No context from patient's actual data

### After Integration (Epic-Connected)
- ✅ **Automatic patient context** - launches with patient already selected
- ✅ **Real-time lab/vital evaluation** - reads troponin, WBC, glucose, etc.
- ✅ **Automated criteria matching** - compares patient data to diagnostic criteria
- ✅ **Intelligent recommendations** - suggests orders based on missing data
- ✅ **Severity scoring** - calculates qSOFA, HEART score, etc. automatically

---

## 🏗️ Architecture

### Components Implemented

1. **FHIR Client** (`backend/services/fhir_client.py`)
   - Connects to Epic FHIR R4 API
   - OAuth 2.0 authentication
   - Fetches Patient, Observation, Condition, Medication data
   - Parses FHIR resources into structured Python objects

2. **Smart Diagnostic Engine** (`backend/services/smart_diagnostic_engine.py`)
   - Evaluates patient data against diagnostic rules
   - Specialized evaluators for ACS, Sepsis, DKA
   - Calculates probability scores
   - Identifies missing tests

3. **SMART on FHIR Router** (`backend/services/smart_router.py`)
   - `/smart/launch` - SMART launch entry point
   - `/smart/callback` - OAuth callback handler
   - `/smart/evaluate-patient` - CDS evaluation endpoint
   - `/smart/patient/{id}` - Patient summary endpoint

4. **Common LOINC Codes** (in `fhir_client.py`)
   - Pre-defined LOINC codes for troponin, WBC, glucose, vitals, etc.
   - Makes it easy to query specific lab tests

---

## 🚀 Deployment Guide

### Step 1: Register with Epic App Oriel

1. **Go to Epic App Oriel**: https://apporchard.epic.com/
2. **Create a new app**:
   - App Type: **SMART on FHIR**
   - Launch Type: **EHR Launch**
   - FHIR Version: **R4**
   
3. **Configure your app**:
   ```
   App Name: RealDiag Clinical Decision Support
   Description: AI-powered diagnostic decision support system
   Redirect URIs: 
     - https://realdiag-software.onrender.com/smart/callback
     - http://localhost:8000/smart/callback (for testing)
   
   Requested Scopes:
     - launch
     - patient/*.read
     - openid
     - fhirUser
   ```

4. **Save your credentials**:
   - Client ID: `abc123...`
   - Client Secret: `xyz789...` (if confidential client)

### Step 2: Configure Environment Variables

Add to your `.env` file or Render environment variables:

```bash
# Epic FHIR Configuration
FHIR_BASE_URL=https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4
SMART_CLIENT_ID=your_client_id_here
SMART_CLIENT_SECRET=your_client_secret_here
SMART_REDIRECT_URI=https://realdiag-software.onrender.com/smart/callback
```

**For Render.com:**
1. Go to your backend service
2. Environment → Add Environment Variables
3. Add each variable above

### Step 3: Install Dependencies

```bash
cd backend
pip install requests pydantic
```

Update `requirements.txt`:
```txt
# Existing dependencies...
requests>=2.31.0
pydantic>=2.0.0
```

### Step 4: Test Locally

```bash
# Start backend
cd backend
python -m uvicorn main:app --reload --port 8000

# Test FHIR connection (with a test token)
curl http://localhost:8000/smart/config
```

### Step 5: Deploy to Production

```bash
git add .
git commit -m "Add Epic FHIR integration with SMART on FHIR"
git push origin main
```

Render will automatically deploy.

### Step 6: Configure Epic Launch

In Epic App Oriel, set your launch URL:
```
https://realdiag-software.onrender.com/smart/launch
```

---

## 📖 Usage Examples

### Example 1: SMART Launch from Epic

**Clinician workflow:**
1. Clinician opens patient chart in Epic
2. Clicks "RealDiag" app in Epic menu
3. Epic redirects to: `https://realdiag-software.onrender.com/smart/launch?iss=...&launch=...`
4. RealDiag handles OAuth flow
5. Clinician sees patient data with diagnostic recommendations

### Example 2: Evaluate Patient via API

```python
import requests

# After SMART launch, you have an access token and patient ID

response = requests.post(
    "https://realdiag-software.onrender.com/smart/evaluate-patient",
    json={
        "patient_id": "eXg4k...",
        "chief_complaint": "chest pain",
        "access_token": "eyJhbG..."
    }
)

results = response.json()
for diagnosis in results:
    print(f"\n{diagnosis['diagnosis_label']}")
    print(f"Probability: {diagnosis['probability']:.1%}")
    print(f"Severity: {diagnosis['severity']}")
    
    print("\nCriteria Met:")
    for criterion in diagnosis['criteria_met']:
        print(f"  ✓ {criterion['criterion']}: {criterion['value']}")
    
    print("\nRecommendations:")
    for rec in diagnosis['recommendations']:
        print(f"  • {rec}")
```

**Example Output:**
```
🔴 Acute Coronary Syndrome
Probability: 85.0%
Severity: CRITICAL

Criteria Met:
  ✓ Elevated troponin: 0.42 ng/mL (expected: > 0.04 ng/mL)
  ✓ Tachycardia: 112 bpm

Recommendations:
  • Aspirin 325mg STAT (if not contraindicated)
  • Obtain ECG immediately
  • Cardiology consultation
  • Consider cath lab activation if STEMI criteria met
```

### Example 3: Get Patient Summary

```python
response = requests.get(
    "https://realdiag-software.onrender.com/smart/patient/eXg4k...",
    params={"access_token": "eyJhbG..."}
)

summary = response.json()
print(f"Patient: {summary['name']}, Age {summary['age']}")
print(f"Labs: {summary['lab_count']}")
print(f"Abnormal Labs: {len(summary['abnormal_labs'])}")

for lab in summary['abnormal_labs']:
    print(f"  ⚠️ {lab['name']}: {lab['value']} {lab['unit']}")
```

---

## 🔧 Configuration Options

### FHIR Server URLs

**Epic (Production)**:
```
https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4
```

**Epic (Sandbox)**:
```
https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4
```

**Cerner/Oracle Health**:
```
https://fhir-myrecord.cerner.com/r4/{tenant_id}
```

### Supported Resources

Currently implemented FHIR resources:
- ✅ Patient (demographics)
- ✅ Observation (labs, vitals)
- ✅ Condition (diagnoses)
- ✅ MedicationRequest (medications)
- ✅ AllergyIntolerance (allergies)

Can easily add:
- Procedure
- DiagnosticReport
- Immunization
- CarePlan

---

## 🧪 Testing

### Unit Tests

```python
# Test FHIR client
python -m pytest backend/tests/test_fhir_client.py

# Test diagnostic engine
python -m pytest backend/tests/test_smart_diagnostic_engine.py
```

### Manual Testing with Epic Sandbox

1. Create Epic sandbox account: https://fhir.epic.com/
2. Use sandbox patient IDs: `Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB`
3. Test SMART launch with sandbox credentials

### Test Patient Scenarios

Create test patients in Epic with specific lab values:

**ACS Patient**:
- Troponin I: 0.25 ng/mL (elevated)
- ECG: ST elevation
- Symptoms: Chest pain

**Sepsis Patient**:
- WBC: 18,000 K/uL (elevated)
- Lactate: 4.2 mmol/L (elevated)
- BP: 88/55 (hypotensive)
- Temp: 102.5°F

**DKA Patient**:
- Glucose: 450 mg/dL
- CO2: 12 mEq/L (low bicarb)
- pH: 7.18 (acidotic)

---

## 🔐 Security Considerations

### OAuth Security
- ✅ Use HTTPS only in production
- ✅ Store access tokens securely (session storage, encrypted)
- ✅ Implement token refresh
- ✅ Validate redirect URIs

### HIPAA Compliance
- ✅ No PHI logged
- ✅ Encrypted data transmission (TLS 1.2+)
- ✅ Access tokens expire (typically 1 hour)
- ✅ Audit logging for patient access

### Epic Security Requirements
- Business Associate Agreement (BAA) required
- HITRUST certification recommended
- Annual security review
- Penetration testing

---

## 📊 Clinical Decision Support Features

### Currently Implemented

**Acute Coronary Syndrome (ACS)**:
- Checks troponin I/T elevation
- Evaluates vital signs (HR, BP)
- Calculates probability
- Recommends immediate actions

**Sepsis**:
- Calculates qSOFA score automatically
- Checks WBC, lactate
- Flags hypotension, tachypnea
- Recommends sepsis bundle

**Diabetic Ketoacidosis (DKA)**:
- Checks glucose, bicarbonate
- Identifies metabolic acidosis
- Recommends insulin protocol

### Coming Soon

- **Heart Failure**: BNP, volume status, LVEF
- **Stroke**: NIH Stroke Scale, CT findings
- **PE**: Wells score, D-dimer
- **Pneumonia**: CURB-65, PSI/PORT score
- **AFib**: CHA₂DS₂-VASc, anticoagulation recommendations

---

## 🎨 Frontend Integration (Next Steps)

### SMART Launch Frontend

Create `frontend/pages/smart-launch.js`:

```javascript
import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';

export default function SmartLaunch() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Get token and patient ID from session
    const token = sessionStorage.getItem('fhir_token');
    const patientId = sessionStorage.getItem('patient_id');
    
    if (token && patientId) {
      // Fetch patient evaluations
      fetch('https://realdiag-software.onrender.com/smart/evaluate-patient', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_id: patientId,
          access_token: token,
          chief_complaint: null
        })
      })
      .then(res => res.json())
      .then(data => {
        // Display results
        setEvaluations(data);
        setLoading(false);
      });
    }
  }, []);
  
  // Render evaluations...
}
```

### Patient Banner Component

```javascript
function PatientBanner({ patientData }) {
  return (
    <div style={{ 
      background: '#667eea', 
      color: 'white', 
      padding: '12px 24px',
      display: 'flex',
      justifyContent: 'space-between'
    }}>
      <div>
        <strong>{patientData.name}</strong>
        <span style={{ marginLeft: 16 }}>
          {patientData.age}yo {patientData.gender}
        </span>
      </div>
      <div>
        MRN: {patientData.patient_id}
      </div>
    </div>
  );
}
```

---

## 📞 Support & Resources

### Epic Documentation
- FHIR API: https://fhir.epic.com/Documentation
- App Oriel: https://apporchard.epic.com/
- SMART on FHIR: https://docs.smarthealthit.org/

### HL7 FHIR
- FHIR R4 Spec: https://hl7.org/fhir/R4/
- LOINC Codes: https://loinc.org/
- SNOMED CT: https://www.snomed.org/

### RealDiag Support
- GitHub Issues: https://github.com/bevroy/RealDiag-Software/issues
- Documentation: /MEDICAL_UPDATE_PROCESS.md

---

## 🚀 Future Enhancements

### Phase 2: CDS Hooks
- Order-select hooks (suggest tests)
- Patient-view hooks (auto-launch CDS)
- Medication-prescribe hooks (interaction checks)

### Phase 3: Bi-directional Integration
- Write orders back to Epic
- Update problem list
- Create clinical notes

### Phase 4: Multi-EHR Support ✅ **IMPLEMENTED**
- ✅ **Cerner/Oracle Health** - Fully supported! See [CERNER_INTEGRATION_GUIDE.md](./CERNER_INTEGRATION_GUIDE.md)
- ⏳ Allscripts (adapter ready, needs testing)
- ⏳ athenahealth (adapter ready, needs testing)
- ⏳ MEDITECH

**Note**: The EHR adapter layer (`backend/services/ehr_adapter.py`) already supports Epic, Cerner, Allscripts, and athenahealth. Just configure environment variables to switch vendors!

### Phase 5: Advanced Features
- Real-time risk calculators
- Clinical pathways
- Care gap identification
- Quality measure reporting

---

## 📝 Change Log

**Version 1.5.0** (2025-11-19):
- ✅ FHIR R4 client implementation
- ✅ SMART on FHIR launch flow
- ✅ Patient data aggregation
- ✅ Automated diagnostic evaluation (ACS, Sepsis, DKA)
- ✅ Clinical decision support API endpoints
- ✅ Epic App Oriel registration guide

**Next Release** (Planned):
- Frontend SMART launch UI
- More specialized evaluators (HF, Stroke, PE)
- CDS Hooks implementation
- Clinical score calculators

---

**Document Version**: 1.0.0  
**Last Updated**: November 19, 2025  
**Status**: Ready for Epic App Oriel submission
