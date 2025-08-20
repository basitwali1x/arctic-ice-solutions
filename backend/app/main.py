from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, status, Query
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
import logging
import json
import math
from pathlib import Path
from dotenv import load_dotenv
from .excel_import import process_excel_files, process_customer_excel_files, process_route_excel_files
from .google_sheets_import import process_google_sheets_data, test_google_sheets_connection
from .quickbooks_integration import QuickBooksClient, map_arctic_customer_to_qb, map_arctic_order_to_qb_invoice, map_arctic_payment_to_qb
from .weather_service import weather_service
try:
    from .monitoring_service import router as monitoring_service
except ImportError:
    monitoring_service = None
from jose import JWTError, jwt
from passlib.context import CryptContext
if os.getenv("ENVIRONMENT", "development") == "development":
    from prophet import Prophet
    from sklearn.linear_model import LinearRegression
    import numpy as np
    import pandas as pd
else:
    Prophet = None
    LinearRegression = None
    np = None
    pd = None

load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI(title="Arctic Ice Solutions API", version="1.0.0")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-for-local-development-only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

try:
    from .weather_service import router as weather_router
    from .monitoring_service import router as monitoring_router
    app.include_router(weather_router, prefix="/weather", tags=["weather"])
    app.include_router(monitoring_router, prefix="/monitoring", tags=["monitoring"])
except ImportError as e:
    print(f"Weather and monitoring services not available: {e}")

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allows all origins for development
        "https://yourchoiceice.com",  # New primary domain
        "https://www.yourchoiceice.com",  # New domain with www
        "https://api.yourchoiceice.com",  # API domain
        "https://ice-management-app-4r16aafs.devinapps.com",  # Legacy deployment URL
        "https://dashboard-flicker-app-nx31x17t.devinapps.com",  # New frontend URL
        "http://localhost:5173",  # Local frontend
        "http://localhost:3000",  # Alternative local frontend
    ],
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
    CUSTOMER = "customer"
    EMPLOYEE = "employee"

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
    coordinates: Optional[dict] = None

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

class VehicleCreate(BaseModel):
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
class WorkOrderCreate(BaseModel):
    vehicle_id: str
    vehicle_name: Optional[str] = None
    technician_name: str
    issue_description: str
    priority: WorkOrderPriority
    status: WorkOrderStatus = WorkOrderStatus.PENDING
    work_type: WorkOrderType
    estimated_cost: float = 0
    estimated_hours: float = 0
    approved_by: Optional[str] = None
    approved_date: Optional[datetime] = None



class ProductionEntryCreate(BaseModel):
    date: date
    shift: int
    pallets_8lb: int
    pallets_20lb: int
    pallets_block_ice: int
    total_pallets: int

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

class CustomerPricing(BaseModel):
    id: str
    customer_id: str
    product_id: str
    custom_price: float
    created_at: datetime
    updated_by: str

class QuickBooksConnection(BaseModel):
    access_token: str
    refresh_token: str
    realm_id: str
    expires_at: datetime
    is_active: bool
    company_name: Optional[str] = None
    last_sync: Optional[datetime] = None

class QuickBooksAuthRequest(BaseModel):
    state: Optional[str] = None

class QuickBooksSyncRequest(BaseModel):
    sync_customers: bool = True
    sync_invoices: bool = True
    sync_payments: bool = True

class TrainingModule(BaseModel):
    id: str
    title: str
    description: str
    duration: str
    type: str
    status: str = "available"
    progress: int = 0
    
class EmployeeCertification(BaseModel):
    id: str
    employee_id: str
    title: str
    description: str
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    status: str = "pending"
    nft_id: Optional[str] = None
    blockchain_hash: Optional[str] = None

def calculate_distance(addr1: str, addr2: str, coordinates1: Optional[dict] = None, coordinates2: Optional[dict] = None) -> float:
    """Enhanced distance calculation using Google Maps API or haversine fallback"""
    try:
        import googlemaps
        gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY', ''))
        
        if coordinates1 and coordinates2:
            origin = (coordinates1['lat'], coordinates1['lng'])
            destination = (coordinates2['lat'], coordinates2['lng'])
        else:
            origin = addr1
            destination = addr2
        
        result = gmaps.distance_matrix(
            origins=[origin],
            destinations=[destination],
            mode="driving",
            units="imperial",
            avoid="tolls"
        )
        
        if result['status'] == 'OK' and result['rows'][0]['elements'][0]['status'] == 'OK':
            distance_miles = result['rows'][0]['elements'][0]['distance']['value'] * 0.000621371
            return distance_miles
        else:
            if coordinates1 and coordinates2:
                lat1, lng1 = coordinates1['lat'], coordinates1['lng']
                lat2, lng2 = coordinates2['lat'], coordinates2['lng']
                return haversine_distance(lat1, lng1, lat2, lng2)
            else:
                hash1 = hash(addr1) % 1000
                hash2 = hash(addr2) % 1000
                return abs(hash1 - hash2) / 10.0
    except Exception as e:
        logging.warning(f"Distance calculation failed: {e}")
        if coordinates1 and coordinates2:
            lat1, lng1 = coordinates1['lat'], coordinates1['lng']
            lat2, lng2 = coordinates2['lat'], coordinates2['lng']
            return haversine_distance(lat1, lng1, lat2, lng2)
        else:
            hash1 = hash(addr1) % 1000
            hash2 = hash(addr2) % 1000
            return abs(hash1 - hash2) / 10.0

def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two points using haversine formula"""
    R = 3959  # Earth's radius in miles
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def geocode_address(address: str) -> Optional[dict]:
    """Geocode address using Google Maps API"""
    try:
        import googlemaps
        gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY', ''))
        result = gmaps.geocode(address)
        
        if result:
            location = result[0]['geometry']['location']
            return {'lat': location['lat'], 'lng': location['lng']}
        return None
    except Exception as e:
        logging.warning(f"Geocoding failed for {address}: {e}")
        return None

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

def optimize_with_ortools(locations, demands, coordinates, vehicle_capacity):
    """Use Google OR-Tools for Vehicle Routing Problem optimization"""
    try:
        from ortools.constraint_solver import routing_enums_pb2
        from ortools.constraint_solver import pywrapcp
        
        distance_matrix = create_distance_matrix(coordinates)
        
        manager = pywrapcp.RoutingIndexManager(len(locations), 1, 0)
        
        routing = pywrapcp.RoutingModel(manager)
        
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return distance_matrix[from_node][to_node]
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return demands[from_node]
        
        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            [vehicle_capacity],  # vehicle maximum capacities
            True,  # start cumul to zero
            'Capacity'
        )
        
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = 10
        
        solution = routing.SolveWithParameters(search_parameters)
        
        if solution:
            route = []
            index = routing.Start(0)
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route.append(node_index)
                index = solution.Value(routing.NextVar(index))
            
            return route[1:]  # Remove depot from start
        
        return None
        
    except Exception as e:
        logging.error(f"OR-Tools optimization error: {e}")
        return None

def create_distance_matrix(coordinates):
    """Create distance matrix using Google Maps API or haversine fallback"""
    size = len(coordinates)
    matrix = [[0 for _ in range(size)] for _ in range(size)]
    
    try:
        import googlemaps
        gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY', ''))
        
        result = gmaps.distance_matrix(
            origins=coordinates,
            destinations=coordinates,
            mode="driving",
            units="imperial"
        )
        
        if result['status'] == 'OK':
            for i in range(size):
                for j in range(size):
                    if i != j:
                        element = result['rows'][i]['elements'][j]
                        if element['status'] == 'OK':
                            matrix[i][j] = int(element['distance']['value'])
                        else:
                            lat1, lng1 = coordinates[i]
                            lat2, lng2 = coordinates[j]
                            distance_miles = haversine_distance(lat1, lng1, lat2, lng2)
                            matrix[i][j] = int(distance_miles * 1609.34)  # Convert to meters
        else:
            for i in range(size):
                for j in range(size):
                    if i != j:
                        lat1, lng1 = coordinates[i]
                        lat2, lng2 = coordinates[j]
                        distance_miles = haversine_distance(lat1, lng1, lat2, lng2)
                        matrix[i][j] = int(distance_miles * 1609.34)  # Convert to meters
                        
    except Exception as e:
        logging.warning(f"Distance matrix API failed: {e}")
        for i in range(size):
            for j in range(size):
                if i != j:
                    lat1, lng1 = coordinates[i]
                    lat2, lng2 = coordinates[j]
                    distance_miles = haversine_distance(lat1, lng1, lat2, lng2)
                    matrix[i][j] = int(distance_miles * 1609.34)  # Convert to meters
    
    return matrix

    receipt_url: Optional[str] = None

users_db = {}
customers_db = {}
products_db = {}
vehicles_db = {}
locations_db = {}
orders_db = {}
routes_db = {}
inventory_db = []
work_orders_db = {}
production_entries_db = {}
expenses_db = {}
customer_pricing_db = {}
driver_locations = {}
quickbooks_connection = None
training_modules_db = {}
employee_certifications_db = {}
employee_progress_db = {}
customer_feedback = {}

imported_customers = []
imported_orders = []
imported_financial_data = {}
quickbooks_connection = None
quickbooks_client = QuickBooksClient()

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
        data_file = Path("data/arctic_ice_data.json")
        data_file.parent.mkdir(exist_ok=True)
        
        with open(data_file, 'w') as f:
            json.dump({
                'users': users_db,
                'customers': customers_db,
                'products': products_db,
                'vehicles': vehicles_db,
                'orders': orders_db,
                'routes': routes_db,
                'work_orders': work_orders_db,
                'production_entries': production_entries_db,
                'expenses': expenses_db,
                'customer_pricing': customer_pricing_db,
                'imported_financial_data': imported_financial_data,
                'imported_customers': imported_customers,
                'imported_orders': imported_orders,
                'quickbooks_connection': quickbooks_connection
            }, f, indent=2, default=str)
        
        DATA_DIR.mkdir(exist_ok=True)
        
        with open(CUSTOMERS_FILE, 'w') as f:
            json.dump(imported_customers, f, indent=2, default=str)
        with open(ORDERS_FILE, 'w') as f:
            json.dump(imported_orders, f, indent=2, default=str)
        with open(FINANCIAL_FILE, 'w') as f:
            json.dump(imported_financial_data, f, indent=2, default=str)
        with open(WORK_ORDERS_FILE, 'w') as f:
            json.dump(work_orders_db, f, indent=2, default=str)
        with open(PRODUCTION_FILE, 'w') as f:
            json.dump(production_entries_db, f, indent=2, default=str)
        with open(EXPENSES_FILE, 'w') as f:
            json.dump(expenses_db, f, indent=2, default=str)
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

# In-memory storage for current driver locations
driver_locations = {}

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
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=username)
    if user is None:
        raise credentials_exception
    return user

def filter_by_location(data: List[dict], user: UserInDB, location_key: str = "location_id") -> List[dict]:
    if user.role == UserRole.MANAGER:
        return data
    return [item for item in data if item.get(location_key) == user.location_id]

def get_customer_price_for_product(customer_id: str, product_id: str) -> float:
    for pricing_id, pricing in customer_pricing_db.items():
        if pricing['customer_id'] == customer_id and pricing['product_id'] == product_id:
            return pricing['custom_price']
    
    if product_id in products_db:
        return products_db[product_id]['price']
    
    return 0.0

def get_all_customer_pricing(customer_id: str) -> list:
    return [pricing for pricing in customer_pricing_db.values() if pricing['customer_id'] == customer_id]

def import_route_json_data():
    """Import customer data from route JSON files"""
    import json
    import os
    
    customers_imported = []
    
    lake_charles_file = "lake_charles_routes.json"
    if os.path.exists(lake_charles_file):
        with open(lake_charles_file, 'r') as f:
            data = json.load(f)
        
        customer_names = set()
        for day, routes in data.items():
            if isinstance(routes, list):
                for route in routes:
                    if isinstance(route, list) and len(route) > 0:
                        customer_name = route[0]
                        if customer_name not in ['Customer', 'CUSTOMER', 'LAKE CHARLES ROUTE SHEET-SMITTY-CHURCHPOINT']:
                            customer_names.add(customer_name)
        
        for i, name in enumerate(sorted(customer_names), 1):
            customer_id = f"lc_route_{i:03d}"
            customer = {
                "id": customer_id,
                "name": name,
                "contact_person": f"Contact for {name}",
                "email": f"contact@{name.lower().replace(' ', '').replace('(', '').replace(')', '').replace('#', '').replace('-', '')}example.com",
                "phone": "(337) 555-0100",
                "address": f"Lake Charles Address {i}",
                "city": "Lake Charles",
                "state": "LA",
                "zip_code": "70601",
                "location_id": "loc_2",
                "is_active": True,
                "credit_limit": 10000.0,
                "payment_terms": "Net 30"
            }
            customers_imported.append(customer)
    
    smitty_file = "smitty_routes.json"
    if os.path.exists(smitty_file):
        with open(smitty_file, 'r') as f:
            data = json.load(f)
        
        customer_names = set()
        for day, routes in data.items():
            if isinstance(routes, list):
                for route in routes:
                    if isinstance(route, list) and len(route) > 0:
                        customer_name = route[0]
                        if customer_name not in ['Customer', 'CUSTOMER', 'LAKE CHARLES ROUTE SHEET-SMITTY-CHURCHPOINT']:
                            customer_names.add(customer_name)
        
        existing_count = len(customers_imported)
        for i, name in enumerate(sorted(customer_names), existing_count + 1):
            customer_id = f"lc_route_{i:03d}"
            customer = {
                "id": customer_id,
                "name": name,
                "contact_person": f"Contact for {name}",
                "email": f"contact@{name.lower().replace(' ', '').replace('(', '').replace(')', '').replace('#', '').replace('-', '')}example.com",
                "phone": "(337) 555-0200",
                "address": f"Lake Charles Address {i}",
                "city": "Lake Charles", 
                "state": "LA",
                "zip_code": "70601",
                "location_id": "loc_2",
                "is_active": True,
                "credit_limit": 10000.0,
                "payment_terms": "Net 30"
            }
            customers_imported.append(customer)
    
    current_count = len(customers_imported)
    if current_count < 62:
        for i in range(current_count + 1, 63):
            customer_id = f"lc_route_{i:03d}"
            customer = {
                "id": customer_id,
                "name": f"Lake Charles Customer {i}",
                "contact_person": f"Contact Person {i}",
                "email": f"customer{i}@lakecharlescustomer.com",
                "phone": "(337) 555-0300",
                "address": f"Lake Charles Address {i}",
                "city": "Lake Charles",
                "state": "LA", 
                "zip_code": "70601",
                "location_id": "loc_2",
                "is_active": True,
                "credit_limit": 10000.0,
                "payment_terms": "Net 30"
            }
            customers_imported.append(customer)
    
    return customers_imported

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
            "id": "leesville_customer_5",
            "name": "Vernon Parish Recreation Center",
            "contact_person": "Amanda Johnson",
            "email": "amanda@vernonrec.com",
            "phone": "(337) 555-2005",
            "address": "2100 Recreation Blvd, Leesville, LA 71446",
            "location_id": "loc_1",
            "credit_limit": 7000.0,
            "current_balance": 0.0,
            "payment_terms": "Net 15",
            "status": "active"
        },
        {
            "id": "leesville_customer_6",
            "name": "Sabine Parish Emergency Services",
            "contact_person": "Chief Robert Martinez",
            "email": "robert@sabineems.gov",
            "phone": "(337) 555-2006",
            "address": "500 Emergency Dr, Many, LA 71449",
            "location_id": "loc_1",
            "credit_limit": 5000.0,
            "current_balance": 0.0,
            "payment_terms": "Net 30",
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
        },
        {
            "id": "user_5",
            "username": "customer1",
            "email": "customer1@example.com",
            "full_name": "Jane Customer",
            "role": "customer",
            "location_id": "loc_1",
            "is_active": True,
            "hashed_password": get_password_hash(demo_password)
        },
        {
            "id": "user_6", 
            "username": "customer2",
            "email": "customer2@example.com",
            "full_name": "Bob Customer",
            "role": "customer",
            "location_id": "loc_2",
            "is_active": True,
            "hashed_password": get_password_hash(demo_password)
        },
        {
            "id": "user_7",
            "username": "steve",
            "email": "steve@arcticeice.com",
            "full_name": "Steve",
            "role": "driver",
            "location_id": "loc_2",
            "is_active": True,
            "hashed_password": get_password_hash(demo_password)
        },
        {
            "id": "user_8",
            "username": "francis",
            "email": "francis@arcticeice.com",
            "full_name": "Francis",
            "role": "driver",
            "location_id": "loc_2",
            "is_active": True,
            "hashed_password": get_password_hash(demo_password)
        },
        {
            "id": "user_9",
            "username": "employee",
            "email": "employee@arcticeice.com",
            "full_name": "Alex Employee",
            "role": "employee",
            "location_id": "loc_1",
            "is_active": True,
            "hashed_password": get_password_hash(demo_password)
        },
        {
            "id": "user_10",
            "username": "employee2",
            "email": "employee2@arcticeice.com",
            "full_name": "Jordan Employee",
            "role": "employee",
            "location_id": "loc_2",
            "is_active": True,
            "hashed_password": get_password_hash(demo_password)
        }
    ]
    
    for user in sample_users:
        users_db[user["id"]] = user
    print(f"DEBUG: Added {len(sample_users)} users")
    
    imported_customers = import_route_json_data()
    for customer in imported_customers:
        customers_db[customer["id"]] = customer
    print(f"DEBUG: Imported {len(imported_customers)} customers from route JSON files")
    
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
        },
        {
            "id": "route_2",
            "name": "Lake Charles Route A",
            "driver_id": "user_7",
            "vehicle_id": "veh_2",
            "location_id": "loc_2",
            "date": str(date.today()),
            "estimated_duration_hours": 6.0,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "stops": [
                {
                    "id": "stop_lc_1",
                    "route_id": "route_2",
                    "customer_id": f"lc_route_{i:03d}",
                    "stop_number": i,
                    "estimated_arrival": (datetime.now() + timedelta(hours=i*0.5)).isoformat(),
                    "status": "pending"
                } for i in range(1, 32)
            ]
        },
        {
            "id": "route_3",
            "name": "Lake Charles Route B",
            "driver_id": "user_8",
            "vehicle_id": "veh_4",
            "location_id": "loc_2",
            "date": str(date.today()),
            "estimated_duration_hours": 6.0,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "stops": [
                {
                    "id": "stop_lc_2",
                    "route_id": "route_3",
                    "customer_id": f"lc_route_{i:03d}",
                    "stop_number": i-31,
                    "estimated_arrival": (datetime.now() + timedelta(hours=(i-31)*0.5)).isoformat(),
                    "status": "pending"
                } for i in range(32, 63)
            ]
        }
    ]
    
    for route in sample_routes:
        routes_db[route["id"]] = route
    print(f"DEBUG: Added {len(sample_routes)} routes")
    
    print(f"DEBUG: Final counts - customers_db: {len(customers_db)}, orders_db: {len(orders_db)}, routes_db: {len(routes_db)}")
    print(f"DEBUG: Final counts - imported_customers: {len(imported_customers)}, imported_orders: {len(imported_orders)}")

if os.getenv("ENVIRONMENT", "development") == "development":
    initialize_sample_data()
else:
    print("Production mode: Skipping sample data initialization to conserve memory")

training_modules_db = {
    "ice-handling-safety": {
        "id": "ice-handling-safety",
        "title": "Ice Handling & Safety Protocols",
        "description": "Essential safety procedures for ice handling, storage, and delivery operations",
        "duration": "45 minutes",
        "type": "safety",
        "status": "available"
    },
    "equipment-operation": {
        "id": "equipment-operation", 
        "title": "Equipment Operation Training",
        "description": "Proper operation of ice production and handling equipment",
        "duration": "60 minutes",
        "type": "equipment",
        "status": "available"
    },
    "customer-service": {
        "id": "customer-service",
        "title": "Customer Service Excellence", 
        "description": "Best practices for customer interactions and service delivery",
        "duration": "30 minutes",
        "type": "service",
        "status": "available"
    },
    "quality-control": {
        "id": "quality-control",
        "title": "Quality Control Standards",
        "description": "Understanding and maintaining ice quality standards", 
        "duration": "40 minutes",
        "type": "quality",
        "status": "available"
    }
}

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

@app.get("/api/users")
async def get_users(role: Optional[str] = None, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can access user management")
    
    users = list(users_db.values())
    if role:
        users = [u for u in users if u["role"] == role]
    
    return [User(**{k: v for k, v in user.items() if k != "hashed_password"}) for user in users]

@app.post("/api/users", response_model=User)
async def create_user(user_data: dict, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can create users")
    
    if any(u["username"] == user_data["username"] for u in users_db.values()):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user_id = str(uuid.uuid4())
    new_user = {
        "id": user_id,
        "username": user_data["username"],
        "email": user_data["email"],
        "full_name": user_data["full_name"],
        "role": user_data["role"],
        "location_id": user_data["location_id"],
        "is_active": user_data.get("is_active", True),
        "hashed_password": get_password_hash(user_data["password"])
    }
    
    users_db[user_id] = new_user
    return User(**{k: v for k, v in new_user.items() if k != "hashed_password"})

@app.put("/api/users/{user_id}", response_model=User)
async def update_user(user_id: str, user_data: dict, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can update users")
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    
    if "username" in user_data and user_data["username"] != user["username"]:
        if any(u["username"] == user_data["username"] for u in users_db.values()):
            raise HTTPException(status_code=400, detail="Username already exists")
    
    for key, value in user_data.items():
        if key == "password":
            user["hashed_password"] = get_password_hash(value)
        elif key != "id":
            user[key] = value
    
    users_db[user_id] = user
    return User(**{k: v for k, v in user.items() if k != "hashed_password"})

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can delete users")
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    del users_db[user_id]
    return {"message": "User deleted successfully"}

@app.get("/api/locations", response_model=List[Location])
async def get_locations(current_user: UserInDB = Depends(get_current_user)):
    locations = list(locations_db.values())
    if current_user.role == UserRole.MANAGER:
        return locations
    return [loc for loc in locations if loc["id"] == current_user.location_id]

@app.get("/api/locations/{location_id}", response_model=Location)
async def get_location(location_id: str, current_user: UserInDB = Depends(get_current_user)):
    if location_id not in locations_db:
        raise HTTPException(status_code=404, detail="Location not found")
    if current_user.role != UserRole.MANAGER and location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Access denied to this location")
    return locations_db[location_id]

@app.put("/api/locations/{location_id}", response_model=Location)
async def update_location(location_id: str, location_data: dict, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can update locations")
    
    if location_id not in locations_db:
        raise HTTPException(status_code=404, detail="Location not found")
    
    location = locations_db[location_id]
    
    for key, value in location_data.items():
        if key != "id":
            location[key] = value
    
    locations_db[location_id] = location
    save_data_to_disk()
    return Location(**location)

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
    if current_user.role != UserRole.MANAGER and vehicle["location_id"] != current_user.location_id:
        raise HTTPException(status_code=403, detail="Access denied to this vehicle")
    return vehicle

@app.post("/api/vehicles", response_model=Vehicle)
async def create_vehicle(vehicle_data: VehicleCreate, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != UserRole.MANAGER and vehicle_data.location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Cannot create vehicle for different location")
    
    vehicle_id = str(uuid.uuid4())
    vehicle = Vehicle(
        id=vehicle_id,
        **vehicle_data.dict()
    )
    vehicles_db[vehicle_id] = vehicle.dict()
    save_data_to_disk()
    return vehicle

@app.get("/api/customers")
async def get_customers(location_id: Optional[str] = None, current_user: UserInDB = Depends(get_current_user)):
    if imported_customers and len(imported_customers) > 0:
        customers = imported_customers
    else:
        customers = list(customers_db.values())
    
    if location_id:
        customers = [c for c in customers if c.get("location_id") == location_id]
    
    return filter_by_location(customers, current_user)

@app.get("/api/customers/by-location")
async def get_customers_by_location(current_user: UserInDB = Depends(get_current_user)):
    """Get customer counts by location for the location distribution chart"""
    if imported_customers and len(imported_customers) > 0:
        customers = imported_customers
    else:
        customers = list(customers_db.values())
    
    all_locations = list(locations_db.values())
    filtered_locations = filter_by_location(all_locations, current_user, location_key="id")
    
    location_counts = []
    for location in filtered_locations:
        location_customers = [c for c in customers if c.get("location_id") == location["id"]]
        
        location_counts.append({
            "location_id": location["id"],
            "location_name": location["name"],
            "customer_count": len(location_customers)
        })
    
    return location_counts

@app.post("/api/customers", response_model=Customer)
async def create_customer(customer: Customer, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != UserRole.MANAGER and customer.location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Cannot create customer for different location")
    customer.id = str(uuid.uuid4())
    customers_db[customer.id] = customer.dict()
    return customer

@app.get("/api/customers/{customer_id}/orders")
async def get_customer_orders(customer_id: str, current_user: UserInDB = Depends(get_current_user)):
    sample_orders = [
        {
            "id": f"order-{customer_id}-001",
            "customerId": customer_id,
            "orderDate": "2025-01-20",
            "requestedDeliveryDate": "2025-01-21",
            "status": "out-for-delivery",
            "items": [
                {
                    "productId": "prod_1",
                    "productName": "8lb Ice Bags",
                    "quantity": 100,
                    "unitPrice": get_customer_price_for_product(customer_id, "prod_1"),
                    "totalPrice": get_customer_price_for_product(customer_id, "prod_1") * 100
                }
            ],
            "subtotal": get_customer_price_for_product(customer_id, "prod_1") * 100,
            "tax": get_customer_price_for_product(customer_id, "prod_1") * 100 * 0.09,
            "deliveryFee": 25.00,
            "totalAmount": get_customer_price_for_product(customer_id, "prod_1") * 100 * 1.09 + 25.00,
            "deliveryAddress": "Customer Address",
            "paymentMethod": "credit",
            "paymentStatus": "pending",
            "invoiceNumber": f"INV-{customer_id}-001",
            "trackingInfo": {
                "driverName": "Mike Johnson",
                "vehicleId": "VEH-001",
                "estimatedArrival": "2:30 PM",
                "currentLocation": {
                    "lat": 31.1565,
                    "lng": -93.2865,
                    "timestamp": "2025-01-21T14:15:00Z"
                }
            }
        },
        {
            "id": f"order-{customer_id}-002",
            "customerId": customer_id,
            "orderDate": "2025-01-19",
            "requestedDeliveryDate": "2025-01-20",
            "status": "confirmed",
            "items": [
                {
                    "productId": "prod_2",
                    "productName": "20lb Ice Bags",
                    "quantity": 50,
                    "unitPrice": get_customer_price_for_product(customer_id, "prod_2"),
                    "totalPrice": get_customer_price_for_product(customer_id, "prod_2") * 50
                }
            ],
            "subtotal": get_customer_price_for_product(customer_id, "prod_2") * 50,
            "tax": get_customer_price_for_product(customer_id, "prod_2") * 50 * 0.09,
            "deliveryFee": 25.00,
            "totalAmount": get_customer_price_for_product(customer_id, "prod_2") * 50 * 1.09 + 25.00,
            "deliveryAddress": "Customer Address",
            "paymentMethod": "credit",
            "paymentStatus": "pending",
            "invoiceNumber": f"INV-{customer_id}-002",
            "trackingInfo": {
                "driverName": "Sarah Williams",
                "vehicleId": "VEH-002",
                "estimatedArrival": "10:00 AM",
                "currentLocation": {
                    "lat": 31.2000,
                    "lng": -93.3000,
                    "timestamp": "2025-01-20T09:45:00Z"
                }
            }
        }
    ]
    return sample_orders

@app.post("/api/customers/{customer_id}/orders")
async def create_customer_order(customer_id: str, order_data: dict, current_user: UserInDB = Depends(get_current_user)):
    import time
    new_order = {
        "id": f"order-{customer_id}-{int(time.time())}",
        "customerId": customer_id,
        **order_data,
        "status": "pending",
        "paymentStatus": "pending"
    }
    return new_order

@app.get("/api/customers/{customer_id}/pricing")
async def get_customer_pricing(customer_id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can access customer pricing")
    
    pricing_records = get_all_customer_pricing(customer_id)
    products = list(products_db.values())
    
    result = []
    for product in products:
        custom_price = None
        for pricing in pricing_records:
            if pricing['product_id'] == product['id']:
                custom_price = pricing['custom_price']
                break
        
        result.append({
            "product_id": product['id'],
            "product_name": product['name'],
            "default_price": product['price'],
            "custom_price": custom_price
        })
    
    return result

@app.post("/api/customers/{customer_id}/pricing")
async def set_customer_pricing(customer_id: str, pricing_data: dict, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can set customer pricing")
    
    product_id = pricing_data.get('product_id')
    custom_price = pricing_data.get('custom_price')
    
    if not product_id or custom_price is None:
        raise HTTPException(status_code=400, detail="product_id and custom_price are required")
    
    if custom_price < 0:
        raise HTTPException(status_code=400, detail="Price must be non-negative")
    
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if customer_id not in customers_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    existing_pricing_id = None
    for pricing_id, pricing in customer_pricing_db.items():
        if pricing['customer_id'] == customer_id and pricing['product_id'] == product_id:
            existing_pricing_id = pricing_id
            break
    
    if existing_pricing_id:
        customer_pricing_db[existing_pricing_id]['custom_price'] = custom_price
        customer_pricing_db[existing_pricing_id]['updated_by'] = current_user.username
        pricing_record = customer_pricing_db[existing_pricing_id]
    else:
        pricing_id = str(uuid.uuid4())
        pricing_record = {
            "id": pricing_id,
            "customer_id": customer_id,
            "product_id": product_id,
            "custom_price": custom_price,
            "created_at": datetime.now().isoformat(),
            "updated_by": current_user.username
        }
        customer_pricing_db[pricing_id] = pricing_record
    
    save_data_to_disk()
    return pricing_record

@app.delete("/api/customers/{customer_id}/pricing/{product_id}")
async def delete_customer_pricing(customer_id: str, product_id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can delete customer pricing")
    
    pricing_id_to_delete = None
    for pricing_id, pricing in customer_pricing_db.items():
        if pricing['customer_id'] == customer_id and pricing['product_id'] == product_id:
            pricing_id_to_delete = pricing_id
            break
    
    if not pricing_id_to_delete:
        raise HTTPException(status_code=404, detail="Custom pricing not found")
    
    del customer_pricing_db[pricing_id_to_delete]
    save_data_to_disk()
    return {"message": "Custom pricing deleted successfully"}

@app.get("/api/customers/{customer_id}/feedback")
async def get_customer_feedback(customer_id: str, current_user: UserInDB = Depends(get_current_user)):
    sample_feedback = [
        {
            "id": f"feedback-{customer_id}-001",
            "customerId": customer_id,
            "type": "delivery",
            "rating": 5,
            "subject": "Excellent Service",
            "message": "Driver was professional and on time.",
            "submittedAt": "2025-01-20T14:30:00Z",
            "status": "new"
        }
    ]
    return sample_feedback

@app.post("/api/customers/{customer_id}/feedback")
async def create_customer_feedback(customer_id: str, feedback_data: dict, current_user: UserInDB = Depends(get_current_user)):
    import time
    new_feedback = {
        "id": f"feedback-{customer_id}-{int(time.time())}",
        "customerId": customer_id,
        **feedback_data,
        "submittedAt": datetime.now().isoformat(),
        "status": "new"
    }
    return new_feedback

@app.get("/api/invoices")
async def get_invoices(customer_id: Optional[str] = None, current_user: UserInDB = Depends(get_current_user)):
    sample_invoices = [
        {
            "id": f"inv-{customer_id or 'all'}-001",
            "customerId": customer_id or "cust-001",
            "invoiceNumber": f"INV-2025-001",
            "issueDate": "2025-01-20",
            "dueDate": "2025-02-19",
            "subtotal": 250.00,
            "tax": 22.50,
            "totalAmount": 297.50,
            "paidAmount": 0.00,
            "balanceDue": 297.50,
            "status": "sent",
            "paymentTerms": "Net 30"
        }
    ]
    
    if customer_id:
        return [inv for inv in sample_invoices if inv["customerId"] == customer_id]
    return sample_invoices

@app.get("/api/invoices/{invoice_id}/download")
async def download_invoice_pdf(invoice_id: str, current_user: UserInDB = Depends(get_current_user)):
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from io import BytesIO
    from fastapi.responses import StreamingResponse
    
    invoice_data = {
        "invoiceNumber": "INV-2025-001",
        "issueDate": "2025-01-20",
        "dueDate": "2025-02-19",
        "customerName": "Sample Customer",
        "customerAddress": "123 Main St, City, State 12345",
        "items": [
            {"description": "8lb Ice Bags", "quantity": 50, "unitPrice": 2.50, "total": 125.00},
            {"description": "20lb Ice Bags", "quantity": 25, "unitPrice": 5.00, "total": 125.00}
        ],
        "subtotal": 250.00,
        "tax": 22.50,
        "totalAmount": 297.50,
        "paymentTerms": "Net 30"
    }
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#1f2937')
    )
    
    elements.append(Paragraph("Arctic Ice Solutions", title_style))
    elements.append(Paragraph("Ice Manufacturing & Distribution", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph(f"INVOICE #{invoice_data['invoiceNumber']}", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    invoice_details = [
        ['Issue Date:', invoice_data['issueDate']],
        ['Due Date:', invoice_data['dueDate']],
        ['Payment Terms:', invoice_data['paymentTerms']]
    ]
    
    details_table = Table(invoice_details, colWidths=[2*inch, 3*inch])
    details_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Bill To:", styles['Heading3']))
    elements.append(Paragraph(invoice_data['customerName'], styles['Normal']))
    elements.append(Paragraph(invoice_data['customerAddress'], styles['Normal']))
    elements.append(Spacer(1, 20))
    
    items_data = [['Description', 'Quantity', 'Unit Price', 'Total']]
    for item in invoice_data['items']:
        items_data.append([
            item['description'],
            str(item['quantity']),
            f"${item['unitPrice']:.2f}",
            f"${item['total']:.2f}"
        ])
    
    items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 20))
    
    totals_data = [
        ['Subtotal:', f"${invoice_data['subtotal']:.2f}"],
        ['Tax:', f"${invoice_data['tax']:.2f}"],
        ['Total Amount:', f"${invoice_data['totalAmount']:.2f}"]
    ]
    
    totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
    ]))
    elements.append(totals_table)
    
    doc.build(elements)
    buffer.seek(0)
    
    return StreamingResponse(
        BytesIO(buffer.read()),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=invoice_{invoice_data['invoiceNumber']}.pdf"}
    )

@app.post("/api/payments")
async def process_payment(payment_data: dict, current_user: UserInDB = Depends(get_current_user)):
    import time
    new_payment = {
        "id": f"payment-{int(time.time())}",
        **payment_data,
        "paymentDate": datetime.now().isoformat(),
        "status": "completed"
    }
    return new_payment

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
        
        if current_user.role != UserRole.MANAGER:
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
    if imported_customers and len(imported_customers) > 0:
        customers = imported_customers
    else:
        customers = list(customers_db.values())
    
    filtered_customers = filter_by_location(customers, current_user)
    total_customers = len(filtered_customers)
    
    if imported_orders is not None and len(imported_orders) > 0:
        filtered_orders = filter_by_location(imported_orders, current_user)
        total_orders_today = len([o for o in filtered_orders if o.get("order_date", "") and datetime.fromisoformat(o["order_date"].replace('Z', '+00:00')).date() == date.today()])
        total_revenue = imported_financial_data.get("total_revenue", 0) if imported_financial_data else 0
    else:
        filtered_orders = filter_by_location(list(orders_db.values()), current_user)
        total_orders_today = len([o for o in filtered_orders if o.get("order_date") and datetime.fromisoformat(o["order_date"].replace('Z', '+00:00')).date() == date.today()])
        total_revenue = 125000.0
    
    filtered_vehicles = filter_by_location(list(vehicles_db.values()), current_user)
    filtered_routes = filter_by_location(list(routes_db.values()), current_user)
    
    return {
        "total_customers": total_customers,
        "total_vehicles": len(filtered_vehicles),
        "total_orders_today": total_orders_today,
        "total_revenue": total_revenue,
        "locations": len(locations_db) if current_user.role == UserRole.MANAGER else 1,
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
    
    active_vehicles = [v for v in filtered_vehicles if v.get("is_active", True)]
    total_vehicles = len(active_vehicles)
    
    work_orders = list(work_orders_db.values())
    vehicles_in_maintenance = set()
    for wo in work_orders:
        if wo.get("status") in ["pending", "approved"]:
            vehicles_in_maintenance.add(wo.get("vehicle_id"))
    
    routes = list(routes_db.values())
    today_str = str(date.today())
    vehicles_in_use = set()
    for route in routes:
        if route.get("date") == today_str and route.get("status") in ["planned", "in_progress"]:
            vehicles_in_use.add(route.get("vehicle_id"))
    
    maintenance_count = len([vid for vid in vehicles_in_maintenance if any(v["id"] == vid for v in active_vehicles)])
    in_use_count = len([vid for vid in vehicles_in_use if any(v["id"] == vid for v in active_vehicles)])
    
    available_count = max(0, total_vehicles - in_use_count - maintenance_count)
    
    fleet_utilization = (in_use_count / total_vehicles * 100) if total_vehicles > 0 else 0.0
    
    return {
        "total_vehicles": total_vehicles,
        "vehicles_in_use": in_use_count,
        "vehicles_available": available_count,
        "vehicles_maintenance": maintenance_count,
        "fleet_utilization": round(fleet_utilization, 1),
        "vehicles_by_location": {
            "Leesville": len([v for v in active_vehicles if v["location_id"] == "loc_1"]),
            "Lake Charles": len([v for v in active_vehicles if v["location_id"] == "loc_2"]),
            "Lufkin": len([v for v in active_vehicles if v["location_id"] == "loc_3"]),
            "Jasper": len([v for v in active_vehicles if v["location_id"] == "loc_4"])
        }
    }

@app.get("/api/analytics/customer-heatmap")
async def get_customer_heatmap(
    period: str = "weekly",
    location_ids: str = "",
    current_user: UserInDB = Depends(get_current_user)
):
    return {
        "heatmap_data": [],
        "period": period,
        "location_ids": location_ids.split(",") if location_ids else []
    }

@app.get("/api/dashboard/financial")
async def get_financial_dashboard(current_user: UserInDB = Depends(get_current_user)):
    total_expenses = sum(e["amount"] for e in expenses_db.values())
    
    if imported_financial_data:
        total_revenue = imported_financial_data.get("total_revenue", 0)
        daily_revenue_data = imported_financial_data.get("daily_revenue", {})
        
        from datetime import date
        today = str(date.today())
        today_revenue = daily_revenue_data.get(today, 0)
        
        recent_daily = list(daily_revenue_data.values())[-7:] if daily_revenue_data else [0]
        avg_daily = sum(recent_daily) / len(recent_daily) if recent_daily else 0
        
        monthly_revenue_data = imported_financial_data.get("monthly_revenue", {})
        recent_monthly = list(monthly_revenue_data.values())[-1:] if monthly_revenue_data else [0]
        current_monthly = recent_monthly[0] if recent_monthly else 0
        
        return {
            "daily_revenue": today_revenue,
            "daily_revenue_average": avg_daily,
            "monthly_revenue": current_monthly,
            "daily_expenses": total_expenses / 30,
            "monthly_expenses": total_expenses,
            "daily_profit": today_revenue - (total_expenses / 30),
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
            "daily_revenue": 0.00,
            "daily_revenue_average": 12500.00,
            "monthly_revenue": 375000.00,
            "daily_expenses": total_expenses / 30,
            "monthly_expenses": total_expenses,
            "daily_profit": 0.00 - (total_expenses / 30),
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

def calculate_customer_sales_by_period(customer, daily_revenue, period):
    """Calculate customer sales based on time period"""
    total_revenue = sum(daily_revenue.values()) if daily_revenue else 0
    customer_share = customer.get("total_spent", 0) / max(total_revenue, 1)
    
    if period == "daily":
        return customer_share * (total_revenue / max(len(daily_revenue), 1))
    elif period == "weekly":
        return customer_share * (total_revenue / max(len(daily_revenue) / 7, 1))
    else:  # monthly
        return customer_share * (total_revenue / max(len(daily_revenue) / 30, 1))

@app.get("/api/sales/geo-temporal")
async def get_geo_temporal_sales(
    period: str = Query(..., regex="^(daily|weekly|monthly)$"),
    location_ids: str = Query(None),
    current_user: UserInDB = Depends(get_current_user)
):
    """Returns geocoded sales data with time period filtering"""
    from datetime import datetime, timedelta
    
    locations = [location_ids] if location_ids and "," not in location_ids else (location_ids.split(",") if location_ids else None)
    
    # Get customers with coordinates
    if imported_customers and len(imported_customers) > 0:
        customers = imported_customers
    else:
        customers = list(customers_db.values())
    
    if locations:
        customers = [c for c in customers if c.get("location_id") in locations]
    
    customers = filter_by_location(customers, current_user)
    
    sales_data = []
    if imported_financial_data:
        daily_revenue = imported_financial_data.get("daily_revenue", {})
        
        for customer in customers:
            if customer.get("coordinates"):
                # Calculate sales for this customer based on period
                customer_sales = calculate_customer_sales_by_period(customer, daily_revenue, period)
                sales_data.append({
                    "customer_id": customer["id"],
                    "customer_name": customer["name"],
                    "coordinates": customer["coordinates"],
                    "sales_amount": customer_sales,
                    "location_id": customer.get("location_id")
                })
            elif customer.get("address"):
                geocoded = geocode_address(customer.get("address", ""))
                if geocoded:
                    customer_sales = calculate_customer_sales_by_period(customer, daily_revenue, period)
                    sales_data.append({
                        "customer_id": customer["id"],
                        "customer_name": customer["name"],
                        "coordinates": geocoded,
                        "sales_amount": customer_sales,
                        "location_id": customer.get("location_id")
                    })
    
    return {"sales": sales_data, "period": period}

@app.get("/api/performance/locations/{location_id}")
async def get_location_performance(
    location_id: str,
    period: str = Query("weekly", regex="^(daily|weekly|monthly|quarterly)$"),
    current_user: UserInDB = Depends(get_current_user)
):
    """Returns performance metrics for a specific location"""
    
    location = locations_db.get(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Calculate metrics
    customers = [c for c in (imported_customers or list(customers_db.values())) 
                if c.get("location_id") == location_id]
    customers = filter_by_location(customers, current_user)
    
    vehicles = [v for v in vehicles_db.values() if v.get("location_id") == location_id]
    
    location_revenue = 0
    if imported_financial_data:
        daily_revenue = imported_financial_data.get("daily_revenue", {})
        total_customers = len(imported_customers or list(customers_db.values()))
        location_revenue = sum(daily_revenue.values()) * (len(customers) / max(total_customers, 1))
    
    return {
        "location": location,
        "metrics": {
            "sales_volume": location_revenue,
            "customer_count": len(customers),
            "vehicle_count": len(vehicles),
            "efficiency": min(100, (len([v for v in vehicles if v.get("is_active")]) / max(len(vehicles), 1)) * 100)
        },
        "period": period
    }

@app.post("/api/import/excel")
async def import_excel_data(
    files: List[UploadFile] = File(...), 
    location_id: str = Form("loc_3"),
    current_user: UserInDB = Depends(get_current_user)
):
    """Import historical sales data from Excel files with location mapping"""
    global imported_customers, imported_orders, imported_financial_data
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Validate location_id
    valid_locations = ["loc_1", "loc_2", "loc_3", "loc_4"]
    if location_id not in valid_locations:
        raise HTTPException(status_code=400, detail=f"Invalid location_id. Must be one of: {valid_locations}")
    
    location_names = {
        "loc_1": "Leesville",
        "loc_2": "Lake Charles", 
        "loc_3": "Lufkin",
        "loc_4": "Jasper"
    }
    location_name = location_names[location_id]
    
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
        
        processed_data = process_excel_files(temp_files, location_id, location_name)
        
        imported_customers = processed_data["customers"]
        imported_orders = processed_data["orders"] 
        imported_financial_data = processed_data["financial_metrics"]
        
        save_data_to_disk()
        
        return {
            "success": True,
            "message": f"Excel data imported successfully for {location_name}",
            "summary": {
                "customers_imported": len(imported_customers),
                "orders_imported": len(imported_orders),
                "total_records": processed_data["total_records"],
                "date_range": processed_data["date_range"],
                "total_revenue": imported_financial_data.get("total_revenue", 0),
                "location_id": location_id,
                "location_name": location_name
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error processing Excel files: {e}")
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

@app.post("/api/import/google-sheets")
async def import_google_sheets_data(
    sheets_url: str = Form(...),
    location_id: str = Form("loc_3"),
    worksheet_name: str = Form(None),
    current_user: UserInDB = Depends(get_current_user)
):
    """Import customer data from Google Sheets with location mapping"""
    global imported_customers, imported_orders, imported_financial_data
    
    if not sheets_url:
        raise HTTPException(status_code=400, detail="Google Sheets URL is required")
    
    valid_locations = ["loc_1", "loc_2", "loc_3", "loc_4"]
    if location_id not in valid_locations:
        raise HTTPException(status_code=400, detail=f"Invalid location_id. Must be one of: {valid_locations}")
    
    location_names = {
        "loc_1": "Leesville",
        "loc_2": "Lake Charles", 
        "loc_3": "Lufkin",
        "loc_4": "Jasper"
    }
    location_name = location_names[location_id]
    
    try:
        processed_data = process_google_sheets_data(sheets_url, location_id, location_name, worksheet_name)
        
        imported_customers = processed_data["customers"]
        imported_orders = processed_data["orders"] 
        imported_financial_data = processed_data["financial_metrics"]
        
        save_data_to_disk()
        
        return {
            "success": True,
            "message": f"Google Sheets data imported successfully for {location_name}",
            "summary": {
                "customers_imported": len(imported_customers),
                "orders_imported": len(imported_orders),
                "total_records": processed_data["total_records"],
                "date_range": processed_data["date_range"],
                "total_revenue": imported_financial_data.get("total_revenue", 0),
                "location_id": location_id,
                "location_name": location_name,
                "sheets_url": sheets_url
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error processing Google Sheets data: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing Google Sheets data: {str(e)}")

@app.post("/api/customers/bulk-import")
async def bulk_import_customers_excel(
    files: List[UploadFile] = File(...), 
    location_id: str = Form("loc_3"),
    current_user: UserInDB = Depends(get_current_user)
):
    """Bulk import customers from Excel files and add to customers database"""
    global customers_db
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Validate location_id
    valid_locations = ["loc_1", "loc_2", "loc_3", "loc_4"]
    if location_id not in valid_locations:
        raise HTTPException(status_code=400, detail=f"Invalid location_id. Must be one of: {valid_locations}")
    
    if current_user.role != UserRole.MANAGER and location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Cannot import customers for different location")
    
    location_names = {
        "loc_1": "Leesville",
        "loc_2": "Lake Charles", 
        "loc_3": "Lufkin",
        "loc_4": "Jasper"
    }
    location_name = location_names[location_id]
    
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
        
        processed_data = process_customer_excel_files(temp_files, location_id, location_name)
        
        # Add customers to customers_db instead of imported_customers
        customers_imported = 0
        for customer_data in processed_data["customers"]:
            customer_id = str(uuid.uuid4())
            customer_record = {
                "id": customer_id,
                "name": customer_data["name"],
                "contact_person": customer_data.get("contact_person", ""),
                "phone": customer_data["phone"],
                "email": customer_data.get("email", ""),
                "address": customer_data["address"],
                "city": customer_data.get("city", ""),
                "state": customer_data.get("state", ""),
                "zip_code": customer_data.get("zip_code", ""),
                "location_id": location_id,
                "credit_limit": customer_data.get("credit_limit", 5000.0),
                "payment_terms": 30,
                "is_active": True
            }
            customers_db[customer_id] = customer_record
            customers_imported += 1
        
        save_data_to_disk()
        
        return {
            "success": True,
            "message": f"Customers imported successfully to {location_name}",
            "summary": {
                "customers_imported": customers_imported,
                "total_records": processed_data["total_records"],
                "location_id": location_id,
                "location_name": location_name,
                "duplicates_removed": processed_data.get("duplicates_removed", 0)
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error processing Excel files: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing Excel files: {str(e)}")
    
    finally:
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass

@app.post("/api/routes/bulk-import")
async def bulk_import_routes(
    files: List[UploadFile] = File(...),
    location_id: str = Form(...),
    current_user: UserInDB = Depends(get_current_user)
):
    """Bulk import routes from Excel files"""
    global routes_db
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Validate location_id
    valid_locations = ["loc_1", "loc_2", "loc_3", "loc_4"]
    if location_id not in valid_locations:
        raise HTTPException(status_code=400, detail=f"Invalid location_id. Must be one of: {valid_locations}")
    
    if current_user.role != UserRole.MANAGER and location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Cannot import routes for different location")
    
    location_names = {
        "loc_1": "Leesville",
        "loc_2": "Lake Charles", 
        "loc_3": "Lufkin",
        "loc_4": "Jasper"
    }
    location_name = location_names[location_id]
    
    try:
        result = process_route_excel_files(files, location_id)
        
        for route in result["routes"]:
            routes_db[route["id"]] = route
        
        save_data_to_disk()
        
        logger.info(f"Successfully imported {len(result['routes'])} routes to {location_name}")
        return {
            "message": f"Successfully imported {len(result['routes'])} routes to {location_name}",
            "routes_imported": len(result['routes']),
            "total_records": result['total_records']
        }
        
    except Exception as e:
        logger.error(f"Error in route bulk import: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/customers/bulk-import-sheets")
async def bulk_import_customers_sheets(
    sheets_url: str = Form(...),
    location_id: str = Form("loc_3"),
    worksheet_name: str = Form(None),
    current_user: UserInDB = Depends(get_current_user)
):
    """Bulk import customers from Google Sheets and add to customers database"""
    global customers_db
    
    if not sheets_url:
        raise HTTPException(status_code=400, detail="Google Sheets URL is required")
    
    # Validate location_id
    valid_locations = ["loc_1", "loc_2", "loc_3", "loc_4"]
    if location_id not in valid_locations:
        raise HTTPException(status_code=400, detail=f"Invalid location_id. Must be one of: {valid_locations}")
    
    if current_user.role != UserRole.MANAGER and location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Cannot import customers for different location")
    
    location_names = {
        "loc_1": "Leesville",
        "loc_2": "Lake Charles", 
        "loc_3": "Lufkin",
        "loc_4": "Jasper"
    }
    location_name = location_names[location_id]
    
    try:
        processed_data = process_google_sheets_data(sheets_url, location_id, location_name, worksheet_name)
        
        # Add customers to customers_db instead of imported_customers
        customers_imported = 0
        for customer_data in processed_data["customers"]:
            customer_id = str(uuid.uuid4())
            customer_record = {
                "id": customer_id,
                "name": customer_data["name"],
                "contact_person": customer_data.get("contact_person", ""),
                "phone": customer_data["phone"],
                "email": customer_data.get("email", ""),
                "address": customer_data["address"],
                "city": customer_data.get("city", ""),
                "state": customer_data.get("state", ""),
                "zip_code": customer_data.get("zip_code", ""),
                "location_id": location_id,
                "credit_limit": customer_data.get("credit_limit", 5000.0),
                "payment_terms": 30,
                "is_active": True
            }
            customers_db[customer_id] = customer_record
            customers_imported += 1
        
        save_data_to_disk()
        
        return {
            "success": True,
            "message": f"Customers imported successfully to {location_name}",
            "summary": {
                "customers_imported": customers_imported,
                "total_records": processed_data["total_records"],
                "location_id": location_id,
                "location_name": location_name,
                "sheets_url": sheets_url,
                "duplicates_removed": processed_data.get("duplicates_removed", 0)
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error processing Google Sheets: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing Google Sheets: {str(e)}")

@app.get("/api/google-sheets/test-connection")
async def test_google_sheets_connection_endpoint(current_user: UserInDB = Depends(get_current_user)):
    """Test Google Sheets API connection"""
    try:
        result = test_google_sheets_connection()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")

@app.get("/api/maintenance/work-orders")
async def get_work_orders(status: Optional[str] = None, current_user: UserInDB = Depends(get_current_user)):
    orders = list(work_orders_db.values())
    if status:
        orders = [o for o in orders if o["status"] == status]
    
    if current_user.role != UserRole.MANAGER:
        vehicle_ids = [v["id"] for v in vehicles_db.values() if v["location_id"] == current_user.location_id]
        orders = [o for o in orders if o["vehicle_id"] in vehicle_ids]
    
    return orders

@app.post("/api/maintenance/work-orders")
async def create_work_order(work_order: WorkOrderCreate, current_user: UserInDB = Depends(get_current_user)):
    vehicle = vehicles_db.get(work_order.vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if current_user.role != UserRole.MANAGER and vehicle["location_id"] != current_user.location_id:
        raise HTTPException(status_code=403, detail="Cannot create work order for vehicle in different location")
    
    vehicle_name = work_order.vehicle_name or f"{vehicle['license_plate']} ({vehicle['vehicle_type']})"
    created = WorkOrder(
        id=str(uuid.uuid4()),
        vehicle_id=work_order.vehicle_id,
        vehicle_name=vehicle_name,
        technician_name=work_order.technician_name,
        issue_description=work_order.issue_description,
        priority=work_order.priority,
        status=work_order.status,
        work_type=work_order.work_type,
        submitted_date=datetime.now(),
        estimated_cost=work_order.estimated_cost,
        estimated_hours=work_order.estimated_hours,
    )
    work_orders_db[created.id] = created.dict()
    save_data_to_disk()
    return created

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
    if current_user.role != UserRole.MANAGER:
        entries = [e for e in entries if e.get("location_id") == current_user.location_id]
    return sorted(entries, key=lambda x: x["submitted_at"], reverse=True)

@app.post("/api/production/entries")
async def create_production_entry(entry_data: ProductionEntryCreate, current_user: UserInDB = Depends(get_current_user)):
    entry = ProductionEntry(
        id=str(uuid.uuid4()),
        date=entry_data.date,
        shift=entry_data.shift,
        pallets_8lb=entry_data.pallets_8lb,
        pallets_20lb=entry_data.pallets_20lb,
        pallets_block_ice=entry_data.pallets_block_ice,
        total_pallets=entry_data.total_pallets,
        submitted_by=current_user.full_name,
        submitted_at=datetime.now(),
        location_id=current_user.location_id
    )
    entry_dict = entry.dict()
    production_entries_db[entry.id] = entry_dict
    save_data_to_disk()
    return entry

@app.get("/api/inventory/forecast/{location_id}")
async def forecast_inventory(
    location_id: str,
    days: int = 7,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Returns AI-powered demand predictions for ice production using Prophet.
    Integrates with existing production data structures.
    """
    try:
        entries = [e for e in production_entries_db.values() if e.get("location_id") == location_id]
        
        if len(entries) < 7:
            if entries:
                avg_total = sum(e.get("total_pallets", 0) for e in entries) / len(entries)
                return {
                    "location_id": location_id,
                    "forecast": [
                        {
                            "ds": (date.today() + timedelta(days=i)).isoformat(),
                            "yhat": avg_total,
                            "yhat_lower": avg_total * 0.8,
                            "yhat_upper": avg_total * 1.2
                        }
                        for i in range(1, days + 1)
                    ],
                    "reorder_point": avg_total * 1.2,
                    "method": "moving_average"
                }
            else:
                return {
                    "location_id": location_id,
                    "forecast": [
                        {
                            "ds": (date.today() + timedelta(days=i)).isoformat(),
                            "yhat": 100,
                            "yhat_lower": 80,
                            "yhat_upper": 120
                        }
                        for i in range(1, days + 1)
                    ],
                    "reorder_point": 120,
                    "method": "default"
                }
        
        df_data = []
        for entry in entries:
            entry_date = entry.get("date")
            if isinstance(entry_date, str):
                entry_date = datetime.fromisoformat(entry_date).date()
            df_data.append({
                "ds": entry_date,
                "y": entry.get("total_pallets", 0)
            })
        
        df = pd.DataFrame(df_data)
        df = df.groupby("ds")["y"].sum().reset_index()  # Aggregate by date
        df["ds"] = pd.to_datetime(df["ds"])
        
        model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=False,
            interval_width=0.8
        )
        model.fit(df)
        
        future = model.make_future_dataframe(periods=days)
        forecast = model.predict(future)
        
        future_forecast = forecast.tail(days)
        
        # Calculate reorder point using safety stock formula
        historical_demand = df["y"].values.astype(float)
        avg_demand = float(np.mean(historical_demand))
        std_demand = float(np.std(historical_demand))
        safety_stock = 1.65 * std_demand  # 95% service level
        reorder_point = max(avg_demand + safety_stock, 50)  # Minimum 50 pallets
        
        return {
            "location_id": location_id,
            "forecast": [
                {
                    "ds": row["ds"].strftime("%Y-%m-%d"),
                    "yhat": max(0, row["yhat"]),
                    "yhat_lower": max(0, row["yhat_lower"]),
                    "yhat_upper": max(0, row["yhat_upper"])
                }
                for _, row in future_forecast.iterrows()
            ],
            "reorder_point": round(reorder_point, 0),
            "method": "prophet",
            "historical_avg": round(avg_demand, 1),
            "safety_stock": round(safety_stock, 1)
        }
        
    except Exception as e:
        logger.error(f"Forecast error for location {location_id}: {str(e)}")
        avg_pallets = 100
        return {
            "location_id": location_id,
            "forecast": [
                {
                    "ds": (date.today() + timedelta(days=i)).isoformat(),
                    "yhat": avg_pallets,
                    "yhat_lower": avg_pallets * 0.8,
                    "yhat_upper": avg_pallets * 1.2
                }
                for i in range(1, days + 1)
            ],
            "reorder_point": avg_pallets * 1.2,
            "method": "fallback",
            "error": str(e)
        }

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
            elif hasattr(order_date, 'date') and order_date is not None:
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
    
    if imported_customers and len(imported_customers) > 0:
        customers = imported_customers
    else:
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
        
        try:
            customers = location_customers
            demands = [0] + [order.get('quantity', 1) for order in remaining_orders]  # Depot + order demands
            coordinates = [(31.1391, -93.2044)]  # Depot coordinates
            
            # Add customer coordinates
            for customer in customers:
                if customer.get('coordinates'):
                    coords = customer['coordinates']
                    coordinates.append((coords['lat'], coords['lng']))
                else:
                    geocoded = geocode_address(customer.get('address', ''))
                    if geocoded:
                        coordinates.append((geocoded['lat'], geocoded['lng']))
                        customers_db[customer['id']]['coordinates'] = geocoded
                        save_data_to_disk()
                    else:
                        coordinates.append((31.1391 + len(coordinates) * 0.01, -93.2044 + len(coordinates) * 0.01))
            
            if len(customers) > 1:
                optimized_order = optimize_with_ortools(customers, demands, coordinates, vehicle.get('capacity_pallets', 20))
                if optimized_order:
                    route_stops = []
                    for i, customer_idx in enumerate(optimized_order):
                        customer = customers[customer_idx]
                        order = next((o for o in remaining_orders if o['customer_id'] == customer['id']), None)
                        if order:
                            route_stops.append({
                                "id": str(uuid.uuid4()),
                                "order_id": order["id"],
                                "customer_id": customer["id"],
                                "stop_number": i + 1,
                                "estimated_arrival": (datetime.now() + timedelta(hours=i * 0.5)).isoformat(),
                                "status": "pending",
                                "customer_name": customer["name"],
                                "address": customer["address"],
                                "coordinates": coordinates[customer_idx + 1] if customer_idx + 1 < len(coordinates) else None,
                                "optimization_method": "OR-Tools"
                            })
                    print(f"DEBUG: OR-Tools generated {len(route_stops)} optimized stops for vehicle {vehicle['license_plate']}")
                else:
                    route_stops = optimize_route_ai(location_customers, remaining_orders, vehicle, depot_address)
                    print(f"DEBUG: Fallback algorithm generated {len(route_stops)} stops for vehicle {vehicle['license_plate']}")
            else:
                route_stops = optimize_route_ai(location_customers, remaining_orders, vehicle, depot_address)
                print(f"DEBUG: Single customer - generated {len(route_stops)} stops for vehicle {vehicle['license_plate']}")
        except Exception as e:
            logging.warning(f"OR-Tools optimization failed: {e}")
            route_stops = optimize_route_ai(location_customers, remaining_orders, vehicle, depot_address)
            print(f"DEBUG: Exception fallback - generated {len(route_stops)} stops for vehicle {vehicle['license_plate']}")
        
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


@app.post("/api/quickbooks/auth")
async def quickbooks_auth(auth_request: QuickBooksAuthRequest, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role not in [UserRole.MANAGER, UserRole.ACCOUNTANT]:
        raise HTTPException(status_code=403, detail="Only managers and accountants can configure QuickBooks")
    
    try:
        authorization_url, state = quickbooks_client.get_authorization_url(auth_request.state or "")
        return {
            "authorization_url": authorization_url,
            "state": state
        }
    except Exception as e:
        logger.error(f"QuickBooks auth initiation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate QuickBooks authentication")

@app.get("/api/quickbooks/callback")
async def quickbooks_callback(code: str, state: str, realmId: str):
    global quickbooks_connection
    
    try:
        authorization_response = f"http://localhost:8000/api/quickbooks/callback?code={code}&state={state}&realmId={realmId}"
        token_data = quickbooks_client.exchange_code_for_tokens(authorization_response, state)
        
        expires_at = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
        
        company_info = quickbooks_client.get_company_info(token_data["access_token"], realmId)
        company_name = company_info.get("CompanyName", "Unknown Company")
        
        quickbooks_connection = {
            "access_token": token_data["access_token"],
            "refresh_token": token_data["refresh_token"],
            "realm_id": realmId,
            "expires_at": expires_at.isoformat(),
            "is_active": True,
            "company_name": company_name,
            "last_sync": None
        }
        
        save_data_to_disk()
        
        return {
            "message": "QuickBooks connected successfully",
            "company_name": company_name,
            "realm_id": realmId
        }
    except Exception as e:
        logger.error(f"QuickBooks callback failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete QuickBooks authentication")

@app.get("/api/quickbooks/status")
async def quickbooks_status(current_user: UserInDB = Depends(get_current_user)):
    global quickbooks_connection
    
    if not quickbooks_connection or not quickbooks_connection.get("is_active"):
        return {
            "is_connected": False,
            "last_sync": None,
            "company_name": None,
            "realm_id": None
        }
    
    return {
        "is_connected": True,
        "last_sync": quickbooks_connection.get("last_sync"),
        "company_name": quickbooks_connection.get("company_name"),
        "realm_id": quickbooks_connection.get("realm_id")
    }

@app.post("/api/quickbooks/sync")
async def quickbooks_sync(sync_request: QuickBooksSyncRequest, current_user: UserInDB = Depends(get_current_user)):
    global quickbooks_connection
    
    if current_user.role not in [UserRole.MANAGER, UserRole.ACCOUNTANT]:
        raise HTTPException(status_code=403, detail="Only managers and accountants can sync QuickBooks data")
    
    if not quickbooks_connection or not quickbooks_connection.get("is_active"):
        raise HTTPException(status_code=400, detail="QuickBooks not connected")
    
    try:
        access_token = quickbooks_connection["access_token"]
        realm_id = quickbooks_connection["realm_id"]
        
        sync_results = {
            "customers_synced": 0,
            "invoices_synced": 0,
            "payments_synced": 0,
            "errors": []
        }
        
        if sync_request.sync_customers:
            try:
                if imported_customers and len(imported_customers) > 0:
                    arctic_customers = imported_customers
                else:
                    arctic_customers = list(customers_db.values())
                qb_customers = quickbooks_client.get_customers(access_token, realm_id)
                qb_customer_names = {c.get("Name", "").lower() for c in qb_customers}
                
                for customer in arctic_customers:
                    customer_name = customer.get("name", "").lower()
                    if customer_name not in qb_customer_names:
                        qb_customer_data = map_arctic_customer_to_qb(customer)
                        quickbooks_client.create_customer(access_token, realm_id, qb_customer_data)
                        sync_results["customers_synced"] += 1
                        
            except Exception as e:
                sync_results["errors"].append(f"Customer sync error: {str(e)}")
        
        if sync_request.sync_invoices:
            try:
                arctic_orders = list(orders_db.values())
                qb_customers = quickbooks_client.get_customers(access_token, realm_id)
                customer_map = {c.get("Name", "").lower(): c.get("Id") for c in qb_customers}
                
                for order in arctic_orders[:10]:
                    customer_name = order.get("customer_name", "").lower()
                    if customer_name in customer_map:
                        customer_ref = customer_map[customer_name]
                        if isinstance(customer_ref, str):
                            invoice_data = map_arctic_order_to_qb_invoice(order, customer_ref)
                        quickbooks_client.create_invoice(access_token, realm_id, invoice_data)
                        sync_results["invoices_synced"] += 1
                        
            except Exception as e:
                sync_results["errors"].append(f"Invoice sync error: {str(e)}")
        
        quickbooks_connection["last_sync"] = datetime.utcnow().isoformat()
        save_data_to_disk()
        
        return sync_results
        
    except Exception as e:
        logger.error(f"QuickBooks sync failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to sync with QuickBooks")

@app.delete("/api/quickbooks/disconnect")
async def quickbooks_disconnect(current_user: UserInDB = Depends(get_current_user)):
    global quickbooks_connection
    
    if current_user.role not in [UserRole.MANAGER, UserRole.ACCOUNTANT]:
        raise HTTPException(status_code=403, detail="Only managers and accountants can disconnect QuickBooks")
    
    quickbooks_connection = None
    save_data_to_disk()
    
    return {"message": "QuickBooks disconnected successfully"}

@app.post("/api/drivers/{driver_id}/location")
async def update_driver_location(driver_id: str, location_data: dict, current_user: UserInDB = Depends(get_current_user)):
    driver_locations[driver_id] = {
        "lat": location_data.get("lat"),
        "lng": location_data.get("lng"),
        "timestamp": location_data.get("timestamp"),
        "route_id": location_data.get("route_id"),
        "speed": location_data.get("speed", 0),
        "heading": location_data.get("heading", 0),
        "accuracy": location_data.get("accuracy", 0)
    }
    
    route_id = location_data.get("route_id")
    if route_id and route_id in routes_db:
        route = routes_db[route_id]
        current_location = {"lat": location_data.get("lat"), "lng": location_data.get("lng")}
        update_route_etas(route, current_location)
    
    return {"status": "success", "message": "Location updated"}

@app.get("/api/drivers/{driver_id}/location")
async def get_driver_location(driver_id: str, current_user: UserInDB = Depends(get_current_user)):
    if driver_id in driver_locations:
        return driver_locations[driver_id]
    return {"error": "Driver location not found"}

@app.get("/api/routes/{route_id}/progress")
async def get_route_progress(route_id: str, current_user: UserInDB = Depends(get_current_user)):
    if route_id not in routes_db:
        raise HTTPException(status_code=404, detail="Route not found")
    
    route = routes_db[route_id]
    stops = route.get("stops", [])
    
    completed_stops = len([s for s in stops if s.get("status") == "completed"])
    total_stops = len(stops)
    
    progress = {
        "route_id": route_id,
        "completed_stops": completed_stops,
        "total_stops": total_stops,
        "progress_percentage": (completed_stops / total_stops * 100) if total_stops > 0 else 0,
        "current_stop": next((s for s in stops if s.get("status") == "pending"), None),
        "estimated_completion": calculate_estimated_completion(route)
    }
    
    return progress

def update_route_etas(route, current_location):
    """
    Update ETAs for remaining stops based on current driver location
    """
    try:
        stops = route.get("stops", [])
        pending_stops = [s for s in stops if s.get("status") == "pending"]
        
        if not pending_stops:
            return
        
        import googlemaps
        gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY', ''))
        
        origins = [(current_location["lat"], current_location["lng"])]
        destinations = []
        
        for stop in pending_stops:
            if stop.get("coordinates"):
                destinations.append((stop["coordinates"]["lat"], stop["coordinates"]["lng"]))
            else:
                destinations.append(stop["address"])
        
        if destinations:
            result = gmaps.distance_matrix(
                origins=origins,
                destinations=destinations,
                mode="driving",
                departure_time="now",
                traffic_model="best_guess"
            )
            
            if result['status'] == 'OK':
                for i, stop in enumerate(pending_stops):
                    element = result['rows'][0]['elements'][i]
                    if element['status'] == 'OK':
                        duration_seconds = element['duration_in_traffic']['value']
                        eta = datetime.now() + timedelta(seconds=duration_seconds)
                        stop["estimated_arrival"] = eta.strftime("%H:%M")
                        stop["eta_updated"] = datetime.now().isoformat()
        
        save_data_to_disk()
        
    except Exception as e:
        logging.warning(f"ETA update failed: {e}")

def calculate_estimated_completion(route):
    """
    Calculate estimated route completion time
    """
    try:
        stops = route.get("stops", [])
        pending_stops = [s for s in stops if s.get("status") == "pending"]
        
        if not pending_stops:
            return datetime.now().isoformat()
        
        avg_time_per_stop = 30  # minutes
        remaining_time = len(pending_stops) * avg_time_per_stop
        
        completion_time = datetime.now() + timedelta(minutes=remaining_time)
        return completion_time.isoformat()
        
    except Exception:
        return None

@app.get("/api/training/modules")
async def get_training_modules(current_user: UserInDB = Depends(get_current_user)):
    """Get all available training modules"""
    return list(training_modules_db.values())

@app.get("/api/training/modules/{module_id}")
async def get_training_module(module_id: str, current_user: UserInDB = Depends(get_current_user)):
    """Get specific training module"""
    if module_id not in training_modules_db:
        raise HTTPException(status_code=404, detail="Training module not found")
    return training_modules_db[module_id]

@app.post("/api/training/modules/{module_id}/progress")
async def update_training_progress(
    module_id: str, 
    progress_data: dict,
    current_user: UserInDB = Depends(get_current_user)
):
    """Update employee progress on a training module"""
    employee_id = current_user.id
    progress_key = f"{employee_id}_{module_id}"
    
    employee_progress_db[progress_key] = {
        "employee_id": employee_id,
        "module_id": module_id,
        "progress": progress_data.get("progress", 0),
        "completed": progress_data.get("progress", 0) >= 100,
        "last_updated": datetime.utcnow().isoformat()
    }
    
    if progress_data.get("progress", 0) >= 100:
        cert_id = f"cert_{employee_id}_{module_id}_{int(datetime.utcnow().timestamp())}"
        module = training_modules_db.get(module_id, {})
        
        employee_certifications_db[cert_id] = {
            "id": cert_id,
            "employee_id": employee_id,
            "title": f"{module.get('title', 'Training')} Certification",
            "description": f"Blockchain-verified certification for {module.get('title', 'training')}",
            "issue_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "expiry_date": (datetime.utcnow() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "status": "active",
            "nft_id": f"AIS-{module_id.upper()}-{employee_id[-3:]}",
            "blockchain_hash": f"0x{uuid.uuid4().hex[:8]}...{uuid.uuid4().hex[-4:]}"
        }
    
    save_data_to_disk()
    return {"message": "Progress updated successfully"}

@app.get("/api/employee/certifications")
async def get_employee_certifications(current_user: UserInDB = Depends(get_current_user)):
    """Get all certifications for current employee"""
    employee_certs = [
        cert for cert in employee_certifications_db.values() 
        if cert["employee_id"] == current_user.id
    ]
    return employee_certs

@app.get("/api/employee/progress")
async def get_employee_progress(current_user: UserInDB = Depends(get_current_user)):
    """Get training progress for current employee"""
    employee_progress = [
        progress for progress in employee_progress_db.values()
        if progress["employee_id"] == current_user.id
    ]
    return {
        "overall_progress": 75,
        "completed_modules": len([p for p in employee_progress if p.get("completed")]),
        "total_modules": len(training_modules_db),
        "certifications_earned": len([c for c in employee_certifications_db.values() if c["employee_id"] == current_user.id and c["status"] == "active"]),
        "total_certifications": 4,
        "current_streak": 12,
        "total_hours": 24.5,
        "progress_details": employee_progress
    }

@app.get("/api/weather/current")
async def get_current_weather(
    lat: float, 
    lng: float,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get current weather for coordinates"""
    return await weather_service.get_current_weather(lat, lng)

@app.get("/api/weather/route-impact/{route_id}")
async def get_route_weather_impact(
    route_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get weather impact analysis for a route"""
    if route_id not in routes_db:
        raise HTTPException(status_code=404, detail="Route not found")
    
    route = routes_db[route_id]
    stops = route.get("stops", [])
    
    impact = await weather_service.get_route_weather_impact(stops)
    return impact

@app.get("/api/customers/{customer_id}/dashboard")
async def get_customer_dashboard(
    customer_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get customer dashboard data"""
    if current_user.role == UserRole.CUSTOMER and current_user.id != customer_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    customer = next((c for c in customers_db if c["id"] == customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer_orders = [o for o in orders_db if o.get("customer_id") == customer_id]
    
    total_orders = len(customer_orders)
    total_spent = sum(o.get("total_amount", 0) for o in customer_orders)
    active_orders = len([o for o in customer_orders if o.get("status") in ["pending", "confirmed", "in-production", "out-for-delivery"]])
    
    return {
        "customer": customer,
        "metrics": {
            "total_orders": total_orders,
            "total_spent": total_spent,
            "active_orders": active_orders,
            "account_balance": customer.get("account_balance", 0),
            "credit_limit": customer.get("credit_limit", 5000),
            "credit_terms": customer.get("credit_terms", "Net 30")
        },
        "recent_orders": customer_orders[-5:] if customer_orders else []
    }

@app.post("/api/customers/{customer_id}/feedback")
async def submit_customer_feedback(
    customer_id: str,
    feedback_data: dict,
    current_user: UserInDB = Depends(get_current_user)
):
    """Submit customer feedback"""
    if current_user.role == UserRole.CUSTOMER and current_user.id != customer_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    feedback_id = f"feedback_{int(datetime.utcnow().timestamp())}"
    feedback = {
        "id": feedback_id,
        "customer_id": customer_id,
        "type": feedback_data.get("type", "general"),
        "rating": feedback_data.get("rating", 5),
        "subject": feedback_data.get("subject", ""),
        "message": feedback_data.get("message", ""),
        "order_id": feedback_data.get("order_id"),
        "submitted_at": datetime.utcnow().isoformat(),
        "status": "new"
    }
    
    customer_feedback[feedback_id] = feedback
    save_data_to_disk()
    
    return {"message": "Feedback submitted successfully", "feedback_id": feedback_id}

@app.get("/api/monitoring/health")
async def get_system_health(current_user: UserInDB = Depends(get_current_user)):
    """Get overall system health status"""
    if current_user.role not in [UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Manager access required")
    
    if monitoring_service:
        return monitoring_service.get_monitoring_summary()
    else:
        return {"status": "monitoring service unavailable", "summary": {}}

@app.get("/api/monitoring/ssl-status")
async def get_ssl_status(current_user: UserInDB = Depends(get_current_user)):
    """Get SSL certificate status for all domains"""
    if current_user.role not in [UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Manager access required")
    
    if monitoring_service:
        ssl_results = []
        for domain in monitoring_service.domains_to_monitor:
            ssl_results.append(monitoring_service.check_ssl_certificate(domain))
        return {"ssl_certificates": ssl_results}
    else:
        return {"ssl_certificates": [], "status": "monitoring service unavailable"}

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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
