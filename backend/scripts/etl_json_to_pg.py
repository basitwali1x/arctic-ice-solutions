"""
ETL script to migrate JSON data to Postgres
Usage:
  poetry run python scripts/etl_json_to_pg.py
"""
from __future__ import annotations
import json
import os
import uuid
from pathlib import Path
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app import models

def load_json_file(path: Path, default=None):
    """Load JSON file if it exists, otherwise return default"""
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if data else default
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return default
    return default

def parse_datetime(dt_str):
    """Parse datetime string to datetime object"""
    if not dt_str:
        return None
    if isinstance(dt_str, str):
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except:
            try:
                return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
            except:
                return datetime.now()
    return dt_str

def parse_date(date_str):
    """Parse date string to date object"""
    if not date_str:
        return None
    if isinstance(date_str, str):
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
        except:
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except:
                return date.today()
    return date_str

def ensure_id(data_dict, prefix=""):
    """Ensure data has an ID field"""
    if "id" not in data_dict or not data_dict["id"]:
        data_dict["id"] = f"{prefix}{str(uuid.uuid4())}"
    return data_dict

def migrate_locations(db: Session, locations_data):
    """Migrate locations data"""
    count = 0
    for loc_data in locations_data:
        ensure_id(loc_data, "loc_")
        
        existing = db.query(models.Location).filter_by(id=loc_data["id"]).first()
        if not existing:
            location = models.Location(
                id=loc_data["id"],
                name=loc_data.get("name", ""),
                location_type=loc_data.get("location_type", "distribution"),
                address=loc_data.get("address"),
                city=loc_data.get("city"),
                state=loc_data.get("state"),
                zip_code=loc_data.get("zip_code")
            )
            db.add(location)
            count += 1
    
    db.commit()
    return count

def migrate_customers(db: Session, customers_data):
    """Migrate customers data"""
    count = 0
    for cust_data in customers_data:
        ensure_id(cust_data, "cust_")
        
        existing = db.query(models.Customer).filter_by(id=cust_data["id"]).first()
        if not existing:
            customer = models.Customer(
                id=cust_data["id"],
                name=cust_data.get("name", ""),
                contact_person=cust_data.get("contact_person"),
                phone=cust_data.get("phone"),
                email=cust_data.get("email"),
                address=cust_data.get("address"),
                city=cust_data.get("city"),
                state=cust_data.get("state"),
                zip_code=cust_data.get("zip_code"),
                location_id=cust_data.get("location_id"),
                is_active=cust_data.get("is_active", True),
                credit_limit=cust_data.get("credit_limit", 0),
                payment_terms=cust_data.get("payment_terms", "Net 30")
            )
            db.add(customer)
            count += 1
    
    db.commit()
    return count

def migrate_products(db: Session, products_data):
    """Migrate products data"""
    count = 0
    for prod_data in products_data:
        ensure_id(prod_data, "prod_")
        
        existing = db.query(models.Product).filter_by(id=prod_data["id"]).first()
        if not existing:
            product = models.Product(
                id=prod_data["id"],
                name=prod_data.get("name", ""),
                product_type=prod_data.get("product_type", "bag"),
                price=float(prod_data.get("price", 0)),
                weight_lbs=float(prod_data.get("weight_lbs", 0)),
                is_active=prod_data.get("is_active", True)
            )
            db.add(product)
            count += 1
    
    db.commit()
    return count

def migrate_vehicles(db: Session, vehicles_data):
    """Migrate vehicles data"""
    count = 0
    for veh_data in vehicles_data:
        ensure_id(veh_data, "veh_")
        
        existing = db.query(models.Vehicle).filter_by(id=veh_data["id"]).first()
        if not existing:
            vehicle = models.Vehicle(
                id=veh_data["id"],
                license_plate=veh_data.get("license_plate", ""),
                vehicle_type=veh_data.get("vehicle_type", "reefer"),
                capacity_pallets=int(veh_data.get("capacity_pallets", 0)),
                location_id=veh_data.get("location_id"),
                is_active=veh_data.get("is_active", True)
            )
            db.add(vehicle)
            count += 1
    
    db.commit()
    return count

def migrate_orders(db: Session, orders_data):
    """Migrate orders data"""
    count = 0
    for order_data in orders_data:
        ensure_id(order_data, "ord_")
        
        existing = db.query(models.Order).filter_by(id=order_data["id"]).first()
        if not existing:
            order = models.Order(
                id=order_data["id"],
                customer_id=order_data.get("customer_id", ""),
                product_id=order_data.get("product_id", ""),
                quantity=int(order_data.get("quantity", 1)),
                unit_price=float(order_data.get("unit_price", 0)),
                total_amount=float(order_data.get("total_amount", 0)),
                order_date=parse_datetime(order_data.get("order_date")),
                delivery_date=parse_date(order_data.get("delivery_date")),
                status=order_data.get("status", "pending"),
                route_id=order_data.get("route_id"),
                payment_method=order_data.get("payment_method"),
                notes=order_data.get("notes")
            )
            db.add(order)
            count += 1
    
    db.commit()
    return count

def migrate_work_orders(db: Session, work_orders_data):
    """Migrate work orders data"""
    count = 0
    for wo_data in work_orders_data.values() if isinstance(work_orders_data, dict) else work_orders_data:
        ensure_id(wo_data, "wo_")
        
        existing = db.query(models.WorkOrder).filter_by(id=wo_data["id"]).first()
        if not existing:
            work_order = models.WorkOrder(
                id=wo_data["id"],
                vehicle_id=wo_data.get("vehicle_id"),
                vehicle_name=wo_data.get("vehicle_name"),
                technician_name=wo_data.get("technician_name"),
                issue_description=wo_data.get("issue_description", ""),
                priority=wo_data.get("priority", "medium"),
                status=wo_data.get("status", "pending"),
                work_type=wo_data.get("work_type", "maintenance"),
                submitted_date=parse_datetime(wo_data.get("submitted_date")),
                estimated_cost=float(wo_data.get("estimated_cost", 0)) if wo_data.get("estimated_cost") else None,
                estimated_hours=float(wo_data.get("estimated_hours", 0)) if wo_data.get("estimated_hours") else None,
                approved_by=wo_data.get("approved_by"),
                approved_date=parse_datetime(wo_data.get("approved_date")),
                completed_date=parse_datetime(wo_data.get("completed_date"))
            )
            db.add(work_order)
            count += 1
    
    db.commit()
    return count

def migrate_users(db: Session, users_data):
    """Migrate users data"""
    count = 0
    for user_data in users_data.values() if isinstance(users_data, dict) else users_data:
        ensure_id(user_data, "user_")
        
        existing = db.query(models.User).filter_by(id=user_data["id"]).first()
        if not existing:
            user = models.User(
                id=user_data["id"],
                username=user_data.get("username", ""),
                email=user_data.get("email"),
                full_name=user_data.get("full_name"),
                role=user_data.get("role", "employee"),
                location_id=user_data.get("location_id"),
                is_active=user_data.get("is_active", True),
                hashed_password=user_data.get("hashed_password", "")
            )
            db.add(user)
            count += 1
    
    db.commit()
    return count

def migrate_expenses(db: Session, expenses_data):
    """Migrate expenses data"""
    count = 0
    for expense_data in expenses_data.values() if isinstance(expenses_data, dict) else expenses_data:
        ensure_id(expense_data, "exp_")
        
        existing = db.query(models.Expense).filter_by(id=expense_data["id"]).first()
        if not existing:
            expense = models.Expense(
                id=expense_data["id"],
                category=expense_data.get("category", "general"),
                amount=float(expense_data.get("amount", 0)),
                description=expense_data.get("description", ""),
                expense_date=parse_date(expense_data.get("expense_date")),
                vendor=expense_data.get("vendor"),
                location_id=expense_data.get("location_id"),
                receipt_url=expense_data.get("receipt_url"),
                approved_by=expense_data.get("approved_by"),
                approved_date=parse_datetime(expense_data.get("approved_date"))
            )
            db.add(expense)
            count += 1
    
    db.commit()
    return count

def migrate_financial_documents(db: Session, financial_docs_data):
    """Migrate financial documents data"""
    count = 0
    for doc_data in financial_docs_data.values() if isinstance(financial_docs_data, dict) else financial_docs_data:
        ensure_id(doc_data, "doc_")
        
        existing = db.query(models.FinancialDocument).filter_by(id=doc_data["id"]).first()
        if not existing:
            document = models.FinancialDocument(
                id=doc_data["id"],
                document_type=doc_data.get("document_type", "invoice"),
                document_number=doc_data.get("document_number", ""),
                amount=float(doc_data.get("amount", 0)),
                document_date=parse_date(doc_data.get("document_date")),
                customer_id=doc_data.get("customer_id"),
                order_id=doc_data.get("order_id"),
                file_path=doc_data.get("file_path"),
                status=doc_data.get("status", "pending"),
                notes=doc_data.get("notes")
            )
            db.add(document)
            count += 1
    
    db.commit()
    return count

def migrate_routes(db: Session, routes_data):
    """Migrate routes data"""
    count = 0
    for route_data in routes_data.values() if isinstance(routes_data, dict) else routes_data:
        ensure_id(route_data, "route_")
        
        existing = db.query(models.Route).filter_by(id=route_data["id"]).first()
        if not existing:
            route = models.Route(
                id=route_data["id"],
                route_name=route_data.get("route_name", ""),
                vehicle_id=route_data.get("vehicle_id"),
                driver_name=route_data.get("driver_name"),
                route_date=parse_date(route_data.get("route_date")),
                start_location=route_data.get("start_location"),
                end_location=route_data.get("end_location"),
                total_distance=float(route_data.get("total_distance", 0)) if route_data.get("total_distance") else None,
                estimated_duration=route_data.get("estimated_duration"),
                status=route_data.get("status", "planned"),
                notes=route_data.get("notes")
            )
            db.add(route)
            count += 1
    
    db.commit()
    return count

def migrate_production_entries(db: Session, production_data):
    """Migrate production entries data"""
    count = 0
    for prod_data in production_data.values() if isinstance(production_data, dict) else production_data:
        ensure_id(prod_data, "prod_entry_")
        
        existing = db.query(models.ProductionEntry).filter_by(id=prod_data["id"]).first()
        if not existing:
            production_entry = models.ProductionEntry(
                id=prod_data["id"],
                production_date=parse_date(prod_data.get("production_date")),
                shift=prod_data.get("shift", "day"),
                product_type=prod_data.get("product_type", "8lb_bag"),
                quantity_produced=int(prod_data.get("quantity_produced", 0)),
                quality_rating=prod_data.get("quality_rating"),
                operator_name=prod_data.get("operator_name"),
                location_id=prod_data.get("location_id"),
                notes=prod_data.get("notes")
            )
            db.add(production_entry)
            count += 1
    
    db.commit()
    return count

def main():
    """Main ETL function"""
    print("Starting ETL: JSON → Postgres")
    
    backend_dir = Path(__file__).parent.parent
    data_dir = backend_dir / "data"
    app_data_dir = backend_dir / "app" / "data"
    
    possible_data_dirs = [data_dir, app_data_dir]
    
    locations_data = []
    customers_data = []
    products_data = []
    vehicles_data = []
    orders_data = []
    work_orders_data = {}
    users_data = {}
    expenses_data = {}
    financial_docs_data = {}
    routes_data = {}
    production_data = {}
    
    for data_path in possible_data_dirs:
        if data_path.exists():
            print(f"Checking data directory: {data_path}")
            
            customers_file = data_path / "customers.json"
            if customers_file.exists():
                customers_data.extend(load_json_file(customers_file, []))
            
            orders_file = data_path / "orders.json"
            if orders_file.exists():
                orders_data.extend(load_json_file(orders_file, []))
            
            work_orders_file = data_path / "work_orders.json"
            if work_orders_file.exists():
                work_orders_data.update(load_json_file(work_orders_file, {}))
            
            expenses_file = data_path / "expenses.json"
            if expenses_file.exists():
                expenses_data.update(load_json_file(expenses_file, {}))
            
            financial_docs_file = data_path / "financial_documents.json"
            if financial_docs_file.exists():
                financial_docs_data.update(load_json_file(financial_docs_file, {}))
            
            routes_file = data_path / "routes.json"
            if routes_file.exists():
                routes_data.update(load_json_file(routes_file, {}))
            
            production_file = data_path / "production.json"
            if production_file.exists():
                production_data.update(load_json_file(production_file, {}))
            
            production_entries_file = data_path / "production_entries.json"
            if production_entries_file.exists():
                production_data.update(load_json_file(production_entries_file, {}))
    
    if not customers_data and not orders_data:
        print("No existing data found, creating sample data...")
        
        locations_data = [
            {
                "id": "loc_1",
                "name": "Leesville HQ & Production",
                "location_type": "headquarters",
                "address": "123 Ice Plant Rd",
                "city": "Leesville",
                "state": "Louisiana",
                "zip_code": "71446"
            },
            {
                "id": "loc_2",
                "name": "Lake Charles Distribution",
                "location_type": "distribution",
                "address": "456 Distribution Ave",
                "city": "Lake Charles",
                "state": "Louisiana",
                "zip_code": "70601"
            }
        ]
        
        products_data = [
            {
                "id": "prod_1",
                "name": "8lb Ice Bag",
                "product_type": "8lb_bag",
                "price": 3.50,
                "weight_lbs": 8.0
            },
            {
                "id": "prod_2",
                "name": "20lb Ice Bag",
                "product_type": "20lb_bag",
                "price": 7.00,
                "weight_lbs": 20.0
            }
        ]
        
        vehicles_data = [
            {
                "id": "veh_1",
                "license_plate": "LA-ICE-01",
                "vehicle_type": "53ft_reefer",
                "capacity_pallets": 26,
                "location_id": "loc_1"
            }
        ]
        
        users_data = {
            "user_1": {
                "id": "user_1",
                "username": "manager",
                "email": "manager@arcticice.com",
                "full_name": "System Manager",
                "role": "manager",
                "location_id": "loc_1",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
            }
        }
    
    db = SessionLocal()
    try:
        print("Migrating data to Postgres...")
        
        locations_count = migrate_locations(db, locations_data)
        print(f"Migrated {locations_count} locations")
        
        products_count = migrate_products(db, products_data)
        print(f"Migrated {products_count} products")
        
        customers_count = migrate_customers(db, customers_data)
        print(f"Migrated {customers_count} customers")
        
        vehicles_count = migrate_vehicles(db, vehicles_data)
        print(f"Migrated {vehicles_count} vehicles")
        
        orders_count = migrate_orders(db, orders_data)
        print(f"Migrated {orders_count} orders")
        
        work_orders_count = migrate_work_orders(db, work_orders_data)
        print(f"Migrated {work_orders_count} work orders")
        
        users_count = migrate_users(db, users_data)
        print(f"Migrated {users_count} users")
        
        expenses_count = migrate_expenses(db, expenses_data)
        print(f"Migrated {expenses_count} expenses")
        
        financial_docs_count = migrate_financial_documents(db, financial_docs_data)
        print(f"Migrated {financial_docs_count} financial documents")
        
        routes_count = migrate_routes(db, routes_data)
        print(f"Migrated {routes_count} routes")
        
        production_count = migrate_production_entries(db, production_data)
        print(f"Migrated {production_count} production entries")
        
        print("\nValidation - Database counts:")
        print(f"Locations: {db.query(models.Location).count()}")
        print(f"Products: {db.query(models.Product).count()}")
        print(f"Customers: {db.query(models.Customer).count()}")
        print(f"Vehicles: {db.query(models.Vehicle).count()}")
        print(f"Orders: {db.query(models.Order).count()}")
        print(f"Work Orders: {db.query(models.WorkOrder).count()}")
        print(f"Users: {db.query(models.User).count()}")
        print(f"Expenses: {db.query(models.Expense).count()}")
        print(f"Financial Documents: {db.query(models.FinancialDocument).count()}")
        print(f"Routes: {db.query(models.Route).count()}")
        print(f"Production Entries: {db.query(models.ProductionEntry).count()}")
        
        total_revenue = float(db.query(models.Order).with_entities(
            db.func.coalesce(db.func.sum(models.Order.total_amount), 0)
        ).scalar() or 0)
        total_expenses = float(db.query(models.Expense).with_entities(
            db.func.coalesce(db.func.sum(models.Expense.amount), 0)
        ).scalar() or 0)
        
        print(f"\nFinancial Validation:")
        print(f"Total Revenue: ${total_revenue:,.2f}")
        print(f"Total Expenses: ${total_expenses:,.2f}")
        
        print("\nETL completed successfully!")
        
    except Exception as e:
        print(f"ETL failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
