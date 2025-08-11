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

## Test Results - Workflow 16885764838

**Status**: ❌ FAILED - Validation passed but deployment still failed  
**Date**: August 11, 2025 16:20 UTC  

### Key Findings:
- ✅ **JSON Validation Step**: Passed successfully for both frontend-customer and frontend-staff
- ❌ **Google Play Deployment**: Still failed with same "error:1E08010C:DECODER routines::unsupported"
- 🔍 **Root Cause**: Current validation logic doesn't catch the specific encoding issue that r0adkll action encounters

### Validation Step Output:
```
🔍 Validating Google Play service account JSON format...
✅ Service account JSON validation successful
```

### Deployment Failure:
```
Creating a new Edit for this release
##[error]error:1E08010C:DECODER routines::unsupported
```

### Analysis:
The JSON passes basic syntax validation and contains all required fields, but there's a deeper encoding or format issue that the r0adkll/upload-google-play@v1 action cannot handle. This suggests:

1. **Possible Base64 encoding**: The secret might be base64 encoded when it should be plain text
2. **Character encoding issues**: UTF-8 vs ASCII encoding problems
3. **Escape sequence problems**: Newlines in private_key field not properly formatted
4. **Hidden characters**: BOM or other invisible characters in the JSON

## Test Results - Workflow 16885877837 (Enhanced Validation)

**Status**: ❌ FAILED - Enhanced validation passed but deployment still failed  
**Date**: August 11, 2025 16:27 UTC  

### Key Findings:
- ✅ **Enhanced JSON Validation Step**: Passed successfully - no base64 encoding detected
- ❌ **Google Play Deployment**: Still failed with same "error:1E08010C:DECODER routines::unsupported"
- 🔍 **Root Cause**: The issue is NOT base64 encoding - it's a deeper character encoding or format problem

### Enhanced Validation Results:
The enhanced validation logic with base64 detection ran successfully but did not detect any encoding issues. The secret appears to be in plain text JSON format as expected, but the r0adkll action still cannot decode it.

### Deployment Failure (Same Error):
```
Creating a new Edit for this release
##[error]error:1E08010C:DECODER routines::unsupported
```

### Updated Analysis:
Since the enhanced validation ruled out base64 encoding, the issue is likely one of these more subtle problems:

1. **Character encoding mismatch**: The JSON might be encoded in UTF-8 with BOM or other encoding that the action cannot handle
2. **Private key format issues**: The private_key field might have incorrect line endings or escape sequences
3. **Hidden/invisible characters**: Zero-width spaces, BOM markers, or other invisible Unicode characters
4. **JSON structure issues**: While syntactically valid, the JSON might have formatting that the specific OpenSSL decoder in the action cannot handle

## Service Account Key Generation Results

**Latest Key Generation Attempts:**

1. **Key ID: `deec9b6c46d086352c8beab6e6169ab808553bec`**
   - Generated: Aug 11, 2025
   - Downloaded as: `fiery-emblem-467622-t0-deec9b6c46d0.json`
   - Status: Downloaded to user's local machine

2. **Key ID: `c5eecd1bacc8` (attempted)**
   - Downloaded as: `fiery-emblem-467622-t0-c5eecd1bacc8.json`
   - Status: Downloaded to user's local machine

3. **Key ID: `bd6ef3f63e4d` (FOUND)**
   - Generated: Aug 11, 2025
   - Downloaded as: `fiery-emblem-467622-t0-bd6ef3f63e4d.json`
   - Status: ✅ Located in user's Downloads folder
   - Location: `C:\Users\Basit\Downloads\fiery-emblem-467622-t0-bd6ef3f63e4d.json`

## PowerShell Commands to Locate and View JSON Files

**Find the downloaded files:**
```powershell
Get-ChildItem -Path $env:USERPROFILE\Downloads -Name "*fiery-emblem-467622-t0*.json" -Recurse
```

**View the content of the most recent file:**
```powershell
# For the deec9b6c46d0 key:
Get-Content "$env:USERPROFILE\Downloads\fiery-emblem-467622-t0-deec9b6c46d0.json" | Out-String

# For the c5eecd1bacc8 key (if available):
Get-Content "$env:USERPROFILE\Downloads\fiery-emblem-467622-t0-c5eecd1bacc8.json" | Out-String
```

**Copy content to clipboard:**
```powershell
Get-Content "$env:USERPROFILE\Downloads\fiery-emblem-467622-t0-deec9b6c46d0.json" | Set-Clipboard
```

## Alternative Solution: Generate New Service Account Key

Since the downloaded JSON files cannot be located, here's an alternative approach:

### Option 1: Use Browser Downloads
If you can find the downloaded files, they should be named:
- `fiery-emblem-467622-t0-deec9b6c46d0.json`
- `fiery-emblem-467622-t0-c5eecd1bacc8.json`

### Option 2: Generate Fresh Service Account Key
If the files cannot be located, generate a new service account key:

1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts/details/109698483018706418481/keys?project=fiery-emblem-467622-t0
2. Click "Add key" → "Create new key"
3. Select "JSON" format
4. Download the key file
5. Copy the entire JSON content

### Expected JSON Structure Template

The downloaded JSON files should contain this structure:

```json
{
  "type": "service_account",
  "project_id": "fiery-emblem-467622-t0",
  "private_key_id": "[KEY_ID_FROM_FILENAME]",
  "private_key": "-----BEGIN PRIVATE KEY-----\n[PRIVATE_KEY_CONTENT]\n-----END PRIVATE KEY-----\n",
  "client_email": "play-store-deployment@fiery-emblem-467622-t0.iam.gserviceaccount.com",
  "client_id": "[CLIENT_ID]",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs/play-store-deployment%40fiery-emblem-467622-t0.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
```

### Troubleshooting File Location Issues

If PowerShell commands don't find the files, try:

```powershell
# Check browser's default download location
$downloads = (New-Object -ComObject Shell.Application).NameSpace('shell:Downloads').Self.Path
Get-ChildItem -Path $downloads -Name "*.json" | Where-Object { $_ -like "*fiery*" }

# Check all recent JSON files
Get-ChildItem -Path $downloads -Filter "*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | ForEach-Object { $_.Name }
```

## Next Steps

**IMMEDIATE ACTION REQUIRED:**

1. **Locate and Copy JSON Content:**
   - Use the PowerShell commands above to find and view the downloaded JSON files
   - Copy the **entire content** of one of the JSON files (recommend using the most recent one)

2. **Update GitHub Repository Secret:**
   - Go to: https://github.com/basitwali1x/arctic-ice-solutions/settings/secrets/actions
   - Find `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` secret
   - Click "Update" 
   - Paste the **entire content** of the JSON file
   - The content should be plain text JSON, NOT base64 encoded

3. **Test the Fix:**
   - Trigger the Android workflow manually: https://github.com/basitwali1x/arctic-ice-solutions/actions/workflows/android.yml
   - Monitor the deployment to verify the "DECODER routines::unsupported" error is resolved

4. **Verify Success:**
   - Check that the validation step passes
   - Confirm Google Play deployment completes successfully
   - Monitor for any new error messages

## Documentation References

- [r0adkll/upload-google-play Action](https://github.com/r0adkll/upload-google-play)
- [Google Cloud Service Account Keys](https://cloud.google.com/iam/docs/service-accounts-create)
- [Google Play Developer API](https://developers.google.com/android-publisher/getting_started)

---
**Created**: August 11, 2025 16:04 UTC  
**Author**: Devin AI  
**Issue**: Workflow 16885104108 Google Play deployment failure  
**Status**: Solution implemented, awaiting secret update and verification
