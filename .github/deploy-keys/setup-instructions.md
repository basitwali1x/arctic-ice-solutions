# Deploy Key Setup Instructions

## Overview
This repository uses an SSH deploy key for secure repository access during automated deployment processes.

## Deploy Key Details
- **Algorithm**: ED25519
- **SHA256 Fingerprint**: ZzwuLY9sJWZOWHEXjm+72YslxuMTAU79a8mNJCXyJGM
- **Purpose**: Repository access for CI/CD deployment workflows

## Setup Steps

### 1. Add Deploy Key to GitHub Repository
1. Navigate to the repository settings: `Settings > Deploy keys`
2. Click "Add deploy key"
3. Title: "Deploy Key for CI/CD"
4. Key: Copy the contents from `deploy-key.pub`
5. Check "Allow write access" if needed for deployment
6. Click "Add key"

### 2. Add Private Key to GitHub Secrets
1. Navigate to repository settings: `Settings > Secrets and variables > Actions`
2. Click "New repository secret"
3. Name: `DEPLOY_KEY_PRIVATE`
4. Value: The private key content (provided separately for security)
5. Click "Add secret"

### 3. Verify Configuration
The CI/CD workflow will automatically use the deploy key for:
- Repository checkout operations
- Secure git operations during deployment
- Authentication with GitHub for automated processes

## Security Notes
- The private key is stored securely in GitHub Secrets
- The public key is added to the repository's deploy keys
- This provides read-only or limited write access as configured
- The key is only accessible during workflow execution

## Auto-Merge Configuration
The repository includes an auto-merge workflow for PRs created by `devin-ai-integration[bot]`. This workflow:
- Uses `juliangruber/merge-pull-request-action@v1` for reliable merging
- Automatically merges PRs using squash method
- Triggers on PR open/sync and check suite completion

## Troubleshooting
If deployment fails with authentication errors:
1. Verify the deploy key is properly added to the repository
2. Check that the `DEPLOY_KEY_PRIVATE` secret contains the correct private key
3. Ensure the key has appropriate permissions (read/write as needed)
4. Verify the SSH agent setup in the workflow is correct

If auto-merge fails:
1. Check that the GitHub token has appropriate permissions
2. Verify the PR is created by `devin-ai-integration[bot]`
3. Ensure all required checks are passing

If deployment is skipped:
1. Check that required secrets are configured: `DEPLOY_KEY_PRIVATE`, `FLY_API_TOKEN`
2. The workflow will show warnings for missing secrets but continue with available deployments
3. Frontend deployment requires `DEVIN_SECRET_KEY` (should already be configured)
