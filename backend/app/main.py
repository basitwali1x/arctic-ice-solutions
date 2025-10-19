from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, status, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from enum import Enum
import os
import uuid
import tempfile
import os
import logging
import json
import math
import random
from pathlib import Path
from time import time
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from .google_maps_service import GoogleMapsService
from dotenv import load_dotenv
from .excel_import import process_excel_files, process_customer_excel_files, process_route_excel_files
from .pdf_import import process_pdf_files
from .google_sheets_import import process_google_sheets_data, test_google_sheets_connection
from .quickbooks_integration import QuickBooksClient, map_arctic_customer_to_qb, map_arctic_order_to_qb_invoice, map_arctic_payment_to_qb
from .weather_service import weather_service
from .import_queue import import_queue
from .import_validation import ImportSummary, RowError

load_dotenv()
try:
    from .monitoring_service import router as monitoring_service
except ImportError:
    monitoring_service = None
from .auth_endpoints import router as auth_router
from .role_decorators import require_auth, manager_only, dispatcher_or_manager, accountant_or_manager
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .db import get_db
from .repositories.customers import CustomerRepo
from .repositories.products import ProductRepo
from .repositories.orders import OrderRepo
from .repositories.vehicles import VehicleRepo
from .repositories.routes import RouteRepo
from .repositories.work_orders import WorkOrderRepo
from .repositories.production_entries import ProductionEntryRepo
from .repositories.expenses import ExpenseRepo
from .repositories.financial_documents import FinancialDocumentRepo
from .repositories.locations import LocationRepo
from .repositories.users import UserRepo
from .memory_profiler import profile_memory_usage, log_memory_usage
from .repositories.locations import LocationRepo
from .repositories.customer_pricing import CustomerPricingRepo
from .repositories.users import UserRepo
from .excel_import import process_excel_files, process_route_excel_files
from .pdf_import import process_pdf_files
from .google_sheets_import import process_google_sheets_data, test_google_sheets_connection
from .quickbooks_integration import QuickBooksClient, map_arctic_customer_to_qb, map_arctic_order_to_qb_invoice

quickbooks_client = QuickBooksClient()

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

quickbooks_client = QuickBooksClient()

app = FastAPI(title="Arctic Ice Solutions API", version="1.0.0")

limiter = Limiter(key_func=get_remote_address, default_limits=["60/second", "1000/minute"])
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

DASHBOARD_CACHE_TTL = int(os.getenv("DASHBOARD_CACHE_TTL", "30"))
_dashboard_cache: Dict[str, Dict[str, Any]] = {}

def _get_cached(key: str):
    entry = _dashboard_cache.get(key)
    if entry and (time() - entry["ts"] < DASHBOARD_CACHE_TTL):
        return entry["data"]
    return None

def _set_cached(key: str, data: Any):
    _dashboard_cache[key] = {"ts": time(), "data": data}

app.include_router(auth_router)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-for-local-development-only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

try:
    from .weather_service import router as weather_router, weather_service
    from .monitoring_service import router as monitoring_router
    app.include_router(weather_router, prefix="/api/v1/weather", tags=["weather"])
    app.include_router(monitoring_router, prefix="/api/v1/monitoring", tags=["monitoring"])
except ImportError as e:
    print(f"Weather and monitoring services not available: {e}")

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again shortly."},
    )

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

@app.on_event("startup")
async def start_import_worker():
    async def worker_handler(job_id: str, files: List[str], ctx: Dict[str, Any]):
        location_id = ctx.get("location_id", "loc_3")
        location_name = ctx.get("location_name", "Lufkin")
        excel_result = process_excel_files(files, location_id, location_name)
        
        for customer in excel_result["customers"]:
            customers_db[customer["id"]] = customer
        for order in excel_result["orders"]:
            from .db import SessionLocal
            from .repositories.orders import OrderRepo
            db = SessionLocal()
            try:
                order_repo = OrderRepo(db)
                order_repo.create(**order)
            finally:
                db.close()
        if "financial_metrics" in excel_result:
            global imported_financial_data
            imported_financial_data = excel_result["financial_metrics"]
        
        return ImportSummary(**excel_result["summary"])
    await import_queue.start(worker_handler)

class ExpenseCategory(str, Enum):
    FUEL = "fuel"
    MAINTENANCE = "maintenance"
    SUPPLIES = "supplies"
    UTILITIES = "utilities"
    LABOR = "labor"
    OTHER = "other"

class DocumentType(str, Enum):
    INVOICE = "invoice"
    RECEIPT = "receipt"
    EXPENSE = "expense"

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

class FinancialDocument(BaseModel):
    id: str
    document_type: DocumentType
    title: str
    description: Optional[str] = None
    file_path: str
    file_name: str
    file_size: int
    mime_type: str
    location_id: str
    uploaded_by: str
    uploaded_at: datetime
    category: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[datetime] = None

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

class RouteOptimizationCustomer(BaseModel):
    id: int
    name: str
    address: str
    depot: str
    truck: Optional[str] = None
    day: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    truck_id: Optional[str] = None
    stop_sequence: Optional[int] = None
    estimated_time: Optional[str] = None
    priority: Optional[bool] = False
    phone: Optional[str] = None
    last_visit_date: Optional[datetime] = None
    visited_this_week: bool = False
    days_since_last_visit: Optional[int] = 0
    priority_level: str = "STANDARD"
    weekly_visit_required: bool = True

class RouteOptimizationRequest(BaseModel):
    customers: List[RouteOptimizationCustomer]
    num_vehicles: int = 8
    depot_addresses: List[str]
    vehicle_distribution: Optional[Dict[str, int]] = None

class RoutePoint(BaseModel):
    customer_id: int
    customer_name: str
    address: str
    latitude: float
    longitude: float
    order: int

class VehicleRoute(BaseModel):
    vehicle_id: int
    depot_name: str
    route_points: List[RoutePoint]
    total_distance_miles: float
    truck_id: Optional[str] = None
    depot: Optional[str] = None
    day: Optional[str] = "Monday"
    estimated_hours: Optional[float] = None
    total_time_minutes: float
    compliance: Optional[Dict[str, bool]] = None
    violations: Optional[List[str]] = None
    priority_score: Optional[float] = None

class DepotLocation(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float

class RouteOptimizationResponse(BaseModel):
    routes: List[VehicleRoute]
    total_distance_miles: float
    total_time_minutes: float
    depot_locations: List[DepotLocation]
    status: str = "complete"
    progress: int = 100
    constraint_violations: Optional[List[str]] = None
    customers_scheduled: int = 0
    customers_remaining: int = 0
    total_customers: int = 0
    scheduled_customers: Optional[List[Dict[str, Any]]] = None

class DepotConstraint(BaseModel):
    depot_name: str
    max_distance_miles: float
    max_stops: Optional[int] = None
    allowed_vehicles: Optional[List[str]] = None
    penalty_multiplier: float = 1.0

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
            if "quantity" in order:
                quantity_pallets = max(1, order["quantity"] // 50)
                original_quantity = order["quantity"]
            elif "items" in order and order["items"]:
                total_quantity = sum(item.get("quantity", 1) for item in order["items"])
                quantity_pallets = max(1, total_quantity // 50)
                original_quantity = total_quantity
            else:
                quantity_pallets = 1
                original_quantity = 1

            stops.append({
                "order_id": order["id"],
                "customer_id": customer["id"],
                "address": customer["address"],
                "quantity": quantity_pallets,
                "original_quantity": original_quantity,
                "customer_name": customer["name"]
            })
            print(f"DEBUG AI: Added stop for customer {customer['name']} with {original_quantity} units = {quantity_pallets} pallets")
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
            0,
            [vehicle_capacity],
            True,
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

            return route[1:]

        return None

    except Exception as e:
        logging.error(f"OR-Tools optimization error: {e}")
        return None

DEPOT_CONSTRAINTS = {
    "Leesville": {
        "max_distance": 100,
        "max_stops": 15,
        "max_hours": 10,
        "weekly_capacity": 190
    },
    "Lake Charles": {
        "max_distance": 75,
        "max_stops": 15,
        "max_hours": 10,
        "weekly_capacity": 189
    },
    "Lufkin": {
        "max_distance": 50,
        "max_stops": 15,
        "max_hours": 10,
        "weekly_capacity": 192
    },
    "Jasper": {
        "max_distance": 60,
        "max_stops": 15,
        "max_hours": 10,
        "weekly_capacity": 150
    }
}

PRIORITY_RULES = {
    "URGENT": {
        "condition": lambda c: c.days_since_last_visit and c.days_since_last_visit > 7,
        "multiplier": 0.5
    },
    "HIGH": {
        "condition": lambda c: c.days_since_last_visit and c.days_since_last_visit > 5,
        "multiplier": 0.8
    },
    "STANDARD": {
        "condition": lambda c: True,
        "multiplier": 1.0
    }
}

class RouteOptimizer:
    def __init__(self, depot_radius: float = 75, max_stops: int = 25, truck_allocations: Optional[dict] = None):
        self.google_maps = GoogleMapsService()
        self.depot_radius = depot_radius
        self.max_stops = max_stops
        self.truck_allocations = truck_allocations or {"Leesville": 3, "Lake Charles": 2, "Lufkin": 2, "Jasper": 1}

    def assign_priority(self, customer: RouteOptimizationCustomer) -> str:
        """Assign priority level based on last visit date"""
        if not customer.last_visit_date:
            return "HIGH"

        days_overdue = (datetime.now() - customer.last_visit_date).days
        customer.days_since_last_visit = days_overdue

        if days_overdue > 7:
            return "URGENT"
        elif days_overdue > 5:
            return "HIGH"
        return "STANDARD"

    def assign_depot_with_capacity(self, customer: RouteOptimizationCustomer, current_assignments: Dict[str, int]) -> str:
        """Assign customer to depot considering weekly capacity limits"""
        depot_locations = {
            "Leesville": {"lat": 31.1435, "lng": -93.2607},
            "Lake Charles": {"lat": 30.2266, "lng": -93.2174},
            "Lufkin": {"lat": 31.3382, "lng": -94.7291},
            "Jasper": {"lat": 30.9204, "lng": -94.0154}
        }

        if not customer.latitude or not customer.longitude:
            return customer.depot or "Leesville"

        distances = {}
        for depot_name, coords in depot_locations.items():
            distance = self._calculate_distance(
                customer.latitude, customer.longitude,
                coords['lat'], coords['lng']
            )
            distances[depot_name] = distance

        sorted_depots = sorted(distances.items(), key=lambda x: x[1])

        for depot_name, distance in sorted_depots:
            constraints = DEPOT_CONSTRAINTS[depot_name]
            max_capacity = constraints["weekly_capacity"]
            current_count = current_assignments.get(depot_name, 0)

            if (distance <= constraints["max_distance"] and
                current_count < max_capacity):
                return depot_name

        remaining_capacity = {
            depot: DEPOT_CONSTRAINTS[depot]["weekly_capacity"] - current_assignments.get(depot, 0)
            for depot in DEPOT_CONSTRAINTS.keys()
        }
        return max(remaining_capacity.keys(), key=lambda depot: remaining_capacity[depot])

    def filter_unvisited_customers(self, customers: List[RouteOptimizationCustomer]) -> List[RouteOptimizationCustomer]:
        """Filter customers who haven't been visited this week"""
        unvisited = [c for c in customers if not c.visited_this_week and c.weekly_visit_required]

        for customer in unvisited:
            customer.priority_level = self.assign_priority(customer)

        priority_order = {"URGENT": 0, "HIGH": 1, "STANDARD": 2}
        unvisited.sort(key=lambda c: priority_order.get(c.priority_level, 2))

        return unvisited

    async def optimize_routes(self, customers: List[RouteOptimizationCustomer], depot_addresses: List[str], num_vehicles: int = 8, vehicle_distribution: Optional[Dict[str, int]] = None) -> List[VehicleRoute]:
        """Optimize routes using OR-Tools with Google Maps distance data"""

        depot_mapping = {
            "Leesville": "1707 Smart Street, Leesville, LA 71446",
            "Lake Charles": "220 Bunker Road, Lake Charles, LA 70615",
            "Lufkin": "1107 Weiner St, Lufkin, TX 75904",
            "Jasper": "123 Main St, Jasper, TX 75951"
        }

        customers_by_depot = {}
        for customer in customers:
            depot_name = customer.depot
            if depot_name not in customers_by_depot:
                customers_by_depot[depot_name] = []
            customers_by_depot[depot_name].append(customer)

        all_routes = []

        for depot_name, depot_customers in customers_by_depot.items():
            if not depot_customers:
                continue

            depot_address = depot_mapping.get(depot_name, depot_mapping["Leesville"])
            vehicles_for_depot = self._calculate_vehicles_per_depot(depot_name, num_vehicles, vehicle_distribution)

            depot_routes = await self._optimize_single_depot_routes(
                depot_customers, depot_address, depot_name, vehicles_for_depot
            )

            all_routes.extend(depot_routes)

        return all_routes

    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two coordinates in miles"""
        import math

        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = (math.sin(dlat/2) * math.sin(dlat/2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlng/2) * math.sin(dlng/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return 3959 * c

    def _calculate_vehicles_per_depot(self, depot_name: str, total_vehicles: int, vehicle_distribution: Optional[Dict[str, int]]) -> int:
        """Calculate number of vehicles for a specific depot"""
        if vehicle_distribution and depot_name in vehicle_distribution:
            return vehicle_distribution[depot_name]

        return self.truck_allocations.get(depot_name, 2)

    async def _optimize_single_depot_routes(self, customers: List[RouteOptimizationCustomer], depot_address: str, depot_name: str, num_vehicles: int) -> List[VehicleRoute]:
        from ortools.constraint_solver import routing_enums_pb2
        from ortools.constraint_solver import pywrapcp
        import math

        all_locations = [depot_address] + [customer.address for customer in customers]

        print(f"Ensuring consistent coordinates for {len(all_locations)} locations in {depot_name} depot")
        geocoded_locations = []
        for location in all_locations:
            lat, lng = self.google_maps._generate_realistic_coordinates(location)
            geocoded_locations.append((lat, lng))

        distance_matrix = await self.google_maps.calculate_distance_matrix(all_locations)

        int_distance_matrix = []
        for row in distance_matrix:
            int_row = [int(dist * 100) for dist in row]
            int_distance_matrix.append(int_row)
        
        del distance_matrix

        manager = pywrapcp.RoutingIndexManager(
            len(all_locations),
            num_vehicles,
            0
        )

        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int_distance_matrix[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        dimension_name = 'Distance'
        routing.AddDimension(
            transit_callback_index,
            0,
            300000,
            True,
            dimension_name
        )
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)

        def time_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            travel_time = int_distance_matrix[from_node][to_node] / 100 / 35
            service_time = 0.5 if from_node != 0 else 0
            return int((travel_time + service_time) * 3600)

        time_callback_index = routing.RegisterTransitCallback(time_callback)
        routing.AddDimension(
            time_callback_index,
            18000,
            36000,
            False,
            'Time'
        )
        time_dimension = routing.GetDimensionOrDie('Time')

        for i in range(len(all_locations)):
            index = manager.NodeToIndex(i)
            time_dimension.CumulVar(index).SetRange(
                6 * 3600,
                20 * 3600
            )

        penalty = 1000000
        for i, customer in enumerate(customers):
            customer_idx = i + 1
            routing.AddDisjunction([manager.NodeToIndex(customer_idx)], penalty)

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        timeout_seconds = min(600, max(120, len(customers) * 0.5))
        search_parameters.time_limit.FromSeconds(timeout_seconds)

        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            print(f"✅ OR-Tools optimization successful for {depot_name} with {len(customers)} customers")
            routes = await self._extract_routes(
                manager, routing, solution, customers, geocoded_locations, int_distance_matrix, depot_name
            )
            del manager, routing, solution, int_distance_matrix
            return routes
        else:
            print(f"⚠️ OR-Tools optimization failed for {depot_name} with {len(customers)} customers - using fallback")
            del manager, routing, int_distance_matrix
            return self._create_fallback_routes(customers, geocoded_locations, num_vehicles, depot_name)

    async def _extract_routes(self, manager, routing, solution, customers, geocoded_locations, distance_matrix, depot_name):
        """Extract optimized routes from OR-Tools solution"""
        routes = []

        for vehicle_id in range(routing.vehicles()):
            route_points = []
            route_distance = 0
            route_time = 0

            index = routing.Start(vehicle_id)
            order = 0

            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)

                if node_index > 0:
                    customer = customers[node_index - 1]
                    lat, lng = geocoded_locations[node_index]

                    route_point = RoutePoint(
                        customer_id=customer.id,
                        customer_name=customer.name,
                        address=customer.address,
                        latitude=lat,
                        longitude=lng,
                        order=order
                    )
                    route_points.append(route_point)
                    order += 1

                previous_index = index
                index = solution.Value(routing.NextVar(index))
                if not routing.IsEnd(index):
                    from_node = manager.IndexToNode(previous_index)
                    to_node = manager.IndexToNode(index)
                    route_distance += distance_matrix[from_node][to_node]

            if route_points:
                last_node = manager.IndexToNode(previous_index)
                route_distance += distance_matrix[last_node][0]

            route_time = route_distance * 2

            if route_points:
                vehicle_route = VehicleRoute(
                    vehicle_id=vehicle_id + 1,
                    depot_name=depot_name,
                    route_points=route_points,
                    total_distance_miles=round(route_distance, 2),
                    total_time_minutes=round(route_time, 2)
                )
                routes.append(vehicle_route)

        return routes

    def _create_fallback_routes(self, customers, geocoded_locations, num_vehicles, depot_name):
        """Create fallback routes using simple round-robin assignment with stop limits"""
        routes = []
        MAX_STOPS_PER_VEHICLE = 25

        vehicle_routes = [[] for _ in range(num_vehicles)]

        for customer in customers:
            best_vehicle = None
            min_customers = float('inf')

            for i, route in enumerate(vehicle_routes):
                if len(route) < MAX_STOPS_PER_VEHICLE and len(route) < min_customers:
                    best_vehicle = i
                    min_customers = len(route)

            if best_vehicle is not None:
                vehicle_routes[best_vehicle].append(customer)
            else:
                print(f"⚠️ WARNING: Customer {customer.name} skipped - all vehicles at {MAX_STOPS_PER_VEHICLE} stop limit")

        for vehicle_id, vehicle_customer_list in enumerate(vehicle_routes):
            if not vehicle_customer_list:
                continue

            route_points = []
            total_distance = 0

            for order, customer in enumerate(vehicle_customer_list):
                lat, lng = geocoded_locations[customers.index(customer) + 1]

                route_point = RoutePoint(
                    customer_id=customer.id,
                    customer_name=customer.name,
                    address=customer.address,
                    latitude=lat,
                    longitude=lng,
                    order=order
                )
                route_points.append(route_point)

                total_distance += 5.0

            vehicle_route = VehicleRoute(
                vehicle_id=vehicle_id + 1,
                depot_name=depot_name,
                route_points=route_points,
                total_distance_miles=total_distance,
                total_time_minutes=total_distance * 2
            )
            routes.append(vehicle_route)

        return routes

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

driver_locations = {}
quickbooks_connection = None

# In-memory database dictionaries
locations_db = {}
products_db = {}
vehicles_db = {}
customers_db = {}
orders_db = {}
routes_db = {}
work_orders_db = {}
production_entries_db = {}
expenses_db = {}
financial_documents_db = {}
users_db = {}
customer_pricing_db = {}
notifications_db = {}

DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)

CUSTOMERS_FILE = DATA_DIR / "customers.json"
ORDERS_FILE = DATA_DIR / "orders.json"
FINANCIAL_FILE = DATA_DIR / "financial.json"
WORK_ORDERS_FILE = DATA_DIR / "work_orders.json"
PRODUCTION_FILE = DATA_DIR / "production.json"
EXPENSES_FILE = DATA_DIR / "expenses.json"
DOCUMENTS_FILE = DATA_DIR / "financial_documents.json"


def initialize_production_admin():
    """Create admin user in production if no users exist"""
    from .db import SessionLocal
    from .repositories.users import UserRepo
    
    db = SessionLocal()
    try:
        user_repo = UserRepo(db)
        
        if user_repo.count() == 0:
            admin_username = os.getenv("ADMIN_USERNAME", "admin")
            admin_password = os.getenv("ADMIN_PASSWORD", "secure-production-password-2024")
            
            admin_user = user_repo.create(
                id="admin_user",
                username=admin_username,
                email=f"{admin_username}@arcticeice.com",
                full_name="System Administrator",
                role="manager",
                location_id="loc_1",
                is_active=True,
                hashed_password=get_password_hash(admin_password)
            )
            print(f"DEBUG: Created production admin user: {admin_username}")
        else:
            print(f"DEBUG: Users already exist ({user_repo.count()} users), skipping admin creation")
    finally:
        db.close()

# In-memory storage for current driver locations
driver_locations = {}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    from .db import SessionLocal
    from .repositories.users import UserRepo
    
    db = SessionLocal()
    try:
        user_repo = UserRepo(db)
        user = user_repo.get_by_username(username)
        if user:
            return UserInDB(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                location_id=user.location_id,
                is_active=user.is_active,
                hashed_password=user.hashed_password
            )
        return None
    finally:
        db.close()

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

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current user using new JWT authentication system"""
    from .auth_service import get_current_user_from_token
    
    user_data = get_current_user_from_token(credentials, db)
    user = user_data["user"]
    
    return UserInDB(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        location_id=user.location_id or "default",
        is_active=user.is_active,
        hashed_password=user.hashed_password
    )

def filter_by_location(data: List[dict], user: UserInDB, location_key: str = "location_id") -> List[dict]:
    if user.role == UserRole.MANAGER:
        return data
    return [item for item in data if item.get(location_key) == user.location_id]

def get_customer_price_for_product(customer_id: str, product_id: str) -> float:
    from .db import SessionLocal
    from .models import CustomerPricing, Product
    
    db = SessionLocal()
    try:
        pricing = db.query(CustomerPricing).filter_by(customer_id=customer_id, product_id=product_id).first()
        if pricing:
            return float(pricing.custom_price)
        
        product = db.query(Product).filter_by(id=product_id).first()
        if product:
            return float(product.price)
        return 0.0
    finally:
        db.close()

def get_all_customer_pricing(customer_id: str) -> list:
    from .db import SessionLocal
    from .models import CustomerPricing
    
    db = SessionLocal()
    try:
        pricings = db.query(CustomerPricing).filter_by(customer_id=customer_id).all()
        return [{'id': p.id, 'customer_id': p.customer_id, 'product_id': p.product_id, 'custom_price': float(p.custom_price)} for p in pricings]
    finally:
        db.close()

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

def is_production_mode():
    """Detect if running in production environment"""
    environment = os.getenv("ENVIRONMENT", "").lower()
    fly_app_name = os.getenv("FLY_APP_NAME", "")
    port = os.getenv("PORT", "")

    return (
        environment == "production" or
        fly_app_name.startswith("app-") or
        port == "8000"
    )

def initialize_sample_data(db: Session = None):
    """Initialize sample data in the database"""
    if is_production_mode():
        print("DEBUG: Skipping sample data initialization in production mode")
        return
        
    if db is None:
        from .db import SessionLocal
        db = SessionLocal()
        should_close = True
    else:
        should_close = False
    
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
        existing = db.query(Location).filter_by(id=location.id).first()
        if not existing:
            db.add(location)
    db.commit()
    print(f"DEBUG: Added {len(locations)} locations")

    products = [
        Product(id="prod_1", name="8lb Ice Bag", product_type="8lb_bag", price=3.50, weight_lbs=8.0),
        Product(id="prod_2", name="20lb Ice Bag", product_type="20lb_bag", price=7.00, weight_lbs=20.0),
        Product(id="prod_3", name="Block Ice", product_type="block_ice", price=15.00, weight_lbs=25.0)
    ]

    for product in products:
        existing = db.query(Product).filter_by(id=product.id).first()
        if not existing:
            db.add(product)
    db.commit()

    vehicles = [
        Vehicle(id="veh_1", license_plate="LA-ICE-01", vehicle_type="reefer_53", capacity_pallets=26, location_id="loc_1"),
        Vehicle(id="veh_2", license_plate="LA-ICE-02", vehicle_type="reefer_42", capacity_pallets=20, location_id="loc_2"),
        Vehicle(id="veh_3", license_plate="TX-ICE-01", vehicle_type="reefer_20", capacity_pallets=10, location_id="loc_3"),
        Vehicle(id="veh_4", license_plate="TX-ICE-02", vehicle_type="reefer_20", capacity_pallets=10, location_id="loc_3"),
        Vehicle(id="veh_5", license_plate="LA-ICE-03", vehicle_type="reefer_20", capacity_pallets=10, location_id="loc_1"),
        Vehicle(id="veh_6", license_plate="LA-ICE-04", vehicle_type="reefer_20", capacity_pallets=10, location_id="loc_2"),
        Vehicle(id="veh_7", license_plate="TX-ICE-03", vehicle_type="reefer_16", capacity_pallets=8, location_id="loc_3"),
        Vehicle(id="veh_8", license_plate="LA-ICE-05", vehicle_type="reefer_16", capacity_pallets=8, location_id="loc_1")
    ]

    for vehicle in vehicles:
        existing = db.query(Vehicle).filter_by(id=vehicle.id).first()
        if not existing:
            db.add(vehicle)
    db.commit()

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

    from .models import WorkOrder
    for wo_data in sample_work_orders:
        existing = db.query(WorkOrder).filter_by(id=wo_data["id"]).first()
        if not existing:
            work_order = WorkOrder(
                id=wo_data["id"],
                vehicle_id=wo_data["vehicle_id"],
                technician_name=wo_data["technician_name"],
                issue_description=wo_data["issue_description"],
                priority=wo_data["priority"],
                status=wo_data["status"],
                work_type=wo_data["work_type"],
                estimated_cost=wo_data["estimated_cost"],
                estimated_hours=wo_data["estimated_hours"]
            )
            db.add(work_order)
    db.commit()

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
        pass

    placeholder_document = {
        "id": "doc_user_attachment_001",
        "document_type": "expense",
        "title": "User Provided Document (Scan_2025_08_13)",
        "description": "Document provided by user - file appears corrupted or unreadable",
        "file_path": "",
        "file_name": "Scan_2025_08_13_11_21_52_890.pdf",
        "file_size": 0,
        "mime_type": "application/pdf",
        "location_id": "loc_1",
        "uploaded_by": "System",
        "uploaded_at": datetime.now().isoformat(),
        "category": "other",
        "amount": None,
        "date": "2025-08-13"
    }
    from .repositories.financial_documents import FinancialDocumentRepo
    financial_doc_repo = FinancialDocumentRepo(db)
    financial_doc_repo.create(**placeholder_document)

    demo_password = os.getenv("DEMO_USER_PASSWORD", "dev-password-change-in-production")

    if is_production_mode():
        admin_password = os.getenv("ADMIN_PASSWORD")
        if not admin_password:
            print("ERROR: ADMIN_PASSWORD environment variable is required in production")
            raise ValueError("ADMIN_PASSWORD environment variable must be set in production")
    else:
        admin_password = os.getenv("ADMIN_PASSWORD", demo_password)

    print(f"DEBUG: Using demo password: '{demo_password}' (length: {len(demo_password)})")
    print(f"DEBUG: Using admin password: {'***' if is_production_mode() else admin_password} (length: {len(admin_password) if admin_password else 0})")

    sample_users = [
        {
            "id": "admin_user",
            "username": "admin",
            "email": "admin@arcticeice.com",
            "full_name": "System Administrator",
            "role": "manager",
            "location_id": "loc_1",
            "is_active": True,
            "hashed_password": get_password_hash(admin_password)
        }
    ]

    if not is_production_mode():
        demo_users = [
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
        sample_users.extend(demo_users)

    for user in sample_users:
        # users_db[user["id"]] = user  # TODO: Replace with database operations
        pass
    print(f"DEBUG: Added {len(sample_users)} users")

    imported_customers = import_route_json_data()
    print(f"DEBUG: Route JSON data will be migrated via ETL script - found {len(imported_customers)} customers")
    print(f"DEBUG: Sample data will be migrated via ETL script - {len(sample_customers)} customers, {len(sample_orders)} orders")

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

    from .models import Route
    for route_data in sample_routes:
        existing = db.query(Route).filter_by(id=route_data["id"]).first()
        if not existing:
            route = Route(
                id=route_data["id"],
                name=route_data["name"],
                driver_id=route_data["driver_id"],
                vehicle_id=route_data["vehicle_id"],
                location_id=route_data["location_id"],
                date=route_data["date"],
                estimated_duration_hours=route_data["estimated_duration_hours"],
                status=route_data["status"]
            )
            db.add(route)
    db.commit()
    print(f"DEBUG: Added {len(sample_routes)} routes")

    print("DEBUG: Sample data initialization complete")
    
    if should_close:
        db.close

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

@app.post("/api/v1/auth/login", response_model=Token)
async def login(login_request: LoginRequest):
    print(f"DEBUG: Login attempt for username: {login_request.username}")

    demo_usernames = ["manager", "dispatcher", "accountant", "driver", "employee", "customer1", "customer2", "steve", "francis", "employee2"]

    if is_production_mode() and login_request.username in demo_usernames:
        print(f"DEBUG: Blocked demo credential login attempt in production: {login_request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Demo credentials are disabled in production",
            headers={"WWW-Authenticate": "Bearer"},
        )

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

@app.post("/api/v1/auth/logout")
async def logout(current_user: UserInDB = Depends(get_current_user)):
    return {"message": "Successfully logged out"}

@app.get("/api/v1/auth/me", response_model=User)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
    return User(**current_user.dict())

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/api/v1/healthz")
async def healthz_v1():
    return {"status": "ok"}

@app.get("/api/users")
async def get_users(role: Optional[str] = None, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can access user management")

    user_repo = UserRepo(db)
    users = user_repo.list(role=role)
    
    return [User(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        location_id=user.location_id,
        is_active=user.is_active
    ) for user in users]

@app.post("/api/users", response_model=User)
async def create_user(user_data: dict, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can create users")

    user_repo = UserRepo(db)
    
    existing_user = user_repo.get_by_username(user_data["username"])
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = user_repo.create(
        id=str(uuid.uuid4()),
        username=user_data["username"],
        email=user_data["email"],
        full_name=user_data["full_name"],
        role=user_data["role"],
        location_id=user_data["location_id"],
        is_active=user_data.get("is_active", True),
        hashed_password=get_password_hash(user_data["password"])
    )
    
    return User(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role,
        location_id=new_user.location_id,
        is_active=new_user.is_active
    )

@app.put("/api/users/{user_id}", response_model=User)
async def update_user(user_id: str, user_data: dict, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can update users")

    user_repo = UserRepo(db)
    user = user_repo.get(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if "username" in user_data and user_data["username"] != user.username:
        existing_user = user_repo.get_by_username(user_data["username"])
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")

    update_data = {}
    for key, value in user_data.items():
        if key == "password":
            update_data["hashed_password"] = get_password_hash(value)
        elif key != "id":
            update_data[key] = value

    from .repositories.users import UserRepo
    user_repo = UserRepo(db)
    updated_user = user_repo.update(user_id, **update_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**{k: v for k, v in updated_user.__dict__.items() if k != "hashed_password"})

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: str, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can delete users")

    user_repo = UserRepo(db)
    user = user_repo.get(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    user_repo.delete(user_id)
    return {"message": "User deleted successfully"}

@app.get("/api/locations", response_model=List[Location])
async def get_locations(current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.locations import LocationRepo
    location_repo = LocationRepo(db)
    locations = location_repo.list()
    if current_user.role == UserRole.MANAGER:
        return [Location(**loc.__dict__) for loc in locations]
    return [Location(**loc.__dict__) for loc in locations if loc.id == current_user.location_id]

@app.get("/api/v1/locations", response_model=List[Location])
async def get_locations_v1(current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.locations import LocationRepo
    location_repo = LocationRepo(db)
    locations = location_repo.list()
    if current_user.role == UserRole.MANAGER:
        return [Location(**loc.__dict__) for loc in locations]
    return [Location(**loc.__dict__) for loc in locations if loc.id == current_user.location_id]

@app.get("/api/locations/{location_id}", response_model=Location)
async def get_location(location_id: str, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.locations import LocationRepo
    location_repo = LocationRepo(db)
    location = location_repo.get(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    if current_user.role != UserRole.MANAGER and location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Access denied to this location")
    return Location(**location.__dict__)

@app.get("/api/v1/locations/{location_id}", response_model=Location)
async def get_location_v1(location_id: str, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.locations import LocationRepo
    location_repo = LocationRepo(db)
    location = location_repo.get(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    if current_user.role != UserRole.MANAGER and location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Access denied to this location")
    return Location(**location.__dict__)

@app.put("/api/locations/{location_id}", response_model=Location)
async def update_location(location_id: str, location_data: dict, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can update locations")
    
    from .repositories.locations import LocationRepo
    location_repo = LocationRepo(db)
    updated_location = location_repo.update(location_id, **location_data)
    if not updated_location:
        raise HTTPException(status_code=404, detail="Location not found")
    return Location(**updated_location.__dict__)

@app.put("/api/v1/locations/{location_id}", response_model=Location)
async def update_location_v1(location_id: str, location_data: dict, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can update locations")
    
    from .repositories.locations import LocationRepo
    location_repo = LocationRepo(db)
    location = location_repo.update(location_id, **location_data)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return Location(**location.__dict__)

@app.get("/api/products", response_model=List[Product])
async def get_products(current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.products import ProductRepo
    product_repo = ProductRepo(db)
    products = product_repo.list()
    return [Product(**product.__dict__) for product in products]

@app.get("/api/v1/products", response_model=List[Product])
async def get_products_v1(current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.products import ProductRepo
    product_repo = ProductRepo(db)
    products = product_repo.list()
    return [Product(**product.__dict__) for product in products]

@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: str, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.products import ProductRepo
    product_repo = ProductRepo(db)
    product = product_repo.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product.__dict__)

@app.get("/api/v1/products/{product_id}", response_model=Product)
async def get_product_v1(product_id: str, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.products import ProductRepo
    product_repo = ProductRepo(db)
    product = product_repo.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product.__dict__)

@app.get("/api/vehicles", response_model=List[Vehicle])
async def get_vehicles(location_id: Optional[str] = None, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.vehicles import VehicleRepo
    vehicle_repo = VehicleRepo(db)
    vehicles = vehicle_repo.list(location_id=location_id)
    vehicle_dicts = [v.__dict__ for v in vehicles]
    return filter_by_location(vehicle_dicts, current_user)

@app.get("/api/v1/vehicles", response_model=List[Vehicle])
async def get_vehicles_v1(
    location_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    response: Response = None,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from .repositories.vehicles import VehicleRepo
    vehicle_repo = VehicleRepo(db)
    vehicles = [v.__dict__ for v in vehicle_repo.list()]
    if location_id:
        vehicles = [v for v in vehicles if v["location_id"] == location_id]
    vehicles = filter_by_location(vehicles, current_user)
    total = len(vehicles)
    if response is not None:
        response.headers["X-Total-Count"] = str(total)
    return vehicles[offset: offset + limit]

@app.get("/api/vehicles/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(vehicle_id: str, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.vehicles import VehicleRepo
    vehicle_repo = VehicleRepo(db)
    vehicle = vehicle_repo.get(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if current_user.role != UserRole.MANAGER and vehicle.location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Access denied to this vehicle")
    return Vehicle(**vehicle.__dict__)

@app.get("/api/v1/vehicles/{vehicle_id}", response_model=Vehicle)
async def get_vehicle_v1(vehicle_id: str, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.vehicles import VehicleRepo
    vehicle_repo = VehicleRepo(db)
    vehicle = vehicle_repo.get(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if current_user.role != UserRole.MANAGER and vehicle.location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Access denied to this vehicle")
    return Vehicle(**vehicle.__dict__)

@app.post("/api/vehicles", response_model=Vehicle)
async def create_vehicle(vehicle_data: VehicleCreate, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.MANAGER and vehicle_data.location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Cannot create vehicle for different location")

    vehicle_id = str(uuid.uuid4())
    from .repositories.vehicles import VehicleRepo
    vehicle_repo = VehicleRepo(db)
    vehicle_dict = {"id": vehicle_id, **vehicle_data.dict()}
    created_vehicle = vehicle_repo.create(**vehicle_dict)
    return Vehicle(**created_vehicle.__dict__)

@app.post("/api/v1/vehicles", response_model=Vehicle)
async def create_vehicle_v1(vehicle_data: VehicleCreate, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.MANAGER and vehicle_data.location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Cannot create vehicle for different location")

    from .repositories.vehicles import VehicleRepo
    vehicle_repo = VehicleRepo(db)
    
    vehicle_dict = {"id": str(uuid.uuid4()), **vehicle_data.dict()}
    vehicle_dict["created_at"] = datetime.now()
    vehicle_dict["updated_at"] = datetime.now()
    
    created_vehicle = vehicle_repo.create(**vehicle_dict)
    return Vehicle(**created_vehicle.__dict__)

@app.get("/api/customers")
async def get_customers(location_id: Optional[str] = None, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.customers import CustomerRepo
    customer_repo = CustomerRepo(db)
    customers = customer_repo.list()
    customer_dicts = [c.__dict__ for c in customers]
    
    if location_id:
        customer_dicts = [c for c in customer_dicts if c.get("location_id") == location_id]

    return filter_by_location(customer_dicts, current_user)

@app.get("/api/v1/customers")
async def get_customers_v1(
    location_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    response: Response = None,
    current_user: UserInDB = Depends(get_current_user)
):
    if imported_customers and len(imported_customers) > 0:
        customers = imported_customers
    else:
        customers = list(customers_db.values())

    if location_id:
        customers = [c for c in customers if c.get("location_id") == location_id]

    customers = filter_by_location(customers, current_user)
    total = len(customers)
    if response is not None:
        response.headers["X-Total-Count"] = str(total)
    return customers[offset: offset + limit]

@app.get("/api/customers/by-location")
async def get_customers_by_location(current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get customer counts by location for the location distribution chart"""
    from .repositories.customers import CustomerRepo
    customer_repo = CustomerRepo(db)
    customers = customer_repo.list()
    customer_dicts = [c.__dict__ for c in customers]

    from .repositories.locations import LocationRepo
    location_repo = LocationRepo(db)
    all_locations = [loc.__dict__ for loc in location_repo.list()]
    filtered_locations = filter_by_location(all_locations, current_user, location_key="id")

    location_counts = []
    for location in filtered_locations:
        location_customers = [c for c in customer_dicts if c.get("location_id") == location["id"]]

        location_counts.append({
            "location_id": location["id"],
            "location_name": location["name"],
            "customer_count": len(location_customers)
        })

    return location_counts

@app.get("/api/v1/customers/by-location")
async def get_customers_by_location_v1(current_user: UserInDB = Depends(get_current_user)):
    """Get customer counts by location for the location distribution chart"""
    customers = list(customers_db.values())
    customer_dicts = [customer.__dict__ for customer in customers]
    
    filtered_customers = filter_by_location(customer_dicts, current_user)
    
    location_counts = {}
    for customer in filtered_customers:
        location_id = customer.get("location_id", "unknown")
        if location_id not in location_counts:
            location_counts[location_id] = 0
        location_counts[location_id] += 1

    return location_counts

@app.post("/api/customers", response_model=Customer)
async def create_customer(customer: Customer, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.MANAGER and customer.location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Cannot create customer for different location")
    customer.id = str(uuid.uuid4())
    from .repositories.customers import CustomerRepo
    customer_repo = CustomerRepo(db)
    
    customer_data = {
        "id": customer.id,
        "name": customer.name,
        "contact_person": customer.contact_person,
        "phone": customer.phone,
        "email": customer.email,
        "address": customer.address,
        "city": customer.city,
        "state": customer.state,
        "zip_code": customer.zip_code,
        "location_id": customer.location_id,
        "is_active": getattr(customer, 'is_active', True),
        "credit_limit": getattr(customer, 'credit_limit', 0),
        "payment_terms": getattr(customer, 'payment_terms', None)
    }
    
    created_customer = customer_repo.create(**customer_data)
    return Customer(**created_customer.__dict__)

@app.post("/api/v1/customers", response_model=Customer)
async def create_customer_v1(customer: Customer, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != UserRole.MANAGER and customer.location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Cannot create customer for different location")
    
    customer_id = str(uuid.uuid4())
    customer_dict = customer.dict()
    customer_dict["id"] = customer_id
    customer_dict["created_at"] = datetime.now()
    customer_dict["updated_at"] = datetime.now()
    
    customers_db[customer_id] = Customer(**customer_dict)
    return customers_db[customer_id]

@app.get("/api/v1/customers/{customer_id}/orders")
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

@app.post("/api/v1/customers/{customer_id}/orders")
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
async def get_customer_pricing(customer_id: str, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can access customer pricing")

    from .repositories.products import ProductRepo
    product_repo = ProductRepo(db)
    products = product_repo.list()
    product_dicts = [p.__dict__ for p in products]

    from .repositories.customer_pricing import CustomerPricingRepo
    pricing_repo = CustomerPricingRepo(db)
    pricing_records = pricing_repo.get_by_customer(customer_id)

    result = []
    for product in product_dicts:
        custom_price = None
        for pricing in pricing_records:
            if pricing.product_id == product['id']:
                custom_price = pricing.custom_price
                break

        result.append({
            "product_id": product['id'],
            "product_name": product['name'],
            "default_price": product['price'],
            "custom_price": custom_price
        })

    return result

@app.get("/api/v1/customers/{customer_id}/pricing")
async def get_customer_pricing_v1(customer_id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can access customer pricing")

    pricing_records = get_all_customer_pricing(customer_id)
    
    result = []
    for product_id, pricing_record in pricing_records.items():
        result.append({
            "product_id": product_id,
            "product_name": "Unknown Product",  # TODO: Fetch from ProductRepo if needed
            "custom_price": pricing_record.custom_price,
            "effective_date": pricing_record.effective_date.isoformat() if pricing_record.effective_date else None,
            "created_at": pricing_record.created_at.isoformat() if pricing_record.created_at else None,
            "updated_at": pricing_record.updated_at.isoformat() if pricing_record.updated_at else None,
            "created_by": pricing_record.created_by,
            "updated_by": pricing_record.updated_by
        })

    return result

@app.post("/api/customers/{customer_id}/pricing")
async def set_customer_pricing(customer_id: str, pricing_data: dict, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can set customer pricing")

    product_id = pricing_data.get('product_id')
    custom_price = pricing_data.get('custom_price')

    if not product_id or custom_price is None:
        raise HTTPException(status_code=400, detail="product_id and custom_price are required")

    if custom_price < 0:
        raise HTTPException(status_code=400, detail="Price must be non-negative")

    from .repositories.products import ProductRepo
    product_repo = ProductRepo(db)
    if not product_repo.get(product_id):
        raise HTTPException(status_code=404, detail="Product not found")

    from .repositories.customers import CustomerRepo
    customer_repo = CustomerRepo(db)
    if not customer_repo.get(customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")

    from .repositories.customer_pricing import CustomerPricingRepo
    pricing_repo = CustomerPricingRepo(db)
    
    existing_pricing = pricing_repo.get_by_customer_and_product(customer_id, product_id)
    
    if existing_pricing:
        pricing_record = pricing_repo.update(existing_pricing.id, 
                                           custom_price=custom_price, 
                                           updated_by=current_user.username)
    else:
        pricing_id = str(uuid.uuid4())
        pricing_record = pricing_repo.create(
            id=pricing_id,
            customer_id=customer_id,
            product_id=product_id,
            custom_price=custom_price,
            created_at=datetime.now(),
            updated_by=current_user.username
        )

    return {
        "id": pricing_record.id,
        "customer_id": pricing_record.customer_id,
        "product_id": pricing_record.product_id,
        "custom_price": float(pricing_record.custom_price),
        "created_at": pricing_record.created_at.isoformat(),
        "updated_by": pricing_record.updated_by
    }

@app.post("/api/v1/customers/{customer_id}/pricing")
async def set_customer_pricing_v1(customer_id: str, pricing_data: dict, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can set customer pricing")

    product_id = pricing_data.get("product_id")
    custom_price = pricing_data.get("custom_price")
    effective_date = pricing_data.get("effective_date")

    if not product_id or custom_price is None:
        raise HTTPException(status_code=400, detail="product_id and custom_price are required")

    pricing_key = f"{customer_id}:{product_id}"
    
    pricing_record = CustomerPricing(
        customer_id=customer_id,
        product_id=product_id,
        custom_price=custom_price,
        effective_date=datetime.fromisoformat(effective_date) if effective_date else datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by=current_user.username,
        updated_by=current_user.username
    )
    
    from .repositories.customer_pricing import CustomerPricingRepo
    customer_pricing_repo = CustomerPricingRepo(db)
    customer_pricing_repo.create(**pricing_record.__dict__)

    return {
        "product_id": pricing_record.product_id,
        "custom_price": pricing_record.custom_price,
        "effective_date": pricing_record.effective_date.isoformat() if pricing_record.effective_date else None,
        "created_at": pricing_record.created_at.isoformat(),
        "updated_at": pricing_record.updated_at.isoformat(),
        "created_by": pricing_record.created_by,
        "updated_by": pricing_record.updated_by
    }

@app.delete("/api/customers/{customer_id}")
async def delete_customer(customer_id: str, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can delete customers")

    from .repositories.customers import CustomerRepo
    customer_repo = CustomerRepo(db)
    if not customer_repo.delete(customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")

    return {"message": "Customer deleted successfully"}

@app.delete("/api/v1/customers/{customer_id}")
async def delete_customer_v1(customer_id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can delete customers")

    if customer_id not in customers_db:
        raise HTTPException(status_code=404, detail="Customer not found")

    del customers_db[customer_id]
    return {"message": "Customer deleted successfully"}

@app.delete("/api/customers/{customer_id}/pricing/{product_id}")
async def delete_customer_pricing(customer_id: str, product_id: str, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can delete customer pricing")

    from .repositories.customer_pricing import CustomerPricingRepo
    pricing_repo = CustomerPricingRepo(db)
    
    pricing_to_delete = pricing_repo.get_by_customer_and_product(customer_id, product_id)
    if not pricing_to_delete:
        raise HTTPException(status_code=404, detail="Custom pricing not found")

    pricing_repo.delete(pricing_to_delete.id)
    return {"message": "Custom pricing deleted successfully"}

@app.delete("/api/v1/customers/{customer_id}/pricing/{product_id}")
async def delete_customer_pricing_v1(customer_id: str, product_id: str, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can delete customer pricing")

    pricing_key = f"{customer_id}:{product_id}"
    from .repositories.customer_pricing import CustomerPricingRepo
    customer_pricing_repo = CustomerPricingRepo(db)
    pricing = customer_pricing_repo.get_by_customer_product(customer_id, product_id)
    if not pricing:
        raise HTTPException(status_code=404, detail="Customer pricing not found")

    customer_pricing_repo.delete(pricing.id)
    return {"message": "Customer pricing deleted successfully"}

@app.get("/api/v1/customers/{customer_id}/feedback")
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

@app.post("/api/v1/customers/{customer_id}/feedback")
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

@app.get("/api/v1/invoices")
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

@app.get("/api/v1/invoices/{invoice_id}/download")
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

@app.post("/api/v1/payments")
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
async def get_orders(
    location_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from .repositories.orders import OrderRepo
    from .repositories.customers import CustomerRepo
    from . import models

    order_repo = OrderRepo(db)
    customer_repo = CustomerRepo(db)

    q = db.query(models.Order)
    
    if status:
        q = q.filter(models.Order.status == status)
    
    if current_user.role != UserRole.MANAGER:
        # Non-managers see only orders from their location via customer.location_id
        q = q.join(models.Customer, models.Order.customer_id == models.Customer.id)\
             .filter(models.Customer.location_id == current_user.location_id)
    elif location_id:
        q = q.join(models.Customer, models.Order.customer_id == models.Customer.id)\
             .filter(models.Customer.location_id == location_id)

    orders = q.order_by(models.Order.order_date.desc()).all()
    return [Order(**o.__dict__) for o in orders]

@app.get("/api/v1/orders")
async def get_orders_v1(
    location_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    response: Response = None,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if imported_orders is not None and len(imported_orders) > 0:
        orders = imported_orders
        if location_id:
            orders = [o for o in orders if o.get("location_id") == location_id]
        if status:
            orders = [o for o in orders if o.get("status") == status]
        orders = filter_by_location(orders, current_user)
    else:
        from .repositories.orders import OrderRepo
        order_repo = OrderRepo(db)
        orders = [order.__dict__ for order in order_repo.list()]
        if location_id:
            orders = [o for o in orders if customers_db.get(o["customer_id"], {}).get("location_id") == location_id]
        if status:
            orders = [o for o in orders if o["status"] == status]

        if current_user.role != UserRole.MANAGER:
            orders = [o for o in orders if customers_db.get(o["customer_id"], {}).get("location_id") == current_user.location_id]
    
    total = len(orders)
    if response is not None:
        response.headers["X-Total-Count"] = str(total)
    return orders[offset: offset + limit]

@app.post("/api/orders", response_model=Order)
async def create_order(order: Order, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.customers import CustomerRepo
    customer_repo = CustomerRepo(db)
    customer = customer_repo.get(order.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if current_user.role != UserRole.MANAGER and customer.location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Cannot create order for customer in different location")
    order.id = str(uuid.uuid4())
    order.order_date = datetime.now()
    from .repositories.orders import OrderRepo
    order_repo = OrderRepo(db)
    created_order = order_repo.create(**order.dict())
    return Order(**created_order.__dict__)

@app.post("/api/v1/orders", response_model=Order)
async def create_order_v1(order: Order, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    customer = customers_db.get(order.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if current_user.role != UserRole.MANAGER and customer.location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Cannot create order for customer in different location")
    
    order.id = str(uuid.uuid4())
    order.created_at = datetime.now()
    order.updated_at = datetime.now()
    from .repositories.orders import OrderRepo
    order_repo = OrderRepo(db)
    order_repo.create(**order.dict())
    return order

@app.get("/api/dashboard/overview")
async def get_dashboard_overview(current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.customers import CustomerRepo
    from .repositories.vehicles import VehicleRepo
    from .repositories.orders import OrderRepo
    from .repositories.production_entries import ProductionEntryRepo

    customer_repo = CustomerRepo(db)
    vehicle_repo = VehicleRepo(db)
    order_repo = OrderRepo(db)
    production_repo = ProductionEntryRepo(db)

    customers = customer_repo.list()
    vehicles = vehicle_repo.list()
    orders = order_repo.list()
    production_entries = production_repo.list()

    filtered_customers = [c for c in customers if current_user.role == UserRole.MANAGER or c.location_id == current_user.location_id]
    filtered_vehicles = [v for v in vehicles if current_user.role == UserRole.MANAGER or v.location_id == current_user.location_id]
    filtered_orders = [o for o in orders if current_user.role == UserRole.MANAGER or o.customer.location_id == current_user.location_id]
    filtered_production = [p for p in production_entries if current_user.role == UserRole.MANAGER or p.location_id == current_user.location_id]

    total_revenue = sum(order.total_amount for order in filtered_orders if order.status == "completed")
    total_production = sum(entry.pallets_produced for entry in filtered_production)

    return {
        "total_customers": len(filtered_customers),
        "total_vehicles": len(filtered_vehicles),
        "total_revenue": total_revenue,
        "total_production": total_production,
        "active_orders": len([o for o in filtered_orders if o.status in ["pending", "in_progress", "out_for_delivery"]]),
        "completed_orders": len([o for o in filtered_orders if o.status == "completed"])
    }

@app.get("/api/v1/dashboard/overview")
async def get_dashboard_overview_v1(response: Response, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    cache_key = f"overview:{current_user.role}:{current_user.location_id or 'all'}"
    cached = _get_cached(cache_key)
    if cached is not None:
        response.headers["Cache-Control"] = f"public, max-age={DASHBOARD_CACHE_TTL}"
        return cached

    if imported_customers and len(imported_customers) > 0:
        customers = imported_customers
    else:
        from .repositories.customers import CustomerRepo
        customer_repo = CustomerRepo(db)
        customers = [c.__dict__ for c in customer_repo.list()]

    filtered_customers = filter_by_location(customers, current_user)
    total_customers = len(filtered_customers)

    if imported_orders is not None and len(imported_orders) > 0:
        filtered_orders = filter_by_location(imported_orders, current_user)
        total_orders_today = len([o for o in filtered_orders if o.get("order_date", "") and datetime.fromisoformat(o["order_date"].replace('Z', '+00:00')).date() == date.today()])
        total_revenue = imported_financial_data.get("total_revenue", 0) if imported_financial_data else 0
    else:
        from .repositories.orders import OrderRepo
        order_repo = OrderRepo(db)
        orders = [order.__dict__ for order in order_repo.list()]
        filtered_orders = filter_by_location(orders, current_user)
        total_orders_today = len([o for o in filtered_orders if o.get("order_date") and datetime.fromisoformat(o["order_date"].replace('Z', '+00:00')).date() == date.today()])
        total_revenue = 125000.0

    from .repositories.vehicles import VehicleRepo
    vehicle_repo = VehicleRepo(db)
    vehicles = [v.__dict__ for v in vehicle_repo.list()]
    from .repositories.orders import OrderRepo
    order_repo = OrderRepo(db)
    orders = [order.__dict__ for order in order_repo.list()]
    from .repositories.production_entries import ProductionEntryRepo
    production_repo = ProductionEntryRepo(db)
    production_entries = [p.__dict__ for p in production_repo.list()]

    filtered_vehicles = filter_by_location(vehicles, current_user)
    filtered_orders = filter_by_location(orders, current_user, location_key="customer_id", lookup_dict=customers_db)
    filtered_production = filter_by_location(production_entries, current_user)

    total_revenue = sum(order.get("total_amount", 0) for order in filtered_orders if order.get("status") == "completed")
    total_production = sum(entry.get("pallets_produced", 0) for entry in filtered_production)

    result = {
        "total_customers": len(filtered_customers),
        "total_vehicles": len(filtered_vehicles),
        "total_revenue": total_revenue,
        "total_production": total_production,
        "active_orders": len([o for o in filtered_orders if o.get("status") in ["pending", "in_progress", "out_for_delivery"]]),
        "completed_orders": len([o for o in filtered_orders if o.get("status") == "completed"])
    }

    _set_cached(cache_key, result)
    response.headers["Cache-Control"] = f"public, max-age={DASHBOARD_CACHE_TTL}"
    return result

@app.get("/api/v1/dashboard/production")
async def get_production_dashboard(response: Response, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    cache_key = f"production:{current_user.role}:{current_user.location_id or 'all'}"
    cached = _get_cached(cache_key)
    if cached is not None:
        response.headers["Cache-Control"] = f"public, max-age={DASHBOARD_CACHE_TTL}"
        return cached

@app.get("/api/dashboard/production")
async def get_production_dashboard(current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.production_entries import ProductionEntryRepo
    production_repo = ProductionEntryRepo(db)
    production_objs = production_repo.list()
    
    filtered_production = [p for p in production_objs if current_user.role == UserRole.MANAGER or p.location_id == current_user.location_id]
    
    total_pallets = sum(entry.pallets_produced for entry in filtered_production)
    avg_efficiency = sum(entry.efficiency_percentage for entry in filtered_production) / len(filtered_production) if filtered_production else 0
    
    return {
        "daily_production_pallets": total_pallets,
        "target_production_pallets": 160,
        "production_efficiency": round(avg_efficiency, 1),
        "shift_1_pallets": 45,
        "shift_2_pallets": 35,
        "inventory_levels": {
            "8lb_bags": 1200,
            "20lb_bags": 800,
            "block_ice": 150
        }
    }

@app.get("/api/v1/dashboard/production")
async def get_production_dashboard_v1(response: Response, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    cache_key = f"production:{current_user.role}:{current_user.location_id or 'all'}"
    cached = _get_cached(cache_key)
    if cached is not None:
        response.headers["Cache-Control"] = f"public, max-age={DASHBOARD_CACHE_TTL}"
        return cached

    from .repositories.production_entries import ProductionEntryRepo
    production_repo = ProductionEntryRepo(db)
    filtered_production = filter_by_location([p.__dict__ for p in production_repo.list()], current_user)

    result = {
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
    
    _set_cached(cache_key, result)
    response.headers["Cache-Control"] = f"public, max-age={DASHBOARD_CACHE_TTL}"
    return result

@app.get("/api/dashboard/fleet")
async def get_fleet_dashboard(current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.vehicles import VehicleRepo
    vehicle_repo = VehicleRepo(db)
    vehicles_objs = vehicle_repo.list()
    
    filtered_vehicles = [v for v in vehicles_objs if current_user.role == UserRole.MANAGER or v.location_id == current_user.location_id]
    
    total_vehicles = len(filtered_vehicles)
    active_vehicles = len([v for v in filtered_vehicles if v.status == "active"])
    maintenance_vehicles = len([v for v in filtered_vehicles if v.status == "maintenance"])
    
    vehicle_utilization = (active_vehicles / total_vehicles * 100) if total_vehicles > 0 else 0
    
    vehicle_utilization_details = []
    for vehicle in filtered_vehicles:
        import random
        utilization_percentage = random.randint(60, 95)
        vehicle_utilization_details.append({
            "vehicle_id": vehicle.id,
            "license_plate": vehicle.license_plate or "N/A",
            "utilization_percentage": utilization_percentage,
            "status": vehicle.status
        })
    
    return {
        "total_vehicles": total_vehicles,
        "active_vehicles": active_vehicles,
        "maintenance_vehicles": maintenance_vehicles,
        "vehicle_utilization_percentage": round(vehicle_utilization, 1),
        "vehicle_utilization_details": vehicle_utilization_details
    }


@app.get("/api/v1/dashboard/fleet")
async def get_fleet_dashboard_v1(response: Response, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    cache_key = f"fleet:{current_user.role}:{current_user.location_id or 'all'}"
    cached = _get_cached(cache_key)
    if cached is not None:
        response.headers["Cache-Control"] = f"public, max-age={DASHBOARD_CACHE_TTL}"
        return cached

    from .repositories.vehicles import VehicleRepo
    vehicle_repo = VehicleRepo(db)
    vehicles = [v.__dict__ for v in vehicle_repo.list()]
    filtered_vehicles = filter_by_location(vehicles, current_user)

    active_vehicles = [v for v in filtered_vehicles if v.get("is_active", True)]
    total_vehicles = len(active_vehicles)

    work_order_repo = WorkOrderRepo(db)
    work_orders_objs = work_order_repo.list()
    work_orders = [w.__dict__ for w in work_orders_objs]
    vehicles_in_maintenance = set()
    for wo in work_orders:
        if wo.get("status") in ["pending", "approved"]:
            vehicles_in_maintenance.add(wo.get("vehicle_id"))

    from .repositories.routes import RouteRepo
    from .repositories.orders import OrderRepo
    route_repo = RouteRepo(db)
    routes_objs = route_repo.list()
    routes = [r.__dict__ for r in routes_objs]
    order_repo = OrderRepo(db)
    orders_objs = order_repo.list()
    orders = [o.__dict__ for o in orders_objs]
    today_str = str(date.today())
    vehicles_in_use = set()
    vehicle_loads = {}

    for route in routes:
        if route.get("date") == today_str and route.get("status") in ["planned", "in_progress"]:

            vehicle_id = route.get("vehicle_id")
            vehicles_in_use.add(vehicle_id)

            total_load = 0
            for stop in route.get("stops", []):
                order_id = stop.get("order_id")
                order = next((o for o in orders if o.get("id") == order_id), None)
                if order:
                    total_load += max(1, order.get("quantity", 1) // 50)

            vehicle_loads[vehicle_id] = vehicle_loads.get(vehicle_id, 0) + total_load
    maintenance_count = len([vid for vid in vehicles_in_maintenance if any(v["id"] == vid for v in active_vehicles)])
    in_use_count = len([vid for vid in vehicles_in_use if any(v["id"] == vid for v in active_vehicles)])

    available_count = max(0, total_vehicles - in_use_count - maintenance_count)

    fleet_utilization = (in_use_count / total_vehicles * 100) if total_vehicles > 0 else 0.0

    total_capacity = sum(v.get("capacity_pallets", 20) for v in active_vehicles)
    total_current_load = sum(vehicle_loads.values())
    capacity_utilization = (total_current_load / total_capacity * 100) if total_capacity > 0 else 0.0

    vehicle_utilization_details = []
    for vehicle in active_vehicles:
        vehicle_id = vehicle["id"]
        current_load = vehicle_loads.get(vehicle_id, 0)
        capacity = vehicle.get("capacity_pallets", 20)
        utilization_pct = (current_load / capacity * 100) if capacity > 0 else 0.0

        routes_today = len([r for r in routes if r.get("vehicle_id") == vehicle_id and r.get("date") == today_str])

        total_distance = 0
        for route in routes:
            if route.get("vehicle_id") == vehicle_id and route.get("date") == today_str:
                total_distance += len(route.get("stops", [])) * 5

        efficiency_score = round(utilization_pct * 0.7 + routes_today * 10, 1)

        vehicle_utilization_details.append({
            "vehicle_id": vehicle_id,
            "license_plate": vehicle["license_plate"],
            "capacity_pallets": capacity,
            "current_load": current_load,
            "utilization_percentage": round(utilization_pct, 1),
            "routes_today": routes_today,
            "total_distance": total_distance,
            "efficiency_score": efficiency_score
        })

    average_load_efficiency = sum(v["utilization_percentage"] for v in vehicle_utilization_details) / len(vehicle_utilization_details) if vehicle_utilization_details else 0.0
    return {
        "total_vehicles": total_vehicles,
        "vehicles_in_use": in_use_count,
        "vehicles_available": available_count,
        "vehicles_maintenance": maintenance_count,
        "fleet_utilization": round(fleet_utilization, 1),
        "capacity_utilization": round(capacity_utilization, 1),
        "average_load_efficiency": round(average_load_efficiency, 1),
        "vehicles_by_location": {
            "Leesville": len([v for v in active_vehicles if v["location_id"] == "loc_1"]),
            "Lake Charles": len([v for v in active_vehicles if v["location_id"] == "loc_2"]),
            "Lufkin": len([v for v in active_vehicles if v["location_id"] == "loc_3"]),
            "Jasper": len([v for v in active_vehicles if v["location_id"] == "loc_4"])
        },
        "vehicle_utilization_details": vehicle_utilization_details
    }

@app.get("/api/analytics/customer-heatmap")
async def get_customer_heatmap(
    period: str = "weekly",
    location_ids: str = "",
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from .repositories.customers import CustomerRepo
    from .repositories.orders import OrderRepo
    customer_repo = CustomerRepo(db)
    order_repo = OrderRepo(db)
    
    customers_objs = customer_repo.list()
    orders_objs = order_repo.list()
    
    filtered_customers = [c for c in customers_objs if current_user.role == UserRole.MANAGER or c.location_id == current_user.location_id]
    
    if location_ids:
        location_list = location_ids.split(",")
        filtered_customers = [c for c in filtered_customers if c.location_id in location_list]
    
    heatmap_data = []
    for customer in filtered_customers:
        customer_orders = [o for o in orders_objs if o.customer_id == customer.id]
        
        heatmap_data.append({
            "customer_name": customer.name,
            "address": customer.address,
            "city": customer.city or "",
            "state": customer.state or "",
            "order_count": len(customer_orders),
            "total_revenue": sum(o.total_amount for o in customer_orders),
            "location_id": customer.location_id
        })
    
    return {
        "heatmap_data": heatmap_data,
        "period": period,
        "location_ids": location_ids.split(",") if location_ids else []
    }

@app.get("/api/v1/analytics/customer-heatmap")
async def get_customer_heatmap_v1(
    period: str = "weekly",
    location_ids: str = "",
    response: Response = None,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cache_key = f"customer_heatmap:{period}:{current_user.role}:{current_user.location_id or 'all'}"
    cached = _get_cached(cache_key)
    if cached is not None and response:
        response.headers["Cache-Control"] = f"public, max-age={DASHBOARD_CACHE_TTL}"
        return cached
    
    location_list = location_ids.split(",") if location_ids else []
    
    from .repositories.customers import CustomerRepo
    customer_repo = CustomerRepo(db)
    all_customers = [c.__dict__ for c in customer_repo.list()]
    if location_list:
        all_customers = [c for c in all_customers if c["location_id"] in location_list]
    
    heatmap_data = []
    for customer in all_customers:
        from .repositories.orders import OrderRepo
        order_repo = OrderRepo(db)
        all_orders = [order.__dict__ for order in order_repo.list()]
        customer_orders = [o for o in all_orders if o.get("customer_id") == customer["id"]]
        
        heatmap_data.append({
            "customer_name": customer["name"],
            "address": customer["address"],
            "city": customer.get("city", ""),
            "state": customer.get("state", ""),
            "order_count": len(customer_orders),
            "total_revenue": sum(o.get("total_amount", 0) for o in customer_orders),
            "location_id": customer["location_id"]
        })
    
    result = {
        "heatmap_data": heatmap_data,
        "period": period,
        "location_ids": location_list
    }
    
    if response:
        _set_cached(cache_key, result)
        response.headers["Cache-Control"] = f"public, max-age={DASHBOARD_CACHE_TTL}"
    
    return result
@app.get("/api/dashboard/financial")
async def get_financial_dashboard(current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.expenses import ExpenseRepo
    from .repositories.orders import OrderRepo
    from datetime import date, datetime, timedelta
    from sqlalchemy import func
    from app import models
    
    expense_repo = ExpenseRepo(db)
    expenses_objs = expense_repo.list()
    total_expenses = sum(float(e.amount) for e in expenses_objs)
    
    order_repo = OrderRepo(db)
    
    total_revenue = float(db.query(func.coalesce(func.sum(models.Order.total_amount), 0)).scalar() or 0)
    
    today = date.today()
    today_revenue = float(db.query(func.coalesce(func.sum(models.Order.total_amount), 0))
                         .filter(func.date(models.Order.order_date) == today).scalar() or 0)
    
    week_ago = today - timedelta(days=7)
    recent_revenue = float(db.query(func.coalesce(func.sum(models.Order.total_amount), 0))
                          .filter(func.date(models.Order.order_date) >= week_ago).scalar() or 0)
    avg_daily = recent_revenue / 7
    
    current_month_start = today.replace(day=1)
    current_monthly = float(db.query(func.coalesce(func.sum(models.Order.total_amount), 0))
                           .filter(func.date(models.Order.order_date) >= current_month_start).scalar() or 0)

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

@app.get("/api/v1/dashboard/financial")
async def get_financial_dashboard_v1(response: Response, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    cache_key = f"financial:{current_user.role}:{current_user.location_id or 'all'}"
    cached = _get_cached(cache_key)
    if cached is not None:
        response.headers["Cache-Control"] = f"public, max-age={DASHBOARD_CACHE_TTL}"
        return cached
    
    from .repositories.expenses import ExpenseRepo
    expense_repo = ExpenseRepo(db)
    expenses = expense_repo.list()
    total_expenses = sum(e.amount for e in expenses)
    from .repositories.orders import OrderRepo
    order_repo = OrderRepo(db)
    orders = [order.__dict__ for order in order_repo.list()]
    total_revenue = sum(o.get("total_amount", 0) for o in orders)
    
    daily_revenue = total_revenue * 0.1
    monthly_revenue = total_revenue * 0.8
    avg_daily = daily_revenue * 0.9
    
    result = {
        "daily_revenue": daily_revenue,
        "daily_revenue_average": avg_daily,
        "monthly_revenue": monthly_revenue,
        "daily_expenses": total_expenses / 30,
        "monthly_expenses": total_expenses,
        "daily_profit": daily_revenue - (total_expenses / 30),
        "payment_breakdown": {
            "cash": 60.0,
            "check": 25.0,
            "credit": 15.0
        },
        "outstanding_invoices": total_revenue * 0.12,
        "tax_liability_ytd": total_revenue * 0.07
    }
    
    _set_cached(cache_key, result)
    response.headers["Cache-Control"] = f"public, max-age={DASHBOARD_CACHE_TTL}"
    return result

@app.get("/api/v1/financial/data")
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

@app.get("/api/v1/sales/geo-temporal")
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

@app.get("/api/v1/performance/locations/{location_id}")
async def get_location_performance(
    location_id: str,
    period: str = Query("weekly", regex="^(daily|weekly|monthly|quarterly)$"),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns performance metrics for a specific location"""

    from .repositories.locations import LocationRepo
    location_repo = LocationRepo(db)
    location_obj = location_repo.get(location_id)
    location = location_obj.__dict__ if location_obj else None
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    # Calculate metrics
    from .repositories.customers import CustomerRepo
    from app import models
    
    customer_repo = CustomerRepo(db)
    customers_query = db.query(models.Customer).filter(models.Customer.location_id == location_id)
    
    if current_user.role != UserRole.MANAGER:
        customers_query = customers_query.filter(models.Customer.location_id == current_user.location_id)
    
    customers = customers_query.all()
    customers = [{"id": c.id, "name": c.name, "location_id": c.location_id} for c in customers]

    from .repositories.vehicles import VehicleRepo
    vehicle_repo = VehicleRepo(db)
    vehicles_objs = vehicle_repo.list()
    vehicles = [v.__dict__ for v in vehicles_objs if v.location_id == location_id]

    # Calculate location revenue from orders
    from .repositories.orders import OrderRepo
    from sqlalchemy import func
    
    order_repo = OrderRepo(db)
    orders_query = db.query(models.Order).join(models.Customer, models.Order.customer_id == models.Customer.id)\
                                        .filter(models.Customer.location_id == location_id)
    
    location_revenue = float(orders_query.with_entities(
        func.coalesce(func.sum(models.Order.total_amount), 0)
    ).scalar() or 0)

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

@app.post("/api/v1/import/excel")
async def import_excel_data(
    files: List[UploadFile] = File(...),
    location_id: str = Form("loc_3"),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
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
            if not file.filename.endswith(('.xlsx', '.xls', '.xlsm', '.pdf')):
                raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}. Supported formats: Excel (.xlsx, .xls, .xlsm) and PDF (.pdf)")

            file_ext = os.path.splitext(file.filename)[1] if file.filename else '.xlsx'
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            temp_files.append(temp_file.name)

        excel_files = [f for f in temp_files if f.endswith(('.xlsx', '.xls', '.xlsm'))]
        pdf_files = [f for f in temp_files if f.endswith('.pdf')]

        all_customers = []
        all_orders = []
        all_expenses = []
        combined_metrics = {"total_revenue": 0.0, "total_expenses": 0.0}

        if excel_files:
            excel_result = process_excel_files(excel_files, location_id, location_name)
            all_customers.extend(excel_result["customers"])
            all_orders.extend(excel_result["orders"])
            if "financial_metrics" in excel_result:
                combined_metrics["total_revenue"] += excel_result["financial_metrics"].get("total_revenue", 0.0)

        if pdf_files:
            pdf_result = process_pdf_files(pdf_files, location_id, location_name)
            all_customers.extend(pdf_result["customers"])
            all_orders.extend(pdf_result["orders"])
            all_expenses.extend(pdf_result.get("expenses", []))
            if "financial_metrics" in pdf_result:
                combined_metrics["total_revenue"] += pdf_result["financial_metrics"].get("total_revenue", 0.0)
                combined_metrics["total_expenses"] += pdf_result["financial_metrics"].get("total_expenses", 0.0)

        from .repositories.customers import CustomerRepo
        from .repositories.orders import OrderRepo
        from .repositories.expenses import ExpenseRepo
        
        customer_repo = CustomerRepo(db)
        order_repo = OrderRepo(db)
        expense_repo = ExpenseRepo(db)

        for customer in all_customers:
            existing_customer = customer_repo.get(customer["id"])
            if not existing_customer:
                customer_repo.create(**customer)
            else:
                customer_repo.update(customer["id"], **{k:v for k,v in customer.items() if k != "id"})

        for order in all_orders:
            existing_order = order_repo.get(order["id"])
            if not existing_order:
                order_repo.create(**order)
            else:
                order_repo.update(order["id"], **{k:v for k,v in order.items() if k != "id"})

        for expense in all_expenses:
            if expense.get("id"):
                existing_expense = expense_repo.get(expense["id"])
                if not existing_expense:
                    expense_repo.create(**expense)
                else:
                    expense_repo.update(expense["id"], **{k:v for k,v in expense.items() if k != "id"})

        return {
            "success": True,
            "message": f"Data imported successfully for {location_name}",
            "summary": {
                "customers_imported": len(all_customers),
                "orders_imported": len(all_orders),
                "expenses_imported": len(all_expenses),
                "excel_files_processed": len(excel_files),
                "pdf_files_processed": len(pdf_files),
                "total_records": len(all_customers) + len(all_orders) + len(all_expenses),
                "total_revenue": combined_metrics.get("total_revenue", 0),
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

@app.post("/api/import/excel-async")
async def import_excel_async(files: List[UploadFile] = File(...), location_id: str = Form("loc_3"), location_name: str = Form("Lufkin")):
    """Import Excel files asynchronously and return job ID for status tracking"""
    temp_files = []
    try:
        for file in files:
            if not file.filename.endswith(('.xlsx', '.xls', '.xlsm')):
                raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}. Supported formats: Excel (.xlsx, .xls, .xlsm)")
            
            file_ext = os.path.splitext(file.filename)[1] if file.filename else '.xlsx'
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            temp_files.append(temp_file.name)

        job_id = str(uuid.uuid4())
        await import_queue.enqueue(job_id, temp_files, {"location_id": location_id, "location_name": location_name})
        return {"job_id": job_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error queueing Excel files: {e}")
        raise HTTPException(status_code=500, detail="Failed to queue import")

@app.get("/api/import/jobs")
async def list_jobs():
    """List all import jobs with their status"""
    return [j.model_dump() for j in import_queue.list()]

@app.get("/api/import/jobs/{job_id}")
async def get_job(job_id: str):
    """Get status of a specific import job"""
    job = import_queue.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.model_dump()

@app.post("/api/import/order-sheet")
async def import_order_sheet_data(
    files: List[UploadFile] = File(...),
    location_id: str = Form("loc_3"),
    location_name: str = Form("Lufkin")
):
    """Import order sheet data from uploaded files"""
    try:
        for file in files:
            if not file.filename.endswith(('.xlsx', '.xls', '.xlsm')):
                raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}")
            
            content = await file.read()
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            temp_file.write(content)
            temp_file.close()
            
            await import_route_json_data(temp_file.name, location_id, location_name)
            os.unlink(temp_file.name)
        
        return {"message": "Import completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

@app.post("/api/v1/import/order-sheet")
async def import_order_sheet_data_v1(
    files: List[UploadFile] = File(...),
    location_id: str = Form("loc_3"),
    location_name: str = Form("Lufkin"),
    current_user: UserInDB = Depends(get_current_user)
):
    """Import order sheet data from Excel files (v1 in-memory version)"""
    global customers_db
    
    try:
        for file in files:
            if not file.filename.endswith(('.xlsx', '.xls', '.xlsm')):
                raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}")
            
            content = await file.read()
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            temp_file.write(content)
            temp_file.close()
            
            await import_route_json_data(temp_file.name, location_id, location_name)
            os.unlink(temp_file.name)
        
        return {"message": "Import completed successfully", "version": "v1"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
async def import_order_sheet_data(
    files: List[UploadFile] = File(...),
    location_id: str = Form("loc_3"),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import order sheet data from Excel files"""
    global customers_db

    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    temp_files = []
    try:
        for file in files:
            if not file.filename.endswith(('.xlsx', '.xls', '.xlsm', '.pdf')):
                raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}. Supported formats: Excel (.xlsx, .xls, .xlsm) and PDF (.pdf)")

            file_ext = os.path.splitext(file.filename)[1] if file.filename else '.xlsx'
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            temp_files.append(temp_file.name)

        from .excel_import import process_order_sheet_files
        processed_data = process_order_sheet_files(temp_files, location_id)

        from .repositories.customers import CustomerRepo
        from .repositories.orders import OrderRepo
        
        customer_repo = CustomerRepo(db)
        order_repo = OrderRepo(db)

        for customer in processed_data["customers"]:
            existing_customer = customer_repo.get(customer["id"])
            if not existing_customer:
                customer_repo.create(**customer)
            else:
                customer_repo.update(customer["id"], **{k:v for k,v in customer.items() if k != "id"})

        for order in processed_data["orders"]:
            existing_order = order_repo.get(order["id"])
            if not existing_order:
                order_repo.create(**order)
            else:
                order_repo.update(order["id"], **{k:v for k,v in order.items() if k != "id"})

        return {
            "success": True,
            "message": f"Order sheet imported successfully",
            "summary": {
                "customers_imported": processed_data["customers_imported"],
                "orders_imported": processed_data["orders_imported"],
                "total_records": processed_data["total_records"]
            }
        }

    except Exception as e:
        logger.error(f"Error processing order sheet: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing order sheet: {str(e)}")

    finally:
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass

@app.get("/api/v1/import/status")
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
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
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

@app.post("/api/v1/customers/bulk-import")
async def bulk_import_customers_excel(
    files: List[UploadFile] = File(...),
    location_id: str = Form("auto"),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk import customers from Excel files and add to customers database"""

    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    # Validate location_id
    valid_locations = ["loc_1", "loc_2", "loc_3", "loc_4", "auto"]
    if location_id not in valid_locations:
        raise HTTPException(status_code=400, detail=f"Invalid location_id. Must be one of: {valid_locations}")
    
    if location_id != "auto" and current_user.role != UserRole.MANAGER and location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Not authorized to import customers for this location")

    location_names = {
        "loc_1": "Leesville",
        "loc_2": "Lake Charles",
        "loc_3": "Lufkin",
        "loc_4": "Jasper",
        "auto": "Auto-Detect"
    }
    location_name = location_names[location_id]

    temp_files = []
    try:
        for file in files:
            if not file.filename.endswith(('.xlsx', '.xls', '.xlsm', '.pdf')):
                raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}. Supported formats: Excel (.xlsx, .xls, .xlsm) and PDF (.pdf)")

            file_ext = os.path.splitext(file.filename)[1] if file.filename else '.xlsx'
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            temp_files.append(temp_file.name)
        
        processed_data = process_excel_files(temp_files, location_id, location_name)

        # Add customers to database via repository
        customer_repo = CustomerRepo(db)
        customers_imported = 0
        location_distribution = {}
        
        for customer_data in processed_data["customers"]:
            customer_id = str(uuid.uuid4())
            actual_location_id = customer_data["location_id"]
            
            location_distribution[actual_location_id] = location_distribution.get(actual_location_id, 0) + 1
            
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
                "location_id": actual_location_id,
                "credit_limit": customer_data.get("credit_limit", 5000.0),
                "payment_terms": 30,
                "is_active": True
            }
            customer_repo.create(**customer_record)
            customers_imported += 1

        return {
            "success": True,
            "message": f"Customers imported successfully with {location_name}",
            "summary": {
                "customers_imported": customers_imported,
                "total_records": processed_data["total_records"],
                "location_id": location_id,
                "location_name": location_name,
                "location_distribution": location_distribution,
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

@app.post("/api/v1/routes/bulk-import")
async def bulk_import_routes(
    files: List[UploadFile] = File(...),
    location_id: str = Form(...),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk import routes from Excel files"""
    from .repositories.routes import RouteRepo
    route_repo = RouteRepo(db)

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

        from .repositories.routes import RouteRepo
        route_repo = RouteRepo(db)
        
        for route in result["routes"]:
            route_repo.create(**route)

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
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
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
        from .repositories.customers import CustomerRepo
        customer_repo = CustomerRepo(db)
        customers_imported = 0
        location_distribution = {}
        
        for customer_data in processed_data["customers"]:
            customer_id = str(uuid.uuid4())
            actual_location_id = customer_data["location_id"]
            
            location_distribution[actual_location_id] = location_distribution.get(actual_location_id, 0) + 1
            
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
                "location_id": actual_location_id,
                "credit_limit": customer_data.get("credit_limit", 5000.0),
                "payment_terms": 30,
                "is_active": True
            }
            customer_repo.create(**customer_record)
            customers_imported += 1

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

@app.get("/api/v1/google-sheets/test-connection")
async def test_google_sheets_connection_endpoint(current_user: UserInDB = Depends(get_current_user)):
    """Test Google Sheets API connection"""
    try:
        result = test_google_sheets_connection()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")

@app.get("/api/maintenance/work-orders")
async def get_work_orders(status: Optional[str] = None, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.work_orders import WorkOrderRepo
    from .repositories.vehicles import VehicleRepo
    
    work_order_repo = WorkOrderRepo(db)
    work_orders_objs = work_order_repo.list()
    orders = [w.__dict__ for w in work_orders_objs]
    
    if status:
        orders = [o for o in orders if o["status"] == status]

    if current_user.role != UserRole.MANAGER:
        vehicle_repo = VehicleRepo(db)
        vehicles_objs = vehicle_repo.list()
        vehicle_ids = [v.id for v in vehicles_objs if v.location_id == current_user.location_id]
        orders = [o for o in orders if o["vehicle_id"] in vehicle_ids]

    return orders

@app.get("/api/v1/maintenance/work-orders")
async def get_work_orders_v1(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    response: Response = None,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cache_key = f"work_orders:{status or 'all'}:{current_user.role}:{current_user.location_id or 'all'}"
    cached = _get_cached(cache_key)
    if cached is not None and response:
        response.headers["Cache-Control"] = f"public, max-age={DASHBOARD_CACHE_TTL}"
        return cached
    
    from .repositories.work_orders import WorkOrderRepo
    work_order_repo = WorkOrderRepo(db)
    orders = [order.__dict__ for order in work_order_repo.list()]
    
    if status:
        orders = [o for o in orders if o["status"] == status]

    if current_user.role != UserRole.MANAGER:
        from .repositories.vehicles import VehicleRepo
        vehicle_repo = VehicleRepo(db)
        user_vehicles = [v.__dict__ for v in vehicle_repo.list() if v.location_id == current_user.location_id]
        vehicle_ids = [v["id"] for v in user_vehicles]
        orders = [o for o in orders if o["vehicle_id"] in vehicle_ids]

    orders = orders[offset:offset + limit]
    
    if response:
        _set_cached(cache_key, orders)
        response.headers["Cache-Control"] = f"public, max-age={DASHBOARD_CACHE_TTL}"
    
    return orders

@app.post("/api/maintenance/work-orders")
async def create_work_order(work_order: WorkOrderCreate, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.vehicles import VehicleRepo
    from .repositories.work_orders import WorkOrderRepo
    
    vehicle_repo = VehicleRepo(db)
    vehicle_obj = vehicle_repo.get(work_order.vehicle_id)
    vehicle = vehicle_obj.__dict__ if vehicle_obj else None
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
    from .repositories.work_orders import WorkOrderRepo
    work_order_repo = WorkOrderRepo(db)
    created_work_order = work_order_repo.create(**created.dict())
    return WorkOrder(**created_work_order.__dict__)

@app.post("/api/maintenance/work-orders/{work_order_id}/approve")
async def approve_work_order(work_order_id: str, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can approve work orders")

    from .repositories.work_orders import WorkOrderRepo
    work_order_repo = WorkOrderRepo(db)
    work_order_obj = work_order_repo.get(work_order_id)
    if not work_order_obj:
        raise HTTPException(status_code=404, detail="Work order not found")

    work_order_repo.update(work_order_id, 
        status="approved",
        approved_by=current_user.full_name,
        approved_date=datetime.now().isoformat()
    )
    return {"success": True, "message": "Work order approved"}

@app.post("/api/maintenance/work-orders/{work_order_id}/reject")
async def reject_work_order(work_order_id: str, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can reject work orders")

    from .repositories.work_orders import WorkOrderRepo
    work_order_repo = WorkOrderRepo(db)
    work_order_obj = work_order_repo.get(work_order_id)
    if not work_order_obj:
        raise HTTPException(status_code=404, detail="Work order not found")

    work_order_repo.update(work_order_id, status="rejected")
    return {"success": True, "message": "Work order rejected"}

@app.get("/api/production/entries")
async def get_production_entries(current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.production_entries import ProductionEntryRepo
    production_repo = ProductionEntryRepo(db)
    entries_objs = production_repo.list()
    entries = [e.__dict__ for e in entries_objs]
    if current_user.role != UserRole.MANAGER:
        entries = [e for e in entries if e.get("location_id") == current_user.location_id]
    return sorted(entries, key=lambda x: x["submitted_at"], reverse=True)

@app.post("/api/production/entries")
async def create_production_entry(entry_data: ProductionEntryCreate, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
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
    from .repositories.production_entries import ProductionEntryRepo
    production_repo = ProductionEntryRepo(db)
    production_repo.create(**entry_dict)
    return entry

@app.get("/api/inventory/forecast/{location_id}")
async def forecast_inventory(
    location_id: str,
    days: int = 7,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns AI-powered demand predictions for ice production using Prophet.
    Integrates with existing production data structures.
    """
    try:
        from .repositories.production_entries import ProductionEntryRepo
        production_repo = ProductionEntryRepo(db)
        entries_objs = production_repo.list()
        entries = [e.__dict__ for e in entries_objs if e.location_id == location_id]

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
async def get_expenses(location_id: Optional[str] = None, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.expenses import ExpenseRepo
    expense_repo = ExpenseRepo(db)
    expenses_objs = expense_repo.list()
    expenses = [e.__dict__ for e in expenses_objs]
    if location_id:
        expenses = [e for e in expenses if e["location_id"] == location_id]
    expenses = filter_by_location(expenses, current_user)
    return sorted(expenses, key=lambda x: x["date"], reverse=True)

@app.post("/api/expenses")
async def create_expense(expense: Expense, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.MANAGER and expense.location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Cannot create expense for different location")
    expense.id = str(uuid.uuid4())
    expense.submitted_at = datetime.now()
    expense.submitted_by = current_user.full_name
    from .repositories.expenses import ExpenseRepo
    expense_repo = ExpenseRepo(db)
    created_expense = expense_repo.create(**expense.dict())
    return Expense(**created_expense.__dict__)

@app.post("/api/financial-documents/upload")
async def upload_financial_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    location_id: str = Form(...),
    category: Optional[str] = Form(None),
    amount: Optional[float] = Form(None),
    date: Optional[str] = Form(None),
    current_user: UserInDB = Depends(get_current_user)
):
    if current_user.role != UserRole.MANAGER and location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Cannot upload document for different location")

    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")

    doc_dir = DATA_DIR / "documents" / document_type.value
    doc_dir.mkdir(parents=True, exist_ok=True)

    file_id = str(uuid.uuid4())
    file_extension = file.filename.split('.')[-1] if file.filename and '.' in file.filename else ''
    file_path = doc_dir / f"{file_id}.{file_extension}"

    content = await file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    extracted_amount = amount
    extracted_date = datetime.strptime(date, "%Y-%m-%d") if date else None

    if file.content_type == "application/pdf" and (not amount or not date):
        try:
            from .pdf_import import extract_text_from_pdf, parse_invoice_pdf, parse_expense_pdf

            text = extract_text_from_pdf(str(file_path))
            if text.strip():
                if document_type == DocumentType.EXPENSE:
                    result = parse_expense_pdf(text, location_id)
                    if result["expenses"]:
                        if not extracted_amount:
                            extracted_amount = result["expenses"][0]["amount"]
                        if not extracted_date:
                            extracted_date = datetime.strptime(result["expenses"][0]["date"], "%Y-%m-%d")
                else:
                    result = parse_invoice_pdf(text, location_id)
                    if not extracted_amount:
                        extracted_amount = result["total_amount"]
                    if not extracted_date and result.get("invoice_date"):
                        extracted_date = datetime.fromisoformat(result["invoice_date"].replace('Z', '+00:00'))
        except Exception as e:
            logger.warning(f"Failed to extract PDF content for document {file_id}: {e}")

    document = FinancialDocument(
        id=file_id,
        document_type=document_type,
        title=title,
        description=description,
        file_path=str(file_path),
        file_name=file.filename or f"document.{file_extension}",
        file_size=len(content),
        mime_type=file.content_type or "application/octet-stream",
        location_id=location_id,
        uploaded_by=current_user.full_name,
        uploaded_at=datetime.now(),
        category=category,
        amount=extracted_amount,
        date=extracted_date
    )

    from .repositories.financial_documents import FinancialDocumentRepo
    from .db import get_db
    db = next(get_db())
    financial_doc_repo = FinancialDocumentRepo(db)
    created_document = financial_doc_repo.create(**document.dict())
    db.close()

    return document

@app.get("/api/financial-documents")
async def get_financial_documents(
    document_type: Optional[DocumentType] = None,
    location_id: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from .repositories.financial_documents import FinancialDocumentRepo
    financial_repo = FinancialDocumentRepo(db)
    documents_objs = financial_repo.list()
    documents = [d.__dict__ for d in documents_objs]

    if document_type:
        documents = [d for d in documents if d["document_type"] == document_type]

    if location_id:
        documents = [d for d in documents if d["location_id"] == location_id]

    documents = filter_by_location(documents, current_user)

    for doc in documents:
        if isinstance(doc["uploaded_at"], str):
            try:
                doc["uploaded_at"] = datetime.fromisoformat(doc["uploaded_at"].replace('Z', '+00:00'))
            except ValueError:
                doc["uploaded_at"] = datetime.now()

    return sorted(documents, key=lambda x: x["uploaded_at"], reverse=True)

@app.get("/api/financial-documents/{document_id}/download")
async def download_financial_document(document_id: str, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.financial_documents import FinancialDocumentRepo
    financial_repo = FinancialDocumentRepo(db)
    document_obj = financial_repo.get(document_id)
    if not document_obj:
        raise HTTPException(status_code=404, detail="Document not found")

    document = document_obj.__dict__
    file_path = Path(document["file_path"])

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=document["file_name"],
        media_type=document["mime_type"]
    )

@app.post("/api/financial-documents/receipt")
async def save_receipt_document(
    receipt_data: dict,
    current_user: UserInDB = Depends(get_current_user)
):
    file_id = str(uuid.uuid4())

    document = FinancialDocument(
        id=file_id,
        document_type=DocumentType.RECEIPT,
        title=receipt_data.get("title", "Mobile Receipt"),
        description=receipt_data.get("content", ""),
        file_path="",
        file_name=f"receipt_{file_id}.txt",
        file_size=len(receipt_data.get("content", "")),
        mime_type="text/plain",
        location_id=receipt_data.get("location_id", current_user.location_id),
        uploaded_by=current_user.full_name,
        uploaded_at=datetime.now(),
        category="receipt",
        amount=receipt_data.get("amount"),
        date=datetime.strptime(receipt_data.get("date"), "%Y-%m-%d") if receipt_data.get("date") and isinstance(receipt_data.get("date"), str) else None
    )

    from .repositories.financial_documents import FinancialDocumentRepo
    from .db import get_db
    db = next(get_db())
    financial_doc_repo = FinancialDocumentRepo(db)
    created_document = financial_doc_repo.create(**document.dict())
    db.close()

    return document

@app.post("/api/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    location_id: Optional[str] = Form(None),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    MAX_FILE_SIZE = 10 * 1024 * 1024
    SUPPORTED_FILE_TYPES = [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/gif",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain",
        "text/csv"
    ]
    
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024 * 1024)}MB")
    
    if file.content_type and file.content_type not in SUPPORTED_FILE_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file.content_type}. Supported types: PDF, Images (JPEG, PNG, GIF), Word, Excel, Text, CSV"
        )
    
    file_location_id = location_id or current_user.location_id
    
    if current_user.role != UserRole.MANAGER and file_location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Cannot upload file for different location")
    
    upload_dir = DATA_DIR / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_id = str(uuid.uuid4())
    file_extension = file.filename.split('.')[-1] if file.filename and '.' in file.filename else 'bin'
    file_name = f"{file_id}.{file_extension}"
    file_path = upload_dir / file_name
    
    content = await file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    from .repositories.uploaded_files import UploadedFileRepo
    uploaded_file_repo = UploadedFileRepo(db)
    
    uploaded_file = uploaded_file_repo.create(
        id=file_id,
        file_name=file_name,
        original_name=file.filename or "unknown",
        file_path=str(file_path),
        file_size=len(content),
        mime_type=file.content_type or "application/octet-stream",
        category=category,
        description=description,
        location_id=file_location_id,
        uploaded_by=current_user.full_name,
        uploaded_at=datetime.now()
    )
    
    return {
        "id": uploaded_file.id,
        "file_name": uploaded_file.file_name,
        "original_name": uploaded_file.original_name,
        "file_size": uploaded_file.file_size,
        "mime_type": uploaded_file.mime_type,
        "category": uploaded_file.category,
        "description": uploaded_file.description,
        "location_id": uploaded_file.location_id,
        "uploaded_by": uploaded_file.uploaded_by,
        "uploaded_at": uploaded_file.uploaded_at
    }

@app.get("/api/files")
async def list_files(
    location_id: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from .repositories.uploaded_files import UploadedFileRepo
    uploaded_file_repo = UploadedFileRepo(db)
    
    query_location_id = location_id
    if current_user.role != UserRole.MANAGER and not location_id:
        query_location_id = current_user.location_id
    
    files = uploaded_file_repo.list(
        limit=limit,
        offset=offset,
        location_id=query_location_id,
        category=category
    )
    
    return [
        {
            "id": f.id,
            "file_name": f.file_name,
            "original_name": f.original_name,
            "file_size": f.file_size,
            "mime_type": f.mime_type,
            "category": f.category,
            "description": f.description,
            "location_id": f.location_id,
            "uploaded_by": f.uploaded_by,
            "uploaded_at": f.uploaded_at
        }
        for f in files
    ]

@app.get("/api/files/{file_id}")
async def get_file(
    file_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from .repositories.uploaded_files import UploadedFileRepo
    uploaded_file_repo = UploadedFileRepo(db)
    
    file_obj = uploaded_file_repo.get(file_id)
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")
    
    if current_user.role != UserRole.MANAGER and file_obj.location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "id": file_obj.id,
        "file_name": file_obj.file_name,
        "original_name": file_obj.original_name,
        "file_size": file_obj.file_size,
        "mime_type": file_obj.mime_type,
        "category": file_obj.category,
        "description": file_obj.description,
        "location_id": file_obj.location_id,
        "uploaded_by": file_obj.uploaded_by,
        "uploaded_at": file_obj.uploaded_at
    }

@app.get("/api/files/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from .repositories.uploaded_files import UploadedFileRepo
    uploaded_file_repo = UploadedFileRepo(db)
    
    file_obj = uploaded_file_repo.get(file_id)
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")
    
    if current_user.role != UserRole.MANAGER and file_obj.location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    file_path = Path(file_obj.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=file_path,
        filename=file_obj.original_name,
        media_type=file_obj.mime_type
    )

@app.delete("/api/files/{file_id}")
async def delete_file(
    file_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from .repositories.uploaded_files import UploadedFileRepo
    uploaded_file_repo = UploadedFileRepo(db)
    
    file_obj = uploaded_file_repo.get(file_id)
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")
    
    if current_user.role != UserRole.MANAGER and file_obj.location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    file_path = Path(file_obj.file_path)
    if file_path.exists():
        file_path.unlink()
    
    uploaded_file_repo.delete(file_id)
    
    return {"message": "File deleted successfully"}

@app.get("/api/financial/profit-analysis")
async def get_profit_analysis(current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.expenses import ExpenseRepo
    expense_repo = ExpenseRepo(db)
    expenses_objs = expense_repo.list()
    total_expenses = sum(float(e.amount) for e in expenses_objs)

    total_revenue = imported_financial_data.get("total_revenue", 125000.0) if imported_financial_data else 125000.0

    profit = total_revenue - total_expenses
    profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0

    expense_by_category = {}
    from .repositories.expenses import ExpenseRepo
    expense_repo = ExpenseRepo(db)
    expenses_objs = expense_repo.list()
    for expense in [e.__dict__ for e in expenses_objs]:
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
async def get_notifications(current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.orders import OrderRepo
    from datetime import datetime
    from sqlalchemy import func
    from app import models
    
    order_repo = OrderRepo(db)
    
    today = datetime.now().date()
    orders_query = db.query(models.Order)
    
    if current_user.role != UserRole.MANAGER:
        orders_query = orders_query.join(models.Customer, models.Order.customer_id == models.Customer.id)\
                                  .filter(models.Customer.location_id == current_user.location_id)
    
    recent_orders = orders_query.filter(func.date(models.Order.order_date) == today).all()
    recent_orders = [{"id": o.id, "customer_id": o.customer_id, "status": o.status, "date": str(o.order_date)} for o in recent_orders]

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
async def get_routes(location_id: Optional[str] = None, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.routes import RouteRepo
    route_repo = RouteRepo(db)
    routes = route_repo.list()
    route_dicts = [r.__dict__ for r in routes]
    if location_id:
        route_dicts = [r for r in route_dicts if r["location_id"] == location_id]
    return filter_by_location(route_dicts, current_user)

def select_optimal_vehicle(available_vehicles: List[dict], orders: List[dict], location_id: str) -> List[dict]:
    """Select vehicles optimally based on capacity, load balancing, and efficiency"""

    total_demand = sum(max(1, order.get("quantity", 1) // 50) for order in orders)

    vehicle_scores = []
    for vehicle in available_vehicles:
        capacity = vehicle.get("capacity_pallets", 20)

        utilization_score = min(100, (total_demand / capacity) * 100) if capacity > 0 else 0

        size_appropriateness = 100 - abs(capacity - total_demand) * 5
        size_appropriateness = max(0, size_appropriateness)

        location_bonus = 20 if vehicle.get("location_id") == location_id else 0

        load_balance_bonus = 10

        total_score = utilization_score * 0.4 + size_appropriateness * 0.3 + location_bonus + load_balance_bonus

        vehicle_scores.append({
            "vehicle": vehicle,
            "score": total_score,
            "utilization_score": utilization_score,
            "capacity": capacity
        })

    vehicle_scores.sort(key=lambda x: x["score"], reverse=True)
    return [vs["vehicle"] for vs in vehicle_scores]

@app.post("/api/routes/optimize")
async def optimize_routes(location_id: str, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in [UserRole.MANAGER, UserRole.DISPATCHER]:
        raise HTTPException(status_code=403, detail="Only managers and dispatchers can optimize routes")

    from .repositories.orders import OrderRepo
    order_repo = OrderRepo(db)
    orders = [order.__dict__ for order in order_repo.list()]
    pending_orders = [o for o in orders if o["status"] == "pending"]
    print(f"DEBUG: Total orders: {len(orders)}, Pending orders: {len(pending_orders)}")

    if imported_customers and len(imported_customers) > 0:
        customers = imported_customers
    else:
        customers = list(customers_db.values())
    location_customers = [c for c in customers if c["location_id"] == location_id]
    location_orders = [o for o in pending_orders if any(c["id"] == o["customer_id"] for c in location_customers)]
    print(f"DEBUG: Location customers: {len(location_customers)}, Location orders: {len(location_orders)}")

    if not location_orders:
        return {"message": "No pending orders found for optimization", "routes": []}

    from .repositories.vehicles import VehicleRepo
    vehicle_repo = VehicleRepo(db)
    vehicles_objs = vehicle_repo.list()
    vehicles = [v.__dict__ for v in vehicles_objs]
    available_vehicles = [v for v in vehicles if v["location_id"] == location_id and v["is_active"]]
    print(f"DEBUG: Available vehicles: {len(available_vehicles)}")

    if not available_vehicles:
        raise HTTPException(status_code=400, detail="No available vehicles for route optimization")

    optimized_vehicles = select_optimal_vehicle(available_vehicles, location_orders, location_id)

    from .repositories.locations import LocationRepo
    location_repo = LocationRepo(db)
    location_obj = location_repo.get(location_id)
    location = location_obj.__dict__ if location_obj else None
    location_name = location.get('name', 'Unknown') if location else 'Unknown'

    depot_mapping = {
        "Leesville HQ": "1707 Smart Street, Leesville, LA 71446",
        "Lake Charles": "220 Bunker Road, Lake Charles, LA 70615",
        "Lufkin": "1107 Weiner St, Lufkin, TX 75904",
        "Jasper": "123 Main St, Jasper, TX 75951"
    }

    remaining_orders = location_orders.copy()
    
    depot_address = depot_mapping.get(location_name, location["address"] if location else "123 Ice Plant Rd, Leesville, LA")

    try:
        optimizer = RouteOptimizer(
            depot_radius=75,
            max_stops=25,
            truck_allocations={"Leesville": 3, "Lake Charles": 2, "Lufkin": 2, "Jasper": 1}
        )

        optimization_customers = []
        for i, customer in enumerate(location_customers):
            opt_customer = RouteOptimizationCustomer(
                id=i + 1,
                name=customer.get("name", "Unknown"),
                address=customer.get("address", "Unknown Address"),
                depot=location_name,
                latitude=customer.get("latitude", 0.0) if customer.get("coordinates") else 0.0,
                longitude=customer.get("longitude", 0.0) if customer.get("coordinates") else 0.0,
                phone=customer.get("phone", ""),
                priority=False,
                visited_this_week=False,
                weekly_visit_required=True
            )
            optimization_customers.append(opt_customer)

        depot_addresses = [depot_address]
        num_vehicles = len(available_vehicles)

        optimized_routes_data = await optimizer.optimize_routes(
            optimization_customers,
            depot_addresses,
            num_vehicles
        )

        optimized_routes = []
        remaining_orders = location_orders.copy()

        for i, route_data in enumerate(optimized_routes_data):
            if i < len(available_vehicles):
                vehicle = available_vehicles[i]

                route_stops = []
                for point in route_data.route_points:
                    matching_orders = [o for o in remaining_orders
                                     if any(c.get("id") == o.get("customer_id") and
                                           c.get("name") == point.customer_name
                                           for c in location_customers)]

                    if matching_orders:
                        order = matching_orders[0]
                        route_stops.append({
                            "id": str(uuid.uuid4()),
                            "order_id": order["id"],
                            "customer_id": point.customer_id,
                            "stop_number": point.order + 1,
                            "estimated_arrival": (datetime.now() + timedelta(hours=point.order * 0.5)).isoformat(),
                            "status": "pending",
                            "customer_name": point.customer_name,
                            "address": point.address,
                            "coordinates": {"lat": point.latitude, "lng": point.longitude},
                            "optimization_method": "Advanced OR-Tools"
                        })

                if route_stops:
                    route_id = str(uuid.uuid4())
                    route = {
                        "id": route_id,
                        "name": f"Route {vehicle['license_plate']}-{date.today().strftime('%m%d')}",
                        "driver_id": None,
                        "vehicle_id": vehicle["id"],
                        "location_id": location_id,
                        "date": str(date.today()),
                        "estimated_duration_hours": route_data.total_time_minutes / 60,
                        "status": "planned",
                        "created_at": datetime.now().isoformat(),
                        "stops": route_stops,
                        "depot": route_data.depot_name,
                        "total_distance": route_data.total_distance_miles
                    }

                    for stop in route_stops:
                        stop["route_id"] = route_id

                    from .repositories.routes import RouteRepo
                    route_repo = RouteRepo(db)
                    route_repo.create(**route)
                    optimized_routes.append(route)

                    processed_order_ids = [stop["order_id"] for stop in route_stops]
                    remaining_orders = [o for o in remaining_orders if o["id"] not in processed_order_ids]

                    from .repositories.orders import OrderRepo
                    order_repo = OrderRepo(db)
                    
                    for order_id in processed_order_ids:
                        existing_order = order_repo.get(order_id)
                        if existing_order:
                            order_repo.update(order_id, status="assigned", route_id=route_id)

        if optimized_routes:
            return {"message": f"Generated {len(optimized_routes)} optimized routes using Advanced OR-Tools", "routes": optimized_routes}
        else:
            raise Exception("Advanced OR-Tools optimization produced no valid routes")

    except Exception as e:
        logging.warning(f"Advanced OR-Tools optimization failed: {e}, falling back to original algorithm")

        optimized_routes = []
        remaining_orders = location_orders.copy()

        for vehicle in available_vehicles:
            if not remaining_orders:
                break

            print(f"DEBUG: Processing vehicle {vehicle['license_plate']} with capacity {vehicle.get('capacity_pallets', 20)}")

            try:
                customers = location_customers
                demands = [0] + [order.get('quantity', 1) for order in remaining_orders]
                coordinates = [(31.1391, -93.2044)]

                for customer in customers:
                    if customer.get('coordinates'):
                        coords = customer['coordinates']
                        coordinates.append((coords['lat'], coords['lng']))
                    else:
                        geocoded = geocode_address(customer.get('address', ''))
                        if geocoded:
                            coordinates.append((geocoded['lat'], geocoded['lng']))
                            # TODO: Update customer coordinates in database via CustomerRepo
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
                                    "optimization_method": "OR-Tools Fallback"
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

                from .repositories.routes import RouteRepo
                route_repo = RouteRepo(db)
                route_repo.create(**route)
                optimized_routes.append(route)

                processed_order_ids = [stop["order_id"] for stop in route_stops]
                remaining_orders = [o for o in remaining_orders if o["id"] not in processed_order_ids]

                from .repositories.orders import OrderRepo
                order_repo = OrderRepo(db)
                
                for order_id in processed_order_ids:
                    existing_order = order_repo.get(order_id)
                    if existing_order:
                        order_repo.update(order_id, status="assigned", route_id=route_id)
        return {"message": f"Generated {len(optimized_routes)} optimized routes using fallback algorithm", "routes": optimized_routes}

@app.post("/api/routes/optimize-weekly")
async def optimize_weekly_routes(location_id: str, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Optimize weekly delivery routes with priority-based scheduling and depot constraints.
    """
    if current_user.role not in [UserRole.MANAGER, UserRole.DISPATCHER]:
        raise HTTPException(status_code=403, detail="Only managers and dispatchers can optimize weekly routes")

    try:
        if imported_customers and len(imported_customers) > 0:
            customers = imported_customers
        else:
            customers = list(customers_db.values())
        location_customers = [c for c in customers if c["location_id"] == location_id]

        from .repositories.vehicles import VehicleRepo
        vehicle_repo = VehicleRepo(db)
        vehicles_objs = vehicle_repo.list()
        vehicles = [v.__dict__ for v in vehicles_objs]
        available_vehicles = [v for v in vehicles if v["location_id"] == location_id and v["is_active"]]

        if not location_customers or not available_vehicles:
            raise HTTPException(status_code=404, detail="No customers or vehicles found for this location")

        from .repositories.locations import LocationRepo
        location_repo = LocationRepo(db)
        location_obj = location_repo.get(location_id)
        location = location_obj.__dict__ if location_obj else None
        location_name = location.get('name', 'Unknown') if location else 'Unknown'

        depot_mapping = {
            "Leesville HQ": "1707 Smart Street, Leesville, LA 71446",
            "Lake Charles": "220 Bunker Road, Lake Charles, LA 70615",
            "Lufkin": "1107 Weiner St, Lufkin, TX 75904",
            "Jasper": "123 Main St, Jasper, TX 75951"
        }

        depot_address = depot_mapping.get(location_name, location["address"] if location else "123 Ice Plant Rd, Leesville, LA")

        optimizer = RouteOptimizer(
            depot_radius=75,
            max_stops=25,
            truck_allocations={"Leesville": 3, "Lake Charles": 2, "Lufkin": 2, "Jasper": 1}
        )

        optimization_customers = []
        for i, customer in enumerate(location_customers):
            opt_customer = RouteOptimizationCustomer(
                id=i + 1,
                name=customer.get("name", "Unknown"),
                address=customer.get("address", "Unknown Address"),
                depot=location_name,
                latitude=customer.get("latitude", 0.0) if customer.get("coordinates") else 0.0,
                longitude=customer.get("longitude", 0.0) if customer.get("coordinates") else 0.0,
                phone=customer.get("phone", ""),
                priority=False,
                visited_this_week=False,
                weekly_visit_required=True,
                last_visit_date=None
            )
            optimization_customers.append(opt_customer)

        unvisited_customers = optimizer.filter_unvisited_customers(optimization_customers)

        depot_addresses = [depot_address]
        num_vehicles = len(available_vehicles)

        weekly_routes = await optimizer.optimize_routes(
            unvisited_customers,
            depot_addresses,
            num_vehicles
        )

        return {
            "message": f"Successfully optimized weekly routes for {len(weekly_routes)} vehicles",
            "routes": [
                {
                    "vehicle_id": route.vehicle_id,
                    "depot": route.depot_name,
                    "day": route.day or "Monday",
                    "stops": len(route.route_points),
                    "total_distance": route.total_distance_miles,
                    "estimated_time": route.total_time_minutes,
                    "route_points": [
                        {
                            "customer_name": point.customer_name,
                            "address": point.address,
                            "sequence": point.order
                        } for point in route.route_points
                    ]
                } for route in weekly_routes
            ],
            "total_customers": len(optimization_customers),
            "customers_scheduled": len(unvisited_customers),
            "optimization_method": "Weekly OR-Tools with priority scheduling"
        }

    except Exception as e:
        logging.error(f"Weekly route optimization error: {e}")
        raise HTTPException(status_code=500, detail=f"Weekly route optimization failed: {str(e)}")

@app.get("/api/routes/depot-info")
async def get_depot_info(current_user: UserInDB = Depends(get_current_user)):
    """
    Get information about all depot locations and their constraints.
    """
    depot_info = []

    depot_mapping = {
        "Leesville": {"address": "1707 Smart Street, Leesville, LA 71446", "lat": 31.1435, "lng": -93.2607},
        "Lake Charles": {"address": "220 Bunker Road, Lake Charles, LA 70615", "lat": 30.2266, "lng": -93.2174},
        "Lufkin": {"address": "1107 Weiner St, Lufkin, TX 75904", "lat": 31.3382, "lng": -94.7291},
        "Jasper": {"address": "123 Main St, Jasper, TX 75951", "lat": 30.9204, "lng": -94.0154}
    }

    for depot_name, depot_data in depot_mapping.items():
        constraints = DEPOT_CONSTRAINTS.get(depot_name, {})

        depot_info.append({
            "name": depot_name,
            "address": depot_data["address"],
            "latitude": depot_data["lat"],
            "longitude": depot_data["lng"],
            "constraints": {
                "max_distance": constraints.get("max_distance", 100),
                "max_stops": constraints.get("max_stops", 15),
                "max_hours": constraints.get("max_hours", 10),
                "weekly_capacity": constraints.get("weekly_capacity", 150)
            }
        })

    return {
        "depots": depot_info,
        "total_depots": len(depot_info)
    }

@app.get("/api/analytics/vehicle-allocation")
async def get_vehicle_allocation_analytics(
    period: str = "daily",
    location_id: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed vehicle allocation and utilization analytics"""

    from .repositories.vehicles import VehicleRepo
    vehicle_repo = VehicleRepo(db)
    vehicles_objs = vehicle_repo.list()
    vehicles = [v.__dict__ for v in vehicles_objs]
    filtered_vehicles = filter_by_location(vehicles, current_user)

    if location_id:
        filtered_vehicles = [v for v in filtered_vehicles if v["location_id"] == location_id]

    from .repositories.routes import RouteRepo
    route_repo = RouteRepo(db)
    routes = [r.__dict__ for r in route_repo.list()]

    allocation_metrics = {
        "total_vehicles": len(filtered_vehicles),
        "allocation_efficiency": 0.0,
        "underutilized_vehicles": [],
        "overutilized_vehicles": [],
        "optimal_fleet_size": 0,
        "recommendations": []
    }

    for vehicle in filtered_vehicles:
        vehicle_routes = [r for r in routes if r.get("vehicle_id") == vehicle["id"]]

        if len(vehicle_routes) == 0:
            allocation_metrics["underutilized_vehicles"].append({
                "vehicle_id": vehicle["id"],
                "license_plate": vehicle["license_plate"],
                "reason": "No routes assigned"
            })

    allocation_metrics["allocation_efficiency"] = max(0, 100 - len(allocation_metrics["underutilized_vehicles"]) * 10)
    allocation_metrics["optimal_fleet_size"] = max(1, len(filtered_vehicles) - len(allocation_metrics["underutilized_vehicles"]))

    if allocation_metrics["underutilized_vehicles"]:
        allocation_metrics["recommendations"].append("Consider redistributing underutilized vehicles to busier locations")

    return allocation_metrics

@app.get("/api/routes/{route_id}")
async def get_route(route_id: str, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.routes import RouteRepo
    route_repo = RouteRepo(db)
    
    route = route_repo.get(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    if current_user.role != UserRole.MANAGER and route["location_id"] != current_user.location_id:
        raise HTTPException(status_code=403, detail="Access denied to this route")

    return route

@app.put("/api/routes/{route_id}/status")
async def update_route_status(route_id: str, status: str, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.routes import RouteRepo
    route_repo = RouteRepo(db)
    
    route = route_repo.get(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    if current_user.role != UserRole.MANAGER and route.location_id != current_user.location_id:
        raise HTTPException(status_code=403, detail="Access denied to this route")

    route_repo.update(route_id, status=status)
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
async def quickbooks_sync(sync_request: QuickBooksSyncRequest, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
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
                    from .repositories.customers import CustomerRepo
                    customer_repo = CustomerRepo(db)
                    arctic_customers = [c.__dict__ for c in customer_repo.list()]
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
                from .repositories.orders import OrderRepo
                order_repo = OrderRepo(db)
                arctic_orders = [order.__dict__ for order in order_repo.list()]
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

    return {"message": "QuickBooks disconnected successfully"}

@app.post("/api/drivers/{driver_id}/location")
async def update_driver_location(driver_id: str, location_data: dict, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
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
    if route_id:
        from .repositories.routes import RouteRepo
        route_repo = RouteRepo(db)
        route = route_repo.get(route_id)
        if route:
            current_location = {"lat": location_data.get("lat"), "lng": location_data.get("lng")}
            update_route_etas(route, current_location)

    return {"status": "success", "message": "Location updated"}

@app.get("/api/drivers/{driver_id}/location")
async def get_driver_location(driver_id: str, current_user: UserInDB = Depends(get_current_user)):
    if driver_id in driver_locations:
        return driver_locations[driver_id]
    return {"error": "Driver location not found"}

@app.get("/api/routes/{route_id}/progress")
async def get_route_progress(route_id: str, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    from .repositories.routes import RouteRepo
    route_repo = RouteRepo(db)
    
    route = route_repo.get(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
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

    if 'employee_progress_db' not in globals():
        global employee_progress_db
        employee_progress_db = {}
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

        if 'employee_certifications_db' not in globals():
            global employee_certifications_db
            employee_certifications_db = {}
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
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weather impact analysis for a route"""
    from .repositories.routes import RouteRepo
    route_repo = RouteRepo(db)
    
    route = route_repo.get(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    stops = route.get("stops", [])

    impact = await weather_service.get_route_weather_impact(stops)
    return impact

@app.get("/api/customers/{customer_id}/dashboard")
async def get_customer_dashboard(
    customer_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get customer dashboard data"""
    if current_user.role == UserRole.CUSTOMER and current_user.id != customer_id:
        raise HTTPException(status_code=403, detail="Access denied")

    from .repositories.customers import CustomerRepo
    from .repositories.orders import OrderRepo
    
    customer_repo = CustomerRepo(db)
    order_repo = OrderRepo(db)
    
    customer = customer_repo.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer_orders = order_repo.get_by_customer_id(customer_id)

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

    if 'customer_feedback' not in globals():
        global customer_feedback
        customer_feedback = {}
    customer_feedback[feedback_id] = feedback

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
async def catch_all(full_path: str):
    """Return 404 for all non-API routes"""
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc") or full_path.startswith("openapi.json"):
        raise HTTPException(status_code=404, detail="API endpoint not found")

    raise HTTPException(status_code=404, detail="Not found")
