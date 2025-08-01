import gspread
import pandas as pd
from google.auth.exceptions import GoogleAuthError
from typing import List, Dict, Any
import logging
import json
import os
from .excel_import import extract_customers_from_excel, extract_orders_from_excel, calculate_financial_metrics

logger = logging.getLogger(__name__)

def authenticate_google_sheets():
    """Authenticate with Google Sheets API using service account"""
    try:
        service_account_json = os.getenv("GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON")
        if not service_account_json:
            raise ValueError("GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON environment variable not set. Please configure your Google Sheets service account credentials in the .env file.")
        
        if service_account_json.strip() == "":
            raise ValueError("GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON is empty. Please add your Google Sheets service account JSON credentials.")
        
        try:
            service_account_info = json.loads(service_account_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON: {e}")
        
        required_fields = ["type", "project_id", "private_key", "client_email"]
        missing_fields = [field for field in required_fields if field not in service_account_info]
        if missing_fields:
            raise ValueError(f"Missing required fields in service account JSON: {missing_fields}")
        
        gc = gspread.service_account_from_dict(service_account_info)
        return gc
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Failed to authenticate with Google Sheets: {e}")
        raise ValueError(f"Google Sheets authentication failed: {str(e)}")

def get_google_sheets_data(sheets_url: str, worksheet_name: str = None) -> pd.DataFrame:
    """Read data from Google Sheets and convert to pandas DataFrame"""
    try:
        gc = authenticate_google_sheets()
        
        if not sheets_url or not sheets_url.strip():
            raise ValueError("Google Sheets URL cannot be empty")
        
        if "/spreadsheets/d/" not in sheets_url:
            raise ValueError("Invalid Google Sheets URL format. Expected format: https://docs.google.com/spreadsheets/d/SHEET_ID/...")
        
        try:
            sheet_id = sheets_url.split("/spreadsheets/d/")[1].split("/")[0]
            if not sheet_id:
                raise ValueError("Could not extract sheet ID from URL")
        except IndexError:
            raise ValueError("Invalid Google Sheets URL format. Could not extract sheet ID.")
        
        try:
            spreadsheet = gc.open_by_key(sheet_id)
        except gspread.SpreadsheetNotFound:
            raise ValueError("Spreadsheet not found. Please check the URL and ensure the service account has access to the sheet.")
        except gspread.APIError as e:
            raise ValueError(f"Google Sheets API error: {str(e)}")
        
        try:
            if worksheet_name:
                worksheet = spreadsheet.worksheet(worksheet_name)
            else:
                worksheet = spreadsheet.sheet1
        except gspread.WorksheetNotFound:
            available_sheets = [ws.title for ws in spreadsheet.worksheets()]
            raise ValueError(f"Worksheet '{worksheet_name}' not found. Available worksheets: {available_sheets}")
        
        try:
            data = worksheet.get_all_records()
        except Exception as e:
            raise ValueError(f"Failed to read data from worksheet: {str(e)}")
        
        if not data:
            raise ValueError("No data found in Google Sheets. Please ensure the sheet contains data with headers in the first row.")
        
        df = pd.DataFrame(data)
        
        if df.empty:
            raise ValueError("Google Sheets data is empty after processing")
        
        data_format = detect_data_format(df)
        if data_format == "unknown":
            available_columns = list(df.columns)
            raise ValueError(f"Unsupported data format. Expected either Customer/Address/Phone columns or Type/Date/Name/Amount columns. Found columns: {available_columns}")
        
        logger.info(f"Successfully read {len(df)} rows from Google Sheets with format: {data_format}")
        return df
        
    except GoogleAuthError as e:
        logger.error(f"Google Sheets authentication error: {e}")
        raise ValueError(f"Google Sheets authentication failed: {str(e)}")
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Error reading Google Sheets data: {e}")
        raise ValueError(f"Failed to read Google Sheets data: {str(e)}")

def process_google_sheets_data(sheets_url: str, location_id: str = "loc_3", location_name: str = "Lufkin", worksheet_name: str = None) -> Dict[str, Any]:
    """Process Google Sheets data and return consolidated customer/order data"""
    try:
        df = get_google_sheets_data(sheets_url, worksheet_name)
        data_format = detect_data_format(df)
        
        if data_format == "customer_only":
            customers = extract_customers_from_customer_data(df, location_id, location_name)
            orders = []
            financial_metrics = {
                "total_revenue": 0.0,
                "total_transactions": 0,
                "monthly_revenue": {},
                "daily_revenue": {},
                "top_products": {},
                "date_range": {"start": None, "end": None}
            }
            
        elif data_format == "sales_transaction":
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.dropna(subset=['Date'])
            df = df[df['Type'].isin(['Invoice', 'Sales Receipt'])]
            df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(0)
            df['Sales Price'] = pd.to_numeric(df['Sales Price'], errors='coerce').fillna(0)
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            df['Name'] = df['Name'].astype(str).str.strip()
            df['Item'] = df['Item'].astype(str).str.strip()
            df['Num'] = df['Num'].astype(str).str.strip()
            df = df[df['Amount'] > 0]
            
            customers = extract_customers_from_excel(df, location_id, location_name)
            orders = extract_orders_from_excel(df, location_id, location_name)
            financial_metrics = calculate_financial_metrics(df)
        
        return {
            "customers": customers,
            "orders": orders,
            "financial_metrics": financial_metrics,
            "total_records": len(df),
            "date_range": financial_metrics["date_range"],
            "data_format": data_format
        }
        
    except Exception as e:
        logger.error(f"Error processing Google Sheets data: {e}")
        raise

def detect_data_format(df: pd.DataFrame) -> str:
    """Detect if data is customer-only format or sales transaction format"""
    customer_cols = ['Customer', 'Address', 'Main Phone']
    sales_cols = ['Type', 'Date', 'Name', 'Amount']
    
    customer_match = all(col in df.columns for col in customer_cols)
    sales_match = all(col in df.columns for col in sales_cols)
    
    if customer_match:
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
    
    for i, row in df.iterrows():
        if pd.isna(row['Customer']) or row['Customer'] == 'nan':
            continue
            
        phone = str(row['Main Phone']).replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
        area_code = phone[:3] if len(phone) >= 10 else '936'
        detected_location_id = area_code_to_location.get(area_code, location_id)
        
        config = location_config.get(detected_location_id, location_config["loc_3"])
        city = config["city"]
        
        customer_name_clean = str(row['Customer']).lower().replace(' ', '').replace('#', '').replace('-', '').replace('.', '').replace(',', '')
        
        customers.append({
            "id": f"{city.lower()}_customer_{i+1}",
            "name": row['Customer'],
            "email": f"{customer_name_clean}@email.com",
            "phone": row['Main Phone'],
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

def test_google_sheets_connection() -> Dict[str, Any]:
    """Test Google Sheets API connection"""
    try:
        gc = authenticate_google_sheets()
        return {
            "connected": True,
            "message": "Successfully connected to Google Sheets API"
        }
    except Exception as e:
        return {
            "connected": False,
            "message": f"Failed to connect: {str(e)}"
        }
