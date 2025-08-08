#!/bin/bash

DOMAIN="arcticicesolutions.com"
API_DOMAIN="api.arcticicesolutions.com"
MONITORING_EMAIL="${MONITORING_EMAIL:-admin@arcticicesolutions.com}"

check_ssl_expiry() {
    local domain=$1
    echo "Checking SSL certificate for $domain..."
    
    expiry=$(openssl s_client -connect $domain:443 -servername $domain 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | grep notAfter | cut -d= -f2)
    
    if [ -z "$expiry" ]; then
        echo "ERROR: Could not retrieve SSL certificate for $domain"
        return 1
    fi
    
    expiry_epoch=$(date -d "$expiry" +%s 2>/dev/null)
    current_epoch=$(date +%s)
    days_left=$(( (expiry_epoch - current_epoch) / 86400 ))
    
    echo "SSL certificate for $domain expires on: $expiry"
    echo "Days remaining: $days_left"
    
    if [ $days_left -lt 30 ]; then
        echo "WARNING: SSL certificate for $domain expires in $days_left days!"
        echo "SSL certificate for $domain expires in $days_left days!" | mail -s "SSL Certificate Warning" $MONITORING_EMAIL 2>/dev/null || echo "Mail not configured"
    elif [ $days_left -lt 7 ]; then
        echo "CRITICAL: SSL certificate for $domain expires in $days_left days!"
        echo "CRITICAL: SSL certificate for $domain expires in $days_left days!" | mail -s "SSL Certificate CRITICAL" $MONITORING_EMAIL 2>/dev/null || echo "Mail not configured"
    else
        echo "SSL certificate for $domain is valid for $days_left more days"
    fi
    
    return 0
}

echo "=== Arctic Ice Solutions SSL Certificate Monitor ==="
echo "Monitoring domains: $DOMAIN, $API_DOMAIN"
echo "Alert email: $MONITORING_EMAIL"
echo ""

check_ssl_expiry $DOMAIN
echo ""
check_ssl_expiry $API_DOMAIN

echo ""
echo "SSL monitoring complete. $(date)"
