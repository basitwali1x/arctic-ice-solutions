from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date, timedelta
from enum import Enum
import os
import uuid
import tempfile
import os
import json
from pathlib import Path
from .excel_import import process_excel_files
from jose import JWTError, jwt
from passlib.context import CryptContext

app = FastAPI(title="Arctic Ice Solutions API", version="1.0.0")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-for-local-development-only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# app.mount("/assets", StaticFiles(directory="../frontend/dist/assets"), name="assets")

class UserRole(str, Enum):
    MANAGER = "manager"
    DISPATCHER = "dispatcher"
    ACCOUNTANT = "accountant"
    DRIVER = "driver"

class LocationType(str, Enum):
    HEADQUARTERS = "headquarters"
    PRODUCTION = "production"
    DISTRIBUTION = "distribution"
    WAREHOUSE = "warehouse"

class ProductType(str, Enum):
    BAG_8LB = "8lb_bag"
    BAG_20LB = "20lb_bag"
    BLOCK_ICE = "block_ice"

class VehicleType(str, Enum):
    REEFER_53 = "53ft_reefer"
    REEFER_42 = "42ft_reefer"
    REEFER_20 = "20ft_reefer"
    REEFER_16 = "16ft_reefer"

class PaymentMethod(str, Enum):
    CASH = "cash"
    CHECK = "check"
    CREDIT = "credit"

class OrderStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class WorkOrderStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"

class WorkOrderType(str, Enum):
    MECHANICAL = "mechanical"
    REFRIGERATION = "refrigeration"
    ELECTRICAL = "electrical"
    BODY = "body"

class WorkOrderPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ExpenseCategory(str, Enum):
    FUEL = "fuel"
    MAINTENANCE = "maintenance"
    SUPPLIES = "supplies"
    UTILITIES = "utilities"
    LABOR = "labor"
    OTHER = "other"

class Location(BaseModel):
    id: str
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    location_type: LocationType
    is_active: bool = True

class User(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    location_id: str
    is_active: bool = True

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class Customer(BaseModel):
    id: str
    name: str
    contact_person: str
    phone: str
    email: Optional[str] = None
    address: str
    city: str
    state: str
    zip_code: str
    location_id: str
    credit_limit: float = 0.0
    payment_terms: int = 30
    is_active: bool = True

class Product(BaseModel):
    id: str
    name: str
    product_type: ProductType
    price: float
    weight_lbs: float
    is_active: bool = True

class Vehicle(BaseModel):
    id: str
    license_plate: str
    vehicle_type: VehicleType
    capacity_pallets: int
    location_id: str
    is_active: bool = True
    last_maintenance: Optional[date] = None

class Inventory(BaseModel):
    id: str
    product_id: str
    location_id: str
    quantity: int
    last_updated: datetime

class Route(BaseModel):
    id: str
    name: str
    driver_id: str
    vehicle_id: str
    location_id: str
    date: date
    estimated_duration_hours: float
    status: str = "planned"
    created_at: datetime

class Order(BaseModel):
    id: str
    customer_id: str
    product_id: str
    quantity: int
    unit_price: float
    total_amount: float
    order_date: datetime
    delivery_date: Optional[date] = None
    status: OrderStatus
    route_id: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    notes: Optional[str] = None

class WorkOrder(BaseModel):
    id: str
    vehicle_id: str
    vehicle_name: str
    technician_name: str
    issue_description: str
    priority: WorkOrderPriority
    status: WorkOrderStatus
    work_type: WorkOrderType
    submitted_date: datetime
    estimated_cost: float
    estimated_hours: float
    approved_by: Optional[str] = None
    approved_date: Optional[datetime] = None

class ProductionEntry(BaseModel):
    id: str
    date: date
    shift: int
    pallets_8lb: int
    pallets_20lb: int
    pallets_block_ice: int
    total_pallets: int
    submitted_by: str
    submitted_at: datetime
    location_id: str = "loc_1"

class Expense(BaseModel):
    id: str
    date: date
    category: ExpenseCategory
    description: str
    amount: float
    location_id: str
    submitted_by: str
    submitted_at: datetime

def calculate_distance(addr1: str, addr2: str) -> float:
    hash1 = hash(addr1) % 1000
    hash2 = hash(addr2) % 1000
    return abs(hash1 - hash2) / 10.0

def optimize_route_ai(customers: List[dict], orders: List[dict], vehicle: dict, depot_address: str) -> List[dict]:
    print(f"DEBUG AI: Starting optimization with {len(orders)} orders, {len(customers)} customers")
    if not orders:
        print("DEBUG AI: No orders provided")
        return []
    
    stops = []
    for order in orders:
        customer = next((c for c in customers if c["id"] == order["customer_id"]), None)
        if customer:
            quantity_pallets = max(1, order["quantity"] // 50)  # At least 1 pallet per order
            stops.append({
                "order_id": order["id"],
                "customer_id": customer["id"],
                "address": customer["address"],
                "quantity": quantity_pallets,
                "original_quantity": order["quantity"],
                "customer_name": customer["name"]
            })
            print(f"DEBUG AI: Added stop for customer {customer['name']} with {order['quantity']} units = {quantity_pallets} pallets")
        else:
            print(f"DEBUG AI: No customer found for order {order['id']} with customer_id {order['customer_id']}")
    
    print(f"DEBUG AI: Created {len(stops)} stops from orders")
    if not stops:
        print("DEBUG AI: No stops created")
        return []
    
    route_stops = []
    remaining_stops = stops.copy()
    current_location = depot_address
    current_capacity = 0
    vehicle_capacity = vehicle.get("capacity_pallets", 20)
    print(f"DEBUG AI: Vehicle capacity: {vehicle_capacity} pallets")
    
    remaining_stops.sort(key=lambda x: x["quantity"])
    print(f"DEBUG AI: Sorted stops by pallet quantity: {[s['quantity'] for s in remaining_stops]}")
    
    while remaining_stops:
        best_stop = None
        best_distance = float('inf')
        
        for stop in remaining_stops:
            if current_capacity + stop["quantity"] <= vehicle_capacity:
                distance = calculate_distance(current_location, stop["address"])
                if distance < best_distance:
                    best_distance = distance
                    best_stop = stop
                    print(f"DEBUG AI: Stop {stop['customer_name']} ({stop['quantity']} pallets) fits in remaining capacity")
            else:
                print(f"DEBUG AI: Stop {stop['customer_name']} ({stop['quantity']} pallets) would exceed capacity (current: {current_capacity}, vehicle: {vehicle_capacity})")
        
        if best_stop is None:
            print(f"DEBUG AI: No more stops can fit in vehicle (current capacity: {current_capacity}/{vehicle_capacity} pallets)")
            break
        
        print(f"DEBUG AI: Adding stop {best_stop['customer_name']} to route")
        route_stops.append({
            "id": str(uuid.uuid4()),
            "order_id": best_stop["order_id"],
            "customer_id": best_stop["customer_id"],
            "stop_number": len(route_stops) + 1,
            "estimated_arrival": (datetime.now() + timedelta(hours=len(route_stops) * 0.5)).isoformat(),
            "status": "pending",
            "customer_name": best_stop["customer_name"],
            "address": best_stop["address"]
        })
        
        current_location = best_stop["address"]
        current_capacity += best_stop["quantity"]
        remaining_stops.remove(best_stop)
        print(f"DEBUG AI: Added stop {best_stop['customer_name']}, new capacity: {current_capacity}/{vehicle_capacity} pallets")
    
    print(f"DEBUG AI: Final route has {len(route_stops)} stops")
    return route_stops
    receipt_url: Optional[str] = None

locations_db = {}
users_db = {}
customers_db = {}
products_db = {}
vehicles_db = {}
inventory_db = {}
routes_db = {}
orders_db = {}

imported_customers = []
imported_orders = []
imported_financial_data = {}

work_orders_db = {}
production_entries_db = {}
expenses_db = {}
notifications_db = {}

DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)

CUSTOMERS_FILE = DATA_DIR / "customers.json"
ORDERS_FILE = DATA_DIR / "orders.json"
FINANCIAL_FILE = DATA_DIR / "financial.json"
WORK_ORDERS_FILE = DATA_DIR / "work_orders.json"
PRODUCTION_FILE = DATA_DIR / "production.json"
EXPENSES_FILE = DATA_DIR / "expenses.json"

def save_data_to_disk():
    """Save all data to disk for persistence"""
    try:
        DATA_DIR.mkdir(exist_ok=True)
        
        with open(CUSTOMERS_FILE, 'w') as f:
            json.dump(imported_customers, f, indent=2)
        with open(ORDERS_FILE, 'w') as f:
            json.dump(imported_orders, f, indent=2)
        with open(FINANCIAL_FILE, 'w') as f:
            json.dump(imported_financial_data, f, indent=2)
        with open(WORK_ORDERS_FILE, 'w') as f:
            json.dump(work_orders_db, f, indent=2)
        with open(PRODUCTION_FILE, 'w') as f:
            json.dump(production_entries_db, f, indent=2)
        with open(EXPENSES_FILE, 'w') as f:
            json.dump(expenses_db, f, indent=2)
        print(f"Saved data: {len(imported_customers)} customers, {len(imported_orders)} orders")
    except Exception as e:
        print(f"Error saving data: {e}")

def load_data_from_disk():
    """Load all data from disk on startup"""
    global imported_customers, imported_orders, imported_financial_data
    global work_orders_db, production_entries_db, expenses_db
    
    try:
        if CUSTOMERS_FILE.exists():
            with open(CUSTOMERS_FILE, 'r') as f:
                data = json.load(f)
                if data:  # Only load if data is not empty
                    imported_customers = data
        if ORDERS_FILE.exists():
            with open(ORDERS_FILE, 'r') as f:
                data = json.load(f)
                if data:  # Only load if data is not empty
                    imported_orders = data
        if FINANCIAL_FILE.exists():
            with open(FINANCIAL_FILE, 'r') as f:
                data = json.load(f)
                if data:  # Only load if data is not empty
                    imported_financial_data = data
        if WORK_ORDERS_FILE.exists():
            with open(WORK_ORDERS_FILE, 'r') as f:
                work_orders_db = json.load(f)
        if PRODUCTION_FILE.exists():
            with open(PRODUCTION_FILE, 'r') as f:
                production_entries_db = json.load(f)
        if EXPENSES_FILE.exists():
            with open(EXPENSES_FILE, 'r') as f:
                expenses_db = json.load(f)
        print(f"Loaded data: {len(imported_customers)} customers, {len(imported_orders)} orders")
    except Exception as e:
        print(f"Error loading data: {e}")
        imported_customers = []
        imported_orders = []
        imported_financial_data = {}

load_data_from_disk()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    for user_data in users_db.values():
        if user_data["username"] == username:
            return UserInDB(**user_data)
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def filter_by_location(data: List[dict], user: UserInDB, location_key: str = "location_id") -> List[dict]:
    if user.role in [UserRole.MANAGER, UserRole.ACCOUNTANT]:
        return data
    return [item for item in data if item.get(location_key) == user.location_id]

def initialize_sample_data():
    print("DEBUG: Initializing sample data...")
    locations = [
        Location(
            id="loc_1",
            name="Leesville HQ & Production",
            address="123 Ice Plant Rd",
            city="Leesville",
            state="Louisiana",
            zip_code="71446",
            location_type=LocationType.HEADQUARTERS
        ),
        Location(
            id="loc_2", 
            name="Lake Charles Distribution",
            address="456 Distribution Ave",
            city="Lake Charles",
            state="Louisiana", 
            zip_code="70601",
            location_type=LocationType.DISTRIBUTION
        ),
        Location(
            id="loc_3",
            name="Lufkin Distribution",
            address="789 Delivery St",
            city="Lufkin",
            state="Texas",
            zip_code="75901",
            location_type=LocationType.DISTRIBUTION
        ),
        Location(
            id="loc_4",
            name="Jasper Warehouse",
            address="321 Storage Blvd",
            city="Jasper",
            state="Texas",
            zip_code="75951",
            location_type=LocationType.WAREHOUSE
        )
    ]
    
    for location in locations:
        locations_db[location.id] = location.dict()
    print(f"DEBUG: Added {len(locations)} locations")
    
    products = [
        Product(id="prod_1", name="8lb Ice Bag", product_type=ProductType.BAG_8LB, price=3.50, weight_lbs=8.0),
        Product(id="prod_2", name="20lb Ice Bag", product_type=ProductType.BAG_20LB, price=7.00, weight_lbs=20.0),
        Product(id="prod_3", name="Block Ice", product_type=ProductType.BLOCK_ICE, price=15.00, weight_lbs=25.0)
    ]
    
    for product in products:
        products_db[product.id] = product.dict()
    
    vehicles = [
        Vehicle(id="veh_1", license_plate="LA-ICE-01", vehicle_type=VehicleType.REEFER_53, capacity_pallets=26, location_id="loc_1"),
        Vehicle(id="veh_2", license_plate="LA-ICE-02", vehicle_type=VehicleType.REEFER_42, capacity_pallets=20, location_id="loc_2"),
        Vehicle(id="veh_3", license_plate="TX-ICE-01", vehicle_type=VehicleType.REEFER_20, capacity_pallets=10, location_id="loc_3"),
        Vehicle(id="veh_4", license_plate="TX-ICE-02", vehicle_type=VehicleType.REEFER_20, capacity_pallets=10, location_id="loc_3"),
        Vehicle(id="veh_5", license_plate="LA-ICE-03", vehicle_type=VehicleType.REEFER_20, capacity_pallets=10, location_id="loc_1"),
        Vehicle(id="veh_6", license_plate="LA-ICE-04", vehicle_type=VehicleType.REEFER_20, capacity_pallets=10, location_id="loc_2"),
        Vehicle(id="veh_7", license_plate="TX-ICE-03", vehicle_type=VehicleType.REEFER_16, capacity_pallets=8, location_id="loc_3"),
        Vehicle(id="veh_8", license_plate="LA-ICE-05", vehicle_type=VehicleType.REEFER_16, capacity_pallets=8, location_id="loc_1")
    ]
    
    for vehicle in vehicles:
        vehicles_db[vehicle.id] = vehicle.dict()
    
    sample_work_orders = [
        {
            "id": "wo_1",
            "vehicle_id": "veh_1",
            "vehicle_name": "LA-ICE-01 (53ft Reefer)",
            "technician_name": "Mike Johnson",
            "issue_description": "Refrigeration unit making unusual noise, temperature inconsistent",
            "priority": "high",
            "status": "pending",
            "work_type": "refrigeration",
            "submitted_date": datetime.now().isoformat(),
            "estimated_cost": 850.0,
            "estimated_hours": 4.0
        },
        {
            "id": "wo_2", 
            "vehicle_id": "veh_3",
            "vehicle_name": "TX-ICE-01 (20ft Reefer)",
            "technician_name": "Carlos Rodriguez",
            "issue_description": "Brake pads need replacement, squeaking noise when stopping",
            "priority": "medium",
            "status": "approved",
            "work_type": "mechanical", 
            "submitted_date": (datetime.now() - timedelta(days=1)).isoformat(),
            "estimated_cost": 320.0,
            "estimated_hours": 2.0,
            "approved_by": "John Manager",
            "approved_date": datetime.now().isoformat()
        },
        {
            "id": "wo_3",
            "vehicle_id": "veh_5",
            "vehicle_name": "LA-ICE-03 (20ft Reefer)",
            "technician_name": "Sarah Wilson",
            "issue_description": "Ice cooler door seal needs replacement, losing temperature",
            "priority": "critical",
            "status": "in_progress",
            "work_type": "refrigeration",
            "submitted_date": (datetime.now() - timedelta(hours=2)).isoformat(),
            "estimated_cost": 450.0,
            "estimated_hours": 3.0,
            "approved_by": "John Manager",
            "approved_date": (datetime.now() - timedelta(hours=1)).isoformat()
        },
        {
            "id": "wo_4",
            "vehicle_id": "veh_4",
            "vehicle_name": "TX-ICE-02 (20ft Reefer)",
            "technician_name": "James Martinez",
            "issue_description": "Routine maintenance - oil change and filter replacement",
            "priority": "low",
            "status": "pending",
            "work_type": "mechanical",
            "submitted_date": datetime.now().isoformat(),
            "estimated_cost": 180.0,
            "estimated_hours": 1.5
        },
        {
            "id": "wo_5",
            "vehicle_id": "veh_7",
            "vehicle_name": "TX-ICE-03 (16ft Reefer)",
            "technician_name": "Carlos Rodriguez",
            "issue_description": "Refrigeration unit temperature sensor malfunction",
            "priority": "high",
            "status": "approved",
            "work_type": "refrigeration",
            "submitted_date": (datetime.now() - timedelta(hours=6)).isoformat(),
            "estimated_cost": 520.0,
            "estimated_hours": 3.5,
            "approved_by": "Lufkin Manager",
            "approved_date": (datetime.now() - timedelta(hours=4)).isoformat()
        }
    ]
    
    for wo in sample_work_orders:
        work_orders_db[wo["id"]] = wo
    
    sample_customers = [
        {
            "id": "leesville_customer_1",
            "name": "Leesville Grocery Chain",
            "contact_person": "James Thompson",
            "email": "james@leesgrocery.com",
            "phone": "(337) 555-2001",
            "address": "1500 S 5th St, Leesville, LA 71446",
            "location_id": "loc_1",
            "credit_limit": 15000.0,
            "current_balance": 0.0,
            "payment_terms": "Net 30",
            "status": "active"
        },
        {
            "id": "leesville_customer_2",
            "name": "Vernon Parish Events",
            "contact_person": "Sarah Mitchell",
            "email": "sarah@vernonevents.com",
            "phone": "(337) 555-2002",
            "address": "789 Parish Rd, Leesville, LA 71446",
            "location_id": "loc_1",
            "credit_limit": 8000.0,
            "current_balance": 0.0,
            "payment_terms": "Net 15",
            "status": "active"
        },
        {
            "id": "leesville_customer_3",
            "name": "Fort Polk Commissary",
            "contact_person": "Colonel Mike Davis",
            "email": "mike.davis@fortpolk.army.mil",
            "phone": "(337) 555-2003",
            "address": "Fort Polk, Leesville, LA 71459",
            "location_id": "loc_1",
            "credit_limit": 25000.0,
            "current_balance": 0.0,
            "payment_terms": "Net 30",
            "status": "active"
        },
        {
            "id": "leesville_customer_4",
            "name": "Leesville School District",
            "contact_person": "Dr. Patricia Williams",
            "email": "patricia@leevilleschools.edu",
            "phone": "(337) 555-2004",
            "address": "1200 Education Dr, Leesville, LA 71446",
            "location_id": "loc_1",
            "credit_limit": 12000.0,
            "current_balance": 0.0,
            "payment_terms": "Net 30",
            "status": "active"
        },
        {
            "id": "lakecharles_customer_1",
            "name": "Calcasieu Marina",
            "contact_person": "Captain Robert LeBlanc",
            "email": "robert@calcasieumarina.com",
            "phone": "(337) 555-3001",
            "address": "2500 Marina Dr, Lake Charles, LA 70601",
            "location_id": "loc_2",
            "credit_limit": 18000.0,
            "current_balance": 0.0,
            "payment_terms": "Net 30",
            "status": "active"
        },
        {
            "id": "lakecharles_customer_2",
            "name": "Southwest Louisiana Fair",
            "contact_person": "Michelle Boudreaux",
            "email": "michelle@swlafair.com",
            "phone": "(337) 555-3002",
            "address": "900 Fair Grounds Rd, Lake Charles, LA 70615",
            "location_id": "loc_2",
            "credit_limit": 10000.0,
            "current_balance": 0.0,
            "payment_terms": "Net 15",
            "status": "active"
        },
        {
            "id": "lakecharles_customer_3",
            "name": "Gulf Coast Seafood Processing",
            "contact_person": "Tony Tran",
            "email": "tony@gulfcoastseafood.com",
            "phone": "(337) 555-3003",
            "address": "3200 Industrial Blvd, Lake Charles, LA 70607",
            "location_id": "loc_2",
            "credit_limit": 22000.0,
            "current_balance": 0.0,
            "payment_terms": "Net 30",
            "status": "active"
        },
        {
            "id": "lakecharles_customer_4",
            "name": "McNeese State University",
            "contact_person": "Dr. Jennifer Adams",
            "email": "jennifer@mcneese.edu",
            "phone": "(337) 555-3004",
            "address": "4205 Ryan St, Lake Charles, LA 70609",
            "location_id": "loc_2",
            "credit_limit": 15000.0,
            "current_balance": 0.0,
            "payment_terms": "Net 30",
            "status": "active"
        },
        {
            "id": "lufkin_customer_1",
            "name": "East Texas Ice Supply",
            "contact_person": "Robert Johnson",
            "email": "robert@easttexasice.com",
            "phone": "(936) 555-1001",
            "address": "1234 Commerce St, Lufkin, TX 75901",
            "location_id": "loc_3",
            "credit_limit": 8000.0,
            "current_balance": 0.0,
            "payment_terms": "Net 30",
            "status": "active"
        },
        {
            "id": "lufkin_customer_2", 
            "name": "Piney Woods Convenience",
            "contact_person": "Maria Rodriguez",
            "email": "maria@pineywoodsconv.com",
            "phone": "(936) 555-1002",
            "address": "567 Highway 69, Lufkin, TX 75904",
            "location_id": "loc_3",
            "credit_limit": 5000.0,
            "current_balance": 0.0,
            "payment_terms": "Net 15",
            "status": "active"
        },
        {
            "id": "lufkin_customer_3",
            "name": "Angelina County Events",
            "contact_person": "David Wilson",
            "email": "david@angelinaevents.com", 
            "phone": "(936) 555-1003",
            "address": "890 Event Center Dr, Lufkin, TX 75902",
            "location_id": "loc_3",
            "credit_limit": 10000.0,
            "current_balance": 0.0,
            "payment_terms": "Net 30",
            "status": "active"
        },
        {
            "id": "lufkin_customer_4",
            "name": "Stephen F. Austin University",
            "contact_person": "Dr. Mark Stevens",
            "email": "mark@sfasu.edu",
            "phone": "(936) 555-1004",
            "address": "1936 North St, Nacogdoches, TX 75962",
            "location_id": "loc_3",
            "credit_limit": 12000.0,
            "current_balance": 0.0,
            "payment_terms": "Net 30",
            "status": "active"
        },
        {
            "id": "jasper_customer_1",
            "name": "Jasper Memorial Hospital",
            "contact_person": "Dr. Lisa Chen",
            "email": "lisa@jasperhospital.com",
            "phone": "(409) 555-4001",
            "address": "1275 Marvin Hancock Dr, Jasper, TX 75951",
            "location_id": "loc_4",
            "credit_limit": 20000.0,
            "current_balance": 0.0,
            "payment_terms": "Net 30",
            "status": "active"
        },
        {
            "id": "jasper_customer_2",
            "name": "Pine Ridge Lodge",
            "contact_person": "Tom Anderson",
            "email": "tom@pineridgelodge.com",
            "phone": "(409) 555-4002",
            "address": "890 Lodge Rd, Jasper, TX 75951",
            "location_id": "loc_4",
            "credit_limit": 8000.0,
            "current_balance": 0.0,
            "payment_terms": "Net 15",
            "status": "active"
        },
        {
            "id": "jasper_customer_3",
            "name": "East Texas Lumber Mill",
            "contact_person": "Frank Miller",
            "email": "frank@etlumber.com",
            "phone": "(409) 555-4003",
            "address": "2500 Mill Rd, Jasper, TX 75951",
            "location_id": "loc_4",
            "credit_limit": 15000.0,
            "current_balance": 0.0,
            "payment_terms": "Net 30",
            "status": "active"
        },
        {
            "id": "jasper_customer_4",
            "name": "Jasper County Fair",
            "contact_person": "Betty Sue Walker",
            "email": "betty@jasperfair.com",
            "phone": "(409) 555-4004",
            "address": "1100 Fair Park Rd, Jasper, TX 75951",
            "location_id": "loc_4",
            "credit_limit": 6000.0,
            "current_balance": 0.0,
            "payment_terms": "Net 15",
            "status": "active"
        }
    ]
    
    for customer in sample_customers:
        customers_db[customer["id"]] = customer
    
    sample_orders = [
        {
            "id": "leesville_order_1",
            "customer_id": "leesville_customer_1",
            "product_id": "prod_1",
            "quantity": 500,
            "unit_price": 3.50,
            "total_amount": 1750.00,
            "order_date": datetime.now().isoformat(),
            "delivery_date": str(date.today()),
            "status": "delivered",
            "route_id": None,
            "payment_method": "credit",
            "notes": "Weekly grocery chain delivery"
        },
        {
            "id": "leesville_order_2",
            "customer_id": "leesville_customer_2",
            "product_id": "prod_2",
            "quantity": 100,
            "unit_price": 7.00,
            "total_amount": 700.00,
            "order_date": (datetime.now() - timedelta(days=1)).isoformat(),
            "delivery_date": str(date.today() - timedelta(days=1)),
            "status": "delivered",
            "route_id": None,
            "payment_method": "cash",
            "notes": "Parish event catering"
        },
        {
            "id": "leesville_order_3",
            "customer_id": "leesville_customer_3",
            "product_id": "prod_1",
            "quantity": 800,
            "unit_price": 3.25,
            "total_amount": 2600.00,
            "order_date": datetime.now().isoformat(),
            "delivery_date": str(date.today()),
            "status": "pending",
            "route_id": None,
            "payment_method": "credit",
            "notes": "Fort Polk commissary bulk order"
        },
        {
            "id": "leesville_order_5",
            "customer_id": "leesville_customer_1",
            "product_id": "prod_2",
            "quantity": 200,
            "unit_price": 6.75,
            "total_amount": 1350.00,
            "order_date": datetime.now().isoformat(),
            "delivery_date": str(date.today()),
            "status": "pending",
            "route_id": None,
            "payment_method": "credit",
            "notes": "Additional grocery chain order"
        },
        {
            "id": "leesville_order_6",
            "customer_id": "leesville_customer_2",
            "product_id": "prod_1",
            "quantity": 300,
            "unit_price": 3.50,
            "total_amount": 1050.00,
            "order_date": datetime.now().isoformat(),
            "delivery_date": str(date.today()),
            "status": "pending",
            "route_id": None,
            "payment_method": "cash",
            "notes": "Vernon Parish weekend event"
        },
        {
            "id": "leesville_order_4",
            "customer_id": "leesville_customer_4",
            "product_id": "prod_2",
            "quantity": 150,
            "unit_price": 6.50,
            "total_amount": 975.00,
            "order_date": (datetime.now() - timedelta(days=2)).isoformat(),
            "delivery_date": str(date.today() - timedelta(days=1)),
            "status": "delivered",
            "route_id": None,
            "payment_method": "credit",
            "notes": "School district cafeteria supply"
        },
        {
            "id": "lakecharles_order_1",
            "customer_id": "lakecharles_customer_1",
            "product_id": "prod_1",
            "quantity": 300,
            "unit_price": 3.75,
            "total_amount": 1125.00,
            "order_date": datetime.now().isoformat(),
            "delivery_date": str(date.today()),
            "status": "pending",
            "route_id": None,
            "payment_method": "credit",
            "notes": "Marina fish storage"
        },
        {
            "id": "lakecharles_order_2",
            "customer_id": "lakecharles_customer_2",
            "product_id": "prod_2",
            "quantity": 75,
            "unit_price": 7.25,
            "total_amount": 543.75,
            "order_date": (datetime.now() - timedelta(days=1)).isoformat(),
            "delivery_date": str(date.today()),
            "status": "in_transit",
            "route_id": None,
            "payment_method": "cash",
            "notes": "Fair concession stands"
        },
        {
            "id": "lakecharles_order_3",
            "customer_id": "lakecharles_customer_3",
            "product_id": "prod_3",
            "quantity": 200,
            "unit_price": 15.50,
            "total_amount": 3100.00,
            "order_date": (datetime.now() - timedelta(days=3)).isoformat(),
            "delivery_date": str(date.today() - timedelta(days=2)),
            "status": "delivered",
            "route_id": None,
            "payment_method": "credit",
            "notes": "Seafood processing facility"
        },
        {
            "id": "lakecharles_order_4",
            "customer_id": "lakecharles_customer_4",
            "product_id": "prod_1",
            "quantity": 250,
            "unit_price": 3.50,
            "total_amount": 875.00,
            "order_date": datetime.now().isoformat(),
            "delivery_date": str(date.today()),
            "status": "delivered",
            "route_id": None,
            "payment_method": "credit",
            "notes": "University dining services"
        },
        {
            "id": "lufkin_order_1",
            "customer_id": "lufkin_customer_1",
            "product_id": "prod_1",
            "quantity": 200,
            "unit_price": 3.50,
            "total_amount": 700.00,
            "order_date": (datetime.now() - timedelta(days=3)).isoformat(),
            "delivery_date": str(date.today() - timedelta(days=2)),
            "status": "delivered",
            "route_id": None,
            "payment_method": "credit",
            "notes": "Regular weekly delivery"
        },
        {
            "id": "lufkin_order_2",
            "customer_id": "lufkin_customer_2",
            "product_id": "prod_2", 
            "quantity": 50,
            "unit_price": 7.00,
            "total_amount": 350.00,
            "order_date": (datetime.now() - timedelta(days=1)).isoformat(),
            "delivery_date": str(date.today()),
            "status": "in_transit",
            "route_id": None,
            "payment_method": "cash",
            "notes": "Weekend event supply"
        },
        {
            "id": "lufkin_order_3",
            "customer_id": "lufkin_customer_3",
            "product_id": "prod_3",
            "quantity": 25,
            "unit_price": 15.00,
            "total_amount": 375.00,
            "order_date": datetime.now().isoformat(),
            "delivery_date": str(date.today() + timedelta(days=1)),
            "status": "pending",
            "route_id": None,
            "payment_method": "credit",
            "notes": "Special event - block ice needed"
        },
        {
            "id": "lufkin_order_4",
            "customer_id": "lufkin_customer_4",
            "product_id": "prod_1",
            "quantity": 180,
            "unit_price": 3.25,
            "total_amount": 585.00,
            "order_date": datetime.now().isoformat(),
            "delivery_date": str(date.today()),
            "status": "delivered",
            "route_id": None,
            "payment_method": "credit",
            "notes": "University campus dining"
        },
        {
            "id": "jasper_order_1",
            "customer_id": "jasper_customer_1",
            "product_id": "prod_1",
            "quantity": 400,
            "unit_price": 3.75,
            "total_amount": 1500.00,
            "order_date": (datetime.now() - timedelta(days=2)).isoformat(),
            "delivery_date": str(date.today() - timedelta(days=1)),
            "status": "delivered",
            "route_id": None,
            "payment_method": "credit",
            "notes": "Hospital cafeteria and patient care"
        },
        {
            "id": "jasper_order_2",
            "customer_id": "jasper_customer_2",
            "product_id": "prod_2",
            "quantity": 60,
            "unit_price": 7.50,
            "total_amount": 450.00,
            "order_date": datetime.now().isoformat(),
            "delivery_date": str(date.today()),
            "status": "pending",
            "route_id": None,
            "payment_method": "cash",
            "notes": "Lodge guest services"
        },
        {
            "id": "jasper_order_3",
            "customer_id": "jasper_customer_3",
            "product_id": "prod_1",
            "quantity": 350,
            "unit_price": 3.25,
            "total_amount": 1137.50,
            "order_date": (datetime.now() - timedelta(days=1)).isoformat(),
            "delivery_date": str(date.today()),
            "status": "in_transit",
            "route_id": None,
            "payment_method": "credit",
            "notes": "Lumber mill worker break areas"
        },
        {
            "id": "jasper_order_4",
            "customer_id": "jasper_customer_4",
            "product_id": "prod_2",
            "quantity": 80,
            "unit_price": 7.00,
            "total_amount": 560.00,
            "order_date": datetime.now().isoformat(),
            "delivery_date": str(date.today()),
            "status": "delivered",
            "route_id": None,
            "payment_method": "cash",
            "notes": "County fair vendor booths"
        }
    ]
    
    for order in sample_orders:
        orders_db[order["id"]] = order

    sample_expenses = [
        {
            "id": "exp_1",
            "date": str(date.today()),
            "category": "fuel",
            "description": "Diesel fuel for delivery trucks",
            "amount": 450.75,
            "location_id": "loc_1",
            "submitted_by": "Fleet Manager",
            "submitted_at": datetime.now().isoformat()
        },
        {
            "id": "exp_2",
            "date": str(date.today() - timedelta(days=1)),
            "category": "maintenance",
            "description": "Brake pad replacement - TX-ICE-01",
            "amount": 320.00,
            "location_id": "loc_3",
            "submitted_by": "Maintenance Team",
            "submitted_at": (datetime.now() - timedelta(days=1)).isoformat()
        },
        {
            "id": "exp_3",
            "date": str(date.today()),
            "category": "utilities",
            "description": "Electricity bill - Leesville facility",
            "amount": 1250.00,
            "location_id": "loc_1",
            "submitted_by": "Accounting",
            "submitted_at": datetime.now().isoformat()
        },
        {
            "id": "exp_4",
            "date": str(date.today()),
            "category": "fuel",
            "description": "Diesel fuel for Lufkin delivery routes",
            "amount": 380.50,
            "location_id": "loc_3",
            "submitted_by": "Lufkin Fleet Manager",
            "submitted_at": datetime.now().isoformat()
        },
        {
            "id": "exp_5",
            "date": str(date.today() - timedelta(days=2)),
            "category": "utilities",
            "description": "Electricity bill - Lufkin distribution center",
            "amount": 890.00,
            "location_id": "loc_3",
            "submitted_by": "Lufkin Operations",
            "submitted_at": (datetime.now() - timedelta(days=2)).isoformat()
        },
        {
            "id": "exp_6",
            "date": str(date.today() - timedelta(days=3)),
            "category": "supplies",
            "description": "Ice bags and packaging supplies",
            "amount": 245.75,
            "location_id": "loc_3",
            "submitted_by": "Lufkin Warehouse",
            "submitted_at": (datetime.now() - timedelta(days=3)).isoformat()
        }
    ]
    
    for exp in sample_expenses:
        expenses_db[exp["id"]] = exp

    demo_password = os.getenv("DEMO_USER_PASSWORD", "dev-password-change-in-production")
    print(f"DEBUG: Using demo password: '{demo_password}' (length: {len(demo_password)})")
    
    sample_users = [
        {
            "id": "user_1",
            "username": "manager",
            "email": "manager@arcticeice.com",
            "full_name": "John Manager",
            "role": "manager",
            "location_id": "loc_1",
            "is_active": True,
            "hashed_password": get_password_hash(demo_password)
        },
        {
            "id": "user_2", 
            "username": "dispatcher",
            "email": "dispatcher@arcticeice.com",
            "full_name": "Sarah Dispatcher",
            "role": "dispatcher",
            "location_id": "loc_2",
            "is_active": True,
            "hashed_password": get_password_hash(demo_password)
        },
        {
            "id": "user_3",
            "username": "accountant",
            "email": "accountant@arcticeice.com", 
            "full_name": "Mike Accountant",
            "role": "accountant",
            "location_id": "loc_3",
            "is_active": True,
            "hashed_password": get_password_hash(demo_password)
        },
        {
            "id": "user_4",
            "username": "driver",
            "email": "driver@arcticeice.com",
            "full_name": "Carlos Driver",
            "role": "driver", 
            "location_id": "loc_4",
            "is_active": True,
            "hashed_password": get_password_hash(demo_password)
        }
    ]
    
    for user in sample_users:
        users_db[user["id"]] = user
    print(f"DEBUG: Added {len(sample_users)} users")
    
    # Add sample customers to customers_db (not just imported_customers)
    for customer in sample_customers:
        customers_db[customer["id"]] = customer
    print(f"DEBUG: Added {len(sample_customers)} customers to customers_db")
    
    for order in sample_orders:
        orders_db[order["id"]] = order
    print(f"DEBUG: Added {len(sample_orders)} orders to orders_db")
    
    sample_routes = [
        {
            "id": "route_1",
            "name": "Leesville Morning Route",
            "driver_id": "user_4",
            "vehicle_id": "veh_1",
            "location_id": "loc_1",
            "date": str(date.today()),
            "estimated_duration_hours": 4.0,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "stops": [
                {
                    "id": "stop_1",
                    "route_id": "route_1",
                    "customer_id": "leesville_customer_1",
                    "order_id": "leesville_order_1",
                    "stop_number": 1,
                    "estimated_arrival": (datetime.now() + timedelta(hours=1)).isoformat(),
                    "status": "completed"
                },
                {
                    "id": "stop_2", 
                    "route_id": "route_1",
                    "customer_id": "leesville_customer_2",
                    "order_id": "leesville_order_2", 
                    "stop_number": 2,
                    "estimated_arrival": (datetime.now() + timedelta(hours=2)).isoformat(),
                    "status": "pending"
                }
            ]
        }
    ]
    
    for route in sample_routes:
        routes_db[route["id"]] = route
    print(f"DEBUG: Added {len(sample_routes)} routes")
    
    print(f"DEBUG: Final counts - customers_db: {len(customers_db)}, orders_db: {len(orders_db)}, routes_db: {len(routes_db)}")
    print(f"DEBUG: Final counts - imported_customers: {len(imported_customers)}, imported_orders: {len(imported_orders)}")

initialize_sample_data()

@app.post("/api/auth/login", response_model=Token)
async def login(login_request: LoginRequest):
    print(f"DEBUG: Login attempt for username: {login_request.username}")
    user = authenticate_user(login_request.username, login_request.password)
    if not user:
        print(f"DEBUG: Authentication failed for username: {login_request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    print(f"DEBUG: Authentication successful for username: {login_request.username}")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/logout")
async def logout(current_user: UserInDB = Depends(get_current_user)):
    return {"message": "Successfully logged out"}

@app.get("/api/auth/me", response_model=User)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
    return User(**current_user.dict())

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/api/locations", response_model=List[Location])
async def get_locations(current_user: UserInDB = Depends(get_current_user)):
    locations = list(locations_db.values())
    if current_user.role in [UserRole.MANAGER, UserRole.ACCOUNTANT]:
        return locations
    return [loc for loc in locations if loc["id"] == current_user.location_id]

@app.get("/api/locations/{location_id}", response_model=Location)
async def get_location(location_id: str, current_user: UserInDB = Depends(get_current_user)):
    if location_id not in locations_db:
        raise HTTPException(status_code=404, detail="Location not found")
    if current_user.role not in [UserRole.MANAGER, UserRole.ACCOUNTANT] and location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Access denied to this location")
    return locations_db[location_id]

@app.get("/api/products", response_model=List[Product])
async def get_products(current_user: UserInDB = Depends(get_current_user)):
    return list(products_db.values())

@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: str, current_user: UserInDB = Depends(get_current_user)):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    return products_db[product_id]

@app.get("/api/vehicles", response_model=List[Vehicle])
async def get_vehicles(location_id: Optional[str] = None, current_user: UserInDB = Depends(get_current_user)):
    vehicles = list(vehicles_db.values())
    if location_id:
        vehicles = [v for v in vehicles if v["location_id"] == location_id]
    return filter_by_location(vehicles, current_user)

@app.get("/api/vehicles/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(vehicle_id: str, current_user: UserInDB = Depends(get_current_user)):
    if vehicle_id not in vehicles_db:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    vehicle = vehicles_db[vehicle_id]
    if current_user.role not in [UserRole.MANAGER, UserRole.ACCOUNTANT] and vehicle["location_id"] != current_user.location_id:
        raise HTTPException(status_code=403, detail="Access denied to this vehicle")
    return vehicle

@app.get("/api/customers")
async def get_customers(location_id: Optional[str] = None, current_user: UserInDB = Depends(get_current_user)):
    if imported_customers is not None and len(imported_customers) > 0:
        customers = imported_customers
        if location_id:
            customers = [c for c in customers if c.get("location_id") == location_id]
        return filter_by_location(customers, current_user)
    else:
        customers = list(customers_db.values())
        if location_id:
            customers = [c for c in customers if c["location_id"] == location_id]
        return filter_by_location(customers, current_user)

@app.post("/api/customers", response_model=Customer)
async def create_customer(customer: Customer, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != UserRole.MANAGER and customer.location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Cannot create customer for different location")
    customer.id = str(uuid.uuid4())
    customers_db[customer.id] = customer.dict()
    return customer

@app.get("/api/orders")
async def get_orders(location_id: Optional[str] = None, status: Optional[str] = None, current_user: UserInDB = Depends(get_current_user)):
    if imported_orders is not None and len(imported_orders) > 0:
        orders = imported_orders
        if location_id:
            orders = [o for o in orders if o.get("location_id") == location_id]
        if status:
            orders = [o for o in orders if o.get("status") == status]
        return filter_by_location(orders, current_user)
    else:
        orders = list(orders_db.values())
        if location_id:
            orders = [o for o in orders if customers_db.get(o["customer_id"], {}).get("location_id") == location_id]
        if status:
            orders = [o for o in orders if o["status"] == status]
        
        if current_user.role not in [UserRole.MANAGER, UserRole.ACCOUNTANT]:
            orders = [o for o in orders if customers_db.get(o["customer_id"], {}).get("location_id") == current_user.location_id]
        return orders

@app.post("/api/orders", response_model=Order)
async def create_order(order: Order, current_user: UserInDB = Depends(get_current_user)):
    customer = customers_db.get(order.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if current_user.role != UserRole.MANAGER and customer["location_id"] != current_user.location_id:
        raise HTTPException(status_code=403, detail="Cannot create order for customer in different location")
    order.id = str(uuid.uuid4())
    order.order_date = datetime.now()
    orders_db[order.id] = order.dict()
    return order

@app.get("/api/dashboard/overview")
async def get_dashboard_overview(current_user: UserInDB = Depends(get_current_user)):
    if imported_customers is not None and len(imported_customers) > 0 and imported_orders is not None and len(imported_orders) > 0:
        filtered_customers = filter_by_location(imported_customers, current_user)
        filtered_orders = filter_by_location(imported_orders, current_user)
        total_customers = len(filtered_customers)
        total_orders_today = len([o for o in filtered_orders if o.get("date", "").startswith(str(date.today()))])
        total_revenue = imported_financial_data.get("total_revenue", 0) if imported_financial_data else 0
    else:
        filtered_customers = filter_by_location(list(customers_db.values()), current_user)
        filtered_orders = filter_by_location(list(orders_db.values()), current_user)
        total_customers = len(filtered_customers)
        total_orders_today = len([o for o in filtered_orders if datetime.fromisoformat(o["order_date"].replace('Z', '+00:00')).date() == date.today()])
        total_revenue = 125000.0
    
    filtered_vehicles = filter_by_location(list(vehicles_db.values()), current_user)
    filtered_routes = filter_by_location(list(routes_db.values()), current_user)
    
    return {
        "total_customers": total_customers,
        "total_vehicles": len(filtered_vehicles),
        "total_orders_today": total_orders_today,
        "total_revenue": total_revenue,
        "locations": len(locations_db) if current_user.role in [UserRole.MANAGER, UserRole.ACCOUNTANT] else 1,
        "active_routes": len([r for r in filtered_routes if r["status"] == "active"])
    }

@app.get("/api/dashboard/production")
async def get_production_dashboard(current_user: UserInDB = Depends(get_current_user)):
    filtered_production = filter_by_location(list(production_entries_db.values()), current_user)
    
    return {
        "daily_production_pallets": len([p for p in filtered_production if p.get("date") == str(date.today())]) * 10,
        "target_production_pallets": 160,
        "production_efficiency": 85.5,
        "shift_1_pallets": 45,
        "shift_2_pallets": 35,
        "inventory_levels": {
            "8lb_bags": 1200,
            "20lb_bags": 800,
            "block_ice": 150
        }
    }

@app.get("/api/dashboard/fleet")
async def get_fleet_dashboard(current_user: UserInDB = Depends(get_current_user)):
    vehicles = list(vehicles_db.values())
    filtered_vehicles = filter_by_location(vehicles, current_user)
    
    return {
        "total_vehicles": len(filtered_vehicles),
        "vehicles_in_use": min(6, len(filtered_vehicles)),
        "vehicles_available": max(0, len(filtered_vehicles) - 6),
        "vehicles_maintenance": 0,
        "fleet_utilization": 75.0,
        "vehicles_by_location": {
            "Leesville": len([v for v in filtered_vehicles if v["location_id"] == "loc_1"]),
            "Lake Charles": len([v for v in filtered_vehicles if v["location_id"] == "loc_2"]),
            "Lufkin": len([v for v in filtered_vehicles if v["location_id"] == "loc_3"]),
            "Jasper": len([v for v in filtered_vehicles if v["location_id"] == "loc_4"])
        }
    }

@app.get("/api/dashboard/financial")
async def get_financial_dashboard(current_user: UserInDB = Depends(get_current_user)):
    total_expenses = sum(e["amount"] for e in expenses_db.values())
    
    if imported_financial_data:
        total_revenue = imported_financial_data.get("total_revenue", 0)
        daily_revenue_data = imported_financial_data.get("daily_revenue", {})
        recent_daily = list(daily_revenue_data.values())[-7:] if daily_revenue_data else [0]
        avg_daily = sum(recent_daily) / len(recent_daily) if recent_daily else 0
        
        monthly_revenue_data = imported_financial_data.get("monthly_revenue", {})
        recent_monthly = list(monthly_revenue_data.values())[-1:] if monthly_revenue_data else [0]
        current_monthly = recent_monthly[0] if recent_monthly else 0
        
        return {
            "daily_revenue": avg_daily,
            "monthly_revenue": current_monthly,
            "daily_expenses": total_expenses / 30,
            "monthly_expenses": total_expenses,
            "daily_profit": avg_daily - (total_expenses / 30),
            "payment_breakdown": {
                "cash": 60.0,
                "check": 25.0,
                "credit": 15.0
            },
            "outstanding_invoices": total_revenue * 0.12,
            "tax_liability_ytd": total_revenue * 0.07
        }
    else:
        return {
            "daily_revenue": 12500.00,
            "monthly_revenue": 375000.00,
            "daily_expenses": total_expenses / 30,
            "monthly_expenses": total_expenses,
            "daily_profit": 12500.00 - (total_expenses / 30),
            "payment_breakdown": {
                "cash": 45.2,
                "check": 30.8,
                "credit": 24.0
            },
            "outstanding_invoices": 25000.00,
            "tax_liability_ytd": 45000.00
        }

@app.get("/api/financial/data")
async def get_financial_data(current_user: UserInDB = Depends(get_current_user)):
    if not imported_financial_data:
        return {
            "daily_revenue": [
                {"date": "2024-01-10", "amount": 4200.0},
                {"date": "2024-01-11", "amount": 3800.0},
                {"date": "2024-01-12", "amount": 5100.0},
                {"date": "2024-01-13", "amount": 4600.0},
                {"date": "2024-01-14", "amount": 5300.0},
                {"date": "2024-01-15", "amount": 4900.0},
                {"date": "2024-01-16", "amount": 5500.0}
            ],
            "monthly_revenue": [
                {"month": "Oct 2023", "amount": 98000.0},
                {"month": "Nov 2023", "amount": 105000.0},
                {"month": "Dec 2023", "amount": 112000.0},
                {"month": "Jan 2024", "amount": 125000.0}
            ],
            "outstanding_invoices": 15420.0,
            "tax_liability": 8750.0,
            "payment_methods": [
                {"method": "Credit Card", "amount": 65000.0, "percentage": 52.0},
                {"method": "Cash", "amount": 37500.0, "percentage": 30.0},
                {"method": "Check", "amount": 22500.0, "percentage": 18.0}
            ]
        }
    
    daily_revenue = [
        {"date": date_str, "amount": amount}
        for date_str, amount in imported_financial_data.get("daily_revenue", {}).items()
    ]
    
    monthly_revenue = [
        {"month": month_str, "amount": amount}
        for month_str, amount in imported_financial_data.get("monthly_revenue", {}).items()
    ]
    
    total_revenue = imported_financial_data.get("total_revenue", 0.0)
    
    return {
        "daily_revenue": daily_revenue[-30:],  # Last 30 days
        "monthly_revenue": monthly_revenue,
        "outstanding_invoices": total_revenue * 0.12,  # Estimate 12% outstanding
        "tax_liability": total_revenue * 0.07,  # Estimate 7% tax liability
        "payment_methods": [
            {"method": "Cash", "amount": total_revenue * 0.6, "percentage": 60.0},
            {"method": "Check", "amount": total_revenue * 0.25, "percentage": 25.0},
            {"method": "Credit Card", "amount": total_revenue * 0.15, "percentage": 15.0}
        ]
    }

@app.post("/api/import/excel")
async def import_excel_data(files: List[UploadFile] = File(...), current_user: UserInDB = Depends(get_current_user)):
    """Import historical sales data from Excel files"""
    global imported_customers, imported_orders, imported_financial_data
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    temp_files = []
    try:
        for file in files:
            if not file.filename.endswith(('.xlsx', '.xls', '.xlsm')):
                raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}")
            
            file_ext = os.path.splitext(file.filename)[1] if file.filename else '.xlsx'
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            temp_files.append(temp_file.name)
        
        processed_data = process_excel_files(temp_files)
        
        imported_customers = processed_data["customers"]
        imported_orders = processed_data["orders"] 
        imported_financial_data = processed_data["financial_metrics"]
        
        save_data_to_disk()
        
        return {
            "success": True,
            "message": "Excel data imported successfully",
            "summary": {
                "customers_imported": len(imported_customers),
                "orders_imported": len(imported_orders),
                "total_records": processed_data["total_records"],
                "date_range": processed_data["date_range"],
                "total_revenue": imported_financial_data.get("total_revenue", 0)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Excel files: {str(e)}")
    
    finally:
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass

@app.get("/api/import/status")
async def get_import_status(current_user: UserInDB = Depends(get_current_user)):
    """Get current data import status"""
    return {
        "has_data": len(imported_customers) > 0,
        "customers_count": len(imported_customers),
        "orders_count": len(imported_orders),
        "total_revenue": imported_financial_data.get("total_revenue", 0),
        "date_range": imported_financial_data.get("date_range") if imported_financial_data else None
    }

@app.get("/api/maintenance/work-orders")
async def get_work_orders(status: Optional[str] = None, current_user: UserInDB = Depends(get_current_user)):
    orders = list(work_orders_db.values())
    if status:
        orders = [o for o in orders if o["status"] == status]
    
    if current_user.role not in [UserRole.MANAGER, UserRole.ACCOUNTANT]:
        vehicle_ids = [v["id"] for v in vehicles_db.values() if v["location_id"] == current_user.location_id]
        orders = [o for o in orders if o["vehicle_id"] in vehicle_ids]
    
    return orders

@app.post("/api/maintenance/work-orders")
async def create_work_order(work_order: WorkOrder, current_user: UserInDB = Depends(get_current_user)):
    vehicle = vehicles_db.get(work_order.vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if current_user.role != UserRole.MANAGER and vehicle["location_id"] != current_user.location_id:
        raise HTTPException(status_code=403, detail="Cannot create work order for vehicle in different location")
    
    work_order.id = str(uuid.uuid4())
    work_order.submitted_date = datetime.now()
    work_orders_db[work_order.id] = work_order.dict()
    save_data_to_disk()
    return work_order

@app.post("/api/maintenance/work-orders/{work_order_id}/approve")
async def approve_work_order(work_order_id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can approve work orders")
    
    if work_order_id not in work_orders_db:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    work_orders_db[work_order_id]["status"] = "approved"
    work_orders_db[work_order_id]["approved_by"] = current_user.full_name
    work_orders_db[work_order_id]["approved_date"] = datetime.now().isoformat()
    
    save_data_to_disk()
    return {"success": True, "message": "Work order approved"}

@app.post("/api/maintenance/work-orders/{work_order_id}/reject")
async def reject_work_order(work_order_id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can reject work orders")
    
    if work_order_id not in work_orders_db:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    work_orders_db[work_order_id]["status"] = "rejected"
    save_data_to_disk()
    return {"success": True, "message": "Work order rejected"}

@app.get("/api/production/entries")
async def get_production_entries(current_user: UserInDB = Depends(get_current_user)):
    entries = list(production_entries_db.values())
    if current_user.role not in [UserRole.MANAGER, UserRole.ACCOUNTANT]:
        entries = [e for e in entries if e.get("location_id") == current_user.location_id]
    return sorted(entries, key=lambda x: x["submitted_at"], reverse=True)

@app.post("/api/production/entries")
async def create_production_entry(entry: ProductionEntry, current_user: UserInDB = Depends(get_current_user)):
    entry.id = str(uuid.uuid4())
    entry.submitted_at = datetime.now()
    entry.submitted_by = current_user.full_name
    entry_dict = entry.dict()
    entry_dict["location_id"] = current_user.location_id
    production_entries_db[entry.id] = entry_dict
    save_data_to_disk()
    return entry

@app.get("/api/expenses")
async def get_expenses(location_id: Optional[str] = None, current_user: UserInDB = Depends(get_current_user)):
    expenses = list(expenses_db.values())
    if location_id:
        expenses = [e for e in expenses if e["location_id"] == location_id]
    expenses = filter_by_location(expenses, current_user)
    return sorted(expenses, key=lambda x: x["date"], reverse=True)

@app.post("/api/expenses")
async def create_expense(expense: Expense, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != UserRole.MANAGER and expense.location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Cannot create expense for different location")
    expense.id = str(uuid.uuid4())
    expense.submitted_at = datetime.now()
    expense.submitted_by = current_user.full_name
    expenses_db[expense.id] = expense.dict()
    save_data_to_disk()
    return expense

@app.get("/api/financial/profit-analysis")
async def get_profit_analysis(current_user: UserInDB = Depends(get_current_user)):
    total_expenses = sum(e["amount"] for e in expenses_db.values())
    
    total_revenue = imported_financial_data.get("total_revenue", 125000.0) if imported_financial_data else 125000.0
    
    profit = total_revenue - total_expenses
    profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
    
    expense_by_category = {}
    for expense in expenses_db.values():
        category = expense["category"]
        expense_by_category[category] = expense_by_category.get(category, 0) + expense["amount"]
    
    return {
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "profit": profit,
        "profit_margin": profit_margin,
        "expense_breakdown": expense_by_category,
        "daily_expenses": total_expenses / 30,
    }

@app.get("/api/notifications")
async def get_notifications(current_user: UserInDB = Depends(get_current_user)):
    recent_orders = []
    if imported_orders:
        today = datetime.now().date()
        filtered_orders = filter_by_location(imported_orders, current_user)
        recent_orders = [o for o in filtered_orders if o.get("date", "").startswith(str(today))]
    else:
        filtered_orders = filter_by_location(list(orders_db.values()), current_user)
        today = datetime.now().date()
        recent_orders = []
        for o in filtered_orders:
            order_date = o.get("order_date")
            if isinstance(order_date, str):
                try:
                    order_date = datetime.fromisoformat(order_date.replace('Z', '+00:00')).date()
                except:
                    continue
            elif hasattr(order_date, 'date'):
                order_date = order_date.date()
            else:
                continue
            
            if order_date == today:
                recent_orders.append(o)
    
    notifications = []
    for order in recent_orders[-10:]:
        notifications.append({
            "id": f"notif_{order.get('id', 'unknown')}",
            "type": "new_order",
            "title": "New Customer Order",
            "message": f"Order from {order.get('customer_name', 'Unknown')} - ${order.get('total_amount', 0):.2f}",
            "timestamp": order.get("date", datetime.now().isoformat()),
            "read": False
        })
    
    return notifications

@app.get("/api/routes")
async def get_routes(location_id: Optional[str] = None, current_user: UserInDB = Depends(get_current_user)):
    routes = list(routes_db.values())
    if location_id:
        routes = [r for r in routes if r["location_id"] == location_id]
    return filter_by_location(routes, current_user)

@app.post("/api/routes/optimize")
async def optimize_routes(location_id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role not in [UserRole.MANAGER, UserRole.DISPATCHER]:
        raise HTTPException(status_code=403, detail="Only managers and dispatchers can optimize routes")
    
    orders = list(orders_db.values())
    pending_orders = [o for o in orders if o["status"] == "pending"]
    print(f"DEBUG: Total orders: {len(orders)}, Pending orders: {len(pending_orders)}")
    
    customers = list(customers_db.values())
    location_customers = [c for c in customers if c["location_id"] == location_id]
    location_orders = [o for o in pending_orders if any(c["id"] == o["customer_id"] for c in location_customers)]
    print(f"DEBUG: Location customers: {len(location_customers)}, Location orders: {len(location_orders)}")
    print(f"DEBUG: Location orders: {[o['id'] for o in location_orders]}")
    
    if not location_orders:
        return {"message": "No pending orders found for optimization", "routes": []}
    
    vehicles = list(vehicles_db.values())
    available_vehicles = [v for v in vehicles if v["location_id"] == location_id and v["is_active"]]
    print(f"DEBUG: Available vehicles: {len(available_vehicles)}")
    print(f"DEBUG: Vehicle IDs: {[v['id'] for v in available_vehicles]}")
    
    if not available_vehicles:
        raise HTTPException(status_code=400, detail="No available vehicles for route optimization")
    
    location = locations_db.get(location_id)
    depot_address = location["address"] if location else "123 Ice Plant Rd, Leesville, LA"
    
    optimized_routes = []
    remaining_orders = location_orders.copy()
    
    for vehicle in available_vehicles:
        if not remaining_orders:
            break
            
        print(f"DEBUG: Processing vehicle {vehicle['license_plate']} with capacity {vehicle.get('capacity_pallets', 20)}")
        print(f"DEBUG: Remaining orders: {len(remaining_orders)}")
        
        route_stops = optimize_route_ai(location_customers, remaining_orders, vehicle, depot_address)
        print(f"DEBUG: Generated {len(route_stops)} stops for vehicle {vehicle['license_plate']}")
        
        if route_stops:
            route_id = str(uuid.uuid4())
            route = {
                "id": route_id,
                "name": f"Route {vehicle['license_plate']}-{date.today().strftime('%m%d')}",
                "driver_id": None,
                "vehicle_id": vehicle["id"],
                "location_id": location_id,
                "date": str(date.today()),
                "estimated_duration_hours": len(route_stops) * 0.5,
                "status": "planned",
                "created_at": datetime.now().isoformat(),
                "stops": route_stops
            }
            
            for stop in route_stops:
                stop["route_id"] = route_id
            
            routes_db[route_id] = route
            optimized_routes.append(route)
            
            processed_order_ids = [stop["order_id"] for stop in route_stops]
            remaining_orders = [o for o in remaining_orders if o["id"] not in processed_order_ids]
            
            for order_id in processed_order_ids:
                if order_id in orders_db:
                    orders_db[order_id]["status"] = "assigned"
                    orders_db[order_id]["route_id"] = route_id
    
    save_data_to_disk()
    return {"message": f"Generated {len(optimized_routes)} optimized routes", "routes": optimized_routes}

@app.get("/api/routes/{route_id}")
async def get_route(route_id: str, current_user: UserInDB = Depends(get_current_user)):
    if route_id not in routes_db:
        raise HTTPException(status_code=404, detail="Route not found")
    
    route = routes_db[route_id]
    if current_user.role != UserRole.MANAGER and route["location_id"] != current_user.location_id:
        raise HTTPException(status_code=403, detail="Access denied to this route")
    
    return route

@app.put("/api/routes/{route_id}/status")
async def update_route_status(route_id: str, status: str, current_user: UserInDB = Depends(get_current_user)):
    if route_id not in routes_db:
        raise HTTPException(status_code=404, detail="Route not found")
    
    route = routes_db[route_id]
    if current_user.role != UserRole.MANAGER and route["location_id"] != current_user.location_id:
        raise HTTPException(status_code=403, detail="Access denied to this route")
    
    routes_db[route_id]["status"] = status
    save_data_to_disk()
    return {"success": True, "message": f"Route status updated to {status}"}

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve React SPA for all non-API routes"""
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc") or full_path.startswith("openapi.json"):
        raise HTTPException(status_code=404, detail="Not found")
    
    if full_path.startswith("assets/"):
        file_path = f"../frontend/dist/{full_path}"
        if os.path.exists(file_path):
            return FileResponse(file_path)
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse("../frontend/dist/index.html")
