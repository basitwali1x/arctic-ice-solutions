# PowerShell Commands to Update GitHub Repository Secret

## Prerequisites

1. **Install GitHub CLI** (if not already installed):
   ```powershell
   winget install GitHub.cli
   ```

2. **Authenticate with GitHub** (if not already authenticated):
   ```powershell
   gh auth login
   ```

## Update GOOGLE_PLAY_SERVICE_ACCOUNT_JSON Secret

### Method 1: Direct Command (Recommended)

```powershell
# Set the service account JSON content as a variable
$serviceAccountJson = @'
{
  "type": "service_account",
  "project_id": "fiery-emblem-467622-t0",
  "private_key_id": "bd6ef3f63e4d",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC5...\n-----END PRIVATE KEY-----\n",
  "client_email": "play-store-deployment@fiery-emblem-467622-t0.iam.gserviceaccount.com",
  "client_id": "109698483018706418481",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs/play-store-deployment%40fiery-emblem-467622-t0.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
'@

# Update the GitHub repository secret
gh secret set GOOGLE_PLAY_SERVICE_ACCOUNT_JSON --repo basitwali1x/arctic-ice-solutions --body $serviceAccountJson
```

### Method 2: From File

```powershell
# If you have the service account JSON file downloaded locally
# Replace the path with your actual file path
$jsonFilePath = "$env:USERPROFILE\Downloads\fiery-emblem-467622-t0-bd6ef3f63e4d.json"

# Update the secret from file
gh secret set GOOGLE_PLAY_SERVICE_ACCOUNT_JSON --repo basitwali1x/arctic-ice-solutions --body-file $jsonFilePath
```

### Method 3: Interactive Input

```powershell
# This will prompt you to paste the JSON content
gh secret set GOOGLE_PLAY_SERVICE_ACCOUNT_JSON --repo basitwali1x/arctic-ice-solutions
# When prompted, paste the entire JSON content and press Enter, then Ctrl+D (or Ctrl+Z on Windows)
```

## Verify Secret Update

```powershell
# List all repository secrets to confirm the update
gh secret list --repo basitwali1x/arctic-ice-solutions
```

## Trigger Android Workflow

```powershell
# Manually trigger the Android CI/CD workflow
gh workflow run android.yml --repo basitwali1x/arctic-ice-solutions --ref main
```

## Monitor Workflow Status

```powershell
# View recent workflow runs
gh run list --repo basitwali1x/arctic-ice-solutions --workflow=android.yml --limit 5

# View specific workflow run details (replace RUN_ID with actual ID)
gh run view RUN_ID --repo basitwali1x/arctic-ice-solutions

# Watch workflow run in real-time (replace RUN_ID with actual ID)
gh run watch RUN_ID --repo basitwali1x/arctic-ice-solutions
```

## Complete Service Account JSON Content

**Note**: You need to replace the truncated private_key content below with the actual private key from your downloaded service account file.

```json
{
  "type": "service_account",
  "project_id": "fiery-emblem-467622-t0",
  "private_key_id": "bd6ef3f63e4d",
  "private_key": "-----BEGIN PRIVATE KEY-----\n[REPLACE_WITH_ACTUAL_PRIVATE_KEY_CONTENT]\n-----END PRIVATE KEY-----\n",
  "client_email": "play-store-deployment@fiery-emblem-467622-t0.iam.gserviceaccount.com",
  "client_id": "109698483018706418481",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs/play-store-deployment%40fiery-emblem-467622-t0.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
```

## Find Downloaded Service Account Files

```powershell
# Search for downloaded service account files
Get-ChildItem -Path $env:USERPROFILE\Downloads -Name "*fiery-emblem-467622-t0*.json" -Recurse

# View content of the most recent file (adjust filename as needed)
Get-Content "$env:USERPROFILE\Downloads\fiery-emblem-467622-t0-bd6ef3f63e4d.json" | Out-String

# Copy file content to clipboard for easy pasting
Get-Content "$env:USERPROFILE\Downloads\fiery-emblem-467622-t0-bd6ef3f63e4d.json" | Set-Clipboard
```

## Expected Results

After running these commands successfully:

1. ✅ **Secret Updated**: `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` will be updated in GitHub repository
2. ✅ **Workflow Triggered**: Android CI/CD workflow will start building both Customer and Staff apps
3. ✅ **Validation Passes**: The enhanced JSON validation step will pass
4. ✅ **Google Play Deployment**: Both apps will be deployed to Google Play Store internal track
5. ✅ **CI Success**: All workflow steps will complete successfully

## Troubleshooting

### If secret update fails:
```powershell
# Check GitHub CLI authentication
gh auth status

# Re-authenticate if needed
gh auth login --web
```

### If workflow fails:
```powershell
# View workflow logs for debugging
gh run view --log --repo basitwali1x/arctic-ice-solutions
```

### If JSON validation fails:
- Ensure the JSON content is valid using: `Get-Content file.json | ConvertFrom-Json`
- Make sure there are no extra characters or encoding issues
- Verify all required fields are present: type, project_id, private_key, client_email

---

**Important**: Make sure to use the actual private key content from your downloaded service account file, not the truncated version shown in the template above.
