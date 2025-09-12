from sqlalchemy.orm import Session
from typing import Sequence, Optional
from ..models import Expense

class ExpenseRepo:
    def __init__(self, db: Session):
        self.db = db

    def list(self, limit: int = 50, offset: int = 0) -> Sequence[Expense]:
        return self.db.query(Expense).offset(offset).limit(limit).all()

    def get(self, expense_id: str) -> Optional[Expense]:
        return self.db.query(Expense).filter(Expense.id == expense_id).first()

    def create(self, **data) -> Expense:
        obj = Expense(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, expense_id: str, **data) -> Optional[Expense]:
        obj = self.get(expense_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, expense_id: str) -> bool:
        obj = self.get(expense_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
