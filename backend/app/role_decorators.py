"""
Phase 2: Role-based Access Control Decorators
Provides decorators and middleware for endpoint protection
"""
from functools import wraps
from typing import List, Callable, Any
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from .db import get_db
from .auth_service import AuthService
from .auth_endpoints import get_current_user_with_roles

def require_permissions(resource: str, actions: List[str]):
    """
    Decorator to require specific permissions for an endpoint
    
    Args:
        resource: The resource type (e.g., 'orders', 'routes', 'financial')
        actions: List of required actions (e.g., ['read'], ['create', 'update'])
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_roles = current_user.get("roles", [])
            auth_service = AuthService(None)  # No DB needed for permission check
            
            has_permission = False
            for action in actions:
                if auth_service.check_permission(user_roles, resource, action):
                    has_permission = True
                    break
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Requires {actions} on {resource}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_roles(*allowed_roles: str):
    """
    Decorator to require specific roles for an endpoint
    
    Args:
        allowed_roles: Roles that are allowed to access this endpoint
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_roles = current_user.get("roles", [])
            if not any(role in user_roles for role in allowed_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Requires one of: {', '.join(allowed_roles)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def manager_only(func: Callable) -> Callable:
    """Decorator for manager-only endpoints"""
    return require_roles("manager")(func)

def dispatcher_or_manager(func: Callable) -> Callable:
    """Decorator for dispatcher or manager access"""
    return require_roles("dispatcher", "manager")(func)

def accountant_or_manager(func: Callable) -> Callable:
    """Decorator for accountant or manager access"""
    return require_roles("accountant", "manager")(func)

def production_or_manager(func: Callable) -> Callable:
    """Decorator for production or manager access"""
    return require_roles("production", "manager")(func)

def technician_or_above(func: Callable) -> Callable:
    """Decorator for technician, production, or manager access"""
    return require_roles("technician", "production", "manager")(func)

def can_read_orders(func: Callable) -> Callable:
    """Decorator for endpoints that read order data"""
    return require_permissions("orders", ["read"])(func)

def can_modify_orders(func: Callable) -> Callable:
    """Decorator for endpoints that create/update orders"""
    return require_permissions("orders", ["create", "update"])(func)

def can_delete_orders(func: Callable) -> Callable:
    """Decorator for endpoints that delete orders"""
    return require_permissions("orders", ["delete"])(func)

def can_read_routes(func: Callable) -> Callable:
    """Decorator for endpoints that read route data"""
    return require_permissions("routes", ["read"])(func)

def can_modify_routes(func: Callable) -> Callable:
    """Decorator for endpoints that create/update routes"""
    return require_permissions("routes", ["create", "update"])(func)

def can_read_financial(func: Callable) -> Callable:
    """Decorator for endpoints that read financial data"""
    return require_permissions("financial", ["read"])(func)

def can_modify_financial(func: Callable) -> Callable:
    """Decorator for endpoints that create/update financial data"""
    return require_permissions("financial", ["create", "update"])(func)

def can_read_work_orders(func: Callable) -> Callable:
    """Decorator for endpoints that read work order data"""
    return require_permissions("work_orders", ["read"])(func)

def can_modify_work_orders(func: Callable) -> Callable:
    """Decorator for endpoints that create/update work orders"""
    return require_permissions("work_orders", ["create", "update"])(func)

def can_manage_users(func: Callable) -> Callable:
    """Decorator for user management endpoints"""
    return require_permissions("users", ["create", "update", "delete"])(func)

def audit_action(action: str, resource_type: str):
    """
    Decorator to automatically log actions to audit trail
    
    Args:
        action: The action being performed (CREATE, UPDATE, DELETE)
        resource_type: The type of resource being acted upon
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            current_user = kwargs.get("current_user")
            db = kwargs.get("db")
            
            if current_user and db:
                auth_service = AuthService(db)
                
                resource_id = "unknown"
                if hasattr(result, "id"):
                    resource_id = str(result.id)
                elif "id" in kwargs:
                    resource_id = str(kwargs["id"])
                
                auth_service.log_audit_event(
                    user_id=current_user["user"].id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    new_values=result.__dict__ if hasattr(result, "__dict__") else None
                )
            
            return result
        return wrapper
    return decorator

def audit_create(resource_type: str):
    """Decorator to audit CREATE operations"""
    return audit_action("CREATE", resource_type)

def audit_update(resource_type: str):
    """Decorator to audit UPDATE operations"""
    return audit_action("UPDATE", resource_type)

def audit_delete(resource_type: str):
    """Decorator to audit DELETE operations"""
    return audit_action("DELETE", resource_type)
