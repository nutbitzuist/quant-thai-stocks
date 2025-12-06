"""
Pairs Trading Setup Model
Correlation-based statistical arbitrage
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Tuple
from app.models.base import QuantitativeModel, SignalType
from app.data.fetcher import get_fetcher


class PairsTradingModel(QuantitativeModel):
    """
    Pairs Trading Strategy
    
    Identifies stocks that are highly correlated but have diverged.
    When the spread between correlated pairs deviates significantly,
    buy the underperformer and sell the outperformer.
    
    This model identifies individual stocks that have diverged from
    their sector/market correlation and are likely to revert.
    """
    
    def __init__(
        self,
        correlation_period: int = 60,
        min_correlation: float = 0.7,
        spread_z_threshold: float = 2.0,
        lookback_period: int = 20,
        min_data_points: int = 100
    ):
        super().__init__(
            name="Pairs Trading Setup",
            description="Correlation-based arbitrage - trade divergent correlated pairs",
            parameters={
                "correlation_period": correlation_period,
                "min_correlation": min_correlation,
                "spread_z_threshold": spread_z_threshold,
                "lookback_period": lookback_period,
                "min_data_points": min_data_points
            }
        )
        self.correlation_period = correlation_period
        self.min_correlation = min_correlation
        self.spread_z_threshold = spread_z_threshold
        self.lookback_period = lookback_period
        self.min_data_points = min_data_points
    
    def calculate_returns(self, price_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Calculate aligned returns for all stocks"""
        returns_dict = {}
        
        for ticker, df in price_data.items():
            if df is not None and len(df) >= self.min_data_points:
                # Use log returns for better statistical properties
                returns = np.log(df['close'] / df['close'].shift(1))
                returns_dict[ticker] = returns
        
        if not returns_dict:
            return pd.DataFrame()
        
        # Align all returns to same dates
        returns_df = pd.DataFrame(returns_dict)
        returns_df = returns_df.dropna(how='all')
        
        return returns_df
    
    def find_best_pair(
        self, 
        ticker: str, 
        returns_df: pd.DataFrame,
        correlation_matrix: pd.DataFrame
    ) -> Tuple[Optional[str], float]:
        """Find the best correlated pair for a given ticker"""
        if ticker not in correlation_matrix.columns:
            return None, 0.0
        
        correlations = correlation_matrix[ticker].drop(ticker)
        
        # Filter by minimum correlation
        valid_pairs = correlations[correlations >= self.min_correlation]
        
        if valid_pairs.empty:
            return None, 0.0
        
        best_pair = valid_pairs.idxmax()
        best_corr = valid_pairs.max()
        
        return best_pair, best_corr
    
    def calculate_spread_z_score(
        self,
        returns_df: pd.DataFrame,
        ticker1: str,
        ticker2: str
    ) -> Tuple[float, float]:
        """Calculate Z-score of the spread between two stocks"""
        if ticker1 not in returns_df.columns or ticker2 not in returns_df.columns:
            return np.nan, np.nan
        
        # Calculate cumulative returns (price ratio proxy)
        cum_ret1 = returns_df[ticker1].cumsum()
        cum_ret2 = returns_df[ticker2].cumsum()
        
        # Calculate spread
        spread = cum_ret1 - cum_ret2
        
        # Calculate Z-score of spread
        rolling_mean = spread.rolling(window=self.lookback_period).mean()
        rolling_std = spread.rolling(window=self.lookback_period).std()
        
        z_score = (spread - rolling_mean) / rolling_std.replace(0, np.nan)
        
        current_z = z_score.iloc[-1] if not z_score.empty else np.nan
        current_spread = spread.iloc[-1] if not spread.empty else np.nan
        
        return current_z, current_spread
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        results = []
        
        # Calculate returns for all stocks
        returns_df = self.calculate_returns(price_data)
        
        if returns_df.empty or len(returns_df.columns) < 2:
            return pd.DataFrame()
        
        # Calculate correlation matrix
        correlation_matrix = returns_df.tail(self.correlation_period).corr()
        
        for ticker in returns_df.columns:
            try:
                df = price_data.get(ticker)
                if df is None or len(df) < self.min_data_points:
                    continue
                
                # Find best correlated pair
                best_pair, correlation = self.find_best_pair(
                    ticker, returns_df, correlation_matrix
                )
                
                if best_pair is None:
                    continue
                
                # Calculate spread Z-score
                spread_z, spread_value = self.calculate_spread_z_score(
                    returns_df, ticker, best_pair
                )
                
                if pd.isna(spread_z):
                    continue
                
                # Calculate relative performance
                ticker_ret_20d = returns_df[ticker].tail(20).sum() * 100
                pair_ret_20d = returns_df[best_pair].tail(20).sum() * 100
                relative_perf = ticker_ret_20d - pair_ret_20d
                
                # Determine signal
                # If spread Z > threshold: ticker outperformed, expect reversion (SELL ticker)
                # If spread Z < -threshold: ticker underperformed, expect reversion (BUY ticker)
                if spread_z <= -self.spread_z_threshold:
                    signal_type = "BUY"
                    # More negative = stronger buy signal
                    score = min(100, 50 + abs(spread_z) * 15)
                elif spread_z >= self.spread_z_threshold:
                    signal_type = "SELL"
                    # More positive = stronger sell signal
                    score = min(100, 50 + abs(spread_z) * 15)
                else:
                    signal_type = "HOLD"
                    score = 50 - abs(spread_z) * 10
                
                # Boost score for higher correlation (more reliable pair)
                score = score * (0.8 + 0.2 * correlation)
                score = max(0, min(100, score))
                
                results.append({
                    "ticker": ticker,
                    "score": score,
                    "signal_type": signal_type,
                    "pair_ticker": best_pair,
                    "correlation": round(correlation, 3),
                    "spread_z_score": round(spread_z, 3),
                    "spread_value": round(spread_value, 4),
                    "ticker_return_20d": round(ticker_ret_20d, 2),
                    "pair_return_20d": round(pair_ret_20d, 2),
                    "relative_performance": round(relative_perf, 2)
                })
                
            except Exception as e:
                continue
        
        return pd.DataFrame(results)
