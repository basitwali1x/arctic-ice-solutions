# Automated Deployment Workflow

## Overview
This repository is configured for automatic deployment of both frontend and backend components when changes are pushed to the main branch.

## Deployment Architecture

### Frontend Deployment
- **Platform**: Devin Apps Platform
- **URL**: https://ice-management-app-4r16aafs.devinapps.com
- **Build Process**: React + TypeScript with Vite
- **Authentication**: Uses `DEVIN_SECRET_KEY` secret

### Backend Deployment
- **Platform**: Fly.io
- **URL**: https://app-rawyclbe.fly.dev
- **Build Process**: FastAPI with Poetry
- **Authentication**: Uses `FLY_API_TOKEN` secret

## Required GitHub Secrets

The following secrets must be configured in the repository settings:

1. **DEPLOY_KEY_PRIVATE**: SSH private key for repository access
2. **DEVIN_SECRET_KEY**: Authentication token for Devin Apps Platform
3. **FLY_API_TOKEN**: Authentication token for Fly.io deployment

## Deployment Triggers

Automatic deployment occurs when:
- Code is pushed to `main` branch
- Code is pushed to `devin/1752750425-arctic-ice-solutions-initial-commit` branch
- Pull requests are merged to either of the above branches

## Deployment Process

1. **Build and Test Phase**:
   - Install Node.js and pnpm dependencies
   - Run frontend linting and build
   - Install Python and Poetry dependencies
   - Run backend tests (if configured)

2. **Deploy Phase**:
   - Setup SSH deploy key for secure repository access
   - Build frontend for production
   - Deploy frontend to Devin Apps Platform
   - Deploy backend to Fly.io

## Monitoring and Verification

After deployment, verify:
- Frontend loads correctly at the production URL
- Backend API responds at the health check endpoint
- All authentication flows work properly
- Database connections and data persistence function correctly

## Troubleshooting

Common issues and solutions:
- **SSH Authentication Errors**: Verify deploy key is properly configured
- **Frontend Deployment Failures**: Check DEVIN_SECRET_KEY secret
- **Backend Deployment Failures**: Check FLY_API_TOKEN secret
- **Build Failures**: Review dependency versions and build logs
