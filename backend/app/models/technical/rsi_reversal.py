"""
RSI Reversal Model
Buy oversold stocks, sell overbought stocks
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import TechnicalModel, SignalType
from app.data.fetcher import get_fetcher


class RSIReversalModel(TechnicalModel):
    """
    RSI Reversal Strategy
    - Buy when RSI < 30 (oversold)
    - Sell when RSI > 70 (overbought)
    """
    
    def __init__(
        self,
        rsi_period: int = 14,
        oversold: int = 30,
        overbought: int = 70
    ):
        super().__init__(
            name="RSI Reversal",
            description="Buy oversold stocks (RSI<30), sell overbought (RSI>70)",
            parameters={
                "rsi_period": rsi_period,
                "oversold": oversold,
                "overbought": overbought
            }
        )
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        fetcher = get_fetcher()
        results = []
        
        for ticker, df in price_data.items():
            if df is None or len(df) < self.rsi_period + 5:
                continue
            
            try:
                df = fetcher.calculate_technicals(df)
                rsi = df['rsi'].iloc[-1]
                
                if pd.isna(rsi):
                    continue
                
                # Determine signal
                if rsi < self.oversold:
                    signal_type = "BUY"
                    # Lower RSI = stronger buy signal
                    score = 100 - (rsi / self.oversold * 50)
                elif rsi > self.overbought:
                    signal_type = "SELL"
                    # Higher RSI = stronger sell signal
                    score = 50 + ((rsi - self.overbought) / (100 - self.overbought) * 50)
                else:
                    signal_type = "HOLD"
                    score = 50
                
                results.append({
                    "ticker": ticker,
                    "score": score,
                    "signal_type": signal_type,
                    "rsi": round(rsi, 2),
                    "rsi_prev": round(df['rsi'].iloc[-2], 2) if len(df) > 1 else rsi
                })
                
            except Exception as e:
                continue
        
        return pd.DataFrame(results)
