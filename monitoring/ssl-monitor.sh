#!/bin/bash

set -e

DOMAIN="arcticicesolutions.com"
WARNING_DAYS=30
CRITICAL_DAYS=7
SLACK_WEBHOOK="${SLACK_DNS_WEBHOOK:-}"
LOG_FILE="./ssl-monitor.log"

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

send_slack_alert() {
    local message="$1"
    local color="$2"
    
    if [ -z "$SLACK_WEBHOOK" ]; then
        log_message "No Slack webhook configured, skipping notification"
        return
    fi
    
    curl -X POST -H 'Content-type: application/json' \
        --data "{
            \"attachments\": [{
                \"color\": \"$color\",
                \"title\": \"SSL Certificate Alert\",
                \"text\": \"$message\",
                \"ts\": $(date +%s)
            }]
        }" \
        "$SLACK_WEBHOOK" 2>/dev/null || log_message "Failed to send Slack notification"
}

check_ssl_certificate() {
    log_message "Checking SSL certificate for $DOMAIN"
    
    if ! cert_info=$(echo | timeout 10 openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" 2>/dev/null); then
        log_message "❌ Failed to connect to $DOMAIN:443"
        send_slack_alert "Failed to connect to $DOMAIN for SSL check" "danger"
        return 1
    fi
    
    if ! expiry_date=$(echo "$cert_info" | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2); then
        log_message "❌ Failed to parse SSL certificate"
        send_slack_alert "Failed to parse SSL certificate for $DOMAIN" "danger"
        return 1
    fi
    
    expiry_unix=$(date -d "$expiry_date" +%s 2>/dev/null || echo "0")
    current_unix=$(date +%s)
    days_left=$(( (expiry_unix - current_unix) / 86400 ))
    
    subject=$(echo "$cert_info" | openssl x509 -noout -subject 2>/dev/null | sed 's/subject=//')
    issuer=$(echo "$cert_info" | openssl x509 -noout -issuer 2>/dev/null | sed 's/issuer=//')
    
    log_message "Certificate Subject: $subject"
    log_message "Certificate Issuer: $issuer"
    log_message "Certificate expires: $expiry_date"
    log_message "Days until expiration: $days_left"
    
    if [ "$days_left" -lt 0 ]; then
        message="🚨 CRITICAL: SSL certificate for $DOMAIN has EXPIRED! (expired $((-days_left)) days ago)"
        echo -e "${RED}$message${NC}"
        send_slack_alert "$message" "danger"
        return 2
    elif [ "$days_left" -lt "$CRITICAL_DAYS" ]; then
        message="🚨 CRITICAL: SSL certificate for $DOMAIN expires in $days_left days! ($expiry_date)"
        echo -e "${RED}$message${NC}"
        send_slack_alert "$message" "danger"
        return 2
    elif [ "$days_left" -lt "$WARNING_DAYS" ]; then
        message="⚠️ WARNING: SSL certificate for $DOMAIN expires in $days_left days ($expiry_date)"
        echo -e "${YELLOW}$message${NC}"
        send_slack_alert "$message" "warning"
        return 1
    else
        message="✅ SSL certificate for $DOMAIN is valid for $days_left more days ($expiry_date)"
        echo -e "${GREEN}$message${NC}"
        log_message "$message"
        return 0
    fi
}

test_ssl_connectivity() {
    log_message "Testing SSL connectivity to $DOMAIN"
    
    if timeout 5 bash -c "</dev/tcp/$DOMAIN/443" 2>/dev/null; then
        log_message "✅ Port 443 is accessible"
    else
        log_message "❌ Port 443 is not accessible"
        send_slack_alert "Port 443 not accessible for $DOMAIN" "danger"
        return 1
    fi
    
    if echo | timeout 10 openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" >/dev/null 2>&1; then
        log_message "✅ SSL handshake successful"
    else
        log_message "❌ SSL handshake failed"
        send_slack_alert "SSL handshake failed for $DOMAIN" "danger"
        return 1
    fi
    
    return 0
}

main() {
    log_message "Starting SSL monitoring for $DOMAIN"
    
    mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null || true
    
    if ! test_ssl_connectivity; then
        log_message "SSL connectivity test failed, skipping certificate check"
        exit 1
    fi
    
    check_ssl_certificate
    exit_code=$?
    
    log_message "SSL monitoring completed with exit code: $exit_code"
    exit $exit_code
}

main "$@"
