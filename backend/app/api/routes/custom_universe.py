"""
Custom Universe API Routes
With user ownership, input validation, and confirmation for destructive actions
Backed by PostgreSQL
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.custom_universe import get_custom_universe_manager
from app.middleware.auth import require_user_id, verify_api_key
from app.validation import validate_name, validate_description, validate_ticker_list
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


class CustomUniverseCreate(BaseModel):
    name: str
    description: str = ""
    tickers: List[str]
    market: str = "Mixed"


class CustomUniverseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tickers: Optional[List[str]] = None
    market: Optional[str] = None


class ImportFromTextRequest(BaseModel):
    name: str
    description: str = ""
    ticker_text: str
    market: str = "Mixed"


@router.get("/")
async def list_custom_universes(
    user_id: Optional[str] = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    List all custom universes visible to the current user.
    Returns user's universes + read-only system universes.
    """
    manager = get_custom_universe_manager()
    universes = await manager.get_all_universes(db, user_id)
    return {"universes": universes, "total": len(universes)}


@router.post("/", dependencies=[Depends(verify_api_key)])
async def create_custom_universe(
    request: CustomUniverseCreate,
    user_id: str = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new custom universe for the current user.
    """
    # Validate inputs
    name = validate_name(request.name, "Universe name")
    description = validate_description(request.description)
    tickers = validate_ticker_list(request.tickers)
    
    manager = get_custom_universe_manager()
    universe = await manager.create_universe(
        db=db,
        name=name,
        description=description or "",
        tickers=tickers,
        market=request.market,
        user_id=user_id
    )
    
    logger.info(f"User {user_id} created custom universe: {universe['id']}")
    
    return {
        "message": "Custom universe created",
        "universe": universe
    }


@router.post("/import", dependencies=[Depends(verify_api_key)])
async def import_universe_from_text(
    request: ImportFromTextRequest,
    user_id: str = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a custom universe from pasted ticker text.
    Accepts comma-separated, space-separated, or newline-separated tickers.
    """
    # Validate inputs
    name = validate_name(request.name, "Universe name")
    description = validate_description(request.description)
    
    manager = get_custom_universe_manager()
    
    # Parse and validate tickers
    parsed_tickers = manager.parse_ticker_input(request.ticker_text)
    if not parsed_tickers:
        raise HTTPException(status_code=400, detail="No valid tickers found in input")
    
    validated_tickers = validate_ticker_list(parsed_tickers)
    
    universe = await manager.create_universe(
        db=db,
        name=name,
        description=description or "",
        tickers=validated_tickers,
        market=request.market,
        user_id=user_id
    )
    
    logger.info(f"User {user_id} imported custom universe: {universe['id']} with {len(validated_tickers)} tickers")
    
    return {
        "message": f"Custom universe created with {len(validated_tickers)} tickers",
        "universe": universe,
        "parsed_count": len(validated_tickers)
    }


@router.get("/{universe_id}")
async def get_custom_universe(
    universe_id: str,
    user_id: Optional[str] = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get details of a specific custom universe.
    Only returns user's own universes or system universes.
    """
    manager = get_custom_universe_manager()
    universe = await manager.get_universe(db, universe_id, user_id)
    
    if not universe:
        raise HTTPException(status_code=404, detail="Custom universe not found")
    
    return universe


@router.put("/{universe_id}", dependencies=[Depends(verify_api_key)])
async def update_custom_universe(
    universe_id: str,
    request: CustomUniverseUpdate,
    user_id: str = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing custom universe.
    Only the owner can update their universes.
    System universes cannot be modified.
    """
    # Validation happens inside manager for specific fields
    
    manager = get_custom_universe_manager()
    updated = await manager.update_universe(
        db=db,
        universe_id=universe_id,
        user_id=user_id,
        name=request.name,
        description=request.description,
        tickers=request.tickers,
        market=request.market
    )
    
    if not updated:
        # Determine if it was 404 or 403 (could be improved in manager return type)
        existing = await manager.get_universe(db, universe_id) # Check existence without ownership first? No, security risk.
        if existing and existing.get('user_id') != user_id and existing.get('is_system'):
             raise HTTPException(status_code=403, detail="Cannot modify system universe")
        raise HTTPException(status_code=404, detail="Universe not found or not authorized")
    
    return {
        "message": "Custom universe updated",
        "universe": updated
    }


@router.delete("/{universe_id}", dependencies=[Depends(verify_api_key)])
async def delete_custom_universe(
    universe_id: str,
    user_id: str = Depends(require_user_id),
    confirm: bool = Query(False, description="Set to true to confirm deletion"),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a custom universe.
    Only the owner can delete their universes.
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Deletion requires confirmation. Add ?confirm=true to the request."
        )
    
    manager = get_custom_universe_manager()
    deleted = await manager.delete_universe(db, universe_id, user_id, soft=True)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Universe not found or not authorized")
    
    logger.info(f"User {user_id} deleted universe: {universe_id}")
    
    # Audit Log
    from app.services.audit import get_audit_service
    audit_service = get_audit_service()
    await audit_service.log(
        db=db,
        user_id=user_id,
        action="DELETE_UNIVERSE",
        resource_type="custom_universe",
        resource_id=universe_id,
        details={"soft_delete": True}
    )
    # Commit audit log
    await db.commit()
    
    return {"message": "Custom universe deleted"}


@router.post("/parse-tickers")
async def parse_tickers_endpoint(
    request: ImportFromTextRequest
):
    """Helper endpoint to parse tickers without creating a universe"""
    manager = get_custom_universe_manager()
    parsed = manager.parse_ticker_input(request.ticker_text)
    return {"tickers": parsed, "count": len(parsed)}
