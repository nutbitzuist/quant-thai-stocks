"""
Backtesting API Routes
VectorBT backtesting and QuantStats reporting endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from app.data.fetcher import get_fetcher
from app.data.universe import get_tickers
from app.services.vectorbt_backtest import get_backtester, BacktestResult, OptimizationResult, WalkForwardResult, MonteCarloResult
from app.services.quantstats_report import get_reporter, TearsheetData
from app.services.custom_universe import get_custom_universe_manager
from app.api.routes.models import ALL_MODELS

logger = logging.getLogger(__name__)

router = APIRouter()


class BacktestRequest(BaseModel):
    """Request for running a backtest"""
    model_id: str
    universe: str = "sp50"
    parameters: Optional[Dict[str, Any]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    initial_capital: float = 100000.0
    position_size: str = "equal"  # equal, score_weighted
    max_positions: int = 20
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


class OptimizationRequest(BaseModel):
    """Request for parameter optimization"""
    model_id: str
    universe: str = "sp50"
    param_grid: Dict[str, List[Any]]
    metric: str = "sharpe_ratio"  # sharpe_ratio, total_return, calmar_ratio


class WalkForwardRequest(BaseModel):
    """Request for walk-forward analysis"""
    model_id: str
    universe: str = "sp50"
    parameters: Optional[Dict[str, Any]] = None
    in_sample_pct: float = 0.7
    n_splits: int = 5


class MonteCarloRequest(BaseModel):
    """Request for Monte Carlo simulation"""
    model_id: str
    universe: str = "sp50"
    parameters: Optional[Dict[str, Any]] = None
    n_simulations: int = 1000
    time_horizon: int = 252


@router.post("/run")
async def run_backtest(request: BacktestRequest):
    """
    Run a full portfolio backtest using VectorBT
    
    Returns comprehensive backtest results including:
    - Performance metrics (returns, Sharpe, Sortino, etc.)
    - Risk metrics (volatility, max drawdown, VaR)
    - Trade statistics
    - Equity curve and drawdown data for charting
    """
    
    if request.model_id not in ALL_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model: {request.model_id}. Available: {list(ALL_MODELS.keys())}"
        )
    
    logger.info(f"Running backtest for {request.model_id} on {request.universe}")
    
    # Get tickers
    custom_manager = get_custom_universe_manager()
    custom_universe = custom_manager.get_universe(request.universe)
    
    if custom_universe:
        tickers = custom_universe.tickers
    else:
        tickers = get_tickers(request.universe)
    
    if not tickers:
        raise HTTPException(status_code=400, detail=f"Unknown universe: {request.universe}")
    
    # Fetch data
    fetcher = get_fetcher()
    price_data = fetcher.get_bulk_price_data(tickers, period="2y")
    
    # Get fundamental data if needed
    fundamental_data = None
    from app.api.routes.models import FUNDAMENTAL_MODELS
    if request.model_id in FUNDAMENTAL_MODELS:
        fundamental_data = fetcher.get_bulk_fundamental_data(tickers)
    
    # Run model
    model_class = ALL_MODELS[request.model_id]
    params = request.parameters or {}
    model = model_class(**params)
    result = model.run(price_data, fundamental_data)
    
    # Get signals
    signals = [s.to_dict() for s in result.signals]
    
    # Run backtest
    backtester = get_backtester()
    backtester.initial_capital = request.initial_capital
    
    backtest_result = backtester.run_backtest(
        price_data=price_data,
        signals=signals,
        strategy_name=f"{model.name} Backtest",
        start_date=request.start_date,
        end_date=request.end_date,
        position_size=request.position_size,
        max_positions=request.max_positions,
        stop_loss=request.stop_loss,
        take_profit=request.take_profit
    )
    
    return backtest_result.to_dict()


@router.post("/optimize")
async def optimize_parameters(request: OptimizationRequest):
    """
    Run parameter optimization using grid search
    
    Tests all combinations of parameters and returns the best performing set
    based on the specified metric (Sharpe ratio, total return, etc.)
    """
    
    if request.model_id not in ALL_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model: {request.model_id}"
        )
    
    logger.info(f"Running optimization for {request.model_id}")
    
    # Get tickers
    tickers = get_tickers(request.universe)
    if not tickers:
        raise HTTPException(status_code=400, detail=f"Unknown universe: {request.universe}")
    
    # Fetch data
    fetcher = get_fetcher()
    price_data = fetcher.get_bulk_price_data(tickers, period="2y")
    
    # Run optimization
    backtester = get_backtester()
    model_class = ALL_MODELS[request.model_id]
    
    result = backtester.optimize_parameters(
        price_data=price_data,
        model_class=model_class,
        param_grid=request.param_grid,
        universe=tickers,
        metric=request.metric
    )
    
    return {
        "best_params": result.best_params,
        "best_sharpe": result.best_sharpe,
        "best_return": result.best_return,
        "all_results": result.all_results[:50]  # Limit results
    }


@router.post("/walk-forward")
async def walk_forward_analysis(request: WalkForwardRequest):
    """
    Run walk-forward analysis for strategy robustness testing
    
    Splits data into multiple in-sample/out-of-sample periods to test
    how well the strategy performs on unseen data.
    """
    
    if request.model_id not in ALL_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model: {request.model_id}"
        )
    
    logger.info(f"Running walk-forward analysis for {request.model_id}")
    
    # Get tickers
    tickers = get_tickers(request.universe)
    if not tickers:
        raise HTTPException(status_code=400, detail=f"Unknown universe: {request.universe}")
    
    # Fetch data
    fetcher = get_fetcher()
    price_data = fetcher.get_bulk_price_data(tickers, period="3y")
    
    # Get fundamental data if needed
    fundamental_data = None
    from app.api.routes.models import FUNDAMENTAL_MODELS
    if request.model_id in FUNDAMENTAL_MODELS:
        fundamental_data = fetcher.get_bulk_fundamental_data(tickers)
    
    # Run model
    model_class = ALL_MODELS[request.model_id]
    params = request.parameters or {}
    model = model_class(**params)
    result = model.run(price_data, fundamental_data)
    signals = [s.to_dict() for s in result.signals]
    
    # Run walk-forward
    backtester = get_backtester()
    wf_result = backtester.walk_forward_analysis(
        price_data=price_data,
        signals=signals,
        in_sample_pct=request.in_sample_pct,
        n_splits=request.n_splits
    )
    
    return {
        "in_sample_results": wf_result.in_sample_results,
        "out_sample_results": wf_result.out_sample_results,
        "overall_performance": wf_result.overall_performance,
        "robustness_score": wf_result.robustness_score
    }


@router.post("/monte-carlo")
async def monte_carlo_simulation(request: MonteCarloRequest):
    """
    Run Monte Carlo simulation for risk analysis
    
    Simulates thousands of possible outcomes based on historical return
    distribution to estimate probability of various outcomes.
    """
    
    if request.model_id not in ALL_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model: {request.model_id}"
        )
    
    logger.info(f"Running Monte Carlo simulation for {request.model_id}")
    
    # Get tickers
    tickers = get_tickers(request.universe)
    if not tickers:
        raise HTTPException(status_code=400, detail=f"Unknown universe: {request.universe}")
    
    # Fetch data
    fetcher = get_fetcher()
    price_data = fetcher.get_bulk_price_data(tickers, period="2y")
    
    # Get fundamental data if needed
    fundamental_data = None
    from app.api.routes.models import FUNDAMENTAL_MODELS
    if request.model_id in FUNDAMENTAL_MODELS:
        fundamental_data = fetcher.get_bulk_fundamental_data(tickers)
    
    # Run model
    model_class = ALL_MODELS[request.model_id]
    params = request.parameters or {}
    model = model_class(**params)
    result = model.run(price_data, fundamental_data)
    signals = [s.to_dict() for s in result.signals]
    
    # Run Monte Carlo
    backtester = get_backtester()
    mc_result = backtester.monte_carlo_simulation(
        price_data=price_data,
        signals=signals,
        n_simulations=request.n_simulations,
        time_horizon=request.time_horizon
    )
    
    return {
        "simulations": mc_result.simulations,
        "confidence_intervals": mc_result.confidence_intervals,
        "var_95": mc_result.var_95,
        "cvar_95": mc_result.cvar_95,
        "probability_of_profit": mc_result.probability_of_profit,
        "expected_return": mc_result.expected_return,
        "return_distribution": mc_result.return_distribution
    }


@router.post("/tearsheet")
async def generate_tearsheet(request: BacktestRequest):
    """
    Generate QuantStats tearsheet data
    
    Returns comprehensive performance data for visualization including:
    - All performance metrics
    - Equity curve
    - Drawdown series
    - Monthly/yearly returns
    - Rolling metrics
    - Return distribution
    """
    
    if request.model_id not in ALL_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model: {request.model_id}"
        )
    
    logger.info(f"Generating tearsheet for {request.model_id}")
    
    # Get tickers
    tickers = get_tickers(request.universe)
    if not tickers:
        raise HTTPException(status_code=400, detail=f"Unknown universe: {request.universe}")
    
    # Fetch data
    fetcher = get_fetcher()
    price_data = fetcher.get_bulk_price_data(tickers, period="2y")
    
    # Get fundamental data if needed
    fundamental_data = None
    from app.api.routes.models import FUNDAMENTAL_MODELS
    if request.model_id in FUNDAMENTAL_MODELS:
        fundamental_data = fetcher.get_bulk_fundamental_data(tickers)
    
    # Run model
    model_class = ALL_MODELS[request.model_id]
    params = request.parameters or {}
    model = model_class(**params)
    result = model.run(price_data, fundamental_data)
    signals = [s.to_dict() for s in result.signals]
    
    # Generate tearsheet data
    reporter = get_reporter()
    tearsheet = reporter.generate_tearsheet_data(price_data, signals)
    
    return tearsheet.to_dict()


@router.post("/tearsheet/html", response_class=HTMLResponse)
async def generate_html_tearsheet(request: BacktestRequest):
    """
    Generate full HTML tearsheet report using QuantStats
    
    Returns a complete HTML page with interactive charts and metrics.
    """
    
    if request.model_id not in ALL_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model: {request.model_id}"
        )
    
    # Get tickers
    tickers = get_tickers(request.universe)
    if not tickers:
        raise HTTPException(status_code=400, detail=f"Unknown universe: {request.universe}")
    
    # Fetch data
    fetcher = get_fetcher()
    price_data = fetcher.get_bulk_price_data(tickers, period="2y")
    
    # Get fundamental data if needed
    fundamental_data = None
    from app.api.routes.models import FUNDAMENTAL_MODELS
    if request.model_id in FUNDAMENTAL_MODELS:
        fundamental_data = fetcher.get_bulk_fundamental_data(tickers)
    
    # Run model
    model_class = ALL_MODELS[request.model_id]
    params = request.parameters or {}
    model = model_class(**params)
    result = model.run(price_data, fundamental_data)
    signals = [s.to_dict() for s in result.signals]
    
    # Generate HTML report
    reporter = get_reporter()
    html = reporter.generate_html_report(price_data, signals, model.name)
    
    return HTMLResponse(content=html)


@router.post("/charts")
async def generate_charts(request: BacktestRequest):
    """
    Generate Plotly charts for backtest visualization
    
    Returns chart data in Plotly JSON format for frontend rendering.
    """
    
    if request.model_id not in ALL_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model: {request.model_id}"
        )
    
    # Get tickers
    tickers = get_tickers(request.universe)
    if not tickers:
        raise HTTPException(status_code=400, detail=f"Unknown universe: {request.universe}")
    
    # Fetch data
    fetcher = get_fetcher()
    price_data = fetcher.get_bulk_price_data(tickers, period="2y")
    
    # Get fundamental data if needed
    fundamental_data = None
    from app.api.routes.models import FUNDAMENTAL_MODELS
    if request.model_id in FUNDAMENTAL_MODELS:
        fundamental_data = fetcher.get_bulk_fundamental_data(tickers)
    
    # Run model
    model_class = ALL_MODELS[request.model_id]
    params = request.parameters or {}
    model = model_class(**params)
    result = model.run(price_data, fundamental_data)
    signals = [s.to_dict() for s in result.signals]
    
    # Generate tearsheet data and charts
    reporter = get_reporter()
    tearsheet = reporter.generate_tearsheet_data(price_data, signals)
    charts = reporter.generate_charts(tearsheet, model.name)
    
    return charts


@router.get("/capabilities")
async def get_capabilities():
    """
    Get available backtesting capabilities
    
    Returns information about what features are available based on
    installed packages (VectorBT, QuantStats, Plotly).
    """
    
    from app.services.vectorbt_backtest import VECTORBT_AVAILABLE
    from app.services.quantstats_report import QUANTSTATS_AVAILABLE, PLOTLY_AVAILABLE
    
    return {
        "vectorbt_available": VECTORBT_AVAILABLE,
        "quantstats_available": QUANTSTATS_AVAILABLE,
        "plotly_available": PLOTLY_AVAILABLE,
        "features": {
            "portfolio_backtest": True,
            "parameter_optimization": VECTORBT_AVAILABLE,
            "walk_forward_analysis": True,
            "monte_carlo_simulation": True,
            "tearsheet_reports": QUANTSTATS_AVAILABLE,
            "interactive_charts": PLOTLY_AVAILABLE
        },
        "position_sizing_options": ["equal", "score_weighted"],
        "optimization_metrics": ["sharpe_ratio", "total_return", "calmar_ratio", "sortino_ratio"]
    }
