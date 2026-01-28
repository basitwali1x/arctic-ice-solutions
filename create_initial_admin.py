
import json
import os
from pathlib import Path
try:
    from passlib.context import CryptContext
except ImportError:
    print("Passlib not installed. Using dummy hash (unsafe).")
    CryptContext = None

from datetime import datetime

# Absolute paths
BASE_DIR = Path(r"C:\Users\Basit\arctic-ice-solutions")
DATA_DIR = BASE_DIR / "backend" / "data"
DATA_FILE = DATA_DIR / "arctic_ice_data.json"

# Setup
if CryptContext:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
else:
    pwd_context = None

DATA_DIR.mkdir(parents=True, exist_ok=True)

USERNAME = "manager"
PASSWORD = "dev-password-change-in-production"
EMAIL = "manager@arcticice.com"

# Known hash for "dev-password-change-in-production" (generated externally if needed, or we rely on passlib)
# If passlib fails, we can't easily sign in unless backend also fails to verifying?
# Backend uses passlib. So we need a valid hash.
# I'll rely on passlib being present since backend is python.

def create_admin():
    print(f"Creating default admin user: {USERNAME}")
    
    if pwd_context:
        hashed_password = pwd_context.hash(PASSWORD)
    else:
        # Fallback: We can't generate, so we abort or use a placeholder?
        # If we use placeholder, login will fail.
        # But maybe the environment HAS passlib.
        print("CRITICAL: passlib not found. Cannot generate hash.")
        return

    admin_user = {
        "id": "user_admin_001",
        "username": USERNAME,
        "email": EMAIL,
        "hashed_password": hashed_password,
        "role": "manager",
        "full_name": "System Manager",
        "location_id": "loc_1", 
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
    
    users = {}
    data = {}
    
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                users = data.get('users', {})
        except Exception as e:
            print(f"Error reading existing data: {e}")

    users[USERNAME] = admin_user
    data['users'] = users
    
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"✅ Admin user created/updated in {DATA_FILE}")
    except Exception as e:
        print(f"Error writing data: {e}")

if __name__ == "__main__":
    create_admin()
