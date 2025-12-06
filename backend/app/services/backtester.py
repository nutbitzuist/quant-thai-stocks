"""
Backtester Service
Simple backtesting for model signals
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


@dataclass
class BacktestResult:
    """Results from a backtest"""
    model_name: str
    universe: str
    start_date: str
    end_date: str
    initial_capital: float
    final_value: float
    total_return_pct: float
    annualized_return_pct: float
    max_drawdown_pct: float
    sharpe_ratio: float
    win_rate_pct: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win_pct: float
    avg_loss_pct: float
    profit_factor: float
    equity_curve: List[Dict]
    trades: List[Dict]


class SimpleBacktester:
    """
    Simple backtesting framework for model signals.
    
    Methodology:
    1. Get model signals at each rebalance period
    2. Buy top N signals, equal weight
    3. Hold for specified period
    4. Rebalance and repeat
    """
    
    def __init__(
        self,
        initial_capital: float = 100000,
        top_n: int = 10,
        holding_period: int = 21,  # Trading days
        transaction_cost: float = 0.001  # 0.1%
    ):
        self.initial_capital = initial_capital
        self.top_n = top_n
        self.holding_period = holding_period
        self.transaction_cost = transaction_cost
    
    def run_backtest(
        self,
        model_class,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None,
        lookback_months: int = 12
    ) -> BacktestResult:
        """
        Run backtest for a model.
        
        Note: This is a simplified backtest. For production use,
        consider using VectorBT for more sophisticated analysis.
        """
        # Get a sample DataFrame for dates
        sample_df = next(iter(price_data.values()))
        all_dates = sample_df['date'].tolist()
        
        # Determine test period
        total_days = len(all_dates)
        if total_days < self.holding_period * 3:
            raise ValueError("Insufficient data for backtest")
        
        # Initialize
        equity = self.initial_capital
        equity_curve = []
        trades = []
        positions = {}
        
        # Run through the backtest period
        rebalance_idx = self.holding_period * 2  # Start after enough history
        
        while rebalance_idx < total_days - self.holding_period:
            current_date = all_dates[rebalance_idx]
            next_date = all_dates[min(rebalance_idx + self.holding_period, total_days - 1)]
            
            # Get historical data up to current date
            historical_data = {}
            for ticker, df in price_data.items():
                mask = df['date'] <= current_date
                if mask.sum() >= 20:
                    historical_data[ticker] = df[mask].copy()
            
            if len(historical_data) < 10:
                rebalance_idx += self.holding_period
                continue
            
            # Run model on historical data
            try:
                model = model_class()
                result = model.run(historical_data, fundamental_data)
                buy_signals = result.get_buy_signals(self.top_n)
            except Exception as e:
                rebalance_idx += self.holding_period
                continue
            
            if not buy_signals:
                rebalance_idx += self.holding_period
                equity_curve.append({
                    "date": str(current_date),
                    "equity": equity
                })
                continue
            
            # Calculate returns for this period
            period_return = 0
            num_positions = len(buy_signals)
            position_size = equity / num_positions if num_positions > 0 else 0
            
            for signal in buy_signals:
                ticker = signal.ticker
                if ticker not in price_data:
                    continue
                
                df = price_data[ticker]
                
                # Find entry and exit prices
                entry_mask = df['date'] == current_date
                exit_mask = df['date'] == next_date
                
                if entry_mask.sum() == 0 or exit_mask.sum() == 0:
                    continue
                
                entry_price = df[entry_mask]['close'].iloc[0]
                exit_price = df[exit_mask]['close'].iloc[0]
                
                # Calculate return
                position_return = (exit_price / entry_price - 1)
                position_return -= self.transaction_cost * 2  # Buy and sell costs
                period_return += position_return / num_positions
                
                # Record trade
                trades.append({
                    "entry_date": str(current_date),
                    "exit_date": str(next_date),
                    "ticker": ticker,
                    "entry_price": round(entry_price, 2),
                    "exit_price": round(exit_price, 2),
                    "return_pct": round(position_return * 100, 2),
                    "pnl": round(position_size * position_return, 2)
                })
            
            # Update equity
            equity *= (1 + period_return)
            equity_curve.append({
                "date": str(current_date),
                "equity": round(equity, 2)
            })
            
            rebalance_idx += self.holding_period
        
        # Calculate statistics
        if not trades:
            return self._empty_result(model_class.__name__ if hasattr(model_class, '__name__') else "Model")
        
        returns = [t['return_pct'] for t in trades]
        winning = [r for r in returns if r > 0]
        losing = [r for r in returns if r <= 0]
        
        total_return = (equity / self.initial_capital - 1) * 100
        
        # Annualized return
        days_in_test = (len(equity_curve) * self.holding_period)
        years = days_in_test / 252
        annualized_return = ((equity / self.initial_capital) ** (1 / years) - 1) * 100 if years > 0 else 0
        
        # Max drawdown
        peak = self.initial_capital
        max_dd = 0
        for point in equity_curve:
            if point['equity'] > peak:
                peak = point['equity']
            dd = (peak - point['equity']) / peak * 100
            if dd > max_dd:
                max_dd = dd
        
        # Sharpe ratio (simplified)
        if len(returns) > 1:
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe = (avg_return / std_return * np.sqrt(252 / self.holding_period)) if std_return > 0 else 0
        else:
            sharpe = 0
        
        # Profit factor
        gross_profit = sum([r for r in returns if r > 0])
        gross_loss = abs(sum([r for r in returns if r < 0]))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        return BacktestResult(
            model_name=model_class.__name__ if hasattr(model_class, '__name__') else "Model",
            universe="backtest",
            start_date=str(all_dates[self.holding_period * 2]) if equity_curve else "",
            end_date=str(all_dates[-1]) if equity_curve else "",
            initial_capital=self.initial_capital,
            final_value=round(equity, 2),
            total_return_pct=round(total_return, 2),
            annualized_return_pct=round(annualized_return, 2),
            max_drawdown_pct=round(max_dd, 2),
            sharpe_ratio=round(sharpe, 2),
            win_rate_pct=round(len(winning) / len(trades) * 100, 1) if trades else 0,
            total_trades=len(trades),
            winning_trades=len(winning),
            losing_trades=len(losing),
            avg_win_pct=round(np.mean(winning), 2) if winning else 0,
            avg_loss_pct=round(np.mean(losing), 2) if losing else 0,
            profit_factor=round(profit_factor, 2),
            equity_curve=equity_curve,
            trades=trades  # All trades (no limit)
        )
    
    def _empty_result(self, model_name: str) -> BacktestResult:
        return BacktestResult(
            model_name=model_name,
            universe="backtest",
            start_date="",
            end_date="",
            initial_capital=self.initial_capital,
            final_value=self.initial_capital,
            total_return_pct=0,
            annualized_return_pct=0,
            max_drawdown_pct=0,
            sharpe_ratio=0,
            win_rate_pct=0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            avg_win_pct=0,
            avg_loss_pct=0,
            profit_factor=0,
            equity_curve=[],
            trades=[]
        )
    
    def to_dict(self, result: BacktestResult) -> Dict:
        """Convert BacktestResult to dictionary"""
        return {
            "model_name": result.model_name,
            "universe": result.universe,
            "period": f"{result.start_date} to {result.end_date}",
            "performance": {
                "initial_capital": result.initial_capital,
                "final_value": result.final_value,
                "total_return_pct": result.total_return_pct,
                "annualized_return_pct": result.annualized_return_pct,
                "max_drawdown_pct": result.max_drawdown_pct,
                "sharpe_ratio": result.sharpe_ratio
            },
            "trades": {
                "total": result.total_trades,
                "winning": result.winning_trades,
                "losing": result.losing_trades,
                "win_rate_pct": result.win_rate_pct,
                "avg_win_pct": result.avg_win_pct,
                "avg_loss_pct": result.avg_loss_pct,
                "profit_factor": result.profit_factor
            },
            "equity_curve": result.equity_curve,
            "recent_trades": result.trades
        }


# Singleton
_backtester = None

def get_backtester() -> SimpleBacktester:
    global _backtester
    if _backtester is None:
        _backtester = SimpleBacktester()
    return _backtester
