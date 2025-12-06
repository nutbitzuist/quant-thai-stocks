"""
Status API Routes
System status, health checks, and debugging
"""

from fastapi import APIRouter
from datetime import datetime
import platform
import sys

from app.data.fetcher import get_fetcher
from app.data.universe import get_available_universes
from app.data.providers import get_available_providers

router = APIRouter()


@router.get("/")
async def get_status():
    """Get comprehensive system status"""
    fetcher = get_fetcher()
    
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "system": {
            "python_version": sys.version,
            "platform": platform.platform()
        },
        "data": {
            "cache_entries": len(fetcher._price_cache) + len(fetcher._fundamental_cache),
            "price_cache": len(fetcher._price_cache),
            "fundamental_cache": len(fetcher._fundamental_cache),
            "recent_errors": len(fetcher.get_errors()),
            "active_providers": fetcher.get_providers(),
            "fallback_enabled": fetcher.fallback_enabled
        },
        "universes": get_available_universes()
    }


@router.get("/logs")
async def get_logs():
    """Get recent activity logs"""
    fetcher = get_fetcher()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "fetch_errors": fetcher.get_errors(),
        "cache_status": {
            "price_tickers": list(fetcher._price_cache.keys())[:20],
            "fundamental_tickers": list(fetcher._fundamental_cache.keys())[:20]
        }
    }


@router.get("/test-connection")
async def test_connection():
    """Simple endpoint to test if backend is reachable"""
    return {
        "connected": True,
        "backend": "Quant Stock Analysis API v2.0",
        "timestamp": datetime.now().isoformat(),
        "message": "If you see this, the backend is working correctly!"
    }


@router.get("/test-data")
async def test_data_fetch():
    """Test data fetching with a reliable ticker"""
    fetcher = get_fetcher()
    
    # Test with Apple (most reliable data)
    test_ticker = "AAPL"
    
    price_result = {"status": "not_tested"}
    fundamental_result = {"status": "not_tested"}
    
    try:
        price_data = fetcher.get_price_data(test_ticker, period="5d")
        if price_data is not None and not price_data.empty:
            price_result = {
                "status": "success",
                "ticker": test_ticker,
                "rows": len(price_data),
                "latest_close": round(price_data['close'].iloc[-1], 2),
                "latest_date": str(price_data['date'].iloc[-1])
            }
        else:
            price_result = {"status": "no_data"}
    except Exception as e:
        price_result = {"status": "error", "message": str(e)}
    
    try:
        fund_data = fetcher.get_fundamental_data(test_ticker)
        if fund_data:
            fundamental_result = {
                "status": "success",
                "ticker": test_ticker,
                "name": fund_data.get('name'),
                "price": fund_data.get('price'),
                "pe_ratio": fund_data.get('pe_ratio'),
                "market_cap": fund_data.get('market_cap')
            }
        else:
            fundamental_result = {"status": "no_data"}
    except Exception as e:
        fundamental_result = {"status": "error", "message": str(e)}
    
    return {
        "timestamp": datetime.now().isoformat(),
        "test_ticker": test_ticker,
        "price_data": price_result,
        "fundamental_data": fundamental_result,
        "conclusion": "Data fetching works!" if price_result["status"] == "success" else "Data fetching may have issues"
    }


@router.post("/clear-cache")
async def clear_all_cache():
    """Clear all cached data"""
    fetcher = get_fetcher()
    
    price_count = len(fetcher._price_cache)
    fund_count = len(fetcher._fundamental_cache)
    error_count = len(fetcher._errors)
    
    fetcher._price_cache.clear()
    fetcher._fundamental_cache.clear()
    fetcher._errors.clear()
    
    return {
        "cleared": {
            "price_cache": price_count,
            "fundamental_cache": fund_count,
            "errors": error_count
        },
        "timestamp": datetime.now().isoformat()
    }


@router.get("/data-providers")
async def get_data_providers():
    """Get information about available and active data providers"""
    fetcher = get_fetcher()
    all_providers = get_available_providers()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "active_providers": fetcher.get_providers(),
        "fallback_enabled": fetcher.fallback_enabled,
        "all_available_providers": [
            {
                "name": p.get_name(),
                "available": p.is_available()
            }
            for p in all_providers
        ],
        "note": "Active providers are used in order. If fallback is enabled, the system will try the next provider if one fails."
    }
