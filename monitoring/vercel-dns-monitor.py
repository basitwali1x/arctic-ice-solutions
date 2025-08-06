#!/usr/bin/env python3
"""
Enhanced DNS Propagation Monitor for Vercel Domain Configuration
Monitors DNS propagation specifically for Vercel ALIAS and CNAME records
"""

import os
import sys
import time
import json
import socket
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Optional

try:
    import requests
except ImportError:
    print("Warning: requests module not available. HTTP checks disabled.")
    requests = None

DOMAIN = "arcticicesolutions.com"
EXPECTED_RECORDS = {
    'root': {
        'type': 'ALIAS',
        'expected': ['cname.vercel-dns.com'],
        'query_type': 'CNAME'
    },
    'www': {
        'type': 'CNAME', 
        'expected': [f'{DOMAIN}'],
        'query_type': 'CNAME'
    },
    '_vercel': {
        'type': 'TXT',
        'expected': ['vercel-verification-code'],  # Will be updated dynamically
        'query_type': 'TXT'
    }
}

CHECK_INTERVAL = 180  # 3 minutes for Vercel
SLACK_WEBHOOK = os.getenv('SLACK_DNS_WEBHOOK', '')

DNS_SERVERS = [
    ("Google Primary", "8.8.8.8"),
    ("Google Secondary", "8.8.4.4"), 
    ("Cloudflare Primary", "1.1.1.1"),
    ("Cloudflare Secondary", "1.0.0.1"),
    ("Vercel DNS", "1.1.1.1")  # Cloudflare powers Vercel
]

def load_vercel_txt_code():
    """Load Vercel verification code from file if available"""
    try:
        with open('./vercel-txt-code.txt', 'r') as f:
            code = f.read().strip()
            if code:
                EXPECTED_RECORDS['_vercel']['expected'] = [code]
                print(f"✅ Loaded Vercel verification code: {code[:20]}...")
                return True
    except FileNotFoundError:
        print("⚠️ Vercel verification code file not found")
    return False

def check_dns_record(record_name: str, record_info: dict, dns_server: str = "8.8.8.8") -> Tuple[bool, str, List[str]]:
    """Check specific DNS record against expected values"""
    try:
        if record_name == 'root':
            query_domain = DOMAIN
        elif record_name == 'www':
            query_domain = f"www.{DOMAIN}"
        elif record_name == '_vercel':
            query_domain = f"_vercel.{DOMAIN}"
        else:
            query_domain = f"{record_name}.{DOMAIN}"
        
        cmd = ['dig', f'@{dns_server}', query_domain, record_info['query_type'], '+short']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            return False, f"DNS query failed", []
        
        records = [line.strip().strip('"') for line in result.stdout.strip().split('\n') if line.strip()]
        
        if not records:
            return False, f"No {record_info['type']} record found", []
        
        if record_name == 'root' and any('vercel-dns.com' in r for r in records):
            return True, f"✅ Correct ALIAS resolution", records
        
        if record_name == 'www' and any(DOMAIN in r for r in records):
            return True, f"✅ Correct CNAME resolution", records
        
        if record_name == '_vercel' and record_info['expected'][0] != 'vercel-verification-code':
            if any(record_info['expected'][0] in r for r in records):
                return True, f"✅ Correct TXT verification", records
        
        return False, f"❌ Incorrect {record_info['type']} record", records
        
    except subprocess.TimeoutExpired:
        return False, f"⚠️ DNS query timeout", []
    except Exception as e:
        return False, f"⚠️ DNS Error: {str(e)}", []

def check_vercel_deployment_status() -> Dict[str, str]:
    """Check if domain is properly configured in Vercel"""
    results = {}
    
    try:
        if requests:
            response = requests.head(f"https://{DOMAIN}", timeout=10, allow_redirects=True)
            server = response.headers.get('Server', '')
            
            if 'vercel' in server.lower():
                results['deployment'] = f"✅ Vercel deployment active (Server: {server})"
            else:
                results['deployment'] = f"❌ Not served by Vercel (Server: {server})"
                
            results['status_code'] = f"HTTP {response.status_code}"
        else:
            results['deployment'] = "⚠️ Cannot check deployment (requests unavailable)"
            
    except Exception as e:
        results['deployment'] = f"❌ Deployment check failed: {str(e)}"
    
    return results

def send_slack_notification(message: str, is_success: bool = False):
    """Send notification to Slack webhook"""
    if not SLACK_WEBHOOK or not requests:
        return
        
    color = "good" if is_success else "warning"
    payload = {
        "attachments": [{
            "color": color,
            "title": "Vercel DNS Monitoring",
            "text": message,
            "ts": int(time.time())
        }]
    }
    
    try:
        response = requests.post(SLACK_WEBHOOK, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ Slack notification sent")
    except Exception as e:
        print(f"❌ Slack notification error: {e}")

def generate_status_report(dns_results: Dict, deployment_results: Dict) -> str:
    """Generate comprehensive status report"""
    report = []
    report.append(f"🔍 Vercel DNS Status Report for {DOMAIN}")
    report.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report.append("=" * 60)
    
    report.append("\n📋 DNS Records Status:")
    for record_name, (success, message, records) in dns_results.items():
        status_icon = "✅" if success else "❌"
        report.append(f"  {status_icon} {record_name.upper()}: {message}")
        if records:
            for record in records[:3]:  # Show first 3 records
                report.append(f"    → {record}")
    
    report.append("\n🚀 Vercel Deployment Status:")
    for key, value in deployment_results.items():
        report.append(f"  {value}")
    
    all_dns_ok = all(result[0] for result in dns_results.values())
    deployment_ok = "✅" in deployment_results.get('deployment', '')
    
    if all_dns_ok and deployment_ok:
        report.append(f"\n🎉 Overall Status: ✅ FULLY OPERATIONAL")
    elif all_dns_ok:
        report.append(f"\n⚠️ Overall Status: DNS OK, Deployment Issues")
    else:
        report.append(f"\n❌ Overall Status: DNS PROPAGATION IN PROGRESS")
    
    return "\n".join(report)

def save_status_to_file(report: str):
    """Save status report to file for dashboard"""
    try:
        status_data = {
            "timestamp": datetime.now().isoformat(),
            "domain": DOMAIN,
            "report": report,
            "status": "operational" if "FULLY OPERATIONAL" in report else "degraded"
        }
        
        with open('./vercel-dns-status.json', 'w') as f:
            json.dump(status_data, f, indent=2)
            
    except Exception as e:
        print(f"⚠️ Failed to save status file: {e}")

def main():
    """Main monitoring loop for Vercel DNS"""
    print(f"🚀 Starting Vercel DNS monitoring for {DOMAIN}")
    print(f"Expected records: ALIAS (root), CNAME (www), TXT (_vercel)")
    print(f"Check interval: {CHECK_INTERVAL} seconds")
    print("-" * 60)
    
    load_vercel_txt_code()
    
    last_notification_time = 0
    
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        print(f"\n[{timestamp}] Checking Vercel DNS configuration...")
        
        dns_results = {}
        for record_name, record_info in EXPECTED_RECORDS.items():
            success, message, records = check_dns_record(record_name, record_info)
            dns_results[record_name] = (success, message, records)
            
            status_line = f"  {record_name.upper()}: {message}"
            if records:
                status_line += f" → {', '.join(records[:2])}"
            print(status_line)
        
        print("\n  🚀 Vercel Deployment Status:")
        deployment_results = check_vercel_deployment_status()
        for key, value in deployment_results.items():
            print(f"    {value}")
        
        report = generate_status_report(dns_results, deployment_results)
        save_status_to_file(report)
        
        all_dns_ok = all(result[0] for result in dns_results.values())
        deployment_ok = "✅" in deployment_results.get('deployment', '')
        
        current_time = time.time()
        
        if all_dns_ok and deployment_ok:
            success_message = f"🎉 Vercel domain fully operational for {DOMAIN}!"
            print(f"\n✅ {success_message}")
            send_slack_notification(success_message, is_success=True)
            break
        else:
            if current_time - last_notification_time > 1800:  # Every 30 minutes
                update_message = f"Vercel DNS propagation in progress for {DOMAIN}"
                send_slack_notification(update_message)
                last_notification_time = current_time
        
        print(f"\n⏳ Waiting {CHECK_INTERVAL} seconds before next check...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Vercel DNS monitoring stopped by user")
        sys.exit(0)
    except Exception as e:
        error_msg = f"💥 Vercel DNS monitoring crashed: {str(e)}"
        print(error_msg)
        send_slack_notification(error_msg)
        sys.exit(1)
