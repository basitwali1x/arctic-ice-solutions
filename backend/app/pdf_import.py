import logging
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import pdfplumber
import pypdf
from pathlib import Path

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using pdfplumber as primary, pypdf as fallback"""
    text = ""
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if text.strip():
            logger.info(f"Successfully extracted text using pdfplumber from {file_path}")
            return text
            
    except Exception as e:
        logger.warning(f"pdfplumber failed for {file_path}: {e}")
    
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if text.strip():
            logger.info(f"Successfully extracted text using pypdf from {file_path}")
            return text
            
    except Exception as e:
        logger.error(f"Both PDF extraction methods failed for {file_path}: {e}")
    
    return text

def parse_invoice_pdf(text: str, location_id: str = "loc_1", location_name: str = "Leesville") -> Dict[str, Any]:
    """Parse invoice data from PDF text"""
    customers = []
    orders = []
    
    invoice_match = re.search(r'invoice\s*#?\s*(\w+)', text, re.IGNORECASE)
    invoice_number = invoice_match.group(1) if invoice_match else "PDF_INV_001"
    
    date_patterns = [
        r'date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{4}-\d{2}-\d{2})'
    ]
    
    invoice_date = None
    for pattern in date_patterns:
        date_match = re.search(pattern, text, re.IGNORECASE)
        if date_match:
            try:
                date_str = date_match.group(1)
                for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%m/%d/%y', '%m-%d-%y']:
                    try:
                        invoice_date = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                if invoice_date:
                    break
            except Exception:
                continue
    
    if not invoice_date:
        invoice_date = datetime.now()
    
    customer_patterns = [
        r'bill\s+to[:\s]+([^\n]+)',
        r'customer[:\s]+([^\n]+)',
        r'sold\s+to[:\s]+([^\n]+)'
    ]
    
    customer_name = "PDF Customer"
    for pattern in customer_patterns:
        customer_match = re.search(pattern, text, re.IGNORECASE)
        if customer_match:
            customer_name = customer_match.group(1).strip()
            break
    
    amount_patterns = [
        r'total[:\s]+\$?(\d+\.?\d*)',
        r'amount[:\s]+\$?(\d+\.?\d*)',
        r'\$(\d+\.?\d*)'
    ]
    
    total_amount = 0.0
    for pattern in amount_patterns:
        amount_matches = re.findall(pattern, text, re.IGNORECASE)
        if amount_matches:
            try:
                amounts = [float(amt) for amt in amount_matches]
                total_amount = max(amounts)
                break
            except ValueError:
                continue
    
    customer_id = f"pdf_cust_{hash(customer_name) % 10000}"
    customer = {
        "id": customer_id,
        "name": customer_name,
        "location_id": location_id,
        "location_name": location_name,
        "address": "",
        "phone": "",
        "email": "",
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
    customers.append(customer)
    
    order = {
        "id": f"pdf_order_{invoice_number}",
        "customer_id": customer_id,
        "customer_name": customer_name,
        "location_id": location_id,
        "date": invoice_date.isoformat(),
        "items": [
            {
                "product_id": "ice_8lb",
                "product_name": "8lb Ice Bag",
                "quantity": 1,
                "price": total_amount,
                "total": total_amount
            }
        ],
        "total_amount": total_amount,
        "status": "completed",
        "payment_method": "unknown",
        "invoice_number": invoice_number
    }
    orders.append(order)
    
    return {
        "customers": customers,
        "orders": orders,
        "total_amount": total_amount,
        "invoice_date": invoice_date.isoformat()
    }

def parse_receipt_pdf(text: str, location_id: str = "loc_1", location_name: str = "Leesville") -> Dict[str, Any]:
    """Parse receipt data from PDF text"""
    return parse_invoice_pdf(text, location_id, location_name)

def parse_expense_pdf(text: str, location_id: str = "loc_1", location_name: str = "Leesville") -> Dict[str, Any]:
    """Parse expense data from PDF text"""
    expenses = []
    
    date_patterns = [
        r'date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{4}-\d{2}-\d{2})'
    ]
    
    expense_date = None
    for pattern in date_patterns:
        date_match = re.search(pattern, text, re.IGNORECASE)
        if date_match:
            try:
                date_str = date_match.group(1)
                for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%m/%d/%y', '%m-%d-%y']:
                    try:
                        expense_date = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                if expense_date:
                    break
            except Exception:
                continue
    
    if not expense_date:
        expense_date = datetime.now()
    
    vendor_patterns = [
        r'vendor[:\s]+([^\n]+)',
        r'payee[:\s]+([^\n]+)',
        r'merchant[:\s]+([^\n]+)'
    ]
    
    vendor = "PDF Vendor"
    for pattern in vendor_patterns:
        vendor_match = re.search(pattern, text, re.IGNORECASE)
        if vendor_match:
            vendor = vendor_match.group(1).strip()
            break
    
    amount_patterns = [
        r'total[:\s]+\$?(\d+\.?\d*)',
        r'amount[:\s]+\$?(\d+\.?\d*)',
        r'\$(\d+\.?\d*)'
    ]
    
    amount = 0.0
    for pattern in amount_patterns:
        amount_matches = re.findall(pattern, text, re.IGNORECASE)
        if amount_matches:
            try:
                amounts = [float(amt) for amt in amount_matches]
                amount = max(amounts)
                break
            except ValueError:
                continue
    
    category = "other"
    if any(word in text.lower() for word in ['fuel', 'gas', 'gasoline']):
        category = "fuel"
    elif any(word in text.lower() for word in ['maintenance', 'repair', 'service']):
        category = "maintenance"
    elif any(word in text.lower() for word in ['office', 'supplies', 'equipment']):
        category = "office_supplies"
    
    expense = {
        "id": f"pdf_exp_{hash(text[:100]) % 10000}",
        "date": expense_date.date().isoformat(),
        "category": category,
        "description": f"PDF Expense - {vendor}",
        "amount": amount,
        "location_id": location_id,
        "vendor": vendor,
        "receipt_number": "",
        "created_at": datetime.now().isoformat()
    }
    expenses.append(expense)
    
    return {
        "expenses": expenses,
        "total_amount": amount,
        "expense_date": expense_date.isoformat()
    }

def process_pdf_files(file_paths: List[str], location_id: str = "loc_1", location_name: str = "Leesville") -> Dict[str, Any]:
    """Process multiple PDF files and return consolidated data"""
    all_customers = []
    all_orders = []
    all_expenses = []
    total_revenue = 0.0
    
    for file_path in file_paths:
        try:
            logger.info(f"Processing PDF file: {file_path}")
            
            text = extract_text_from_pdf(file_path)
            
            if not text.strip():
                logger.warning(f"No text extracted from {file_path} - likely a scanned image-based PDF requiring OCR")
                continue
            
            text_lower = text.lower()
            
            if any(word in text_lower for word in ['invoice', 'bill to', 'invoice number']):
                result = parse_invoice_pdf(text, location_id, location_name)
                all_customers.extend(result["customers"])
                all_orders.extend(result["orders"])
                total_revenue += result["total_amount"]
                logger.info(f"Processed {file_path} as invoice")
                
            elif any(word in text_lower for word in ['receipt', 'thank you', 'purchase']):
                result = parse_receipt_pdf(text, location_id, location_name)
                all_customers.extend(result["customers"])
                all_orders.extend(result["orders"])
                total_revenue += result["total_amount"]
                logger.info(f"Processed {file_path} as receipt")
                
            elif any(word in text_lower for word in ['expense', 'reimbursement', 'vendor', 'payee']):
                result = parse_expense_pdf(text, location_id, location_name)
                all_expenses.extend(result["expenses"])
                logger.info(f"Processed {file_path} as expense")
                
            else:
                result = parse_invoice_pdf(text, location_id, location_name)
                all_customers.extend(result["customers"])
                all_orders.extend(result["orders"])
                total_revenue += result["total_amount"]
                logger.info(f"Processed {file_path} as default invoice")
                
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            continue
    
    financial_metrics = {
        "total_revenue": total_revenue,
        "total_expenses": sum(exp["amount"] for exp in all_expenses),
        "net_profit": total_revenue - sum(exp["amount"] for exp in all_expenses),
        "date_range": {
            "start": datetime.now().date().isoformat(),
            "end": datetime.now().date().isoformat()
        }
    }
    
    return {
        "customers": all_customers,
        "orders": all_orders,
        "expenses": all_expenses,
        "financial_metrics": financial_metrics,
        "total_records": len(all_customers) + len(all_orders) + len(all_expenses),
        "date_range": financial_metrics["date_range"]
    }
