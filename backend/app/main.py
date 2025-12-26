"""
Quant Stock Analysis API
Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import settings
from app.middleware.auth import verify_api_key
from app.limiter import limiter
from app.error_handlers import rate_limit_handler, global_exception_handler, validation_exception_handler

from app.middleware.request_id import RequestIdMiddleware
from app.utils.logger import setup_logger

import sentry_sdk

# Configure logging
logger = setup_logger()

# Initialize Sentry if DSN is set
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )
    logger.info("✅ Sentry: Initialized")
else:
    logger.info("⚠️ Sentry: DSN not set (skipping)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("=" * 50)
    logger.info("🚀 Starting Quant Stock Analysis API")
    logger.info(f"   Debug mode: {settings.debug}")
    logger.info(f"   Default universe: {settings.default_universe}")
    logger.info(f"   API Key configured: {'Yes' if settings.api_secret_key else 'No (auth disabled)'}")
    logger.info(f"   Rate limiting: {'Enabled' if settings.rate_limit_enabled else 'Disabled'}")
    
    # Initialize database
    try:
        from app.database import init_db, check_db_connection
        await init_db()
        db_connected = await check_db_connection()
        if db_connected:
            logger.info("   ✅ Database: Connected to PostgreSQL")
        else:
            logger.warning("   ⚠️ Database: Not configured (using in-memory)")
    except Exception as e:
        logger.warning(f"   ⚠️ Database: Failed to initialize - {e}")
        
    # Initialize Scheduler
    try:
        from app.scheduler import start_scheduler, stop_scheduler
        await start_scheduler()
    except Exception as e:
        logger.error(f"   ❌ Scheduler: Failed to start - {e}")
    
    logger.info("=" * 50)
    yield
    # Shutdown
    try:
        await stop_scheduler()
    except:
        pass
    logger.info("Shutting down API")


# Create FastAPI app
app = FastAPI(
    title="Quant Stock Analysis API",
    description="Quantitative analysis platform for US and Thai stocks",
    version="2.0.3",
    lifespan=lifespan
)

# Set up limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(ValueError, validation_exception_handler)

# CORS middleware - Allow frontend connections
# SECURITY: Never allow wildcard in production
cors_origins = settings.cors_origins

app.add_middleware(
    RequestIdMiddleware
)
app.add_middleware(
    SlowAPIMiddleware
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "Content-Type"],
)


# Health check endpoints (always public)
@app.get("/")
async def root():
    """Root endpoint - basic health check"""
    return {
        "status": "ok",
        "message": "Quant Stock Analysis API is running",
        "version": "2.0.3",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    from app.data.fetcher import get_fetcher
    from app.data.universe import get_available_universes
    from app.database import check_db_connection
    from fastapi import Response, status

    db_ok = await check_db_connection()
    fetcher = get_fetcher()
    
    if not db_ok:
        return Response(
            content='{"status": "unhealthy", "reason": "database_connection_failed"}', 
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            media_type="application/json"
        )
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "debug_mode": settings.debug,
        "components": {
            "api": "ok",
            "database": "connected" if db_ok else "disconnected",
            "data_fetcher": "ok",
            "data_fetcher": "ok",
            "cache_size": len(fetcher._price_cache),
            "recent_errors": len(fetcher.get_errors())
        },
        "universes": get_available_universes(),
    }


# Debug endpoints - ONLY available in debug mode
if settings.debug:
    logger.warning("⚠️ Debug mode enabled - debug endpoints are accessible")
    
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
        from app.validation import validate_ticker
        
        # Validate ticker even in debug mode
        ticker = validate_ticker(ticker)
        
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
from app.api.routes import models, universe, status, custom_universe, advanced, scheduled_scans, backtest, enhanced, analysis, screening, billing

# Public read-only routes (no auth required for GET)
app.include_router(models.router, prefix="/api/models", tags=["Models"])
app.include_router(universe.router, prefix="/api/universe", tags=["Universe"])
app.include_router(status.router, prefix="/api/status", tags=["Status"])

# Analysis routes (public read)
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(billing.router, prefix="/api/billing", tags=["Billing"])
app.include_router(screening.router, prefix="/api/screening", tags=["Screening"])

# Protected routes (require auth for mutations)
app.include_router(custom_universe.router, prefix="/api/custom-universe", tags=["Custom Universe"])
app.include_router(advanced.router, prefix="/api/advanced", tags=["Advanced Features"])
app.include_router(scheduled_scans.router, tags=["Scheduled Scans"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["Backtesting"])
app.include_router(enhanced.router, prefix="/api", tags=["Enhanced Features"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
