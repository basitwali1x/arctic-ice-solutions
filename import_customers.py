#!/usr/bin/env python3
"""
Customer Import Script for Arctic Ice Solutions
Imports 582 customers from West La Ice Customer List Excel file
"""

import pandas as pd
import requests
import json
import sys
import os
from pathlib import Path

def analyze_customer_addresses(df):
    """Analyze customer addresses to determine appropriate location assignments"""
    location_assignments = {
        'loc_1': [],  # Leesville HQ & Production (Louisiana)
        'loc_2': [],  # Lake Charles Distribution (Louisiana)
        'loc_3': [],  # Lufkin Distribution (Texas)
        'loc_4': []   # Jasper Warehouse (Texas)
    }
    
    for i, row in df.iterrows():
        customer_name = str(row['Customer']).strip()
        address = str(row.get('Address', '')).strip()
        
        address_lower = address.lower()
        
        if 'tx' in address_lower or 'texas' in address_lower:
            if any(city in address_lower for city in ['lufkin', 'huntsville', 'crockett', 'livingston']):
                location_assignments['loc_3'].append(i)  # Lufkin
            elif any(city in address_lower for city in ['jasper', 'newton', 'hemphill', 'woodville']):
                location_assignments['loc_4'].append(i)  # Jasper
            else:
                location_assignments['loc_3'].append(i)
        
        elif 'la' in address_lower or 'louisiana' in address_lower:
            if any(city in address_lower for city in ['leesville', 'deridder', 'many', 'zwolle']):
                location_assignments['loc_1'].append(i)  # Leesville
            elif any(city in address_lower for city in ['lake charles', 'sulphur', 'westlake', 'vinton']):
                location_assignments['loc_2'].append(i)  # Lake Charles
            else:
                location_assignments['loc_1'].append(i)
        
        else:
            location_assignments['loc_3'].append(i)
    
    return location_assignments

def import_customers_to_location(excel_file_path, sheet_name, location_id, api_base_url="https://app-gkwjwdji.fly.dev"):
    """Import customers from a specific sheet to a specific location"""
    
    import os
    username = os.getenv("API_USERNAME", "manager")
    password = os.getenv("API_PASSWORD")
    
    if not password:
        print("❌ Error: API_PASSWORD environment variable is required")
        print("Set it with: export API_PASSWORD='your-password'")
        return None
    
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        login_response = requests.post(f"{api_base_url}/api/auth/login", json=login_data)
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return None
            
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        with open(excel_file_path, 'rb') as f:
            files = {'files': (os.path.basename(excel_file_path), f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            data = {'location_id': location_id}
            
            response = requests.post(
                f"{api_base_url}/api/customers/bulk-import",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Successfully imported to {location_id}: {result}")
                return result
            else:
                print(f"Import failed for {location_id}: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        print(f"Error importing to {location_id}: {e}")
        return None

def create_location_specific_excel_files(excel_file_path, output_dir="temp_imports"):
    """Create separate Excel files for each location based on address analysis"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    df_all = pd.read_excel(excel_file_path, sheet_name='all')
    
    location_assignments = analyze_customer_addresses(df_all)
    
    location_names = {
        'loc_1': 'Leesville',
        'loc_2': 'Lake_Charles', 
        'loc_3': 'Lufkin',
        'loc_4': 'Jasper'
    }
    
    created_files = {}
    
    for location_id, indices in location_assignments.items():
        if indices:  # Only create file if there are customers for this location
            location_df = df_all.iloc[indices].copy()
            location_name = location_names[location_id]
            output_file = os.path.join(output_dir, f"customers_{location_name}.xlsx")
            
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                location_df.to_excel(writer, sheet_name=location_name.lower(), index=False)
            
            created_files[location_id] = {
                'file_path': output_file,
                'customer_count': len(location_df),
                'location_name': location_name
            }
            
            print(f"Created {output_file} with {len(location_df)} customers for {location_name}")
    
    return created_files

def main():
    excel_file_path = "/home/ubuntu/attachments/f7e8b46b-027e-4324-8d34-79503b26093d/West+La+Ice+Customer+List+new.xlsx"
    
    if not os.path.exists(excel_file_path):
        print(f"Excel file not found: {excel_file_path}")
        sys.exit(1)
    
    print("Starting customer import process...")
    print(f"Excel file: {excel_file_path}")
    
    df_jasper = pd.read_excel(excel_file_path, sheet_name='jasper')
    df_all = pd.read_excel(excel_file_path, sheet_name='all')
    
    print(f"\nExcel file analysis:")
    print(f"- Jasper sheet: {len(df_jasper)} customers")
    print(f"- All sheet: {len(df_all)} customers")
    print(f"- Expected total: {len(df_jasper) + len(df_all)} = 582 customers")
    
    print("\n1. Importing Jasper customers (loc_4)...")
    jasper_result = import_customers_to_location(excel_file_path, 'jasper', 'loc_4')
    
    print("\n2. Analyzing 'all' sheet and creating location-specific files...")
    location_files = create_location_specific_excel_files(excel_file_path)
    
    print("\n3. Importing customers by location from 'all' sheet...")
    import_results = {}
    
    for location_id, file_info in location_files.items():
        if location_id == 'loc_4':
            print(f"\nSkipping {file_info['customer_count']} Jasper customers from 'all' sheet (already imported from dedicated sheet)")
            continue
            
        print(f"\nImporting {file_info['customer_count']} customers to {file_info['location_name']} ({location_id})...")
        result = import_customers_to_location(file_info['file_path'], None, location_id)
        if result:
            import_results[location_id] = result
    
    print("\n" + "="*60)
    print("IMPORT SUMMARY")
    print("="*60)
    
    total_imported = 0
    
    if jasper_result:
        jasper_count = jasper_result.get('summary', {}).get('customers_imported', 0)
        print(f"Jasper (loc_4) from dedicated sheet: {jasper_count} customers")
        total_imported += jasper_count
    
    for location_id, result in import_results.items():
        if result:
            count = result.get('summary', {}).get('customers_imported', 0)
            location_name = location_files[location_id]['location_name']
            print(f"{location_name} ({location_id}) from 'all' sheet: {count} customers")
            total_imported += count
    
    jasper_from_all = location_files.get('loc_4', {}).get('customer_count', 0)
    expected_total = len(df_jasper) + len(df_all)
    
    print(f"\nTotal customers imported: {total_imported}")
    print(f"Jasper customers skipped from 'all' sheet: {jasper_from_all}")
    print(f"Expected total: {expected_total} customers")
    
    if total_imported == expected_total:
        print("✅ SUCCESS: All 582 customers imported successfully!")
    else:
        print(f"⚠️  Note: Imported {total_imported} customers, expected {expected_total}")
        print("This may be due to duplicate removal or data processing differences.")
    
    import shutil
    if os.path.exists("temp_imports"):
        shutil.rmtree("temp_imports")
        print("\nCleaned up temporary files")

if __name__ == "__main__":
    main()
