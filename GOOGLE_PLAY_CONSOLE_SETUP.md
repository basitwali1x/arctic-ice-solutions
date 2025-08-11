# Google Play Console Developer Environment Setup

## Overview

This document provides comprehensive setup instructions for the Google Play Console developer environment for Arctic Ice Solutions mobile applications. The setup includes both local development environment configuration and CI/CD pipeline verification.

## Mobile Applications

Arctic Ice Solutions has two Android applications configured for Google Play Store deployment:

- **Customer App**: `com.arcticeicesolutions.customer`
- **Staff App**: `com.arcticeicesolutions.staff`

Both applications are built using:
- **Framework**: React + TypeScript with Capacitor 6.0
- **Build System**: Gradle with Android SDK API 34
- **Deployment**: Automated CI/CD via GitHub Actions

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu recommended)
- **Java**: JDK 11 or higher
- **Node.js**: Version 18+ with pnpm package manager
- **Git**: For version control and repository access

### Required Tools

1. **Android SDK Command Line Tools**
2. **Capacitor CLI**
3. **Gradle** (included with Android projects)

## Local Development Environment Setup

### 1. Install Android SDK Command Line Tools

```bash
# Download Android SDK command line tools
cd /tmp
wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O android-cmdline-tools.zip

# Extract and setup directory structure
unzip android-cmdline-tools.zip
mkdir -p /tmp/android-sdk/cmdline-tools
mv cmdline-tools /tmp/android-sdk/cmdline-tools/latest

# Set environment variables
export ANDROID_HOME=/tmp/android-sdk
export ANDROID_SDK_ROOT=/tmp/android-sdk
export PATH=$PATH:/tmp/android-sdk/cmdline-tools/latest/bin:/tmp/android-sdk/platform-tools

# Accept Android SDK licenses
yes | sdkmanager --licenses

# Install required Android SDK components
sdkmanager "platforms;android-34" "build-tools;34.0.0" "platform-tools"
```

### 2. Configure Environment Variables

Add the following to your shell profile (`~/.bashrc` or `~/.zshrc`):

```bash
export ANDROID_HOME=/tmp/android-sdk
export ANDROID_SDK_ROOT=/tmp/android-sdk
export PATH=$PATH:/tmp/android-sdk/cmdline-tools/latest/bin:/tmp/android-sdk/platform-tools
```

### 3. Configure Android Projects

Update the `local.properties` files in both Android projects:

**Customer App**: `frontend-customer/android/local.properties`
```properties
sdk.dir=/tmp/android-sdk
```

**Staff App**: `frontend-staff/android/local.properties`
```properties
sdk.dir=/tmp/android-sdk
```

### 4. Install Node.js Dependencies

```bash
# Navigate to project root
cd ~/repos/arctic-ice-solutions

# Install dependencies for customer app
cd frontend-customer
pnpm install

# Install dependencies for staff app
cd ../frontend-staff
pnpm install
```

## Building Android Applications

### Debug Builds (Local Development)

Debug builds can be created locally without signing configuration:

```bash
# Customer App Debug Build
cd frontend-customer/android
./gradlew assembleDebug

# Staff App Debug Build
cd ../../frontend-staff/android
./gradlew assembleDebug
```

**Build Artifacts Location**:
- Customer App: `frontend-customer/android/app/build/outputs/apk/debug/app-debug.apk`
- Staff App: `frontend-staff/android/app/build/outputs/apk/debug/app-debug.apk`

### Release Builds (CI/CD Only)

Release builds require proper signing configuration and should only be built in the CI/CD environment:

```bash
# This will fail locally without proper keystore configuration
./gradlew bundleRelease
```

## Google Play Console CI/CD Configuration

### GitHub Actions Workflow

The automated deployment is configured in `.github/workflows/android.yml` with the following features:

- **Matrix Build**: Builds both Customer and Staff apps simultaneously
- **Artifact Generation**: Creates both APK and AAB files
- **Automatic Deployment**: Deploys to Google Play Store internal track
- **Signing**: Uses encrypted keystore for release signing

### Required GitHub Secrets

The following secrets must be configured in the GitHub repository:

| Secret Name | Description | Status |
|-------------|-------------|---------|
| `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` | Service account JSON for Google Play API | ⚠️ Needs Update |
| `ANDROID_KEYSTORE_BASE64` | Base64 encoded Android keystore | ✅ Configured |
| `ANDROID_KEYSTORE_PASSWORD` | Keystore password | ✅ Configured |
| `KEY_ALIAS` | Key alias for signing | ✅ Configured |

### Service Account Configuration

**Current Status**: The `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` secret requires updating with proper JSON content.

**Required Permissions**:
- Google Play Developer API access
- Release management permissions
- Internal testing track access

## Capacitor Configuration

### Installed Plugins

Both mobile applications use the following Capacitor plugins:

- `@capacitor/camera` - Camera functionality
- `@capacitor/device` - Device information
- `@capacitor/geolocation` - GPS location services
- `@capacitor/push-notifications` - Push notification support
- `@capacitor/splash-screen` - App splash screen
- `@capacitor/status-bar` - Status bar customization

### Capacitor Commands

```bash
# Sync native projects with web assets
npx cap sync android

# Open Android project in Android Studio
npx cap open android

# Build and sync in one command
npx cap build android
```

## Development Workflow

### 1. Local Development

```bash
# Start backend API server
cd backend
poetry run fastapi dev app/main.py --host 0.0.0.0 --port 8000

# Start frontend development server
cd frontend
pnpm dev

# For mobile development, build and sync
cd frontend-customer  # or frontend-staff
pnpm build
npx cap sync android
```

### 2. Testing Mobile Apps

```bash
# Build debug APK for testing
cd frontend-customer/android
./gradlew assembleDebug

# Install on connected device/emulator
adb install app/build/outputs/apk/debug/app-debug.apk
```

### 3. Deployment Process

1. **Commit Changes**: Push changes to the repository
2. **Trigger Workflow**: GitHub Actions automatically builds and deploys
3. **Monitor CI**: Check workflow status in GitHub Actions
4. **Verify Deployment**: Confirm apps are available in Google Play Console

## Troubleshooting

### Common Issues

#### 1. Android SDK License Not Accepted

**Error**: `Failed to install the following Android SDK packages as some licences have not been accepted`

**Solution**:
```bash
yes | sdkmanager --licenses
```

#### 2. SDK Path Not Found

**Error**: `SDK location not found`

**Solution**: Verify `local.properties` files contain correct SDK path:
```properties
sdk.dir=/tmp/android-sdk
```

#### 3. Build Tools Version Mismatch

**Error**: `Could not find build-tools;34.0.0`

**Solution**:
```bash
sdkmanager "build-tools;34.0.0"
```

#### 4. Release Build Signing Failure

**Error**: `Execution failed for task ':app:signReleaseBundle'`

**Cause**: Release builds require proper keystore configuration only available in CI/CD environment.

**Solution**: Use debug builds for local development, release builds for CI/CD only.

### Environment Verification

Run the following commands to verify your setup:

```bash
# Check Android SDK installation
echo $ANDROID_HOME
ls -la $ANDROID_HOME

# Check available Android platforms
sdkmanager --list | grep "platforms;android"

# Check build tools
sdkmanager --list | grep "build-tools"

# Verify Capacitor installation
npx cap doctor
```

## Google Play Console Access

### Developer Account Requirements

- **Google Play Developer Account**: Required for app publishing
- **Service Account**: Configured for API access
- **App Registration**: Both Customer and Staff apps registered

### Release Management

- **Internal Testing**: Automated deployment target
- **Production**: Manual promotion from internal testing
- **Version Management**: Automated version code increment

## Security Considerations

### Local Development

- **Debug Builds Only**: Never attempt release builds locally
- **API Keys**: Use development API endpoints only
- **Keystore**: Production keystore never stored locally

### CI/CD Environment

- **Encrypted Secrets**: All sensitive data encrypted in GitHub
- **Service Account**: Limited permissions for deployment only
- **Audit Trail**: All deployments logged and traceable

## Support and Documentation

### Additional Resources

- [Capacitor Android Documentation](https://capacitorjs.com/docs/android)
- [Google Play Console Help](https://support.google.com/googleplay/android-developer)
- [Android Developer Documentation](https://developer.android.com/)

### Internal Documentation

- `GOOGLE_PLAY_SERVICE_ACCOUNT_FIX.md` - Service account configuration details
- `MOBILE_DEPLOYMENT_CUSTOMER.md` - Customer app deployment guide
- `MOBILE_DEPLOYMENT_STAFF.md` - Staff app deployment guide

---

**Last Updated**: August 11, 2025  
**Author**: Devin AI  
**Version**: 1.0  
**Status**: ✅ Environment Setup Complete - Local Development Ready
