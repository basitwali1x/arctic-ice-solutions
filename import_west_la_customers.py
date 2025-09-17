import pandas as pd
import json
import re
from datetime import datetime

def process_west_la_customer_excel():
    """Process the West LA customer Excel file and create structured customer data"""
    
    excel_file = '/home/ubuntu/attachments/ec5be3b2-f83c-4bb9-ab74-a85e5b3df301/West+La+Ice+Customer+List+new.xlsx'
    
    try:
        df = pd.read_excel(excel_file)
        print(f"Excel file loaded with {len(df)} rows")
        print(f"Columns: {list(df.columns)}")
        
        customers = []
        
        for index, row in df.iterrows():
            customer_name = str(row.get('Customer', '')).strip()
            address = str(row.get('Address', '')).strip()
            phone = str(row.get('Main Phone', '')).strip()
            
            if not customer_name or customer_name.lower() in ['nan', 'none', '']:
                continue
            
            phone_clean = re.sub(r'[^\d]', '', phone) if phone != 'nan' else ''
            if len(phone_clean) == 10:
                phone_formatted = f"({phone_clean[:3]}) {phone_clean[3:6]}-{phone_clean[6:]}"
            else:
                phone_formatted = phone if phone != 'nan' else ''
            
            email_safe_name = re.sub(r'[^a-zA-Z0-9]', '', customer_name.lower())
            email = f"{email_safe_name}@email.com" if email_safe_name else f"customer{index+1}@email.com"
            
            address_parts = address.split(',') if address != 'nan' else []
            street_address = address_parts[0].strip() if len(address_parts) > 0 else ''
            city_state_zip = address_parts[1].strip() if len(address_parts) > 1 else ''
            
            city = "Lake Charles"
            state = "Louisiana"
            zip_code = "70601"
            
            if city_state_zip:
                zip_match = re.search(r'\b\d{5}(-\d{4})?\b', city_state_zip)
                if zip_match:
                    zip_code = zip_match.group(0)
                
                city_state_part = re.sub(r'\b\d{5}(-\d{4})?\b', '', city_state_zip).strip()
                if city_state_part:
                    parts = city_state_part.split()
                    if len(parts) >= 2:
                        state = parts[-1]
                        city = ' '.join(parts[:-1])
            
            customer = {
                "id": f"west_la_excel_customer_{index + 1}",
                "name": customer_name,
                "contact_person": "",
                "phone": phone_formatted,
                "email": email,
                "address": street_address,
                "city": city,
                "state": state,
                "zip_code": zip_code,
                "location_id": "loc_2",
                "credit_limit": 5000.0,
                "payment_terms": 30,
                "is_active": True,
                "coordinates": None
            }
            
            customers.append(customer)
        
        print(f"Successfully processed {len(customers)} customers from Excel file")
        
        summary = {
            "source": "West LA Ice Customer List Excel",
            "processed_date": datetime.now().isoformat(),
            "total_customers": len(customers),
            "location_id": "loc_2",
            "location_name": "Lake Charles"
        }
        
        output_data = {
            "customers": customers,
            "summary": summary
        }
        
        output_file = '/home/ubuntu/repos/arctic-ice-solutions/west_la_customers_from_excel.json'
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        print(f"Customer data saved to: {output_file}")
        
        if customers:
            print("\nSample customer records:")
            for i, customer in enumerate(customers[:3]):
                print(f"  {i+1}. {customer['name']} - {customer['phone']} - {customer['address']}")
            if len(customers) > 3:
                print(f"  ... and {len(customers)-3} more customers")
        
        return output_data
        
    except Exception as e:
        print(f'Error processing Excel file: {e}')
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = process_west_la_customer_excel()
