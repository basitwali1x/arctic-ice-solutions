import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def clean_excel_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize Excel data"""
    transaction_cols = ['Type', 'Date', 'Name', 'Amount']
    customer_cols = ['Customer', 'Address', 'Main Phone']
    
    if all(col in df.columns for col in transaction_cols):
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
    elif all(col in df.columns for col in customer_cols):
        df_clean = df.dropna(subset=['Customer'], how='any')
        df_clean['Customer'] = df_clean['Customer'].astype(str).str.strip()
        df_clean['Address'] = df_clean['Address'].astype(str).str.strip()
        df_clean['Main Phone'] = df_clean['Main Phone'].astype(str).str.strip()
        return df_clean
    else:
        return pd.DataFrame()

def extract_customers_from_excel(df: pd.DataFrame, location_id: str = "loc_1", location_name: str = "Leesville HQ & Production") -> List[Dict[str, Any]]:
    """Extract unique customers from Excel data"""
    customers = []
    
    location_mapping = {
        "loc_1": {"area_code": "337", "state": "Louisiana", "zip_base": 71446},
        "loc_2": {"area_code": "337", "state": "Louisiana", "zip_base": 70601},
        "loc_3": {"area_code": "936", "state": "Texas", "zip_base": 75901},
        "loc_4": {"area_code": "903", "state": "Texas", "zip_base": 75951}
    }
    
    location_info = location_mapping.get(location_id, location_mapping["loc_1"])
    area_code = location_info["area_code"]
    state = location_info["state"]
    zip_base = location_info["zip_base"]
    
    if 'Customer' in df.columns:
        for i, row in df.iterrows():
            if pd.isna(row['Customer']) or row['Customer'] == 'nan':
                continue
                
            customer_name = str(row['Customer']).strip()
            customer_address = str(row.get('Address', '')).strip()
            customer_phone = str(row.get('Main Phone', '')).strip()
            
            if not customer_phone or customer_phone == 'nan':
                customer_phone = f"({area_code}) 555-{1000 + i:04d}"
            
            customers.append({
                "id": f"{location_id}_customer_{i+1}",
                "name": customer_name,
                "email": f"{customer_name.lower().replace(' ', '').replace('#', '').replace('-', '').replace('.', '').replace(',', '').replace('&', '')}@email.com",
                "phone": customer_phone,
                "address": customer_address if customer_address and customer_address != 'nan' else f"{100 + i} Customer St, {location_name.split(' ')[0]}, {state[:2]} {zip_base}",
                "location_id": location_id,
                "credit_limit": 5000.0,
                "current_balance": 0.0,
                "total_orders": 0,
                "total_spent": 0.0,
                "last_order_date": None,
                "status": "active"
            })
    else:
        unique_customers = df['Name'].unique()
        
        for i, customer_name in enumerate(unique_customers):
            if pd.isna(customer_name) or customer_name == 'nan':
                continue
                
            customer_data = df[df['Name'] == customer_name]
            total_orders = len(customer_data)
            total_spent = customer_data['Amount'].sum()
            last_order = customer_data['Date'].max()
            
            customers.append({
                "id": f"{location_id}_customer_{i+1}",
                "name": customer_name,
                "email": f"{customer_name.lower().replace(' ', '').replace('#', '').replace('-', '').replace('.', '').replace(',', '')}@email.com",
                "phone": f"({area_code}) 555-{1000 + i:04d}",
                "address": f"{100 + i} Customer St, {location_name.split(' ')[0]}, {state[:2]} {zip_base}",
                "location_id": location_id,
                "credit_limit": 5000.0,
                "current_balance": 0.0,
                "total_orders": int(total_orders),
                "total_spent": float(total_spent),
                "last_order_date": last_order.isoformat() if pd.notna(last_order) else None,
                "status": "active"
            })
    
    return customers

def extract_orders_from_excel(df: pd.DataFrame, location_id: str = "loc_1", location_name: str = "Leesville HQ & Production") -> List[Dict[str, Any]]:
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
            
        orders.append({
            "id": f"{location_name.lower()}_order_{i+1}",
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

def process_excel_files(file_paths: List[str], location_id: str = "loc_1", location_name: str = "Leesville HQ & Production") -> Dict[str, Any]:
    """Process multiple Excel files and return consolidated data"""
    all_data = []
    
    for file_path in file_paths:
        try:
            logger.info(f"Processing Excel file: {file_path}")
            if file_path.endswith('.xlsm'):
                df = pd.read_excel(file_path, engine='openpyxl')
            else:
                df = pd.read_excel(file_path)
            df_clean = clean_excel_data(df)
            if not df_clean.empty:
                all_data.append(df_clean)
                logger.info(f"Processed {len(df_clean)} records from {file_path}")
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            continue
    
    if not all_data:
        raise ValueError("No valid data found in Excel files")
    
    combined_df = pd.concat(all_data, ignore_index=True)
    
    customers = extract_customers_from_excel(combined_df, location_id, location_name)
    
    orders = []
    financial_metrics = {}
    
    if 'Name' in combined_df.columns and 'Amount' in combined_df.columns:
        orders = extract_orders_from_excel(combined_df, location_id, location_name)
        financial_metrics = calculate_financial_metrics(combined_df)
    else:
        financial_metrics = {
            "total_revenue": 0.0,
            "total_transactions": 0,
            "monthly_revenue": {},
            "daily_revenue": {},
            "top_products": {},
            "date_range": {
                "start": datetime.now().isoformat(),
                "end": datetime.now().isoformat()
            }
        }
    
    return {
        "customers": customers,
        "orders": orders,
        "financial_metrics": financial_metrics,
        "total_records": len(combined_df),
        "date_range": financial_metrics["date_range"]
    }
