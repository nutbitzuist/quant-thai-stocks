"""
Scheduled Scans API Routes
Manage scheduled daily model scans with user ownership
Backed by PostgreSQL
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.middleware.auth import require_user_id, verify_api_key
from app.validation import validate_name, validate_schedule_time, validate_days
from app.database import get_db
from app.database.models import ScheduledScan as DBScheduledScan
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scheduled-scans", tags=["scheduled-scans"])


class ScheduledScanCreate(BaseModel):
    model_id: str
    universe: str
    schedule_time: str  # HH:MM format
    days: List[str]  # ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    enabled: bool = True
    parameters: Optional[dict] = None


class ScheduledScanUpdate(BaseModel):
    enabled: bool


class ScheduledScanResponse(BaseModel):
    id: str
    user_id: str
    model_id: str
    model_name: Optional[str] = None
    universe: str
    schedule_time: str
    days: List[str]
    enabled: bool
    parameters: Optional[dict] = None
    created_at: str
    last_run: Optional[str] = None
    deleted_at: Optional[str] = None



# Cache for model names to avoid repeated instantiation
_MODEL_NAMES_CACHE = {}

def get_model_name(model_id: str) -> str:
    """Get model name from ID with caching"""
    if model_id in _MODEL_NAMES_CACHE:
        return _MODEL_NAMES_CACHE[model_id]
        
    from app.api.routes.models import ALL_MODELS
    
    if model_id in ALL_MODELS:
        model_class = ALL_MODELS[model_id]
        # Try class attribute first fallback to instantiation
        if hasattr(model_class, 'name') and isinstance(model_class.name, str):
            name = model_class.name
        else:
            try:
                instance = model_class()
                name = instance.name
            except Exception:
                name = model_id
                
        _MODEL_NAMES_CACHE[model_id] = name
        return name
        
    return model_id


@router.get("/")
async def list_scheduled_scans(
    user_id: str = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    """List all scheduled scans for the current user"""
    query = select(DBScheduledScan).where(
        DBScheduledScan.user_id == user_id,
        DBScheduledScan.deleted_at.is_(None)
    )
    result = await db.execute(query)
    scans = result.scalars().all()
    
    # Convert to list of dicts/pydantic models
    scan_list = []
    for scan in scans:
        scan_dict = {
            "id": scan.id,
            "user_id": scan.user_id,
            "model_id": scan.model_id,
            "model_name": scan.model_name or get_model_name(scan.model_id),
            "universe": scan.universe,
            "schedule_time": scan.schedule_time,
            "days": scan.days,
            "enabled": scan.enabled,
            "parameters": scan.parameters,
            "created_at": scan.created_at.isoformat() if scan.created_at else None,
            "last_run": scan.last_run.isoformat() if scan.last_run else None,
            "deleted_at": scan.deleted_at.isoformat() if scan.deleted_at else None
        }
        scan_list.append(scan_dict)
    
    return {"scans": scan_list, "total": len(scan_list)}


@router.post("/", dependencies=[Depends(verify_api_key)])
async def create_scheduled_scan(
    scan: ScheduledScanCreate,
    user_id: str = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new scheduled scan for the current user"""
    # Validate inputs
    schedule_time = validate_schedule_time(scan.schedule_time)
    days = validate_days(scan.days)
    
    # Validate model exists
    from app.api.routes.models import ALL_MODELS
    if scan.model_id not in ALL_MODELS:
        raise HTTPException(status_code=400, detail=f"Unknown model: {scan.model_id}")
    
    new_scan = DBScheduledScan(
        # ID auto-generated
        user_id=user_id,
        model_id=scan.model_id,
        model_name=get_model_name(scan.model_id),
        universe=scan.universe,
        schedule_time=schedule_time,
        days=days,
        enabled=scan.enabled,
        parameters=scan.parameters,
        created_at=datetime.now()
    )
    
    db.add(new_scan)
    await db.commit()
    await db.refresh(new_scan)
    
    logger.info(f"User {user_id} created scheduled scan: {new_scan.id}")
    
    # Update Scheduler
    from app.scheduler import add_job_for_scan
    add_job_for_scan(new_scan)
    
    return {
        "message": "Scheduled scan created and scheduled",
        "scan": {
            "id": new_scan.id,
            "model_name": new_scan.model_name,
            "schedule_time": new_scan.schedule_time
        }
    }


@router.get("/{scan_id}")
async def get_scheduled_scan(
    scan_id: str,
    user_id: str = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific scan"""
    query = select(DBScheduledScan).where(DBScheduledScan.id == scan_id)
    result = await db.execute(query)
    scan = result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    if scan.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    if scan.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this scan")
        
    return {
        "id": scan.id,
        "user_id": scan.user_id,
        "model_id": scan.model_id,
        "model_name": scan.model_name,
        "universe": scan.universe,
        "schedule_time": scan.schedule_time,
        "days": scan.days,
        "enabled": scan.enabled,
        "parameters": scan.parameters,
        "last_run": scan.last_run
    }


@router.put("/{scan_id}/toggle", dependencies=[Depends(verify_api_key)])
async def toggle_scan(
    scan_id: str,
    update: ScheduledScanUpdate,
    user_id: str = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Enable or disable a scheduled scan"""
    query = select(DBScheduledScan).where(DBScheduledScan.id == scan_id)
    result = await db.execute(query)
    scan = result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    if scan.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    if scan.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this scan")
    
    scan.enabled = update.enabled
    await db.commit()
    await db.refresh(scan)
    
    # Update Scheduler
    from app.scheduler import add_job_for_scan, remove_job
    if scan.enabled:
        add_job_for_scan(scan)
    else:
        remove_job(scan.id)
    
    status_str = "enabled" if scan.enabled else "disabled"
    return {"message": f"Scan {status_str}", "enabled": scan.enabled}


@router.delete("/{scan_id}", dependencies=[Depends(verify_api_key)])
async def delete_scan(
    scan_id: str,
    user_id: str = Depends(require_user_id),
    confirm: bool = Query(False, description="Set to true to confirm deletion"),
    db: AsyncSession = Depends(get_db)
):
    """Delete a scheduled scan"""
    if not confirm:
        raise HTTPException(
            status_code=400, 
            detail="Deletion requires confirmation. Add ?confirm=true to the request."
        )
        
    query = select(DBScheduledScan).where(DBScheduledScan.id == scan_id)
    result = await db.execute(query)
    scan = result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    if scan.user_id != user_id:
         raise HTTPException(status_code=403, detail="Not authorized to delete this scan")
         
    # Soft delete
    scan.deleted_at = datetime.now()
    await db.commit()
    
    # Remove from Scheduler
    from app.scheduler import remove_job
    remove_job(scan.id)
    
    # Audit Log
    from app.services.audit import get_audit_service
    audit_service = get_audit_service()
    await audit_service.log(
        db=db,
        user_id=user_id,
        action="DELETE_SCHEDULED_SCAN",
        resource_type="scheduled_scan",
        resource_id=scan_id,
        details={"soft_delete": True}
    )
    # Commit audit log
    await db.commit()
    
    return {"message": "Scheduled scan deleted and unscheduled"}
