#!/usr/bin/env python3
import json
import urllib.request
import urllib.parse
import os

def update_dns_record():
    token = os.environ.get('CLOUDFLARE_API_TOKEN')
    if not token:
        print("❌ CLOUDFLARE_API_TOKEN environment variable not set")
        return False
        
    zone_id = '18d5dc0addf920e7378c4beddd2ac009'

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    list_url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?name=yourchoiceice.com'
    req = urllib.request.Request(list_url, headers=headers)
    
    try:
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode())

        if data['success'] and data['result']:
            record_id = data['result'][0]['id']
            print(f'Found existing record ID: {record_id}')
            
            update_data = {
                'type': 'CNAME',
                'name': 'yourchoiceice.com',
                'content': 'git-pr-helper-a1lqq6oq.devinapps.com',
                'proxied': True,
                'ttl': 1
            }
            
            update_url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}'
            update_req = urllib.request.Request(update_url, 
                                              data=json.dumps(update_data).encode(),
                                              headers=headers)
            update_req.get_method = lambda: 'PUT'
            
            update_response = urllib.request.urlopen(update_req)
            update_result = json.loads(update_response.read().decode())
            
            if update_result['success']:
                print('✅ Successfully updated yourchoiceice.com DNS record')
                print(f'Now pointing to: {update_data["content"]}')
                return True
            else:
                print('❌ Failed to update DNS record')
                print(update_result)
                return False
        else:
            print('❌ Could not find existing DNS record')
            print(data)
            return False
            
    except Exception as e:
        print(f'❌ Error updating DNS record: {e}')
        return False

if __name__ == '__main__':
    update_dns_record()
