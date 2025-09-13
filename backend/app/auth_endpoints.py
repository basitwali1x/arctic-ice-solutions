"""
Phase 2: Authentication Endpoints
JWT authentication endpoints with refresh token support
"""
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .db import get_db
from .auth_service import AuthService
from .repositories.users import UserRepo

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: Dict[str, Any]

class RefreshRequest(BaseModel):
    refresh_token: str

class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens
    """
    user_repo = UserRepo(db)
    auth_service = AuthService(db)
    
    user = user_repo.authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    device_info = f"{request.headers.get('user-agent', 'Unknown')} - {request.client.host if request.client else 'Unknown'}"
    
    tokens = auth_service.create_tokens(user, device_info)
    
    user_roles = user_repo.get_user_roles(user.id)
    
    auth_service.log_audit_event(
        user_id=user.id,
        action="login",
        resource_type="auth",
        request=request
    )
    
    return LoginResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        expires_in=tokens["expires_in"],
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "roles": user_roles,
            "is_active": user.is_active
        }
    )

@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    request: Request,
    refresh_data: RefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token (with rotation)
    """
    auth_service = AuthService(db)
    
    device_info = f"{request.headers.get('user-agent', 'Unknown')} - {request.client.host if request.client else 'Unknown'}"
    
    try:
        tokens = auth_service.refresh_access_token(refresh_data.refresh_token, device_info)
        
        return RefreshResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.post("/logout")
async def logout(
    request: Request,
    refresh_data: RefreshRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Logout user and revoke refresh token
    """
    auth_service = AuthService(db)
    
    try:
        payload = auth_service.verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        revoked = auth_service.revoke_refresh_token(refresh_data.refresh_token)
        
        if user_id:
            auth_service.log_audit_event(
                user_id=user_id,
                action="logout",
                resource_type="auth",
                request=request
            )
        
        return {"message": "Successfully logged out", "revoked": revoked}
    
    except Exception as e:
        auth_service.revoke_refresh_token(refresh_data.refresh_token)
        return {"message": "Logged out", "revoked": True}

@router.get("/me")
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current user information from JWT token
    """
    from .auth_service import get_current_user_from_token
    
    user_data = get_current_user_from_token(credentials, db)
    user = user_data["user"]
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "roles": user_data["roles"],
        "permissions": user_data["permissions"],
        "is_active": user.is_active
    }

@router.get("/roles")
async def get_user_roles(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current user's roles and permissions
    """
    from .auth_service import get_current_user_from_token
    
    user_data = get_current_user_from_token(credentials, db)
    
    return {
        "user_id": user_data["user"].id,
        "roles": user_data["roles"],
        "permissions": user_data["permissions"]
    }
