"""
Phase 2: Enhanced Authentication Service
Handles JWT tokens, refresh tokens, role-based access, and audit logging
"""
from __future__ import annotations
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from .auth_models import RefreshToken, AuditLog, Role, UserRole
from .models import User
import os

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-for-local-development-only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

security = HTTPBearer()

class AuthService:
    """Enhanced authentication service with refresh tokens and RBAC"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_tokens(self, user: User, device_info: str = None) -> Dict[str, Any]:
        """Create both access and refresh tokens for a user"""
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self._create_access_token(
            data={"sub": user.username, "user_id": user.id, "roles": self._get_user_roles(user.id)},
            expires_delta=access_token_expires
        )
        
        refresh_token = self._create_refresh_token(user.id, device_info)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
    
    def _create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def _create_refresh_token(self, user_id: int, device_info: str = None) -> str:
        """Create and store refresh token"""
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            device_info=device_info
        )
        self.db.add(refresh_token)
        self.db.commit()
        
        return token
    
    def refresh_access_token(self, refresh_token: str, device_info: str = None) -> Dict[str, Any]:
        """Refresh access token using refresh token (with rotation)"""
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        db_token = self.db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        ).first()
        
        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        user = self.db.query(User).filter(User.id == db_token.user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        db_token.is_revoked = True
        db_token.revoked_at = datetime.utcnow()
        
        new_tokens = self.create_tokens(user, device_info)
        
        self.db.commit()
        return new_tokens
    
    def revoke_refresh_token(self, refresh_token: str) -> bool:
        """Revoke a refresh token (logout)"""
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        db_token = self.db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False
        ).first()
        
        if db_token:
            db_token.is_revoked = True
            db_token.revoked_at = datetime.utcnow()
            self.db.commit()
            return True
        
        return False
    
    def revoke_all_user_tokens(self, user_id: int) -> int:
        """Revoke all refresh tokens for a user"""
        count = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        ).update({
            "is_revoked": True,
            "revoked_at": datetime.utcnow()
        })
        self.db.commit()
        return count
    
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode access token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    def _get_user_roles(self, user_id: int) -> List[str]:
        """Get list of role names for a user"""
        roles = self.db.query(Role.name).join(UserRole).filter(
            UserRole.user_id == user_id
        ).all()
        return [role.name for role in roles]
    
    def check_permission(self, user_roles: List[str], resource: str, action: str) -> bool:
        """Check if user has permission for a specific action on a resource"""
        from .auth_models import ROLE_PERMISSIONS
        
        for role_name in user_roles:
            role_perms = ROLE_PERMISSIONS.get(role_name, {})
            resource_perms = role_perms.get(resource, [])
            if action in resource_perms:
                return True
        
        return False
    
    def log_audit_event(
        self,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: str,
        old_values: Dict[str, Any] = None,
        new_values: Dict[str, Any] = None,
        request: Request = None
    ):
        """Log an audit event"""
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
        
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(audit_log)
        self.db.commit()

def get_current_user_from_token(credentials: HTTPAuthorizationCredentials, db: Session) -> Dict[str, Any]:
    """Extract current user info from JWT token"""
    auth_service = AuthService(db)
    payload = auth_service.verify_access_token(credentials.credentials)
    
    user = db.query(User).filter(User.id == payload.get("user_id")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return {
        "user": user,
        "roles": payload.get("roles", []),
        "token_payload": payload
    }

def require_permission(resource: str, action: str):
    """Decorator to require specific permission for an endpoint"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            current_user_info = kwargs.get("current_user")
            if not current_user_info:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_roles = current_user_info.get("roles", [])
            auth_service = AuthService(None)  # No DB needed for permission check
            
            if not auth_service.check_permission(user_roles, resource, action):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions for {action} on {resource}"
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
