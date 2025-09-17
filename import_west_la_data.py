import sys
import os
import json
import re
from datetime import datetime
from decimal import Decimal

def parse_west_la_pdf_data():
    """Parse the West LA order history PDF data and structure it"""
    
    pdf_file_path = '/home/ubuntu/full_outputs/pdftotext_attachment_1758128412.9712448.txt'
    
    with open(pdf_file_path, 'r') as f:
        content = f.read()
    
    customers = []
    orders = []
    
    lines = content.split('\n')
    current_customer = None
    current_customer_data = {}
    order_counter = 1
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line or line in ['10:33 AM', 'West Louisiana Ice Service Inc.', '08/13/25', 'Sales by Customer Detail', 'Accrual Basis', 'July 2025', 'Type', 'Date', 'Num', 'Item', 'Qty', 'Sales Price', 'Amount']:
            i += 1
            continue
            
        if (line and not line.startswith(('Sales Receipt', 'Invoice', 'Total', 'Page', '07/', '54', '25', '52', '50', '45')) 
            and not re.match(r'^\d+\.\d+$', line) 
            and not re.match(r'^\d+$', line)
            and len(line) > 3
            and not line.startswith('0.00')):
            
            if current_customer and current_customer_data:
                customers.append(current_customer_data)
            
            current_customer = line
            customer_id = f"west_la_customer_{len(customers) + 1}"
            current_customer_data = {
                "id": customer_id,
                "name": current_customer,
                "contact_person": "",
                "phone": "",
                "email": f"{current_customer.lower().replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('#', '').replace('&', 'and')}@email.com",
                "address": "",
                "city": "Lake Charles",
                "state": "Louisiana", 
                "zip_code": "70601",
                "location_id": "loc_2",
                "credit_limit": 5000.0,
                "payment_terms": 30,
                "is_active": True,
                "coordinates": None
            }
            
        elif line.startswith(('Sales Receipt', 'Invoice')) and current_customer:
            transaction_type = line
            date_line = ""
            num_line = ""
            item_line = ""
            qty_line = ""
            price_line = ""
            amount_line = ""
            
            for j in range(1, 15):
                if i + j < len(lines):
                    next_line = lines[i + j].strip()
                    
                    if next_line.startswith(('Sales Receipt', 'Invoice', 'Total')):
                        break
                    
                    if re.match(r'07/\d{2}/2025', next_line) and not date_line:
                        date_line = next_line
                    elif re.match(r'^\d{5}$', next_line) and not num_line:
                        num_line = next_line
                    elif ('Cube' in next_line or 'No Sale' in next_line or 'Void' in next_line or 'No Charg' in next_line) and not item_line:
                        item_line = next_line
                    elif re.match(r'^\d+\.?\d*$', next_line):
                        value = float(next_line)
                        if not qty_line and value > 0:
                            qty_line = next_line
                        elif qty_line and not price_line and value > 0:
                            price_line = next_line
                        elif qty_line and price_line and not amount_line and value > 0:
                            amount_line = next_line
                            break  # We have all needed data
            
            if qty_line and price_line and not amount_line:
                try:
                    calculated_amount = float(qty_line) * float(price_line)
                    amount_line = str(calculated_amount)
                except (ValueError, TypeError):
                    pass
            
            if date_line and current_customer_data and qty_line and price_line:
                try:
                    order_date = datetime.strptime(date_line, '%m/%d/%Y').strftime('%Y-%m-%d')
                    quantity = float(qty_line)
                    unit_price = float(price_line)
                    total_amount = float(amount_line) if amount_line else quantity * unit_price
                    
                    order = {
                        "id": f"west_la_order_{order_counter}",
                        "customer_id": current_customer_data["id"],
                        "customer_name": current_customer,
                        "order_date": order_date,
                        "transaction_type": transaction_type,
                        "transaction_number": num_line,
                        "product": item_line if item_line else "8# Cube",
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "total_amount": total_amount,
                        "location_id": "loc_2",
                        "location_name": "Lake Charles",
                        "status": "completed"
                    }
                    orders.append(order)
                    order_counter += 1
                except (ValueError, TypeError):
                    pass
        
        i += 1
    
    if current_customer and current_customer_data:
        customers.append(current_customer_data)
    
    unique_customers = {}
    for customer in customers:
        key = customer["name"].lower().strip()
        if key not in unique_customers and customer["name"]:
            unique_customers[key] = customer
    
    final_customers = list(unique_customers.values())
    
    total_revenue = sum(order["total_amount"] for order in orders)
    location_summary = {
        "loc_2": {
            "customers": len(final_customers),
            "orders": len(orders),
            "revenue": total_revenue
        }
    }
    
    print(f"Processed West LA data:")
    print(f"  Customers: {len(final_customers)}")
    print(f"  Orders: {len(orders)}")
    print(f"  Total Revenue: ${total_revenue:,.2f}")
    
    return {
        "customers": final_customers,
        "orders": orders,
        "summary": location_summary
    }

def save_west_la_data():
    """Process and save West LA order history data"""
    
    data = parse_west_la_pdf_data()
    
    output_file = '/home/ubuntu/repos/arctic-ice-solutions/west_la_order_history.json'
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"\nWest LA order history saved to: {output_file}")
    return data

if __name__ == "__main__":
    result = save_west_la_data()
