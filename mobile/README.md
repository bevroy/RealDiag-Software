# RealDiag Mobile App

Native iOS and Android mobile application for RealDiag Clinical Decision Support System.

## Features

- 🔐 **Secure Authentication** - JWT-based auth with biometric support (Face ID/Touch ID)
- 🔍 **Symptom Search** - Advanced search with voice input and autocomplete
- 🎙️ **Voice Input** - Hands-free symptom entry using speech recognition
- 📱 **Offline Support** - Cache diagnostic rules for offline use with Realm
- 🏥 **EHR Integration** - View patient demographics, medications, allergies, and vitals
- 📊 **Diagnostic Trees** - Interactive visualization of diagnostic criteria
- ⭐ **Favorites & History** - Save frequently used rules and track searches
- 🌙 **Dark Mode Ready** - Theme system prepared for dark mode support

## Tech Stack

- **Framework**: React Native 0.72.6
- **Language**: TypeScript 5.3+
- **State Management**: Redux Toolkit
- **Navigation**: React Navigation 6
- **API Client**: Axios
- **Local Storage**: AsyncStorage + Realm
- **Voice Input**: @react-native-voice/voice
- **Security**: react-native-keychain
- **Icons**: react-native-vector-icons

## Prerequisites

- Node.js 18+ and npm/yarn
- React Native development environment:
  - **iOS**: Xcode 14+, CocoaPods
  - **Android**: Android Studio, JDK 11+
- MacOS required for iOS development

## Installation

### 1. Install Dependencies

```bash
cd mobile
npm install
# or
yarn install
```

### 2. iOS Setup

```bash
cd ios
pod install
cd ..
```

### 3. Android Setup

Ensure Android SDK is installed and `ANDROID_HOME` is set:

```bash
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

## Running the App

### Development Mode

#### iOS
```bash
npm run ios
# or for specific device
npm run ios -- --simulator="iPhone 15 Pro"
```

#### Android
```bash
npm run android
# or for specific device
adb devices  # List devices
npm run android -- --deviceId=<device-id>
```

### Metro Bundler
```bash
npm start
# or
npx react-native start
```

## Project Structure

```
mobile/
├── src/
│   ├── api/              # API client and service layers
│   │   ├── client.ts     # Axios client with interceptors
│   │   ├── auth.ts       # Authentication API
│   │   └── diagnostics.ts # Diagnostics API
│   ├── navigation/       # Navigation configuration
│   │   └── AppNavigator.tsx
│   ├── screens/          # Screen components
│   │   ├── AuthScreen.tsx
│   │   ├── HomeScreen.tsx
│   │   ├── SearchScreen.tsx
│   │   ├── PatientScreen.tsx
│   │   ├── SettingsScreen.tsx
│   │   └── TreeDetailScreen.tsx
│   ├── store/            # Redux store and slices
│   │   ├── store.ts
│   │   └── slices/
│   │       ├── authSlice.ts
│   │       ├── diagnosticsSlice.ts
│   │       ├── patientSlice.ts
│   │       └── settingsSlice.ts
│   ├── constants/        # App constants and theme
│   │   ├── index.ts
│   │   └── theme.ts
│   ├── types/            # TypeScript type definitions
│   │   └── index.ts
│   └── App.tsx           # Main app component
├── ios/                  # iOS native project
├── android/              # Android native project
├── package.json
└── tsconfig.json
```

## Configuration

### API Endpoint

Update `src/constants/index.ts`:

```typescript
export const API_BASE_URL = 'https://realdiag-software.onrender.com';
```

### Theme Customization

Edit `src/constants/theme.ts` to customize colors, typography, and spacing.

## Key Features Implementation

### Authentication

- Login with email/password
- Secure token storage using react-native-keychain
- Auto-refresh token on app launch
- Biometric authentication support

### Search

- Real-time symptom search with debouncing
- Voice input integration
- Search history tracking
- Autocomplete suggestions

### Offline Mode

- Diagnostic rules cached in Realm database
- Automatic sync when online
- Offline indicator in UI

### Patient Data

- EHR integration via backend API
- View demographics, medications, allergies
- Display recent vitals
- Secure data handling

## Testing

### Test Users

Use these accounts for testing:

```
Admin: admin@realdiag.org / RealDiag2024!
Provider: provider@realdiag.org / Provider123!
Doctor: doctor@example.com / Doctor123!
Patient: patient@example.com / Patient123!
```

### Running Tests

```bash
npm test
# or
npm run test:watch
```

## Building for Production

### iOS

1. Open `ios/RealDiag.xcworkspace` in Xcode
2. Select Product > Archive
3. Distribute to App Store Connect

```bash
# Or use fastlane
cd ios
fastlane ios release
```

### Android

```bash
cd android
./gradlew assembleRelease
# APK will be at: android/app/build/outputs/apk/release/app-release.apk

# For App Bundle (Google Play)
./gradlew bundleRelease
# AAB will be at: android/app/build/outputs/bundle/release/app-release.aab
```

## Environment Variables

Create `.env` file:

```env
API_BASE_URL=https://realdiag-software.onrender.com
API_TIMEOUT=30000
ENABLE_LOGGING=true
```

## Troubleshooting

### iOS Build Issues

```bash
cd ios
pod deintegrate
pod install
cd ..
npm run ios
```

### Android Build Issues

```bash
cd android
./gradlew clean
cd ..
npm run android
```

### Metro Bundler Issues

```bash
npx react-native start --reset-cache
```

### Common Errors

1. **"Unable to resolve module"** - Clear cache and reinstall:
   ```bash
   rm -rf node_modules
   npm install
   npx react-native start --reset-cache
   ```

2. **iOS Simulator not found** - List available simulators:
   ```bash
   xcrun simctl list devices
   ```

3. **Android emulator issues** - Start emulator first:
   ```bash
   emulator -avd Pixel_5_API_33
   ```

## Security Considerations

- ✅ Tokens stored in device keychain (not AsyncStorage)
- ✅ HTTPS-only API communication
- ✅ Biometric authentication option
- ✅ Auto-logout on token expiration
- ✅ Sensitive data encrypted at rest
- ⚠️ Enable certificate pinning for production
- ⚠️ Implement root detection
- ⚠️ Add code obfuscation

## Performance Optimization

- Image optimization with FastImage
- List virtualization with FlatList
- Memoization of expensive components
- Lazy loading of screens
- Bundle size optimization

## Deployment Checklist

- [ ] Update version in package.json and native files
- [ ] Configure production API endpoint
- [ ] Enable ProGuard (Android)
- [ ] Add app icons and splash screens
- [ ] Test on physical devices
- [ ] Run security audit
- [ ] Configure crash reporting (Sentry/Firebase)
- [ ] Set up analytics
- [ ] Prepare store listings
- [ ] Create privacy policy URL

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines.

## License

See [LICENSE](../LICENSE) file.

## Support

For issues and questions:
- GitHub Issues: https://github.com/your-org/realdiag/issues
- Email: support@realdiag.org

---

**⚠️ Medical Disclaimer**: This app is a clinical decision support tool and should not replace professional medical judgment. Always consider patient context and clinical expertise.
