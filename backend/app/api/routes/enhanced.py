"""
Enhanced API Routes
- Enhanced Signal Combiner with model selection
- Rich signal context
- Model validation
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from fastapi.responses import Response
from app.data.fetcher import get_fetcher
from app.data.universe import get_tickers
from app.services.enhanced_combiner import (
    EnhancedSignalCombiner, CombineMethod, get_enhanced_combiner, reset_enhanced_combiner
)
from app.services.signal_context import get_signal_context_builder
from app.services.market_regime import get_regime_detector
from app.services.model_validation import ModelValidator, validate_model_historical
from app.services.pdf_generator import get_pdf_generator
from app.api.routes.models import ALL_MODELS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/enhanced", tags=["Enhanced Features"])


# ==================== REQUEST/RESPONSE MODELS ====================

class CombineSignalsRequest(BaseModel):
    """Request for combining signals from multiple models"""
    universe: str = Field(default="sp50", description="Stock universe to analyze")
    models: Optional[List[str]] = Field(
        default=None, 
        description="List of model IDs to include. If None, uses all models."
    )
    model_weights: Optional[Dict[str, float]] = Field(
        default=None,
        description="Custom weights for models. Higher = more influence."
    )
    combine_method: str = Field(
        default="weighted",
        description="How to combine: 'weighted', 'majority', 'unanimous', 'any'"
    )
    min_models: int = Field(
        default=3,
        description="Minimum models that must have data for a ticker"
    )
    min_confidence: float = Field(
        default=50.0,
        description="Minimum confidence score to include in results"
    )
    include_context: bool = Field(
        default=True,
        description="Include rich context (why, risks, historical stats)"
    )
    signal_filter: Optional[str] = Field(
        default=None,
        description="Filter results: 'BUY', 'SELL', or None for all"
    )
    top_n: int = Field(default=20, description="Maximum results to return")


class EnhancedSignalResponse(BaseModel):
    """Response with enhanced signal data"""
    ticker: str
    final_signal: str
    confidence: float
    confidence_label: str
    voting: Dict[str, int]
    agreeing_models: List[str]
    disagreeing_models: List[str]
    avg_score: float
    enhanced_context: Optional[Dict] = None


class ModelInfo(BaseModel):
    """Information about a model for selection"""
    id: str
    name: str
    category: str
    description: str
    default_weight: float
    enabled: bool


# ==================== ENDPOINTS ====================

@router.get("/models/available")
async def get_available_models():
    """
    Get all available models grouped by category.
    Use this to populate model selection UI.
    """
    combiner = get_enhanced_combiner()
    
    models_by_category = {
        "technical": [],
        "fundamental": [],
        "quantitative": []
    }
    
    for model_id, model_class in ALL_MODELS.items():
        try:
            model = model_class()
            weight_info = combiner.model_weights.get(model_id)
            
            model_info = ModelInfo(
                id=model_id,
                name=model.name,
                category=model.category.value.lower(),
                description=model.description,
                default_weight=weight_info.weight if weight_info else 1.0,
                enabled=weight_info.enabled if weight_info else True
            )
            
            category = model.category.value.lower()
            if category in models_by_category:
                models_by_category[category].append(model_info)
            else:
                models_by_category["technical"].append(model_info)
                
        except Exception as e:
            logger.warning(f"Could not load model {model_id}: {e}")
    
    # Convert to dicts for JSON serialization
    serialized = {
        cat: [m.model_dump() for m in models]
        for cat, models in models_by_category.items()
    }
    
    return {
        "models": [m.model_dump() for models in models_by_category.values() for m in models],
        "by_category": serialized,
        "total_models": sum(len(v) for v in models_by_category.values())
    }


@router.post("/combine-signals")
async def combine_signals(request: CombineSignalsRequest) -> Dict:
    """
    Combine signals from multiple models with rich context.
    
    This is the enhanced version of signal combiner that allows:
    - Selecting specific models to include
    - Custom weights for each model
    - Multiple combination methods
    - Rich context for each signal (why, risks, historical stats)
    """
    try:
        logger.info(f"Combining signals for universe: {request.universe}")
        
        # Get tickers
        tickers = get_tickers(request.universe)
        if not tickers:
            raise HTTPException(status_code=400, detail=f"Unknown universe: {request.universe}")
        
        # Reset and configure combiner
        reset_enhanced_combiner()
        combiner = get_enhanced_combiner()
        
        # Set model weights if provided
        if request.model_weights:
            combiner.set_model_weights(request.model_weights)
        
        # Enable only selected models if provided
        if request.models:
            combiner.enable_models(request.models)
        
        # Fetch data
        fetcher = get_fetcher()
        logger.info(f"Fetching data for {len(tickers)} tickers...")
        
        price_data = fetcher.get_bulk_price_data(tickers, period="1y")
        fundamental_data = fetcher.get_bulk_fundamental_data(tickers)
        
        # Get market regime for context
        market_regime = None
        try:
            index_data = fetcher.get_price_data("SPY", period="2y")
            if index_data is not None and len(index_data) >= 252:
                detector = get_regime_detector()
                regime = detector.detect_regime(index_data)
                market_regime = detector.to_dict(regime)
        except Exception as e:
            logger.warning(f"Could not get market regime: {e}")
        
        # Run all enabled models
        enabled_models = combiner.get_enabled_models()
        logger.info(f"Running {len(enabled_models)} models...")
        
        models_run = 0
        for model_id in enabled_models:
            if model_id not in ALL_MODELS:
                continue
            
            try:
                model = ALL_MODELS[model_id]()
                result = model.run(price_data, fundamental_data)
                combiner.add_model_result(model_id, result)
                models_run += 1
            except Exception as e:
                logger.warning(f"Model {model_id} failed: {e}")
        
        logger.info(f"Successfully ran {models_run} models")
        
        # Combine signals
        combine_method = CombineMethod(request.combine_method)
        
        combined_signals = combiner.combine_signals(
            method=combine_method,
            min_models=request.min_models,
            min_confidence=request.min_confidence,
            include_context=request.include_context,
            price_data=price_data,
            fundamental_data=fundamental_data,
            market_regime=market_regime
        )
        
        # Filter by signal type if requested
        if request.signal_filter:
            combined_signals = [
                s for s in combined_signals 
                if s.final_signal == request.signal_filter
            ]
        
        # Limit results
        combined_signals = combined_signals[:request.top_n]
        
        # Convert to response format
        results = [s.to_dict() for s in combined_signals]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "universe": request.universe,
            "total_tickers": len(tickers),
            "models_used": models_run,
            "enabled_models": enabled_models,
            "combine_method": request.combine_method,
            "market_regime": market_regime.get("regime") if market_regime else "UNKNOWN",
            "signals_count": len(results),
            "buy_count": sum(1 for s in combined_signals if s.final_signal == "BUY"),
            "sell_count": sum(1 for s in combined_signals if s.final_signal == "SELL"),
            "signals": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error combining signals: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-agreement")
async def get_model_agreement(
    universe: str = Query("sp50", description="Universe to analyze")
) -> Dict:
    """
    Get model agreement matrix showing how often models agree with each other.
    Useful for understanding model correlations and diversification.
    """
    try:
        # Get tickers
        tickers = get_tickers(universe)
        if not tickers:
            raise HTTPException(status_code=400, detail=f"Unknown universe: {universe}")
        
        # Fetch data
        fetcher = get_fetcher()
        price_data = fetcher.get_bulk_price_data(tickers, period="1y")
        fundamental_data = fetcher.get_bulk_fundamental_data(tickers)
        
        # Run all models
        combiner = get_enhanced_combiner()
        
        for model_id, model_class in ALL_MODELS.items():
            try:
                model = model_class()
                result = model.run(price_data, fundamental_data)
                combiner.add_model_result(model_id, result)
            except Exception as e:
                logger.warning(f"Model {model_id} failed: {e}")
        
        # Get agreement matrix
        matrix = combiner.get_model_agreement_matrix()
        
        return {
            "universe": universe,
            "models": list(matrix.columns),
            "agreement_matrix": matrix.to_dict(),
            "avg_agreement": matrix.values.mean()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating model agreement: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/signal-context/{ticker}")
async def get_signal_context(
    ticker: str,
    model_id: str = Query(..., description="Model that generated the signal"),
    signal_type: str = Query(..., description="Signal type: BUY or SELL"),
    score: float = Query(..., description="Signal score")
) -> Dict:
    """
    Get rich context for a specific signal.
    Returns: why, confirmations, risks, historical stats, position suggestion.
    """
    try:
        fetcher = get_fetcher()
        
        # Get data for this ticker
        price_data = fetcher.get_bulk_price_data([ticker], period="1y")
        fundamental_data = fetcher.get_bulk_fundamental_data([ticker])
        
        # Get market regime
        market_regime = None
        try:
            index_data = fetcher.get_price_data("SPY", period="2y")
            if index_data is not None and len(index_data) >= 252:
                detector = get_regime_detector()
                regime = detector.detect_regime(index_data)
                market_regime = detector.to_dict(regime)
        except:
            pass
        
        # Build context
        context_builder = get_signal_context_builder()
        context_builder.set_price_data(price_data)
        if fundamental_data is not None:
            context_builder.set_fundamental_data(fundamental_data)
        if market_regime:
            context_builder.set_market_regime(market_regime)
        
        enhanced_signal = context_builder.build_enhanced_signal(
            ticker=ticker,
            signal_type=signal_type,
            score=score,
            model_id=model_id,
            all_scores=[score]  # Single score for percentile
        )
        
        return enhanced_signal.to_dict()
        
    except Exception as e:
        logger.error(f"Error getting signal context: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MODEL VALIDATION ====================

class ValidateModelRequest(BaseModel):
    """Request for model validation"""
    model_id: str = Field(..., description="Model ID to validate")
    universe: str = Field(default="sp50", description="Universe to test on")
    holding_period: int = Field(default=21, description="Holding period in trading days")
    n_simulations: int = Field(default=50, description="Number of historical simulations")


@router.post("/validate-model")
async def validate_model(request: ValidateModelRequest) -> Dict:
    """
    Validate a model's effectiveness through historical backtesting.
    
    Returns comprehensive metrics including:
    - Win rate, profit factor, average returns
    - Statistical significance (t-test, p-value)
    - Risk metrics (Sharpe, Sortino, max drawdown)
    - Comparison to benchmark (alpha, beta)
    - Verdict: EXCELLENT, GOOD, MARGINAL, or POOR
    """
    try:
        if request.model_id not in ALL_MODELS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown model: {request.model_id}"
            )
        
        logger.info(f"Validating model: {request.model_id}")
        
        # Get tickers
        tickers = get_tickers(request.universe)
        if not tickers:
            raise HTTPException(status_code=400, detail=f"Unknown universe: {request.universe}")
        
        # Fetch data
        fetcher = get_fetcher()
        price_data = fetcher.get_bulk_price_data(tickers, period="2y")
        fundamental_data = fetcher.get_bulk_fundamental_data(tickers)
        
        # Run validation
        model_class = ALL_MODELS[request.model_id]
        
        metrics = validate_model_historical(
            model_class=model_class,
            model_id=request.model_id,
            price_data=price_data,
            fundamental_data=fundamental_data,
            holding_period=request.holding_period,
            n_simulations=request.n_simulations
        )
        
        return {
            "timestamp": datetime.now().isoformat(),
            "request": {
                "model_id": request.model_id,
                "universe": request.universe,
                "holding_period": request.holding_period,
                "n_simulations": request.n_simulations,
            },
            "validation": metrics.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validate-all-models")
async def validate_all_models(
    universe: str = Query("sp50", description="Universe to test on"),
    holding_period: int = Query(21, description="Holding period in days"),
    n_simulations: int = Query(30, description="Simulations per model")
) -> Dict:
    """
    Validate all models and rank them by effectiveness.
    
    Returns a leaderboard of models sorted by their validation score.
    """
    try:
        logger.info(f"Validating all models on {universe}")
        
        # Get tickers
        tickers = get_tickers(universe)
        if not tickers:
            raise HTTPException(status_code=400, detail=f"Unknown universe: {universe}")
        
        # Fetch data once
        fetcher = get_fetcher()
        price_data = fetcher.get_bulk_price_data(tickers, period="2y")
        fundamental_data = fetcher.get_bulk_fundamental_data(tickers)
        
        results = []
        
        for model_id, model_class in ALL_MODELS.items():
            try:
                logger.info(f"Validating {model_id}...")
                
                metrics = validate_model_historical(
                    model_class=model_class,
                    model_id=model_id,
                    price_data=price_data,
                    fundamental_data=fundamental_data,
                    holding_period=holding_period,
                    n_simulations=n_simulations
                )
                
                result_dict = metrics.to_dict()
                results.append({
                    "model_id": model_id,
                    "model_name": metrics.model_name,
                    "verdict": result_dict["verdict"]["verdict"],
                    "score": result_dict["verdict"]["score"],
                    "win_rate": float(metrics.win_rate),
                    "avg_return": float(metrics.avg_return),
                    "sharpe_ratio": float(metrics.sharpe_ratio),
                    "is_significant": bool(metrics.is_significant),
                    "alpha": float(metrics.alpha),
                    "total_signals": int(metrics.total_signals),
                })
                
            except Exception as e:
                logger.warning(f"Failed to validate {model_id}: {e}")
                results.append({
                    "model_id": model_id,
                    "model_name": model_id,
                    "verdict": "ERROR",
                    "score": 0,
                    "error": str(e)
                })
        
        # Sort by score
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "universe": universe,
            "holding_period": holding_period,
            "models_tested": len(results),
            "leaderboard": results,
            "top_models": [r["model_id"] for r in results[:5] if r.get("verdict") in ["EXCELLENT", "GOOD"]],
            "avoid_models": [r["model_id"] for r in results if r.get("verdict") == "POOR"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating all models: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ENHANCED PDF EXPORT ====================

class EnhancedPDFRequest(BaseModel):
    """Request for enhanced PDF with rich context"""
    model_id: str = Field(..., description="Model ID")
    universe: str = Field(default="sp50", description="Universe")
    top_n: int = Field(default=10, description="Top N signals")
    include_context: bool = Field(default=True, description="Include rich context")


@router.post("/export-pdf")
async def export_enhanced_pdf(request: EnhancedPDFRequest):
    """
    Export model results as enhanced PDF with rich context.
    Includes: WHY signals were generated, risk factors, position suggestions.
    """
    try:
        if request.model_id not in ALL_MODELS:
            raise HTTPException(status_code=400, detail=f"Unknown model: {request.model_id}")
        
        logger.info(f"Generating enhanced PDF for {request.model_id}")
        
        # Get tickers
        tickers = get_tickers(request.universe)
        if not tickers:
            raise HTTPException(status_code=400, detail=f"Unknown universe: {request.universe}")
        
        # Fetch data
        fetcher = get_fetcher()
        price_data = fetcher.get_bulk_price_data(tickers, period="1y")
        fundamental_data = fetcher.get_bulk_fundamental_data(tickers)
        
        # Get market regime
        market_regime = None
        try:
            index_data = fetcher.get_price_data("SPY", period="2y")
            if index_data is not None and len(index_data) >= 252:
                detector = get_regime_detector()
                regime = detector.detect_regime(index_data)
                market_regime = detector.to_dict(regime)
        except Exception as e:
            logger.warning(f"Could not get market regime: {e}")
        
        # Run model
        model_class = ALL_MODELS[request.model_id]
        model = model_class()
        result = model.run(price_data, fundamental_data)
        
        # Build enhanced context for each signal
        buy_signals = []
        sell_signals = []
        
        if request.include_context:
            context_builder = get_signal_context_builder()
            context_builder.set_price_data(price_data)
            if fundamental_data is not None:
                context_builder.set_fundamental_data(fundamental_data)
            if market_regime:
                context_builder.set_market_regime(market_regime)
            context_builder.set_model_results(request.model_id, result)
            
            for ranking in result.rankings[:request.top_n]:
                signal_type = ranking.get('signal', 'HOLD')
                if signal_type == 'HOLD':
                    continue
                
                try:
                    enhanced = context_builder.build_enhanced_signal(
                        ticker=ranking['ticker'],
                        signal_type=signal_type,
                        score=ranking.get('score', 50),
                        model_id=request.model_id,
                        all_scores=[r.get('score', 50) for r in result.rankings]
                    )
                    
                    signal_data = {
                        'ticker': ranking['ticker'],
                        'score': ranking.get('score', 0),
                        'price_at_signal': ranking.get('price', 0),
                        'enhanced_context': enhanced.to_dict() if enhanced else {}
                    }
                    
                    if signal_type == 'BUY':
                        buy_signals.append(signal_data)
                    else:
                        sell_signals.append(signal_data)
                except Exception as e:
                    logger.warning(f"Failed to build context for {ranking['ticker']}: {e}")
                    signal_data = {
                        'ticker': ranking['ticker'],
                        'score': ranking.get('score', 0),
                        'price_at_signal': ranking.get('price', 0),
                        'enhanced_context': {}
                    }
                    if signal_type == 'BUY':
                        buy_signals.append(signal_data)
                    else:
                        sell_signals.append(signal_data)
        else:
            # Without context
            for ranking in result.rankings[:request.top_n]:
                signal_type = ranking.get('signal', 'HOLD')
                if signal_type == 'HOLD':
                    continue
                signal_data = {
                    'ticker': ranking['ticker'],
                    'score': ranking.get('score', 0),
                    'price_at_signal': ranking.get('price', 0),
                    'enhanced_context': {}
                }
                if signal_type == 'BUY':
                    buy_signals.append(signal_data)
                else:
                    sell_signals.append(signal_data)
        
        # Generate PDF
        pdf_generator = get_pdf_generator()
        pdf_bytes = pdf_generator.generate_enhanced_signal_report(
            model_name=model.name,
            universe=request.universe,
            buy_signals=buy_signals,
            sell_signals=sell_signals,
            market_regime=market_regime,
            total_analyzed=len(tickers),
            stocks_with_data=len(result.rankings),
            description=model.description
        )
        
        filename = f"{request.model_id}_{request.universe}_enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating enhanced PDF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
