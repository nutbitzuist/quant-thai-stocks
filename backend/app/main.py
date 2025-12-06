"""
Quant Stock Analysis API
Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("=" * 50)
    logger.info("🚀 Starting Quant Stock Analysis API")
    logger.info(f"   Debug mode: {settings.debug}")
    logger.info(f"   Default universe: {settings.default_universe}")
    logger.info("=" * 50)
    yield
    logger.info("Shutting down API")


# Create FastAPI app
app = FastAPI(
    title="Quant Stock Analysis API",
    description="Quantitative analysis platform for US and Thai stocks",
    version="2.0.2",
    lifespan=lifespan
)

# CORS middleware - Allow frontend connections
# In production, only allow specific origins. In debug mode, allow all for development.
cors_origins = settings.cors_origins if not settings.debug else settings.cors_origins + ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "Content-Type"],  # Expose headers for filename extraction
)


# Health check endpoints
@app.get("/")
async def root():
    """Root endpoint - basic health check"""
    return {
        "status": "ok",
        "message": "Quant Stock Analysis API is running",
        "version": "2.0.2",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    from app.data.fetcher import get_fetcher
    from app.data.universe import get_available_universes
    
    fetcher = get_fetcher()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "ok",
            "data_fetcher": "ok",
            "cache_size": len(fetcher._price_cache),
            "recent_errors": len(fetcher.get_errors())
        },
        "universes": get_available_universes(),
        "cors_origins": settings.cors_origins
    }


@app.get("/debug/errors")
async def get_debug_errors():
    """Get recent data fetching errors for debugging"""
    from app.data.fetcher import get_fetcher
    fetcher = get_fetcher()
    return {
        "errors": fetcher.get_errors(),
        "count": len(fetcher.get_errors())
    }


@app.post("/debug/clear-cache")
async def clear_cache():
    """Clear data cache"""
    from app.data.fetcher import get_fetcher
    fetcher = get_fetcher()
    fetcher._price_cache.clear()
    fetcher._fundamental_cache.clear()
    fetcher.clear_errors()
    return {"status": "cache cleared"}


@app.get("/debug/test-fetch/{ticker}")
async def test_fetch(ticker: str):
    """Test fetching data for a single ticker"""
    from app.data.fetcher import get_fetcher
    
    fetcher = get_fetcher()
    
    # Test price data
    price_result = None
    price_error = None
    try:
        price_data = fetcher.get_price_data(ticker, period="1mo")
        if price_data is not None:
            price_result = {
                "rows": len(price_data),
                "columns": list(price_data.columns),
                "latest_close": float(price_data['close'].iloc[-1]),
                "date_range": f"{price_data['date'].iloc[0]} to {price_data['date'].iloc[-1]}"
            }
    except Exception as e:
        price_error = str(e)
    
    # Test fundamental data
    fund_result = None
    fund_error = None
    try:
        fund_data = fetcher.get_fundamental_data(ticker)
        if fund_data:
            fund_result = {
                "name": fund_data.get('name'),
                "price": fund_data.get('price'),
                "pe_ratio": fund_data.get('pe_ratio'),
                "market_cap": fund_data.get('market_cap')
            }
    except Exception as e:
        fund_error = str(e)
    
    return {
        "ticker": ticker,
        "price_data": price_result,
        "price_error": price_error,
        "fundamental_data": fund_result,
        "fundamental_error": fund_error,
        "recent_errors": fetcher.get_errors()[-5:]
    }


# Import and register routers
from app.api.routes import models, universe, status, custom_universe, advanced, scheduled_scans, backtest, enhanced

app.include_router(models.router, prefix="/api/models", tags=["Models"])
app.include_router(universe.router, prefix="/api/universe", tags=["Universe"])
app.include_router(status.router, prefix="/api/status", tags=["Status"])
app.include_router(custom_universe.router, prefix="/api/custom-universe", tags=["Custom Universe"])
app.include_router(advanced.router, prefix="/api/advanced", tags=["Advanced Features"])
app.include_router(scheduled_scans.router, tags=["Scheduled Scans"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["Backtesting"])
app.include_router(enhanced.router, prefix="/api", tags=["Enhanced Features"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
