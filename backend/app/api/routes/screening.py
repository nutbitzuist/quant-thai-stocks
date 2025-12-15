"""
Screening API Routes
Sector screening and financial statements for Thai stocks using SETSMART
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import logging
import os

from app.data.universe import get_universe, SET100_STOCKS, SET_STOCKS, Sector

logger = logging.getLogger(__name__)

router = APIRouter()


def get_setsmart_provider():
    """Get SETSMART provider if available"""
    try:
        from app.data.setsmart_provider import SetsmartProvider
        api_key = os.getenv("SETSMART_API_KEY")
        if api_key:
            return SetsmartProvider(api_key=api_key)
    except ImportError:
        pass
    return None


# Official SET sectors mapping
SET_SECTORS = {
    "Resources": ["ENERGY", "MINING"],
    "Technology": ["TECH", "ETRON", "ICT"],
    "Industrials": ["AUTO", "IMM", "PAPER", "PETRO", "PKG", "STEEL"],
    "Property & Construction": ["CONMAT", "CONS", "PROP"],
    "Financials": ["BANK", "FIN", "INSUR"],
    "Services": ["COMM", "HELTH", "MEDIA", "PROF", "TOURISM", "TRANS"],
    "Consumer Products": ["FASHION", "HOME", "PERSON"],
    "Agro & Food Industry": ["AGRI", "FOOD"],
}


@router.get("/sectors")
async def list_sectors():
    """Get list of all SET sectors with stock counts"""
    provider = get_setsmart_provider()
    
    # Try SETSMART first
    if provider:
        sectors = provider.get_all_sectors()
        if sectors:
            return {"sectors": sectors, "source": "setsmart"}
    
    # Fallback: Calculate from local universe data
    sector_counts = {}
    all_stocks = SET100_STOCKS + SET_STOCKS
    seen = set()
    
    for stock in all_stocks:
        if stock.ticker in seen:
            continue
        seen.add(stock.ticker)
        sector = stock.sector.value
        if sector not in sector_counts:
            sector_counts[sector] = {"sector": sector, "count": 0, "stocks": []}
        sector_counts[sector]["count"] += 1
        sector_counts[sector]["stocks"].append(stock.ticker)
    
    sectors = [
        {
            "sector": v["sector"],
            "count": v["count"],
            "market_cap": None,
            "pe_avg": None,
        }
        for v in sorted(sector_counts.values(), key=lambda x: -x["count"])
    ]
    
    return {"sectors": sectors, "source": "local"}


@router.get("/by-sector/{sector}")
async def get_stocks_by_sector(
    sector: str,
    limit: int = Query(50, ge=1, le=200),
    include_fundamentals: bool = Query(False)
):
    """Get all Thai stocks in a specific sector"""
    provider = get_setsmart_provider()
    
    # Find matching stocks from local universe
    all_stocks = SET100_STOCKS + SET_STOCKS
    seen = set()
    matches = []
    
    for stock in all_stocks:
        if stock.ticker in seen:
            continue
        seen.add(stock.ticker)
        
        # Match by sector name (case-insensitive partial match)
        if sector.lower() in stock.sector.value.lower() or stock.sector.value.lower() in sector.lower():
            stock_info = {
                "ticker": stock.ticker,
                "name": stock.name,
                "sector": stock.sector.value,
                "is_major": stock.is_major,
            }
            
            # Optionally include fundamentals from SETSMART
            if include_fundamentals and provider:
                fundamentals = provider.get_fundamental_data(stock.ticker)
                if fundamentals:
                    stock_info["fundamentals"] = {
                        "price": fundamentals.get("price"),
                        "pe_ratio": fundamentals.get("pe_ratio"),
                        "pb_ratio": fundamentals.get("pb_ratio"),
                        "roe": fundamentals.get("roe"),
                        "dividend_yield": fundamentals.get("dividend_yield"),
                        "market_cap": fundamentals.get("market_cap"),
                    }
            
            matches.append(stock_info)
    
    # Sort by is_major first, then by name
    matches.sort(key=lambda x: (not x["is_major"], x["name"]))
    
    return {
        "sector": sector,
        "count": len(matches),
        "stocks": matches[:limit],
    }


@router.get("/financials/{ticker}")
async def get_financial_statements(
    ticker: str,
    years: int = Query(3, ge=1, le=6)
):
    """Get quarterly financial statements for a Thai stock"""
    provider = get_setsmart_provider()
    
    if not provider:
        raise HTTPException(
            status_code=503,
            detail="SETSMART API not configured. Please set SETSMART_API_KEY environment variable."
        )
    
    # Normalize ticker
    ticker_upper = ticker.upper()
    if not ticker_upper.endswith('.BK'):
        ticker_upper = f"{ticker_upper}.BK"
    
    financials = provider.get_financial_statements(ticker_upper, years=years)
    
    if not financials:
        # Return empty structure with message
        return {
            "ticker": ticker_upper,
            "message": "Financial data not available from SETSMART. This may be due to API limitations or the stock not being covered.",
            "income_statement": [],
            "balance_sheet": [],
            "cash_flow": [],
            "ratios": {},
        }
    
    return financials


@router.get("/sector-info/{ticker}")
async def get_sector_info(ticker: str):
    """Get sector/industry classification for a Thai stock"""
    provider = get_setsmart_provider()
    
    # Normalize ticker
    ticker_upper = ticker.upper()
    if not ticker_upper.endswith('.BK'):
        ticker_upper = f"{ticker_upper}.BK"
    
    # Try SETSMART first
    if provider:
        info = provider.get_sector_info(ticker_upper)
        if info:
            return {**info, "source": "setsmart"}
    
    # Fallback to local data
    all_stocks = SET100_STOCKS + SET_STOCKS
    for stock in all_stocks:
        if stock.ticker == ticker_upper:
            return {
                "ticker": ticker_upper,
                "symbol": ticker_upper.replace(".BK", ""),
                "name": stock.name,
                "sector": stock.sector.value,
                "industry": None,
                "sub_industry": None,
                "market": "SET",
                "source": "local"
            }
    
    raise HTTPException(status_code=404, detail=f"Stock not found: {ticker}")


@router.post("/filter")
async def filter_stocks(
    sectors: List[str] = Query(None, description="Filter by sectors"),
    min_pe: float = Query(None, description="Minimum P/E ratio"),
    max_pe: float = Query(None, description="Maximum P/E ratio"),
    min_roe: float = Query(None, description="Minimum ROE (%)"),
    min_dividend: float = Query(None, description="Minimum dividend yield (%)"),
    min_market_cap: float = Query(None, description="Minimum market cap (millions)"),
    universe: str = Query("set100", description="Universe to screen"),
    limit: int = Query(50, ge=1, le=200)
):
    """
    Advanced multi-criteria stock screening
    """
    provider = get_setsmart_provider()
    
    # Get stocks from universe
    if universe.lower() == "set100":
        stocks = SET100_STOCKS
    elif universe.lower() == "set":
        stocks = SET_STOCKS
    else:
        stocks = get_universe(universe)
    
    results = []
    seen = set()
    
    for stock in stocks:
        if stock.ticker in seen:
            continue
        seen.add(stock.ticker)
        
        # Filter by sector
        if sectors and stock.sector.value not in sectors:
            match = False
            for s in sectors:
                if s.lower() in stock.sector.value.lower():
                    match = True
                    break
            if not match:
                continue
        
        stock_data = {
            "ticker": stock.ticker,
            "name": stock.name,
            "sector": stock.sector.value,
            "is_major": stock.is_major,
        }
        
        # Get fundamentals for filtering
        if provider and (min_pe or max_pe or min_roe or min_dividend or min_market_cap):
            fundamentals = provider.get_fundamental_data(stock.ticker)
            if fundamentals:
                pe = fundamentals.get("pe_ratio")
                roe = fundamentals.get("roe")
                div_yield = fundamentals.get("dividend_yield")
                mcap = fundamentals.get("market_cap")
                
                # Apply filters
                if min_pe and (pe is None or pe < min_pe):
                    continue
                if max_pe and (pe is None or pe > max_pe):
                    continue
                if min_roe and (roe is None or roe * 100 < min_roe):
                    continue
                if min_dividend and (div_yield is None or div_yield * 100 < min_dividend):
                    continue
                if min_market_cap and (mcap is None or mcap / 1e6 < min_market_cap):
                    continue
                
                stock_data["fundamentals"] = {
                    "price": fundamentals.get("price"),
                    "pe_ratio": pe,
                    "pb_ratio": fundamentals.get("pb_ratio"),
                    "roe": roe,
                    "dividend_yield": div_yield,
                    "market_cap": mcap,
                }
        
        results.append(stock_data)
        
        if len(results) >= limit:
            break
    
    return {
        "universe": universe,
        "filters_applied": {
            "sectors": sectors,
            "min_pe": min_pe,
            "max_pe": max_pe,
            "min_roe": min_roe,
            "min_dividend": min_dividend,
            "min_market_cap": min_market_cap,
        },
        "count": len(results),
        "stocks": results,
    }
