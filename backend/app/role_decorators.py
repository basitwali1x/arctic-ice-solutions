"""
Phase 2: Role-Based Access Control Decorators
Decorators for protecting endpoints with role-based permissions
"""
from functools import wraps
from typing import List, Optional
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .db import get_db
from .auth_service import AuthService, get_current_user_from_token

security = HTTPBearer()

def require_auth(
    required_roles: Optional[List[str]] = None,
    required_permissions: Optional[dict] = None,
    audit_action: Optional[str] = None,
    audit_resource: Optional[str] = None
):
    """
    Decorator to require authentication and optionally specific roles/permissions
    
    Args:
        required_roles: List of role names that can access this endpoint
        required_permissions: Dict of {resource: [actions]} required
        audit_action: Action to log in audit trail
        audit_resource: Resource type for audit logging
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(
            *args,
            request: Request = None,
            credentials: HTTPAuthorizationCredentials = Depends(security),
            db: Session = Depends(get_db),
            **kwargs
        ):
            user_data = get_current_user_from_token(credentials, db)
            user = user_data["user"]
            user_roles = user_data["roles"]
            user_permissions = user_data["permissions"]
            
            if required_roles:
                if not any(role in user_roles for role in required_roles):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Access denied. Required roles: {required_roles}"
                    )
            
            if required_permissions:
                for resource, actions in required_permissions.items():
                    user_resource_permissions = user_permissions.get(resource, [])
                    if not any(action in user_resource_permissions for action in actions):
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Access denied. Required permissions: {resource}:{actions}"
                        )
            
            kwargs["current_user"] = user
            kwargs["current_user_roles"] = user_roles
            kwargs["current_user_permissions"] = user_permissions
            
            result = await func(*args, **kwargs) if hasattr(func, '__code__') and func.__code__.co_flags & 0x80 else func(*args, **kwargs)
            
            if audit_action and audit_resource:
                auth_service = AuthService(db)
                resource_id = None
                
                if hasattr(result, 'id'):
                    resource_id = str(result.id)
                elif 'id' in kwargs:
                    resource_id = str(kwargs['id'])
                
                auth_service.log_audit_event(
                    user_id=user.id,
                    action=audit_action,
                    resource_type=audit_resource,
                    resource_id=resource_id,
                    request=request
                )
            
            return result
        
        return wrapper
    return decorator

def require_roles(*roles: str):
    """Shorthand decorator to require specific roles"""
    return require_auth(required_roles=list(roles))

def require_permissions(**permissions):
    """Shorthand decorator to require specific permissions"""
    return require_auth(required_permissions=permissions)

def audit_action(action: str, resource: str):
    """Shorthand decorator to add audit logging"""
    return require_auth(audit_action=action, audit_resource=resource)

manager_only = require_roles("manager")
dispatcher_or_manager = require_roles("dispatcher", "manager")
accountant_or_manager = require_roles("accountant", "manager")
production_or_manager = require_roles("production", "manager")
technician_or_manager = require_roles("technician", "manager")

can_create_orders = require_permissions(orders=["create"])
can_update_orders = require_permissions(orders=["update"])
can_delete_orders = require_permissions(orders=["delete"])
can_view_financials = require_permissions(financials=["read"])
can_manage_financials = require_permissions(financials=["create", "update", "delete"])
