import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def detect_data_format(df: pd.DataFrame) -> str:
    """Detect if data is customer-only format or sales transaction format"""
    customer_cols_strict = ['Customer', 'Address', 'Main Phone']
    customer_cols_flexible = ['Customer', 'Address', 'Phone']
    sales_cols = ['Type', 'Date', 'Name', 'Amount']
    
    customer_match_strict = all(col in df.columns for col in customer_cols_strict)
    customer_match_flexible = all(col in df.columns for col in customer_cols_flexible)
    sales_match = all(col in df.columns for col in sales_cols)
    
    if customer_match_strict or customer_match_flexible:
        return "customer_only"
    elif sales_match:
        return "sales_transaction"
    else:
        return "unknown"

def extract_customers_from_customer_data(df: pd.DataFrame, location_id: str = "loc_3", location_name: str = "Lufkin") -> List[Dict[str, Any]]:
    """Extract customers from customer-only data format (Customer/Address/Phone)"""
    customers = []
    
    location_config = {
        "loc_1": {"area_code": "337", "state": "Louisiana", "zip_base": 71446, "city": "Leesville"},
        "loc_2": {"area_code": "337", "state": "Louisiana", "zip_base": 70601, "city": "Lake Charles"},
        "loc_3": {"area_code": "936", "state": "Texas", "zip_base": 75901, "city": "Lufkin"},
        "loc_4": {"area_code": "903", "state": "Texas", "zip_base": 75951, "city": "Jasper"}
    }
    
    area_code_to_location = {
        "337": "loc_1",
        "936": "loc_3",
        "903": "loc_4",
        "409": "loc_3"
    }
    
    phone_col = 'Main Phone' if 'Main Phone' in df.columns else 'Phone'
    
    for i, row in df.iterrows():
        if pd.isna(row['Customer']) or row['Customer'] == 'nan':
            continue
            
        phone = str(row[phone_col]).replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
        area_code = phone[:3] if len(phone) >= 10 else '936'
        detected_location_id = area_code_to_location.get(area_code, location_id)
        
        config = location_config.get(detected_location_id, location_config["loc_3"])
        city = config["city"]
        
        customer_name_clean = str(row['Customer']).lower().replace(' ', '').replace('#', '').replace('-', '').replace('.', '').replace(',', '')
        
        customers.append({
            "id": f"{city.lower()}_customer_{i+1}",
            "name": row['Customer'],
            "email": f"{customer_name_clean}@email.com",
            "phone": row[phone_col],
            "address": row['Address'],
            "location_id": detected_location_id,
            "credit_limit": 5000.0,
            "current_balance": 0.0,
            "total_orders": 0,
            "total_spent": 0.0,
            "last_order_date": None,
            "status": "active"
        })
    
    return customers

def clean_excel_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize Excel data"""
    required_cols = ['Type', 'Date', 'Name', 'Amount']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
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

def process_excel_files(file_paths: List[str], location_id: str = "loc_3", location_name: str = "Lufkin") -> Dict[str, Any]:
    """Process multiple Excel files and return consolidated data"""
    all_customers = []
    all_orders = []
    all_data = []
    
    for file_path in file_paths:
        try:
            logger.info(f"Processing Excel file: {file_path}")
            
            if file_path.endswith('.xlsm'):
                df = pd.read_excel(file_path, engine='openpyxl', sheet_name=None)
            else:
                df = pd.read_excel(file_path, sheet_name=None)
            
            first_sheet_name = list(df.keys())[0]
            df = df[first_sheet_name]
            
            data_format = detect_data_format(df)
            logger.info(f"Detected data format: {data_format}")
            
            if data_format == "customer_only":
                customers = extract_customers_from_customer_data(df, location_id, location_name)
                all_customers.extend(customers)
                logger.info(f"Processed {len(customers)} customers from {file_path}")
                
            elif data_format == "sales_transaction":
                df_clean = clean_excel_data(df)
                if not df_clean.empty:
                    all_data.append(df_clean)
                    customers = extract_customers_from_excel(df_clean, location_id, location_name)
                    orders = extract_orders_from_excel(df_clean, location_id, location_name)
                    all_customers.extend(customers)
                    all_orders.extend(orders)
                    logger.info(f"Processed {len(df_clean)} records from {file_path}")
            else:
                logger.warning(f"Unsupported data format in {file_path}")
                continue
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            continue
    
    if not all_customers:
        raise ValueError("No valid data found in Excel files")
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        financial_metrics = calculate_financial_metrics(combined_df)
    else:
        financial_metrics = {
            "total_revenue": 0.0,
            "total_transactions": 0,
            "monthly_revenue": {},
            "daily_revenue": {},
            "top_products": {},
            "date_range": {"start": None, "end": None}
        }
    
    return {
        "customers": all_customers,
        "orders": all_orders,
        "financial_metrics": financial_metrics,
        "total_records": len(all_customers),
        "date_range": financial_metrics["date_range"],
        "data_format": "mixed" if all_data and all_customers else ("customer_only" if all_customers else "sales_transaction")
    }
