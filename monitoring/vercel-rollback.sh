#!/bin/bash

set -e

DOMAIN="arcticicesolutions.com"
LOG_FILE="./vercel-rollback.log"

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
    log_message "INFO: $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    log_message "SUCCESS: $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    log_message "WARNING: $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    log_message "ERROR: $1"
}

backup_current_config() {
    print_status "Backing up current Vercel configuration..."
    
    vercel domains ls > ./vercel-domains-backup.txt 2>/dev/null || true
    vercel deployments ls > ./vercel-deployments-backup.txt 2>/dev/null || true
    
    print_success "Configuration backed up"
}

remove_domain_configuration() {
    print_status "Removing current domain configuration..."
    
    if vercel domains ls | grep -q "$DOMAIN"; then
        print_status "Removing $DOMAIN from project..."
        vercel domains rm "$DOMAIN" --yes 2>/dev/null || print_warning "Failed to remove $DOMAIN"
    fi
    
    if vercel domains ls | grep -q "www.$DOMAIN"; then
        print_status "Removing www.$DOMAIN from project..."
        vercel domains rm "www.$DOMAIN" --yes 2>/dev/null || print_warning "Failed to remove www.$DOMAIN"
    fi
    
    print_success "Domain configuration removed"
}

rollback_to_stable_deployment() {
    print_status "Finding last stable deployment..."
    
    LAST_STABLE=$(vercel deployments ls --meta production=true 2>/dev/null | head -n 2 | tail -n 1 | awk '{print $1}')
    
    if [ -n "$LAST_STABLE" ] && [ "$LAST_STABLE" != "URL" ]; then
        print_status "Rolling back to deployment: $LAST_STABLE"
        
        if vercel rollback "$LAST_STABLE" --yes; then
            print_success "Rollback to $LAST_STABLE completed"
        else
            print_error "Failed to rollback to $LAST_STABLE"
            return 1
        fi
    else
        print_warning "No previous stable deployment found"
        print_status "Triggering fresh deployment instead..."
        vercel --prod --force
    fi
}

restore_dns_to_devin_platform() {
    print_status "DNS Rollback Instructions:"
    print_warning "Please manually configure these DNS records to restore Devin Apps Platform:"
    
    echo ""
    echo "┌─────────────┬──────────┬─────────────────────────────┬─────┐"
    echo "│ Name        │ Type     │ Value                       │ TTL │"
    echo "├─────────────┼──────────┼─────────────────────────────┼─────┤"
    echo "│ @           │ A        │ 76.76.21.21                 │ 3600│"
    echo "│ www         │ CNAME    │ $DOMAIN                     │ 3600│"
    echo "└─────────────┴──────────┴─────────────────────────────┴─────┘"
    echo ""
    
    print_warning "Remove any Vercel-specific records:"
    print_warning "- Remove ALIAS records pointing to vercel-dns.com"
    print_warning "- Remove _vercel TXT verification records"
    print_warning "- Remove CAA records for letsencrypt.org (if not needed)"
}

verify_rollback() {
    print_status "Verifying rollback status..."
    
    if ! vercel domains ls | grep -q "$DOMAIN"; then
        print_success "Domain removed from Vercel project"
    else
        print_warning "Domain still exists in Vercel project"
    fi
    
    CURRENT_DEPLOYMENT=$(vercel deployments ls | head -n 2 | tail -n 1 | awk '{print $1}')
    if [ -n "$CURRENT_DEPLOYMENT" ]; then
        print_status "Current active deployment: $CURRENT_DEPLOYMENT"
    fi
}

cleanup_vercel_files() {
    print_status "Cleaning up Vercel-specific files..."
    
    rm -f ./vercel-txt-code.txt
    rm -f ./vercel-dns-status.json
    
    print_success "Cleanup completed"
}

generate_recovery_instructions() {
    print_status "Generating recovery instructions..."
    
    cat > ./recovery-instructions.md << EOF

- **Date**: $(date)
- **Domain**: $DOMAIN
- **Action**: Rolled back from Vercel to Devin Apps Platform

To complete the rollback, update your DNS records:

- Remove ALIAS record for @ pointing to vercel-dns.com
- Remove _vercel TXT verification record
- Remove any Vercel-specific CAA records

\`\`\`
Name: @
Type: A
Value: 76.76.21.21
TTL: 3600

Name: www
Type: CNAME
Value: $DOMAIN
TTL: 3600
\`\`\`

\`\`\`bash
dig $DOMAIN +short

curl -I https://$DOMAIN
\`\`\`

- Use existing dns-monitor.py to track DNS propagation
- Expected propagation time: 1-4 hours
- Monitor at: https://status.$DOMAIN

- vercel-domains-backup.txt
- vercel-deployments-backup.txt
- vercel-rollback.log

If issues persist, check:
1. DNS propagation status
2. Devin Apps Platform domain configuration
3. SSL certificate provisioning
EOF

    print_success "Recovery instructions saved to: ./recovery-instructions.md"
}

main() {
    print_status "Starting Vercel domain rollback for $DOMAIN"
    print_warning "This will remove the domain from Vercel and rollback to previous deployment"
    
    echo ""
    read -p "Are you sure you want to proceed with rollback? (y/N): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Rollback cancelled by user"
        exit 0
    fi
    
    backup_current_config
    
    remove_domain_configuration
    
    rollback_to_stable_deployment
    
    restore_dns_to_devin_platform
    
    verify_rollback
    
    cleanup_vercel_files
    
    generate_recovery_instructions
    
    print_success "Vercel rollback completed!"
    print_status "Next steps:"
    print_status "1. Update DNS records as shown above"
    print_status "2. Wait for DNS propagation (1-4 hours)"
    print_status "3. Monitor with: python3 dns-monitor.py"
    print_status "4. Review: ./recovery-instructions.md"
}

main "$@"
