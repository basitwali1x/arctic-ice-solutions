#!/bin/bash

set -e

DOMAIN="arcticicesolutions.com"
PROJECT_NAME="arctic-ice-solutions"
LOG_FILE="./vercel-automation.log"

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

check_vercel_cli() {
    if ! command -v vercel &> /dev/null; then
        print_error "Vercel CLI not found. Installing..."
        npm install -g vercel
        print_success "Vercel CLI installed"
    else
        print_success "Vercel CLI found"
    fi
}

login_vercel() {
    print_status "Checking Vercel authentication..."
    if ! vercel whoami &> /dev/null; then
        print_warning "Not logged in to Vercel. Please login:"
        vercel login
    else
        print_success "Already logged in to Vercel"
    fi
}

add_domain_to_project() {
    print_status "Adding domain $DOMAIN to Vercel project..."
    
    if vercel domains ls | grep -q "$DOMAIN"; then
        print_warning "Domain $DOMAIN already exists in Vercel"
    else
        print_status "Adding domain to project..."
        vercel domains add "$DOMAIN" --yes
        print_success "Domain $DOMAIN added to project"
    fi
    
    if vercel domains ls | grep -q "www.$DOMAIN"; then
        print_warning "www.$DOMAIN already exists in Vercel"
    else
        print_status "Adding www subdomain..."
        vercel domains add "www.$DOMAIN" --yes
        print_success "www.$DOMAIN added to project"
    fi
}

get_verification_code() {
    print_status "Getting verification code for $DOMAIN..."
    
    VERCEL_TXT=$(vercel domains inspect "$DOMAIN" 2>/dev/null | grep -E "TXT.*_vercel" | awk '{print $NF}' | tr -d '"')
    
    if [ -z "$VERCEL_TXT" ]; then
        print_error "Could not retrieve verification code. Domain may not be added to project."
        return 1
    fi
    
    print_success "Verification code retrieved: $VERCEL_TXT"
    echo "$VERCEL_TXT" > ./vercel-txt-code.txt
    return 0
}

configure_dns_records() {
    print_status "Configuring DNS records for $DOMAIN..."
    
    if ! get_verification_code; then
        print_error "Failed to get verification code"
        return 1
    fi
    
    VERCEL_TXT=$(cat ./vercel-txt-code.txt)
    
    print_status "DNS Records to configure:"
    echo "┌─────────────┬──────────┬─────────────────────────────┬─────┐"
    echo "│ Name        │ Type     │ Value                       │ TTL │"
    echo "├─────────────┼──────────┼─────────────────────────────┼─────┤"
    echo "│ @           │ ALIAS    │ cname.vercel-dns.com        │ 60  │"
    echo "│ www         │ CNAME    │ $DOMAIN                     │ 60  │"
    echo "│ _vercel     │ TXT      │ $VERCEL_TXT                 │ 60  │"
    echo "│ @           │ CAA      │ 0 issue \"letsencrypt.org\"   │ 60  │"
    echo "└─────────────┴──────────┴─────────────────────────────┴─────┘"
    
    print_warning "Please configure these DNS records in your Vercel DNS management interface:"
    print_warning "1. Remove any existing invalid CNAME records for the root domain"
    print_warning "2. Add the ALIAS record for @ pointing to cname.vercel-dns.com"
    print_warning "3. Add the CNAME record for www pointing to $DOMAIN"
    print_warning "4. Add the TXT record for _vercel with value: $VERCEL_TXT"
    print_warning "5. Add the CAA record for @ with value: 0 issue \"letsencrypt.org\""
    
    echo ""
    read -p "Press Enter after you have configured the DNS records..."
}

verify_domain() {
    print_status "Verifying domain configuration..."
    
    local max_attempts=12
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        print_status "Verification attempt $attempt/$max_attempts..."
        
        if vercel domains verify "$DOMAIN" 2>/dev/null; then
            print_success "Domain $DOMAIN verified successfully!"
            return 0
        fi
        
        if vercel domains verify "www.$DOMAIN" 2>/dev/null; then
            print_success "www.$DOMAIN verified successfully!"
        fi
        
        print_warning "Verification failed. Waiting 30 seconds before retry..."
        sleep 30
        ((attempt++))
    done
    
    print_error "Domain verification failed after $max_attempts attempts"
    return 1
}

force_deployment() {
    print_status "Triggering production deployment..."
    
    if vercel --prod --force; then
        print_success "Production deployment triggered"
    else
        print_error "Failed to trigger deployment"
        return 1
    fi
}

check_domain_status() {
    print_status "Checking domain status..."
    
    if dig +short "$DOMAIN" | grep -q "cname.vercel-dns.com\|76.76.21.21"; then
        print_success "DNS resolution looks correct"
    else
        print_warning "DNS may not be fully propagated yet"
    fi
    
    if curl -s -I "https://$DOMAIN" | grep -q "200\|301\|302"; then
        print_success "HTTPS response successful"
    else
        print_warning "HTTPS not yet accessible"
    fi
    
    if echo | openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" 2>/dev/null | grep -q "Verify return code: 0"; then
        print_success "SSL certificate valid"
    else
        print_warning "SSL certificate not yet valid"
    fi
}

generate_rollback_script() {
    print_status "Generating rollback configuration..."
    
    cat > ./vercel-rollback.sh << 'EOF'
#!/bin/bash

DOMAIN="arcticicesolutions.com"

echo "🔄 Starting Vercel domain rollback..."

echo "Removing current domains..."
vercel domains rm "$DOMAIN" --yes 2>/dev/null || true
vercel domains rm "www.$DOMAIN" --yes 2>/dev/null || true

LAST_STABLE=$(vercel deployments ls --meta production=true | head -n 2 | tail -n 1 | awk '{print $1}')

if [ -n "$LAST_STABLE" ]; then
    echo "Rolling back to deployment: $LAST_STABLE"
    vercel rollback "$LAST_STABLE" --yes
else
    echo "No previous stable deployment found"
fi

echo "✅ Rollback completed"
EOF

    chmod +x ./vercel-rollback.sh
    print_success "Rollback script created: ./vercel-rollback.sh"
}

main() {
    print_status "Starting Vercel domain automation for $DOMAIN"
    print_status "Log file: $LOG_FILE"
    
    check_vercel_cli
    
    login_vercel
    
    add_domain_to_project
    
    configure_dns_records
    
    if verify_domain; then
        print_success "Domain verification successful!"
    else
        print_error "Domain verification failed. Check DNS configuration."
        exit 1
    fi
    
    force_deployment
    
    check_domain_status
    
    generate_rollback_script
    
    print_success "Vercel domain automation completed!"
    print_status "Domain should be accessible at: https://$DOMAIN"
    print_status "Monitor propagation with: python3 dns-monitor.py"
    print_status "Check status at: https://status.$DOMAIN"
}

main "$@"
