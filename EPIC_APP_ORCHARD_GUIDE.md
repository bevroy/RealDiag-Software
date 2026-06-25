# Epic App Orchard Registration Guide

## Overview
This guide walks you through registering RealDiag with **Epic App Orchard** to enable FHIR R4 and SMART on FHIR integration with Epic EHR systems used by thousands of hospitals.

## Why Epic Integration?

- **Market Coverage**: Epic is used by ~50% of US hospitals
- **Major Health Systems**: Mayo Clinic, Cleveland Clinic, Johns Hopkins, Stanford, UCSF
- **FHIR Standards**: Full FHIR R4 support with SMART on FHIR launch
- **Patient Access**: Epic MyChart integration for patient-facing apps

## Prerequisites

Before you begin:
- [ ] RealDiag production site live (www.realdiag.com) ✅
- [ ] Backend API accessible (api.realdiag.com) ✅
- [ ] Valid SSL certificates ✅
- [ ] Company/organization details ready
- [ ] Screenshots of RealDiag interface
- [ ] Privacy policy and terms of service

## Step 1: Create Epic App Orchard Account (10 minutes)

1. **Go to Epic App Orchard**
   - Navigate to: https://apporchard.epic.com/
   - Click "Join the App Orchard" or "Register"

2. **Complete Registration**
   - **Organization Name**: RealDiag, LLC
   - **Organization Type**: Healthcare Technology Vendor
   - **Contact Email**: Your business email
   - **Contact Name**: Your name
   - **Phone Number**: Business phone

3. **Verify Email**
   - Check your email for verification link
   - Click link to activate account

4. **Complete Profile**
   - Add company logo
   - Provide company address
   - Add website: www.realdiag.com

## Step 2: Create New App (20 minutes)

1. **Navigate to "My Apps"**
   - Click "Create New App" button

2. **Basic Information**
   - **App Name**: RealDiag - Clinical Decision Support
   - **Short Description**: Evidence-based diagnostic decision trees and symptom-based search for clinicians
   - **Category**: Clinical Decision Support
   - **Sub-category**: Diagnosis Assistant

3. **App Details**
   ```
   Full Description:
   RealDiag provides evidence-based diagnostic decision trees across 17 medical 
   specialties with 268 diagnoses. Clinicians can search by symptoms to receive 
   ranked differential diagnoses with clinical pearls, management protocols, and 
   recommended diagnostic tests. FHIR integration pulls patient demographics, 
   conditions, medications, and recent lab results to enhance diagnostic accuracy.
   
   Key Features:
   - Symptom-based diagnostic search
   - 17 medical specialties (Cardiology, Neurology, Emergency Medicine, etc.)
   - Bayesian likelihood ranking of diagnoses
   - Clinical pearls and management protocols
   - FHIR R4 patient data integration
   - SMART on FHIR EHR launch support
   ```

4. **Screenshots**
   Upload 3-5 screenshots:
   - Home page (www.realdiag.com)
   - Symptom search interface
   - Diagnostic results page
   - Patient data integration (mock if needed)

5. **Target Users**
   - [x] Physicians
   - [x] Nurse Practitioners
   - [x] Physician Assistants
   - [x] Medical Students
   - [x] Residents

## Step 3: Configure SMART on FHIR (15 minutes)

1. **Select Integration Type**
   - Choose: **SMART on FHIR**
   - Select: **Provider-facing (EHR launch)**

2. **OAuth2 Configuration**
   
   **Redirect URIs** (add both):
   ```
   https://www.realdiag.com/auth/callback
   https://api.realdiag.com/integration/smart/callback
   ```
   
   **Launch URI**:
   ```
   https://www.realdiag.com/launch
   ```
   
   **JWKS URI** (if using JWT):
   ```
   https://api.realdiag.com/.well-known/jwks.json
   ```

3. **FHIR Scopes Requested**
   
   Select these scopes:
   - [x] `patient/Patient.read` - Patient demographics
   - [x] `patient/Condition.read` - Medical conditions
   - [x] `patient/Observation.read` - Vitals and labs
   - [x] `patient/MedicationRequest.read` - Current medications
   - [x] `patient/AllergyIntolerance.read` - Allergies
   - [x] `patient/Encounter.read` - Encounters
   - [x] `launch` - SMART launch context
   - [x] `launch/patient` - Patient context
   - [x] `openid` - OpenID Connect
   - [x] `fhirUser` - Identify clinician

4. **App Type**
   - Select: **Confidential Client** (server-side app with secret)

## Step 4: Security & Compliance (10 minutes)

1. **Privacy Policy**
   - URL: https://www.realdiag.com/privacy
   - Upload PDF copy

2. **Terms of Service**
   - URL: https://www.realdiag.com/terms
   - Upload PDF copy

3. **Security Attestation**
   - [x] Data encrypted in transit (HTTPS/TLS)
   - [x] Data encrypted at rest
   - [x] HIPAA compliance measures in place
   - [x] Regular security audits
   - [x] Incident response plan

4. **Data Handling**
   ```
   Data Storage:
   - Patient data accessed via FHIR is not permanently stored
   - Only session-level caching for performance
   - No PHI stored in application database
   - All FHIR queries use OAuth2 tokens with short expiration
   
   Data Use:
   - Patient data used solely for diagnostic decision support
   - No data sold or shared with third parties
   - No marketing use of patient information
   ```

## Step 5: Submit for Review

1. **Review Checklist**
   - [ ] All required fields completed
   - [ ] Screenshots uploaded
   - [ ] FHIR scopes justified
   - [ ] Redirect URIs correct
   - [ ] Privacy policy accessible
   - [ ] Terms of service accessible

2. **Submit Application**
   - Click "Submit for Review"
   - Epic reviews within 2-4 weeks

3. **Track Status**
   - Monitor status in App Orchard dashboard
   - Respond to any Epic questions promptly

## Step 6: Obtain Credentials (After Approval)

Once approved, Epic provides:

1. **Production Credentials**
   ```
   Client ID: <epic-provided-client-id>
   Client Secret: <epic-provided-client-secret>
   ```

2. **Sandbox Credentials** (for testing)
   ```
   Sandbox Client ID: <sandbox-client-id>
   Sandbox Client Secret: <sandbox-client-secret>
   ```

3. **FHIR Endpoints**
   ```
   Production: https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/
   Sandbox: https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/
   ```

## Step 7: Configure RealDiag Backend

Add credentials to Render environment variables:

```bash
# Epic Production
EPIC_CLIENT_ID=<your-client-id>
EPIC_CLIENT_SECRET=<your-client-secret>
EPIC_FHIR_BASE_URL=https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/

# Epic Sandbox (for testing)
EPIC_SANDBOX_CLIENT_ID=<sandbox-client-id>
EPIC_SANDBOX_CLIENT_SECRET=<sandbox-client-secret>
EPIC_SANDBOX_FHIR_BASE_URL=https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/
```

## Step 8: Test Integration

1. **Test with Epic Sandbox**
   ```bash
   # Configure sandbox
   curl -X POST https://api.realdiag.com/integration/ehr/fhir/configure \
     -H "Content-Type: application/json" \
     -d '{
       "config_name": "epic_sandbox",
       "base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/",
       "auth_type": "oauth2",
       "client_id": "'"$EPIC_SANDBOX_CLIENT_ID"'",
       "client_secret": "'"$EPIC_SANDBOX_CLIENT_SECRET"'"
     }'
   
   # Test patient search
   curl "https://api.realdiag.com/integration/ehr/fhir/search/patients?name=Jason"
   
   # Pull patient data
   curl "https://api.realdiag.com/integration/ehr/fhir/pull/patient/Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB"
   ```

2. **Test SMART Launch** (requires Epic sandbox account)
   - Go to Epic's sandbox: https://fhir.epic.com/
   - Launch RealDiag app from sandbox EHR
   - Verify patient context loads correctly

## Epic Sandbox Test Patients

Epic provides test patients in sandbox:

| Name | Patient ID | Use Case |
|------|-----------|----------|
| Jason Argonaut | Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB | General testing |
| Jessica Argonaut | eq081-VQEgP8drUUqCWzHfw3 | Pediatric patient |
| Derrick Lin | erXuFYUfucBZaryVksYEcMg3 | Multiple conditions |

## Common Issues

### "Invalid redirect_uri"
- **Cause**: Redirect URI doesn't match registration
- **Fix**: Ensure exact match including https:// and trailing slash

### "Invalid scope"
- **Cause**: Requesting scope not approved
- **Fix**: Only request scopes selected during registration

### "Token expired"
- **Cause**: OAuth2 token expiration (typically 1 hour)
- **Fix**: Implement token refresh logic

### "Patient not found"
- **Cause**: Using wrong patient ID format
- **Fix**: Use Epic's FHIR format (includes periods and hyphens)

## Production Deployment Checklist

Before going live with Epic production:

- [ ] App approved by Epic (status: "Live")
- [ ] Production credentials received
- [ ] Environment variables configured on Render
- [ ] Privacy policy live and accessible
- [ ] Terms of service live and accessible
- [ ] SSL certificates valid
- [ ] SMART launch flow tested in sandbox
- [ ] Error handling implemented
- [ ] Token refresh logic working
- [ ] Logging and monitoring active (Sentry)
- [ ] Support contact information published

## Epic Resources

- **App Orchard**: https://apporchard.epic.com/
- **FHIR Documentation**: https://fhir.epic.com/Documentation
- **SMART on FHIR**: https://fhir.epic.com/Documentation?docId=oauth2
- **API Sandbox**: https://fhir.epic.com/
- **Support**: apporchard@epic.com

## Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Account creation | 10 min | ⏳ Ready |
| App registration | 30 min | ⏳ Ready |
| Epic review | 2-4 weeks | ⏳ Pending submission |
| Sandbox testing | 1 week | ⏳ After credentials |
| Production launch | Immediate | ⏳ After testing |

**Total Time**: ~3-5 weeks from submission to production

## Next Steps

1. **Register on App Orchard** - Start immediately
2. **While waiting for approval**:
   - Test with Epic's public sandbox (limited access)
   - Implement OAuth2 flow
   - Build patient data UI
3. **After credentials received**:
   - Full sandbox testing
   - Production configuration
   - Launch to Epic customers

## Support

For Epic-specific questions:
- Email: apporchard@epic.com
- Documentation: https://fhir.epic.com/
- Community: Epic UserWeb (requires healthcare org credentials)

For RealDiag integration support:
- Check documentation in `/docs/EHR_INTEGRATION.md`
- Review code: `backend/services/ehr_integration.py`
- API docs: https://api.realdiag.com/docs#/integration
