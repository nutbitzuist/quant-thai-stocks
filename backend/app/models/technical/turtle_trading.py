"""
Turtle Trading Model
Richard Dennis's famous trend-following system
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import TechnicalModel, SignalType
from app.data.fetcher import get_fetcher


class TurtleTradingModel(TechnicalModel):
    """
    Turtle Trading System
    
    Entry Rules:
    - System 1 (short-term): Buy on 20-day high, sell on 10-day low
    - System 2 (long-term): Buy on 55-day high, sell on 20-day low
    
    Position Sizing:
    - Based on ATR (Average True Range)
    - 1 Unit = 1% account risk / (N * Dollar per point)
    
    This implementation uses System 2 (55/20) which is more reliable
    """
    
    def __init__(
        self,
        entry_period: int = 55,
        exit_period: int = 20,
        atr_period: int = 20,
        use_filter: bool = True  # Skip signal if last trade was winner
    ):
        super().__init__(
            name="Turtle Trading",
            description="Buy on 55-day breakout, sell on 20-day breakdown (Turtle Trading System 2)",
            parameters={
                "entry_period": entry_period,
                "exit_period": exit_period,
                "atr_period": atr_period,
                "use_filter": use_filter
            }
        )
        self.entry_period = entry_period
        self.exit_period = exit_period
        self.atr_period = atr_period
        self.use_filter = use_filter
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        fetcher = get_fetcher()
        results = []
        
        for ticker, df in price_data.items():
            if df is None or len(df) < self.entry_period + 10:
                continue
            
            try:
                df = fetcher.calculate_technicals(df)
                
                close = df['close'].iloc[-1]
                high = df['high'].iloc[-1]
                low = df['low'].iloc[-1]
                
                # Calculate channels
                entry_high = df['high'].rolling(self.entry_period).max().iloc[-2]  # Previous day
                exit_low = df['low'].rolling(self.exit_period).min().iloc[-2]  # Previous day
                
                # ATR for volatility assessment
                atr = df['atr'].iloc[-1]
                atr_pct = (atr / close) * 100 if close > 0 else 0
                
                # Calculate N (ATR in dollars)
                n_value = atr
                
                # Determine trend strength
                # Higher high breakout = uptrend, lower low breakdown = downtrend
                days_since_entry_high = 0
                days_since_exit_low = 0
                
                for i in range(1, min(self.entry_period, len(df))):
                    if df['high'].iloc[-i-1] >= entry_high:
                        days_since_entry_high = i
                        break
                
                for i in range(1, min(self.exit_period, len(df))):
                    if df['low'].iloc[-i-1] <= exit_low:
                        days_since_exit_low = i
                        break
                
                # Entry signal: today's high exceeds previous entry_period high
                is_entry_signal = high > entry_high
                
                # Exit signal: today's low breaks previous exit_period low  
                is_exit_signal = low < exit_low
                
                # Calculate how much price exceeded the channel
                entry_strength = ((close - entry_high) / entry_high * 100) if is_entry_signal else 0
                exit_strength = ((exit_low - close) / exit_low * 100) if is_exit_signal else 0
                
                if is_entry_signal:
                    signal_type = "BUY"
                    # Score based on breakout strength and volatility
                    score = 60 + min(20, entry_strength * 5) + min(20, (1 / atr_pct) * 5)
                elif is_exit_signal:
                    signal_type = "SELL"
                    score = 60 + min(20, abs(exit_strength) * 5)
                else:
                    signal_type = "HOLD"
                    # Neutral score, slight bias based on position in channel
                    channel_position = (close - exit_low) / (entry_high - exit_low) if entry_high > exit_low else 0.5
                    score = 30 + channel_position * 40
                
                score = min(100, max(0, score))
                
                results.append({
                    "ticker": ticker,
                    "score": score,
                    "signal_type": signal_type,
                    "entry_high": round(entry_high, 2),
                    "exit_low": round(exit_low, 2),
                    "atr": round(atr, 2),
                    "atr_pct": round(atr_pct, 2),
                    "is_breakout": is_entry_signal,
                    "is_breakdown": is_exit_signal,
                    "entry_strength_pct": round(entry_strength, 2),
                    "n_value": round(n_value, 2)
                })
                
            except Exception as e:
                continue
        
        return pd.DataFrame(results)
