# Deploy Keys Configuration

This directory contains configuration for SSH deploy keys used in the deployment process.

## Deploy Key Information

- **Key SHA256**: ZzwuLY9sJWZOWHEXjm+72YslxuMTAU79a8mNJCXyJGM
- **Purpose**: Repository access for automated deployment processes
- **Algorithm**: ED25519
- **Key Type**: ED25519 256-bit

## Files in this Directory

- `deploy-key.pub`: Public key to be added to GitHub repository deploy keys
- `setup-instructions.md`: Detailed setup instructions for configuring the deploy key
- `README.md`: This file - overview of the deploy key configuration

## Quick Setup

1. Add the public key (`deploy-key.pub`) to GitHub repository deploy keys
2. Add the private key to GitHub Secrets as `DEPLOY_KEY_PRIVATE`
3. The CI/CD workflow will automatically use the key for secure repository access

## Security Notes

- The private key should be stored securely in GitHub Secrets only
- The public key is safe to store in the repository
- This provides secure authentication for automated deployment processes
- The key is configured for repository access during CI/CD workflows
