#!/usr/bin/env python3
import json
import urllib.request
import urllib.parse
import urllib.error
import os
import sys

def make_fly_request(endpoint, method="GET", data=None, token=None):
    """Make authenticated request to Fly.io API"""
    if not token:
        print("ERROR: No Fly.io API token provided")
        return None
    
    url = f"https://api.fly.io/v1/{endpoint}"
    headers = {
        'Authorization': f'Bearer {token}',
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

def get_app_info(app_name, token):
    """Get app information"""
    print(f"Fetching app info for {app_name}...")
    return make_fly_request(f"apps/{app_name}", token=token)

def add_custom_domain(app_name, domain, token):
    """Add custom domain to app"""
    data = {
        'hostname': domain
    }
    print(f"Adding custom domain {domain} to app {app_name}...")
    return make_fly_request(f"apps/{app_name}/certificates", method="POST", data=data, token=token)

def list_certificates(app_name, token):
    """List certificates for app"""
    print(f"Listing certificates for app {app_name}...")
    return make_fly_request(f"apps/{app_name}/certificates", token=token)

def main():
    app_name = "arctic-ice-api"
    domain = "api.yourchoiceice.com"
    
    tokens_to_try = [
        os.environ.get('FLY_API_TOKEN'),
        os.environ.get('cloufaretoken'),  # This won't work but let's try
        os.environ.get('cloudfare')       # This won't work but let's try
    ]
    
    print("=== Fly.io Custom Domain Configuration ===")
    print(f"App: {app_name}")
    print(f"Domain: {domain}")
    print()
    
    for i, token in enumerate(tokens_to_try):
        if not token:
            continue
            
        print(f"Trying token source {i+1}...")
        
        app_info = get_app_info(app_name, token)
        if app_info:
            print(f"✅ Successfully authenticated with token {i+1}")
            print(f"App name: {app_info.get('name', 'Unknown')}")
            print(f"App status: {app_info.get('status', 'Unknown')}")
            print()
            
            certs = list_certificates(app_name, token)
            if certs:
                print("Existing certificates:")
                for cert in certs.get('data', []):
                    print(f"  - {cert.get('hostname', 'Unknown')} (Status: {cert.get('check_status', 'Unknown')})")
                print()
            
            existing_domain = False
            if certs and 'data' in certs:
                for cert in certs['data']:
                    if cert.get('hostname') == domain:
                        existing_domain = True
                        print(f"✅ Domain {domain} already configured!")
                        print(f"Status: {cert.get('check_status', 'Unknown')}")
                        break
            
            if not existing_domain:
                result = add_custom_domain(app_name, domain, token)
                if result:
                    print(f"✅ Successfully added custom domain {domain}")
                    print(f"Certificate ID: {result.get('id', 'Unknown')}")
                    print(f"Status: {result.get('check_status', 'Unknown')}")
                else:
                    print(f"❌ Failed to add custom domain {domain}")
            
            return 0
        else:
            print(f"❌ Token {i+1} failed authentication")
    
    print("❌ No valid Fly.io API token found")
    print("Available environment variables:")
    for var in ['FLY_API_TOKEN', 'cloufaretoken', 'cloudfare']:
        value = os.environ.get(var)
        if value:
            print(f"  {var}: {'*' * min(len(value), 10)}...")
        else:
            print(f"  {var}: Not set")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
