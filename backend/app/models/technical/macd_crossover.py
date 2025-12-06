"""
MACD Crossover Model
Buy on bullish crossovers, sell on bearish crossovers
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import TechnicalModel, SignalType
from app.data.fetcher import get_fetcher


class MACDCrossoverModel(TechnicalModel):
    """
    MACD Crossover Strategy
    - Buy when MACD crosses above signal line
    - Sell when MACD crosses below signal line
    """
    
    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        lookback_days: int = 5
    ):
        super().__init__(
            name="MACD Crossover",
            description="Buy on bullish MACD crossovers, sell on bearish",
            parameters={
                "fast_period": fast_period,
                "slow_period": slow_period,
                "signal_period": signal_period,
                "lookback_days": lookback_days
            }
        )
        self.lookback_days = lookback_days
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        fetcher = get_fetcher()
        results = []
        
        for ticker, df in price_data.items():
            if df is None or len(df) < 35:
                continue
            
            try:
                df = fetcher.calculate_technicals(df)
                
                macd = df['macd'].iloc[-self.lookback_days:]
                signal = df['macd_signal'].iloc[-self.lookback_days:]
                hist = df['macd_hist'].iloc[-self.lookback_days:]
                
                if macd.isna().any():
                    continue
                
                # Check for crossover in lookback period
                cross_above = False
                cross_below = False
                cross_day = 0
                
                for i in range(1, len(macd)):
                    if macd.iloc[i-1] <= signal.iloc[i-1] and macd.iloc[i] > signal.iloc[i]:
                        cross_above = True
                        cross_day = i
                    elif macd.iloc[i-1] >= signal.iloc[i-1] and macd.iloc[i] < signal.iloc[i]:
                        cross_below = True
                        cross_day = i
                
                current_hist = hist.iloc[-1]
                
                if cross_above:
                    signal_type = "BUY"
                    # Score based on histogram strength and recency
                    score = 60 + abs(current_hist) * 10 + (self.lookback_days - cross_day) * 5
                elif cross_below:
                    signal_type = "SELL"
                    score = 60 + abs(current_hist) * 10 + (self.lookback_days - cross_day) * 5
                else:
                    signal_type = "HOLD"
                    score = 50
                
                score = min(100, max(0, score))
                
                results.append({
                    "ticker": ticker,
                    "score": score,
                    "signal_type": signal_type,
                    "macd": round(macd.iloc[-1], 4),
                    "macd_signal": round(signal.iloc[-1], 4),
                    "histogram": round(current_hist, 4)
                })
                
            except Exception as e:
                continue
        
        return pd.DataFrame(results)
