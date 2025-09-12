"""
Phase 2: Initialize Default Roles
Script to create default roles with permissions for Arctic Ice Solutions
"""
import os
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.auth_models import Role, DEFAULT_ROLES
from app import models  # Import models to register them with SQLAlchemy

def init_roles():
    """Initialize default roles in the database"""
    db: Session = SessionLocal()
    
    try:
        print("Initializing default roles...")
        
        for role_data in DEFAULT_ROLES:
            existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
            
            if existing_role:
                print(f"Role '{role_data['name']}' already exists, updating permissions...")
                existing_role.description = role_data["description"]
                existing_role.permissions = role_data["permissions"]
            else:
                print(f"Creating role '{role_data['name']}'...")
                role = Role(
                    name=role_data["name"],
                    description=role_data["description"],
                    permissions=role_data["permissions"]
                )
                db.add(role)
        
        db.commit()
        
        roles = db.query(Role).all()
        print(f"\nRoles in database ({len(roles)}):")
        for role in roles:
            print(f"  - {role.name}: {role.description}")
            if role.permissions:
                print(f"    Permissions: {list(role.permissions.keys())}")
        
        print("\nRole initialization completed successfully!")
        
    except Exception as e:
        print(f"Error initializing roles: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_roles()
