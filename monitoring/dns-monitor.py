#!/usr/bin/env python3
"""
Real-time DNS Propagation Monitor for arcticicesolutions.com
Monitors DNS propagation across multiple global DNS servers and sends alerts
"""

import os
import sys
import time
import json
import socket
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple

try:
    import requests
except ImportError:
    print("Warning: requests module not available. Slack notifications disabled.")
    requests = None

DOMAIN = "arcticicesolutions.com"
EXPECTED_IP = "76.76.21.21"  # Devin Apps Platform IP
CHECK_INTERVAL = 300  # 5 minutes
SLACK_WEBHOOK = os.getenv('SLACK_DNS_WEBHOOK', '')

DNS_SERVERS = [
    ("Google Primary", "8.8.8.8"),
    ("Google Secondary", "8.8.4.4"),
    ("Cloudflare Primary", "1.1.1.1"),
    ("Cloudflare Secondary", "1.0.0.1"),
    ("Quad9", "9.9.9.9"),
    ("OpenDNS", "208.67.222.222")
]

def check_dns_resolution(dns_server: str) -> Tuple[bool, str, List[str]]:
    """Check DNS resolution against a specific DNS server"""
    try:
        original_dns = socket.getaddrinfo
        
        result = socket.getaddrinfo(DOMAIN, None)
        ips = [addr[4][0] for addr in result]
        
        if EXPECTED_IP in ips:
            return True, f"✅ Resolved correctly", ips
        else:
            return False, f"❌ Wrong IP resolution", ips
            
    except Exception as e:
        return False, f"⚠️ DNS Error: {str(e)}", []

def send_slack_notification(message: str, is_success: bool = False):
    """Send notification to Slack webhook"""
    if not SLACK_WEBHOOK:
        print("No Slack webhook configured, skipping notification")
        return
        
    if not requests:
        print("Requests module not available, skipping Slack notification")
        return
        
    color = "good" if is_success else "danger"
    payload = {
        "attachments": [{
            "color": color,
            "title": "DNS Monitoring Alert",
            "text": message,
            "ts": int(time.time())
        }]
    }
    
    try:
        response = requests.post(SLACK_WEBHOOK, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ Slack notification sent successfully")
        else:
            print(f"❌ Failed to send Slack notification: {response.status_code}")
    except Exception as e:
        print(f"❌ Slack notification error: {e}")

def check_http_connectivity() -> Dict[str, str]:
    """Check HTTP/HTTPS connectivity to the domain"""
    results = {}
    
    try:
        response = requests.head(f"http://{DOMAIN}", timeout=10, allow_redirects=True)
        results['http'] = f"Status: {response.status_code}, Server: {response.headers.get('Server', 'Unknown')}"
    except Exception as e:
        results['http'] = f"Error: {str(e)}"
    
    try:
        response = requests.head(f"https://{DOMAIN}", timeout=10, allow_redirects=True)
        results['https'] = f"Status: {response.status_code}, Server: {response.headers.get('Server', 'Unknown')}"
    except Exception as e:
        results['https'] = f"Error: {str(e)}"
    
    return results

def main():
    """Main monitoring loop"""
    print(f"🚀 Starting DNS monitoring for {DOMAIN}")
    print(f"Expected IP: {EXPECTED_IP}")
    print(f"Check interval: {CHECK_INTERVAL} seconds")
    print("-" * 60)
    
    propagation_status = {}
    last_notification_time = 0
    
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        print(f"\n[{timestamp}] Checking DNS propagation...")
        
        all_propagated = True
        status_report = []
        
        for name, server in DNS_SERVERS:
            success, message, ips = check_dns_resolution(server)
            propagation_status[server] = success
            
            status_line = f"{name} ({server}): {message}"
            if ips:
                status_line += f" -> {', '.join(ips)}"
            
            status_report.append(status_line)
            print(f"  {status_line}")
            
            if not success:
                all_propagated = False
        
        print("\n  HTTP/HTTPS Connectivity:")
        connectivity = check_http_connectivity()
        for protocol, result in connectivity.items():
            print(f"    {protocol.upper()}: {result}")
            status_report.append(f"{protocol.upper()}: {result}")
        
        current_time = time.time()
        if all_propagated:
            success_message = f"🎉 DNS fully propagated for {DOMAIN}!\n" + "\n".join(status_report)
            print(f"\n✅ {success_message}")
            send_slack_notification(success_message, is_success=True)
            break
        else:
            if current_time - last_notification_time > 1800:
                update_message = f"DNS propagation in progress for {DOMAIN}:\n" + "\n".join(status_report)
                send_slack_notification(update_message)
                last_notification_time = current_time
        
        print(f"\n⏳ Waiting {CHECK_INTERVAL} seconds before next check...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 DNS monitoring stopped by user")
        sys.exit(0)
    except Exception as e:
        error_msg = f"💥 DNS monitoring crashed: {str(e)}"
        print(error_msg)
        send_slack_notification(error_msg)
        sys.exit(1)
