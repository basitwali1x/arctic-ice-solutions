import os
import requests
import glob
from datetime import datetime
import json

BASE_URL = "http://localhost:8000"
DATA_DIR = r"C:\Users\Basit\OneDrive\Desktop\your choice ice app data"

def get_token():
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "manager",
            "password": "dev-password-change-in-production"
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"❌ Failed to get token: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting token: {e}")
        return None

def import_scans():
    token = get_token()
    if not token:
        print("🛑 Could not proceed without token. Is the backend running?")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # Supported file patterns
    patterns = [
        os.path.join(DATA_DIR, "ai*.pdf"),
        os.path.join(DATA_DIR, "Adobe Scan*.pdf")
    ]
    
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))
        
    if not files:
        print("❓ No scan files found in the data directory.")
        return

    print(f"📦 Found {len(files)} scan files. Importing as 2025 Expenses...")
    
    count = 0
    for file_path in files:
        filename = os.path.basename(file_path)
        
        # Determine category based on filename if possible (just a guess)
        category = "other"
        if "fuel" in filename.lower():
            category = "fuel"
        elif "repair" in filename.lower() or "maintenance" in filename.lower():
            category = "maintenance"
            
        expense_data = {
            "id": "",
            "date": "2025-01-01",  # Historical date for "last year"
            "category": category,
            "description": f"Historical Invoice Scan: {filename}",
            "amount": 0.0,  # User will need to enter the amount in the UI
            "location_id": "loc_1", # Default to HQ
            "submitted_by": "System Import",
            "submitted_at": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/expenses", json=expense_data, headers=headers)
            if response.status_code == 200:
                print(f"  ✅ Imported: {filename}")
                count += 1
            else:
                print(f"  ❌ Failed for {filename}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  ❌ Exception for {filename}: {e}")
            
    print(f"\n✨ Successfully imported {count} expense records.")

if __name__ == "__main__":
    import_scans()
