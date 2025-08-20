# Security Incident Response Runbook

## Arctic Ice Solutions - Production Security Deployment Protocol

### Overview
This document outlines the two-phase approach used to resolve critical security vulnerabilities in production systems, specifically when authentication fixes need immediate deployment but CI/CD pipelines are disabled.

### Incident Type: Demo Credentials Active in Production
**Severity**: CRITICAL  
**Impact**: Unauthorized access to production system via demo accounts

---

## Two-Phase Response Protocol

### Phase 1: Immediate Security Fix (Emergency Deployment)

#### Prerequisites
- Access to Fly.io account with deployment permissions
- Valid `FLY_API_TOKEN` with access to target application
- Fly CLI installed and authenticated

#### Steps

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   export FLYCTL_INSTALL="/home/ubuntu/.fly"
   export PATH="$FLYCTL_INSTALL/bin:$PATH"
   ```

2. **Set Production Environment Variables**
   ```bash
   export FLY_API_TOKEN="your-token-here"
   flyctl secrets set PRODUCTION_MODE=true \
     ADMIN_USERNAME=admin \
     ADMIN_PASSWORD=secure-production-password-2024 \
     --app arctic-ice-api
   ```

3. **Deploy from Repository Root**
   ```bash
   cd /path/to/arctic-ice-solutions
   flyctl deploy --app arctic-ice-api --remote-only
   ```

4. **Verify Security Fix**
   ```bash
   # Test demo credentials are BLOCKED (expect HTTP 401)
   curl -X POST https://api.yourchoiceice.com/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "manager", "password": "dev-password-change-in-production"}'
   
   # Test admin credentials WORK (expect HTTP 200)
   curl -X POST https://api.yourchoiceice.com/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "secure-production-password-2024"}'
   ```

### Phase 2: CI/CD Pipeline Restoration

#### Purpose
Prevent future security deployment gaps by restoring automated deployment capabilities.

#### Steps

1. **Create Branch for CI/CD Changes**
   ```bash
   git checkout -b devin/$(date +%s)-enable-cicd-pipeline
   ```

2. **Re-enable Disabled Workflow**
   ```bash
   mv .github/workflows/ci-cd.yml.backup.disabled .github/workflows/ci-cd.yml
   ```

3. **Commit and Push Changes**
   ```bash
   git add .github/workflows/ci-cd.yml
   git rm .github/workflows/ci-cd.yml.backup.disabled
   git commit -m "Phase 2: Re-enable CI/CD pipeline for automated backend deployments"
   git push origin devin/$(date +%s)-enable-cicd-pipeline
   ```

4. **Create Pull Request**
   - Use GitHub CLI or web interface
   - Include context about Phase 1 completion
   - Wait for CI checks to pass before merging

---

## Verification Checklist

### ✅ Phase 1 Success Criteria
- [ ] Demo credentials return HTTP 401 with "Demo credentials are disabled in production"
- [ ] Admin credentials return HTTP 200 with valid JWT token
- [ ] Production API responds correctly at `api.yourchoiceice.com`
- [ ] Fly.io deployment completed without errors

### ✅ Phase 2 Success Criteria
- [ ] CI/CD workflow file renamed and active
- [ ] Pull request created and merged successfully
- [ ] GitHub Actions workflow triggers on future commits
- [ ] All CI checks pass

---

## Security Implementation Details

### Backend Changes (`backend/app/main.py`)
```python
# Environment-based authentication control
is_production = os.getenv("PRODUCTION_MODE", "false").lower() == "true"

if is_production:
    # Block demo credentials
    demo_usernames = ["manager", "dispatcher", "accountant", "driver", ...]
    if login_request.username in demo_usernames:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Demo credentials are disabled in production"
        )
```

### Frontend Changes
```typescript
// Conditional demo credential display
{process.env.NODE_ENV === 'development' && (
  <div className="text-sm text-gray-600 text-center">
    <p>Demo credentials (Development Only):</p>
    // ... demo credentials list
  </div>
)}
```

### Environment Configuration (`.env.production`)
```env
PRODUCTION_MODE=true
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure-production-password-2024
DEMO_USER_PASSWORD=disabled-in-production
```

---

## Post-Incident Actions

### Immediate (0-24 hours)
- [ ] Monitor GitHub Actions for successful automated deployments
- [ ] Verify all frontend applications hide demo credentials
- [ ] Test admin panel functionality with production credentials

### Short-term (1-7 days)
- [ ] Schedule credential rotation policy (every 90 days)
- [ ] Document incident in security log
- [ ] Review access controls and permissions

### Long-term (1-4 weeks)
- [ ] Conduct lightweight penetration test on authentication endpoints
- [ ] Implement monitoring alerts for authentication failures
- [ ] Create automated security testing in CI/CD pipeline

---

## Emergency Contacts

### Technical Escalation
- **DevOps Lead**: [Contact Information]
- **Security Team**: [Contact Information]
- **CTO/Technical Director**: [Contact Information]

### Service Providers
- **Fly.io Support**: https://fly.io/docs/about/support/
- **GitHub Support**: https://support.github.com/

---

## Lessons Learned

### What Worked Well
- Two-phase approach allowed immediate security fix while preserving automation
- Manual Fly.io deployment provided rapid response capability
- Environment-based configuration enabled clean production/development separation

### Areas for Improvement
- Implement monitoring to detect when CI/CD pipelines are disabled
- Add automated security testing to prevent demo credentials in production
- Create alerts for authentication configuration changes

---

**Document Version**: 1.0  
**Last Updated**: August 20, 2025  
**Next Review**: November 20, 2025  
**Owner**: Security Team / DevOps
