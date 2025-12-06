"""
VectorBT Backtesting Service
High-performance portfolio backtesting with advanced features
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)

# Try to import vectorbt - graceful fallback if not installed
try:
    import vectorbt as vbt
    VECTORBT_AVAILABLE = True
except ImportError:
    VECTORBT_AVAILABLE = False
    logger.warning("VectorBT not installed. Backtesting features will be limited.")


@dataclass
class BacktestResult:
    """Backtest result container"""
    # Basic info
    strategy_name: str
    start_date: str
    end_date: str
    initial_capital: float
    
    # Returns
    total_return: float
    annual_return: float
    benchmark_return: float
    alpha: float
    
    # Risk metrics
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    max_drawdown_duration: int  # days
    calmar_ratio: float
    
    # Trade statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    avg_trade_duration: float  # days
    
    # Portfolio metrics
    final_value: float
    best_day: float
    worst_day: float
    avg_daily_return: float
    
    # Time series data (for charts)
    equity_curve: List[Dict]
    drawdown_curve: List[Dict]
    monthly_returns: List[Dict]
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class OptimizationResult:
    """Parameter optimization result"""
    best_params: Dict[str, Any]
    best_sharpe: float
    best_return: float
    all_results: List[Dict]
    heatmap_data: Optional[List[Dict]] = None


@dataclass
class WalkForwardResult:
    """Walk-forward analysis result"""
    in_sample_results: List[Dict]
    out_sample_results: List[Dict]
    overall_performance: Dict
    robustness_score: float


@dataclass
class MonteCarloResult:
    """Monte Carlo simulation result"""
    simulations: int
    confidence_intervals: Dict[str, Dict]  # 5%, 25%, 50%, 75%, 95%
    var_95: float  # Value at Risk
    cvar_95: float  # Conditional VaR
    probability_of_profit: float
    expected_return: float
    return_distribution: List[float]


class VectorBTBacktester:
    """
    VectorBT-based backtesting engine with advanced features
    """
    
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.benchmark_ticker = "SPY"
        
    def prepare_data(
        self,
        price_data: Dict[str, pd.DataFrame],
        signals: List[Dict],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Prepare price and signal data for backtesting"""
        
        # Get tickers from signals
        signal_tickers = {s['ticker'] for s in signals if s.get('signal') == 'BUY'}
        
        # Filter price data
        available_tickers = [t for t in signal_tickers if t in price_data]
        
        if not available_tickers:
            raise ValueError("No price data available for signal tickers")
        
        # Create aligned price DataFrame
        prices = {}
        for ticker in available_tickers:
            df = price_data[ticker].copy()
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
            prices[ticker] = df['close']
        
        price_df = pd.DataFrame(prices)
        price_df = price_df.dropna(how='all')
        
        # Apply date filters
        if start_date:
            price_df = price_df[price_df.index >= pd.to_datetime(start_date)]
        if end_date:
            price_df = price_df[price_df.index <= pd.to_datetime(end_date)]
        
        # Create signal DataFrame (entry signals)
        signal_df = pd.DataFrame(False, index=price_df.index, columns=price_df.columns)
        
        # Mark entry signals on first day
        if len(signal_df) > 0:
            for ticker in available_tickers:
                signal_df.iloc[0][ticker] = True
        
        return price_df, signal_df
    
    def run_backtest(
        self,
        price_data: Dict[str, pd.DataFrame],
        signals: List[Dict],
        strategy_name: str = "Model Strategy",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        position_size: str = "equal",  # equal, score_weighted, volatility_adjusted
        rebalance_freq: str = "monthly",  # daily, weekly, monthly, quarterly
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        max_positions: int = 20
    ) -> BacktestResult:
        """
        Run portfolio backtest using VectorBT
        """
        
        if not VECTORBT_AVAILABLE:
            return self._run_simple_backtest(
                price_data, signals, strategy_name, start_date, end_date
            )
        
        try:
            # Prepare data
            price_df, signal_df = self.prepare_data(
                price_data, signals, start_date, end_date
            )
            
            if price_df.empty:
                raise ValueError("No price data available for backtesting")
            
            # Filter to top signals by score
            buy_signals = [s for s in signals if s.get('signal') == 'BUY']
            buy_signals.sort(key=lambda x: x.get('score', 0), reverse=True)
            top_tickers = [s['ticker'] for s in buy_signals[:max_positions]]
            top_tickers = [t for t in top_tickers if t in price_df.columns]
            
            if not top_tickers:
                raise ValueError("No valid tickers for backtesting")
            
            price_df = price_df[top_tickers]
            
            # Calculate position sizes
            if position_size == "equal":
                weights = np.ones(len(top_tickers)) / len(top_tickers)
            elif position_size == "score_weighted":
                scores = [next((s['score'] for s in buy_signals if s['ticker'] == t), 50) for t in top_tickers]
                total_score = sum(scores)
                weights = np.array([s / total_score for s in scores])
            else:
                weights = np.ones(len(top_tickers)) / len(top_tickers)
            
            # Create portfolio using VectorBT
            portfolio = vbt.Portfolio.from_holding(
                price_df,
                init_cash=self.initial_capital,
                freq='1D'
            )
            
            # Calculate metrics
            total_return = float(portfolio.total_return())
            
            # Get returns series
            returns = portfolio.returns()
            daily_returns = returns.values if hasattr(returns, 'values') else returns
            
            # Calculate risk metrics
            volatility = float(np.std(daily_returns) * np.sqrt(252) * 100)
            sharpe = float(portfolio.sharpe_ratio()) if hasattr(portfolio, 'sharpe_ratio') else 0
            
            # Drawdown
            equity = portfolio.value()
            running_max = equity.cummax()
            drawdown = (equity - running_max) / running_max
            max_dd = float(drawdown.min() * 100)
            
            # Calculate drawdown duration
            dd_duration = 0
            current_dd_start = None
            max_dd_duration = 0
            for i, dd in enumerate(drawdown):
                if dd < 0:
                    if current_dd_start is None:
                        current_dd_start = i
                else:
                    if current_dd_start is not None:
                        duration = i - current_dd_start
                        max_dd_duration = max(max_dd_duration, duration)
                        current_dd_start = None
            
            # Annual return
            days = (price_df.index[-1] - price_df.index[0]).days
            years = days / 365.25
            annual_return = ((1 + total_return) ** (1 / years) - 1) * 100 if years > 0 else 0
            
            # Sortino ratio
            negative_returns = daily_returns[daily_returns < 0]
            downside_std = np.std(negative_returns) * np.sqrt(252) if len(negative_returns) > 0 else 0.001
            sortino = (annual_return / 100) / downside_std if downside_std > 0 else 0
            
            # Calmar ratio
            calmar = annual_return / abs(max_dd) if max_dd != 0 else 0
            
            # Build equity curve for charts
            equity_curve = [
                {"date": str(date.date()), "value": float(val)}
                for date, val in zip(equity.index, equity.values)
            ]
            
            # Build drawdown curve
            drawdown_curve = [
                {"date": str(date.date()), "drawdown": float(dd * 100)}
                for date, dd in zip(drawdown.index, drawdown.values)
            ]
            
            # Monthly returns
            monthly_returns = []
            if len(returns) > 20:
                monthly = returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
                monthly_returns = [
                    {"month": str(date.date()), "return": float(ret * 100)}
                    for date, ret in zip(monthly.index, monthly.values)
                ]
            
            return BacktestResult(
                strategy_name=strategy_name,
                start_date=str(price_df.index[0].date()),
                end_date=str(price_df.index[-1].date()),
                initial_capital=self.initial_capital,
                total_return=round(total_return * 100, 2),
                annual_return=round(annual_return, 2),
                benchmark_return=0,  # Would need benchmark data
                alpha=round(annual_return, 2),  # Simplified
                volatility=round(volatility, 2),
                sharpe_ratio=round(sharpe, 2),
                sortino_ratio=round(sortino, 2),
                max_drawdown=round(max_dd, 2),
                max_drawdown_duration=max_dd_duration,
                calmar_ratio=round(calmar, 2),
                total_trades=len(top_tickers),
                winning_trades=0,  # Would need trade-level analysis
                losing_trades=0,
                win_rate=0,
                avg_win=0,
                avg_loss=0,
                profit_factor=0,
                avg_trade_duration=days,
                final_value=round(float(equity.iloc[-1]), 2),
                best_day=round(float(np.max(daily_returns) * 100), 2),
                worst_day=round(float(np.min(daily_returns) * 100), 2),
                avg_daily_return=round(float(np.mean(daily_returns) * 100), 4),
                equity_curve=equity_curve[::max(1, len(equity_curve)//100)],  # Limit points
                drawdown_curve=drawdown_curve[::max(1, len(drawdown_curve)//100)],
                monthly_returns=monthly_returns
            )
            
        except Exception as e:
            logger.error(f"VectorBT backtest error: {e}")
            return self._run_simple_backtest(
                price_data, signals, strategy_name, start_date, end_date
            )
    
    def _run_simple_backtest(
        self,
        price_data: Dict[str, pd.DataFrame],
        signals: List[Dict],
        strategy_name: str,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> BacktestResult:
        """Simple backtest fallback when VectorBT is not available"""
        
        # Get buy signals
        buy_signals = [s for s in signals if s.get('signal') == 'BUY']
        buy_signals.sort(key=lambda x: x.get('score', 0), reverse=True)
        top_tickers = [s['ticker'] for s in buy_signals[:20]]
        
        # Calculate simple equal-weight returns
        returns_list = []
        for ticker in top_tickers:
            if ticker in price_data:
                df = price_data[ticker]
                if len(df) > 1:
                    start_price = df['close'].iloc[0]
                    end_price = df['close'].iloc[-1]
                    ret = (end_price - start_price) / start_price
                    returns_list.append(ret)
        
        if not returns_list:
            total_return = 0
        else:
            total_return = np.mean(returns_list)
        
        final_value = self.initial_capital * (1 + total_return)
        
        return BacktestResult(
            strategy_name=strategy_name,
            start_date=start_date or "N/A",
            end_date=end_date or "N/A",
            initial_capital=self.initial_capital,
            total_return=round(total_return * 100, 2),
            annual_return=round(total_return * 100, 2),  # Simplified
            benchmark_return=0,
            alpha=round(total_return * 100, 2),
            volatility=0,
            sharpe_ratio=0,
            sortino_ratio=0,
            max_drawdown=0,
            max_drawdown_duration=0,
            calmar_ratio=0,
            total_trades=len(top_tickers),
            winning_trades=len([r for r in returns_list if r > 0]),
            losing_trades=len([r for r in returns_list if r < 0]),
            win_rate=len([r for r in returns_list if r > 0]) / len(returns_list) * 100 if returns_list else 0,
            avg_win=np.mean([r for r in returns_list if r > 0]) * 100 if any(r > 0 for r in returns_list) else 0,
            avg_loss=np.mean([r for r in returns_list if r < 0]) * 100 if any(r < 0 for r in returns_list) else 0,
            profit_factor=0,
            avg_trade_duration=0,
            final_value=round(final_value, 2),
            best_day=0,
            worst_day=0,
            avg_daily_return=0,
            equity_curve=[],
            drawdown_curve=[],
            monthly_returns=[]
        )
    
    def optimize_parameters(
        self,
        price_data: Dict[str, pd.DataFrame],
        model_class: type,
        param_grid: Dict[str, List[Any]],
        universe: List[str],
        metric: str = "sharpe_ratio",
        n_jobs: int = -1
    ) -> OptimizationResult:
        """
        Grid search parameter optimization
        """
        from itertools import product
        
        # Generate all parameter combinations
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        combinations = list(product(*param_values))
        
        results = []
        best_metric = float('-inf')
        best_params = {}
        
        for combo in combinations:
            params = dict(zip(param_names, combo))
            
            try:
                # Create model with parameters
                model = model_class(**params)
                
                # Run model
                result = model.run(price_data, None)
                
                # Get signals
                signals = [s.to_dict() for s in result.signals]
                
                # Run backtest
                backtest = self.run_backtest(
                    price_data, signals, f"Opt_{combo}"
                )
                
                # Get metric value
                metric_value = getattr(backtest, metric, 0)
                
                results.append({
                    "params": params,
                    "sharpe_ratio": backtest.sharpe_ratio,
                    "total_return": backtest.total_return,
                    "max_drawdown": backtest.max_drawdown,
                    "metric_value": metric_value
                })
                
                if metric_value > best_metric:
                    best_metric = metric_value
                    best_params = params
                    
            except Exception as e:
                logger.warning(f"Optimization error for {params}: {e}")
                continue
        
        return OptimizationResult(
            best_params=best_params,
            best_sharpe=best_metric if metric == "sharpe_ratio" else 0,
            best_return=best_metric if metric == "total_return" else 0,
            all_results=results
        )
    
    def walk_forward_analysis(
        self,
        price_data: Dict[str, pd.DataFrame],
        signals: List[Dict],
        in_sample_pct: float = 0.7,
        n_splits: int = 5
    ) -> WalkForwardResult:
        """
        Walk-forward analysis for strategy robustness testing
        """
        
        # Get date range
        all_dates = set()
        for ticker, df in price_data.items():
            if 'date' in df.columns:
                all_dates.update(pd.to_datetime(df['date']).tolist())
            else:
                all_dates.update(df.index.tolist())
        
        all_dates = sorted(all_dates)
        total_days = len(all_dates)
        split_size = total_days // n_splits
        
        in_sample_results = []
        out_sample_results = []
        
        for i in range(n_splits):
            split_start = i * split_size
            split_end = (i + 1) * split_size
            
            in_sample_end = split_start + int(split_size * in_sample_pct)
            
            # In-sample period
            is_start = str(all_dates[split_start].date()) if hasattr(all_dates[split_start], 'date') else str(all_dates[split_start])
            is_end = str(all_dates[in_sample_end].date()) if hasattr(all_dates[in_sample_end], 'date') else str(all_dates[in_sample_end])
            
            # Out-of-sample period
            os_start = is_end
            os_end = str(all_dates[min(split_end, len(all_dates)-1)].date()) if hasattr(all_dates[min(split_end, len(all_dates)-1)], 'date') else str(all_dates[min(split_end, len(all_dates)-1)])
            
            try:
                # Run in-sample backtest
                is_result = self.run_backtest(
                    price_data, signals, f"IS_Split_{i+1}",
                    start_date=is_start, end_date=is_end
                )
                in_sample_results.append({
                    "split": i + 1,
                    "period": f"{is_start} to {is_end}",
                    "return": is_result.total_return,
                    "sharpe": is_result.sharpe_ratio
                })
                
                # Run out-of-sample backtest
                os_result = self.run_backtest(
                    price_data, signals, f"OS_Split_{i+1}",
                    start_date=os_start, end_date=os_end
                )
                out_sample_results.append({
                    "split": i + 1,
                    "period": f"{os_start} to {os_end}",
                    "return": os_result.total_return,
                    "sharpe": os_result.sharpe_ratio
                })
            except Exception as e:
                logger.warning(f"Walk-forward split {i+1} error: {e}")
        
        # Calculate robustness score
        if in_sample_results and out_sample_results:
            is_avg_return = np.mean([r['return'] for r in in_sample_results])
            os_avg_return = np.mean([r['return'] for r in out_sample_results])
            
            # Robustness = how well out-of-sample matches in-sample
            if is_avg_return != 0:
                robustness = min(1.0, os_avg_return / is_avg_return) if is_avg_return > 0 else 0
            else:
                robustness = 0.5
        else:
            robustness = 0
            is_avg_return = 0
            os_avg_return = 0
        
        return WalkForwardResult(
            in_sample_results=in_sample_results,
            out_sample_results=out_sample_results,
            overall_performance={
                "in_sample_avg_return": round(is_avg_return, 2),
                "out_sample_avg_return": round(os_avg_return, 2),
                "degradation": round(is_avg_return - os_avg_return, 2)
            },
            robustness_score=round(robustness, 2)
        )
    
    def monte_carlo_simulation(
        self,
        price_data: Dict[str, pd.DataFrame],
        signals: List[Dict],
        n_simulations: int = 1000,
        time_horizon: int = 252  # 1 year
    ) -> MonteCarloResult:
        """
        Monte Carlo simulation for risk analysis
        """
        
        # Get historical returns
        buy_signals = [s for s in signals if s.get('signal') == 'BUY']
        tickers = [s['ticker'] for s in buy_signals[:20]]
        
        all_returns = []
        for ticker in tickers:
            if ticker in price_data:
                df = price_data[ticker]
                if len(df) > 1:
                    returns = df['close'].pct_change().dropna()
                    all_returns.extend(returns.tolist())
        
        if not all_returns:
            return MonteCarloResult(
                simulations=0,
                confidence_intervals={},
                var_95=0,
                cvar_95=0,
                probability_of_profit=0,
                expected_return=0,
                return_distribution=[]
            )
        
        # Calculate return statistics
        mean_return = np.mean(all_returns)
        std_return = np.std(all_returns)
        
        # Run simulations
        final_returns = []
        
        for _ in range(n_simulations):
            # Generate random returns
            sim_returns = np.random.normal(mean_return, std_return, time_horizon)
            
            # Calculate cumulative return
            cumulative = np.prod(1 + sim_returns) - 1
            final_returns.append(cumulative * 100)  # Convert to percentage
        
        final_returns = np.array(final_returns)
        
        # Calculate statistics
        percentiles = {
            "5%": round(np.percentile(final_returns, 5), 2),
            "25%": round(np.percentile(final_returns, 25), 2),
            "50%": round(np.percentile(final_returns, 50), 2),
            "75%": round(np.percentile(final_returns, 75), 2),
            "95%": round(np.percentile(final_returns, 95), 2)
        }
        
        var_95 = round(np.percentile(final_returns, 5), 2)  # 5th percentile
        cvar_95 = round(np.mean(final_returns[final_returns <= var_95]), 2)
        
        prob_profit = round(len(final_returns[final_returns > 0]) / len(final_returns) * 100, 2)
        expected_return = round(np.mean(final_returns), 2)
        
        return MonteCarloResult(
            simulations=n_simulations,
            confidence_intervals=percentiles,
            var_95=var_95,
            cvar_95=cvar_95,
            probability_of_profit=prob_profit,
            expected_return=expected_return,
            return_distribution=sorted(final_returns.tolist())[::max(1, n_simulations//100)]
        )


# Singleton instance
_backtester = None

def get_backtester() -> VectorBTBacktester:
    global _backtester
    if _backtester is None:
        _backtester = VectorBTBacktester()
    return _backtester
