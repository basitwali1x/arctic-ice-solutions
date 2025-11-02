from sqlalchemy.orm import Session
from typing import Sequence, Optional
from ..models import PlayStoreDeployment
from datetime import datetime

class PlayStoreDeploymentRepo:
    def __init__(self, db: Session):
        self.db = db

    def list(
        self, 
        app_name: str | None = None, 
        status: str | None = None,
        limit: int = 50, 
        offset: int = 0
    ) -> Sequence[PlayStoreDeployment]:
        query = self.db.query(PlayStoreDeployment)
        if app_name:
            query = query.filter(PlayStoreDeployment.app_name == app_name)
        if status:
            query = query.filter(PlayStoreDeployment.status == status)
        return query.order_by(PlayStoreDeployment.created_at.desc()).offset(offset).limit(limit).all()

    def get(self, deployment_id: str) -> Optional[PlayStoreDeployment]:
        return self.db.get(PlayStoreDeployment, deployment_id)

    def create(self, **data) -> PlayStoreDeployment:
        obj = PlayStoreDeployment(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, deployment_id: str, **data) -> Optional[PlayStoreDeployment]:
        obj = self.get(deployment_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        obj.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, deployment_id: str) -> bool:
        obj = self.get(deployment_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True

    def get_latest_version(self, app_name: str) -> Optional[int]:
        """Get the latest version code for an app"""
        latest = self.db.query(PlayStoreDeployment).filter(
            PlayStoreDeployment.app_name == app_name
        ).order_by(PlayStoreDeployment.version_code.desc()).first()
        return latest.version_code if latest else None
