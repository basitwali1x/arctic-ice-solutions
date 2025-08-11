# Google Play Service Account JSON Configuration Fix

## Issue Summary
**Workflow ID**: 16885104108  
**Error**: "DECODER routines::unsupported" during Google Play authentication  
**Root Cause**: Malformed JSON in `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` repository secret  
**Impact**: Both frontend-customer and frontend-staff deployments failing  

## Error Analysis

The deployment workflow failed with the following error during the Google Play Store upload step:
```
DECODER routines::unsupported
```

This error occurs in the Android workflow at line 133 where the `r0adkll/upload-google-play@v1` action attempts to parse the `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` secret:

```yaml
- name: Deploy to Google Play Store
  if: github.ref == 'refs/heads/main'
  uses: r0adkll/upload-google-play@v1
  with:
    serviceAccountJsonPlainText: ${{ secrets.GOOGLE_PLAY_SERVICE_ACCOUNT_JSON }}
```

## Root Cause Analysis

Based on investigation of the r0adkll/upload-google-play action documentation and comparison with the existing Google Sheets service account implementation, the issue is that the `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` repository secret contains malformed JSON that cannot be decoded.

### Expected Format

The `serviceAccountJsonPlainText` parameter expects "The contents of your service-account.json" as plain text JSON, not base64 encoded or otherwise modified.

### Required JSON Structure

Based on Google Cloud service account standards and the validation pattern used in `backend/app/google_sheets_import.py`, the JSON must contain these required fields:

```json
{
  "type": "service_account",
  "project_id": "fiery-emblem-467622-t0",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "play-store-deployment@fiery-emblem-467622-t0.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

### Service Account Details

From `DEPLOYMENT_TRIGGER.md`:
- **Project ID**: fiery-emblem-467622-t0
- **Client Email**: play-store-deployment@fiery-emblem-467622-t0.iam.gserviceaccount.com

## Solution Implementation

### 1. JSON Validation in Workflow

Added validation step to the Android workflow to catch JSON format issues before deployment:

```yaml
- name: Validate Google Play Service Account JSON
  run: |
    echo "🔍 Validating Google Play service account JSON format..."
    if ! echo '${{ secrets.GOOGLE_PLAY_SERVICE_ACCOUNT_JSON }}' | jq empty; then
      echo "❌ Invalid JSON format in GOOGLE_PLAY_SERVICE_ACCOUNT_JSON"
      exit 1
    fi
    
    # Check required fields
    REQUIRED_FIELDS=("type" "project_id" "private_key" "client_email")
    for field in "${REQUIRED_FIELDS[@]}"; do
      if ! echo '${{ secrets.GOOGLE_PLAY_SERVICE_ACCOUNT_JSON }}' | jq -e ".$field" > /dev/null; then
        echo "❌ Missing required field: $field"
        exit 1
      fi
    done
    echo "✅ Service account JSON validation successful"
```

### 2. Repository Secret Update Instructions

To fix the current issue, the `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` repository secret needs to be updated:

1. **Access Google Cloud Console**
   - Navigate to https://console.cloud.google.com/
   - Select project "fiery-emblem-467622-t0"

2. **Generate Service Account Key**
   - Go to IAM & Admin > Service Accounts
   - Find "play-store-deployment@fiery-emblem-467622-t0.iam.gserviceaccount.com"
   - Click "Actions" > "Manage keys"
   - Click "Add Key" > "Create new key"
   - Select "JSON" format
   - Download the key file

3. **Update GitHub Repository Secret**
   - Go to GitHub repository settings
   - Navigate to Secrets and variables > Actions
   - Find `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON`
   - Click "Update"
   - Copy the ENTIRE contents of the downloaded JSON file
   - Paste as plain text (do NOT base64 encode)
   - Save the secret

## Common Issues and Solutions

### JSON Formatting Errors
- **Issue**: Extra quotes, escaped characters, or malformed JSON structure
- **Solution**: Validate JSON using `jq` command: `cat service-account.json | jq empty`

### Base64 Encoding Problems
- **Issue**: Secret contains base64 encoded JSON instead of plain text
- **Solution**: Use the raw JSON content, not encoded

### Missing Required Fields
- **Issue**: JSON missing essential fields like `private_key` or `client_email`
- **Solution**: Generate a new service account key from Google Cloud Console

### Expired Service Account Keys
- **Issue**: Service account key has been revoked or expired
- **Solution**: Generate a new key and update the repository secret

## Verification Steps

1. **Local JSON Validation**
   ```bash
   # Test JSON format
   echo "$JSON_CONTENT" | jq empty
   
   # Check required fields
   echo "$JSON_CONTENT" | jq -r '.type, .project_id, .client_email'
   ```

2. **Workflow Testing**
   - Trigger the Android workflow manually
   - Monitor the validation step output
   - Verify Google Play deployment completes successfully

3. **Deployment Verification**
   - Check that both frontend-customer and frontend-staff apps deploy
   - Verify apps appear in Google Play Console internal track

## Reference Implementation

The Google Sheets service account validation in `backend/app/google_sheets_import.py` provides a good reference pattern:

```python
try:
    service_account_info = json.loads(service_account_json)
except json.JSONDecodeError as e:
    raise ValueError(f"Invalid JSON format in GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON: {e}")

required_fields = ["type", "project_id", "private_key", "client_email"]
missing_fields = [field for field in required_fields if field not in service_account_info]
if missing_fields:
    raise ValueError(f"Missing required fields in service account JSON: {missing_fields}")
```

## Next Steps

1. Update the `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` repository secret with properly formatted JSON
2. Retrigger the Android workflow to verify the fix
3. Monitor deployment success for both mobile applications
4. Consider adding similar validation to other service account configurations

## Documentation References

- [r0adkll/upload-google-play Action](https://github.com/r0adkll/upload-google-play)
- [Google Cloud Service Account Keys](https://cloud.google.com/iam/docs/service-accounts-create)
- [Google Play Developer API](https://developers.google.com/android-publisher/getting_started)

---
**Created**: August 11, 2025 16:04 UTC  
**Author**: Devin AI  
**Issue**: Workflow 16885104108 Google Play deployment failure  
**Status**: Solution implemented, awaiting secret update and verification
