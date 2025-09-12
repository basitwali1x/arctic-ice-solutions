"""
Phase 2: Enhanced Authentication Models
Extends the existing authentication system with refresh tokens, RBAC, and audit logging
"""
from __future__ import annotations
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timedelta
from typing import Optional, List
from .db import Base

class Role(Base):
    """Role definitions for RBAC system"""
    __tablename__ = "roles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(200))
    permissions: Mapped[dict] = mapped_column(JSON)  # Store role permissions as JSON
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")

class UserRole(Base):
    """Many-to-many relationship between users and roles"""
    __tablename__ = "user_roles"
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), primary_key=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    assigned_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    user = relationship("User", foreign_keys=[user_id])
    role = relationship("Role", back_populates="user_roles")
    assigner = relationship("User", foreign_keys=[assigned_by])

class RefreshToken(Base):
    """Refresh token storage with rotation support"""
    __tablename__ = "refresh_tokens"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    revoked_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    device_info: Mapped[str] = mapped_column(String(500), nullable=True)  # User agent, IP, etc.
    
    user = relationship("User")

class AuditLog(Base):
    """Audit logging for sensitive operations"""
    __tablename__ = "audit_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # order, route, customer, etc.
    resource_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    old_values: Mapped[dict] = mapped_column(JSON, nullable=True)  # Previous state for updates
    new_values: Mapped[dict] = mapped_column(JSON, nullable=True)  # New state for creates/updates
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)  # IPv4/IPv6
    user_agent: Mapped[str] = mapped_column(String(500), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("User")

ROLE_PERMISSIONS = {
    "manager": {
        "users": ["create", "read", "update", "delete"],
        "customers": ["create", "read", "update", "delete"],
        "orders": ["create", "read", "update", "delete"],
        "routes": ["create", "read", "update", "delete"],
        "vehicles": ["create", "read", "update", "delete"],
        "work_orders": ["create", "read", "update", "delete"],
        "production": ["create", "read", "update", "delete"],
        "financial": ["create", "read", "update", "delete"],
        "inventory": ["create", "read", "update", "delete"],
        "audit_logs": ["read"],
    },
    "dispatcher": {
        "customers": ["create", "read", "update"],
        "orders": ["create", "read", "update", "delete"],
        "routes": ["create", "read", "update", "delete"],
        "vehicles": ["read", "update"],
        "inventory": ["read", "update"],
    },
    "accountant": {
        "customers": ["read", "update"],
        "orders": ["read"],
        "financial": ["create", "read", "update", "delete"],
        "customer_pricing": ["create", "read", "update", "delete"],
    },
    "production": {
        "work_orders": ["create", "read", "update"],
        "production": ["create", "read", "update", "delete"],
        "inventory": ["read", "update"],
    },
    "technician": {
        "work_orders": ["read", "update"],
    },
    "driver": {
        "routes": ["read"],
        "orders": ["read", "update"],  # Update delivery status
    },
    "customer": {
        "orders": ["create", "read"],  # Own orders only
        "customers": ["read"],  # Own customer data only
    },
}

DEFAULT_ROLES = [
    {
        "name": "manager",
        "description": "Full system access - can manage all aspects of the business",
        "permissions": ROLE_PERMISSIONS["manager"]
    },
    {
        "name": "dispatcher",
        "description": "Route and order management - handles daily operations and logistics",
        "permissions": ROLE_PERMISSIONS["dispatcher"]
    },
    {
        "name": "accountant",
        "description": "Financial management - handles billing, payments, and financial reporting",
        "permissions": ROLE_PERMISSIONS["accountant"]
    },
    {
        "name": "production",
        "description": "Production oversight - manages manufacturing and inventory",
        "permissions": ROLE_PERMISSIONS["production"]
    },
    {
        "name": "technician",
        "description": "Maintenance and repairs - handles work orders and equipment maintenance",
        "permissions": ROLE_PERMISSIONS["technician"]
    },
    {
        "name": "driver",
        "description": "Delivery operations - accesses routes and updates delivery status",
        "permissions": ROLE_PERMISSIONS["driver"]
    },
    {
        "name": "customer",
        "description": "Customer portal access - can place orders and view account information",
        "permissions": ROLE_PERMISSIONS["customer"]
    },
]
