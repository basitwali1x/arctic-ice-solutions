import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import logging
import re
from fastapi import UploadFile

logger = logging.getLogger(__name__)

def clean_excel_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize Excel data"""
    required_cols = ['Type', 'Date', 'Name', 'Amount']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        logger.warning(f"Missing required columns for sales data format: {missing_cols}")
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
    df_clean = df_clean[df_clean['Amount'] > 0]  # Remove negative/zero amounts

    return df_clean

def extract_timesheet_sales_data(df: pd.DataFrame, date_from_filename: str = None) -> pd.DataFrame:
    """Extract sales data from timesheet format and convert to standard format"""
    sales_data = []

    for i, row in df.iterrows():
        if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
            continue

        customer_name = str(row.iloc[0]).strip()

        if customer_name in ['Account Name', 'TICKETS:', 'MISSING TICKETS:', 'C.P.', 'JAMIE'] or 'DRIVER:' in customer_name or 'ROUTE:' in customer_name or 'CHECK IN SHEETS' in customer_name or 'CASH SALES' in customer_name:
            continue

        qty_8lb = pd.to_numeric(row.iloc[2] if len(row) > 2 else 0, errors='coerce') or 0
        qty_20lb = pd.to_numeric(row.iloc[3] if len(row) > 3 else 0, errors='coerce') or 0

        if qty_8lb > 0:
            sales_data.append({
                'Type': 'Sales Receipt',
                'Date': date_from_filename or datetime.now().strftime('%Y-%m-%d'),
                'Name': customer_name,
                'Item': '8lb Ice Bag',
                'Qty': qty_8lb,
                'Sales Price': 1.25,
                'Amount': qty_8lb * 1.25,
                'Num': f'TS-{i}-8LB'
            })

        if qty_20lb > 0:
            sales_data.append({
                'Type': 'Sales Receipt',
                'Date': date_from_filename or datetime.now().strftime('%Y-%m-%d'),
                'Name': customer_name,
                'Item': '20lb Ice Bag',
                'Qty': qty_20lb,
                'Sales Price': 2.00,
                'Amount': qty_20lb * 2.00,
                'Num': f'TS-{i}-20LB'
            })

    if sales_data:
        return pd.DataFrame(sales_data)
    else:
        return pd.DataFrame()

def extract_customers_from_excel(df: pd.DataFrame, location_id: str = "loc_3", location_name: str = "Lufkin") -> List[Dict[str, Any]]:
    """Extract unique customers from Excel data with proper location mapping"""
    customers = []
    unique_customers = df['Name'].unique()

    location_config = {
        "loc_1": {  # Leesville HQ & Production
            "area_code": "337",
            "state": "Louisiana",
            "zip_base": 71446,
            "city": "Leesville"
        },
        "loc_2": {  # Lake Charles Distribution
            "area_code": "337",
            "state": "Louisiana",
            "zip_base": 70601,
            "city": "Lake Charles"
        },
        "loc_3": {  # Lufkin Distribution
            "area_code": "936",
            "state": "Texas",
            "zip_base": 75901,
            "city": "Lufkin"
        },
        "loc_4": {  # Jasper Warehouse
            "area_code": "903",
            "state": "Texas",
            "zip_base": 75951,
            "city": "Jasper"
        }
    }

    config = location_config.get(location_id, location_config["loc_3"])
    area_code = config["area_code"]
    state = config["state"]
    zip_base = config["zip_base"]
    city = config["city"]

    for i, customer_name in enumerate(unique_customers):
        if pd.isna(customer_name) or customer_name == 'nan':
            continue

        customer_data = df[df['Name'] == customer_name]
        total_orders = len(customer_data)
        total_spent = customer_data['Amount'].sum()
        last_order = customer_data['Date'].max()

        customers.append({
            "id": f"{city.lower()}_customer_{i+1}",
            "name": customer_name,
            "email": f"{customer_name.lower().replace(' ', '').replace('#', '').replace('-', '').replace('.', '').replace(',', '')}@email.com",
            "phone": f"({area_code}) 555-{1000 + i:04d}",
            "address": f"{100 + i} Customer St, {city}, {state} {zip_base + (i % 100)}",
            "location_id": location_id,
            "credit_limit": 5000.0,
            "current_balance": 0.0,
            "total_orders": int(total_orders),
            "total_spent": float(total_spent),
            "last_order_date": last_order.isoformat() if pd.notna(last_order) else None,
            "status": "active"
        })

    return customers

def extract_orders_from_excel(df: pd.DataFrame, location_id: str = "loc_3", location_name: str = "Lufkin") -> List[Dict[str, Any]]:
    """Extract orders from Excel data"""
    orders = []

    for i, row in df.iterrows():
        if pd.isna(row['Name']) or pd.isna(row['Date']) or row['Amount'] <= 0:
            continue

        item_desc = str(row['Item']).lower()
        qty = row['Qty']
        price = row['Sales Price']

        if price <= 1.5 and qty <= 500:  # Likely 8lb bags
            product_type = "8lb_bag"
        elif price <= 2.0 and qty <= 200:  # Likely 20lb bags
            product_type = "20lb_bag"
        else:  # Default to 8lb bags
            product_type = "8lb_bag"

        location_cities = {
            "loc_1": "leesville",
            "loc_2": "lakecharles",
            "loc_3": "lufkin",
            "loc_4": "jasper"
        }
        city_name = location_cities.get(location_id, "lufkin")

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
            "location_id": location_id
        })

    return orders

def calculate_financial_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate financial metrics from Excel data"""
    total_revenue = df['Amount'].sum()
    total_transactions = len(df)

    df['YearMonth'] = df['Date'].dt.to_period('M')
    monthly_revenue = df.groupby('YearMonth')['Amount'].sum().to_dict()

    monthly_revenue = {str(k): float(v) for k, v in monthly_revenue.items()}

    daily_revenue = df.groupby(df['Date'].dt.date)['Amount'].sum().to_dict()
    daily_revenue = {str(k): float(v) for k, v in daily_revenue.items()}

    product_sales = df.groupby('Item')['Amount'].sum().sort_values(ascending=False).head(10).to_dict()

    return {
        "total_revenue": float(total_revenue),
        "total_transactions": int(total_transactions),
        "monthly_revenue": monthly_revenue,
        "daily_revenue": daily_revenue,
        "top_products": product_sales,
        "date_range": {
            "start": df['Date'].min().isoformat(),
            "end": df['Date'].max().isoformat()
        }
    }

def extract_customers_from_customer_list(df: pd.DataFrame, location_id: str = "loc_3", location_name: str = "Lufkin") -> List[Dict[str, Any]]:
    """Extract customers from customer list format (Customer, Address, Main Phone)"""
    customers = []

    location_config = {
        "loc_1": {  # Leesville HQ & Production
            "area_code": "337",
            "state": "Louisiana",
            "zip_base": 71446,
            "city": "Leesville"
        },
        "loc_2": {  # Lake Charles Distribution
            "area_code": "337",
            "state": "Louisiana",
            "zip_base": 70601,
            "city": "Lake Charles"
        },
        "loc_3": {  # Lufkin Distribution
            "area_code": "936",
            "state": "Texas",
            "zip_base": 75901,
            "city": "Lufkin"
        },
        "loc_4": {  # Jasper Warehouse
            "area_code": "903",
            "state": "Texas",
            "zip_base": 75951,
            "city": "Jasper"
        }
    }

    config = location_config.get(location_id, location_config["loc_3"])

    for i, row in df.iterrows():
        if pd.isna(row.get('Customer')) or str(row.get('Customer')).strip() == '':
            continue

        customer_name = str(row['Customer']).strip()
        address = str(row.get('Address', '')).strip() if pd.notna(row.get('Address')) else f"{100 + i} Customer St"
        phone = str(row.get('Main Phone', '')).strip() if pd.notna(row.get('Main Phone')) else f"({config['area_code']}) 555-{1000 + i:04d}"

        if phone and phone != 'nan':
            phone = re.sub(r'[^\d\-\(\)\s\+ext]', '', phone)
            if not phone or phone == '':
                phone = f"({config['area_code']}) 555-{1000 + i:04d}"
        else:
            phone = f"({config['area_code']}) 555-{1000 + i:04d}"

        city = config['city']
        state = config['state']
        zip_code = str(config['zip_base'])

        if address and ', ' in address:
            parts = address.split(', ')
            if len(parts) >= 2:
                street_address = parts[0]
                city_state_zip = parts[-1]
                if ' ' in city_state_zip:
                    city_parts = city_state_zip.split(' ')
                    if len(city_parts) >= 2:
                        city = ' '.join(city_parts[:-2]) if len(city_parts) > 2 else city_parts[0]
                        if len(city_parts) >= 2:
                            state_zip = city_parts[-2:]
                            if len(state_zip) == 2:
                                state = state_zip[0]
                                zip_code = state_zip[1]
                address = street_address

        email_base = re.sub(r'[^a-zA-Z0-9]', '', customer_name.lower())
        email = f"{email_base}@email.com"

        customers.append({
            "name": customer_name,
            "contact_person": "",
            "phone": phone,
            "email": email,
            "address": address,
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "location_id": location_id,
            "credit_limit": 5000.0,
            "payment_terms": 30,
            "is_active": True
        })

    return customers

def process_customer_excel_files(file_paths: List[str], location_id: str = "loc_3", location_name: str = "Lufkin") -> Dict[str, Any]:
    """Process customer list Excel files and return customer data"""
    all_customers = []

    location_sheet_map = {
        "loc_1": ["leesville", "leesville "],  # Note the space variant
        "loc_2": ["lake charles", "lakecharles", "lake_charles"],
        "loc_3": ["lufkin"],
        "loc_4": ["jasper"]
    }

    for file_path in file_paths:
        try:
            logger.info(f"Processing customer Excel file: {file_path}")

            xl_file = pd.ExcelFile(file_path)
            logger.info(f"Available sheets: {xl_file.sheet_names}")

            customers_found = False

            target_sheets = location_sheet_map.get(location_id, [])
            for sheet_name in xl_file.sheet_names:
                if sheet_name.lower().strip() in [s.lower() for s in target_sheets]:
                    try:
                        df = pd.read_excel(file_path, sheet_name=sheet_name)
                        if not df.empty and 'Customer' in df.columns:
                            customers = extract_customers_from_customer_list(df, location_id, location_name)
                            all_customers.extend(customers)
                            customers_found = True
                            logger.info(f"Processed {len(customers)} customers from {sheet_name} sheet")
                            break
                    except Exception as e:
                        logger.warning(f"Failed to process {sheet_name} sheet: {e}")

            if not customers_found and 'all' in xl_file.sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name='all')
                    if not df.empty and 'Customer' in df.columns:
                        customers = extract_customers_from_customer_list(df, location_id, location_name)
                        all_customers.extend(customers)
                        customers_found = True
                        logger.info(f"Processed {len(customers)} customers from 'all' sheet")
                except Exception as e:
                    logger.warning(f"Failed to process 'all' sheet: {e}")

            if not customers_found and 'Sheet1' in xl_file.sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name='Sheet1')
                    if not df.empty and 'Customer' in df.columns:
                        customers = extract_customers_from_customer_list(df, location_id, location_name)
                        all_customers.extend(customers)
                        customers_found = True
                        logger.info(f"Processed {len(customers)} customers from Sheet1")
                except Exception as e:
                    logger.warning(f"Failed to process Sheet1: {e}")

            if not customers_found:
                try:
                    df = pd.read_excel(file_path, sheet_name=0)
                    if not df.empty and 'Customer' in df.columns:
                        customers = extract_customers_from_customer_list(df, location_id, location_name)
                        all_customers.extend(customers)
                        customers_found = True
                        logger.info(f"Processed {len(customers)} customers from first sheet")
                except Exception as e:
                    logger.warning(f"Failed to process first sheet: {e}")

            if not customers_found:
                logger.warning(f"No valid customer data found in {file_path}")

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            continue

    if not all_customers:
        raise ValueError("No valid customer data found in any Excel files. Please ensure files contain:\n1. A 'Customer' column with customer names\n2. Optional 'Address' and 'Main Phone' columns\n3. Data in the correct sheet (try sheets named after your location or 'all')\n4. Check that your Excel files are not corrupted")

    unique_customers = {}
    for customer in all_customers:
        key = customer["name"].lower().strip()
        if key not in unique_customers:
            unique_customers[key] = customer
        else:
            logger.info(f"Skipping duplicate customer: {customer['name']}")

    deduplicated_customers = list(unique_customers.values())

    return {
        "customers": deduplicated_customers,
        "total_records": len(deduplicated_customers),
        "duplicates_removed": len(all_customers) - len(deduplicated_customers)
    }

def process_route_excel_files(files: List[UploadFile], location_id: str) -> dict:
    """Process route Excel files and create route data"""
    import uuid
    from datetime import datetime, date
    
    all_routes = []
    total_records = 0
    
    for file in files:
        try:
            xl_file = pd.ExcelFile(file.file)
            
            for sheet_name in xl_file.sheet_names:
                try:
                    df = pd.read_excel(file.file, sheet_name=sheet_name)
                    
                    if df.empty:
                        continue
                    
                    customer_column = None
                    for col in df.columns:
                        if 'customer' in str(col).lower() or col == df.columns[0]:
                            customer_column = col
                            break
                    
                    if customer_column is None:
                        continue
                    
                    customer_data = df[customer_column].dropna().astype(str).str.strip()
                    valid_customers = customer_data[
                        (customer_data != '') & 
                        (~customer_data.str.upper().isin(['CUSTOMER', 'NAN']))
                    ].tolist()
                    
                    if not valid_customers:
                        continue
                    
                    route_stops = []
                    for i, customer_name in enumerate(valid_customers, 1):
                        stop = {
                            "id": str(uuid.uuid4()),
                            "route_id": "",
                            "customer_id": f"route_customer_{uuid.uuid4().hex[:8]}",
                            "customer_name": customer_name,
                            "order_id": f"route_order_{uuid.uuid4().hex[:8]}",
                            "stop_number": i,
                            "estimated_arrival": "",
                            "status": "pending"
                        }
                        route_stops.append(stop)
                    
                    route_id = str(uuid.uuid4())
                    route = {
                        "id": route_id,
                        "name": f"Route {sheet_name}",
                        "driver_id": None,
                        "vehicle_id": None,
                        "location_id": location_id,
                        "date": str(date.today()),
                        "estimated_duration_hours": len(route_stops) * 0.5,
                        "status": "planned",
                        "created_at": datetime.now().isoformat(),
                        "stops": route_stops
                    }
                    
                    for stop in route_stops:
                        stop["route_id"] = route_id
                    
                    all_routes.append(route)
                    total_records += len(valid_customers)
                    
                except Exception as e:
                    print(f"Error processing sheet {sheet_name}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error processing file {file.filename}: {e}")
            continue
    
    return {
        'routes': all_routes,
        'total_records': total_records,
        'routes_created': len(all_routes)
    }

def process_excel_files(file_paths: List[str], location_id: str = "loc_3", location_name: str = "Lufkin") -> Dict[str, Any]:
    """Process multiple Excel files and return consolidated data"""
    all_data = []

    for file_path in file_paths:
        try:
            logger.info(f"Processing Excel file: {file_path}")
            df_clean = None

            xl_file = pd.ExcelFile(file_path)
            logger.info(f"Available sheets: {xl_file.sheet_names}")
            
            for sheet_name in xl_file.sheet_names:
                try:
                    df_sample = pd.read_excel(file_path, sheet_name=sheet_name, nrows=1)
                    if len(df_sample.columns) > 100:
                        logger.warning(f"Sheet {sheet_name} has {len(df_sample.columns)} columns, limiting to first 10 for memory efficiency")
                        usecols = list(range(min(10, len(df_sample.columns))))
                        df = pd.read_excel(file_path, sheet_name=sheet_name, usecols=usecols)
                    else:
                        df = pd.read_excel(file_path, sheet_name=sheet_name)
                    break
                except Exception as e:
                    logger.warning(f"Failed to read sheet {sheet_name}: {e}")
                    continue
            else:
                logger.error(f"Could not read any sheets from {file_path}")
                continue
            if 'Sheet1' in xl_file.sheet_names:
                try:
                    df_clean = clean_excel_data(df)
                    if not df_clean.empty:
                        logger.info(f"Successfully processed as sales data from Sheet1")
                except Exception as e:
                    logger.warning(f"Failed to process Sheet1 as sales data: {e}")

            if df_clean is None or df_clean.empty:
                try:
                    date_match = re.search(r'JULY\s*(\d{1,2})[+\s]*(\d{4})', file_path)
                    date_str = None
                    if date_match:
                        day, year = date_match.groups()
                        date_str = f"{year}-07-{day.zfill(2)}"

                    df_timesheet = extract_timesheet_sales_data(df, date_str)
                    if not df_timesheet.empty:
                        df_clean = clean_excel_data(df_timesheet)
                        if not df_clean.empty:
                            logger.info(f"Successfully processed as timesheet data")
                except Exception as e:
                    logger.warning(f"Failed to process as timesheet data: {e}")

            if df_clean is None or df_clean.empty:
                for sheet_name in xl_file.sheet_names:
                    if sheet_name.lower() in ['sales', 'daily sales', 'lc-daily sales sheet']:
                        try:
                            df_sample = pd.read_excel(file_path, sheet_name=sheet_name, nrows=1)
                            if len(df_sample.columns) > 100:
                                usecols = list(range(min(10, len(df_sample.columns))))
                                df = pd.read_excel(file_path, sheet_name=sheet_name, usecols=usecols)
                            else:
                                df = pd.read_excel(file_path, sheet_name=sheet_name)
                            df_clean = clean_excel_data(df)
                            if not df_clean.empty:
                                logger.info(f"Successfully processed sales data from {sheet_name}")
                                break
                        except Exception as e:
                            logger.warning(f"Failed to process {sheet_name}: {e}")
                            continue

            if df_clean is not None and not df_clean.empty:
                all_data.append(df_clean)
                logger.info(f"Processed {len(df_clean)} records from {file_path}")
            else:
                logger.warning(f"No valid data found in {file_path}")

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            continue

    if not all_data:
        raise ValueError("No valid sales data found in any Excel files. Please ensure files contain either:\n1. Standard sales data with columns: Type, Date, Name, Amount, Item, Qty, Sales Price, Num\n2. Timesheet format with customer names in first column and quantities in columns 3 and 4\n3. Check that your Excel files are not corrupted and contain actual data rows")

    combined_df = pd.concat(all_data, ignore_index=True)

    if combined_df.empty:
        raise ValueError("Combined data is empty after processing all Excel files")

    customers = extract_customers_from_excel(combined_df, location_id, location_name)
    orders = extract_orders_from_excel(combined_df, location_id, location_name)
    financial_metrics = calculate_financial_metrics(combined_df)

    return {
        "customers": customers,
        "orders": orders,
        "financial_metrics": financial_metrics,
        "total_records": len(combined_df),
        "date_range": financial_metrics["date_range"]
    }
