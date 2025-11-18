# Mobile Features & Offline Capabilities 📱

## Overview

RealDiag now includes comprehensive mobile optimization and offline capabilities, designed for clinicians working in the field with poor connectivity (ERs, rural areas, disaster zones). These features ensure uninterrupted access to diagnostic support tools.

**Bundle Impact**: The mobile features add ~2.9 kB to the symptom-search page (34.6 kB vs 31.7 kB previous).

---

## Features

### 1. Enhanced PWA Offline Capabilities ✈️

**Service Worker v3.0.0** with comprehensive offline support:
- **IndexedDB Storage**: 5 object stores (rules, searches, favorites, syncQueue, userData)
- **Multiple Cache Strategies**:
  - `CACHE_NAME`: Core app assets
  - `RUNTIME_CACHE`: Runtime-generated resources
  - `RULES_CACHE`: Diagnostic rules
  - `API_CACHE`: API responses
  - `IMAGES_CACHE`: Images and media
- **Background Sync**: Automatic data synchronization when connection restored
- **Offline Queue**: Mutations queued and synced when online
- **Connection Monitoring**: Real-time online/offline status detection

**File**: `frontend/public/sw.js`

**Key Functions**:
- `initDB()`: Initialize IndexedDB
- `saveToStore()`, `getFromStore()`, `getAllFromStore()`: Data operations
- `syncSearches()`, `syncFavorites()`, `syncQueuedRequests()`: Background sync handlers

---

### 2. Download Entire Rule Database 💾

Download all diagnostic rules for complete offline access:

**Features**:
- **Progress Tracking**: Real-time download progress (0-100%)
- **Specialty Breakdown**: View rules by medical specialty
- **Storage Statistics**: See counts and sizes of offline data
- **Rule Management**: Clear offline data when needed

**UI Location**: Mobile Features panel (📱 button) → "Download All Rules"

**File**: `frontend/utils/offlineManager.js`

**Key Functions**:
```javascript
// Download all rules with progress callback
await downloadAllRules(apiBase, (progress) => {
  console.log(`Downloaded ${progress}%`);
});

// Get storage statistics
const stats = await getOfflineStats();
console.log(stats.rules.count); // Number of cached rules
console.log(stats.rules.byFamily); // Rules by specialty

// Clear all offline data
await clearAllOfflineData();
```

**Storage Breakdown**:
- Rules by specialty (e.g., Neurology: 25, Cardiology: 30)
- Search history count
- Favorites count
- Total storage usage

---

### 3. Sync Search History 🔄

Automatic synchronization of search history across devices:

**Features**:
- **Offline Queue**: Searches saved locally when offline
- **Auto-Sync**: Syncs to server when connection restored
- **Conflict Resolution**: Last-write-wins strategy
- **Privacy**: Search history encrypted in transit

**Background Sync**:
- Triggered automatically on reconnection
- Manual sync: `requestBackgroundSync('search-sync')`
- Retries with exponential backoff

**File**: `frontend/utils/offlineManager.js`

**Key Functions**:
```javascript
// Save search locally
await saveSearch({
  symptoms: ['headache', 'dizziness'],
  results: [...],
  timestamp: Date.now()
});

// Get unsynced searches
const unsynced = await getUnsyncedSearches();

// Mark search as synced
await markSearchSynced(searchId);
```

---

### 4. Voice Input for Symptom Entry 🎤

Hands-free symptom entry using Web Speech API:

**Features**:
- **Medical Term Recognition**: Normalizes common misrecognitions
  - "heading" → "headache"
  - "cuffing" → "cough"
  - "sob" → "shortness of breath"
- **Voice Commands**:
  - "add symptom [name]" - Add specific symptom
  - "search" - Execute diagnostic search
  - "clear all" - Clear all symptoms
  - "help" - List available commands
- **Visual Feedback**: Listening indicator, transcript display
- **Text-to-Speech**: Audible confirmations
- **Permission Handling**: Microphone access request

**UI Location**: 🎤 button next to symptom input field

**File**: `frontend/utils/voiceInput.js`

**Key Functions**:
```javascript
// Check browser support
if (isVoiceInputSupported()) {
  // Create recognition instance
  const recognition = createVoiceRecognition({
    continuous: false,
    interimResults: true,
    lang: 'en-US',
    maxAlternatives: 3
  });

  // Start listening
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    const normalized = normalizeMedicalText(transcript);
    console.log(normalized); // "headache" (not "heading")
  };
  
  recognition.start();
}

// Text-to-speech
speak('Symptom added successfully');
```

**Medical Terms Dictionary**:
- 50+ common medical term corrections
- Phonetic mapping for misheard terms
- Expandable for custom terminology

---

### 5. Barcode Scanner for Patient IDs 📷

Camera-based QR code and barcode scanning:

**Features**:
- **Multiple Formats**: QR code, Code 128, Code 39, EAN-13, UPC-A
- **BarcodeDetector API**: Native browser barcode detection
- **Patient ID Parsing**: Extracts ID from various formats
- **Validation**: Ensures ID format correctness
- **Camera Controls**: Front/back camera selection
- **Visual Feedback**: Bounding box overlay on detection

**UI Location**: 📷 button next to symptom input field

**File**: `frontend/utils/barcodeScanner.js`

**Key Functions**:
```javascript
// Check support
if (isScannerSupported()) {
  // Create detector
  const detector = await createBarcodeDetector(['qr_code', 'code_128']);
  
  // Start camera
  const video = document.getElementById('scanner-video');
  await startCameraStream(video, { facingMode: 'environment' });
  
  // Continuous scanning
  const scanner = startContinuousScanning(detector, video, (result) => {
    if (result.success && result.found) {
      const barcode = result.barcodes[0];
      const parsed = parsePatientID(barcode.rawValue, barcode.format);
      console.log(parsed.patientId); // Extracted patient ID
    }
  });
  
  // Stop scanning
  scanner.stop();
  stopCameraStream(video);
}
```

**Patient ID Formats Supported**:
- Numeric IDs: `12345678`
- Prefixed IDs: `P-12345678`, `PT:12345678`
- QR Code JSON: `{"patientId": "12345678", "name": "John Doe"}`

**Validation Rules**:
- Minimum length: 3 characters
- Maximum length: 20 characters
- Allowed characters: alphanumeric + hyphens
- Auto-removes common prefixes (P, PT)

---

### 6. Touch-Optimized UI 👆

Mobile-first responsive design improvements:

**Features**:
- **44x44px Minimum Touch Targets**: All interactive elements
- **Increased Padding**: Easier tapping on mobile
- **Button Spacing**: Prevents accidental taps
- **Swipe Gestures**: (Planned) Navigate between diagnoses
- **Haptic Feedback**: (Planned) Touch confirmation
- **Mobile Layout**: Optimized for small screens

**Implementation**:
- All buttons use `minHeight: '44px'` and `minWidth: '44px'`
- Gap spacing of 0.5rem minimum between interactive elements
- Flex layouts for responsive button groups
- Fixed-position mobile features panel

**Button Examples**:
```javascript
// Voice input button
<button style={{
  minHeight: '44px',
  minWidth: '44px',
  padding: '0.75rem',
  // ... other styles
}}>🎤</button>

// Barcode scanner button
<button style={{
  minHeight: '44px',
  minWidth: '44px',
  padding: '0.75rem',
  // ... other styles
}}>📷</button>
```

---

## Mobile Features Panel

**Access**: Click the 📱 button in the symptom input section

**Features**:
1. **Connection Status**: Real-time online/offline indicator
2. **Offline Storage Stats**: View cached data counts and specialties
3. **Download Rules**: Button to download all diagnostic rules
4. **Download Progress**: Visual progress bar during download
5. **Feature Status**: Checkmarks for available features:
   - ✅ Voice Input (if supported)
   - ✅ Barcode Scanner (if supported)
   - ✅ Offline Data (if rules downloaded)

---

## Browser Support

### Full Support
- **Chrome 88+**: All features (BarcodeDetector, Web Speech API)
- **Edge 88+**: All features
- **Safari 14+**: Voice input only (no BarcodeDetector)

### Partial Support
- **Firefox 85+**: Voice input with flag enabled, manual barcode scanning
- **Mobile browsers**: Voice input, camera access, offline storage

### Feature Detection
All features include graceful degradation:
```javascript
// Voice input check
if (typeof window !== 'undefined' && isVoiceInputSupported()) {
  // Show voice button
}

// Barcode scanner check
if (typeof window !== 'undefined' && isScannerSupported()) {
  // Show scanner button
}
```

---

## Performance Impact

### Bundle Size
- **Service Worker**: 12 kB (cached separately)
- **offlineManager.js**: 10 kB
- **voiceInput.js**: 8 kB
- **barcodeScanner.js**: 9 kB
- **Total mobile features**: ~39 kB
- **symptom-search.js**: 34.6 kB (from 31.7 kB, +2.9 kB impact)

### Caching Strategy
- **App shell**: Cached indefinitely
- **Diagnostic rules**: Cached on demand, refreshed periodically
- **Search results**: Cached with 1-hour TTL
- **Images**: Cached with 7-day TTL

### Storage Usage
- **IndexedDB**: ~5-10 MB for full rule database
- **Cache Storage**: ~2-3 MB for app assets
- **Total**: ~7-13 MB maximum

---

## Usage Examples

### 1. Download Rules for Offline Use
```javascript
// In symptom-search page
const handleDownloadRules = async () => {
  setIsDownloadingRules(true);
  
  await downloadAllRules(apiBase, (progress) => {
    setDownloadProgress(progress); // 0-100
  });
  
  const stats = await getOfflineStats();
  console.log(`Downloaded ${stats.rules.count} rules`);
  
  setIsDownloadingRules(false);
};
```

### 2. Voice Input Symptom Entry
```javascript
// Initialize voice recognition
const recognition = createVoiceRecognition({
  continuous: false,
  interimResults: true
});

recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  const normalized = normalizeMedicalText(transcript);
  
  // "heading" becomes "headache"
  addSymptom(normalized);
  speak('Symptom added');
};

recognition.start();
```

### 3. Scan Patient ID
```javascript
// Start barcode scanner
const detector = await createBarcodeDetector(['qr_code']);
const video = document.getElementById('scanner-video');

await startCameraStream(video, { facingMode: 'environment' });

const scanner = startContinuousScanning(detector, video, (result) => {
  if (result.success && result.found) {
    const barcode = result.barcodes[0];
    const parsed = parsePatientID(barcode.rawValue, barcode.format);
    
    if (validatePatientID(parsed.patientId).valid) {
      setPatientId(parsed.patientId);
      scanner.stop();
    }
  }
});
```

### 4. Monitor Connection Status
```javascript
// Listen for connection changes
onConnectionChange((online) => {
  if (online) {
    speak('Connection restored');
    requestBackgroundSync('search-sync');
  } else {
    speak('You are now offline. Cached data is available.');
  }
});

// Check current status
const online = isOnline();
console.log(online ? 'Online' : 'Offline');
```

---

## Testing

### Offline Mode Testing
1. Open DevTools → Application → Service Workers
2. Check "Offline" checkbox
3. Verify:
   - ✅ Downloaded rules still accessible
   - ✅ Searches saved to local queue
   - ✅ Connection status indicator shows red
   - ✅ Offline message displayed

### Voice Input Testing
1. Click 🎤 microphone button
2. Grant microphone permission
3. Say: "headache"
4. Verify:
   - ✅ Transcript shows normalized text
   - ✅ Symptom added to list
   - ✅ Audio feedback played

### Barcode Scanner Testing
1. Click 📷 camera button
2. Grant camera permission
3. Point camera at QR code or barcode
4. Verify:
   - ✅ Camera preview displayed
   - ✅ Barcode detected and parsed
   - ✅ Patient ID extracted and validated

### Touch Target Testing
1. Open in mobile browser or DevTools device mode
2. Verify:
   - ✅ All buttons at least 44x44px
   - ✅ Adequate spacing between buttons
   - ✅ No accidental taps

---

## Troubleshooting

### Voice Input Not Working
- **Check browser support**: Chrome/Edge recommended
- **Microphone permission**: Ensure permission granted
- **HTTPS required**: Voice input requires secure context
- **Check DevTools**: Look for speech recognition errors

### Barcode Scanner Not Detected
- **BarcodeDetector API**: Only in Chrome/Edge 88+
- **Camera permission**: Must be granted
- **HTTPS required**: Camera access requires secure context
- **Fallback**: Use manual patient ID entry

### Offline Data Not Syncing
- **Background sync**: Check service worker status in DevTools
- **IndexedDB**: Verify data in Application → IndexedDB
- **Connection**: Ensure device reconnected to network
- **Manual sync**: Click "Download All Rules" again

### Service Worker Not Updating
- **Force update**: DevTools → Application → Service Workers → Update
- **Clear cache**: Clear site data and reload
- **Version**: Check console for service worker version (v3.0.0)

---

## Security Considerations

### Data Privacy
- **Local storage only**: Patient IDs never sent to server unless explicitly saved
- **Encrypted transit**: All network requests use HTTPS
- **No persistent patient data**: Scanned IDs held in memory only
- **User control**: Clear offline data anytime

### Permissions
- **Microphone**: Requested only when voice input activated
- **Camera**: Requested only when barcode scanner opened
- **Storage**: IndexedDB/Cache API used within browser quotas
- **Background sync**: Only for queued searches, not patient data

### Best Practices
- Clear offline data periodically to save space
- Don't store sensitive patient information in search history
- Use barcode scanner for patient ID verification only
- Ensure device screen lock for physical security

---

## Future Enhancements

### Planned Features
- 🚀 **Haptic Feedback**: Touch confirmation vibrations
- 🚀 **Swipe Gestures**: Navigate between diagnosis cards
- 🚀 **Offline Rule Updates**: Delta sync for updated rules only
- 🚀 **Voice Commands**: More natural language processing
- 🚀 **OCR**: Text recognition for patient documents
- 🚀 **Biometric Auth**: Fingerprint/Face ID for security

### Performance Optimizations
- Lazy loading of mobile feature utilities
- Service worker precaching strategies
- IndexedDB query optimization
- Voice recognition accuracy improvements

---

## Credits

- **Service Worker**: Built with Workbox patterns
- **Voice Input**: Web Speech API
- **Barcode Scanner**: BarcodeDetector API
- **Offline Storage**: IndexedDB with Dexie.js patterns
- **UI Components**: Custom React components with inline styles

---

## Related Documentation

- [ADVANCED_FEATURES.md](./ADVANCED_FEATURES.md) - Clinical decision support tools
- [QUICKSTART.md](./QUICKSTART.md) - Getting started guide
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment instructions

---

**Last Updated**: 2025-01-XX  
**Version**: 1.0.0  
**Maintainer**: RealDiag Development Team
