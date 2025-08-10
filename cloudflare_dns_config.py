#!/usr/bin/env python3
import json
import urllib.request
import urllib.parse
import urllib.error
import os
import sys

def make_cloudflare_request(endpoint, method="GET", data=None):
    """Make authenticated request to Cloudflare API"""
    api_token = os.environ.get('cloufaretoken')
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

def get_zones():
    """Get all zones accessible with the API token"""
    print("Fetching Cloudflare zones...")
    result = make_cloudflare_request("zones")
    if result and result.get('success'):
        return result.get('result', [])
    return []

def get_zone_id(domain):
    """Get zone ID for a specific domain"""
    zones = get_zones()
    for zone in zones:
        if zone['name'] == domain:
            return zone['id']
    return None

def get_dns_records(zone_id):
    """Get all DNS records for a zone"""
    print(f"Fetching DNS records for zone {zone_id}...")
    result = make_cloudflare_request(f"zones/{zone_id}/dns_records")
    if result and result.get('success'):
        return result.get('result', [])
    return []

def create_dns_record(zone_id, record_type, name, content, ttl=1):
    """Create a new DNS record"""
    data = {
        'type': record_type,
        'name': name,
        'content': content,
        'ttl': ttl
    }
    print(f"Creating {record_type} record: {name} -> {content}")
    result = make_cloudflare_request(f"zones/{zone_id}/dns_records", method="POST", data=data)
    return result

def update_dns_record(zone_id, record_id, record_type, name, content, ttl=1):
    """Update an existing DNS record"""
    data = {
        'type': record_type,
        'name': name,
        'content': content,
        'ttl': ttl
    }
    print(f"Updating {record_type} record: {name} -> {content}")
    result = make_cloudflare_request(f"zones/{zone_id}/dns_records/{record_id}", method="PUT", data=data)
    return result

def main():
    domain = "yourchoiceice.com"
    subdomain = "api.yourchoiceice.com"
    target = "arctic-ice-api.fly.dev"
    
    print("=== Cloudflare DNS Configuration ===")
    print(f"Domain: {domain}")
    print(f"Target subdomain: {subdomain}")
    print(f"Target: {target}")
    print()
    
    zone_id = get_zone_id(domain)
    if not zone_id:
        print(f"ERROR: Could not find zone for {domain}")
        print("Available zones:")
        zones = get_zones()
        for zone in zones:
            print(f"  - {zone['name']} (ID: {zone['id']})")
        return 1
    
    print(f"Found zone ID: {zone_id}")
    print()
    
    records = get_dns_records(zone_id)
    print("Current DNS records:")
    for record in records:
        print(f"  {record['type']} {record['name']} -> {record['content']}")
    print()
    
    api_record = None
    for record in records:
        if record['name'] == subdomain:
            api_record = record
            break
    
    if api_record:
        print(f"Found existing record for {subdomain}:")
        print(f"  Type: {api_record['type']}")
        print(f"  Content: {api_record['content']}")
        print(f"  TTL: {api_record['ttl']}")
        
        if api_record['content'] == target:
            print("✅ Record already points to correct target!")
            return 0
        else:
            print(f"⚠️  Record points to {api_record['content']}, should be {target}")
            print(f"Updating CNAME record to point to {target}...")
            
            result = update_dns_record(zone_id, api_record['id'], "CNAME", subdomain, target)
            if result and result.get('success'):
                print("✅ CNAME record updated successfully!")
                updated_record = result.get('result', {})
                print(f"  ID: {updated_record.get('id')}")
                print(f"  Name: {updated_record.get('name')}")
                print(f"  Content: {updated_record.get('content')}")
            else:
                print("❌ Failed to update CNAME record")
                if result:
                    print(f"Error: {result.get('errors', [])}")
                return 1
    else:
        print(f"No existing record found for {subdomain}")
        print(f"Creating CNAME record: {subdomain} -> {target}")
        
        result = create_dns_record(zone_id, "CNAME", subdomain, target)
        if result and result.get('success'):
            print("✅ CNAME record created successfully!")
            new_record = result.get('result', {})
            print(f"  ID: {new_record.get('id')}")
            print(f"  Name: {new_record.get('name')}")
            print(f"  Content: {new_record.get('content')}")
        else:
            print("❌ Failed to create CNAME record")
            if result:
                print(f"Error: {result.get('errors', [])}")
            return 1
    
    print()
    print("=== DNS Configuration Complete ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
