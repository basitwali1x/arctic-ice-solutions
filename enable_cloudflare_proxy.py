#!/usr/bin/env python3
import json
import urllib.request
import urllib.parse
import urllib.error
import os
import sys

def make_cloudflare_request(endpoint, method="GET", data=None):
    """Make authenticated request to Cloudflare API"""
    api_token = os.environ.get('cl')
    if not api_token:
        print("ERROR: No Cloudflare API token found in environment")
        return None
    
    url = f"https://api.cloudflare.com/client/v4/{endpoint}"
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers, method=method)
        if data:
            req.data = json.dumps(data).encode('utf-8')
        
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTP Error {e.code}: {error_body}")
        return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def get_zone_id(domain):
    """Get zone ID for a specific domain"""
    result = make_cloudflare_request("zones")
    if result and result.get('success'):
        zones = result.get('result', [])
        for zone in zones:
            if zone['name'] == domain:
                return zone['id']
    return None

def get_dns_records(zone_id):
    """Get all DNS records for a zone"""
    result = make_cloudflare_request(f"zones/{zone_id}/dns_records")
    if result and result.get('success'):
        return result.get('result', [])
    return []

def enable_proxy_for_domain(zone_id, record_id, record_type, name, content):
    """Enable Cloudflare proxy for a DNS record"""
    data = {
        'type': record_type,
        'name': name,
        'content': content,
        'proxied': True,
        'ttl': 1
    }
    print(f"Enabling Cloudflare proxy for {name}...")
    result = make_cloudflare_request(f"zones/{zone_id}/dns_records/{record_id}", method="PUT", data=data)
    return result

def main():
    domain = "yourchoiceice.com"
    
    print("=== Cloudflare Proxy Configuration ===")
    print(f"Domain: {domain}")
    print("Enabling Cloudflare proxy for SSL termination")
    print()
    
    zone_id = get_zone_id(domain)
    if not zone_id:
        print(f"ERROR: Could not find zone for {domain}")
        return 1
    
    print(f"Found zone ID: {zone_id}")
    print()
    
    records = get_dns_records(zone_id)
    print("Current DNS records:")
    for record in records:
        print(f"  {record['type']} {record['name']} -> {record['content']} (Proxied: {record.get('proxied', False)})")
    print()
    
    main_record = None
    for record in records:
        if record['name'] == domain:
            main_record = record
            break
    
    if main_record:
        print(f"Found existing record for {domain}:")
        print(f"  Type: {main_record['type']}")
        print(f"  Content: {main_record['content']}")
        print(f"  Proxied: {main_record.get('proxied', False)}")
        
        if main_record.get('proxied', False):
            print("✅ Cloudflare proxy already enabled!")
            print("SSL termination should be handled by Cloudflare")
            return 0
        else:
            print("⚠️  Cloudflare proxy is disabled")
            print("Enabling proxy for SSL termination...")
            
            result = enable_proxy_for_domain(
                zone_id, 
                main_record['id'], 
                main_record['type'], 
                main_record['name'], 
                main_record['content']
            )
            
            if result and result.get('success'):
                print("✅ Cloudflare proxy enabled successfully!")
                updated_record = result.get('result', {})
                print(f"  ID: {updated_record.get('id')}")
                print(f"  Name: {updated_record.get('name')}")
                print(f"  Content: {updated_record.get('content')}")
                print(f"  Proxied: {updated_record.get('proxied')}")
                print()
                print("🔒 SSL Certificate: Cloudflare will now provide SSL termination")
                print("🌐 This should resolve the SSL certificate error for yourchoiceice.com")
                print("⏱️  Changes may take 1-2 minutes to propagate")
            else:
                print("❌ Failed to enable Cloudflare proxy")
                if result:
                    print(f"Error: {result.get('errors', [])}")
                return 1
    else:
        print(f"ERROR: No DNS record found for {domain}")
        print("Please ensure the CNAME record exists first")
        return 1
    
    print()
    print("=== Cloudflare Proxy Configuration Complete ===")
    print("You can test with: curl -I https://yourchoiceice.com")
    print("The SSL certificate should now be provided by Cloudflare")
    return 0

if __name__ == "__main__":
    sys.exit(main())
