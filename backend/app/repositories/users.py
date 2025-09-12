from sqlalchemy.orm import Session
from typing import Sequence, Optional
from passlib.context import CryptContext
from ..models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepo:
    def __init__(self, db: Session):
        self.db = db

    def list(self, limit: int = 50, offset: int = 0) -> Sequence[User]:
        return self.db.query(User).offset(offset).limit(limit).all()

    def get(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, **data) -> User:
        if "password" in data:
            data["hashed_password"] = pwd_context.hash(data.pop("password"))
        
        obj = User(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, user_id: int, **data) -> Optional[User]:
        obj = self.get(user_id)
        if not obj:
            return None
        
        if "password" in data:
            data["hashed_password"] = pwd_context.hash(data.pop("password"))
        
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, user_id: int) -> bool:
        obj = self.get(user_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password"""
        user = self.get_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def get_user_roles(self, user_id: int) -> list[str]:
        """Get list of role names for a user"""
        from ..auth_models import Role, UserRole
        roles = self.db.query(Role.name).join(UserRole).filter(
            UserRole.user_id == user_id
        ).all()
        return [role.name for role in roles]
