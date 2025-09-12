from sqlalchemy.orm import Session
from typing import Sequence, Optional
from ..models import Vehicle

class VehicleRepo:
    def __init__(self, db: Session):
        self.db = db

    def list(self, location_id: str = None, limit: int = 50, offset: int = 0) -> Sequence[Vehicle]:
        query = self.db.query(Vehicle)
        if location_id:
            query = query.filter(Vehicle.location_id == location_id)
        return query.offset(offset).limit(limit).all()

    def get(self, vehicle_id: str) -> Optional[Vehicle]:
        return self.db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

    def create(self, **data) -> Vehicle:
        obj = Vehicle(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, vehicle_id: str, **data) -> Optional[Vehicle]:
        obj = self.get(vehicle_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, vehicle_id: str) -> bool:
        obj = self.get(vehicle_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
