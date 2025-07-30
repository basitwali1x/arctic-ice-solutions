#!/usr/bin/env python3

import sys
import os
sys.path.append('/home/ubuntu/repos/arctic-ice-solutions/backend')

from app.excel_import import process_customer_contact_excel

def test_customer_contact_processing():
    """Test the customer contact Excel processing directly"""
    
    file_path = "/home/ubuntu/attachments/29eaa1ae-7e6d-4a83-9bcf-a0d8177d108c/West+La+Ice+Customer+List.xlsx"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    try:
        print(f"Testing customer contact processing for: {file_path}")
        result = process_customer_contact_excel(file_path)
        
        print("Processing successful!")
        print(f"Total customers imported: {result['total_imported']}")
        print(f"Sheets processed: {result['sheets_processed']}")
        print(f"Location distribution: {result['location_distribution']}")
        
        if result['customers']:
            print("\nFirst 3 customers:")
            for i, customer in enumerate(result['customers'][:3]):
                print(f"  {i+1}. {customer['name']} - {customer['location_id']} - {customer['phone']}")
        
        return True
        
    except Exception as e:
        print(f"Error processing customer contact file: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_customer_contact_processing()
