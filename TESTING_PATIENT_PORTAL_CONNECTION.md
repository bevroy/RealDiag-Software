# Testing Patient EMR Portal Connection

This guide explains how to test the patient EMR portal connection feature.

## Overview

Patients can connect RealDiag to their patient portal (MyChart, Cerner, etc.) to automatically import:
- Demographics
- Medications
- Allergies
- Lab results
- Vital signs

## Test Options

### Option 1: Use Test Patient Account (Quickest)

```bash
# 1. Login as the test patient
URL: http://localhost:3000/login
Email: patient@example.com
Password: Patient123!

# 2. Navigate to Health Manager
Click "Health Manager" in navigation

# 3. View EHR Integration Section
Scroll to "Electronic Health Records" section

# 4. Choose an EHR system to connect
- MyChart (Epic)
- Cerner Health
- Allscripts
- athenahealth
- Apple Health Records

# 5. Click "Connect"
This will initiate OAuth flow (currently mock/demo mode)
```

### Option 2: Test API Endpoints Directly

```bash
# Get auth token for patient user
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "password": "Patient123!"
  }'

# Save the token from response
TOKEN="your_token_here"

# Initiate EHR connection
curl -X POST http://localhost:8000/api/health/ehr/connect \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "ehrSystem": "mychart-epic"
  }'

# This should return an authUrl for OAuth redirect

# After connecting, sync data
curl -X POST http://localhost:8000/api/health/ehr/sync \
  -H "Authorization: Bearer $TOKEN"

# View connected EHR
curl -X GET http://localhost:8000/api/health/ehr/status \
  -H "Authorization: Bearer $TOKEN"

# Disconnect EHR
curl -X DELETE http://localhost:8000/api/health/ehr/disconnect \
  -H "Authorization: Bearer $TOKEN"
```

### Option 3: Test with SMART on FHIR (Production-like)

For testing actual FHIR integration with Epic sandbox:

```bash
# 1. Set up Epic sandbox credentials
# Register at: https://fhir.epic.com/Developer/Apps

# 2. Configure environment variables
export FHIR_BASE_URL="https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"
export SMART_CLIENT_ID="your_epic_client_id"
export SMART_CLIENT_SECRET="your_epic_client_secret"
export SMART_REDIRECT_URI="http://localhost:8000/smart/callback"

# 3. Start backend with these settings
cd backend
python main.py

# 4. Test SMART launch sequence
# Open in browser:
http://localhost:8000/smart/launch?iss=https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4&launch=test123

# This will:
# - Redirect to Epic OAuth
# - User logs in to Epic
# - Returns to /smart/callback with code
# - Exchanges code for access token
# - Shows patient data
```

### Option 4: Run Automated E2E Tests

```bash
# Install test dependencies
pip install playwright pytest-playwright
playwright install

# Run EHR connection test
cd /workspaces/RealDiag-Software
pytest tests/test_e2e_playwright.py::TestEHRIntegration::test_ehr_connection_flow -v

# This test:
# - Logs in as patient
# - Navigates to Health Manager
# - Clicks EHR connection
# - Fills in FHIR endpoint
# - Verifies connection UI
```

## Current Implementation Status

### ✅ Implemented
- Frontend UI for selecting EHR systems
- EHR connection component with OAuth flow
- SMART on FHIR router with launch/callback endpoints
- FHIR client for reading patient data
- Support for Epic, Cerner, Allscripts, athenahealth

### 🔄 Partially Implemented
- OAuth flow redirects (requires actual EHR credentials)
- Patient data parsing from FHIR resources
- Sync functionality (imports data into database)

### ⚠️ Demo Mode
Currently running in **demo/mock mode** because:
- No real EHR credentials configured
- OAuth flow shows mock authorization page
- Returns sample patient data instead of real FHIR data

## Checking Implementation

### 1. Check if EHR endpoints exist

```bash
# Check backend routes
curl http://localhost:8000/docs

# Look for these endpoints:
# POST /api/health/ehr/connect
# POST /api/health/ehr/sync
# GET  /api/health/ehr/status
# DELETE /api/health/ehr/disconnect
# GET /smart/launch
# GET /smart/callback
```

### 2. Check if frontend component exists

```bash
# Look for EHR integration component
ls -la frontend/components/health-manager/EHRIntegration.jsx

# Check if it's imported in Health Manager page
grep -r "EHRIntegration" frontend/pages/
```

### 3. Check database schema

```bash
# Check if patient_ehr_connections table exists
# Login to Supabase dashboard or:
psql $DATABASE_URL -c "\d patient_ehr_connections"

# Should have columns:
# - id
# - user_id
# - ehr_system
# - access_token (encrypted)
# - refresh_token (encrypted)
# - patient_id
# - connected_at
# - last_sync_at
```

## Setting Up Real EHR Connection

To enable real patient portal connections:

### 1. Register with Epic (for MyChart)

```bash
# Go to Epic App Orchard
https://apporchard.epic.com/

# Create SMART on FHIR app
# Get Client ID and Secret

# Add to .env:
SMART_CLIENT_ID=your_epic_client_id
SMART_CLIENT_SECRET=your_epic_secret
FHIR_BASE_URL=https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4
SMART_REDIRECT_URI=https://realdiag-software.onrender.com/smart/callback
```

### 2. Register with Cerner

```bash
# Go to Cerner Developer Portal
https://code-console.cerner.com/

# Create app and get credentials
EHR_VENDOR=cerner
FHIR_BASE_URL=https://fhir-ehr.cerner.com/r4/YOUR_TENANT
EHR_TENANT_ID=your_tenant_id
SMART_CLIENT_ID=your_cerner_client_id
```

### 3. Test with Epic Sandbox

Epic provides test patients:

```bash
# Use Epic sandbox patient IDs:
# - Derrick Lin: Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB
# - Camila Lopez: eq081-VQEgP8drUUqCWzHfw3

# Test credentials available at:
https://fhir.epic.com/Documentation?docId=testpatients
```

## Troubleshooting

### Issue: "EHR connection button does nothing"

```bash
# Check browser console for errors
# Check if API endpoint exists
curl -X POST http://localhost:8000/api/health/ehr/connect \
  -H "Content-Type: application/json" \
  -d '{"ehrSystem": "mychart-epic"}'

# Should return authUrl or error message
```

### Issue: "OAuth redirect fails"

```bash
# Verify redirect URI matches exactly in:
# 1. Epic App Orchard configuration
# 2. Environment variable SMART_REDIRECT_URI
# 3. OAuth authorization request

# Check backend logs:
tail -f logs/realdiag.log | grep -i oauth
```

### Issue: "No patient data after connection"

```bash
# Check if sync was called
curl -X POST http://localhost:8000/api/health/ehr/sync \
  -H "Authorization: Bearer $TOKEN"

# Check FHIR client logs
tail -f logs/realdiag.log | grep -i fhir

# Verify access token is valid
curl -X GET http://localhost:8000/api/health/ehr/status \
  -H "Authorization: Bearer $TOKEN"
```

### Issue: "FHIR endpoint returns 401"

```bash
# Token might be expired
# Check token expiration
# Implement refresh token flow

# Or re-authenticate:
# Disconnect and reconnect EHR
```

## Next Steps

1. **Get Epic Sandbox Credentials** - Register at https://fhir.epic.com/
2. **Configure Real OAuth Flow** - Add credentials to environment
3. **Test with Epic Test Patients** - Use sandbox patient IDs
4. **Implement Data Persistence** - Save synced data to database
5. **Add Refresh Token Logic** - Auto-refresh expired tokens
6. **Expand to More EHRs** - Add Cerner, Allscripts support

## Demo Video Script

For testing the feature in a demo:

1. "Let me show you how patients connect their medical records"
2. Login as patient@example.com
3. Navigate to Health Manager
4. "Here patients can connect to their patient portal - MyChart, Cerner, etc."
5. Click "Connect" on MyChart
6. "In production, this would redirect to Epic's login"
7. "After authorization, we import their medications, allergies, lab results"
8. Show imported data in Health Manager
9. "This gives our AI better context for recommendations"

---

**Need Help?** 
- See: [EPIC_INTEGRATION_GUIDE.md](./EPIC_INTEGRATION_GUIDE.md)
- See: [EHR_INTEGRATION_COMPLETE.md](./EHR_INTEGRATION_COMPLETE.md)
