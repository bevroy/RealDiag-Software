# Phase 4: Mobile App Implementation Plan

## 📱 Overview

**Objective**: Build native iOS and Android apps using React Native for bedside clinical decision support.

**Timeline**: 6-8 weeks (parallel to Phase 3 diagnostic tree expansion)

**Team**: 1-2 mobile developers

## 🎯 Goals

1. **Offline-First**: Work without internet, sync when available
2. **Fast Launch**: App opens in <2 seconds
3. **Voice Input**: Hands-free symptom entry
4. **EHR Integration**: Pull patient data seamlessly
5. **Biometric Auth**: Face ID / Touch ID security

## 📅 Implementation Timeline

### Week 1-2: Project Setup & Core Navigation

**Tasks**:
- [ ] Create React Native TypeScript project
- [ ] Configure iOS and Android build environments
- [ ] Set up navigation (React Navigation 6)
- [ ] Implement authentication screen with biometric auth
- [ ] Create main tab navigation (Home, Search, Patient, Settings)

**Deliverables**:
```
mobile/
├── ios/                  # iOS project
├── android/              # Android project
├── src/
│   ├── navigation/
│   │   └── AppNavigator.tsx
│   ├── screens/
│   │   ├── AuthScreen.tsx
│   │   ├── HomeScreen.tsx
│   │   └── SettingsScreen.tsx
│   └── App.tsx
```

**Testing**:
- App runs on iOS simulator
- App runs on Android emulator
- Biometric auth works (Face ID/Touch ID)
- Navigation transitions smooth

### Week 3-4: Symptom Search & Diagnostic Engine

**Tasks**:
- [ ] Build symptom search UI with autocomplete
- [ ] Implement voice input (react-native-voice)
- [ ] Connect to RealDiag API (`/api/search`)
- [ ] Cache diagnostic rules for offline use (Realm DB)
- [ ] Display differential diagnosis cards
- [ ] Implement swipe gestures for card navigation

**Deliverables**:
```typescript
// src/screens/SearchScreen.tsx
- Voice-activated symptom input
- Real-time autocomplete suggestions
- Differential diagnosis cards
- Offline rule matching

// src/api/diagnostics.ts
- searchSymptoms(query: string)
- getDifferentialDiagnosis(symptoms: string[])
- getWorkupPlan(diagnosis: string)
```

**Testing**:
- Voice input accurate (>90%)
- Offline search works without network
- Results appear in <1 second
- Swipe gestures smooth

### Week 5-6: EHR Integration & Patient View

**Tasks**:
- [ ] Implement SMART on FHIR launch sequence
- [ ] OAuth2 token handling (react-native-keychain)
- [ ] Pull patient data from `/api/integration/ehr/fhir/pull/patient/{id}`
- [ ] Display patient demographics, medications, allergies, conditions
- [ ] Show recent vitals and lab results
- [ ] Context-aware diagnostic suggestions

**Deliverables**:
```typescript
// src/screens/PatientScreen.tsx
- Patient header (name, DOB, MRN)
- Medications list
- Allergies with severity
- Problem list
- Recent vitals chart
- Labs table

// src/api/ehr.ts
- launchSMART(iss: string, launch: string)
- exchangeToken(code: string)
- getPatient(id: string)
```

**Testing**:
- SMART launch works with Cerner sandbox
- Patient data displays correctly
- Token refresh automatic
- Security: encrypted storage

### Week 7-8: Workup Planning & Reports

**Tasks**:
- [ ] Display recommended tests/imaging
- [ ] CPOE order creation UI
- [ ] Generate PDF reports (react-native-pdf-lib)
- [ ] Share via email/secure messaging
- [ ] Export to EHR documentation
- [ ] Polish UI/UX based on testing

**Deliverables**:
```typescript
// src/screens/WorkupScreen.tsx
- Recommended tests cards
- One-tap order creation
- Track pending orders
- Clinical pathway guidance

// src/utils/reporting.ts
- generatePDF(diagnosis, workup, patient)
- shareReport(pdf, method)
- exportToEHR(report)
```

**Testing**:
- PDF generation works (<5 seconds)
- Email sharing functional
- Print to AirPrint printers
- CPOE orders submit successfully

## 🛠️ Technology Stack

```json
{
  "framework": "React Native 0.72+",
  "language": "TypeScript 5.0+",
  "state_management": "Redux Toolkit",
  "networking": "Axios + React Query",
  "ui_library": "React Native Paper (Material Design)",
  "navigation": "React Navigation 6",
  "local_storage": "AsyncStorage (config) + Realm (diagnostic rules)",
  "security": "react-native-keychain (OAuth tokens)",
  "pdf_generation": "react-native-pdf-lib",
  "voice_input": "react-native-voice",
  "biometrics": "@react-native-community/biometrics"
}
```

## 📦 Dependencies

```json
{
  "dependencies": {
    "react": "18.2.0",
    "react-native": "0.72.0",
    "@react-navigation/native": "^6.1.0",
    "@react-navigation/bottom-tabs": "^6.5.0",
    "@react-navigation/stack": "^6.3.0",
    "react-native-paper": "^5.10.0",
    "@reduxjs/toolkit": "^1.9.0",
    "react-redux": "^8.1.0",
    "axios": "^1.5.0",
    "@tanstack/react-query": "^4.35.0",
    "react-native-keychain": "^8.1.0",
    "react-native-voice": "^3.2.0",
    "realm": "^12.2.0",
    "react-native-pdf-lib": "^1.0.0",
    "@react-native-community/biometrics": "^3.0.0",
    "react-native-config": "^1.5.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-native": "^0.72.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "jest": "^29.0.0",
    "react-test-renderer": "18.2.0"
  }
}
```

## 🔐 Security Requirements

### HIPAA Compliance
- [ ] Biometric authentication (Face ID/Touch ID)
- [ ] Automatic session timeout (15 minutes)
- [ ] Encrypted local storage (Keychain for tokens, Realm encryption for data)
- [ ] TLS 1.2+ for all API calls
- [ ] Audit logging for patient data access
- [ ] Secure memory handling (no screenshots of PHI)

### iOS Security
```swift
// ios/RealDiagMobile/Info.plist
<key>NSFaceIDUsageDescription</key>
<string>RealDiag uses Face ID to securely authenticate you</string>
<key>ITSAppUsesNonExemptEncryption</key>
<false/>
```

### Android Security
```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<uses-permission android:name="android.permission.USE_BIOMETRIC" />
<application
  android:allowBackup="false"
  android:usesCleartextTraffic="false">
```

## 🧪 Testing Strategy

### Unit Tests (Jest)
- API client functions
- Redux reducers and actions
- Utility functions (formatting, validation)
- **Target**: >80% code coverage

### Integration Tests
- SMART launch sequence
- Patient data pull and display
- Offline search with cached rules
- **Target**: All critical paths tested

### E2E Tests (Detox)
- Full diagnostic workflow
- EHR integration end-to-end
- Report generation and sharing
- **Target**: Core user journeys covered

### Manual Testing
- Real device testing (iOS 15+, Android 12+)
- Network conditions (offline, slow 3G, WiFi)
- Accessibility (VoiceOver, TalkBack)
- Clinical workflow validation with physicians

## 📊 Performance Targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| App Launch | <2s | Instant access at bedside |
| Search Results | <1s | Real-time diagnostic feedback |
| Patient Data Load | <3s | Network dependent, show loading state |
| PDF Generation | <5s | Acceptable wait for report |
| Offline Mode | Full functionality | Must work without internet |
| Memory Usage | <150MB | Don't impact other medical apps |
| Battery Impact | <5% per hour | Long shifts without recharge |

## 🚀 Deployment

### iOS App Store
1. **Apple Developer Account** ($99/year)
   - Organization: Your medical institution
   - DUNS number required for organizations
   
2. **App Store Connect**
   - Create app listing
   - Screenshots (6.5", 5.5", iPad Pro)
   - Medical app category
   - Age rating: 17+ (Medical/Treatment Info)

3. **Medical Device Classification**
   - Class I device (clinical decision support)
   - FDA guidance: "Clinical Decision Support Software" (2022)
   - Not a regulated medical device (provides recommendations, not diagnoses)

4. **Review Process**
   - Submit via Xcode/Transporter
   - Review time: 1-3 business days
   - Common rejections: Privacy policy, data handling

### Google Play Store
1. **Google Play Developer Account** ($25 one-time)
   
2. **Play Console**
   - Create app listing
   - Screenshots (phone, tablet, 7", 10")
   - Medical category
   - Content rating: Everyone/PEGI 3

3. **Compliance**
   - HIPAA compliance declaration
   - Privacy policy URL required
   - Data safety form (PHI handling)

4. **Review Process**
   - Submit via Play Console
   - Review time: 1-7 days
   - Staged rollout: 1% → 10% → 50% → 100%

## 📱 App Store Listings

### iOS App Store

**Name**: RealDiag - Clinical Decision Support

**Subtitle**: Evidence-Based Diagnostic Tool for Healthcare Providers

**Description**:
```
RealDiag provides instant access to evidence-based diagnostic guidelines at the point of care. Built for physicians, nurse practitioners, and physician assistants working in emergency departments, urgent care, and inpatient settings.

KEY FEATURES:
• Real-time differential diagnosis based on symptom input
• Voice-activated hands-free operation
• EHR integration via SMART on FHIR (Epic, Cerner)
• Offline access to full diagnostic rule database
• Clinical pearls and red flags for each diagnosis
• Recommended workup plans with test interpretations
• Secure patient data handling (HIPAA compliant)

WHO IT'S FOR:
- Emergency Medicine physicians
- Hospitalists and internists
- Family Medicine practitioners
- Urgent Care providers
- Medical residents and students

SECURITY:
- Face ID/Touch ID authentication
- Encrypted local storage
- Automatic session timeout
- No PHI stored on device

Requires valid healthcare provider credentials for full access.
```

**Keywords**:
```
clinical decision support, diagnosis, medical, EMR, EHR, FHIR, SMART, differential diagnosis, evidence-based medicine, clinical guidelines
```

**Screenshots**:
- Home screen with recent searches
- Voice-activated symptom input
- Differential diagnosis cards
- Patient data integration
- Workup recommendations
- Report generation

### Google Play Store

**Short Description**:
```
Evidence-based clinical decision support for healthcare providers. Instant differential diagnosis at the point of care.
```

**Full Description**: (Same as iOS)

**Category**: Medical (Productivity subcategory)

## 📈 Success Metrics

### Adoption
- [ ] 100+ downloads in first month
- [ ] 500+ active users by Month 3
- [ ] 50% weekly retention rate

### Engagement
- [ ] Average 5+ searches per session
- [ ] 70% of users enable EHR integration
- [ ] 40% of users generate reports

### Performance
- [ ] <1% crash rate
- [ ] 4.5+ star rating (App Store & Play Store)
- [ ] <5% uninstall rate

### Clinical Impact
- [ ] Survey: 80%+ find app "very useful"
- [ ] Time savings: Average 3-5 minutes per patient
- [ ] Diagnostic confidence: Self-reported improvement

## 🔄 Post-Launch Roadmap

### Version 1.1 (Month 2)
- [ ] Additional EHR vendors (Allscripts, athenahealth)
- [ ] Dark mode
- [ ] Clinical calculators (CURB-65, Wells score, CHADS2)
- [ ] Favorites and bookmarks

### Version 1.2 (Month 4)
- [ ] Collaborative features (share cases with colleagues)
- [ ] CME tracking
- [ ] Push notifications for new guidelines
- [ ] Apple Watch companion app

### Version 2.0 (Month 6)
- [ ] AI-powered symptom analysis
- [ ] Integration with wearables (patient vitals)
- [ ] Telemedicine support
- [ ] Multi-language support (Spanish, French, German)

## 💰 Budget Estimate

| Item | Cost | Notes |
|------|------|-------|
| Apple Developer Account | $99/year | Required for iOS |
| Google Play Developer Account | $25 one-time | Required for Android |
| Development (6-8 weeks) | $15,000-$30,000 | 1-2 developers @ $75-100/hr |
| Design/UX | $3,000-$5,000 | UI mockups, user flows |
| Testing Devices | $2,000 | 2-3 iOS, 2-3 Android devices |
| App Store Optimization | $1,000 | Keywords, screenshots, description |
| **Total** | **$21,000-$38,000** | One-time development cost |

**Ongoing Costs**:
- Developer accounts: $124/year
- Backend hosting: $25-50/month (Render)
- Push notifications: Free (Firebase)
- Error monitoring: Free (Sentry)

## 🎓 Resources

### Documentation
- React Native: https://reactnative.dev/
- SMART on FHIR: https://docs.smarthealthit.org/
- React Navigation: https://reactnavigation.org/
- Redux Toolkit: https://redux-toolkit.js.org/

### Tutorials
- React Native + TypeScript: https://reactnative.dev/docs/typescript
- FHIR Client: https://github.com/smart-on-fhir/client-js
- Biometric Auth: https://github.com/SelfLender/react-native-biometrics

### Tools
- React Native Debugger: https://github.com/jhen0409/react-native-debugger
- Flipper (Meta): https://fbflipper.com/
- Detox E2E Testing: https://wix.github.io/Detox/

## ✅ Checklist

### Before Starting
- [ ] Review `MOBILE_APP.md` for detailed specs
- [ ] Set up development environment (Xcode, Android Studio)
- [ ] Install React Native CLI and dependencies
- [ ] Create GitHub repository for mobile app code
- [ ] Join Apple Developer Program (if iOS)
- [ ] Register Google Play Developer account (if Android)

### During Development
- [ ] Follow Phase 4 timeline (Weeks 1-8)
- [ ] Write unit tests as you code (TDD)
- [ ] Test on real devices weekly
- [ ] Get feedback from 3-5 physicians
- [ ] Validate HIPAA compliance

### Before Launch
- [ ] Complete App Store/Play Store listings
- [ ] Prepare marketing materials (website, demo video)
- [ ] Train support team
- [ ] Set up analytics (Firebase)
- [ ] Submit for review

## 🚦 Go/No-Go Decision

**Proceed with mobile app development if**:
- ✅ Backend API stable and documented
- ✅ At least 30 diagnostic trees available
- ✅ EHR integration tested with Cerner/Epic
- ✅ Physician feedback positive on web version
- ✅ Budget approved ($25K-40K)
- ✅ 1-2 mobile developers available

**Current Status**:
- ✅ Backend API: Complete and stable
- ⏳ Diagnostic Trees: 20 available, 25 more planned (Phase 3)
- ✅ EHR Integration: Backend 100% complete, awaiting Cerner credentials
- ❓ Physician Feedback: Need to collect
- ❓ Budget: Need approval
- ❓ Mobile Developers: Need to hire/assign

**Recommendation**: Start Phase 3 (diagnostic trees) first, plan mobile app for Month 2-3 after web version has been validated by physicians.

---

**Next Steps**:
1. Review this plan with stakeholders
2. Complete Phase 3 diagnostic tree expansion (4 weeks)
3. Collect physician feedback on web version
4. Secure budget approval
5. Hire mobile developer(s)
6. Begin Week 1 of Phase 4 mobile app development
