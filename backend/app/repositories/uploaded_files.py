from sqlalchemy.orm import Session
from typing import Sequence, Optional
from ..models import UploadedFile

class UploadedFileRepo:
    def __init__(self, db: Session):
        self.db = db

    def list(self, limit: int = 50, offset: int = 0, location_id: Optional[str] = None, category: Optional[str] = None) -> Sequence[UploadedFile]:
        query = self.db.query(UploadedFile)
        if location_id:
            query = query.filter(UploadedFile.location_id == location_id)
        if category:
            query = query.filter(UploadedFile.category == category)
        return query.order_by(UploadedFile.uploaded_at.desc()).offset(offset).limit(limit).all()

    def get(self, file_id: str) -> Optional[UploadedFile]:
        return self.db.query(UploadedFile).filter(UploadedFile.id == file_id).first()

    def create(self, **data) -> UploadedFile:
        obj = UploadedFile(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, file_id: str, **data) -> Optional[UploadedFile]:
        obj = self.get(file_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, file_id: str) -> bool:
        obj = self.get(file_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
