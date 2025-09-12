from sqlalchemy.orm import Session
from typing import Sequence, Optional
from ..models import FinancialDocument

class FinancialDocumentRepo:
    def __init__(self, db: Session):
        self.db = db

    def list(self, limit: int = 50, offset: int = 0) -> Sequence[FinancialDocument]:
        return self.db.query(FinancialDocument).offset(offset).limit(limit).all()

    def get(self, document_id: str) -> Optional[FinancialDocument]:
        return self.db.query(FinancialDocument).filter(FinancialDocument.id == document_id).first()

    def create(self, **data) -> FinancialDocument:
        obj = FinancialDocument(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, document_id: str, **data) -> Optional[FinancialDocument]:
        obj = self.get(document_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, document_id: str) -> bool:
        obj = self.get(document_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
