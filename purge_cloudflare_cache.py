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

def purge_cache(zone_id, urls):
    """Purge cache for specific URLs"""
    data = {
        'files': urls
    }
    print(f"Purging cache for URLs: {urls}")
    result = make_cloudflare_request(f"zones/{zone_id}/purge_cache", method="POST", data=data)
    return result

def main():
    zone_id = "18d5dc0addf920e7378c4beddd2ac009"  # yourchoiceice.com zone ID
    urls_to_purge = [
        "https://yourchoiceice.com",
        "https://yourchoiceice.com/",
        "https://yourchoiceice.com/*"
    ]
    
    print("=== Cloudflare Cache Purge ===")
    print(f"Zone ID: {zone_id}")
    print(f"URLs to purge: {urls_to_purge}")
    print()
    
    result = purge_cache(zone_id, urls_to_purge)
    if result and result.get('success'):
        print("✅ Cache purged successfully!")
        print(f"Purge ID: {result.get('result', {}).get('id', 'N/A')}")
        print("Cache should be cleared within 30 seconds.")
    else:
        print("❌ Failed to purge cache")
        if result:
            print(f"Errors: {result.get('errors', [])}")
        return 1
    
    print()
    print("=== Cache Purge Complete ===")
    print("You can now test: https://yourchoiceice.com")
    return 0

if __name__ == "__main__":
    sys.exit(main())
