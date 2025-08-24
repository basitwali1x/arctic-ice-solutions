import pandas as pd
import json
from datetime import datetime
from typing import List, Dict, Any
import logging

def clean_excel_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize Excel data"""
    required_cols = ['Type', 'Date', 'Name', 'Amount']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"Missing required columns for sales data format: {missing_cols}")
        return pd.DataFrame()

    df_clean = df.dropna(subset=['Type', 'Date', 'Name', 'Amount'], how='any')

    df_clean = df_clean[df_clean['Type'].isin(['Invoice', 'Sales Receipt'])]

    df_clean['Qty'] = pd.to_numeric(df_clean['Qty'], errors='coerce').fillna(0)
    df_clean['Sales Price'] = pd.to_numeric(df_clean['Sales Price'], errors='coerce').fillna(0)
    df_clean['Amount'] = pd.to_numeric(df_clean['Amount'], errors='coerce').fillna(0)

    df_clean['Name'] = df_clean['Name'].astype(str).str.strip()
    df_clean['Item'] = df_clean['Item'].astype(str).str.strip()
    df_clean['Num'] = df_clean['Num'].astype(str).str.strip()

    df_clean['Date'] = pd.to_datetime(df_clean['Date'], errors='coerce')

    df_clean = df_clean.dropna(subset=['Date'])
    df_clean = df_clean[df_clean['Amount'] > 0]

    return df_clean

def extract_customers_from_excel(df: pd.DataFrame, location_id: str = "loc_3", location_name: str = "Lufkin") -> List[Dict[str, Any]]:
    """Extract unique customers from Excel data with proper location mapping"""
    customers = []
    unique_customers = df['Name'].unique()

    location_config = {
        "loc_1": {
            "area_code": "337",
            "state": "Louisiana",
            "zip_base": 71446,
            "city": "Leesville",
            "keywords": ["leesville"]
        },
        "loc_2": {
            "area_code": "337",
            "state": "Louisiana",
            "zip_base": 70601,
            "city": "Lake Charles",
            "keywords": ["lake charles", "lakecharles"]
        },
        "loc_3": {
            "area_code": "936",
            "state": "Texas",
            "zip_base": 75901,
            "city": "Lufkin",
            "keywords": ["lufkin"]
        },
        "loc_4": {
            "area_code": "903",
            "state": "Texas",
            "zip_base": 75951,
            "city": "Jasper",
            "keywords": ["jasper"]
        }
    }

    def detect_location_from_name(customer_name: str) -> str:
        """Detect location based on customer name keywords"""
        name_lower = customer_name.lower()
        for loc_id, config in location_config.items():
            for keyword in config["keywords"]:
                if keyword in name_lower:
                    return loc_id
        return location_id

    for i, customer_name in enumerate(unique_customers):
        if pd.isna(customer_name) or customer_name == 'nan':
            continue

        detected_location_id = detect_location_from_name(customer_name)
        config = location_config.get(detected_location_id, location_config["loc_3"])
        
        customer_data = df[df['Name'] == customer_name]
        total_orders = len(customer_data)
        total_spent = customer_data['Amount'].sum()
        last_order = customer_data['Date'].max()

        customers.append({
            "id": f"{config['city'].lower()}_customer_{i+1}",
            "name": customer_name,
            "contact_person": "",
            "phone": f"({config['area_code']}) 555-{1000 + i:04d}",
            "email": f"{customer_name.lower().replace(' ', '').replace('#', '').replace('-', '').replace('.', '').replace(',', '')}@email.com",
            "address": f"{100 + i} Customer St",
            "city": config['city'],
            "state": config['state'],
            "zip_code": str(config['zip_base'] + (i % 100)),
            "location_id": detected_location_id,
            "credit_limit": 5000.0,
            "payment_terms": 30,
            "is_active": True,
            "coordinates": None
        })

    return customers

def extract_orders_from_excel(df: pd.DataFrame, location_id: str = "loc_3", location_name: str = "Lufkin") -> List[Dict[str, Any]]:
    """Extract orders from Excel data"""
    orders = []

    location_config = {
        "loc_1": {"keywords": ["leesville"], "city": "leesville"},
        "loc_2": {"keywords": ["lake charles", "lakecharles"], "city": "lakecharles"},
        "loc_3": {"keywords": ["lufkin"], "city": "lufkin"},
        "loc_4": {"keywords": ["jasper"], "city": "jasper"}
    }

    def detect_location_from_name(customer_name: str) -> str:
        """Detect location based on customer name keywords"""
        name_lower = customer_name.lower()
        for loc_id, config in location_config.items():
            for keyword in config["keywords"]:
                if keyword in name_lower:
                    return loc_id
        return location_id

    for i, row in df.iterrows():
        if pd.isna(row['Name']) or pd.isna(row['Date']) or row['Amount'] <= 0:
            continue

        detected_location_id = detect_location_from_name(row['Name'])
        city_name = location_config.get(detected_location_id, {"city": "lufkin"})["city"]

        item_desc = str(row['Item']).lower()
        qty = row['Qty']
        price = row['Sales Price']

        if price <= 1.5 and qty <= 500:
            product_type = "8lb_bag"
        elif price <= 2.0 and qty <= 200:
            product_type = "20lb_bag"
        else:
            product_type = "8lb_bag"

        orders.append({
            "id": f"{city_name}_order_{i+1}",
            "customer_name": row['Name'],
            "date": row['Date'].isoformat(),
            "invoice_number": str(row['Num']) if pd.notna(row['Num']) else f"INV-{i+1}",
            "type": row['Type'],
            "product_type": product_type,
            "quantity": int(qty),
            "unit_price": float(price),
            "total_amount": float(row['Amount']),
            "status": "completed",
            "payment_method": "cash",
            "location_id": detected_location_id
        })

    return orders

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
