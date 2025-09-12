from sqlalchemy.orm import Session
from typing import Sequence, Optional, List
from ..models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepo:
    def __init__(self, db: Session):
        self.db = db

    def list(self, role: str | None = None) -> Sequence[User]:
        query = self.db.query(User)
        if role:
            query = query.filter(User.role == role)
        return query.all()

    def get(self, user_id: str) -> Optional[User]:
        return self.db.get(User, user_id)

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = self.get_by_username(username)
        if not user:
            return None
        if not pwd_context.verify(password, user.hashed_password):
            return None
        return user

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    def create(self, **data) -> User:
        if 'password' in data:
            data['hashed_password'] = pwd_context.hash(data.pop('password'))
        obj = User(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, user_id: str, **data) -> Optional[User]:
        obj = self.get(user_id)
        if not obj:
            return None
        if 'password' in data:
            data['hashed_password'] = pwd_context.hash(data.pop('password'))
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, user_id: str) -> bool:
        obj = self.get(user_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True

    def get_user_roles(self, user_id: str) -> List[str]:
        """Get list of role names for a user"""
        from ..auth_models import UserRole, Role
        
        roles = self.db.query(Role.name).join(UserRole).filter(
            UserRole.user_id == user_id
        ).all()
        
        return [role.name for role in roles]

    def assign_role(self, user_id: str, role_name: str, assigned_by: str = None) -> bool:
        """Assign a role to a user"""
        from ..auth_models import UserRole, Role
        
        role = self.db.query(Role).filter(Role.name == role_name).first()
        if not role:
            return False
        
        existing = self.db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role.id
        ).first()
        
        if existing:
            return True  # Already assigned
        
        user_role = UserRole(
            user_id=user_id,
            role_id=role.id,
            assigned_by=assigned_by
        )
        self.db.add(user_role)
        self.db.commit()
        return True

    def remove_role(self, user_id: str, role_name: str) -> bool:
        """Remove a role from a user"""
        from ..auth_models import UserRole, Role
        
        role = self.db.query(Role).filter(Role.name == role_name).first()
        if not role:
            return False
        
        user_role = self.db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role.id
        ).first()
        
        if user_role:
            self.db.delete(user_role)
            self.db.commit()
            return True
        
        return False
