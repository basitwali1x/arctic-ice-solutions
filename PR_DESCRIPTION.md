# Fix Android Deployment Credentials - Safe Secret Rotation

## Overview
This PR implements safe credential rotation to fix the corrupted Android keystore and Google Play service account credentials that are preventing successful deployment to Google Play Store.

## Root Cause Analysis
- **Android Keystore**: Corrupted magic bytes (fc35 b388 vs expected feedfeed) causing "keystore password was incorrect" errors
- **Service Account**: Documented "error:1E08010C:DECODER routines::unsupported" indicating corrupted JSON credentials

## Changes Made

### 1. Safe Secret Rotation Strategy
- Updated Android workflow to use `_NEW` suffixed secrets for testing
- Maintains audit trail during credential transition
- Allows rollback if issues occur

### 2. Single-App Testing First
- Modified matrix strategy to deploy only `frontend-customer` initially
- Reduces risk during credential validation
- Will restore both apps after successful testing

### 3. Updated Secret References
- `ANDROID_KEYSTORE_BASE64` → `ANDROID_KEYSTORE_BASE64_NEW`
- `ANDROID_KEYSTORE_PASSWORD` → `ANDROID_KEYSTORE_PASSWORD_NEW`
- `KEY_ALIAS` → `KEY_ALIAS_NEW`
- `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` → `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON_NEW`

## Required Actions Before Testing

### Generate New Android Keystore
```bash
keytool -genkeypair \
  -v -keystore yourchoiceice.jks \
  -alias yourchoiceice-key \
  -keyalg RSA -keysize 2048 \
  -validity 10000 \
  -storepass "ArcticIce2025!Secure" \
  -keypass "ArcticIce2025!Secure" \
  -dname "CN=Arctic Ice Solutions, OU=Mobile, O=Arctic Ice, L=Seattle, ST=WA, C=US"
```

### Encode Keystore for GitHub
```bash
# Linux/macOS
base64 -w 0 yourchoiceice.jks > keystore_base64_new.txt

# Windows PowerShell
[Convert]::ToBase64String([System.IO.File]::ReadAllBytes("yourchoiceice.jks")) > keystore_base64_new.txt
```

### Generate New Google Play Service Account
```bash
gcloud iam service-accounts keys create service-account-new.json \
  --iam-account=deploy@fiery-emblem-467622-t0.iam.gserviceaccount.com \
  --key-output-type=json
```

### Update GitHub Secrets
Navigate to: https://github.com/basitwali1x/arctic-ice-solutions/settings/secrets/actions

Add these new secrets:
- `ANDROID_KEYSTORE_BASE64_NEW`: Content of keystore_base64_new.txt
- `ANDROID_KEYSTORE_PASSWORD_NEW`: `ArcticIce2025!Secure`
- `KEY_ALIAS_NEW`: `yourchoiceice-key`
- `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON_NEW`: Complete JSON from service-account-new.json

## Testing Plan

### Phase 1: Single-App Validation
1. Generate credentials using provided commands
2. Update GitHub secrets with _NEW suffixes
3. Push this PR to trigger CI
4. Monitor for successful keystore validation and Google Play deployment

### Phase 2: Dual-App Deployment
1. After successful single-app test, update matrix to include both apps:
```yaml
strategy:
  matrix:
    app: [frontend-customer, frontend-staff]
```

### Phase 3: Secret Rotation Cleanup
1. Rotate secrets from _NEW to primary names
2. Delete old corrupted credentials
3. Remove _NEW suffix references from workflow

## Verification Steps
- [ ] Keystore validation passes with new credentials
- [ ] Service account JSON validation succeeds
- [ ] Google Play deployment completes without decoder errors
- [ ] Apps appear in Google Play Console internal testing track
- [ ] Both package names deploy successfully:
  - `com.arcticeicesolutions.customer`
  - `com.arcticeicesolutions.staff`

## Security Notes
- Using strong password: `ArcticIce2025!Secure`
- 27-year validity period ensures long-term app signing
- Safe rotation maintains credential history
- Keystore backup required for future app updates

## Files Changed
- `.github/workflows/android.yml`: Updated to use _NEW secret references
- `CREDENTIAL_GENERATION_GUIDE.md`: Complete step-by-step instructions

## Related Issues
- Fixes corrupted keystore preventing Android builds
- Resolves Google Play service account decoder errors
- Enables successful deployment to Play Store internal testing

---

**Link to Devin run**: https://app.devin.ai/sessions/0f8aeb98577346218b5f39cc5173501e  
**Requested by**: @basitwali1x

**Next Steps**: Generate new credentials using provided commands, update GitHub secrets, then test deployment.
