#!/usr/bin/env python3
"""
Reduce customer data from 2,700 to 2,025 customers while maintaining proportional location distribution
"""

import requests
import json
import sys
import argparse
from collections import defaultdict
import random

def authenticate_session():
    """Authenticate with production API and return session with headers"""
    login_data = {
        'username': 'admin',
        'password': 'secure-production-password-2024'
    }
    
    session = requests.Session()
    try:
        login_response = session.post('https://api.yourchoiceice.com/api/auth/login', json=login_data)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return None, None
            
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        return session, headers
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None, None

def analyze_current_customers(session, headers):
    """Analyze current customer distribution and patterns"""
    try:
        customers_response = session.get('https://api.yourchoiceice.com/api/customers', headers=headers)
        if customers_response.status_code != 200:
            print(f"❌ Could not get customers: {customers_response.status_code}")
            return None
            
        customers = customers_response.json()
        print(f"📊 Current total customers: {len(customers)}")
        
    except Exception as e:
        print(f"❌ Error getting customers: {e}")
        return None
    
    location_customers = defaultdict(list)
    sample_customers = []
    uuid_customers = []
    
    for customer in customers:
        customer_id = customer.get('id', '')
        location_id = customer.get('location_id', 'unknown')
        name = customer.get('name', '')
        
        location_customers[location_id].append(customer)
        
        if (customer_id.startswith('leesville_customer_') or 
            customer_id.startswith('lakecharles_customer_') or
            customer_id.startswith('lake_charles_customer_') or
            customer_id.startswith('lufkin_customer_') or
            customer_id.startswith('jasper_customer_') or
            customer_id.startswith('lc_route_')):
            sample_customers.append(customer)
        elif len(customer_id) == 36 and '-' in customer_id:
            uuid_customers.append(customer)
    
    location_names = {
        'loc_1': 'Leesville',
        'loc_2': 'Lake Charles', 
        'loc_3': 'Lufkin',
        'loc_4': 'Jasper'
    }
    
    print(f"\n📍 Current Location Distribution:")
    for loc_id in ['loc_1', 'loc_2', 'loc_3', 'loc_4']:
        location_name = location_names.get(loc_id, loc_id)
        count = len(location_customers[loc_id])
        percentage = (count / len(customers)) * 100
        print(f"  {location_name}: {count} customers ({percentage:.1f}%)")
    
    print(f"\n🏷️  Customer Type Analysis:")
    print(f"  Sample/Demo customers: {len(sample_customers)}")
    print(f"  UUID (Real) customers: {len(uuid_customers)}")
    print(f"  Other format customers: {len(customers) - len(sample_customers) - len(uuid_customers)}")
    
    return {
        'all_customers': customers,
        'location_customers': location_customers,
        'sample_customers': sample_customers,
        'uuid_customers': uuid_customers,
        'location_names': location_names
    }

def calculate_reduction_plan(analysis_data, target_total=2025):
    """Calculate which customers to remove to reach target total"""
    current_total = len(analysis_data['all_customers'])
    reduction_needed = current_total - target_total
    
    print(f"\n🎯 Reduction Plan:")
    print(f"  Current total: {current_total}")
    print(f"  Target total: {target_total}")
    print(f"  Need to remove: {reduction_needed} customers")
    
    sample_customers = analysis_data['sample_customers']
    uuid_customers = analysis_data['uuid_customers']
    location_customers = analysis_data['location_customers']
    
    customers_to_remove = []
    
    print(f"\n📋 Removal Strategy:")
    print(f"  1. Remove all {len(sample_customers)} sample/demo customers first")
    customers_to_remove.extend(sample_customers)
    
    remaining_to_remove = reduction_needed - len(sample_customers)
    if remaining_to_remove > 0:
        print(f"  2. Remove {remaining_to_remove} additional UUID customers proportionally")
        
        location_reduction = {}
        for loc_id in ['loc_1', 'loc_2', 'loc_3', 'loc_4']:
            current_count = len(location_customers[loc_id])
            target_percentage = current_count / current_total
            target_count = int(target_total * target_percentage)
            to_remove = current_count - target_count
            location_reduction[loc_id] = to_remove
            
            location_name = analysis_data['location_names'][loc_id]
            print(f"    {location_name}: {current_count} -> {target_count} (remove {to_remove})")
        
        for loc_id, remove_count in location_reduction.items():
            location_uuid_customers = [c for c in location_customers[loc_id] 
                                     if c not in sample_customers]
            
            location_uuid_customers.sort(key=lambda x: x['name'].lower())
            
            customers_to_remove_from_location = location_uuid_customers[:remove_count]
            customers_to_remove.extend(customers_to_remove_from_location)
    
    print(f"\n📈 Final Removal Summary:")
    print(f"  Total customers to remove: {len(customers_to_remove)}")
    
    removal_by_location = defaultdict(int)
    for customer in customers_to_remove:
        removal_by_location[customer['location_id']] += 1
    
    for loc_id in ['loc_1', 'loc_2', 'loc_3', 'loc_4']:
        location_name = analysis_data['location_names'][loc_id]
        current_count = len(location_customers[loc_id])
        remove_count = removal_by_location[loc_id]
        final_count = current_count - remove_count
        print(f"  {location_name}: {current_count} -> {final_count} (removing {remove_count})")
    
    return customers_to_remove

def execute_customer_deletion(session, headers, customers_to_remove, dry_run=True):
    """Execute the customer deletion process"""
    if dry_run:
        print(f"\n🔍 DRY RUN MODE - No actual deletions will be performed")
        print(f"Would delete {len(customers_to_remove)} customers:")
        
        for i, customer in enumerate(customers_to_remove[:10]):
            print(f"  {i+1}. {customer['name']} (ID: {customer['id'][:20]}..., Location: {customer['location_id']})")
        
        if len(customers_to_remove) > 10:
            print(f"  ... and {len(customers_to_remove) - 10} more customers")
        
        return True
    
    print(f"\n🚀 EXECUTING DELETION of {len(customers_to_remove)} customers...")
    
    deleted_count = 0
    failed_count = 0
    
    for i, customer in enumerate(customers_to_remove):
        try:
            delete_response = session.delete(
                f'https://api.yourchoiceice.com/api/customers/{customer["id"]}', 
                headers=headers
            )
            
            if delete_response.status_code == 200:
                deleted_count += 1
                if (i + 1) % 50 == 0:
                    print(f"  ✅ Deleted {i + 1}/{len(customers_to_remove)} customers...")
            else:
                failed_count += 1
                if failed_count <= 5:
                    print(f"  ❌ Failed to delete '{customer['name']}': {delete_response.status_code}")
                
        except Exception as e:
            failed_count += 1
            if failed_count <= 5:
                print(f"  ❌ Error deleting '{customer['name']}': {e}")
    
    print(f"\n📈 Deletion Results:")
    print(f"  ✅ Successfully deleted: {deleted_count} customers")
    print(f"  ❌ Failed deletions: {failed_count} customers")
    
    return deleted_count > 0

def verify_final_results(session, headers, target_total=2025):
    """Verify the final customer count and distribution"""
    try:
        customers_response = session.get('https://api.yourchoiceice.com/api/customers', headers=headers)
        if customers_response.status_code != 200:
            print(f"❌ Could not verify final results: {customers_response.status_code}")
            return False
            
        final_customers = customers_response.json()
        final_count = len(final_customers)
        
        print(f"\n🎯 Final Verification:")
        print(f"  Target customer count: {target_total}")
        print(f"  Actual customer count: {final_count}")
        
        if final_count == target_total:
            print(f"  ✅ SUCCESS: Reached exact target count!")
        else:
            print(f"  ⚠️  WARNING: Count mismatch (difference: {final_count - target_total})")
        
        location_response = session.get('https://api.yourchoiceice.com/api/customers/by-location', headers=headers)
        if location_response.status_code == 200:
            distribution = location_response.json()
            print(f"\n📍 Final Location Distribution:")
            
            location_names = {
                'loc_1': 'Leesville',
                'loc_2': 'Lake Charles', 
                'loc_3': 'Lufkin',
                'loc_4': 'Jasper'
            }
            
            total_distributed = 0
            for loc_id, count in distribution.items():
                location_name = location_names.get(loc_id, loc_id)
                percentage = (count / final_count) * 100 if final_count > 0 else 0
                print(f"  {location_name}: {count} customers ({percentage:.1f}%)")
                total_distributed += count
            
            print(f"  Total distributed: {total_distributed} customers")
        
        return final_count == target_total
        
    except Exception as e:
        print(f"❌ Error verifying results: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Reduce customer data to 2,025 customers')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')
    parser.add_argument('--execute', action='store_true', help='Actually perform the deletions')
    parser.add_argument('--target', type=int, default=2025, help='Target customer count (default: 2025)')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("❌ Must specify either --dry-run or --execute")
        sys.exit(1)
    
    print(f"🎯 Customer Data Reduction Tool")
    print(f"=" * 50)
    print(f"Target: {args.target} customers")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'EXECUTE'}")
    print(f"=" * 50)
    
    session, headers = authenticate_session()
    if not session:
        sys.exit(1)
    
    analysis_data = analyze_current_customers(session, headers)
    if not analysis_data:
        sys.exit(1)
    
    customers_to_remove = calculate_reduction_plan(analysis_data, args.target)
    
    success = execute_customer_deletion(session, headers, customers_to_remove, args.dry_run)
    if not success:
        print(f"\n❌ Customer deletion failed!")
        sys.exit(1)
    
    if not args.dry_run:
        verify_success = verify_final_results(session, headers, args.target)
        if verify_success:
            print(f"\n🎉 Customer reduction completed successfully!")
            print(f"🌐 Check results at: https://sales-data-app-sy8pl450.devinapps.com")
            print(f"🔑 Login: admin / secure-production-password-2024")
        else:
            print(f"\n⚠️  Customer reduction completed with warnings - please verify manually")
    else:
        print(f"\n✅ Dry run completed - use --execute to perform actual deletions")

if __name__ == "__main__":
    main()
