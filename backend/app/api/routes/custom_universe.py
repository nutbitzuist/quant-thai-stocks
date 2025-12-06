"""
Custom Universe API Routes
Manage user-defined stock universes
"""

from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel
from typing import List, Optional
import logging

from app.services.custom_universe import get_custom_universe_manager

logger = logging.getLogger(__name__)

router = APIRouter()


class CreateUniverseRequest(BaseModel):
    name: str
    description: str
    tickers: List[str]
    market: str = "Mixed"


class ImportUniverseRequest(BaseModel):
    name: str
    description: str
    ticker_text: str  # Flexible format: comma, space, or newline separated
    market: str = "Mixed"


class UpdateUniverseRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tickers: Optional[List[str]] = None
    market: Optional[str] = None


@router.get("/")
async def list_custom_universes():
    """List all custom universes"""
    manager = get_custom_universe_manager()
    return {
        "universes": manager.get_all_universes()
    }


@router.post("/")
async def create_custom_universe(request: CreateUniverseRequest):
    """Create a new custom universe"""
    manager = get_custom_universe_manager()
    
    try:
        universe = manager.create_universe(
            name=request.name,
            description=request.description,
            tickers=request.tickers,
            market=request.market
        )
        return {
            "message": f"Created universe '{universe.name}' with {len(universe.tickers)} tickers",
            "universe": universe.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/import")
async def import_universe_from_text(request: ImportUniverseRequest):
    """
    Create a universe from text input (flexible format)
    Accepts comma, space, or newline separated tickers
    """
    manager = get_custom_universe_manager()
    
    try:
        universe = manager.import_from_text(
            name=request.name,
            description=request.description,
            ticker_text=request.ticker_text,
            market=request.market
        )
        return {
            "message": f"Imported universe '{universe.name}' with {len(universe.tickers)} tickers",
            "universe": universe.to_dict(),
            "parsed_tickers": universe.tickers
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{universe_id}")
async def get_custom_universe(universe_id: str):
    """Get details of a custom universe"""
    manager = get_custom_universe_manager()
    universe = manager.get_universe(universe_id)
    
    if not universe:
        raise HTTPException(status_code=404, detail=f"Universe not found: {universe_id}")
    
    return universe.to_dict()


@router.put("/{universe_id}")
async def update_custom_universe(universe_id: str, request: UpdateUniverseRequest):
    """Update a custom universe"""
    manager = get_custom_universe_manager()
    
    universe = manager.update_universe(
        universe_id=universe_id,
        name=request.name,
        description=request.description,
        tickers=request.tickers,
        market=request.market
    )
    
    if not universe:
        raise HTTPException(status_code=404, detail=f"Universe not found: {universe_id}")
    
    return {
        "message": f"Updated universe '{universe.name}'",
        "universe": universe.to_dict()
    }


@router.delete("/{universe_id}")
async def delete_custom_universe(universe_id: str):
    """Delete a custom universe"""
    manager = get_custom_universe_manager()
    
    if not manager.delete_universe(universe_id):
        raise HTTPException(status_code=404, detail=f"Universe not found: {universe_id}")
    
    return {"message": f"Deleted universe: {universe_id}"}


@router.post("/parse")
async def parse_ticker_text(ticker_text: str = Form(...)):
    """
    Parse ticker text to preview what tickers will be extracted
    Useful for testing before creating a universe
    """
    manager = get_custom_universe_manager()
    tickers = manager.parse_ticker_input(ticker_text)
    
    return {
        "original": ticker_text,
        "parsed_count": len(tickers),
        "tickers": tickers
    }
