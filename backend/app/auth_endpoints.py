"""
Phase 2: Enhanced Authentication Endpoints
Implements JWT with refresh tokens, role-based access, and audit logging
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel

from .db import get_db
from .auth_service import AuthService, get_current_user_from_token
from .auth_models import Role, UserRole, AuditLog, DEFAULT_ROLES
from .models import User
from .repositories.users import UserRepo

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    roles: List[str]
    location_id: Optional[str] = None
    is_active: bool

class RoleResponse(BaseModel):
    id: int
    name: str
    description: str
    permissions: Dict[str, List[str]]

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()

def get_current_user_with_roles(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Dependency to get current user with role information"""
    return get_current_user_from_token(credentials, db)

def require_role(*allowed_roles: str):
    """Decorator to require specific roles for an endpoint"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            current_user_info = kwargs.get("current_user")
            if not current_user_info:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_roles = current_user_info.get("roles", [])
            if not any(role in user_roles for role in allowed_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires one of these roles: {', '.join(allowed_roles)}"
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

@router.post("/login", response_model=TokenResponse)
async def login(
    login_request: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Enhanced login with access + refresh tokens"""
    auth_service = AuthService(db)
    user_repo = UserRepo(db)
    
    user = user_repo.authenticate_user(login_request.username, login_request.password)
    if not user:
        auth_service.log_audit_event(
            user_id=0,  # Unknown user
            action="LOGIN_FAILED",
            resource_type="auth",
            resource_id=login_request.username,
            request=request
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled"
        )
    
    device_info = request.headers.get("user-agent", "Unknown")
    tokens = auth_service.create_tokens(user, device_info)
    
    auth_service.log_audit_event(
        user_id=user.id,
        action="LOGIN",
        resource_type="auth",
        resource_id=str(user.id),
        request=request
    )
    
    return TokenResponse(**tokens)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token (with rotation)"""
    auth_service = AuthService(db)
    
    try:
        device_info = request.headers.get("user-agent", "Unknown")
        tokens = auth_service.refresh_access_token(refresh_request.refresh_token, device_info)
        return TokenResponse(**tokens)
    except HTTPException as e:
        auth_service.log_audit_event(
            user_id=0,  # Unknown user for failed refresh
            action="REFRESH_FAILED",
            resource_type="auth",
            resource_id="refresh_token",
            request=request
        )
        raise e

@router.post("/logout")
async def logout(
    refresh_token: str,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user_with_roles),
    db: Session = Depends(get_db)
):
    """Logout and revoke refresh token"""
    auth_service = AuthService(db)
    
    revoked = auth_service.revoke_refresh_token(refresh_token)
    
    auth_service.log_audit_event(
        user_id=current_user["user"].id,
        action="LOGOUT",
        resource_type="auth",
        resource_id=str(current_user["user"].id),
        request=request
    )
    
    return {"message": "Successfully logged out", "revoked": revoked}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user_with_roles)
):
    """Get current user information with roles"""
    user = current_user["user"]
    roles = current_user["roles"]
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        roles=roles,
        location_id=user.location_id,
        is_active=user.is_active
    )

@router.get("/roles", response_model=List[RoleResponse])
@require_role("manager")
async def list_roles(
    current_user: Dict[str, Any] = Depends(get_current_user_with_roles),
    db: Session = Depends(get_db)
):
    """List all available roles (manager only)"""
    roles = db.query(Role).all()
    return [
        RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            permissions=role.permissions or {}
        )
        for role in roles
    ]

@router.post("/users/{user_id}/roles/{role_name}")
@require_role("manager")
async def assign_role_to_user(
    user_id: int,
    role_name: str,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user_with_roles),
    db: Session = Depends(get_db)
):
    """Assign a role to a user (manager only)"""
    auth_service = AuthService(db)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    existing = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="User already has this role")
    
    user_role = UserRole(
        user_id=user_id,
        role_id=role.id,
        assigned_by=current_user["user"].id
    )
    db.add(user_role)
    db.commit()
    
    auth_service.log_audit_event(
        user_id=current_user["user"].id,
        action="ASSIGN_ROLE",
        resource_type="user_role",
        resource_id=f"{user_id}:{role_name}",
        new_values={"user_id": user_id, "role_name": role_name},
        request=request
    )
    
    return {"message": f"Role '{role_name}' assigned to user {user_id}"}

@router.delete("/users/{user_id}/roles/{role_name}")
@require_role("manager")
async def remove_role_from_user(
    user_id: int,
    role_name: str,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user_with_roles),
    db: Session = Depends(get_db)
):
    """Remove a role from a user (manager only)"""
    auth_service = AuthService(db)
    
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role.id
    ).first()
    
    if not user_role:
        raise HTTPException(status_code=404, detail="User does not have this role")
    
    db.delete(user_role)
    db.commit()
    
    auth_service.log_audit_event(
        user_id=current_user["user"].id,
        action="REMOVE_ROLE",
        resource_type="user_role",
        resource_id=f"{user_id}:{role_name}",
        old_values={"user_id": user_id, "role_name": role_name},
        request=request
    )
    
    return {"message": f"Role '{role_name}' removed from user {user_id}"}

@router.get("/audit-logs")
@require_role("manager")
async def get_audit_logs(
    limit: int = 100,
    offset: int = 0,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user_with_roles),
    db: Session = Depends(get_db)
):
    """Get audit logs (manager only)"""
    query = db.query(AuditLog).order_by(AuditLog.timestamp.desc())
    
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    
    logs = query.offset(offset).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "old_values": log.old_values,
            "new_values": log.new_values,
            "ip_address": log.ip_address,
            "timestamp": log.timestamp
        }
        for log in logs
    ]

def initialize_roles(db: Session):
    """Initialize default roles if they don't exist"""
    for role_data in DEFAULT_ROLES:
        existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing_role:
            role = Role(
                name=role_data["name"],
                description=role_data["description"],
                permissions=role_data["permissions"]
            )
            db.add(role)
    
    db.commit()
    print(f"Initialized {len(DEFAULT_ROLES)} default roles")
