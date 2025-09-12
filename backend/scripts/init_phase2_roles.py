"""
Phase 2: Initialize default roles and migrate existing users
Run this script after Phase 1 migration to set up RBAC system
"""
import os
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.auth_models import Role, UserRole, DEFAULT_ROLES
from app.models import User

def initialize_roles(db: Session):
    """Create default roles if they don't exist"""
    print("Initializing default roles...")
    
    for role_data in DEFAULT_ROLES:
        existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing_role:
            role = Role(
                name=role_data["name"],
                description=role_data["description"],
                permissions=role_data["permissions"]
            )
            db.add(role)
            print(f"  Created role: {role_data['name']}")
        else:
            print(f"  Role already exists: {role_data['name']}")
    
    db.commit()
    print(f"✅ Roles initialization complete")

def migrate_existing_users(db: Session):
    """Assign roles to existing users based on their current role field"""
    print("\nMigrating existing users to new role system...")
    
    users = db.query(User).all()
    role_mapping = {
        "manager": "manager",
        "dispatcher": "dispatcher", 
        "accountant": "accountant",
        "driver": "driver",
        "customer": "customer",
        "employee": "production",  # Map generic employee to production role
    }
    
    for user in users:
        current_role = getattr(user, 'role', 'employee')  # Default to employee if no role
        new_role_name = role_mapping.get(current_role, 'production')
        
        role = db.query(Role).filter(Role.name == new_role_name).first()
        if not role:
            print(f"  ⚠️  Role '{new_role_name}' not found for user {user.username}")
            continue
        
        existing_assignment = db.query(UserRole).filter(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id
        ).first()
        
        if not existing_assignment:
            user_role = UserRole(
                user_id=user.id,
                role_id=role.id,
                assigned_by=None  # System assignment
            )
            db.add(user_role)
            print(f"  Assigned '{new_role_name}' role to user: {user.username}")
        else:
            print(f"  User {user.username} already has role: {new_role_name}")
    
    db.commit()
    print(f"✅ User role migration complete")

def verify_setup(db: Session):
    """Verify the RBAC setup is working correctly"""
    print("\nVerifying RBAC setup...")
    
    role_count = db.query(Role).count()
    print(f"  Total roles: {role_count}")
    
    assignment_count = db.query(UserRole).count()
    print(f"  Total role assignments: {assignment_count}")
    
    assignments = db.query(UserRole).join(User).join(Role).limit(5).all()
    for assignment in assignments:
        user = db.query(User).filter(User.id == assignment.user_id).first()
        role = db.query(Role).filter(Role.id == assignment.role_id).first()
        print(f"  {user.username} -> {role.name}")
    
    print(f"✅ RBAC verification complete")

def main():
    """Main initialization function"""
    print("🚀 Starting Phase 2 RBAC initialization...")
    
    db = SessionLocal()
    try:
        initialize_roles(db)
        migrate_existing_users(db)
        verify_setup(db)
        print("\n🎉 Phase 2 RBAC initialization successful!")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
