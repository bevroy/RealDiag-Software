# RealDiag Mobile App - React Native

## Overview

The RealDiag mobile app provides bedside clinical decision support for healthcare providers. Built with React Native, it offers the full diagnostic capabilities of RealDiag on iOS and Android devices.

## Features

### 🔍 Symptom Search
- Quick symptom entry with autocomplete
- Voice input for hands-free operation
- Recent searches history
- Offline caching of rule database

### 📊 Patient Integration
- Pull patient data from EHR via FHIR API
- Display current medications, allergies, conditions
- Review recent vitals and labs
- Context-aware diagnostic suggestions

### 📋 Differential Diagnosis
- Real-time matching as symptoms are entered
- Swipe through diagnostic possibilities
- Expandable cards with clinical pearls
- Filter by specialty or urgency

### 🔬 Workup Planning
- Recommended tests displayed prominently
- One-tap CPOE order creation
- Track pending orders and results
- Clinical pathway guidance

### 📄 Report Generation
- Generate PDF reports on device
- Share via email, secure messaging
- Print to nearby AirPrint printers
- Export to EHR documentation

### 🔐 Security
- Biometric authentication (Face ID, Touch ID)
- Encrypted local storage
- Automatic session timeout
- HIPAA-compliant data handling

## Technology Stack

```json
{
  "framework": "React Native 0.72+",
  "language": "TypeScript",
  "state_management": "Redux Toolkit",
  "networking": "Axios + React Query",
  "ui_library": "React Native Paper",
  "navigation": "React Navigation 6",
  "local_storage": "AsyncStorage + Realm",
  "security": "react-native-keychain",
  "pdf_generation": "react-native-pdf-lib",
  "voice_input": "react-native-voice"
}
```

## Project Structure

```
mobile/
├── android/               # Android native code
├── ios/                   # iOS native code
├── src/
│   ├── api/              # API client and hooks
│   │   ├── client.ts
│   │   ├── diagnostics.ts
│   │   ├── ehr.ts
│   │   └── hooks.ts
│   ├── components/       # Reusable components
│   │   ├── DiagnosticCard.tsx
│   │   ├── SymptomInput.tsx
│   │   ├── PatientHeader.tsx
│   │   └── WorkupList.tsx
│   ├── screens/          # App screens
│   │   ├── HomeScreen.tsx
│   │   ├── SearchScreen.tsx
│   │   ├── DiagnosticDetailScreen.tsx
│   │   ├── PatientScreen.tsx
│   │   └── SettingsScreen.tsx
│   ├── store/            # Redux store
│   │   ├── slices/
│   │   │   ├── authSlice.ts
│   │   │   ├── patientSlice.ts
│   │   │   └── diagnosticSlice.ts
│   │   └── store.ts
│   ├── navigation/       # Navigation configuration
│   │   └── AppNavigator.tsx
│   ├── utils/            # Utilities
│   │   ├── security.ts
│   │   ├── offline.ts
│   │   └── formatting.ts
│   └── App.tsx           # Root component
├── package.json
└── tsconfig.json
```

## Setup Instructions

### Prerequisites

```bash
# Install Node.js 18+
brew install node

# Install React Native CLI
npm install -g react-native-cli

# iOS only: Install CocoaPods
sudo gem install cocoapods

# Android only: Install Android Studio
# Download from https://developer.android.com/studio
```

### Create Project

```bash
# Create new React Native project
npx react-native init RealDiagMobile --template react-native-template-typescript

cd RealDiagMobile

# Install dependencies
npm install @react-navigation/native @react-navigation/stack
npm install react-native-paper
npm install @reduxjs/toolkit react-redux
npm install axios react-query
npm install react-native-keychain
npm install react-native-voice
npm install realm
npm install react-native-pdf-lib

# iOS specific
cd ios && pod install && cd ..
```

### Configuration

Create `src/config.ts`:

```typescript
export const API_CONFIG = {
  BASE_URL: __DEV__ 
    ? 'http://localhost:8000' 
    : 'https://realdiag-software.onrender.com',
  TIMEOUT: 30000,
  API_KEY: '', // Set via secure storage
};

export const FHIR_CONFIG = {
  BASE_URL: '', // Configure in settings
  AUTH_TYPE: 'bearer',
};

export const SECURITY = {
  SESSION_TIMEOUT: 15 * 60 * 1000, // 15 minutes
  BIOMETRIC_ENABLED: true,
  ENCRYPTION_KEY_ALIAS: 'realdiag_key',
};
```

## Key Components

### SymptomSearchScreen

```typescript
import React, { useState } from 'react';
import { View, FlatList } from 'react-native';
import { Searchbar, Card, Chip } from 'react-native-paper';
import { useQuery } from 'react-query';
import { searchSymptoms } from '../api/diagnostics';

export const SymptomSearchScreen = () => {
  const [symptoms, setSymptoms] = useState<string[]>([]);
  const [query, setQuery] = useState('');

  const { data: results, isLoading } = useQuery(
    ['search', symptoms],
    () => searchSymptoms(symptoms),
    { enabled: symptoms.length > 0 }
  );

  return (
    <View style={styles.container}>
      <Searchbar
        placeholder="Enter symptoms..."
        value={query}
        onChangeText={setQuery}
        onSubmitEditing={() => {
          if (query) {
            setSymptoms([...symptoms, query]);
            setQuery('');
          }
        }}
      />
      
      <View style={styles.chipContainer}>
        {symptoms.map((symptom, idx) => (
          <Chip 
            key={idx}
            onClose={() => setSymptoms(symptoms.filter((_, i) => i !== idx))}
          >
            {symptom}
          </Chip>
        ))}
      </View>

      <FlatList
        data={results?.diagnoses}
        renderItem={({ item }) => (
          <DiagnosticCard diagnosis={item} />
        )}
        keyExtractor={(item) => item.rule_id}
      />
    </View>
  );
};
```

### PatientDataScreen

```typescript
import React, { useEffect } from 'react';
import { ScrollView, View } from 'react-native';
import { Card, Title, Paragraph, List } from 'react-native-paper';
import { useQuery } from 'react-query';
import { pullPatientData } from '../api/ehr';

export const PatientDataScreen = ({ route }) => {
  const { patientId } = route.params;

  const { data: patient, isLoading } = useQuery(
    ['patient', patientId],
    () => pullPatientData(patientId)
  );

  if (isLoading) return <LoadingSpinner />;

  return (
    <ScrollView style={styles.container}>
      <Card>
        <Card.Content>
          <Title>{patient.name}</Title>
          <Paragraph>DOB: {patient.birth_date}</Paragraph>
          <Paragraph>Age: {patient.age}</Paragraph>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Allergies</Title>
          {patient.allergies.map((allergy, idx) => (
            <Chip key={idx} mode="outlined" style={styles.allergyChip}>
              {allergy}
            </Chip>
          ))}
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Active Conditions</Title>
          {patient.conditions.map((condition, idx) => (
            <List.Item
              key={idx}
              title={condition.code}
              description={condition.status}
              left={props => <List.Icon {...props} icon="medical-bag" />}
            />
          ))}
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Current Medications</Title>
          {patient.medications.map((med, idx) => (
            <List.Item
              key={idx}
              title={med.name}
              description={med.status}
              left={props => <List.Icon {...props} icon="pill" />}
            />
          ))}
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Recent Labs</Title>
          {patient.recent_labs.map((lab, idx) => (
            <List.Item
              key={idx}
              title={lab.test}
              description={`${lab.value} - ${lab.date}`}
              left={props => <List.Icon {...props} icon="test-tube" />}
            />
          ))}
        </Card.Content>
      </Card>
    </ScrollView>
  );
};
```

### CPOEOrderScreen

```typescript
import React, { useState } from 'react';
import { View, ScrollView } from 'react-native';
import { Button, TextInput, RadioButton, Snackbar } from 'react-native-paper';
import { useMutation } from 'react-query';
import { createCPOEOrder } from '../api/ehr';

export const CPOEOrderScreen = ({ route }) => {
  const { diagnosis, patientId } = route.params;
  const [selectedTest, setSelectedTest] = useState('');
  const [priority, setPriority] = useState('routine');
  const [indication, setIndication] = useState('');
  const [snackbarVisible, setSnackbarVisible] = useState(false);

  const orderMutation = useMutation(createCPOEOrder, {
    onSuccess: () => {
      setSnackbarVisible(true);
    }
  });

  const handleOrder = () => {
    orderMutation.mutate({
      order_type: 'lab',
      description: selectedTest,
      patient_id: patientId,
      priority,
      ordering_provider: 'Current User', // From auth context
      clinical_indication: indication,
      diagnosis_codes: diagnosis.icd10
    });
  };

  return (
    <ScrollView style={styles.container}>
      <Title>Order Test/Referral</Title>
      
      <Subheading>Recommended Tests:</Subheading>
      <RadioButton.Group 
        onValueChange={setSelectedTest} 
        value={selectedTest}
      >
        {diagnosis.tests.map((test, idx) => (
          <RadioButton.Item key={idx} label={test} value={test} />
        ))}
      </RadioButton.Group>

      <TextInput
        label="Clinical Indication"
        value={indication}
        onChangeText={setIndication}
        multiline
        numberOfLines={3}
      />

      <Subheading>Priority:</Subheading>
      <RadioButton.Group onValueChange={setPriority} value={priority}>
        <RadioButton.Item label="STAT" value="stat" />
        <RadioButton.Item label="Urgent" value="urgent" />
        <RadioButton.Item label="Routine" value="routine" />
      </RadioButton.Group>

      <Button 
        mode="contained" 
        onPress={handleOrder}
        loading={orderMutation.isLoading}
        disabled={!selectedTest}
      >
        Create Order
      </Button>

      <Snackbar
        visible={snackbarVisible}
        onDismiss={() => setSnackbarVisible(false)}
        duration={3000}
      >
        Order created successfully!
      </Snackbar>
    </ScrollView>
  );
};
```

## API Integration

Create `src/api/client.ts`:

```typescript
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_CONFIG } from '../config';

const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
});

// Add API key to all requests
apiClient.interceptors.request.use(async (config) => {
  const apiKey = await AsyncStorage.getItem('api_key');
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey;
  }
  return config;
});

// Handle token expiration
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Navigate to login
      await AsyncStorage.removeItem('api_key');
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

## Security Implementation

```typescript
// src/utils/security.ts
import * as Keychain from 'react-native-keychain';
import * as LocalAuthentication from 'expo-local-authentication';

export const securelySaveApiKey = async (apiKey: string) => {
  await Keychain.setGenericPassword('realdiag', apiKey, {
    accessControl: Keychain.ACCESS_CONTROL.BIOMETRY_ANY,
    accessible: Keychain.ACCESSIBLE.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
  });
};

export const securelyRetrieveApiKey = async (): Promise<string | null> => {
  const hasHardware = await LocalAuthentication.hasHardwareAsync();
  const isEnrolled = await LocalAuthentication.isEnrolledAsync();
  
  if (hasHardware && isEnrolled) {
    const result = await LocalAuthentication.authenticateAsync({
      promptMessage: 'Authenticate to access RealDiag',
    });
    
    if (result.success) {
      const credentials = await Keychain.getGenericPassword();
      return credentials ? credentials.password : null;
    }
  }
  
  return null;
};

export const clearSecureStorage = async () => {
  await Keychain.resetGenericPassword();
};
```

## Offline Support

```typescript
// src/utils/offline.ts
import Realm from 'realm';

const DiagnosticRuleSchema = {
  name: 'DiagnosticRule',
  primaryKey: 'rule_id',
  properties: {
    rule_id: 'string',
    label: 'string',
    family: 'string',
    presentations: 'string[]',
    clinical_pearls: 'string[]',
    management: 'string[]',
    tests: 'string[]',
    referrals: 'string[]',
    icd10: 'string[]',
    snomed: 'int[]',
    last_updated: 'date',
  }
};

export const syncRulesToLocal = async (rules: any[]) => {
  const realm = await Realm.open({
    schema: [DiagnosticRuleSchema],
  });
  
  realm.write(() => {
    rules.forEach(rule => {
      realm.create('DiagnosticRule', {
        ...rule,
        last_updated: new Date(),
      }, Realm.UpdateMode.Modified);
    });
  });
  
  realm.close();
};

export const searchLocalRules = async (symptoms: string[]) => {
  const realm = await Realm.open({
    schema: [DiagnosticRuleSchema],
  });
  
  // Simple text search across presentations
  const results = realm.objects('DiagnosticRule').filtered(
    symptoms.map(s => `presentations CONTAINS[c] "${s}"`).join(' OR ')
  );
  
  const array = Array.from(results);
  realm.close();
  
  return array;
};
```

## Building & Distribution

### iOS

```bash
# Development build
npx react-native run-ios

# Production build
cd ios
xcodebuild -workspace RealDiagMobile.xcworkspace \
  -scheme RealDiagMobile \
  -configuration Release \
  -archivePath build/RealDiagMobile.xcarchive \
  archive

# Upload to App Store
xcodebuild -exportArchive \
  -archivePath build/RealDiagMobile.xcarchive \
  -exportPath build \
  -exportOptionsPlist exportOptions.plist
```

### Android

```bash
# Development build
npx react-native run-android

# Production build
cd android
./gradlew assembleRelease

# APK location: android/app/build/outputs/apk/release/app-release.apk

# Upload to Play Store
./gradlew bundleRelease
# AAB location: android/app/build/outputs/bundle/release/app-release.aab
```

## Testing

```bash
# Unit tests
npm test

# E2E tests (Detox)
npm install -g detox-cli
detox build --configuration ios.sim.debug
detox test --configuration ios.sim.debug

# Coverage
npm run test:coverage
```

## Deployment Checklist

- [ ] Configure API endpoints for production
- [ ] Set up secure API key storage
- [ ] Enable biometric authentication
- [ ] Implement offline mode with Realm
- [ ] Add crash reporting (Sentry)
- [ ] Set up analytics (Firebase)
- [ ] Create app icons and splash screens
- [ ] Write user documentation
- [ ] Conduct security audit
- [ ] Test on physical devices (iOS & Android)
- [ ] Submit to App Store review
- [ ] Submit to Play Store review
- [ ] Create promotional materials

## Future Enhancements

- **Voice Commands**: "Search for chest pain and dyspnea"
- **Apple Watch Integration**: Quick symptom logging
- **Barcode Scanner**: Scan patient wristbands for ID
- **Clinical Calculator**: Integrated TIMI, CHADS2, etc.
- **Photo Documentation**: Attach photos to reports
- **Telemedicine Integration**: Connect with video consults
- **Push Notifications**: Alert for critical updates
- **Dark Mode**: Full theme support

## Support

For mobile app development assistance:
- Email: support@realdiag.com
- Slack: #mobile-dev
- Documentation: https://docs.realdiag.com/mobile

---

**Note**: This is a comprehensive specification. Actual development would require a separate React Native project and approximately 3-6 months of development time with a dedicated mobile team.
