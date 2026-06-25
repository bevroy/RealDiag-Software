# Cerner/Oracle Health Integration Guide

## Overview

RealDiag fully supports **Cerner/Oracle Health** EHR systems using the same FHIR R4 and SMART on FHIR standards as Epic. The core integration code works with both vendors, with an adapter layer handling vendor-specific differences.

---

## ✅ What Works with Cerner

The **same backend infrastructure** works for both Epic and Cerner:
- ✅ FHIR R4 client
- ✅ OAuth 2.0 / SMART on FHIR launch
- ✅ Patient data retrieval (demographics, labs, vitals, conditions, medications)
- ✅ Diagnostic evaluation engine
- ✅ Clinical decision support endpoints
- ✅ Frontend SMART launch page

---

## 🔧 Key Differences: Epic vs Cerner

### 1. **Tenant ID Requirement**
- **Epic**: No tenant ID needed, single authorization endpoint
- **Cerner**: Requires tenant ID in URLs and OAuth endpoints

```bash
# Epic
https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4

# Cerner (includes tenant ID)
https://fhir-myrecord.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d
```

### 2. **OAuth Endpoints**
- **Epic**: Static OAuth URLs
- **Cerner**: Dynamic URLs with tenant ID embedded

```bash
# Epic
Token:     https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token
Authorize: https://fhir.epic.com/interconnect-fhir-oauth/oauth2/authorize

# Cerner
Token:     https://authorization.cerner.com/tenants/{tenant_id}/protocols/oauth2/profiles/smart-v1/token
Authorize: https://authorization.cerner.com/tenants/{tenant_id}/protocols/oauth2/profiles/smart-v1/personas/provider/authorize
```

### 3. **FHIR Resource Structure**
- **Epic**: Direct `valueQuantity` in Observations
- **Cerner**: Often uses `component` array for multi-part results (e.g., Blood Pressure)

```json
// Epic Observation (Troponin)
{
  "resourceType": "Observation",
  "valueQuantity": {
    "value": 0.42,
    "unit": "ng/mL"
  }
}

// Cerner Observation (Blood Pressure - uses components)
{
  "resourceType": "Observation",
  "component": [
    {
      "code": { "coding": [{ "code": "8480-6" }] },
      "valueQuantity": { "value": 120, "unit": "mmHg" }
    },
    {
      "code": { "coding": [{ "code": "8462-4" }] },
      "valueQuantity": { "value": 80, "unit": "mmHg" }
    }
  ]
}
```

### 4. **Search Parameter Requirements**
- **Epic**: Category parameter optional
- **Cerner**: Requires explicit `category` parameter in Observation searches

```bash
# Epic (category optional)
GET /Observation?patient=123&code=10839-9

# Cerner (category required)
GET /Observation?patient=123&category=laboratory&code=10839-9
```

### 5. **OAuth Scopes**
- **Epic**: `patient/*.read`
- **Cerner**: More granular: `patient/Patient.read`, `patient/Observation.read`, etc.

---

## 🚀 Setup for Cerner Integration

### Step 1: Register with Cerner Code Console

1. Go to: https://code-console.cerner.com/
2. Create a new **SMART on FHIR app**
3. Configure:
   ```
   App Name: RealDiag Clinical Decision Support
   Launch Type: EHR Launch (Provider)
   FHIR Version: R4
   Redirect URI: https://realdiag-software.onrender.com/smart/callback
   
   Requested Scopes:
     - launch
     - patient/Patient.read
     - patient/Observation.read
     - patient/Condition.read
     - patient/MedicationRequest.read
     - patient/AllergyIntolerance.read
     - openid
     - fhirUser
   ```

4. **Save your credentials**:
   - Client ID: `abc123...`
   - Client Secret: `xyz789...`
   - **Tenant ID**: `ec2458f2-1e24-41c8-b71b-0e701af7583d` (from your FHIR URL)

### Step 2: Configure Environment Variables

Edit your `.env` file:

```bash
# Select Cerner as vendor
EHR_VENDOR=cerner

# Cerner FHIR Base URL (includes tenant ID)
FHIR_BASE_URL=https://fhir-myrecord.cerner.com/r4/YOUR_TENANT_ID_HERE

# Cerner OAuth Credentials (from Cerner Code Console)
SMART_CLIENT_ID=your_cerner_client_id
SMART_CLIENT_SECRET=your_cerner_client_secret

# Tenant ID (extract from your FHIR Base URL)
EHR_TENANT_ID=YOUR_TENANT_ID_HERE

# Redirect URI (must match Cerner Code Console)
SMART_REDIRECT_URI=https://realdiag-software.onrender.com/smart/callback
```

### Step 3: Test with Cerner Sandbox

Cerner provides test patients in their sandbox:

```bash
# Example Cerner sandbox patient
Patient ID: 12724066
Tenant ID: ec2458f2-1e24-41c8-b71b-0e701af7583d
FHIR Base: https://fhir-myrecord.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d
```

---

## 🔄 Switching Between Epic and Cerner

The adapter layer makes switching vendors trivial:

```bash
# For Epic
EHR_VENDOR=epic
FHIR_BASE_URL=https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4
SMART_CLIENT_ID=epic_client_id
SMART_CLIENT_SECRET=epic_secret

# For Cerner
EHR_VENDOR=cerner
FHIR_BASE_URL=https://fhir-myrecord.cerner.com/r4/{tenant_id}
SMART_CLIENT_ID=cerner_client_id
SMART_CLIENT_SECRET=cerner_secret
EHR_TENANT_ID=ec2458f2-1e24-41c8-b71b-0e701af7583d
```

**No code changes required** - the `ehr_adapter.py` handles all vendor differences automatically!

---

## 🧪 Testing Cerner Integration

### Unit Tests

```python
# Test Cerner observation parsing
from backend.services.ehr_adapter import EHRAdapter, EHRVendor

# Cerner BP observation with components
cerner_obs = {
    "resourceType": "Observation",
    "component": [
        {
            "code": {"coding": [{"code": "8480-6"}]},
            "valueQuantity": {"value": 140, "unit": "mmHg"}
        }
    ],
    "effectiveDateTime": "2025-11-19T10:00:00Z"
}

result = EHRAdapter.parse_observation(cerner_obs, EHRVendor.CERNER)
assert result["value"] == 140
assert result["unit"] == "mmHg"
```

### Integration Test with Cerner Sandbox

```bash
# Start backend with Cerner config
EHR_VENDOR=cerner python -m uvicorn backend.main:app --reload

# Test SMART launch
curl "http://localhost:8000/smart/launch?iss=https://fhir-myrecord.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d&launch=test123"

# Should redirect to Cerner authorization page
```

---

## 📊 Cerner-Specific Features

### Component-Based Observations

The adapter automatically handles Cerner's component structure:

```python
# Epic: Direct value
lab = patient_data.get_lab("10839-9")  # Troponin
print(f"Troponin: {lab.value} {lab.unit}")

# Cerner: Same API, but handles components internally
bp = patient_data.get_vital("85354-9")  # Blood Pressure
print(f"BP: {bp.value} {bp.unit}")  # Extracts from component[0]
```

### Category Filtering

The adapter adds required category filters for Cerner:

```python
# Automatically adds category=laboratory for Cerner
labs = client.get_observations(
    patient_id="12724066",
    category="laboratory"
)
# Behind the scenes: /Observation?patient=12724066&category=laboratory
```

---

## 🔒 Cerner Security Considerations

### OAuth Flow
- **Epic**: Confidential client (backend can use client_secret)
- **Cerner**: Also supports confidential clients

### Data Access
- **Epic**: Broad scopes (`patient/*.read`)
- **Cerner**: Granular scopes (better security, more configuration)

### Token Expiry
- **Epic**: Typically 1 hour
- **Cerner**: Also 1 hour, but check token response

---

## 🐛 Troubleshooting Cerner Integration

### Issue: "Tenant ID required"
**Solution**: Set `EHR_TENANT_ID` environment variable

### Issue: "Category parameter required"
**Solution**: Already handled by adapter - ensure `EHR_VENDOR=cerner`

### Issue: "Cannot parse observation"
**Cause**: Cerner uses components for multi-part results
**Solution**: Adapter handles this automatically - check logs for details

### Issue: OAuth redirect fails
**Cause**: Redirect URI mismatch
**Solution**: Ensure `.env` redirect URI matches Cerner Code Console exactly

---

## 📈 Performance Comparison

| Feature | Epic | Cerner | Notes |
|---------|------|--------|-------|
| **OAuth Setup** | Simple | Requires tenant ID | Cerner more complex setup |
| **API Response Time** | ~500ms | ~600ms | Cerner slightly slower |
| **Data Structure** | Simple | Components | Adapter normalizes |
| **Search Flexibility** | High | Requires categories | Epic more flexible |
| **Pagination** | Automatic | Explicit `_count` | Both supported |

---

## 🎯 Production Deployment with Cerner

### Render.com Environment Variables

```bash
# In Render dashboard, add:
EHR_VENDOR=cerner
FHIR_BASE_URL=https://fhir-myrecord.cerner.com/r4/YOUR_TENANT_ID
SMART_CLIENT_ID=your_cerner_client_id
SMART_CLIENT_SECRET=your_cerner_client_secret
EHR_TENANT_ID=YOUR_TENANT_ID
SMART_REDIRECT_URI=https://realdiag-software.onrender.com/smart/callback
```

### Netlify Frontend (No Changes Needed!)

The frontend works identically for Epic and Cerner - it just calls the backend API.

---

## 📝 Summary

### What You Need to Change for Cerner:
1. ✅ **Register app** at Cerner Code Console (instead of Epic App Oriel)
2. ✅ **Set environment variables** (EHR_VENDOR=cerner, tenant ID, credentials)
3. ❌ **NO code changes** - adapter handles everything

### What Stays the Same:
- ✅ Backend Python code (fhir_client.py, smart_diagnostic_engine.py)
- ✅ Frontend React components
- ✅ SMART launch flow
- ✅ Diagnostic evaluation logic
- ✅ API endpoints

### Bottom Line:
**The current implementation already supports Cerner!** Just change the configuration. The adapter layer (`ehr_adapter.py`) automatically handles:
- Tenant ID in OAuth URLs
- Component-based observations
- Category filtering requirements
- Vendor-specific scopes

---

## 🔗 Resources

- **Cerner Code Console**: https://code-console.cerner.com/
- **Cerner FHIR Docs**: https://fhir.cerner.com/
- **Cerner Sandbox**: Use tenant `ec2458f2-1e24-41c8-b71b-0e701af7583d`
- **RealDiag Adapter**: `backend/services/ehr_adapter.py`

---

**Last Updated**: November 19, 2025  
**Status**: ✅ Cerner fully supported (same codebase as Epic)
