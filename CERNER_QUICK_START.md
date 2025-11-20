# Cerner Integration - Quick Start (5 Minutes)

## 🚀 Get Started Now

Cerner provides **immediate self-service access** - no waiting for approval!

### Step 1: Create Cerner Account (2 minutes)

1. **Go to Cerner Code Console**
   - URL: https://code-console.cerner.com/
   - Click "Sign Up" or "Register"

2. **Complete Registration**
   - **Email**: Your business email
   - **Name**: Your full name
   - **Organization**: RealDiag, LLC
   - Verify email and activate account

### Step 2: Create SMART App (3 minutes)

1. **Login to Code Console**
   - Go to https://code-console.cerner.com/
   - Click "My Apps" or "Applications"

2. **Create New Application**
   - Click "New App" or "Create Application"

3. **Fill Out App Details**
   ```
   Application Name: RealDiag Clinical Decision Support
   Application Type: Provider App
   FHIR Version: R4
   Launch Type: EHR Launch
   
   Description:
   Evidence-based diagnostic decision trees and symptom-based search for clinicians. 
   Provides real-time clinical decision support integrated with patient data from Cerner.
   
   Redirect URI:
   https://api.realdiag.com/smart/callback
   
   Launch URI:
   https://www.realdiag.com/launch
   ```

4. **Select Scopes**
   
   Check these permissions:
   - [x] `launch` - SMART launch context
   - [x] `launch/patient` - Patient context
   - [x] `patient/Patient.read` - Patient demographics
   - [x] `patient/Observation.read` - Labs and vitals
   - [x] `patient/Condition.read` - Medical conditions
   - [x] `patient/MedicationRequest.read` - Current medications
   - [x] `patient/AllergyIntolerance.read` - Allergies
   - [x] `openid` - OpenID Connect
   - [x] `fhirUser` - Identify clinician

5. **Save Application**
   - Click "Create" or "Save"
   - **Copy your credentials immediately!**

### Step 3: Get Your Credentials

After creating the app, Cerner displays:

```
Client ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Client Secret: **************************************

Sandbox FHIR Base URL:
https://fhir-ehr-code.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d

Tenant ID: ec2458f2-1e24-41c8-b71b-0e701af7583d
```

**⚠️ Save these credentials securely!** You'll need them in the next step.

### Step 4: Configure RealDiag Backend (1 minute)

Add credentials to Render:

1. **Go to Render Dashboard**
   - Navigate to: https://dashboard.render.com/
   - Click on "realdiag-software" service

2. **Add Environment Variables**
   - Click "Environment" tab
   - Add these variables:

   ```bash
   CERNER_CLIENT_ID=<paste your client ID>
   CERNER_CLIENT_SECRET=<paste your client secret>
   CERNER_FHIR_BASE_URL=https://fhir-ehr-code.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d
   CERNER_TENANT_ID=ec2458f2-1e24-41c8-b71b-0e701af7583d
   EHR_VENDOR=cerner
   ```

3. **Save Changes**
   - Backend will automatically redeploy (~3 minutes)

### Step 5: Test Integration (2 minutes)

**Configure FHIR Endpoint:**

```bash
curl -X POST https://api.realdiag.com/integration/ehr/fhir/configure \
  -H "Content-Type: application/json" \
  -d '{
    "config_name": "cerner_sandbox",
    "base_url": "https://fhir-ehr-code.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d",
    "auth_type": "oauth2",
    "client_id": "'"$CERNER_CLIENT_ID"'",
    "client_secret": "'"$CERNER_CLIENT_SECRET"'"
  }'
```

**Test Patient Search:**

```bash
curl "https://api.realdiag.com/integration/ehr/fhir/search/patients?name=Smart&config_name=cerner_sandbox"
```

**Pull Test Patient Data:**

```bash
# Use Cerner's test patient
curl "https://api.realdiag.com/integration/ehr/fhir/pull/patient/12724066?config_name=cerner_sandbox"
```

Expected response:
```json
{
  "patient_id": "12724066",
  "name": "SMART, NANCY",
  "gender": "female",
  "birth_date": "1980-01-01",
  "age": 45,
  "allergies": ["Penicillin"],
  "conditions": [
    {"code": "Type 2 Diabetes", "status": "active"}
  ],
  "medications": [
    {"name": "Metformin 500mg", "status": "active"}
  ],
  "recent_vitals": {
    "Blood Pressure": "120/80 mmHg",
    "Heart Rate": "72 /min"
  },
  "recent_labs": [
    {"test": "Glucose", "value": "110 mg/dL", "date": "2025-11-15"}
  ]
}
```

## ✅ Success!

If you see patient data, **Cerner integration is working!** 🎉

## 🧪 Cerner Sandbox Test Patients

Cerner provides these test patients:

| Patient ID | Name | Use Case |
|------------|------|----------|
| 12724066 | SMART, NANCY | General testing |
| 12724067 | SMART, JOE | Pediatric patient |
| 12724068 | SMART, WILMA | Multiple conditions |
| 12742400 | SMART, FRED | Labs and vitals |

## 🔄 SMART Launch Testing

Once configured, test the SMART launch flow:

1. **Initiate Launch**
   ```
   https://api.realdiag.com/smart/launch?iss=https://fhir-ehr-code.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d&launch=test123
   ```

2. **Authorize Access**
   - You'll be redirected to Cerner's authorization page
   - Sign in with Cerner sandbox credentials
   - Grant permissions

3. **View Patient Data**
   - After authorization, RealDiag loads with patient context
   - Patient data automatically pulled from Cerner

## 📋 Next Steps

After successful testing:

1. **Production Credentials**
   - Contact Cerner to get production access
   - Update environment variables with production URLs
   - Same code works in production!

2. **Epic Registration**
   - Submit to Epic App Orchard in parallel
   - See: `EPIC_APP_ORCHARD_GUIDE.md`

3. **Frontend Integration**
   - Build UI to display patient data
   - Add SMART launch button
   - Patient data visualization

## 🐛 Troubleshooting

### "Invalid client_id"
- **Cause**: Wrong client ID or not yet activated
- **Fix**: Double-check credentials from Code Console

### "Redirect URI mismatch"
- **Cause**: Redirect URI doesn't match registration
- **Fix**: Ensure `https://api.realdiag.com/smart/callback` is registered exactly

### "Insufficient scopes"
- **Cause**: Missing required scopes
- **Fix**: Add all scopes listed in Step 2

### "Patient not found"
- **Cause**: Using invalid patient ID
- **Fix**: Use test patient IDs: 12724066, 12724067, 12724068

## 📞 Support

- **Cerner Code Console**: https://code-console.cerner.com/
- **Cerner Docs**: https://fhir.cerner.com/
- **RealDiag Guide**: `CERNER_INTEGRATION_GUIDE.md`
- **API Docs**: https://api.realdiag.com/docs

## ⏱️ Timeline Summary

- **Registration**: 2 minutes
- **App Creation**: 3 minutes  
- **Configuration**: 1 minute
- **Testing**: 2 minutes
- **Total**: ~10 minutes from start to working integration!

🎯 **Start now:** https://code-console.cerner.com/
