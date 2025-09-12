#!/usr/bin/env python3
"""
Clear existing customers and re-import with automatic location detection
"""

import requests
import json
import os

def main():
    backend_url = 'https://app-gkwjwdji.fly.dev'
    
    login_data = {
        "username": "admin",
        "password": "secure-production-password-2024"
    }
    
    login_response = requests.post(f'{backend_url}/api/auth/login', json=login_data)
    if login_response.status_code != 200:
        print(f'Login failed: {login_response.text}')
        return
        
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    customers_response = requests.get(f'{backend_url}/api/customers', headers=headers)
    if customers_response.status_code == 200:
        customers = customers_response.json()
        print(f'Found {len(customers)} existing customers to clear')
        
    
    excel_path = '/home/ubuntu/attachments/f7e8b46b-027e-4324-8d34-79503b26093d/West+La+Ice+Customer+List+new.xlsx'
    
    with open(excel_path, 'rb') as f:
        files = {'files': ('West+La+Ice+Customer+List+new.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        data = {'location_id': 'auto'}
        
        response = requests.post(
            f'{backend_url}/api/customers/bulk-import',
            files=files,
            data=data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print('Import successful!')
            print(f"Customers imported: {result['summary']['customers_imported']}")
            print(f"Location distribution: {result['summary']['location_distribution']}")
        else:
            print(f'Import failed: {response.status_code} - {response.text}')

if __name__ == '__main__':
    main()
