from __future__ import annotations
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Numeric, Boolean,
    Date, Time, Enum, UniqueConstraint, Index, Text
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from .db import Base

class Location(Base):
    __tablename__ = "locations"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    location_type: Mapped[str] = mapped_column(String(40))
    address: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(80))
    state: Mapped[str | None] = mapped_column(String(40))
    zip_code: Mapped[str | None] = mapped_column(String(20))

    customers = relationship("Customer", back_populates="location")

class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    contact_person: Mapped[str | None] = mapped_column(String(160))
    phone: Mapped[str | None] = mapped_column(String(64))
    email: Mapped[str | None] = mapped_column(String(160))
    address: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(80))
    state: Mapped[str | None] = mapped_column(String(40))
    zip_code: Mapped[str | None] = mapped_column(String(20))
    location_id: Mapped[str | None] = mapped_column(ForeignKey("locations.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    credit_limit: Mapped[float | None] = mapped_column(Numeric(12,2), default=0)
    payment_terms: Mapped[str | None] = mapped_column(String(40))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    location = relationship("Location", back_populates="customers")
    orders = relationship("Order", back_populates="customer")

class Product(Base):
    __tablename__ = "products"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    product_type: Mapped[str] = mapped_column(String(40))
    price: Mapped[float] = mapped_column(Numeric(12,2))
    weight_lbs: Mapped[float] = mapped_column(Numeric(8,2))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Vehicle(Base):
    __tablename__ = "vehicles"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    license_plate: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    vehicle_type: Mapped[str] = mapped_column(String(40))
    capacity_pallets: Mapped[int] = mapped_column(Integer)
    location_id: Mapped[str | None] = mapped_column(ForeignKey("locations.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_maintenance: Mapped[Date | None] = mapped_column(Date, nullable=True)

class Route(Base):
    __tablename__ = "routes"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    driver_id: Mapped[str | None] = mapped_column(String, index=True)
    vehicle_id: Mapped[str | None] = mapped_column(ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True)
    location_id: Mapped[str | None] = mapped_column(ForeignKey("locations.id"), index=True)
    date: Mapped[Date] = mapped_column(Date, index=True)
    estimated_duration_hours: Mapped[float | None] = mapped_column(Numeric(8,2), default=0)
    status: Mapped[str] = mapped_column(String(24), default="planned")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(12,2), nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(12,2), nullable=False)
    order_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    delivery_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="pending")
    route_id: Mapped[str | None] = mapped_column(ForeignKey("routes.id", ondelete="SET NULL"), nullable=True)
    payment_method: Mapped[str | None] = mapped_column(String(24), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text)

    customer = relationship("Customer", back_populates="orders")

class WorkOrder(Base):
    __tablename__ = "work_orders"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    vehicle_id: Mapped[str | None] = mapped_column(ForeignKey("vehicles.id"), nullable=True)
    vehicle_name: Mapped[str | None] = mapped_column(String(160))
    technician_name: Mapped[str | None] = mapped_column(String(160))
    issue_description: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(16), default="medium")
    status: Mapped[str] = mapped_column(String(24), default="pending")
    work_type: Mapped[str] = mapped_column(String(40))
    submitted_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    estimated_cost: Mapped[float | None] = mapped_column(Numeric(12,2))
    estimated_hours: Mapped[float | None] = mapped_column(Numeric(8,2))
    approved_by: Mapped[str | None] = mapped_column(String(160))
    approved_date: Mapped[datetime | None] = mapped_column(DateTime)
    completed_date: Mapped[datetime | None] = mapped_column(DateTime)

class ProductionEntry(Base):
    __tablename__ = "production_entries"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    date: Mapped[Date] = mapped_column(Date, index=True)
    shift: Mapped[str] = mapped_column(String(20))
    product_type: Mapped[str] = mapped_column(String(40))
    quantity_produced: Mapped[int] = mapped_column(Integer)
    location_id: Mapped[str | None] = mapped_column(ForeignKey("locations.id"))
    operator_name: Mapped[str | None] = mapped_column(String(160))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Inventory(Base):
    __tablename__ = "inventory"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Expense(Base):
    __tablename__ = "expenses"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    date: Mapped[Date] = mapped_column(Date, index=True)
    category: Mapped[str] = mapped_column(String(40))
    description: Mapped[str] = mapped_column(Text)
    amount: Mapped[float] = mapped_column(Numeric(12,2))
    location_id: Mapped[str | None] = mapped_column(ForeignKey("locations.id"))
    submitted_by: Mapped[str | None] = mapped_column(String(160))
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class FinancialDocument(Base):
    __tablename__ = "financial_documents"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    document_type: Mapped[str] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    file_path: Mapped[str] = mapped_column(String(500))
    file_name: Mapped[str] = mapped_column(String(255))
    file_size: Mapped[int] = mapped_column(Integer)
    mime_type: Mapped[str] = mapped_column(String(100))
    location_id: Mapped[str | None] = mapped_column(ForeignKey("locations.id"))
    uploaded_by: Mapped[str | None] = mapped_column(String(160))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    category: Mapped[str | None] = mapped_column(String(100))
    amount: Mapped[float | None] = mapped_column(Numeric(12,2))
    date: Mapped[datetime | None] = mapped_column(DateTime)

class CustomerPricing(Base):
    __tablename__ = "customer_pricing"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    custom_price: Mapped[float] = mapped_column(Numeric(12,2))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_by: Mapped[str | None] = mapped_column(String(160))

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(160))
    full_name: Mapped[str | None] = mapped_column(String(160))
    role: Mapped[str] = mapped_column(String(40))
    location_id: Mapped[str | None] = mapped_column(ForeignKey("locations.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
