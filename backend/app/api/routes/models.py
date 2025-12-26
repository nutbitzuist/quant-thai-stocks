"""
Models API Routes
Run quantitative models and get signals
Backed by PostgreSQL
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.concurrency import run_in_threadpool

from app.middleware.auth import get_current_user_id, require_user_id, verify_api_key
from app.data.fetcher import get_fetcher
from app.data.universe import get_tickers, get_available_universes
from app.database import get_db

# Import services
from app.services.history import get_history_service
from app.services.pdf_generator import get_pdf_generator
from app.services.model_docs import get_model_documentation, get_all_model_docs, get_model_list_with_summaries
from app.services.custom_universe import get_custom_universe_manager

# Import all models - TECHNICAL (10)
from app.models.technical.rsi_reversal import RSIReversalModel
from app.models.technical.macd_crossover import MACDCrossoverModel
from app.models.technical.minervini_trend import MinerviniTrendModel
from app.models.technical.darvas_box import DarvasBoxModel
from app.models.technical.turtle_trading import TurtleTradingModel
from app.models.technical.elder_triple_screen import ElderTripleScreenModel
from app.models.technical.bollinger_squeeze import BollingerSqueezeModel
from app.models.technical.adx_trend import ADXTrendModel
from app.models.technical.keltner_channel import KeltnerChannelModel
from app.models.technical.volume_profile import VolumeProfileModel
from app.models.technical.dual_ema import DualEMAModel

# Import all models - FUNDAMENTAL (12)
from app.models.fundamental.canslim import CANSLIMModel
from app.models.fundamental.value_composite import ValueCompositeModel
from app.models.fundamental.quality_score import QualityScoreModel
from app.models.fundamental.piotroski_f import PiotroskiFScoreModel
from app.models.fundamental.magic_formula import MagicFormulaModel
from app.models.fundamental.dividend_aristocrats import DividendAristocratsModel
from app.models.fundamental.earnings_momentum import EarningsMomentumModel
from app.models.fundamental.garp import GARPModel
from app.models.fundamental.altman_z import AltmanZScoreModel
from app.models.fundamental.ev_ebitda import EVEBITDAModel
from app.models.fundamental.fcf_yield import FCFYieldModel
from app.models.fundamental.momentum_value import MomentumValueModel

# Import all models - QUANTITATIVE (4)
from app.models.quantitative.mean_reversion import MeanReversionModel
from app.models.quantitative.pairs_trading import PairsTradingModel
from app.models.quantitative.factor_momentum import FactorMomentumModel
from app.models.quantitative.volatility_breakout import VolatilityBreakoutModel

logger = logging.getLogger(__name__)

router = APIRouter()

# Model registry - 11 Technical Models
TECHNICAL_MODELS = {
    "rsi_reversal": RSIReversalModel,
    "macd_crossover": MACDCrossoverModel,
    "minervini_trend": MinerviniTrendModel,
    "darvas_box": DarvasBoxModel,
    "turtle_trading": TurtleTradingModel,
    "elder_triple_screen": ElderTripleScreenModel,
    "bollinger_squeeze": BollingerSqueezeModel,
    "adx_trend": ADXTrendModel,
    "keltner_channel": KeltnerChannelModel,
    "volume_profile": VolumeProfileModel,
    "dual_ema": DualEMAModel,
}

# Model registry - 12 Fundamental Models
FUNDAMENTAL_MODELS = {
    "canslim": CANSLIMModel,
    "value_composite": ValueCompositeModel,
    "quality_score": QualityScoreModel,
    "piotroski_f": PiotroskiFScoreModel,
    "magic_formula": MagicFormulaModel,
    "dividend_aristocrats": DividendAristocratsModel,
    "earnings_momentum": EarningsMomentumModel,
    "garp": GARPModel,
    "altman_z": AltmanZScoreModel,
    "ev_ebitda": EVEBITDAModel,
    "fcf_yield": FCFYieldModel,
    "momentum_value": MomentumValueModel,
}

# Model registry - 4 Quantitative/Statistical Models
QUANTITATIVE_MODELS = {
    "mean_reversion": MeanReversionModel,
    "pairs_trading": PairsTradingModel,
    "factor_momentum": FactorMomentumModel,
    "volatility_breakout": VolatilityBreakoutModel,
}

ALL_MODELS = {**TECHNICAL_MODELS, **FUNDAMENTAL_MODELS, **QUANTITATIVE_MODELS}


class RunModelRequest(BaseModel):
    model_id: str
    universe: str
    parameters: Optional[Dict[str, Any]] = None
    top_n: int = 50


class RunModelResponse(BaseModel):
    run_id: str
    model_name: str
    category: str
    run_timestamp: str
    universe: str
    total_stocks_analyzed: int
    stocks_with_data: int
    data_coverage_pct: float
    buy_signals: List[Dict]
    sell_signals: List[Dict]
    full_rankings: List[Dict]
    parameters: Dict[str, Any]
    errors: List[str]
    fetch_errors: List[str]


@router.get("/")
async def list_models():
    """Get list of available models with summaries"""
    return get_model_list_with_summaries()


@router.get("/docs")
async def get_all_documentation():
    """Get detailed documentation for all models"""
    return get_all_model_docs()


@router.get("/docs/{model_id}")
async def get_model_docs(model_id: str):
    """Get detailed documentation for a specific model"""
    doc = get_model_documentation(model_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Documentation not found for: {model_id}")
    return doc


@router.post("/run", response_model=RunModelResponse)
async def run_model(
    request: RunModelRequest,
    user_id: Optional[str] = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Run a specific model and get signals"""
    
    if request.model_id not in ALL_MODELS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unknown model: {request.model_id}. Available: {list(ALL_MODELS.keys())}"
        )
    
    logger.info(f"Running model: {request.model_id} on universe: {request.universe}")
    
    # Get tickers - check custom universes first
    custom_manager = get_custom_universe_manager()
    custom_universe = await custom_manager.get_universe(db, request.universe, user_id)
    
    if custom_universe:
        tickers = custom_universe['tickers']
    else:
        tickers = get_tickers(request.universe)
    
    if not tickers:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown universe: {request.universe}"
        )
    
    logger.info(f"Fetching data for {len(tickers)} tickers...")
    
    # Fetch data
    fetcher = get_fetcher()
    fetcher.clear_errors()
    
    price_data = fetcher.get_bulk_price_data(tickers, period="1y")
    
    logger.info(f"Got price data for {len(price_data)} tickers")
    
    # Get fundamental data if needed
    fundamental_data = None
    if request.model_id in FUNDAMENTAL_MODELS:
        logger.info("Fetching fundamental data...")
        fundamental_data = fetcher.get_bulk_fundamental_data(tickers)
        logger.info(f"Got fundamental data for {len(fundamental_data)} tickers")
    
    # Create and run model
    model_class = ALL_MODELS[request.model_id]
    params = request.parameters or {}
    model = model_class(**params)
    
    logger.info(f"Running {model.name}...")
    result = await run_in_threadpool(model.run, price_data, fundamental_data)
    
    # Get fetch errors for debugging
    fetch_errors = fetcher.get_errors()
    
    # Save to history
    record_id = f"run_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    try:
        if user_id:
            history_service = get_history_service()
            record = await history_service.add_run(
                db=db,
                model_id=request.model_id,
                model_name=result.model_name,
                category=result.category,
                universe=request.universe,
                total_analyzed=len(tickers),
                stocks_with_data=len(price_data),
                buy_signals=[s.to_dict() for s in result.get_buy_signals(request.top_n)],
                sell_signals=[s.to_dict() for s in result.get_sell_signals(request.top_n)],
                parameters=result.parameters,
                errors=result.errors,
                user_id=user_id
            )
            await db.commit()
            record_id = record['id']
            logger.info(f"Saved run to history: {record_id}")
    except Exception as e:
        logger.error(f"Failed to save run to history: {str(e)}", exc_info=True)
    
    # Calculate coverage
    coverage_pct = (len(price_data) / len(tickers) * 100) if tickers else 0.0
    
    return RunModelResponse(
        run_id=record_id,
        model_name=result.model_name,
        category=result.category,
        run_timestamp=result.run_timestamp.isoformat(),
        universe=request.universe,
        total_stocks_analyzed=len(tickers),
        stocks_with_data=len(price_data),
        data_coverage_pct=round(coverage_pct, 2),
        buy_signals=[s.to_dict() for s in result.get_buy_signals(request.top_n)],
        sell_signals=[s.to_dict() for s in result.get_sell_signals(request.top_n)],
        full_rankings=result.rankings[:50],
        parameters=result.parameters,
        errors=result.errors,
        fetch_errors=fetch_errors[:10]
    )


@router.get("/history")
async def get_run_history(
    limit: int = Query(50, description="Maximum records to return"),
    user_id: Optional[str] = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get history of model runs"""
    history_service = get_history_service()
    
    # Only return user specific history or common history if system-wide sharing enabled (not for now)
    # If no user_id, return empty or public runs? Let's assume strict ownership for now.
    
    # Note: If auth is optional, user_id might be None.
    # But this endpoint feels like it should return the user's history.
    
    return {
        "summary": await history_service.get_summary(db, user_id),
        "runs": await history_service.get_all(db, limit, user_id)
    }


@router.get("/history/{run_id}")
async def get_run_details(
    run_id: str,
    user_id: Optional[str] = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific run"""
    history_service = get_history_service()
    record = await history_service.get_by_id(db, run_id, user_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
    return record


@router.get("/history/{run_id}/pdf")
async def export_run_pdf(
    run_id: str, 
    limit: int = Query(15, description="Number of top signals to inclusion"),
    user_id: Optional[str] = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Generate PDF report for a past run"""
    history_service = get_history_service()
    record = await history_service.get_by_id(db, run_id, user_id)
    
    if not record:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
    
    # Generate PDF
    try:
        pdf_gen = get_pdf_generator()
        pdf_bytes = await run_in_threadpool(pdf_gen.create_model_run_report, record, limit=limit)
    except Exception as e:
        logger.error(f"Failed to generate PDF for run {run_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF report: {str(e)}"
        )
    
    filename = f"{record['model_id']}_{record['run_timestamp'].split('T')[0]}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.delete("/history", dependencies=[Depends(verify_api_key)])
async def clear_history(
    user_id: str = Depends(require_user_id),
    confirm: bool = Query(False, description="Set to true to confirm deletion"),
    db: AsyncSession = Depends(get_db)
):
    """
    Clear run history for the current user only.
    Requires confirm=true query parameter.
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Deletion requires confirmation. Add ?confirm=true to the request."
        )
    
    history_service = get_history_service()
    count = await history_service.clear_for_user(db, user_id)
    logger.info(f"User {user_id} cleared {count} history records")
    
    # Audit Log
    from app.services.audit import get_audit_service
    audit_service = get_audit_service()
    await audit_service.log(
        db=db,
        user_id=user_id,
        action="CLEAR_HISTORY",
        resource_type="run_history",
        details={"count": count}
    )
    # Commit audit log
    await db.commit()
    
    return {"cleared": count, "message": f"Cleared {count} history records"}
