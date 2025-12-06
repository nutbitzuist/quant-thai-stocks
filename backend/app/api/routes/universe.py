"""
Universe API Routes
Stock universe management and information
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from app.data.universe import (
    get_universe, 
    get_tickers, 
    get_stock_info,
    get_universe_summary,
    get_available_universes,
    SP500_STOCKS,
    SET100_STOCKS
)
from app.data.fetcher import get_fetcher

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def list_universes():
    """List all available stock universes"""
    return {
        "universes": get_available_universes(),
        "default": "sp50"
    }


@router.get("/{universe_id}")
async def get_universe_details(universe_id: str):
    """Get details of a specific universe"""
    summary = get_universe_summary(universe_id)
    tickers = get_tickers(universe_id)
    
    if not tickers:
        raise HTTPException(
            status_code=404,
            detail=f"Universe not found: {universe_id}"
        )
    
    return {
        **summary,
        "tickers": tickers
    }


@router.get("/{universe_id}/stocks")
async def get_universe_stocks(
    universe_id: str,
    sector: Optional[str] = Query(None, description="Filter by sector")
):
    """Get all stocks in a universe with details"""
    stocks = get_universe(universe_id)
    
    if not stocks:
        raise HTTPException(status_code=404, detail=f"Universe not found: {universe_id}")
    
    if sector:
        stocks = [s for s in stocks if s.sector.value.lower() == sector.lower()]
    
    return {
        "universe": universe_id,
        "count": len(stocks),
        "stocks": [
            {
                "ticker": s.ticker,
                "name": s.name,
                "sector": s.sector.value,
                "is_major": s.is_major
            }
            for s in stocks
        ]
    }


@router.get("/stock/{ticker}")
async def get_stock_details(ticker: str):
    """Get detailed info for a single stock"""
    
    # Normalize ticker
    ticker_upper = ticker.upper()
    if not ticker_upper.endswith('.BK') and '.' not in ticker_upper:
        # Try both US and Thai versions
        stock = get_stock_info(ticker_upper) or get_stock_info(f"{ticker_upper}.BK")
    else:
        stock = get_stock_info(ticker_upper)
    
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock not found: {ticker}")
    
    # Get real-time data
    fetcher = get_fetcher()
    price_data = fetcher.get_price_data(stock.ticker, period="3mo")
    fundamental_data = fetcher.get_fundamental_data(stock.ticker)
    
    result = {
        "ticker": stock.ticker,
        "name": stock.name,
        "sector": stock.sector.value,
        "market": stock.market.value,
        "is_major": stock.is_major
    }
    
    if price_data is not None and not price_data.empty:
        result["price"] = {
            "current": round(price_data['close'].iloc[-1], 2),
            "change_1d_pct": round(
                (price_data['close'].iloc[-1] / price_data['close'].iloc[-2] - 1) * 100, 2
            ) if len(price_data) > 1 else 0,
            "high": round(price_data['high'].max(), 2),
            "low": round(price_data['low'].min(), 2),
            "volume": int(price_data['volume'].iloc[-1])
        }
    
    if fundamental_data:
        result["fundamentals"] = {
            k: round(v, 2) if isinstance(v, float) else v
            for k, v in fundamental_data.items()
            if k not in ['ticker', 'name'] and v is not None
        }
    
    return result
