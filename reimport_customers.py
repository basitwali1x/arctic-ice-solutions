#!/usr/bin/env python3
"""
Re-import customers from Excel file to restore the 582 customer count.
This script processes the Excel file and imports customers via the backend API.
"""

import sys
import os
import requests
import json
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.excel_import import extract_customers_from_excel

def main():
    excel_path = '/home/ubuntu/attachments/f7e8b46b-027e-4324-8d34-79503b26093d/West+La+Ice+Customer+List+new.xlsx'
    backend_url = 'https://app-gkwjwdji.fly.dev'
    
    print(f'Processing Excel file: {excel_path}')
    
    try:
        customers = extract_customers_from_excel(excel_path)
        print(f'Successfully extracted {len(customers)} customers from Excel file')
        
        if customers:
            print('Sample customer data:')
            for i, customer in enumerate(customers[:3]):
                print(f'  {i+1}. {customer.get("name", "N/A")} - {customer.get("location_id", "N/A")}')
            print(f'  ... and {len(customers)-3} more customers')
            
            print('\nAttempting to login to backend...')
            login_data = {
                "username": "admin",
                "password": "secure-production-password-2024"
            }
            
            login_response = requests.post(f'{backend_url}/api/auth/login', json=login_data)
            if login_response.status_code == 200:
                token = login_response.json()['access_token']
                print('Login successful!')
                
                headers = {'Authorization': f'Bearer {token}'}
                
                import_data = {
                    'customers': customers,
                    'location_id': 'loc_1'  # Default location
                }
                
                print(f'Importing {len(customers)} customers...')
                import_response = requests.post(
                    f'{backend_url}/api/customers/bulk-import',
                    json=import_data,
                    headers=headers
                )
                
                if import_response.status_code == 200:
                    result = import_response.json()
                    print(f'Import successful! {result.get("imported_count", len(customers))} customers imported.')
                else:
                    print(f'Import failed: {import_response.status_code} - {import_response.text}')
            else:
                print(f'Login failed: {login_response.status_code} - {login_response.text}')
                
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
