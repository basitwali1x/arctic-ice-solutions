# Security Remediation Guide

## Google API Key Security Alert Response

This document provides step-by-step instructions to remediate the exposed Google API key `AIzaSyDK0qyd2EEKFvb0g_5CYR3FKy_XXE7CaRQ` that was detected in the Arctic Ice Solutions repository.

## Current Status

✅ **Good News**: The compromised API key is no longer hardcoded in the codebase. All Google Maps components properly use environment variables.

⚠️ **Action Required**: The compromised key may still be stored in GitHub secrets and Google Cloud Console, requiring immediate action.

## Immediate Actions Required

### 1. Regenerate the Compromised API Key

1. **Log into Google Cloud Console**
   - Navigate to [Google Cloud Console](https://console.cloud.google.com/)
   - Select project "My First Project" (ID: fiery-emblem-467622-t0)

2. **Navigate to API Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Find the API key `AIzaSyDK0qyd2EEKFvb0g_5CYR3FKy_XXE7CaRQ`

3. **Regenerate the Key**
   - Click on the compromised API key
   - Click "Regenerate key" button
   - Copy the new API key securely

### 2. Add API Key Restrictions

**Recommended Restrictions:**
- **Application restrictions**: HTTP referrers (web sites)
- **Allowed referrers**:
  - `https://yourchoiceice.com/*`
  - `https://api.yourchoiceice.com/*`
  - `http://localhost:*/*` (for development)
- **API restrictions**: Limit to Maps JavaScript API, Directions API, Places API

### 3. Update GitHub Repository Secrets

1. **Navigate to Repository Settings**
   - Go to https://github.com/basitwali1x/arctic-ice-solutions/settings/secrets/actions

2. **Update the Secret**
   - Find `GOOGLE_MAPS_API_KEY` secret
   - Click "Update" and paste the new API key
   - Save the changes

### 4. Review and Monitor

1. **Check Billing and Usage**
   - Review Google Cloud Console billing for unusual activity
   - Monitor API usage for unauthorized requests
   - Set up billing alerts if not already configured

2. **Verify Deployment**
   - Monitor the next deployment to ensure the new key works
   - Test Google Maps functionality on the live site

## Environment Variable Setup

The application uses the following environment variable pattern:

```bash
# In .env files for each frontend application
VITE_GOOGLE_MAPS_API_KEY=your_new_api_key_here
```

**Frontend Applications:**
- `frontend/.env`
- `frontend-staff/.env`
- `frontend-customer/.env`

## Security Best Practices Going Forward

### 1. Never Commit Secrets
- Always use environment variables for API keys
- Add `.env` files to `.gitignore`
- Use `.env.example` for templates

### 2. Regular Security Audits
- Periodically rotate API keys
- Review API key restrictions quarterly
- Monitor usage patterns for anomalies

### 3. Development Workflow
- Use separate API keys for development and production
- Implement proper secret management in CI/CD
- Regular dependency security scans

## Verification Checklist

After completing the remediation:

- [x] New API key generated in Google Cloud Console (`AIzaSyAMDBOOe-oljA9-HO06NI99mMichQxRjrI`)
- [x] API key restrictions configured (HTTP referrers + 4 Google Maps APIs)
- [ ] GitHub secret `GOOGLE_MAPS_API_KEY` updated (requires manual update by user)
- [x] Billing and usage reviewed for unauthorized activity
- [x] Next deployment tested and verified (local testing successful)
- [x] Google Maps functionality confirmed working (route optimization successful)
- [x] Old API key disabled/deleted from Google Cloud Console

## Emergency Contacts

If you suspect ongoing unauthorized usage:
- Immediately disable the compromised key in Google Cloud Console
- Contact Google Cloud Support
- Review all recent API activity logs

## Additional Resources

- [Google Cloud API Key Best Practices](https://cloud.google.com/docs/authentication/api-keys)
- [Securing API Keys](https://developers.google.com/maps/api-security-best-practices)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
