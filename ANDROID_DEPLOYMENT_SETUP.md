# Android Deployment Setup Guide

This guide provides step-by-step instructions for setting up Android deployment for the Arctic Ice Solutions mobile apps.

## Overview

The Arctic Ice Solutions project includes two separate Android applications:
- **Customer App**: `com.arcticeicesolutions.customer` (frontend-customer/)
- **Staff App**: `com.arcticeicesolutions.staff` (frontend-staff/)

## Prerequisites

✅ **Already Completed:**
- Android signing keystore generated (`yourchoiceice-release.keystore`)
- GitHub Actions workflow created (`.github/workflows/android.yml`)
- Gradle signing configuration added to both apps
- Capacitor 6.0 setup with all required plugins

## Required GitHub Secrets

To enable automated Android builds and deployment, add these secrets to your GitHub repository:

### 1. Navigate to GitHub Secrets
Go to: https://github.com/basitwali1x/arctic-ice-solutions/settings/secrets/actions

### 2. Add Required Secrets

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `ANDROID_KEYSTORE_BASE64` | [Base64 encoded keystore] | The signing keystore file encoded in base64 |
| `ANDROID_KEYSTORE_PASSWORD` | `7OCUkzWc8cwZzfZJ` | Password for the keystore file |
| `ANDROID_KEY_PASSWORD` | `DANEKNuuIyuyYoIs` | Password for the signing key |
| `KEYSTORE_ALIAS` | `yourchoiceice-key` | Alias name for the signing key |

### 3. Optional Secrets (for deployment)

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `FIREBASE_TOKEN` | [Firebase CLI token] | For Firebase App Distribution |
| `FIREBASE_APP_ID_CUSTOMER` | [Firebase app ID] | Customer app Firebase project ID |
| `FIREBASE_APP_ID_STAFF` | [Firebase app ID] | Staff app Firebase project ID |
| `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` | [Service account JSON] | For Google Play Store uploads |

## Keystore Information

**Generated Keystore Details:**
- **File**: `yourchoiceice-release.keystore`
- **Algorithm**: RSA 4096-bit
- **Validity**: 25 years (9,125 days)
- **Subject**: CN=Arctic Ice Solutions, OU=Mobile, O=Arctic Ice Solutions, L=Leesville, ST=Louisiana, C=US

**⚠️ Important Security Notes:**
- The keystore file is NOT committed to the repository
- Passwords are stored securely in GitHub Secrets
- Base64 encoded keystore is used for CI/CD deployment

## Deployment Workflow

### Automatic Builds
The GitHub Actions workflow (`.github/workflows/android.yml`) automatically:

1. **On Pull Requests**: Builds debug APKs for testing
2. **On Main Branch**: Builds signed release APKs and AABs
3. **Artifacts**: Uploads build artifacts for download
4. **Firebase**: Deploys to Firebase App Distribution (if configured)
5. **Play Store**: Uploads to Google Play internal track (if configured)

### Manual Testing
```bash
# Test debug build locally
cd frontend-customer
pnpm install && pnpm build
npx cap sync android
cd android && ./gradlew assembleDebug

# Test staff app
cd ../frontend-staff
pnpm install && pnpm build
npx cap sync android
cd android && ./gradlew assembleDebug
```

## Firebase App Distribution Setup

1. **Install Firebase CLI**: `npm install -g firebase-tools`
2. **Login**: `firebase login`
3. **Get Token**: `firebase login:ci`
4. **Create Apps** in Firebase Console for both customer and staff apps
5. **Add Secrets** with Firebase app IDs and token

## Google Play Store Setup

1. **Create Apps** in Google Play Console:
   - Customer app: `com.arcticeicesolutions.customer`
   - Staff app: `com.arcticeicesolutions.staff`

2. **Generate Service Account**:
   - Go to Play Console → API Access
   - Create service account with "App Deployment" role
   - Download JSON key file
   - Add as `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` secret

3. **Initial Upload**: First AAB must be uploaded manually via Play Console

## App Store Assets

### Required Icons
- **Android**: 512x512 PNG (adaptive icon)
- **Play Store**: 512x512 PNG (feature graphic)

### Screenshots
- **Phone**: 16:9 aspect ratio
- **Tablet**: 16:10 aspect ratio
- Multiple device sizes recommended

### Store Listings

**Customer App:**
- **Title**: Arctic Ice Customer
- **Description**: Customer app for Arctic Ice Solutions - order placement, delivery tracking, and billing management
- **Category**: Business
- **Keywords**: ice delivery, customer portal, order tracking, billing

**Staff App:**
- **Title**: Arctic Ice Staff  
- **Description**: Staff app for Arctic Ice Solutions - field operations, work orders, and route management
- **Category**: Business
- **Keywords**: field operations, work orders, route management, delivery tracking

## Troubleshooting

### Common Build Issues

1. **Gradle Build Fails**:
   ```bash
   cd android && ./gradlew clean
   ./gradlew assembleDebug --info
   ```

2. **Signing Errors**:
   - Verify GitHub Secrets are set correctly
   - Check keystore passwords match generated values

3. **Capacitor Sync Issues**:
   ```bash
   npx cap sync android --force
   ```

### CI/CD Issues

1. **GitHub Actions Fails**:
   - Check secrets are properly configured
   - Verify workflow syntax in `.github/workflows/android.yml`

2. **Firebase Upload Fails**:
   - Verify Firebase token and app IDs
   - Check Firebase project permissions

## Next Steps

1. **Add GitHub Secrets** using the values provided above
2. **Test Workflow** by creating a pull request
3. **Configure Firebase** for internal testing (optional)
4. **Set up Play Store** for production deployment (optional)
5. **Create App Store Assets** (icons, screenshots, descriptions)

## Support

For issues with:
- **Capacitor**: [Capacitor Documentation](https://capacitorjs.com/docs)
- **Android**: [Android Developer Docs](https://developer.android.com)
- **GitHub Actions**: [GitHub Actions Docs](https://docs.github.com/en/actions)
