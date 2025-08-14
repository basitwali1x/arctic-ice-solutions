# Android Keystore Update Guide

## Overview
This document outlines the process for updating the Android keystore configuration to fix the Google Play Console signing key mismatch.

## New Keystore Details
- **Keystore Type**: PKCS12
- **Key Alias**: yourchoiceice-key
- **SHA1 Fingerprint**: 87:F9:E9:B3:40:0E:A4:E3:A1:EB:2C:46:77:B9:03:95:0A:AA:1A:59
- **SHA256 Fingerprint**: E3:0F:F0:16:8B:7D:22:AB:0A:FC:8F:13:79:CD:31:A3:7F:C9:B1:A6:F3:52:F2:6D:79:5A:CF:80:CA:A5:DA:7D
- **Valid Until**: December 29, 2052

## Required GitHub Secrets
The following secrets need to be configured in the GitHub repository:

1. **ANDROID_KEYSTORE_BASE64_NEW**: Base64-encoded keystore file
2. **ANDROID_KEYSTORE_PASSWORD_NEW**: ArcticIce2025!Secure
3. **KEY_ALIAS_NEW**: yourchoiceice-key
4. **GOOGLE_PLAY_SERVICE_ACCOUNT_JSON_NEW**: Service account JSON for Google Play deployment

## Changes Made
- Updated `.github/workflows/android.yml` to use new secret names with `_NEW` suffix
- Added SHA1 fingerprint extraction to keystore validation step
- Updated all environment variables to reference new secrets

## Verification Steps
1. Keystore validation passes with new password
2. Android build process completes successfully
3. Google Play deployment works with new service account
4. SHA1 fingerprint matches Google Play Console requirements

## Next Steps
1. Update GitHub repository secrets with the new values
2. Test Android workflow to ensure builds complete successfully
3. Verify Google Play deployment works without signing key mismatch errors
