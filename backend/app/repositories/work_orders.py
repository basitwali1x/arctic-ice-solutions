from sqlalchemy.orm import Session
from typing import Sequence, Optional
from ..models import WorkOrder

class WorkOrderRepo:
    def __init__(self, db: Session):
        self.db = db

    def list(self, status: str = None, limit: int = 50, offset: int = 0) -> Sequence[WorkOrder]:
        query = self.db.query(WorkOrder)
        if status:
            query = query.filter(WorkOrder.status == status)
        return query.order_by(WorkOrder.created_at.desc()).offset(offset).limit(limit).all()

    def get(self, work_order_id: str) -> Optional[WorkOrder]:
        return self.db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()

    def create(self, **data) -> WorkOrder:
        obj = WorkOrder(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, work_order_id: str, **data) -> Optional[WorkOrder]:
        obj = self.get(work_order_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, work_order_id: str) -> bool:
        obj = self.get(work_order_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
