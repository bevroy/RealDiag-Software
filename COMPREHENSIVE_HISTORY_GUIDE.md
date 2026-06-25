# Comprehensive Patient History Integration

## Overview

RealDiag now supports **comprehensive patient history retrieval** from EMR/EHR systems, enabling diagnostic decision support with complete clinical context including:

- 📋 **Prior Visit Notes** - All clinical documentation from past encounters
- 🧪 **Diagnostic Tests** - Lab results, pathology, diagnostic procedures with trending
- 📝 **History & Physicals** - Complete H&P examinations with structured sections
- 🔬 **Procedures** - Surgical and interventional procedures performed
- 🏥 **Imaging Studies** - CT, MRI, X-Ray, Ultrasound reports with radiologist findings
- 📊 **Problem Lists** - Active and resolved medical conditions
- 💊 **Medication History** - Current and historical medication regimens
- ⚠️ **Allergies** - All documented allergies and intolerances
- 👨‍👩‍👧 **Family History** - Hereditary conditions and risk factors
- 🚬 **Social History** - Lifestyle factors, occupation, substance use

## Why Comprehensive History Matters

Traditional diagnostic systems only access **current visit data**, missing crucial context:

### ❌ Without History:
- No trending of lab values (is glucose 180 improving or worsening?)
- No prior similar presentations (has this patient had similar chest pain before?)
- No context for comorbidities (unknown that patient has CKD, heart failure)
- No medication reconciliation (possible drug interactions)
- No baseline comparison (is BP 160/95 new or chronic?)

### ✅ With Comprehensive History:
- **Trending Analysis**: See if troponin 0.08 is rising trend or isolated
- **Pattern Recognition**: Identify recurrent presentations (3rd UTI this year)
- **Risk Stratification**: Factor in comorbidities (patient with CAD presenting with chest pain = higher risk)
- **Medication Context**: Current diuretic use explains low potassium
- **Baseline Comparison**: New shortness of breath vs chronic COPD baseline
- **Prior Workup**: Avoid repeating recent negative stress test

## Architecture

### Patient History Service
New `PatientHistoryService` retrieves comprehensive data via FHIR:

```python
from backend.services.patient_history_service import PatientHistoryService

# Initialize service
history_service = PatientHistoryService(
    fhir_base_url="https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
    auth_token="Bearer eyJhbG..."
)

# Retrieve comprehensive history
comprehensive_history = await history_service.get_comprehensive_history(
    patient_id="patient-12345",
    lookback_days=365,  # 1 year of history
    include_resolved=True  # Include resolved conditions
)
```

### FHIR Resources Retrieved

| FHIR Resource | Data Retrieved | Clinical Use |
|---------------|----------------|--------------|
| `DocumentReference` | Visit notes, H&Ps, discharge summaries | Complete clinical narrative |
| `Observation` | Lab results, vitals, social history | Trending, risk factors |
| `DiagnosticReport` | Imaging reports, pathology | Prior workup, findings |
| `Procedure` | Surgeries, interventions | Surgical history, complications |
| `ImagingStudy` | CT, MRI, X-Ray studies | Radiologic findings |
| `Condition` | Active & resolved diagnoses | Problem list, comorbidities |
| `MedicationRequest` | Current & historical meds | Drug reconciliation, interactions |
| `AllergyIntolerance` | All allergies | Safety, contraindications |
| `FamilyMemberHistory` | Hereditary conditions | Genetic risk factors |

## API Endpoints

### 1. Comprehensive History Endpoint

**Endpoint:** `GET /integration/ehr/fhir/comprehensive-history/{patient_id}`

**Purpose:** Retrieve complete patient history for diagnostic decision support

**Authentication:** User login OR API key

**Parameters:**
- `patient_id` (required): FHIR Patient resource ID
- `config_name` (optional): FHIR server configuration name (default: "main_ehr")
- `lookback_days` (optional): Days of history to retrieve (default: 365)
- `include_resolved` (optional): Include resolved conditions (default: true)

**Example Request:**
```bash
curl -X GET "https://api.realdiag.com/integration/ehr/fhir/comprehensive-history/patient-12345?lookback_days=730" \
  -H "X-API-Key: your_api_key_here"
```

**Example Response:**
```json
{
  "patient_id": "patient-12345",
  "patient_name": "John Smith",
  "demographics": {
    "date_of_birth": "1970-01-15",
    "age": 55,
    "gender": "male"
  },
  "visit_notes": [
    {
      "date": "2025-10-15T14:30:00Z",
      "type": "Progress Note",
      "author": "Dr. Sarah Johnson",
      "specialty": "Cardiology",
      "content": "Patient presents for follow-up of stable angina...",
      "encounter_id": "encounter-789"
    }
  ],
  "diagnostic_tests": [
    {
      "date": "2025-10-15T08:00:00Z",
      "test_name": "Troponin I",
      "test_type": "Laboratory",
      "result": "0.04 ng/mL",
      "interpretation": "Normal",
      "abnormal": false,
      "critical": false,
      "reference_range": "0.00-0.04 ng/mL",
      "loinc_code": "10839-9"
    },
    {
      "date": "2025-09-20T09:15:00Z",
      "test_name": "Troponin I",
      "test_type": "Laboratory",
      "result": "0.03 ng/mL",
      "interpretation": "Normal",
      "abnormal": false,
      "critical": false,
      "reference_range": "0.00-0.04 ng/mL",
      "loinc_code": "10839-9"
    }
  ],
  "history_and_physicals": [
    {
      "date": "2025-01-10T10:00:00Z",
      "author": "Dr. Michael Chen",
      "chief_complaint": "Chest pain",
      "history_of_present_illness": "58-year-old male with history of hypertension...",
      "past_medical_history": [
        "Hypertension",
        "Hyperlipidemia",
        "Type 2 Diabetes"
      ],
      "past_surgical_history": [
        "Appendectomy (1995)",
        "Cholecystectomy (2010)"
      ],
      "medications": [
        "Lisinopril 20mg daily",
        "Atorvastatin 40mg daily",
        "Metformin 1000mg BID"
      ],
      "allergies": ["Penicillin (rash)"],
      "family_history": "Father had MI at age 62, mother with diabetes",
      "social_history": "Former smoker (quit 5 years ago, 20 pack-years), occasional alcohol",
      "review_of_systems": "Negative except as noted in HPI",
      "physical_exam": "BP 142/88, HR 78, RR 16, SpO2 98% on RA...",
      "assessment": "1. Stable angina 2. Hypertension 3. Type 2 Diabetes",
      "plan": "Continue current medications, stress test ordered..."
    }
  ],
  "procedures": [
    {
      "date": "2024-06-15T11:00:00Z",
      "procedure_name": "Coronary angiography",
      "procedure_code": "93458",
      "indication": "Positive stress test",
      "outcome": "40% LAD stenosis, medical management",
      "operator": "Dr. Robert Williams"
    }
  ],
  "imaging_studies": [
    {
      "date": "2025-08-20T13:00:00Z",
      "modality": "CT",
      "body_site": "Chest",
      "indication": "Chest pain evaluation",
      "findings": "Coronary artery calcium score 285...",
      "impression": "Moderate coronary calcification, recommend cardiology follow-up",
      "radiologist": "Dr. Emily Taylor"
    }
  ],
  "problem_list": {
    "active": [
      {
        "code": "Hypertension",
        "status": "active",
        "recorded_date": "2015-03-10",
        "onset": "2015-03-10"
      },
      {
        "code": "Type 2 Diabetes Mellitus",
        "status": "active",
        "recorded_date": "2018-07-22",
        "onset": "2018-07-22"
      }
    ],
    "resolved": [
      {
        "code": "Acute Bronchitis",
        "status": "resolved",
        "recorded_date": "2024-11-05",
        "abatement": "2024-11-20"
      }
    ]
  },
  "medications": {
    "current": [
      {
        "name": "Lisinopril 20mg",
        "status": "active",
        "dosage": "20mg by mouth once daily",
        "date_prescribed": "2023-01-15"
      },
      {
        "name": "Atorvastatin 40mg",
        "status": "active",
        "dosage": "40mg by mouth at bedtime",
        "date_prescribed": "2023-01-15"
      }
    ],
    "historical": [
      {
        "name": "Metoprolol 50mg",
        "status": "stopped",
        "date_prescribed": "2020-05-10",
        "date_stopped": "2022-08-15"
      }
    ]
  },
  "allergies": [
    "Penicillin (rash)",
    "Shellfish (anaphylaxis)"
  ],
  "family_history": "Father: MI at age 62; Mother: Type 2 diabetes, hypertension; Sister: breast cancer at age 50",
  "social_history": "Former smoker (quit 2020, 20 pack-year history); Occasional alcohol use (2-3 drinks/week); Works as accountant; Married with 2 children",
  "summary": "John Smith is a 55-year-old male with history of Hypertension, Type 2 Diabetes Mellitus. Recent visits: 8 clinical encounters in the past year. 15 abnormal test results noted. Currently on 5 medications.",
  "data_quality": {
    "visit_notes_count": 8,
    "diagnostic_tests_count": 47,
    "abnormal_tests_count": 15,
    "critical_tests_count": 0,
    "h_and_p_count": 2,
    "procedures_count": 3,
    "imaging_studies_count": 4,
    "lookback_days": 365
  }
}
```

## Integration with Diagnostic Engine

### Automatic History Retrieval

When evaluating a patient, the system can automatically retrieve comprehensive history:

```python
# Example: Enhanced diagnostic evaluation with history
from backend.services.smart_diagnostic_engine import SmartDiagnosticEngine
from backend.services.patient_history_service import PatientHistoryService

# Get comprehensive history
history_service = PatientHistoryService(fhir_base_url, auth_token)
history = await history_service.get_comprehensive_history(patient_id)

# Diagnostic engine uses history for context
diagnostic_engine = SmartDiagnosticEngine()
evaluations = diagnostic_engine.evaluate_patient_with_history(
    patient_data=current_patient_data,
    comprehensive_history=history,
    chief_complaint="Chest pain"
)
```

### Enhanced Clinical Decision Support

With comprehensive history, the diagnostic engine can:

1. **Trending Analysis**
   ```python
   # Compare current troponin to prior values
   current_trop = 0.08
   prior_trops = [0.03, 0.04, 0.05]  # from history
   # Rising trend indicates ACS even if technically "normal"
   ```

2. **Pattern Recognition**
   ```python
   # Identify recurrent presentations
   visit_notes = history.visit_notes
   chest_pain_visits = [v for v in visit_notes if "chest pain" in v.content.lower()]
   # 3 chest pain visits in 6 months = consider unstable angina
   ```

3. **Risk Stratification**
   ```python
   # Factor comorbidities into risk calculation
   active_conditions = history.active_conditions
   has_cad = any("coronary" in c['code'].lower() for c in active_conditions)
   has_diabetes = any("diabetes" in c['code'].lower() for c in active_conditions)
   # Adjust probability: chest pain + CAD + DM = much higher ACS risk
   ```

4. **Medication Reconciliation**
   ```python
   # Check for drug interactions and contraindications
   current_meds = [m['name'] for m in history.current_medications]
   # Patient on beta blocker - consider in treatment recommendations
   ```

## Use Cases

### Use Case 1: Emergency Department Chest Pain

**Without History:**
- Patient presents with chest pain
- Troponin 0.08 ng/mL (technically normal, cutoff 0.10)
- No context for risk assessment

**With Comprehensive History:**
- Review shows 3 prior ED visits for chest pain (6 months)
- Prior troponins: 0.03 → 0.05 → 0.06 → 0.08 (rising trend!)
- Known CAD with 40% LAD stenosis (prior cath)
- Recent stress test positive for ischemia
- Family history: father MI at 62
- **Enhanced Decision**: Rising troponin trend + known CAD = admit for ACS workup despite "normal" single value

### Use Case 2: Primary Care Dyspnea

**Without History:**
- Patient reports shortness of breath
- Current vitals: BP 160/95, HR 95, SpO2 94%
- No recent labs available

**With Comprehensive History:**
- H&P from 2 months ago: BP was 130/80 (new hypertension)
- Prior BNP: 450 pg/mL (elevated - heart failure)
- Echocardiogram: EF 35% (reduced - heart failure)
- Current meds: Lisinopril, furosemide (HF regimen)
- Recent visit note: "Doing well, no dyspnea at baseline"
- **Enhanced Decision**: New dyspnea in known HF patient with worsening BP = acute decompensated heart failure, not new diagnosis

### Use Case 3: Inpatient Hyperglycemia

**Without History:**
- Glucose 285 mg/dL on admission labs
- Need to determine if new-onset DM vs known DM vs stress hyperglycemia

**With Comprehensive History:**
- Problem list: Type 2 Diabetes since 2018
- Prior HbA1c values: 7.2% → 7.8% → 8.5% (worsening control)
- Current medications: Metformin 1000mg BID (poor compliance per notes)
- Recent visit note: "Patient admits not taking medications regularly"
- **Enhanced Decision**: Known diabetic with poor compliance presenting with hyperglycemia = medication non-compliance, optimize regimen

## Implementation Guide

### Step 1: Configure FHIR Server

Same as existing EHR integration:

```bash
curl -X POST "https://api.realdiag.com/integration/ehr/fhir/configure" \
  -H "Content-Type: application/json" \
  -d '{
    "config_name": "main_ehr",
    "base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
    "auth_type": "oauth2",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret"
  }'
```

### Step 2: Test History Retrieval

```bash
curl -X GET "https://api.realdiag.com/integration/ehr/fhir/comprehensive-history/patient-12345" \
  -H "X-API-Key: your_api_key"
```

### Step 3: Integrate with Diagnostic Workflow

```python
# In your diagnostic application
import requests

# Pull comprehensive history
history_response = requests.get(
    f"https://api.realdiag.com/integration/ehr/fhir/comprehensive-history/{patient_id}",
    headers={"X-API-Key": api_key},
    params={"lookback_days": 730}  # 2 years
)
comprehensive_history = history_response.json()

# Use history in diagnostic evaluation
# - Review prior similar presentations
# - Trend lab values
# - Factor comorbidities
# - Check medication interactions
# - Compare to baseline
```

## Data Quality Indicators

The response includes data quality metrics:

```json
{
  "data_quality": {
    "visit_notes_count": 8,
    "diagnostic_tests_count": 47,
    "abnormal_tests_count": 15,
    "critical_tests_count": 0,
    "h_and_p_count": 2,
    "procedures_count": 3,
    "imaging_studies_count": 4,
    "lookback_days": 365
  }
}
```

**Interpretation:**
- **High quality**: Many visit notes, tests, comprehensive documentation
- **Low quality**: Sparse data may indicate incomplete EHR or new patient
- **Abnormal/Critical flags**: Immediate attention to concerning values

## Privacy & Security

- ✅ Authentication required (User OR API key)
- ✅ HIPAA-compliant data handling
- ✅ Audit logging of all data access
- ✅ OAuth 2.0 token-based EHR authentication
- ✅ Data encrypted in transit (TLS 1.3)
- ✅ No persistent storage of patient data
- ✅ Configurable lookback periods
- ✅ Patient consent verification (via EHR)

## Performance Considerations

### Optimization Strategies

1. **Lookback Period**: Limit to necessary timeframe (default 365 days)
   ```python
   # Faster: Recent data only
   history = await service.get_comprehensive_history(patient_id, lookback_days=90)
   
   # Slower: Entire history
   history = await service.get_comprehensive_history(patient_id, lookback_days=3650)
   ```

2. **Parallel Retrieval**: Multiple FHIR resources fetched concurrently
   - DocumentReference, Observation, DiagnosticReport fetched in parallel
   - Typical retrieval time: 2-5 seconds for 1 year of data

3. **Caching**: Consider caching for repeated accesses (with appropriate TTL)
   ```python
   # Cache comprehensive history for 1 hour
   cache_key = f"patient_history:{patient_id}"
   cached = redis.get(cache_key)
   if cached:
       return json.loads(cached)
   
   history = await service.get_comprehensive_history(patient_id)
   redis.setex(cache_key, 3600, json.dumps(history.dict()))
   ```

## Troubleshooting

### Common Issues

**Issue: No visit notes retrieved**
- Check DocumentReference query permissions
- Verify LOINC code mapping for H&P type (34117-2)
- Some EHRs may not expose visit notes via FHIR

**Issue: Slow retrieval (>10 seconds)**
- Reduce lookback_days parameter
- Check network latency to FHIR server
- Verify FHIR server performance

**Issue: Missing historical labs**
- Verify Observation resource permissions
- Check date range format (ISO 8601)
- Some EHRs purge old data

## Next Steps

1. **Test with your EHR**: Configure FHIR endpoint and test retrieval
2. **Review documentation**: Check EHR vendor's FHIR documentation
3. **Adjust parameters**: Fine-tune lookback period and resource types
4. **Integrate diagnostic logic**: Use history in clinical decision support
5. **Monitor performance**: Track retrieval times and optimize

## Support

For questions or issues:
- GitHub Issues: https://github.com/bevroy/RealDiag-Software/issues
- Documentation: See EHR_INTEGRATION_COMPLETE.md
- Epic App Orchard: See EPIC_APP_ORCHARD_GUIDE.md

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: December 2025
