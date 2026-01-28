#!/usr/bin/env python3
"""
Import Lake Charles route data for Steve and Francis
This script will:
1. Create driver profiles for Steve and Francis
2. Import customer data from the extracted Excel files
3. Create optimized routes and assign them to drivers
4. Set up fleet assignments for Lake Charles (loc_2)
"""

import json
import requests
import sys
from datetime import datetime, date
from typing import Dict, List, Any

BASE_URL = "http://localhost:8000"
LOCATION_ID = "loc_2"  # Lake Charles
LOCATION_NAME = "Lake Charles"

def get_auth_token():
    """Get authentication token for API calls"""
    login_data = {
        "username": "manager",  # Default manager user from backend initialization
        "password": "dev-password-change-in-production"  # Default password from backend logs
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error getting auth token: {e}")
        return None

def create_driver_profile(token: str, driver_name: str, username: str) -> bool:
    """Create a driver profile in the system"""
    headers = {"Authorization": f"Bearer {token}"}
    
    driver_data = {
        "username": username,
        "email": f"{username}@arcticice.com",
        "full_name": driver_name,
        "role": "driver",
        "location_id": LOCATION_ID,
        "password": "driver123"  # Default password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/users", json=driver_data, headers=headers)
        if response.status_code == 200:
            print(f"✅ Created driver profile for {driver_name}")
            return True
        else:
            print(f"❌ Failed to create driver {driver_name}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating driver {driver_name}: {e}")
        return False

def create_vehicle(token: str, vehicle_id: str, driver_name: str) -> bool:
    """Create a vehicle for the driver"""
    headers = {"Authorization": f"Bearer {token}"}
    
    vehicle_data = {
        "license_plate": vehicle_id,  # API expects license_plate, not vehicle_id
        "vehicle_type": "20ft_reefer",  # Appropriate for Lake Charles routes
        "capacity_pallets": 12,
        "location_id": LOCATION_ID,
        "is_active": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/vehicles", json=vehicle_data, headers=headers)
        if response.status_code == 200:
            print(f"✅ Created vehicle {vehicle_id} for {driver_name}")
            return True
        else:
            print(f"❌ Failed to create vehicle {vehicle_id}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating vehicle {vehicle_id}: {e}")
        return False

def import_customers_from_route_data(token: str, route_data: Dict) -> List[str]:
    """Import unique customers from the extracted route data"""
    headers = {"Authorization": f"Bearer {token}"}
    imported_customers = []
    seen_names = set()
    
    # First, get existing customers to avoid duplicates across runs
    try:
        response = requests.get(f"{BASE_URL}/api/customers", headers=headers)
        if response.status_code == 200:
            for c in response.json():
                seen_names.add(c['name'].strip().lower())
    except Exception as e:
        print(f"⚠️ Could not fetch existing customers: {e}")

    for day, routes in route_data.items():
        if not routes or len(routes) <= 1:  # Skip empty or header-only routes
            continue
            
        print(f"\n📋 Processing {day} route for unique customers...")
        
        for route in routes[1:]:
            if len(route) < 1:
                continue
                
            customer_name = route[0].strip() if route[0] else "Unknown Customer"
            
            if not customer_name or customer_name.lower() in ['customer', 'name', '', 'nan']:
                continue
            
            # De-duplicate
            name_key = customer_name.lower()
            if name_key in seen_names:
                continue
                
            seen_names.add(name_key)
            
            address = ""
            city = LOCATION_NAME
            phone = ""
            
            # Find address/city/phone in the list (they might be in different indices per row)
            # Based on the JSON structure we saw, Address is around index 4-6
            for part in route[1:]:
                if not part: continue
                part_str = str(part)
                if any(char.isdigit() for char in part_str) and len(part_str) > 5:
                    if '-' in part_str and len(part_str) < 15: # Phone-ish
                        phone = part_str
                    elif ' ' in part_str: # Address-ish
                        address = part_str
            
            customer_data = {
                "id": "",
                "name": customer_name,
                "contact_person": customer_name,
                "address": address,
                "city": city,
                "state": "LA",
                "zip_code": "70601",
                "phone": phone if phone else "(337) 555-0000",
                "location_id": LOCATION_ID,
                "credit_limit": 1000.0,
                "payment_terms": 30,
                "is_active": True
            }
            
            try:
                response = requests.post(f"{BASE_URL}/api/customers", json=customer_data, headers=headers)
                if response.status_code == 200:
                    customer_id = response.json().get("id")
                    imported_customers.append(customer_id)
                    print(f"  ✅ Imported new customer: {customer_name}")
                else:
                    print(f"  ❌ Failed to import customer {customer_name}: {response.status_code}")
            except Exception as e:
                print(f"  ❌ Error importing customer {customer_name}: {e}")
    
    return imported_customers

def create_optimized_route(token: str, route_name: str, driver_name: str, vehicle_id: str, customers: List[str]) -> bool:
    """Create an optimized route for the driver"""
    headers = {"Authorization": f"Bearer {token}"}
    
    route_stops = []
    for customer_id in customers[:10]:  # Limit to first 10 customers for testing
        try:
            response = requests.get(f"{BASE_URL}/api/customers/{customer_id}", headers=headers)
            if response.status_code == 200:
                customer = response.json()
                route_stops.append({
                    "customer_id": customer_id,
                    "customer_name": customer["name"],
                    "address": customer["address"],
                    "city": customer["city"],
                    "bags": 20  # Default bag count
                })
        except Exception as e:
            print(f"  ⚠️  Could not get details for customer {customer_id}: {e}")
    
    if not route_stops:
        print(f"❌ No valid stops found for route {route_name}")
        return False
    
    route_data = {
        "route_name": route_name,
        "driver_name": driver_name,
        "vehicle_id": vehicle_id,
        "location_id": LOCATION_ID,
        "stops": route_stops,
        "date": date.today().isoformat()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/routes/optimize", json=route_data, headers=headers)
        if response.status_code == 200:
            print(f"✅ Created optimized route: {route_name}")
            return True
        else:
            print(f"❌ Failed to create route {route_name}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating route {route_name}: {e}")
        return False

def main():
    print("🚛 ARCTIC ICE SOLUTIONS - LAKE CHARLES DATA IMPORT")
    print("=" * 60)
    print(f"Importing route data for Steve and Francis")
    print(f"Location: {LOCATION_NAME} ({LOCATION_ID})")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("🔐 Authenticating with API...")
    token = get_auth_token()
    if not token:
        print("❌ Failed to authenticate. Make sure the backend is running.")
        sys.exit(1)
    print("✅ Authentication successful")
    
    print("\n👥 Creating driver profiles...")
    steve_created = create_driver_profile(token, "Steve", "steve")
    francis_created = create_driver_profile(token, "Francis", "francis")
    
    print("\n🚚 Creating vehicles...")
    steve_vehicle = create_vehicle(token, "LC-ICE-01", "Steve")
    francis_vehicle = create_vehicle(token, "LC-ICE-02", "Francis")
    
    print("\n📊 Loading extracted route data...")
    try:
        with open('lake_charles_routes.json', 'r') as f:
            lake_charles_data = json.load(f)
        
        with open('smitty_routes.json', 'r') as f:
            smitty_data = json.load(f)
        
        print(f"✅ Loaded Lake Charles data: {list(lake_charles_data.keys())}")
        print(f"✅ Loaded Smitty data: {list(smitty_data.keys())}")
    except Exception as e:
        print(f"❌ Error loading route data: {e}")
        sys.exit(1)
    
    print("\n🏪 Importing customers from Lake Charles routes...")
    lake_charles_customers = import_customers_from_route_data(token, lake_charles_data)
    
    print("\n🏪 Importing customers from Smitty Lake Charles route...")
    smitty_lake_charles = {}
    for route_name, route_data in smitty_data.items():
        if "Lake Charles" in route_name:
            smitty_lake_charles[route_name] = route_data
    
    smitty_customers = import_customers_from_route_data(token, smitty_lake_charles)
    
    print("\n🗺️  Creating optimized routes...")
    
    if lake_charles_data.get("MONDAY") and steve_created and steve_vehicle:
        monday_customers = lake_charles_customers[:len(lake_charles_data["MONDAY"])-1]  # Exclude header
        create_optimized_route(token, "Steve - Monday Lake Charles", "Steve", "LC-ICE-01", monday_customers)
    
    if francis_created and francis_vehicle:
        if lake_charles_data.get("FRIDAY"):
            friday_customers = lake_charles_customers[len(lake_charles_data.get("MONDAY", []))-1:]
            create_optimized_route(token, "Francis - Friday Lake Charles", "Francis", "LC-ICE-02", friday_customers)
        elif smitty_customers:
            create_optimized_route(token, "Francis - Wednesday Lake Charles", "Francis", "LC-ICE-02", smitty_customers)
    
    print("\n✅ IMPORT COMPLETE!")
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"  • Drivers created: {int(steve_created) + int(francis_created)}")
    print(f"  • Vehicles created: {int(steve_vehicle) + int(francis_vehicle)}")
    print(f"  • Customers imported: {len(lake_charles_customers) + len(smitty_customers)}")
    print(f"  • Location: {LOCATION_NAME} ({LOCATION_ID})")
    print()
    print("🌐 Next steps:")
    print("  1. Start the frontend to view the imported data")
    print("  2. Check Fleet Management for vehicle assignments")
    print("  3. Verify routes in the mobile driver interface")
    print("  4. Test route optimization and delivery tracking")

if __name__ == "__main__":
    main()
