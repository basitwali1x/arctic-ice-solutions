from sqlalchemy.orm import Session
from typing import Sequence, Optional
from ..models import Order

class OrderRepo:
    def __init__(self, db: Session):
        self.db = db

    def list(self, customer_id: str = None, limit: int = 50, offset: int = 0) -> Sequence[Order]:
        query = self.db.query(Order)
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        return query.order_by(Order.order_date.desc()).offset(offset).limit(limit).all()

    def get(self, order_id: str) -> Optional[Order]:
        return self.db.query(Order).filter(Order.id == order_id).first()

    def create(self, **data) -> Order:
        obj = Order(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, order_id: str, **data) -> Optional[Order]:
        obj = self.get(order_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, order_id: str) -> bool:
        obj = self.get(order_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
