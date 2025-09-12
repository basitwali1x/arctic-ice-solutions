from sqlalchemy.orm import Session
from typing import Sequence, Optional
from ..models import User

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

    def create(self, **data) -> User:
        obj = User(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, user_id: str, **data) -> Optional[User]:
        obj = self.get(user_id)
        if not obj:
            return None
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
