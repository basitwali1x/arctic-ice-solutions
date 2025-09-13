from sqlalchemy.orm import Session
from typing import Sequence, Optional
from ..models import Location

class LocationRepo:
    def __init__(self, db: Session):
        self.db = db

    def list(self, limit: int = 50, offset: int = 0) -> Sequence[Location]:
        return self.db.query(Location).offset(offset).limit(limit).all()

    def get(self, location_id: str) -> Optional[Location]:
        return self.db.query(Location).filter(Location.id == location_id).first()

    def create(self, **data) -> Location:
        obj = Location(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, location_id: str, **data) -> Optional[Location]:
        obj = self.get(location_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, location_id: str) -> bool:
        obj = self.get(location_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
