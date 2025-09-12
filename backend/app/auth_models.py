"""
Phase 2: Authentication Models
SQLAlchemy models for JWT authentication, RBAC, and audit logging
"""
from __future__ import annotations
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from .db import Base

class Role(Base):
    __tablename__ = "roles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255))
    permissions: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")

class UserRole(Base):
    __tablename__ = "user_roles"
    
    user_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), primary_key=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    assigned_by: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=True)
    
    user = relationship("app.models.User", foreign_keys=[user_id])
    role = relationship("Role", back_populates="user_roles")
    assigner = relationship("app.models.User", foreign_keys=[assigned_by])

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    device_info: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    user = relationship("app.models.User")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_id: Mapped[str] = mapped_column(String(100), nullable=True)
    old_values: Mapped[dict] = mapped_column(JSON, nullable=True)
    new_values: Mapped[dict] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(500), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("app.models.User")

DEFAULT_ROLES = [
    {
        "name": "manager",
        "description": "Full system access - can manage all operations, users, and view all data",
        "permissions": {
            "customers": ["create", "read", "update", "delete"],
            "orders": ["create", "read", "update", "delete"],
            "routes": ["create", "read", "update", "delete"],
            "vehicles": ["create", "read", "update", "delete"],
            "work_orders": ["create", "read", "update", "delete"],
            "production": ["create", "read", "update", "delete"],
            "inventory": ["create", "read", "update", "delete"],
            "financials": ["create", "read", "update", "delete"],
            "users": ["create", "read", "update", "delete"],
            "roles": ["create", "read", "update", "delete"],
            "audit_logs": ["read"],
            "reports": ["read", "export"]
        }
    },
    {
        "name": "dispatcher",
        "description": "Route and order management - can manage routes, orders, and customer interactions",
        "permissions": {
            "customers": ["create", "read", "update"],
            "orders": ["create", "read", "update", "delete"],
            "routes": ["create", "read", "update", "delete"],
            "vehicles": ["read", "update"],
            "work_orders": ["read", "update"],
            "production": ["read"],
            "inventory": ["read"],
            "reports": ["read"]
        }
    },
    {
        "name": "accountant",
        "description": "Financial operations - can manage financials, view orders, and generate reports",
        "permissions": {
            "customers": ["read", "update"],
            "orders": ["read", "update"],
            "routes": ["read"],
            "vehicles": ["read"],
            "work_orders": ["read"],
            "production": ["read"],
            "inventory": ["read"],
            "financials": ["create", "read", "update", "delete"],
            "reports": ["read", "export"]
        }
    },
    {
        "name": "production",
        "description": "Production operations - can manage production entries and work orders",
        "permissions": {
            "customers": ["read"],
            "orders": ["read"],
            "routes": ["read"],
            "vehicles": ["read"],
            "work_orders": ["create", "read", "update"],
            "production": ["create", "read", "update", "delete"],
            "inventory": ["read", "update"],
            "reports": ["read"]
        }
    },
    {
        "name": "technician",
        "description": "Maintenance operations - can only manage work orders and view basic information",
        "permissions": {
            "customers": ["read"],
            "orders": ["read"],
            "routes": ["read"],
            "vehicles": ["read"],
            "work_orders": ["read", "update"],
            "production": ["read"],
            "inventory": ["read"]
        }
    },
    {
        "name": "driver",
        "description": "Driver operations - can view assigned routes and update delivery status",
        "permissions": {
            "customers": ["read"],
            "orders": ["read", "update"],
            "routes": ["read", "update"],
            "vehicles": ["read"],
            "work_orders": ["read"],
            "reports": ["read"]
        }
    },
    {
        "name": "customer",
        "description": "Customer portal access - can view own orders and account information",
        "permissions": {
            "customers": ["read"],
            "orders": ["read"],
            "reports": ["read"]
        }
    }
]
