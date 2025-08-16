# Android Deployment Credential Generation Guide

## Overview
This guide provides the exact commands to regenerate the corrupted Android keystore and Google Play service account credentials for Arctic Ice Solutions app deployment.

## Phase 1: Generate New Android Keystore

### Step 1: Create New Keystore
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

### Step 2: Validate Keystore
```bash
keytool -list -keystore yourchoiceice.jks -alias yourchoiceice-key -storepass "ArcticIce2025!Secure"
```

### Step 3: Encode for GitHub Secret
```bash
# Linux/macOS
base64 -w 0 yourchoiceice.jks > keystore_base64_new.txt

# Windows PowerShell
[Convert]::ToBase64String([System.IO.File]::ReadAllBytes("yourchoiceice.jks")) > keystore_base64_new.txt
```

### Step 4: Verify Encoding
```bash
# Test decode and validate
base64 -d keystore_base64_new.txt > test_keystore.jks
keytool -list -keystore test_keystore.jks -alias yourchoiceice-key -storepass "ArcticIce2025!Secure"
```

## Phase 2: Generate New Google Play Service Account

### Step 1: Access Google Cloud Console
Navigate to: Let's systematically diagnose and resolve the OpenAI API key integration issue. Here's a step-by-step action plan:

1. Verify Key Permissions & Account Status
Check key permissions at OpenAI API Keys:

Ensure the key has "All" permissions (not just "Read")

Confirm the key isn't restricted to specific endpoints

Verify account status:

bash
curl https://api.openai.com/v1/dashboard/billing/subscription \
  -H "Authorization: Bearer YOUR_API_KEY"
Look for "has_payment_method": true and "hard_limit_usd": >0

2. Backend Configuration Audit
Key Injection
In your FastAPI backend (main.py), add debug logging:

python
# Add to startup (before routes)
print(f"🔑 OpenAI Key Loaded: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
print(f"🔐 Key Starts With: {os.getenv('OPENAI_API_KEY')[:5]}...")  # First 5 chars

# Modify client initialization
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID")  # If applicable
)
Fly.io Secrets Verification
Confirm secrets are properly set:

bash
flyctl secrets list
Update secrets if needed:

bash
flyctl secrets set OPENAI_API_KEY=sk-new-key-here OPENAI_ORG_ID=org-abc123
3. Network & Headers Check
Proxy/Header Issues
Modify the OpenAI client call to log full requests:

python
from httpx import Transport, AsyncClient

custom_transport = Transport(
    verify=False,  # For debugging only
    retries=3
)

openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=AsyncClient(
        transport=custom_transport,
        timeout=30.0,
        headers={
            "User-Agent": "DocuGen-AI/1.0",
            "X-Custom-Auth": "Bearer " + os.getenv("OPENAI_API_KEY")[-4:]  # Log last 4 chars
        }
    )
)
4. Test with Minimal Reproduction
Create a test endpoint in FastAPI:

python
@app.get("/test-openai")
async def test_openai():
    try:
        test = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'TEST_OK'"}],
            max_tokens=5
        )
        return {"status": "success", "response": test.choices[0].message.content}
    except Exception as e:
        return {"status": "error", "detail": str(e), "key_used": os.getenv("OPENAI_API_KEY")[:5] + "..."}
Test via:

bash
curl https://your-backend.fly.dev/test-openai
5. Fallback Strategies
Key Rotation
Create a new key with full permissions

Update Fly.io secrets:

bash
flyctl secrets set OPENAI_API_KEY=sk-new-key-here
flyctl deploy
Alternative Auth
If using Azure OpenAI:

python
openai_client = OpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    base_url="https://YOUR_RESOURCE.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT"
)
Expected Outcomes
Success: /test-openai returns TEST_OK → Focus on video generation logic

Failure: Logs will show exact:

Key used

HTTP status code

OpenAI error message

Critical Checks
Time Synchronization: Ensure server clock is accurate (TLS failures if >5min off)

bash
date && curl -I https://api.openai.com
IP Restrictions: Whitelist Fly.io IPs in OpenAI Allowlist

Let me know the /test-openai results, and we can pinpoint the exact layer failing. This is typically either:

Key permissions

Network egress

Account limits
### Step 2: Create New Service Account Key
```bash
# Using gcloud CLI (recommended)
gcloud iam service-accounts keys create service-account-new.json \
  --iam-account=deploy@fiery-emblem-467622-t0.iam.gserviceaccount.com \
  --key-output-type=json
```

**Manual Steps:**
1. Click "ADD KEY" button
2. Select "Create new key"
3. Choose "JSON" format
4. Click "CREATE"
5. Download the new service account JSON file

### Step 3: Validate Service Account JSON
```bash
# Validate JSON structure
cat service-account-new.json | jq -e '.'

# Verify private key format
cat service-account-new.json | jq -r '.private_key' | head -n 1
# Should output: -----BEGIN PRIVATE KEY-----

# Check for proper newlines (not escaped)
cat service-account-new.json | jq -r '.private_key' | grep -c "BEGIN PRIVATE KEY"
# Should output: 1
```

## Phase 3: Update GitHub Repository Secrets

Navigate to: https://github.com/basitwali1x/arctic-ice-solutions/settings/secrets/actions

### Required Secrets (with _NEW suffix for safe rotation):

1. **ANDROID_KEYSTORE_BASE64_NEW**
   - Value: Content of `keystore_base64_new.txt`

2. **ANDROID_KEYSTORE_PASSWORD_NEW**
   - Value: `ArcticIce2025!Secure`

3. **KEY_ALIAS_NEW**
   - Value: `yourchoiceice-key`

4. **GOOGLE_PLAY_SERVICE_ACCOUNT_JSON_NEW**
   - Value: Complete JSON content from `service-account-new.json`
   - **CRITICAL**: Paste as plain text (NOT base64 encoded)
   - Ensure private_key field contains actual newlines, not escaped `\n`

## Phase 4: Testing and Verification

### Step 1: Test Single-App Deployment
- Current workflow is configured to deploy only `frontend-customer` first
- Monitor "Deploy to Google Play Store" step for decoder error resolution
- Verify successful deployment to internal track

### Step 2: Restore Dual-App Deployment (After Success)
- Update matrix strategy back to both apps:
```yaml
strategy:
  matrix:
    app: [frontend-customer, frontend-staff]
```

### Step 3: Clean Up (After Verification)
Only after confirming new credentials work:
1. Return to Google Cloud Console
2. Delete old service account key
3. Rotate GitHub secrets from _NEW to primary names
4. Keep only new working credentials active

## Security Notes

- **Password Strength**: The suggested password `ArcticIce2025!Secure` meets Android keystore requirements
- **Key Validity**: 10000 days (~27 years) ensures long-term app signing capability
- **Audit Trail**: Using _NEW suffixes maintains credential rotation history
- **Backup**: Store keystore file securely - losing it prevents app updates

## Troubleshooting

### Common Issues:
1. **Magic Bytes Error**: Indicates corrupted keystore file
2. **Decoder Error**: Service account JSON has formatting issues
3. **Alias Mismatch**: Ensure alias exactly matches "yourchoiceice-key"
4. **Password Mismatch**: Verify storepass and keypass are identical

### Verification Commands:
```bash
# Check keystore magic bytes
hexdump -C yourchoiceice.jks | head -n 1
# Should start with: feedfeed

# Validate service account
openssl rsa -in <(cat service-account-new.json | jq -r '.private_key') -check -noout
# Should output: RSA key ok
```

## References
- [Android App Signing](https://developer.android.com/studio/publish/app-signing)
- [Google Play Developer API](https://developers.google.com/android-publisher/getting_started)
- [Google Cloud Service Account Keys](https://cloud.google.com/iam/docs/service-accounts-create)
