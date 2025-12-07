"""
Advanced Features API Routes
Signal Combinations, Sector Rotation, Market Regime, Backtesting
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import logging
import csv
import io
import json

from app.data.fetcher import get_fetcher
from app.data.universe import get_tickers
from app.services.signal_combiner import get_signal_combiner
from app.services.sector_rotation import get_sector_analyzer
from app.services.backtester import get_backtester
from app.services.pdf_generator import get_pdf_generator

from app.api.routes.models import ALL_MODELS, TECHNICAL_MODELS, FUNDAMENTAL_MODELS, QUANTITATIVE_MODELS
from app.services.market_regime import get_regime_detector

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== SIGNAL COMBINATIONS ====================

class RunCombinedRequest(BaseModel):
    universe: str = "sp50"
    models: Optional[List[str]] = None  # If None, run all
    min_confirmation: int = 3
    category: Optional[str] = None  # "technical", "fundamental", or None for all


@router.post("/signal-combiner")
async def run_signal_combiner(request: RunCombinedRequest):
    """
    Run multiple models and combine signals for confirmation.
    Stocks appearing in multiple model outputs get higher confidence.
    """
    logger.info(f"Running signal combiner on {request.universe}")
    
    # Determine which models to run
    if request.models:
        models_to_run = {k: v for k, v in ALL_MODELS.items() if k in request.models}
    elif request.category == "technical":
        models_to_run = TECHNICAL_MODELS
    elif request.category == "fundamental":
        models_to_run = FUNDAMENTAL_MODELS
    else:
        models_to_run = ALL_MODELS
    
    if not models_to_run:
        raise HTTPException(status_code=400, detail="No models specified")
    
    # Fetch data
    tickers = get_tickers(request.universe)
    fetcher = get_fetcher()
    price_data = fetcher.get_bulk_price_data(tickers, period="1y")
    fundamental_data = fetcher.get_bulk_fundamental_data(tickers)
    
    # Run all models
    model_results = {}
    for model_id, model_class in models_to_run.items():
        try:
            model = model_class()
            result = model.run(price_data, fundamental_data)
            model_results[model_id] = {
                "buy_signals": [s.to_dict() for s in result.get_buy_signals(20)],
                "sell_signals": [s.to_dict() for s in result.get_sell_signals(20)]
            }
        except Exception as e:
            logger.warning(f"Error running {model_id}: {e}")
    
    # Combine signals
    combiner = get_signal_combiner()
    combiner.min_confirmation = request.min_confirmation
    
    report = combiner.get_consensus_report(model_results)
    report["models_run"] = list(model_results.keys())
    report["universe"] = request.universe
    
    return report


@router.get("/signal-combiner/quick")
async def quick_signal_combiner(
    universe: str = Query("sp50"),
    min_confirmation: int = Query(3)
):
    """Quick endpoint to get combined signals"""
    request = RunCombinedRequest(
        universe=universe,
        min_confirmation=min_confirmation
    )
    return await run_signal_combiner(request)


# ==================== SECTOR ROTATION ====================

@router.get("/sector-rotation")
async def analyze_sector_rotation(
    universe: str = Query("sp500", description="Universe to analyze")
):
    """
    Analyze sector performance and rotation opportunities.
    Returns sector rankings by momentum and rotation recommendations.
    """
    logger.info(f"Analyzing sector rotation for {universe}")
    
    tickers = get_tickers(universe)
    fetcher = get_fetcher()
    price_data = fetcher.get_bulk_price_data(tickers, period="1y")
    
    analyzer = get_sector_analyzer()
    result = analyzer.analyze_sector_rotation(price_data, universe)
    
    return result


# ==================== MARKET REGIME ====================

@router.get("/market-regime")
async def detect_market_regime(
    index: str = Query("SPY", description="Market index ticker (SPY, ^SET.BK, etc.)"),
    universe: Optional[str] = Query(None, description="Universe for breadth calculation")
):
    """
    Detect current market regime (Bull/Bear/Neutral).
    Uses moving averages, momentum, and breadth indicators.
    """
    try:
        logger.info(f"Detecting market regime using {index}")
        
        fetcher = get_fetcher()
        
        # Get index data - try different ticker formats if needed
        index_data = fetcher.get_price_data(index, period="2y")
        
        # If data fetch failed, try alternative ticker formats
        if index_data is None or len(index_data) < 252:
            # Try alternative formats for common indices
            alternative_tickers = {
                "^SET": ["^SET.BK", "SET.BK", "SET"],
                "^SET.BK": ["^SET.BK", "SET.BK", "^SET"],
                "SET.BK": ["^SET.BK", "SET.BK", "^SET"],
                "SET": ["^SET.BK", "SET.BK", "^SET"],
            }
            
            if index in alternative_tickers:
                for alt_ticker in alternative_tickers[index]:
                    logger.info(f"Trying alternative ticker format: {alt_ticker}")
                    index_data = fetcher.get_price_data(alt_ticker, period="2y")
                    if index_data is not None and len(index_data) >= 252:
                        index = alt_ticker  # Use the working ticker
                        break
        
        if index_data is None:
            raise HTTPException(
                status_code=400, 
                detail=f"Could not fetch data for index: {index}. Please try a different index like SPY, QQQ, or DIA. For Thai market, try '^SET.BK' (with caret)."
            )
        
        if len(index_data) < 252:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient data for index: {index}. Got {len(index_data)} rows, need at least 252 trading days. Try using a different index or check if the ticker is correct."
            )
        
        # Get universe data for breadth
        universe_data = None
        if universe:
            try:
                tickers = get_tickers(universe)
                if tickers:
                    logger.info(f"Fetching universe data for breadth calculation: {len(tickers)} tickers")
                    universe_data = fetcher.get_bulk_price_data(tickers, period="3mo")
                    # Filter out None or empty dataframes
                    if universe_data:
                        universe_data = {k: v for k, v in universe_data.items() if v is not None and not v.empty and len(v) > 0}
                        logger.info(f"Successfully fetched data for {len(universe_data)} stocks in universe")
                        if len(universe_data) == 0:
                            logger.warning("No valid universe data available for breadth calculation")
                            universe_data = None
            except Exception as e:
                logger.warning(f"Could not fetch universe data for breadth: {e}", exc_info=True)
                universe_data = None
        
        # Detect market regime
        detector = get_regime_detector()
        regime = detector.detect_regime(index_data, universe_data)
        
        return {
            "index": index,
            "universe": universe,
            **detector.to_dict(regime)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detecting market regime: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to detect market regime: {str(e)}")


@router.get("/market-regime/quick")
async def quick_market_regime():
    """Quick market regime check using SPY"""
    return await detect_market_regime(index="SPY", universe="sp50")


@router.post("/signal-combiner/export-pdf")
async def export_signal_combiner_pdf(result: Dict):
    """Export signal combiner results as PDF"""
    try:
        pdf_generator = get_pdf_generator()
        pdf_bytes = pdf_generator.generate_signal_combiner_report(
            universe=result.get('universe', 'unknown'),
            total_models=result.get('total_models_analyzed', 0),
            min_confirmation=result.get('min_confirmation', 3),
            strong_buy_signals=result.get('strong_buy_signals', []),
            moderate_buy_signals=result.get('moderate_buy_signals', []),
            strong_sell_signals=result.get('strong_sell_signals', []),
            timestamp=result.get('timestamp')
        )
        
        safe_universe = result.get('universe', 'unknown').upper().replace(' ', '_')
        date_str = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        filename = f"SignalCombiner_{safe_universe}_{date_str}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        logger.error(f"Error generating signal combiner PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


@router.post("/sector-rotation/export-pdf")
async def export_sector_rotation_pdf(result: Dict):
    """Export sector rotation analysis as PDF"""
    try:
        pdf_generator = get_pdf_generator()
        pdf_bytes = pdf_generator.generate_sector_rotation_report(
            universe=result.get('universe', 'unknown'),
            sector_rankings=result.get('sector_rankings', []),
            rotation_recommendation=result.get('rotation_recommendation', {}),
            timestamp=result.get('timestamp')
        )
        
        safe_universe = result.get('universe', 'unknown').upper().replace(' ', '_')
        date_str = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        filename = f"SectorRotation_{safe_universe}_{date_str}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        logger.error(f"Error generating sector rotation PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


@router.post("/market-regime/export-pdf")
async def export_market_regime_pdf(result: Dict):
    """Export market regime detection as PDF"""
    try:
        pdf_generator = get_pdf_generator()
        pdf_bytes = pdf_generator.generate_market_regime_report(
            index=result.get('index', 'SPY'),
            regime=result,
            timestamp=result.get('timestamp')
        )
        
        index_name = result.get('index', 'SPY').replace('^', '').replace('.', '_')
        date_str = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        filename = f"MarketRegime_{index_name}_{date_str}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        logger.error(f"Error generating market regime PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


@router.get("/market-regime/pdf")
async def get_market_regime_pdf(
    index: str = Query("SPY", description="Market index ticker"),
    universe: Optional[str] = Query(None, description="Universe for breadth calculation")
):
    """Detect market regime and export as PDF in one call"""
    try:
        # First detect the regime
        fetcher = get_fetcher()
        detector = get_regime_detector()
        
        # Get index data
        index_data = fetcher.get_price_data(index, period="2y")
        if index_data is None or len(index_data) < 252:
            raise HTTPException(status_code=400, detail=f"Insufficient data for {index}")
        
        # Detect regime
        regime = detector.detect_regime(index_data)
        result = detector.to_dict(regime)
        result['index'] = index
        result['timestamp'] = datetime.now().isoformat()
        
        # Calculate breadth if universe provided
        if universe:
            tickers = get_tickers(universe)
            if tickers:
                price_data = fetcher.get_bulk_price_data(tickers, period="6mo")
                breadth = detector.calculate_breadth(price_data)
                result['breadth'] = breadth
        
        # Generate PDF
        pdf_generator = get_pdf_generator()
        pdf_bytes = pdf_generator.generate_market_regime_report(
            index=index,
            regime=result,
            timestamp=result.get('timestamp')
        )
        
        index_name = index.replace('^', '').replace('.', '_')
        date_str = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        filename = f"MarketRegime_{index_name}_{date_str}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating market regime PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


# ==================== BACKTESTING ====================

class BacktestRequest(BaseModel):
    model_id: str
    universe: str = "sp50"
    initial_capital: float = 100000
    holding_period: int = 21  # Days
    top_n: int = 10


@router.post("/backtest")
async def run_backtest(request: BacktestRequest):
    """
    Run a simple backtest for a model.
    
    Note: This is a simplified backtest. Results are indicative only.
    For production use, consider more sophisticated backtesting tools.
    """
    if request.model_id not in ALL_MODELS:
        raise HTTPException(status_code=400, detail=f"Unknown model: {request.model_id}")
    
    logger.info(f"Running backtest for {request.model_id} on {request.universe}")
    
    # Fetch data
    tickers = get_tickers(request.universe)
    fetcher = get_fetcher()
    price_data = fetcher.get_bulk_price_data(tickers, period="2y")
    fundamental_data = fetcher.get_bulk_fundamental_data(tickers)
    
    # Run backtest
    backtester = get_backtester()
    backtester.initial_capital = request.initial_capital
    backtester.holding_period = request.holding_period
    backtester.top_n = request.top_n
    
    model_class = ALL_MODELS[request.model_id]
    
    try:
        result = backtester.run_backtest(
            model_class=model_class,
            price_data=price_data,
            fundamental_data=fundamental_data
        )
        return backtester.to_dict(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest error: {str(e)}")


@router.get("/backtest/{model_id}")
async def quick_backtest(
    model_id: str,
    universe: str = Query("sp50")
):
    """Quick backtest endpoint"""
    request = BacktestRequest(model_id=model_id, universe=universe)
    return await run_backtest(request)


@router.post("/backtest/export-pdf")
async def export_backtest_pdf(backtest_result: Dict):
    """Export backtest results as PDF"""
    try:
        pdf_generator = get_pdf_generator()
        pdf_bytes = pdf_generator.generate_backtest_report(
            model_name=backtest_result.get('model_name', 'Unknown Model'),
            universe=backtest_result.get('universe', 'unknown'),
            period=backtest_result.get('period', ''),
            performance=backtest_result.get('performance', {}),
            trades=backtest_result.get('trades', {}),
            equity_curve=backtest_result.get('equity_curve', []),
            recent_trades=backtest_result.get('recent_trades', [])
        )
        
        # Generate filename
        safe_model_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in backtest_result.get('model_name', 'Model'))
        safe_model_name = safe_model_name.replace(' ', '_')
        safe_universe = backtest_result.get('universe', 'unknown').upper().replace(' ', '_')
        date_str = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        filename = f"Backtest_{safe_model_name}_{safe_universe}_{date_str}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        logger.error(f"Error generating backtest PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


@router.post("/backtest/export-csv")
async def export_backtest_csv(backtest_result: Dict):
    """Export backtest results as CSV (trades and equity curve)"""
    try:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Backtest Results Export'])
        writer.writerow(['Model', backtest_result.get('model_name', 'Unknown')])
        writer.writerow(['Universe', backtest_result.get('universe', 'unknown')])
        writer.writerow(['Period', backtest_result.get('period', '')])
        writer.writerow([])
        
        # Performance metrics
        perf = backtest_result.get('performance', {})
        writer.writerow(['Performance Metrics'])
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Initial Capital', f"${perf.get('initial_capital', 0):,.2f}"])
        writer.writerow(['Final Value', f"${perf.get('final_value', 0):,.2f}"])
        writer.writerow(['Total Return %', f"{perf.get('total_return_pct', 0):.2f}%"])
        writer.writerow(['Annualized Return %', f"{perf.get('annualized_return_pct', 0):.2f}%"])
        writer.writerow(['Sharpe Ratio', f"{perf.get('sharpe_ratio', 0):.2f}"])
        writer.writerow(['Max Drawdown %', f"{perf.get('max_drawdown_pct', 0):.2f}%"])
        writer.writerow([])
        
        # Trade statistics
        trade_stats = backtest_result.get('trades', {})
        writer.writerow(['Trade Statistics'])
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Trades', trade_stats.get('total', 0)])
        writer.writerow(['Winning Trades', trade_stats.get('winning', 0)])
        writer.writerow(['Losing Trades', trade_stats.get('losing', 0)])
        writer.writerow(['Win Rate %', f"{trade_stats.get('win_rate_pct', 0):.1f}%"])
        writer.writerow(['Avg Win %', f"{trade_stats.get('avg_win_pct', 0):.2f}%"])
        writer.writerow(['Avg Loss %', f"{trade_stats.get('avg_loss_pct', 0):.2f}%"])
        writer.writerow(['Profit Factor', f"{trade_stats.get('profit_factor', 0):.2f}"])
        writer.writerow([])
        
        # Equity curve
        equity_curve = backtest_result.get('equity_curve', [])
        if equity_curve:
            writer.writerow(['Equity Curve'])
            writer.writerow(['Date', 'Equity'])
            for point in equity_curve:
                writer.writerow([point.get('date', ''), f"{point.get('equity', 0):.2f}"])
            writer.writerow([])
        
        # Trades
        trades = backtest_result.get('recent_trades', [])
        if trades:
            writer.writerow(['Trades'])
            writer.writerow(['Entry Date', 'Exit Date', 'Ticker', 'Entry Price', 'Exit Price', 'Return %', 'P&L'])
            for trade in trades:
                writer.writerow([
                    trade.get('entry_date', ''),
                    trade.get('exit_date', ''),
                    trade.get('ticker', '').replace('.BK', ''),
                    f"{trade.get('entry_price', 0):.2f}",
                    f"{trade.get('exit_price', 0):.2f}",
                    f"{trade.get('return_pct', 0):.2f}%",
                    f"{trade.get('pnl', 0):.2f}"
                ])
        
        csv_content = output.getvalue()
        output.close()
        
        # Generate filename
        safe_model_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in backtest_result.get('model_name', 'Model'))
        safe_model_name = safe_model_name.replace(' ', '_')
        safe_universe = backtest_result.get('universe', 'unknown').upper().replace(' ', '_')
        date_str = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        filename = f"Backtest_{safe_model_name}_{safe_universe}_{date_str}.csv"
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        logger.error(f"Error generating backtest CSV: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate CSV: {str(e)}")


# ==================== DASHBOARD SUMMARY ====================

@router.get("/dashboard-summary")
async def get_dashboard_summary(
    universe: str = Query("sp50")
):
    """
    Get a comprehensive dashboard summary including:
    - Market regime
    - Top sector
    - Strongest combined signals
    """
    try:
        # Market regime - removed due to reliability issues
        regime_result = {
            "regime": "UNKNOWN",
            "risk_level": "MEDIUM",
            "recommended_exposure": 50,
            "recommendation": "Market regime detection temporarily unavailable"
        }
        
        # Run quick signal combiner with top 5 models
        top_models = ["dual_ema", "rsi_reversal", "value_composite", "quality_score", "minervini_trend"]
        combiner_request = RunCombinedRequest(
            universe=universe,
            models=top_models,
            min_confirmation=2
        )
        combined_result = await run_signal_combiner(combiner_request)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "universe": universe,
            "market_regime": {
                "regime": regime_result["regime"],
                "risk_level": regime_result["risk_level"],
                "recommended_exposure": regime_result["recommended_exposure"],
                "recommendation": regime_result["recommendation"]
            },
            "top_combined_buys": combined_result.get("strong_buy_signals", [])[:5],
            "top_combined_sells": combined_result.get("strong_sell_signals", [])[:5],
            "models_analyzed": len(top_models)
        }
    except Exception as e:
        logger.error(f"Dashboard summary error: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "universe": universe,
            "error": str(e),
            "market_regime": {"regime": "UNKNOWN"},
            "top_combined_buys": [],
            "top_combined_sells": []
        }
