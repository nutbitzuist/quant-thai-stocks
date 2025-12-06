"""
Scheduled Scans API Routes
Manage scheduled daily model scans
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
import json
import os

router = APIRouter(prefix="/api/scheduled-scans", tags=["scheduled-scans"])

# Simple file-based storage for scheduled scans
SCANS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "scheduled_scans.json")


class ScheduledScanCreate(BaseModel):
    model_id: str
    universe: str
    schedule_time: str  # HH:MM format
    days: List[str]  # ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    enabled: bool = True
    parameters: Optional[dict] = None


class ScheduledScanUpdate(BaseModel):
    enabled: bool


class ScheduledScan(BaseModel):
    id: str
    model_id: str
    model_name: Optional[str] = None
    universe: str
    schedule_time: str
    days: List[str]
    enabled: bool
    parameters: Optional[dict] = None
    created_at: str
    last_run: Optional[str] = None


def load_scans() -> List[dict]:
    """Load scheduled scans from file"""
    try:
        os.makedirs(os.path.dirname(SCANS_FILE), exist_ok=True)
        if os.path.exists(SCANS_FILE):
            with open(SCANS_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return []


def save_scans(scans: List[dict]):
    """Save scheduled scans to file"""
    try:
        os.makedirs(os.path.dirname(SCANS_FILE), exist_ok=True)
        with open(SCANS_FILE, 'w') as f:
            json.dump(scans, f, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save scans: {e}")


def get_model_name(model_id: str) -> str:
    """Get model name from ID"""
    from app.api.routes.models import ALL_MODELS
    if model_id in ALL_MODELS:
        model_class = ALL_MODELS[model_id]
        try:
            instance = model_class()
            return instance.name
        except:
            pass
    return model_id


@router.get("/")
async def list_scheduled_scans():
    """List all scheduled scans"""
    scans = load_scans()
    # Enrich with model names
    for scan in scans:
        if not scan.get('model_name'):
            scan['model_name'] = get_model_name(scan['model_id'])
    return {"scans": scans, "total": len(scans)}


@router.post("/")
async def create_scheduled_scan(scan: ScheduledScanCreate):
    """Create a new scheduled scan"""
    scans = load_scans()
    
    new_scan = {
        "id": str(uuid.uuid4())[:8],
        "model_id": scan.model_id,
        "model_name": get_model_name(scan.model_id),
        "universe": scan.universe,
        "schedule_time": scan.schedule_time,
        "days": scan.days,
        "enabled": scan.enabled,
        "parameters": scan.parameters,
        "created_at": datetime.now().isoformat(),
        "last_run": None
    }
    
    scans.append(new_scan)
    save_scans(scans)
    
    return {"message": "Scheduled scan created", "scan": new_scan}


@router.get("/{scan_id}")
async def get_scheduled_scan(scan_id: str):
    """Get a specific scheduled scan"""
    scans = load_scans()
    for scan in scans:
        if scan['id'] == scan_id:
            scan['model_name'] = get_model_name(scan['model_id'])
            return scan
    raise HTTPException(status_code=404, detail="Scan not found")


@router.put("/{scan_id}/toggle")
async def toggle_scheduled_scan(scan_id: str, update: ScheduledScanUpdate):
    """Enable/disable a scheduled scan"""
    scans = load_scans()
    for scan in scans:
        if scan['id'] == scan_id:
            scan['enabled'] = update.enabled
            save_scans(scans)
            return {"message": f"Scan {'enabled' if update.enabled else 'disabled'}", "scan": scan}
    raise HTTPException(status_code=404, detail="Scan not found")


@router.delete("/{scan_id}")
async def delete_scheduled_scan(scan_id: str):
    """Delete a scheduled scan"""
    scans = load_scans()
    original_length = len(scans)
    scans = [s for s in scans if s['id'] != scan_id]
    
    if len(scans) == original_length:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    save_scans(scans)
    return {"message": "Scan deleted"}


@router.post("/{scan_id}/run")
async def run_scheduled_scan_now(scan_id: str):
    """Manually run a scheduled scan"""
    from app.api.routes.models import ALL_MODELS, run_model_internal
    
    scans = load_scans()
    scan = None
    for s in scans:
        if s['id'] == scan_id:
            scan = s
            break
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Run the model
    try:
        result = await run_model_internal(
            model_id=scan['model_id'],
            universe=scan['universe'],
            top_n=20,
            parameters=scan.get('parameters')
        )
        
        # Update last run time
        scan['last_run'] = datetime.now().isoformat()
        save_scans(scans)
        
        return {
            "message": "Scan executed successfully",
            "scan_id": scan_id,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run scan: {e}")


@router.get("/due")
async def get_due_scans():
    """Get scans that are due to run (for scheduler)"""
    from datetime import datetime
    
    scans = load_scans()
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_day = now.strftime("%a")
    
    due_scans = []
    for scan in scans:
        if not scan.get('enabled', False):
            continue
        if current_day not in scan.get('days', []):
            continue
        if scan.get('schedule_time') == current_time:
            due_scans.append(scan)
    
    return {"due_scans": due_scans, "current_time": current_time, "current_day": current_day}
