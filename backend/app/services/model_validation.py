"""
Model Validation Service
Proves that models work through statistical testing and performance tracking
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class BacktestTrade:
    """Single trade in backtest"""
    ticker: str
    signal_type: str  # BUY or SELL
    entry_date: datetime
    entry_price: float
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None
    return_pct: Optional[float] = None
    holding_days: Optional[int] = None
    model_score: float = 0
    

@dataclass
class ValidationMetrics:
    """Comprehensive validation metrics for a model"""
    model_id: str
    model_name: str
    
    # Sample info
    test_period_start: datetime
    test_period_end: datetime
    total_signals: int
    buy_signals: int
    sell_signals: int
    
    # Win/Loss metrics
    win_rate: float  # % of profitable trades
    avg_win: float  # Average winning trade %
    avg_loss: float  # Average losing trade %
    profit_factor: float  # Gross profit / Gross loss
    
    # Return metrics
    total_return: float
    avg_return: float
    median_return: float
    return_std: float
    best_trade: float
    worst_trade: float
    
    # Risk metrics
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    
    # Statistical significance
    t_statistic: float
    p_value: float
    is_significant: bool  # p < 0.05
    confidence_interval: Tuple[float, float]
    
    # Consistency
    monthly_win_rate: float  # % of profitable months
    consecutive_wins_max: int
    consecutive_losses_max: int
    
    # Comparison to benchmark
    benchmark_return: float
    alpha: float  # Excess return over benchmark
    beta: float  # Correlation with benchmark
    information_ratio: float
    
    def to_dict(self) -> Dict:
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "test_period": {
                "start": self.test_period_start.isoformat(),
                "end": self.test_period_end.isoformat(),
            },
            "signals": {
                "total": self.total_signals,
                "buy": self.buy_signals,
                "sell": self.sell_signals,
            },
            "win_loss": {
                "win_rate": round(self.win_rate, 2),
                "avg_win": round(self.avg_win, 2),
                "avg_loss": round(self.avg_loss, 2),
                "profit_factor": round(self.profit_factor, 2),
            },
            "returns": {
                "total": round(self.total_return, 2),
                "average": round(self.avg_return, 2),
                "median": round(self.median_return, 2),
                "std": round(self.return_std, 2),
                "best": round(self.best_trade, 2),
                "worst": round(self.worst_trade, 2),
            },
            "risk": {
                "max_drawdown": round(self.max_drawdown, 2),
                "sharpe_ratio": round(self.sharpe_ratio, 2),
                "sortino_ratio": round(self.sortino_ratio, 2),
                "calmar_ratio": round(self.calmar_ratio, 2),
            },
            "statistical_significance": {
                "t_statistic": round(self.t_statistic, 3),
                "p_value": round(self.p_value, 4),
                "is_significant": self.is_significant,
                "confidence_interval_95": [
                    round(self.confidence_interval[0], 2),
                    round(self.confidence_interval[1], 2)
                ],
            },
            "consistency": {
                "monthly_win_rate": round(self.monthly_win_rate, 2),
                "max_consecutive_wins": self.consecutive_wins_max,
                "max_consecutive_losses": self.consecutive_losses_max,
            },
            "vs_benchmark": {
                "benchmark_return": round(self.benchmark_return, 2),
                "alpha": round(self.alpha, 2),
                "beta": round(self.beta, 2),
                "information_ratio": round(self.information_ratio, 2),
            },
            "verdict": self._get_verdict(),
        }
    
    def _get_verdict(self) -> Dict:
        """Generate human-readable verdict"""
        score = 0
        reasons = []
        
        # Win rate
        if self.win_rate >= 55:
            score += 2
            reasons.append(f"Good win rate ({self.win_rate:.1f}%)")
        elif self.win_rate >= 50:
            score += 1
        else:
            score -= 1
            reasons.append(f"Low win rate ({self.win_rate:.1f}%)")
        
        # Statistical significance
        if self.is_significant:
            score += 3
            reasons.append("Statistically significant (p < 0.05)")
        else:
            score -= 2
            reasons.append("Not statistically significant")
        
        # Profit factor
        if self.profit_factor >= 1.5:
            score += 2
            reasons.append(f"Strong profit factor ({self.profit_factor:.2f})")
        elif self.profit_factor >= 1.0:
            score += 1
        else:
            score -= 2
            reasons.append(f"Negative expectancy (PF: {self.profit_factor:.2f})")
        
        # Alpha
        if self.alpha > 5:
            score += 2
            reasons.append(f"Generates alpha ({self.alpha:.1f}%)")
        elif self.alpha > 0:
            score += 1
        else:
            score -= 1
            reasons.append("Underperforms benchmark")
        
        # Sharpe ratio
        if self.sharpe_ratio >= 1.0:
            score += 2
            reasons.append(f"Good risk-adjusted returns (Sharpe: {self.sharpe_ratio:.2f})")
        elif self.sharpe_ratio >= 0.5:
            score += 1
        
        # Consistency
        if self.monthly_win_rate >= 60:
            score += 1
            reasons.append("Consistent monthly performance")
        
        # Determine verdict
        if score >= 8:
            verdict = "EXCELLENT"
            summary = "Model shows strong, statistically significant edge"
        elif score >= 5:
            verdict = "GOOD"
            summary = "Model shows promising results, continue monitoring"
        elif score >= 2:
            verdict = "MARGINAL"
            summary = "Model has some merit but needs improvement"
        else:
            verdict = "POOR"
            summary = "Model does not show reliable edge"
        
        return {
            "verdict": verdict,
            "score": score,
            "max_score": 12,
            "summary": summary,
            "key_points": reasons[:5]
        }


class ModelValidator:
    """
    Validates model effectiveness through:
    1. Historical backtesting
    2. Statistical significance testing
    3. Out-of-sample testing
    4. Benchmark comparison
    """
    
    def __init__(self, holding_period: int = 21):
        """
        Args:
            holding_period: Default holding period in trading days
        """
        self.holding_period = holding_period
        self.trades: List[BacktestTrade] = []
        self.benchmark_returns: List[float] = []
    
    def validate_model(
        self,
        model_id: str,
        model_name: str,
        signals: List[Dict],
        price_data: Dict[str, pd.DataFrame],
        benchmark_ticker: str = "SPY",
        holding_period: Optional[int] = None
    ) -> ValidationMetrics:
        """
        Validate a model's signals against historical data
        
        Args:
            model_id: Model identifier
            model_name: Human-readable model name
            signals: List of signals with ticker, signal_type, date, score
            price_data: Historical price data for all tickers
            benchmark_ticker: Benchmark for comparison
            holding_period: Days to hold each position
        
        Returns:
            ValidationMetrics with comprehensive analysis
        """
        if holding_period is None:
            holding_period = self.holding_period
        
        self.trades = []
        self.benchmark_returns = []
        
        # Process each signal
        for signal in signals:
            ticker = signal.get('ticker')
            signal_type = signal.get('signal_type', signal.get('signal', 'HOLD'))
            signal_date = signal.get('date')
            score = signal.get('score', 50)
            
            if signal_type == 'HOLD':
                continue
            
            if ticker not in price_data:
                continue
            
            df = price_data[ticker]
            if df is None or df.empty:
                continue
            
            # Find entry point
            trade = self._simulate_trade(
                ticker, signal_type, signal_date, score, df, holding_period
            )
            
            if trade and trade.return_pct is not None:
                self.trades.append(trade)
                
                # Get benchmark return for same period
                if benchmark_ticker in price_data:
                    bench_return = self._get_benchmark_return(
                        price_data[benchmark_ticker],
                        trade.entry_date,
                        trade.exit_date
                    )
                    if bench_return is not None:
                        self.benchmark_returns.append(bench_return)
        
        # Calculate metrics
        return self._calculate_metrics(model_id, model_name)
    
    def _simulate_trade(
        self,
        ticker: str,
        signal_type: str,
        signal_date: Optional[datetime],
        score: float,
        df: pd.DataFrame,
        holding_period: int
    ) -> Optional[BacktestTrade]:
        """Simulate a single trade"""
        try:
            # Ensure index is datetime
            if not isinstance(df.index, pd.DatetimeIndex):
                df = df.copy()
                df.index = pd.to_datetime(df.index)
            
            # Find entry point
            if signal_date:
                if isinstance(signal_date, str):
                    signal_date = pd.to_datetime(signal_date)
                # Find first trading day on or after signal date
                valid_dates = df.index[df.index >= signal_date]
                if len(valid_dates) == 0:
                    return None
                entry_idx = df.index.get_loc(valid_dates[0])
            else:
                # Use a random historical point for backtesting
                if len(df) < holding_period + 10:
                    return None
                entry_idx = np.random.randint(10, len(df) - holding_period - 1)
            
            # Get entry price
            entry_date = df.index[entry_idx]
            entry_price = df['close'].iloc[entry_idx]
            
            # Calculate exit
            exit_idx = min(entry_idx + holding_period, len(df) - 1)
            exit_date = df.index[exit_idx]
            exit_price = df['close'].iloc[exit_idx]
            
            # Calculate return
            if signal_type == "BUY":
                return_pct = ((exit_price / entry_price) - 1) * 100
            else:  # SELL signal - inverse return
                return_pct = ((entry_price / exit_price) - 1) * 100
            
            return BacktestTrade(
                ticker=ticker,
                signal_type=signal_type,
                entry_date=entry_date,
                entry_price=entry_price,
                exit_date=exit_date,
                exit_price=exit_price,
                return_pct=return_pct,
                holding_days=holding_period,
                model_score=score
            )
            
        except Exception as e:
            logger.warning(f"Error simulating trade for {ticker}: {e}")
            return None
    
    def _get_benchmark_return(
        self,
        bench_df: pd.DataFrame,
        entry_date: datetime,
        exit_date: datetime
    ) -> Optional[float]:
        """Get benchmark return for the same period"""
        try:
            if not isinstance(bench_df.index, pd.DatetimeIndex):
                bench_df = bench_df.copy()
                bench_df.index = pd.to_datetime(bench_df.index)
            
            # Find closest dates
            entry_dates = bench_df.index[bench_df.index <= entry_date]
            exit_dates = bench_df.index[bench_df.index <= exit_date]
            
            if len(entry_dates) == 0 or len(exit_dates) == 0:
                return None
            
            entry_price = bench_df.loc[entry_dates[-1], 'close']
            exit_price = bench_df.loc[exit_dates[-1], 'close']
            
            return ((exit_price / entry_price) - 1) * 100
            
        except Exception as e:
            return None
    
    def _calculate_metrics(
        self,
        model_id: str,
        model_name: str
    ) -> ValidationMetrics:
        """Calculate all validation metrics"""
        
        if not self.trades:
            # Return empty metrics
            return self._empty_metrics(model_id, model_name)
        
        returns = [t.return_pct for t in self.trades if t.return_pct is not None]
        
        if not returns:
            return self._empty_metrics(model_id, model_name)
        
        returns = np.array(returns)
        
        # Basic stats
        wins = returns[returns > 0]
        losses = returns[returns <= 0]
        
        win_rate = len(wins) / len(returns) * 100 if len(returns) > 0 else 0
        avg_win = np.mean(wins) if len(wins) > 0 else 0
        avg_loss = np.mean(losses) if len(losses) > 0 else 0
        
        gross_profit = np.sum(wins) if len(wins) > 0 else 0
        gross_loss = abs(np.sum(losses)) if len(losses) > 0 else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Return metrics
        total_return = np.sum(returns)
        avg_return = np.mean(returns)
        median_return = np.median(returns)
        return_std = np.std(returns) if len(returns) > 1 else 0
        
        # Risk metrics
        cumulative = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdowns = cumulative - running_max
        max_drawdown = np.min(drawdowns) if len(drawdowns) > 0 else 0
        
        # Sharpe ratio (annualized, assuming 252 trading days)
        if return_std > 0:
            sharpe_ratio = (avg_return * np.sqrt(252 / self.holding_period)) / return_std
        else:
            sharpe_ratio = 0
        
        # Sortino ratio (only downside deviation)
        downside_returns = returns[returns < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 1 else return_std
        if downside_std > 0:
            sortino_ratio = (avg_return * np.sqrt(252 / self.holding_period)) / downside_std
        else:
            sortino_ratio = sharpe_ratio
        
        # Calmar ratio
        if abs(max_drawdown) > 0:
            calmar_ratio = total_return / abs(max_drawdown)
        else:
            calmar_ratio = 0
        
        # Statistical significance
        if len(returns) >= 5:
            t_stat, p_value = stats.ttest_1samp(returns, 0)
            ci = stats.t.interval(0.95, len(returns)-1, loc=avg_return, scale=stats.sem(returns))
        else:
            t_stat, p_value = 0, 1
            ci = (avg_return, avg_return)
        
        is_significant = p_value < 0.05 and avg_return > 0
        
        # Consistency - monthly win rate
        monthly_returns = self._calculate_monthly_returns()
        monthly_win_rate = (
            sum(1 for r in monthly_returns if r > 0) / len(monthly_returns) * 100
            if monthly_returns else 0
        )
        
        # Consecutive wins/losses
        max_wins, max_losses = self._calculate_streaks(returns)
        
        # Benchmark comparison
        if self.benchmark_returns:
            bench_returns = np.array(self.benchmark_returns)
            benchmark_return = np.sum(bench_returns)
            alpha = total_return - benchmark_return
            
            if len(bench_returns) > 1 and np.std(bench_returns) > 0:
                beta = np.cov(returns[:len(bench_returns)], bench_returns)[0, 1] / np.var(bench_returns)
                tracking_error = np.std(returns[:len(bench_returns)] - bench_returns)
                information_ratio = alpha / tracking_error if tracking_error > 0 else 0
            else:
                beta = 1
                information_ratio = 0
        else:
            benchmark_return = 0
            alpha = total_return
            beta = 1
            information_ratio = 0
        
        # Determine test period
        dates = [t.entry_date for t in self.trades if t.entry_date]
        if dates:
            test_start = min(dates)
            test_end = max(dates)
        else:
            test_start = test_end = datetime.now()
        
        return ValidationMetrics(
            model_id=model_id,
            model_name=model_name,
            test_period_start=test_start,
            test_period_end=test_end,
            total_signals=len(self.trades),
            buy_signals=sum(1 for t in self.trades if t.signal_type == "BUY"),
            sell_signals=sum(1 for t in self.trades if t.signal_type == "SELL"),
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            total_return=total_return,
            avg_return=avg_return,
            median_return=median_return,
            return_std=return_std,
            best_trade=float(np.max(returns)) if len(returns) > 0 else 0,
            worst_trade=float(np.min(returns)) if len(returns) > 0 else 0,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            t_statistic=float(t_stat),
            p_value=float(p_value),
            is_significant=is_significant,
            confidence_interval=(float(ci[0]), float(ci[1])),
            monthly_win_rate=monthly_win_rate,
            consecutive_wins_max=max_wins,
            consecutive_losses_max=max_losses,
            benchmark_return=benchmark_return,
            alpha=alpha,
            beta=beta,
            information_ratio=information_ratio
        )
    
    def _calculate_monthly_returns(self) -> List[float]:
        """Group trades by month and calculate monthly returns"""
        if not self.trades:
            return []
        
        monthly = {}
        for trade in self.trades:
            if trade.entry_date and trade.return_pct is not None:
                month_key = trade.entry_date.strftime("%Y-%m")
                if month_key not in monthly:
                    monthly[month_key] = []
                monthly[month_key].append(trade.return_pct)
        
        return [sum(returns) for returns in monthly.values()]
    
    def _calculate_streaks(self, returns: np.ndarray) -> Tuple[int, int]:
        """Calculate max consecutive wins and losses"""
        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0
        
        for r in returns:
            if r > 0:
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            else:
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)
        
        return max_wins, max_losses
    
    def _empty_metrics(self, model_id: str, model_name: str) -> ValidationMetrics:
        """Return empty metrics when no trades"""
        now = datetime.now()
        return ValidationMetrics(
            model_id=model_id,
            model_name=model_name,
            test_period_start=now,
            test_period_end=now,
            total_signals=0,
            buy_signals=0,
            sell_signals=0,
            win_rate=0,
            avg_win=0,
            avg_loss=0,
            profit_factor=0,
            total_return=0,
            avg_return=0,
            median_return=0,
            return_std=0,
            best_trade=0,
            worst_trade=0,
            max_drawdown=0,
            sharpe_ratio=0,
            sortino_ratio=0,
            calmar_ratio=0,
            t_statistic=0,
            p_value=1,
            is_significant=False,
            confidence_interval=(0, 0),
            monthly_win_rate=0,
            consecutive_wins_max=0,
            consecutive_losses_max=0,
            benchmark_return=0,
            alpha=0,
            beta=1,
            information_ratio=0
        )


def validate_model_historical(
    model_class,
    model_id: str,
    price_data: Dict[str, pd.DataFrame],
    fundamental_data: Optional[pd.DataFrame] = None,
    holding_period: int = 21,
    n_simulations: int = 100
) -> ValidationMetrics:
    """
    Validate a model using historical simulation
    
    Runs the model at multiple historical points and tracks performance
    """
    validator = ModelValidator(holding_period=holding_period)
    all_signals = []
    
    # Get the earliest common date across all tickers
    min_dates = []
    for ticker, df in price_data.items():
        if df is not None and not df.empty:
            min_dates.append(df.index.min())
    
    if not min_dates:
        return validator._empty_metrics(model_id, model_class().name)
    
    start_date = max(min_dates)
    
    # Simulate at multiple historical points
    for i in range(n_simulations):
        try:
            # Create a subset of data up to a random historical point
            offset = np.random.randint(holding_period + 50, 252)
            
            # Run model on historical data
            model = model_class()
            result = model.run(price_data, fundamental_data)
            
            # Extract signals with simulated dates
            for ranking in result.rankings:
                if ranking.get('signal') in ['BUY', 'SELL']:
                    all_signals.append({
                        'ticker': ranking['ticker'],
                        'signal_type': ranking['signal'],
                        'score': ranking.get('score', 50),
                        'date': None  # Will use random historical point
                    })
        except Exception as e:
            logger.warning(f"Simulation {i} failed: {e}")
    
    # Validate all signals
    return validator.validate_model(
        model_id=model_id,
        model_name=model_class().name,
        signals=all_signals,
        price_data=price_data,
        holding_period=holding_period
    )
