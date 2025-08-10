#!/usr/bin/env python3
import socket
import ssl
import json
from datetime import datetime
import sys
import urllib.request
import urllib.error

def check_dns_resolution(domain):
    """Check if domain resolves to an IP address"""
    try:
        ip = socket.gethostbyname(domain)
        return {"domain": domain, "status": "resolved", "ip": ip}
    except socket.gaierror as e:
        return {"domain": domain, "status": "failed", "error": str(e)}

def check_http_status(url):
    """Check HTTP status of URL"""
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            return {
                "url": url,
                "status": "accessible",
                "http_code": response.getcode(),
                "headers": dict(response.headers)
            }
    except urllib.error.URLError as e:
        return {"url": url, "status": "failed", "error": str(e)}
    except Exception as e:
        return {"url": url, "status": "failed", "error": str(e)}

def check_ssl_certificate(domain, port=443):
    """Check SSL certificate status"""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
        if cert and 'notAfter' in cert:
            expiry_str = cert['notAfter']
            expiry_date = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z')
            days_remaining = (expiry_date - datetime.utcnow()).days
            
            status = "healthy"
            if days_remaining < 7:
                status = "critical"
            elif days_remaining < 30:
                status = "warning"
            
            return {
                "domain": domain,
                "status": status,
                "days_remaining": days_remaining,
                "expiry_date": expiry_date.isoformat(),
                "issuer": cert.get('issuer', [{}])[0].get('organizationName', 'Unknown') if cert.get('issuer') else 'Unknown'
            }
        else:
            return {"domain": domain, "status": "no_cert", "error": "No certificate found"}
            
    except Exception as e:
        return {"domain": domain, "status": "error", "error": str(e)}

def main():
    domains = ["yourchoiceice.com", "api.yourchoiceice.com"]
    urls = ["https://yourchoiceice.com", "https://api.yourchoiceice.com/healthz"]
    
    print("=== DNS Configuration Check ===")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print()
    
    print("1. DNS Resolution Status:")
    dns_results = []
    for domain in domains:
        result = check_dns_resolution(domain)
        dns_results.append(result)
        status_icon = "✅" if result["status"] == "resolved" else "❌"
        if result["status"] == "resolved":
            print(f"   {status_icon} {domain} -> {result['ip']}")
        else:
            print(f"   {status_icon} {domain} -> {result['error']}")
    print()
    
    print("2. HTTP Accessibility:")
    http_results = []
    for url in urls:
        result = check_http_status(url)
        http_results.append(result)
        status_icon = "✅" if result["status"] == "accessible" and result.get("http_code") == 200 else "❌"
        if result["status"] == "accessible":
            print(f"   {status_icon} {url} -> HTTP {result['http_code']} ({result['response_time']:.2f}s)")
        else:
            print(f"   {status_icon} {url} -> {result['error']}")
    print()
    
    print("3. SSL Certificate Status:")
    ssl_results = []
    for domain in domains:
        result = check_ssl_certificate(domain)
        ssl_results.append(result)
        if result["status"] == "healthy":
            print(f"   ✅ {domain} -> Valid ({result['days_remaining']} days remaining)")
        elif result["status"] == "warning":
            print(f"   ⚠️  {domain} -> Expires soon ({result['days_remaining']} days remaining)")
        elif result["status"] == "critical":
            print(f"   🚨 {domain} -> Expires very soon ({result['days_remaining']} days remaining)")
        else:
            print(f"   ❌ {domain} -> {result['error']}")
    print()
    
    print("=== Summary ===")
    resolved_domains = sum(1 for r in dns_results if r["status"] == "resolved")
    accessible_urls = sum(1 for r in http_results if r["status"] == "accessible" and r.get("http_code") == 200)
    healthy_ssl = sum(1 for r in ssl_results if r["status"] == "healthy")
    
    print(f"DNS Resolution: {resolved_domains}/{len(domains)} domains resolved")
    print(f"HTTP Access: {accessible_urls}/{len(urls)} URLs accessible")
    print(f"SSL Health: {healthy_ssl}/{len(domains)} certificates healthy")
    
    if resolved_domains == 0:
        print("\n🚨 CRITICAL: No domains are resolving. DNS configuration issue detected.")
    elif accessible_urls == 0:
        print("\n⚠️  WARNING: Domains resolve but services are not accessible.")
    elif resolved_domains == len(domains) and accessible_urls == len(urls):
        print("\n✅ All systems operational.")
    
    detailed_results = {
        "timestamp": datetime.utcnow().isoformat(),
        "dns_resolution": dns_results,
        "http_accessibility": http_results,
        "ssl_certificates": ssl_results,
        "summary": {
            "domains_resolved": resolved_domains,
            "urls_accessible": accessible_urls,
            "ssl_healthy": healthy_ssl,
            "total_domains": len(domains),
            "total_urls": len(urls)
        }
    }
    
    with open("dns_check_results.json", "w") as f:
        json.dump(detailed_results, f, indent=2)
    
    print(f"\nDetailed results saved to: dns_check_results.json")

if __name__ == "__main__":
    main()
