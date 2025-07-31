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
            raise ValueError("GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON environment variable not set")
        
        service_account_info = json.loads(service_account_json)
        gc = gspread.service_account_from_dict(service_account_info)
        return gc
    except Exception as e:
        logger.error(f"Failed to authenticate with Google Sheets: {e}")
        raise

def get_google_sheets_data(sheets_url: str, worksheet_name: str = None) -> pd.DataFrame:
    """Read data from Google Sheets and convert to pandas DataFrame"""
    try:
        gc = authenticate_google_sheets()
        
        if "/spreadsheets/d/" in sheets_url:
            sheet_id = sheets_url.split("/spreadsheets/d/")[1].split("/")[0]
        else:
            raise ValueError("Invalid Google Sheets URL format")
        
        spreadsheet = gc.open_by_key(sheet_id)
        
        if worksheet_name:
            worksheet = spreadsheet.worksheet(worksheet_name)
        else:
            worksheet = spreadsheet.sheet1
        
        data = worksheet.get_all_records()
        
        if not data:
            raise ValueError("No data found in Google Sheets")
        
        df = pd.DataFrame(data)
        
        required_cols = ['Type', 'Date', 'Name', 'Amount']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        logger.info(f"Successfully read {len(df)} rows from Google Sheets")
        return df
        
    except GoogleAuthError as e:
        logger.error(f"Google Sheets authentication error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error reading Google Sheets data: {e}")
        raise

def process_google_sheets_data(sheets_url: str, location_id: str = "loc_3", location_name: str = "Lufkin", worksheet_name: str = None) -> Dict[str, Any]:
    """Process Google Sheets data and return consolidated customer/order data"""
    try:
        df = get_google_sheets_data(sheets_url, worksheet_name)
        
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
            "date_range": financial_metrics["date_range"]
        }
        
    except Exception as e:
        logger.error(f"Error processing Google Sheets data: {e}")
        raise

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
