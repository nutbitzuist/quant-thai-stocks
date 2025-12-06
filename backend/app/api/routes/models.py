"""
Models API Routes
Run quantitative models and get signals
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from app.data.fetcher import get_fetcher
from app.data.universe import get_tickers, get_available_universes

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

# Import all models - FUNDAMENTAL (9)
from app.models.fundamental.canslim import CANSLIMModel
from app.models.fundamental.value_composite import ValueCompositeModel
from app.models.fundamental.quality_score import QualityScoreModel
from app.models.fundamental.piotroski_f import PiotroskiFScoreModel
from app.models.fundamental.magic_formula import MagicFormulaModel
from app.models.fundamental.dividend_aristocrats import DividendAristocratsModel
from app.models.fundamental.earnings_momentum import EarningsMomentumModel
from app.models.fundamental.garp import GARPModel
from app.models.fundamental.altman_z import AltmanZScoreModel

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

# Model registry - 9 Fundamental Models
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
}

ALL_MODELS = {**TECHNICAL_MODELS, **FUNDAMENTAL_MODELS}


class RunModelRequest(BaseModel):
    model_id: str
    universe: str = "sp50"
    parameters: Optional[Dict[str, Any]] = None
    top_n: int = 10


class RunModelResponse(BaseModel):
    run_id: str
    model_name: str
    category: str
    run_timestamp: str
    universe: str
    total_stocks_analyzed: int
    stocks_with_data: int
    buy_signals: List[Dict]
    sell_signals: List[Dict]
    full_rankings: List[Dict]
    parameters: Dict[str, Any]
    errors: List[str]
    fetch_errors: List[Dict]


@router.get("/")
async def list_models():
    """List all available models with summaries"""
    models = []
    
    for model_id, model_class in ALL_MODELS.items():
        model = model_class()
        doc = get_model_documentation(model_id)
        models.append({
            "id": model_id,
            "name": model.name,
            "description": model.description,
            "category": model.category.value,
            "summary": doc.get("summary", model.description) if doc else model.description,
            "default_parameters": model.parameters
        })
    
    return {
        "total": len(models),
        "technical": len(TECHNICAL_MODELS),
        "fundamental": len(FUNDAMENTAL_MODELS),
        "models": models
    }


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
async def run_model(request: RunModelRequest):
    """Run a specific model and get signals"""
    
    if request.model_id not in ALL_MODELS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unknown model: {request.model_id}. Available: {list(ALL_MODELS.keys())}"
        )
    
    logger.info(f"Running model: {request.model_id} on universe: {request.universe}")
    
    # Get tickers - check custom universes first
    custom_manager = get_custom_universe_manager()
    custom_universe = custom_manager.get_universe(request.universe)
    
    if custom_universe:
        tickers = custom_universe.tickers
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
    result = model.run(price_data, fundamental_data)
    
    # Get fetch errors for debugging
    fetch_errors = fetcher.get_errors()
    
    # Save to history
    try:
        history_service = get_history_service()
        record = history_service.add_run(
            model_id=request.model_id,
            model_name=result.model_name,
            category=result.category,
            universe=request.universe,
            total_analyzed=len(tickers),
            stocks_with_data=len(price_data),
            buy_signals=[s.to_dict() for s in result.get_buy_signals(request.top_n)],
            sell_signals=[s.to_dict() for s in result.get_sell_signals(request.top_n)],
            parameters=result.parameters,
            errors=result.errors
        )
        logger.info(f"Saved run to history: {record.id}")
    except Exception as e:
        logger.error(f"Failed to save run to history: {str(e)}", exc_info=True)
        # Create a dummy record ID if history save fails
        record_id = f"run_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        record = type('Record', (), {'id': record_id})()
    
    return RunModelResponse(
        run_id=record.id,
        model_name=result.model_name,
        category=result.category,
        run_timestamp=result.run_timestamp.isoformat(),
        universe=request.universe,
        total_stocks_analyzed=len(tickers),
        stocks_with_data=len(price_data),
        buy_signals=[s.to_dict() for s in result.get_buy_signals(request.top_n)],
        sell_signals=[s.to_dict() for s in result.get_sell_signals(request.top_n)],
        full_rankings=result.rankings[:50],
        parameters=result.parameters,
        errors=result.errors,
        fetch_errors=fetch_errors[:10]
    )


@router.get("/history")
async def get_run_history(limit: int = Query(50, description="Maximum records to return")):
    """Get history of model runs"""
    history_service = get_history_service()
    return {
        "summary": history_service.get_summary(),
        "runs": history_service.get_all(limit)
    }


@router.get("/history/{run_id}")
async def get_run_details(run_id: str):
    """Get details of a specific run"""
    history_service = get_history_service()
    record = history_service.get_by_id(run_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
    return record.to_dict()


@router.get("/history/{run_id}/pdf")
async def export_run_pdf(run_id: str):
    """Export a run result as PDF"""
    try:
        history_service = get_history_service()
        record = history_service.get_by_id(run_id)
        
        if not record:
            raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
        
        # Get model documentation for description
        doc = get_model_documentation(record.model_id)
        description = doc.get("summary", "") if doc else ""
        
        # Generate PDF
        pdf_generator = get_pdf_generator()
        try:
            pdf_bytes = pdf_generator.generate_model_report(
                model_name=record.model_name,
                category=record.category,
                universe=record.universe,
                buy_signals=record.buy_signals,
                sell_signals=record.sell_signals,
                total_analyzed=record.total_analyzed,
                stocks_with_data=record.stocks_with_data,
                parameters=record.parameters,
                description=description,
                run_timestamp=record.run_timestamp
            )
        except Exception as e:
            logger.error(f"Error generating PDF for run {run_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate PDF: {str(e)}"
            )
        
        # Generate readable filename: ModelName_Universe_YYYY-MM-DD_HHMMSS.pdf
        # Parse timestamp to get date and time
        try:
            if 'T' in record.run_timestamp:
                dt = datetime.fromisoformat(record.run_timestamp.replace('Z', '+00:00'))
                date_str = dt.strftime('%Y-%m-%d_%H%M%S')
            else:
                # Try to parse timestamp and add time component
                dt = datetime.fromisoformat(record.run_timestamp) if len(record.run_timestamp) >= 10 else datetime.now()
                date_str = dt.strftime('%Y-%m-%d_%H%M%S')
        except (ValueError, AttributeError):
            # Fallback to current time with timestamp
            date_str = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        
        # Clean model name for filename (remove special chars, spaces)
        safe_model_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in record.model_name)
        safe_model_name = safe_model_name.replace(' ', '_')
        
        # Clean universe name
        safe_universe = record.universe.upper().replace(' ', '_')
        
        # Create filename: ModelName_Universe_YYYY-MM-DD_HHMMSS.pdf
        filename = f"{safe_model_name}_{safe_universe}_{date_str}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in PDF export for run {run_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/export-pdf")
async def export_current_pdf(request: RunModelRequest):
    """Run a model and immediately export as PDF"""
    # Run the model first
    result = await run_model(request)
    
    # Get documentation
    doc = get_model_documentation(request.model_id)
    description = doc.get("summary", "") if doc else ""
    
    # Generate PDF
    pdf_generator = get_pdf_generator()
    pdf_bytes = pdf_generator.generate_model_report(
        model_name=result.model_name,
        category=result.category,
        universe=result.universe,
        buy_signals=result.buy_signals,
        sell_signals=result.sell_signals,
        total_analyzed=result.total_stocks_analyzed,
        stocks_with_data=result.stocks_with_data,
        parameters=result.parameters,
        description=description,
        run_timestamp=result.run_timestamp
    )
    
    # Generate readable filename: ModelName_Universe_YYYY-MM-DD_HHMMSS.pdf
    try:
        if hasattr(result.run_timestamp, 'strftime'):
            dt = result.run_timestamp
            date_str = dt.strftime('%Y-%m-%d_%H%M%S')
        elif isinstance(result.run_timestamp, str) and 'T' in result.run_timestamp:
            dt = datetime.fromisoformat(result.run_timestamp.replace('Z', '+00:00'))
            date_str = dt.strftime('%Y-%m-%d_%H%M%S')
        else:
            date_str = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    except (ValueError, AttributeError):
        date_str = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    
    # Clean model name for filename (remove special chars, spaces)
    safe_model_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in result.model_name)
    safe_model_name = safe_model_name.replace(' ', '_')
    
    # Clean universe name
    safe_universe = result.universe.upper().replace(' ', '_')
    
    # Create filename: ModelName_Universe_YYYY-MM-DD_HHMMSS.pdf
    filename = f"{safe_model_name}_{safe_universe}_{date_str}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.delete("/history")
async def clear_history():
    """Clear all run history"""
    history_service = get_history_service()
    count = history_service.clear()
    return {"cleared": count}
