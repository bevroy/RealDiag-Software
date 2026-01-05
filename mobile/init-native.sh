#!/bin/bash

# RealDiag Mobile - Native Project Initialization Script
# This script initializes iOS and Android native projects for React Native

set -e

echo "🚀 Initializing RealDiag Mobile Native Projects..."

# Check if we're in the mobile directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run from mobile/ directory"
    exit 1
fi

# Backup our custom source files
echo "📦 Backing up custom source files..."
mkdir -p .temp_backup
cp -r src .temp_backup/ 2>/dev/null || true
cp package.json .temp_backup/package.json 2>/dev/null || true
cp tsconfig.json .temp_backup/tsconfig.json 2>/dev/null || true
cp babel.config.js .temp_backup/babel.config.js 2>/dev/null || true
cp metro.config.js .temp_backup/metro.config.js 2>/dev/null || true
cp README.md .temp_backup/README.md 2>/dev/null || true

# Check if React Native CLI is available
if ! command -v npx &> /dev/null; then
    echo "❌ Error: npx not found. Please install Node.js"
    exit 1
fi

echo "📱 Initializing React Native project with TypeScript..."

# Create a temporary directory for initialization
cd ..
TEMP_DIR="RealDiagTemp"

# Initialize React Native project in temp directory
npx react-native@latest init RealDiag --template react-native-template-typescript --directory "$TEMP_DIR" --skip-install

# Copy native files to mobile directory
echo "📂 Copying native project files..."
cp -r "$TEMP_DIR/ios" mobile/
cp -r "$TEMP_DIR/android" mobile/
cp "$TEMP_DIR/App.tsx" mobile/App.tsx.template 2>/dev/null || true
cp "$TEMP_DIR/.watchmanconfig" mobile/ 2>/dev/null || true
cp "$TEMP_DIR/app.json" mobile/ 2>/dev/null || true
cp "$TEMP_DIR/.gitignore" mobile/.gitignore.native 2>/dev/null || true

# Clean up temp directory
rm -rf "$TEMP_DIR"

cd mobile

# Restore our custom files
echo "♻️  Restoring custom source files..."
rm -rf src
cp -r .temp_backup/src .
cp .temp_backup/package.json package.json
cp .temp_backup/tsconfig.json tsconfig.json
cp .temp_backup/babel.config.js babel.config.js
cp .temp_backup/metro.config.js metro.config.js
cp .temp_backup/README.md README.md

# Clean up backup
rm -rf .temp_backup

# Update app.json with RealDiag configuration
echo "⚙️  Configuring app settings..."
cat > app.json << 'EOF'
{
  "name": "RealDiag",
  "displayName": "RealDiag Clinical Support",
  "version": "1.0.0",
  "buildNumber": "1"
}
EOF

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Install additional dependencies
echo "📦 Installing additional packages..."
npm install @react-navigation/native @react-navigation/native-stack @react-navigation/bottom-tabs
npm install react-native-screens react-native-safe-area-context react-native-gesture-handler
npm install @reduxjs/toolkit react-redux
npm install axios react-native-keychain
npm install @react-native-voice/voice
npm install react-native-vector-icons
npm install realm

# iOS specific setup
if [ -d "ios" ]; then
    echo "🍎 Setting up iOS..."
    
    # Update Info.plist with permissions
    cat >> ios/RealDiag/Info.plist.permissions << 'EOF'

<!-- Add these to your Info.plist before the closing </dict> -->
<key>NSMicrophoneUsageDescription</key>
<string>RealDiag needs microphone access for voice symptom input</string>
<key>NSFaceIDUsageDescription</key>
<string>Authenticate using Face ID for secure access</string>
<key>NSCameraUsageDescription</key>
<string>RealDiag needs camera access for document scanning</string>
EOF
    
    echo "📝 Note: Add permissions from ios/RealDiag/Info.plist.permissions to ios/RealDiag/Info.plist"
    
    # Install CocoaPods dependencies
    if command -v pod &> /dev/null; then
        echo "📦 Installing iOS pods..."
        cd ios
        pod install
        cd ..
    else
        echo "⚠️  Warning: CocoaPods not found. Install with: sudo gem install cocoapods"
        echo "   Then run: cd ios && pod install"
    fi
fi

# Android specific setup
if [ -d "android" ]; then
    echo "🤖 Setting up Android..."
    
    # Update AndroidManifest.xml with permissions
    MANIFEST_FILE="android/app/src/main/AndroidManifest.xml"
    if [ -f "$MANIFEST_FILE" ]; then
        # Backup original
        cp "$MANIFEST_FILE" "$MANIFEST_FILE.backup"
        
        # Add permissions after the manifest tag
        sed -i '/<manifest/a\    <uses-permission android:name="android.permission.INTERNET" />\n    <uses-permission android:name="android.permission.RECORD_AUDIO" />\n    <uses-permission android:name="android.permission.USE_BIOMETRIC" />\n    <uses-permission android:name="android.permission.USE_FINGERPRINT" />' "$MANIFEST_FILE" 2>/dev/null || echo "⚠️  Note: Manually add Android permissions to $MANIFEST_FILE"
    fi
fi

echo ""
echo "✅ Native projects initialized successfully!"
echo ""
echo "📱 Next steps:"
echo ""
echo "1. iOS Setup (macOS only):"
echo "   cd ios"
echo "   pod install"
echo "   cd .."
echo ""
echo "2. Run on iOS:"
echo "   npm run ios"
echo ""
echo "3. Run on Android:"
echo "   npm run android"
echo ""
echo "4. Start Metro bundler:"
echo "   npm start"
echo ""
echo "📚 See README.md for detailed setup instructions"
echo ""
