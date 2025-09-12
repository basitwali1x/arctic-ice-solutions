"""
Phase 2: Authentication Service
JWT token management, role-based permissions, and audit logging
"""
from __future__ import annotations
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from .auth_models import Role, UserRole, RefreshToken, AuditLog
from .models import User
from .repositories.users import UserRepo

SECRET_KEY = "your-secret-key-change-in-production"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepo(db)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, user: User, device_info: str = "Unknown") -> str:
        """Create and store refresh token"""
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            device_info=device_info,
            expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        self.db.add(refresh_token)
        self.db.commit()
        
        return token

    def create_tokens(self, user: User, device_info: str = "Unknown") -> Dict[str, Any]:
        """Create both access and refresh tokens"""
        user_roles = self.user_repo.get_user_roles(user.id)
        
        access_token_data = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "roles": user_roles
        }
        access_token = self.create_access_token(access_token_data)
        
        refresh_token = self.create_refresh_token(user, device_info)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def refresh_access_token(self, refresh_token: str, device_info: str = "Unknown") -> Dict[str, Any]:
        """Refresh access token using refresh token (with rotation)"""
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        stored_token = self.db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_active == True,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.utcnow()
        ).first()
        
        if not stored_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        user = self.db.query(User).filter(User.id == stored_token.user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        stored_token.revoked_at = datetime.utcnow()
        stored_token.is_active = False
        
        new_tokens = self.create_tokens(user, device_info)
        
        self.db.commit()
        return new_tokens

    def revoke_refresh_token(self, refresh_token: str) -> bool:
        """Revoke a refresh token (logout)"""
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        stored_token = self.db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_active == True
        ).first()
        
        if stored_token:
            stored_token.revoked_at = datetime.utcnow()
            stored_token.is_active = False
            self.db.commit()
            return True
        
        return False

    def get_user_permissions(self, user_id: str) -> Dict[str, List[str]]:
        """Get all permissions for a user based on their roles"""
        user_roles = self.db.query(Role).join(UserRole).filter(
            UserRole.user_id == user_id
        ).all()
        
        permissions = {}
        for role in user_roles:
            if role.permissions:
                for resource, actions in role.permissions.items():
                    if resource not in permissions:
                        permissions[resource] = []
                    permissions[resource].extend(actions)
        
        for resource in permissions:
            permissions[resource] = list(set(permissions[resource]))
        
        return permissions

    def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """Check if user has specific permission"""
        permissions = self.get_user_permissions(user_id)
        return resource in permissions and action in permissions[resource]

    def log_audit_event(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str = None,
        old_values: Dict = None,
        new_values: Dict = None,
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

def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials,
    db: Session
) -> Dict[str, Any]:
    """Dependency to get current user from JWT token"""
    auth_service = AuthService(db)
    
    try:
        payload = auth_service.verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled"
            )
        
        user_roles = auth_service.user_repo.get_user_roles(user_id)
        permissions = auth_service.get_user_permissions(user_id)
        
        return {
            "user": user,
            "roles": user_roles,
            "permissions": permissions,
            "token_payload": payload
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
