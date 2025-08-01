# Mobile Deployment Setup Guide

This guide covers the setup and deployment process for the Arctic Ice Solutions mobile app on iOS and Android platforms using Capacitor.

## Overview

The Arctic Ice Solutions mobile app is built using:
- **Frontend**: React + TypeScript + Vite
- **Mobile Framework**: Capacitor 6.0
- **PWA Support**: VitePWA plugin for web app capabilities
- **Native Features**: GPS tracking, camera access, push notifications

## Prerequisites

### For Android Development
- **Java JDK 17** (OpenJDK recommended)
- **Android Studio** or Android SDK Command Line Tools
- **Android SDK Platform 34** (API level 34)
- **Android SDK Build Tools 34.0.0+**

### For iOS Development
- **macOS** (required for iOS development)
- **Xcode 14+**
- **iOS SDK 16.0+**
- **Apple Developer Account** (for app store deployment)

## Project Structure

```
frontend/
├── android/                 # Android native project (generated)
├── ios/                     # iOS native project (generated)
├── src/
│   ├── mobile/             # Mobile-specific components
│   │   ├── pages/          # Mobile app pages
│   │   └── components/     # Mobile UI components
│   └── utils/
│       └── capacitor.ts    # Capacitor utility functions
├── public/
│   ├── manifest.json       # PWA manifest
│   └── icon-*.png         # App icons (various sizes)
├── capacitor.config.ts     # Capacitor configuration
└── package.json           # Dependencies and scripts
```

## Installation & Setup

### 1. Install Dependencies

```bash
cd frontend
pnpm install
```

### 2. Build the Web App

```bash
pnpm build
```

### 3. Initialize Capacitor (if not already done)

```bash
npx cap init
```

### 4. Add Native Platforms

```bash
# Add Android platform
npx cap add android

# Add iOS platform (macOS only)
npx cap add ios
```

### 5. Sync Web Assets to Native Projects

```bash
npx cap sync
```

## Capacitor Plugins

The app uses the following Capacitor plugins:

- **@capacitor/geolocation** - GPS tracking for delivery routes
- **@capacitor/camera** - Photo capture for inspections
- **@capacitor/push-notifications** - Mobile notifications
- **@capacitor/device** - Device information
- **@capacitor/status-bar** - Native status bar styling
- **@capacitor/splash-screen** - App launch screen

## Build Commands

### Development
```bash
# Start web development server
pnpm dev

# Build web app
pnpm build

# Sync changes to native projects
npx cap sync

# Open in Android Studio
npx cap open android

# Open in Xcode (macOS only)
npx cap open ios
```

### Production Builds
```bash
# Build and sync for Android
pnpm cap:build:android

# Build and sync for iOS
pnpm cap:build:ios
```

## Android Setup

### 1. Install Android SDK

#### Option A: Android Studio (Recommended)
1. Download and install [Android Studio](https://developer.android.com/studio)
2. Open Android Studio and install SDK Platform 34
3. Install Android SDK Build Tools 34.0.0+

#### Option B: Command Line Tools (Alternative)
```bash
# Download and extract Android Studio (recommended for better compatibility)
cd /tmp
wget https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2023.3.1.18/android-studio-2023.3.1.18-linux.tar.gz
sudo tar -xzf android-studio-2023.3.1.18-linux.tar.gz -C /opt/
sudo chown -R $USER:$USER /opt/android-studio

# Setup Android Studio SDK
export ANDROID_HOME=/opt/android-studio/sdk
mkdir -p $ANDROID_HOME/cmdline-tools/latest
cd $ANDROID_HOME
wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
unzip commandlinetools-linux-9477386_latest.zip
cd cmdline-tools/latest
unzip ../../commandlinetools-linux-9477386_latest.zip
mv cmdline-tools/* .
rmdir cmdline-tools

# Set environment variables
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools

# Install required packages
sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"
sdkmanager --licenses
```

### 2. Build Android App

```bash
# Build release APK
npx cap build android

# Or open in Android Studio for debugging
npx cap open android
```

### 3. Android App Store Deployment

1. **Generate Signed APK/AAB**:
   - Open project in Android Studio
   - Build → Generate Signed Bundle/APK
   - Create or use existing keystore
   - Build release version

2. **Upload to Google Play Console**:
   - Create app listing in Google Play Console
   - Upload AAB file
   - Complete store listing (descriptions, screenshots, etc.)
   - Submit for review

## iOS Setup (macOS Required)

### 1. Install Xcode
```bash
# Install Xcode from Mac App Store
# Or download from Apple Developer portal
```

### 2. Build iOS App
```bash
# Open in Xcode
npx cap open ios

# Build from Xcode:
# Product → Archive → Distribute App
```

### 3. iOS App Store Deployment

1. **Configure App in Xcode**:
   - Set bundle identifier
   - Configure signing certificates
   - Set deployment target (iOS 13.0+)

2. **Archive and Upload**:
   - Product → Archive
   - Distribute App → App Store Connect
   - Upload to App Store Connect

3. **App Store Connect**:
   - Complete app metadata
   - Add screenshots and descriptions
   - Submit for App Store review

## App Store Assets

### Icons Required
- **iOS**: 1024x1024 (App Store), 180x180, 120x120, 87x87, etc.
- **Android**: 512x512 (Play Store), 192x192, 144x144, 96x96, 72x72, 48x48

### Screenshots
- **iOS**: Various device sizes (iPhone, iPad)
- **Android**: Phone and tablet screenshots

### App Store Descriptions
- **Title**: Arctic Ice Solutions
- **Subtitle**: Field Operations & Delivery Management
- **Description**: Mobile app for Arctic Ice Solutions field technicians and customers
- **Keywords**: delivery, field service, ice delivery, route management

## Environment Variables

Set these environment variables for Android development:

```bash
# For Android Studio installation (recommended)
export ANDROID_HOME=/opt/android-studio/sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# For standalone SDK installation (alternative)
export ANDROID_HOME=/opt/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

## Troubleshooting

### Common Android Issues

1. **AAPT2 Daemon Startup Failed**:
   - Use Android Studio installation instead of standalone SDK tools
   - Install 32-bit libraries: `sudo apt install lib32stdc++6 lib32z1`
   - Clean Gradle cache: `cd android && ./gradlew clean`

2. **SDK Not Found**:
   - Verify ANDROID_HOME environment variable points to correct SDK location
   - For Android Studio: `/opt/android-studio/sdk`
   - For standalone SDK: `/opt/android-sdk`

3. **Build Tools Version**:
   - Update build tools: `sdkmanager "build-tools;34.0.0"`

4. **Signing Errors (Development)**:
   - Signing errors are expected for development builds without keystore
   - Use `npx cap run android` for development testing
   - Configure keystore only for production releases

### Common iOS Issues

1. **Code Signing**:
   - Ensure valid Apple Developer account
   - Configure signing certificates in Xcode

2. **Deployment Target**:
   - Set minimum iOS version to 13.0+
   - Update Capacitor iOS platform if needed

## Testing

### Web Testing
```bash
pnpm dev
# Test at http://localhost:5173/mobile
```

### Native Testing
```bash
# Android (requires Android Studio/emulator)
npx cap run android

# iOS (requires Xcode/simulator)
npx cap run ios
```

## Deployment Checklist

### Pre-Deployment
- [ ] Test all mobile features (GPS, camera, notifications)
- [ ] Verify PWA functionality in browsers
- [ ] Test on physical devices
- [ ] Update app version in package.json and capacitor.config.ts
- [ ] Generate proper app icons and splash screens
- [ ] Test offline functionality

### Android Deployment
- [ ] Build signed APK/AAB
- [ ] Test on multiple Android devices
- [ ] Upload to Google Play Console
- [ ] Complete store listing
- [ ] Submit for review

### iOS Deployment
- [ ] Archive in Xcode
- [ ] Test on multiple iOS devices
- [ ] Upload to App Store Connect
- [ ] Complete app metadata
- [ ] Submit for App Store review

## Support

For issues with:
- **Capacitor**: [Capacitor Documentation](https://capacitorjs.com/docs)
- **Android**: [Android Developer Docs](https://developer.android.com)
- **iOS**: [Apple Developer Docs](https://developer.apple.com)

## Notes

- iOS development requires macOS and Xcode
- Android development can be done on Linux/Windows/macOS
- PWA functionality works on all platforms
- Native builds require platform-specific SDKs
