from sqlalchemy.orm import Session
from typing import Sequence, Optional
from ..models import Customer

class CustomerRepo:
    def __init__(self, db: Session):
        self.db = db

    def list(self, q: str | None = None, limit: int = 50, offset: int = 0) -> Sequence[Customer]:
        query = self.db.query(Customer)
        if q:
            query = query.filter(Customer.name.ilike(f"%{q}%"))
        return query.order_by(Customer.created_at.desc()).offset(offset).limit(limit).all()

    def get(self, customer_id: str) -> Optional[Customer]:
        return self.db.get(Customer, customer_id)

    def create(self, **data) -> Customer:
        obj = Customer(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, customer_id: str, **data) -> Optional[Customer]:
        obj = self.get(customer_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, customer_id: str) -> bool:
        obj = self.get(customer_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
