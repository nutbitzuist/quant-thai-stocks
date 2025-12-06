"""
Mean Reversion (Z-Score) Model
Statistical arbitrage based on price deviation from mean
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import QuantitativeModel, SignalType
from app.data.fetcher import get_fetcher


class MeanReversionModel(QuantitativeModel):
    """
    Mean Reversion Strategy using Z-Score
    
    Identifies stocks that have deviated significantly from their mean price.
    - Buy when Z-Score < -2 (oversold, price below 2 std devs)
    - Sell when Z-Score > 2 (overbought, price above 2 std devs)
    
    Based on the statistical concept that prices tend to revert to their mean.
    """
    
    def __init__(
        self,
        lookback_period: int = 20,
        z_buy_threshold: float = -2.0,
        z_sell_threshold: float = 2.0,
        min_data_points: int = 50
    ):
        super().__init__(
            name="Mean Reversion Z-Score",
            description="Statistical arbitrage - buy oversold (Z<-2), sell overbought (Z>2)",
            parameters={
                "lookback_period": lookback_period,
                "z_buy_threshold": z_buy_threshold,
                "z_sell_threshold": z_sell_threshold,
                "min_data_points": min_data_points
            }
        )
        self.lookback_period = lookback_period
        self.z_buy_threshold = z_buy_threshold
        self.z_sell_threshold = z_sell_threshold
        self.min_data_points = min_data_points
    
    def calculate_z_score(self, prices: pd.Series) -> pd.Series:
        """Calculate rolling Z-Score for price series"""
        rolling_mean = prices.rolling(window=self.lookback_period).mean()
        rolling_std = prices.rolling(window=self.lookback_period).std()
        z_score = (prices - rolling_mean) / rolling_std.replace(0, np.nan)
        return z_score
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        results = []
        
        for ticker, df in price_data.items():
            if df is None or len(df) < self.min_data_points:
                continue
            
            try:
                close = df['close']
                
                # Calculate Z-Score
                z_score = self.calculate_z_score(close)
                current_z = z_score.iloc[-1]
                
                if pd.isna(current_z):
                    continue
                
                # Calculate additional metrics
                rolling_mean = close.rolling(window=self.lookback_period).mean().iloc[-1]
                rolling_std = close.rolling(window=self.lookback_period).std().iloc[-1]
                current_price = close.iloc[-1]
                
                # Distance from mean in percentage
                pct_from_mean = ((current_price - rolling_mean) / rolling_mean) * 100
                
                # Half-life estimation (how fast does it revert)
                z_series = z_score.dropna()
                if len(z_series) > 10:
                    # Simple autocorrelation-based half-life estimate
                    lag_1_corr = z_series.autocorr(lag=1)
                    if lag_1_corr > 0 and lag_1_corr < 1:
                        half_life = -np.log(2) / np.log(lag_1_corr)
                    else:
                        half_life = np.nan
                else:
                    half_life = np.nan
                
                # Determine signal
                if current_z <= self.z_buy_threshold:
                    signal_type = "BUY"
                    # More negative Z = stronger buy signal
                    score = min(100, 50 + abs(current_z) * 20)
                elif current_z >= self.z_sell_threshold:
                    signal_type = "SELL"
                    # More positive Z = stronger sell signal
                    score = min(100, 50 + abs(current_z) * 20)
                else:
                    signal_type = "HOLD"
                    # Score based on how close to threshold
                    score = 50 - abs(current_z) * 10
                
                score = max(0, min(100, score))
                
                results.append({
                    "ticker": ticker,
                    "score": score,
                    "signal_type": signal_type,
                    "z_score": round(current_z, 3),
                    "current_price": round(current_price, 2),
                    "rolling_mean": round(rolling_mean, 2),
                    "rolling_std": round(rolling_std, 2),
                    "pct_from_mean": round(pct_from_mean, 2),
                    "half_life_days": round(half_life, 1) if not pd.isna(half_life) else None
                })
                
            except Exception as e:
                continue
        
        return pd.DataFrame(results)
