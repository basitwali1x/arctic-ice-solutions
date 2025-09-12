from sqlalchemy.orm import Session
from typing import Sequence, Optional
from ..models import ProductionEntry

class ProductionEntryRepo:
    def __init__(self, db: Session):
        self.db = db

    def list(self, limit: int = 50, offset: int = 0) -> Sequence[ProductionEntry]:
        return self.db.query(ProductionEntry).offset(offset).limit(limit).all()

    def get(self, entry_id: str) -> Optional[ProductionEntry]:
        return self.db.query(ProductionEntry).filter(ProductionEntry.id == entry_id).first()

    def create(self, **data) -> ProductionEntry:
        obj = ProductionEntry(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, entry_id: str, **data) -> Optional[ProductionEntry]:
        obj = self.get(entry_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, entry_id: str) -> bool:
        obj = self.get(entry_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
