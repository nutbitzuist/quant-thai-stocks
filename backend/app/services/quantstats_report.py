"""
QuantStats Reporting Service
Generate beautiful performance reports and tearsheets
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import io
import base64

logger = logging.getLogger(__name__)

# Try to import quantstats - graceful fallback if not installed
try:
    import quantstats as qs
    QUANTSTATS_AVAILABLE = True
except ImportError:
    QUANTSTATS_AVAILABLE = False
    logger.warning("QuantStats not installed. Report features will be limited.")

# Try to import plotly for charts
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    logger.warning("Plotly not installed. Chart features will be limited.")


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics"""
    # Returns
    total_return: float
    cagr: float
    mtd: float
    ytd: float
    
    # Risk
    volatility: float
    sharpe: float
    sortino: float
    calmar: float
    
    # Drawdown
    max_drawdown: float
    avg_drawdown: float
    max_drawdown_duration: int
    
    # Win/Loss
    win_rate: float
    best_day: float
    worst_day: float
    best_month: float
    worst_month: float
    
    # Ratios
    profit_factor: float
    payoff_ratio: float
    
    # Risk-adjusted
    var_95: float
    cvar_95: float
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TearsheetData:
    """Data for generating tearsheet"""
    metrics: PerformanceMetrics
    equity_curve: List[Dict]
    drawdown_series: List[Dict]
    monthly_returns: List[Dict]
    yearly_returns: List[Dict]
    rolling_sharpe: List[Dict]
    rolling_volatility: List[Dict]
    return_distribution: List[Dict]
    
    def to_dict(self) -> dict:
        return {
            "metrics": self.metrics.to_dict(),
            "equity_curve": self.equity_curve,
            "drawdown_series": self.drawdown_series,
            "monthly_returns": self.monthly_returns,
            "yearly_returns": self.yearly_returns,
            "rolling_sharpe": self.rolling_sharpe,
            "rolling_volatility": self.rolling_volatility,
            "return_distribution": self.return_distribution
        }


class QuantStatsReporter:
    """
    QuantStats-based performance reporting
    """
    
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
    
    def calculate_returns(
        self,
        price_data: Dict[str, pd.DataFrame],
        signals: List[Dict],
        weights: Optional[Dict[str, float]] = None
    ) -> pd.Series:
        """Calculate portfolio returns from signals"""
        
        # Get buy signals
        buy_signals = [s for s in signals if s.get('signal') == 'BUY']
        tickers = [s['ticker'] for s in buy_signals[:20]]
        
        # Calculate weights
        if weights is None:
            weights = {t: 1.0 / len(tickers) for t in tickers}
        
        # Get aligned returns
        returns_dict = {}
        for ticker in tickers:
            if ticker in price_data:
                df = price_data[ticker].copy()
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)
                returns_dict[ticker] = df['close'].pct_change()
        
        if not returns_dict:
            return pd.Series(dtype=float)
        
        # Create returns DataFrame
        returns_df = pd.DataFrame(returns_dict)
        returns_df = returns_df.dropna(how='all')
        
        # Calculate weighted portfolio returns
        portfolio_returns = pd.Series(0.0, index=returns_df.index)
        for ticker in returns_df.columns:
            weight = weights.get(ticker, 1.0 / len(returns_df.columns))
            portfolio_returns += returns_df[ticker].fillna(0) * weight
        
        return portfolio_returns.dropna()
    
    def generate_metrics(self, returns: pd.Series) -> PerformanceMetrics:
        """Generate comprehensive performance metrics"""
        
        if returns.empty or len(returns) < 2:
            return self._empty_metrics()
        
        if QUANTSTATS_AVAILABLE:
            try:
                return self._quantstats_metrics(returns)
            except Exception as e:
                logger.warning(f"QuantStats metrics error: {e}")
        
        return self._manual_metrics(returns)
    
    def _quantstats_metrics(self, returns: pd.Series) -> PerformanceMetrics:
        """Calculate metrics using QuantStats"""
        
        # Extend pandas with quantstats
        qs.extend_pandas()
        
        # Basic returns
        total_return = float(qs.stats.comp(returns) * 100)
        cagr = float(qs.stats.cagr(returns) * 100) if len(returns) > 252 else total_return
        
        # MTD and YTD
        mtd = float(returns.last('M').sum() * 100) if len(returns) > 20 else 0
        ytd = float(returns.last('Y').sum() * 100) if len(returns) > 252 else total_return
        
        # Risk metrics
        volatility = float(qs.stats.volatility(returns) * 100)
        sharpe = float(qs.stats.sharpe(returns, rf=self.risk_free_rate))
        sortino = float(qs.stats.sortino(returns, rf=self.risk_free_rate))
        calmar = float(qs.stats.calmar(returns))
        
        # Drawdown
        max_dd = float(qs.stats.max_drawdown(returns) * 100)
        avg_dd = float(qs.stats.avg_drawdown(returns) * 100) if hasattr(qs.stats, 'avg_drawdown') else max_dd / 2
        
        # Calculate max drawdown duration
        equity = (1 + returns).cumprod()
        running_max = equity.cummax()
        drawdown = (equity - running_max) / running_max
        
        max_dd_duration = 0
        current_dd_start = None
        for i, dd in enumerate(drawdown):
            if dd < 0:
                if current_dd_start is None:
                    current_dd_start = i
            else:
                if current_dd_start is not None:
                    duration = i - current_dd_start
                    max_dd_duration = max(max_dd_duration, duration)
                    current_dd_start = None
        
        # Win/Loss
        win_rate = float(len(returns[returns > 0]) / len(returns) * 100)
        best_day = float(returns.max() * 100)
        worst_day = float(returns.min() * 100)
        
        # Monthly returns
        monthly = returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
        best_month = float(monthly.max() * 100) if len(monthly) > 0 else 0
        worst_month = float(monthly.min() * 100) if len(monthly) > 0 else 0
        
        # Ratios
        wins = returns[returns > 0]
        losses = returns[returns < 0]
        
        if len(losses) > 0 and losses.sum() != 0:
            profit_factor = abs(wins.sum() / losses.sum())
        else:
            profit_factor = float('inf') if len(wins) > 0 else 0
        
        if len(wins) > 0 and len(losses) > 0:
            payoff_ratio = abs(wins.mean() / losses.mean())
        else:
            payoff_ratio = 0
        
        # VaR and CVaR
        var_95 = float(np.percentile(returns, 5) * 100)
        cvar_95 = float(returns[returns <= np.percentile(returns, 5)].mean() * 100)
        
        return PerformanceMetrics(
            total_return=round(total_return, 2),
            cagr=round(cagr, 2),
            mtd=round(mtd, 2),
            ytd=round(ytd, 2),
            volatility=round(volatility, 2),
            sharpe=round(sharpe, 2),
            sortino=round(sortino, 2),
            calmar=round(calmar, 2),
            max_drawdown=round(max_dd, 2),
            avg_drawdown=round(avg_dd, 2),
            max_drawdown_duration=max_dd_duration,
            win_rate=round(win_rate, 2),
            best_day=round(best_day, 2),
            worst_day=round(worst_day, 2),
            best_month=round(best_month, 2),
            worst_month=round(worst_month, 2),
            profit_factor=round(profit_factor, 2) if profit_factor != float('inf') else 999,
            payoff_ratio=round(payoff_ratio, 2),
            var_95=round(var_95, 2),
            cvar_95=round(cvar_95, 2)
        )
    
    def _manual_metrics(self, returns: pd.Series) -> PerformanceMetrics:
        """Calculate metrics manually (fallback)"""
        
        # Basic returns
        total_return = ((1 + returns).prod() - 1) * 100
        
        days = len(returns)
        years = days / 252
        cagr = ((1 + total_return/100) ** (1/years) - 1) * 100 if years > 0 else total_return
        
        # Risk
        volatility = returns.std() * np.sqrt(252) * 100
        excess_return = (cagr / 100) - self.risk_free_rate
        sharpe = excess_return / (volatility / 100) if volatility > 0 else 0
        
        # Downside deviation
        negative_returns = returns[returns < 0]
        downside_std = negative_returns.std() * np.sqrt(252) if len(negative_returns) > 0 else 0.001
        sortino = excess_return / downside_std if downside_std > 0 else 0
        
        # Drawdown
        equity = (1 + returns).cumprod()
        running_max = equity.cummax()
        drawdown = (equity - running_max) / running_max
        max_dd = drawdown.min() * 100
        
        calmar = cagr / abs(max_dd) if max_dd != 0 else 0
        
        # Win rate
        win_rate = len(returns[returns > 0]) / len(returns) * 100
        
        return PerformanceMetrics(
            total_return=round(total_return, 2),
            cagr=round(cagr, 2),
            mtd=0,
            ytd=round(total_return, 2),
            volatility=round(volatility, 2),
            sharpe=round(sharpe, 2),
            sortino=round(sortino, 2),
            calmar=round(calmar, 2),
            max_drawdown=round(max_dd, 2),
            avg_drawdown=round(max_dd / 2, 2),
            max_drawdown_duration=0,
            win_rate=round(win_rate, 2),
            best_day=round(returns.max() * 100, 2),
            worst_day=round(returns.min() * 100, 2),
            best_month=0,
            worst_month=0,
            profit_factor=0,
            payoff_ratio=0,
            var_95=round(np.percentile(returns, 5) * 100, 2),
            cvar_95=round(returns[returns <= np.percentile(returns, 5)].mean() * 100, 2)
        )
    
    def _empty_metrics(self) -> PerformanceMetrics:
        """Return empty metrics"""
        return PerformanceMetrics(
            total_return=0, cagr=0, mtd=0, ytd=0,
            volatility=0, sharpe=0, sortino=0, calmar=0,
            max_drawdown=0, avg_drawdown=0, max_drawdown_duration=0,
            win_rate=0, best_day=0, worst_day=0, best_month=0, worst_month=0,
            profit_factor=0, payoff_ratio=0, var_95=0, cvar_95=0
        )
    
    def generate_tearsheet_data(
        self,
        price_data: Dict[str, pd.DataFrame],
        signals: List[Dict],
        benchmark_ticker: str = "SPY"
    ) -> TearsheetData:
        """Generate all data needed for tearsheet visualization"""
        
        returns = self.calculate_returns(price_data, signals)
        
        if returns.empty:
            return TearsheetData(
                metrics=self._empty_metrics(),
                equity_curve=[],
                drawdown_series=[],
                monthly_returns=[],
                yearly_returns=[],
                rolling_sharpe=[],
                rolling_volatility=[],
                return_distribution=[]
            )
        
        metrics = self.generate_metrics(returns)
        
        # Equity curve
        equity = (1 + returns).cumprod() * 100000  # Start with $100k
        equity_curve = [
            {"date": str(date.date()), "value": round(float(val), 2)}
            for date, val in zip(equity.index, equity.values)
        ]
        
        # Drawdown series
        running_max = equity.cummax()
        drawdown = (equity - running_max) / running_max * 100
        drawdown_series = [
            {"date": str(date.date()), "drawdown": round(float(dd), 2)}
            for date, dd in zip(drawdown.index, drawdown.values)
        ]
        
        # Monthly returns
        monthly = returns.resample('M').apply(lambda x: (1 + x).prod() - 1) * 100
        monthly_returns = [
            {"month": str(date.date()), "return": round(float(ret), 2)}
            for date, ret in zip(monthly.index, monthly.values)
        ]
        
        # Yearly returns
        yearly = returns.resample('Y').apply(lambda x: (1 + x).prod() - 1) * 100
        yearly_returns = [
            {"year": str(date.year), "return": round(float(ret), 2)}
            for date, ret in zip(yearly.index, yearly.values)
        ]
        
        # Rolling Sharpe (63-day = ~3 months)
        rolling_sharpe_series = returns.rolling(63).apply(
            lambda x: (x.mean() * 252 - self.risk_free_rate) / (x.std() * np.sqrt(252)) if x.std() > 0 else 0
        )
        rolling_sharpe = [
            {"date": str(date.date()), "sharpe": round(float(val), 2)}
            for date, val in zip(rolling_sharpe_series.index, rolling_sharpe_series.values)
            if not np.isnan(val)
        ]
        
        # Rolling Volatility (21-day = ~1 month)
        rolling_vol_series = returns.rolling(21).std() * np.sqrt(252) * 100
        rolling_volatility = [
            {"date": str(date.date()), "volatility": round(float(val), 2)}
            for date, val in zip(rolling_vol_series.index, rolling_vol_series.values)
            if not np.isnan(val)
        ]
        
        # Return distribution
        hist, bins = np.histogram(returns * 100, bins=50)
        return_distribution = [
            {"bin": round(float(bins[i]), 2), "count": int(hist[i])}
            for i in range(len(hist))
        ]
        
        return TearsheetData(
            metrics=metrics,
            equity_curve=equity_curve[::max(1, len(equity_curve)//200)],  # Limit points
            drawdown_series=drawdown_series[::max(1, len(drawdown_series)//200)],
            monthly_returns=monthly_returns,
            yearly_returns=yearly_returns,
            rolling_sharpe=rolling_sharpe[::max(1, len(rolling_sharpe)//100)],
            rolling_volatility=rolling_volatility[::max(1, len(rolling_volatility)//100)],
            return_distribution=return_distribution
        )
    
    def generate_html_report(
        self,
        price_data: Dict[str, pd.DataFrame],
        signals: List[Dict],
        strategy_name: str = "Strategy"
    ) -> str:
        """Generate HTML tearsheet report"""
        
        if not QUANTSTATS_AVAILABLE:
            return "<html><body><h1>QuantStats not installed</h1></body></html>"
        
        returns = self.calculate_returns(price_data, signals)
        
        if returns.empty:
            return "<html><body><h1>No data available</h1></body></html>"
        
        try:
            # Generate HTML report
            html_buffer = io.StringIO()
            qs.reports.html(returns, output=html_buffer, title=strategy_name)
            return html_buffer.getvalue()
        except Exception as e:
            logger.error(f"HTML report generation error: {e}")
            return f"<html><body><h1>Error generating report: {e}</h1></body></html>"
    
    def generate_charts(
        self,
        tearsheet_data: TearsheetData,
        strategy_name: str = "Strategy"
    ) -> Dict[str, str]:
        """Generate Plotly charts as JSON"""
        
        if not PLOTLY_AVAILABLE:
            return {}
        
        charts = {}
        
        try:
            # Equity Curve
            if tearsheet_data.equity_curve:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=[d['date'] for d in tearsheet_data.equity_curve],
                    y=[d['value'] for d in tearsheet_data.equity_curve],
                    mode='lines',
                    name='Portfolio Value',
                    line=dict(color='#2196F3', width=2)
                ))
                fig.update_layout(
                    title=f'{strategy_name} - Equity Curve',
                    xaxis_title='Date',
                    yaxis_title='Portfolio Value ($)',
                    template='plotly_white'
                )
                charts['equity_curve'] = fig.to_json()
            
            # Drawdown
            if tearsheet_data.drawdown_series:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=[d['date'] for d in tearsheet_data.drawdown_series],
                    y=[d['drawdown'] for d in tearsheet_data.drawdown_series],
                    mode='lines',
                    fill='tozeroy',
                    name='Drawdown',
                    line=dict(color='#f44336', width=1)
                ))
                fig.update_layout(
                    title='Underwater (Drawdown)',
                    xaxis_title='Date',
                    yaxis_title='Drawdown (%)',
                    template='plotly_white'
                )
                charts['drawdown'] = fig.to_json()
            
            # Monthly Returns Heatmap
            if tearsheet_data.monthly_returns:
                # Create heatmap data
                monthly_data = pd.DataFrame(tearsheet_data.monthly_returns)
                if not monthly_data.empty:
                    monthly_data['month'] = pd.to_datetime(monthly_data['month'])
                    monthly_data['year'] = monthly_data['month'].dt.year
                    monthly_data['month_num'] = monthly_data['month'].dt.month
                    
                    pivot = monthly_data.pivot(index='year', columns='month_num', values='return')
                    
                    fig = go.Figure(data=go.Heatmap(
                        z=pivot.values,
                        x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][:pivot.shape[1]],
                        y=pivot.index.tolist(),
                        colorscale='RdYlGn',
                        zmid=0
                    ))
                    fig.update_layout(
                        title='Monthly Returns (%)',
                        template='plotly_white'
                    )
                    charts['monthly_heatmap'] = fig.to_json()
            
            # Return Distribution
            if tearsheet_data.return_distribution:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=[d['bin'] for d in tearsheet_data.return_distribution],
                    y=[d['count'] for d in tearsheet_data.return_distribution],
                    marker_color='#2196F3'
                ))
                fig.update_layout(
                    title='Return Distribution',
                    xaxis_title='Daily Return (%)',
                    yaxis_title='Frequency',
                    template='plotly_white'
                )
                charts['return_distribution'] = fig.to_json()
            
            # Rolling Sharpe
            if tearsheet_data.rolling_sharpe:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=[d['date'] for d in tearsheet_data.rolling_sharpe],
                    y=[d['sharpe'] for d in tearsheet_data.rolling_sharpe],
                    mode='lines',
                    name='Rolling Sharpe',
                    line=dict(color='#4CAF50', width=2)
                ))
                fig.add_hline(y=0, line_dash="dash", line_color="gray")
                fig.update_layout(
                    title='Rolling Sharpe Ratio (63-day)',
                    xaxis_title='Date',
                    yaxis_title='Sharpe Ratio',
                    template='plotly_white'
                )
                charts['rolling_sharpe'] = fig.to_json()
            
        except Exception as e:
            logger.error(f"Chart generation error: {e}")
        
        return charts


# Singleton instance
_reporter = None

def get_reporter() -> QuantStatsReporter:
    global _reporter
    if _reporter is None:
        _reporter = QuantStatsReporter()
    return _reporter
