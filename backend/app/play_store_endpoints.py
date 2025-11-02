"""
API endpoints for Google Play Store deployment management
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import logging

from .db import get_db
from .repositories.play_store_deployments import PlayStoreDeploymentRepo
from .play_store_service import play_store_service
from .role_decorators import manager_only
from .main import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/deployments/play-store", tags=["Play Store Deployments"])


class PlayStoreDeploymentCreate(BaseModel):
    app_name: str
    release_track: str = "internal"
    version_code: Optional[int] = None
    version_name: Optional[str] = None
    app_bundle_path: Optional[str] = None


class PlayStoreDeploymentResponse(BaseModel):
    id: str
    app_name: str
    app_bundle_path: Optional[str]
    release_track: str
    version_code: int
    version_name: str
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    deployment_logs: Optional[str]
    created_by: Optional[str]

    class Config:
        from_attributes = True


class DeploymentStatusResponse(BaseModel):
    id: str
    status: str
    message: str
    logs: Optional[str]


def process_deployment(
    deployment_id: str,
    app_name: str,
    release_track: str,
    version_code: int,
    version_name: str,
    aab_path: Optional[str],
    db: Session
):
    """Background task to process the deployment"""
    repo = PlayStoreDeploymentRepo(db)
    
    try:
        repo.update(
            deployment_id,
            status="building",
            deployment_logs="Starting build process..."
        )
        
        if not aab_path:
            logger.info(f"Building AAB for {app_name}")
            build_result = play_store_service.build_aab(app_name, version_code, version_name)
            
            if not build_result["success"]:
                repo.update(
                    deployment_id,
                    status="failed",
                    error_message=build_result["message"],
                    completed_at=datetime.utcnow()
                )
                return
            
            aab_path = build_result["aab_path"]
            repo.update(
                deployment_id,
                app_bundle_path=aab_path,
                deployment_logs="AAB built successfully. Starting upload..."
            )
        
        repo.update(
            deployment_id,
            status="uploading",
            deployment_logs="Uploading to Google Play Store..."
        )
        
        logger.info(f"Deploying {app_name} to Play Store")
        deploy_result = play_store_service.deploy_to_play_store(
            app_name,
            aab_path,
            release_track
        )
        
        if deploy_result["success"]:
            repo.update(
                deployment_id,
                status="completed",
                deployment_logs=deploy_result["message"],
                completed_at=datetime.utcnow()
            )
        else:
            repo.update(
                deployment_id,
                status="failed",
                error_message=deploy_result["message"],
                completed_at=datetime.utcnow()
            )
            
    except Exception as e:
        logger.error(f"Deployment error: {e}")
        repo.update(
            deployment_id,
            status="failed",
            error_message=str(e),
            completed_at=datetime.utcnow()
        )


@router.post("", response_model=PlayStoreDeploymentResponse, status_code=status.HTTP_201_CREATED)
async def create_deployment(
    deployment: PlayStoreDeploymentCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(manager_only),
    db: Session = Depends(get_db)
):
    """
    Create a new Play Store deployment
    
    Requires manager role. Initiates a background job to build and deploy the app.
    """
    repo = PlayStoreDeploymentRepo(db)
    
    valid_apps = ["frontend-customer", "frontend-staff"]
    if deployment.app_name not in valid_apps:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid app name. Must be one of: {', '.join(valid_apps)}"
        )
    
    valid_tracks = ["internal", "alpha", "beta", "production"]
    if deployment.release_track not in valid_tracks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid release track. Must be one of: {', '.join(valid_tracks)}"
        )
    
    if not play_store_service.validate_credentials():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google Play Store credentials not configured"
        )
    
    if not deployment.version_code or not deployment.version_name:
        latest_version = repo.get_latest_version(deployment.app_name)
        
        if latest_version:
            version_info = play_store_service.increment_version(latest_version)
        else:
            version_info = play_store_service.get_latest_version_from_gradle(deployment.app_name)
        
        version_code = deployment.version_code or version_info["version_code"]
        version_name = deployment.version_name or version_info["version_name"]
    else:
        version_code = deployment.version_code
        version_name = deployment.version_name
    
    deployment_id = str(uuid.uuid4())
    deployment_obj = repo.create(
        id=deployment_id,
        app_name=deployment.app_name,
        app_bundle_path=deployment.app_bundle_path,
        release_track=deployment.release_track,
        version_code=version_code,
        version_name=version_name,
        status="pending",
        created_by=current_user.get("user_id")
    )
    
    background_tasks.add_task(
        process_deployment,
        deployment_id,
        deployment.app_name,
        deployment.release_track,
        version_code,
        version_name,
        deployment.app_bundle_path,
        db
    )
    
    return deployment_obj


@router.get("/{deployment_id}", response_model=PlayStoreDeploymentResponse)
async def get_deployment(
    deployment_id: str,
    current_user: dict = Depends(manager_only),
    db: Session = Depends(get_db)
):
    """Get deployment status and details"""
    repo = PlayStoreDeploymentRepo(db)
    deployment = repo.get(deployment_id)
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found"
        )
    
    return deployment


@router.get("", response_model=List[PlayStoreDeploymentResponse])
async def list_deployments(
    app_name: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(manager_only),
    db: Session = Depends(get_db)
):
    """
    List all deployments with optional filtering
    
    Query parameters:
    - app_name: Filter by app name (frontend-customer or frontend-staff)
    - status: Filter by status (pending, building, uploading, completed, failed)
    - limit: Maximum number of results (default 50)
    - offset: Pagination offset (default 0)
    """
    repo = PlayStoreDeploymentRepo(db)
    deployments = repo.list(
        app_name=app_name,
        status=status,
        limit=limit,
        offset=offset
    )
    
    return deployments


@router.post("/{deployment_id}/cancel", response_model=DeploymentStatusResponse)
async def cancel_deployment(
    deployment_id: str,
    current_user: dict = Depends(manager_only),
    db: Session = Depends(get_db)
):
    """
    Cancel a pending deployment
    
    Only deployments with status 'pending' can be cancelled.
    """
    repo = PlayStoreDeploymentRepo(db)
    deployment = repo.get(deployment_id)
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found"
        )
    
    if deployment.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel deployment with status '{deployment.status}'"
        )
    
    updated = repo.update(
        deployment_id,
        status="cancelled",
        error_message="Cancelled by user",
        completed_at=datetime.utcnow()
    )
    
    return DeploymentStatusResponse(
        id=deployment_id,
        status="cancelled",
        message="Deployment cancelled successfully",
        logs=updated.deployment_logs if updated else None
    )


@router.get("/{deployment_id}/status", response_model=DeploymentStatusResponse)
async def get_deployment_status(
    deployment_id: str,
    current_user: dict = Depends(manager_only),
    db: Session = Depends(get_db)
):
    """Get simplified deployment status for polling"""
    repo = PlayStoreDeploymentRepo(db)
    deployment = repo.get(deployment_id)
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found"
        )
    
    message = deployment.error_message if deployment.status == "failed" else deployment.deployment_logs or ""
    
    return DeploymentStatusResponse(
        id=deployment_id,
        status=deployment.status,
        message=message,
        logs=deployment.deployment_logs
    )
