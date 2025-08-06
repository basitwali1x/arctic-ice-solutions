#!/bin/bash

set -e

DOMAIN="arcticicesolutions.com"
EXPECTED_IP="76.76.21.21"
BACKUP_DOMAIN="backup.arcticicesolutions.com"
LOG_FILE="/tmp/domain-troubleshoot-$(date +%Y%m%d-%H%M%S).log"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

print_header() {
    log "${BLUE}=================================="
    log "Arctic Ice Solutions Domain Diagnostics"
    log "Domain: $DOMAIN"
    log "Expected IP: $EXPECTED_IP"
    log "Timestamp: $(date)"
    log "==================================${NC}"
}

check_dns_resolution() {
    log "\n${BLUE}🔍 DNS Resolution Check${NC}"
    log "----------------------------------------"
    
    if ! command -v dig &> /dev/null; then
        log "${RED}❌ dig command not found. Installing dnsutils...${NC}"
        sudo apt-get update && sudo apt-get install -y dnsutils
    fi
    
    log "Checking DNS resolution for $DOMAIN..."
    if dns_result=$(dig +short "$DOMAIN" 2>/dev/null); then
        if [ -n "$dns_result" ]; then
            log "${GREEN}✅ DNS Resolution:${NC}"
            echo "$dns_result" | while read -r ip; do
                if [ "$ip" = "$EXPECTED_IP" ]; then
                    log "  ${GREEN}✅ $ip (CORRECT)${NC}"
                else
                    log "  ${RED}❌ $ip (INCORRECT - Expected: $EXPECTED_IP)${NC}"
                fi
            done
        else
            log "${RED}❌ No DNS resolution found${NC}"
        fi
    else
        log "${RED}❌ DNS lookup failed${NC}"
    fi
    
    log "\nChecking against multiple DNS servers:"
    dns_servers=("8.8.8.8" "1.1.1.1" "208.67.222.222")
    for server in "${dns_servers[@]}"; do
        if result=$(dig @"$server" +short "$DOMAIN" 2>/dev/null); then
            if [ -n "$result" ]; then
                log "  DNS Server $server: ${GREEN}$result${NC}"
            else
                log "  DNS Server $server: ${RED}No response${NC}"
            fi
        else
            log "  DNS Server $server: ${RED}Query failed${NC}"
        fi
    done
}

check_port_connectivity() {
    log "\n${BLUE}🔌 Port Connectivity Check${NC}"
    log "----------------------------------------"
    
    ports=(80 443)
    for port in "${ports[@]}"; do
        log "Testing port $port..."
        if timeout 5 bash -c "</dev/tcp/$DOMAIN/$port" 2>/dev/null; then
            log "  ${GREEN}✅ Port $port is accessible${NC}"
        else
            log "  ${RED}❌ Port $port is not accessible${NC}"
        fi
    done
}

check_http_response() {
    log "\n${BLUE}🌐 HTTP Response Check${NC}"
    log "----------------------------------------"
    
    log "Testing HTTP connection..."
    if http_response=$(curl -I --connect-timeout 10 --max-time 15 "http://$DOMAIN" 2>&1); then
        log "${GREEN}✅ HTTP Response:${NC}"
        echo "$http_response" | head -10 | sed 's/^/  /' | tee -a "$LOG_FILE"
    else
        log "${RED}❌ HTTP connection failed:${NC}"
        echo "$http_response" | sed 's/^/  /' | tee -a "$LOG_FILE"
    fi
    
    log "\nTesting HTTPS connection..."
    if https_response=$(curl -I --connect-timeout 10 --max-time 15 "https://$DOMAIN" 2>&1); then
        log "${GREEN}✅ HTTPS Response:${NC}"
        echo "$https_response" | head -10 | sed 's/^/  /' | tee -a "$LOG_FILE"
    else
        log "${RED}❌ HTTPS connection failed:${NC}"
        echo "$https_response" | sed 's/^/  /' | tee -a "$LOG_FILE"
    fi
}

check_ssl_certificate() {
    log "\n${BLUE}🔒 SSL Certificate Check${NC}"
    log "----------------------------------------"
    
    log "Checking SSL certificate..."
    if cert_info=$(echo | timeout 10 openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" 2>/dev/null); then
        if subject=$(echo "$cert_info" | openssl x509 -noout -subject 2>/dev/null); then
            log "${GREEN}✅ Certificate Subject:${NC} ${subject#subject=}"
        fi
        
        if issuer=$(echo "$cert_info" | openssl x509 -noout -issuer 2>/dev/null); then
            log "${GREEN}✅ Certificate Issuer:${NC} ${issuer#issuer=}"
        fi
        
        if dates=$(echo "$cert_info" | openssl x509 -noout -dates 2>/dev/null); then
            log "${GREEN}✅ Certificate Validity:${NC}"
            echo "$dates" | sed 's/^/  /' | tee -a "$LOG_FILE"
            
            if expiry_date=$(echo "$dates" | grep "notAfter" | cut -d= -f2); then
                expiry_unix=$(date -d "$expiry_date" +%s 2>/dev/null || echo "0")
                current_unix=$(date +%s)
                days_left=$(( (expiry_unix - current_unix) / 86400 ))
                
                if [ "$days_left" -gt 30 ]; then
                    log "  ${GREEN}✅ Certificate expires in $days_left days${NC}"
                elif [ "$days_left" -gt 0 ]; then
                    log "  ${YELLOW}⚠️ Certificate expires in $days_left days${NC}"
                else
                    log "  ${RED}❌ Certificate expired $((-days_left)) days ago${NC}"
                fi
            fi
        fi
    else
        log "${RED}❌ SSL certificate check failed${NC}"
    fi
}

check_whois_info() {
    log "\n${BLUE}📋 Domain WHOIS Information${NC}"
    log "----------------------------------------"
    
    if command -v whois &> /dev/null; then
        log "Checking WHOIS information..."
        if whois_info=$(whois "$DOMAIN" 2>/dev/null | grep -E "(Name Server|Registrar|Creation Date|Expiry Date)" | head -10); then
            log "${GREEN}✅ WHOIS Info:${NC}"
            echo "$whois_info" | sed 's/^/  /' | tee -a "$LOG_FILE"
        else
            log "${YELLOW}⚠️ WHOIS information not available${NC}"
        fi
    else
        log "${YELLOW}⚠️ whois command not available${NC}"
    fi
}

check_backup_domain() {
    log "\n${BLUE}🔄 Backup Domain Check${NC}"
    log "----------------------------------------"
    
    log "Testing backup domain: $BACKUP_DOMAIN"
    if backup_response=$(curl -I --connect-timeout 5 --max-time 10 "http://$BACKUP_DOMAIN" 2>&1); then
        log "${GREEN}✅ Backup domain response:${NC}"
        echo "$backup_response" | head -5 | sed 's/^/  /' | tee -a "$LOG_FILE"
    else
        log "${RED}❌ Backup domain not accessible${NC}"
    fi
}

generate_recommendations() {
    log "\n${BLUE}💡 Recommendations${NC}"
    log "----------------------------------------"
    
    current_ips=$(dig +short "$DOMAIN" 2>/dev/null)
    if [ -n "$current_ips" ] && ! echo "$current_ips" | grep -q "$EXPECTED_IP"; then
        log "${YELLOW}📝 DNS Configuration Issue Detected:${NC}"
        log "  Current IPs: $current_ips"
        log "  Expected IP: $EXPECTED_IP"
        log "  Action: Update DNS A record to point to $EXPECTED_IP"
        log ""
    fi
    
    if ! timeout 5 bash -c "</dev/tcp/$DOMAIN/443" 2>/dev/null; then
        log "${YELLOW}📝 Connectivity Issue Detected:${NC}"
        log "  Port 443 not accessible"
        log "  Action: Check firewall rules and server configuration"
        log ""
    fi
    
    log "${GREEN}📝 General Recommendations:${NC}"
    log "  1. Verify DNS A record points to $EXPECTED_IP"
    log "  2. Ensure domain is added to Devin Apps Platform"
    log "  3. Wait for DNS propagation (up to 48 hours)"
    log "  4. Check SSL certificate configuration"
    log "  5. Verify firewall allows ports 80 and 443"
}

create_summary_report() {
    log "\n${BLUE}📊 Summary Report${NC}"
    log "=========================================="
    
    if dig +short "$DOMAIN" | grep -q "$EXPECTED_IP"; then
        log "DNS Status: ${GREEN}✅ CORRECT${NC}"
    else
        log "DNS Status: ${RED}❌ INCORRECT${NC}"
    fi
    
    if timeout 5 bash -c "</dev/tcp/$DOMAIN/443" 2>/dev/null; then
        log "Connectivity: ${GREEN}✅ ACCESSIBLE${NC}"
    else
        log "Connectivity: ${RED}❌ NOT ACCESSIBLE${NC}"
    fi
    
    if echo | timeout 10 openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" >/dev/null 2>&1; then
        log "SSL Status: ${GREEN}✅ WORKING${NC}"
    else
        log "SSL Status: ${RED}❌ FAILED${NC}"
    fi
    
    log "\n${BLUE}📄 Full log saved to: $LOG_FILE${NC}"
}

main() {
    print_header
    check_dns_resolution
    check_port_connectivity
    check_http_response
    check_ssl_certificate
    check_whois_info
    check_backup_domain
    generate_recommendations
    create_summary_report
    
    log "\n${GREEN}🎉 Domain troubleshooting completed!${NC}"
    log "Review the log file for detailed information: $LOG_FILE"
}

main "$@"
