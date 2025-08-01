import json
from datetime import datetime

def generate_route_analysis():
    """Generate comprehensive analysis of Lake Charles route data for Steve and Francis"""
    
    print("=" * 80)
    print("ARCTIC ICE SOLUTIONS - LAKE CHARLES ROUTE ANALYSIS")
    print("=" * 80)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    with open('/home/ubuntu/lake_charles_routes.json', 'r') as f:
        lake_charles_data = json.load(f)
    
    with open('/home/ubuntu/smitty_routes.json', 'r') as f:
        smitty_data = json.load(f)
    
    print("EXECUTIVE SUMMARY")
    print("-" * 40)
    print("• Two Excel files analyzed containing comprehensive route data")
    print("• No explicit driver assignments found for 'Steve' or 'Francis'")
    print("• Routes are organized by location/day rather than specific drivers")
    print("• Data suggests need to assign these routes to Steve and Francis")
    print()
    
    print("FILE 1: LAKE CHARLES ROUTE SHEET")
    print("-" * 40)
    print(f"Available Routes: {list(lake_charles_data.keys())}")
    
    for day, routes in lake_charles_data.items():
        if routes:  # Skip empty routes
            customer_count = len(routes) - 1  # Subtract header row
            print(f"• {day}: {customer_count} customers")
            
            if len(routes) > 1:
                print(f"  Sample customers:")
                for i, route in enumerate(routes[1:6]):  # Show first 5 customers
                    if len(route) >= 2:
                        customer_name = route[0]
                        address = route[4] if len(route) > 4 else "N/A"
                        city = route[5] if len(route) > 5 else "N/A"
                        print(f"    - {customer_name} ({city})")
                if customer_count > 5:
                    print(f"    ... and {customer_count - 5} more customers")
    print()
    
    print("FILE 2: SMITTY ROUTE SHEET")
    print("-" * 40)
    print(f"Available Routes: {list(smitty_data.keys())}")
    
    for route_name, routes in smitty_data.items():
        if routes:  # Skip empty routes
            customer_count = len(routes) - 1  # Subtract header row
            print(f"• {route_name}: {customer_count} customers")
            
            if "Lake Charles" in route_name and len(routes) > 1:
                print(f"  Sample customers:")
                for i, route in enumerate(routes[1:6]):  # Show first 5 customers
                    if len(route) >= 2:
                        customer_name = route[0]
                        city = route[7] if len(route) > 7 else "N/A"
                        print(f"    - {customer_name} ({city})")
                if customer_count > 5:
                    print(f"    ... and {customer_count - 5} more customers")
    print()
    
    print("ROUTE ASSIGNMENT RECOMMENDATIONS")
    print("-" * 40)
    print("Based on the route data analysis, here are recommendations for Steve and Francis:")
    print()
    
    lake_charles_routes = []
    
    for day, routes in lake_charles_data.items():
        if routes and len(routes) > 1:
            lake_charles_routes.append({
                'source': 'Lake Charles Route Sheet',
                'day': day,
                'customer_count': len(routes) - 1,
                'customers': routes[1:]  # Exclude header
            })
    
    for route_name, routes in smitty_data.items():
        if "Lake Charles" in route_name and routes and len(routes) > 1:
            lake_charles_routes.append({
                'source': 'Smitty Route Sheet',
                'day': route_name,
                'customer_count': len(routes) - 1,
                'customers': routes[1:]  # Exclude header
            })
    
    print("STEVE - RECOMMENDED ROUTE ASSIGNMENT:")
    if len(lake_charles_routes) >= 1:
        route = lake_charles_routes[0]
        print(f"• Route: {route['day']} ({route['source']})")
        print(f"• Customer Count: {route['customer_count']}")
        print(f"• Coverage Area: Lake Charles and surrounding areas")
        
        print("• Key Customers:")
        for i, customer in enumerate(route['customers'][:5]):
            if len(customer) >= 2:
                name = customer[0]
                city = customer[5] if len(customer) > 5 else customer[7] if len(customer) > 7 else "N/A"
                print(f"  - {name} ({city})")
    print()
    
    print("FRANCIS - RECOMMENDED ROUTE ASSIGNMENT:")
    if len(lake_charles_routes) >= 2:
        route = lake_charles_routes[1]
        print(f"• Route: {route['day']} ({route['source']})")
        print(f"• Customer Count: {route['customer_count']}")
        print(f"• Coverage Area: Lake Charles and surrounding areas")
        
        print("• Key Customers:")
        for i, customer in enumerate(route['customers'][:5]):
            if len(customer) >= 2:
                name = customer[0]
                city = customer[5] if len(customer) > 5 else customer[7] if len(customer) > 7 else "N/A"
                print(f"  - {name} ({city})")
    elif len(lake_charles_routes) >= 1:
        print("• Could share route with Steve or be assigned to additional Smitty routes")
        print("• Consider Churchpoint routes from Smitty sheet for expanded coverage")
    print()
    
    print("NEXT STEPS FOR IMPLEMENTATION")
    print("-" * 40)
    print("1. Create driver profiles for Steve and Francis in the system")
    print("2. Import customer data from Excel files using existing import functionality")
    print("3. Assign routes to drivers using the route optimization system")
    print("4. Set up location_id 'loc_2' (Lake Charles) for proper data filtering")
    print("5. Configure mobile driver interface for route management")
    print()
    
    print("TECHNICAL DETAILS")
    print("-" * 40)
    print("• System supports driver role with mobile interface")
    print("• Route optimization available via /api/routes/optimize endpoint")
    print("• Excel import functionality exists in excel_import.py")
    print("• Lake Charles location mapped to loc_2 in system")
    print("• Customer pricing and delivery tracking supported")
    print()
    
    print("=" * 80)

if __name__ == "__main__":
    generate_route_analysis()
