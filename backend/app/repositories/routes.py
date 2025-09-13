from sqlalchemy.orm import Session
from typing import Sequence, Optional
from ..models import Route

class RouteRepo:
    def __init__(self, db: Session):
        self.db = db

    def list(self, location_id: str = None, limit: int = 50, offset: int = 0) -> Sequence[Route]:
        query = self.db.query(Route)
        if location_id:
            query = query.filter(Route.location_id == location_id)
        return query.order_by(Route.date.desc()).offset(offset).limit(limit).all()

    def get(self, route_id: str) -> Optional[Route]:
        return self.db.query(Route).filter(Route.id == route_id).first()

    def create(self, **data) -> Route:
        obj = Route(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, route_id: str, **data) -> Optional[Route]:
        obj = self.get(route_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, route_id: str) -> bool:
        obj = self.get(route_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
