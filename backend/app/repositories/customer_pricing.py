from sqlalchemy.orm import Session
from typing import Sequence, Optional
from ..models import CustomerPricing

class CustomerPricingRepo:
    def __init__(self, db: Session):
        self.db = db

    def list(self, customer_id: str = None, limit: int = 50, offset: int = 0) -> Sequence[CustomerPricing]:
        query = self.db.query(CustomerPricing)
        if customer_id:
            query = query.filter(CustomerPricing.customer_id == customer_id)
        return query.offset(offset).limit(limit).all()

    def get(self, pricing_id: str) -> Optional[CustomerPricing]:
        return self.db.query(CustomerPricing).filter(CustomerPricing.id == pricing_id).first()

    def get_by_customer_and_product(self, customer_id: str, product_id: str) -> Optional[CustomerPricing]:
        return self.db.query(CustomerPricing).filter(
            CustomerPricing.customer_id == customer_id,
            CustomerPricing.product_id == product_id
        ).first()

    def create(self, **data) -> CustomerPricing:
        obj = CustomerPricing(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, pricing_id: str, **data) -> Optional[CustomerPricing]:
        obj = self.get(pricing_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, pricing_id: str) -> bool:
        obj = self.get(pricing_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
