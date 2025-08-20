#!/usr/bin/env python3
"""
Test automatic location detection with the Excel file locally
"""

import sys
import os
sys.path.append('/home/ubuntu/repos/arctic-ice-solutions/backend')

from app.excel_import import process_customer_excel_files

def main():
    excel_path = '/home/ubuntu/attachments/f7e8b46b-027e-4324-8d34-79503b26093d/West+La+Ice+Customer+List+new.xlsx'
    
    print("Testing automatic location detection with Excel file...")
    print(f"Processing: {excel_path}")
    
    processed_data = process_customer_excel_files([excel_path], "auto", "Auto-Detect")
    
    location_distribution = {}
    for customer in processed_data["customers"]:
        location_id = customer["location_id"]
        location_distribution[location_id] = location_distribution.get(location_id, 0) + 1
    
    print(f"\nTotal customers processed: {len(processed_data['customers'])}")
    print("Location distribution:")
    location_names = {
        "loc_1": "Leesville",
        "loc_2": "Lake Charles", 
        "loc_3": "Lufkin",
        "loc_4": "Jasper"
    }
    
    for loc_id, count in sorted(location_distribution.items()):
        location_name = location_names.get(loc_id, loc_id)
        print(f"  {location_name} ({loc_id}): {count} customers")
    
    print("\nExample customer assignments:")
    for i, customer in enumerate(processed_data["customers"][:10]):
        location_name = location_names.get(customer["location_id"], customer["location_id"])
        print(f"  {customer['name']} -> {location_name} (based on: {customer.get('address', 'N/A')})")
    
    print("\nAutomatic location detection test completed successfully!")

if __name__ == '__main__':
    main()
