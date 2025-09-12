from sqlalchemy.orm import Session
from typing import Sequence, Optional
from ..models import Product

class ProductRepo:
    def __init__(self, db: Session):
        self.db = db

    def list(self, limit: int = 50, offset: int = 0) -> Sequence[Product]:
        return self.db.query(Product).offset(offset).limit(limit).all()

    def get(self, product_id: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def create(self, **data) -> Product:
        obj = Product(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, product_id: str, **data) -> Optional[Product]:
        obj = self.get(product_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, product_id: str) -> bool:
        obj = self.get(product_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
