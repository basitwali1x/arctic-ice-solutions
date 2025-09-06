import sys
import os
import pandas as pd
sys.path.append('/home/ubuntu/repos/arctic-ice-solutions/backend')

from app.excel_import import process_excel_files, clean_excel_data, extract_customers_from_excel, extract_orders_from_excel
import json

def import_all_sales_files():
    """Import all sales Excel files with proper location assignment"""
    
    file_paths = [
        '/home/ubuntu/attachments/9f24ecec-6c02-437f-aa2c-f6dbc6031e77/Sales+from+A+to+Sunshine+8.xlsx',
        '/home/ubuntu/attachments/538a0738-590a-432d-890a-374877301b2a/Sales+from+Sunshine+9+to+Z.xlsx',
        '/home/ubuntu/attachments/355744ee-6b3d-4753-b674-722c9df93c0d/Sales+Coustomer+Detail.xlsm',
        '/home/ubuntu/attachments/05d4f480-3cad-4725-a315-9dd74cd77300/sales+coustomer+detail+1.xlsm',
        '/home/ubuntu/attachments/d5c9750e-ce54-4ec2-a5b8-1b4ccebc4992/sales+By+Coustomer+Detail+2.xlsm'
    ]
    
    all_customers = []
    all_orders = []
    
    for file_path in file_paths:
        print(f"Processing {file_path}...")
        try:
            df = pd.read_excel(file_path, sheet_name='Sheet1')
            
            df_clean = clean_excel_data(df)
            if df_clean.empty:
                print(f"  No valid data found in {file_path}")
                continue
                
            customers = extract_customers_from_excel(df_clean, location_id="loc_3", location_name="Lufkin")
            orders = extract_orders_from_excel(df_clean, location_id="loc_3", location_name="Lufkin")
            
            all_customers.extend(customers)
            all_orders.extend(orders)
            print(f"  Added {len(customers)} customers and {len(orders)} orders")
        except Exception as e:
            print(f"  Error processing {file_path}: {e}")
            continue
    
    unique_customers = {}
    for customer in all_customers:
        key = customer["name"].lower().strip()
        if key not in unique_customers:
            unique_customers[key] = customer
    
    final_customers = list(unique_customers.values())
    
    print(f"\nSummary:")
    print(f"Total unique customers: {len(final_customers)}")
    print(f"Total orders: {len(all_orders)}")
    
    location_summary = {}
    for customer in final_customers:
        loc = customer["location_id"]
        if loc not in location_summary:
            location_summary[loc] = {"customers": 0, "orders": 0}
        location_summary[loc]["customers"] += 1
    
    for order in all_orders:
        loc = order["location_id"]
        if loc in location_summary:
            location_summary[loc]["orders"] += 1
    
    print(f"\nLocation breakdown:")
    location_names = {
        "loc_1": "Leesville",
        "loc_2": "Lake Charles", 
        "loc_3": "Lufkin",
        "loc_4": "Jasper"
    }
    for loc_id, counts in location_summary.items():
        loc_name = location_names.get(loc_id, loc_id)
        print(f"  {loc_name} ({loc_id}): {counts['customers']} customers, {counts['orders']} orders")
    
    with open('/home/ubuntu/repos/arctic-ice-solutions/imported_sales_data.json', 'w') as f:
        json.dump({
            "customers": final_customers,
            "orders": all_orders,
            "summary": location_summary
        }, f, indent=2, default=str)
    print(f"\nData saved to imported_sales_data.json")
    
    return {
        "customers": final_customers,
        "orders": all_orders,
        "summary": location_summary
    }

if __name__ == "__main__":
    result = import_all_sales_files()
