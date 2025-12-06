"""
Dual EMA Model
Price above both EMA15 and EMA50 indicates strong uptrend
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.models.base import TechnicalModel, SignalType
from app.data.fetcher import get_fetcher


class DualEMAModel(TechnicalModel):
    """
    Dual EMA Trend Filter
    
    Simple but effective trend confirmation:
    - Price above both EMA15 and EMA50 = Strong uptrend
    - EMA15 above EMA50 = Bullish structure
    - Price below both EMAs = Downtrend
    
    Additional confirmations:
    - EMAs expanding (getting further apart) = Strengthening trend
    - EMAs contracting = Potential trend change
    """
    
    def __init__(
        self,
        fast_ema: int = 15,
        slow_ema: int = 50,
        require_both: bool = True
    ):
        super().__init__(
            name="Dual EMA Filter",
            description="Price above EMA15 and EMA50 confirms strong uptrend",
            parameters={
                "fast_ema": fast_ema,
                "slow_ema": slow_ema,
                "require_both": require_both
            }
        )
        self.fast = fast_ema
        self.slow = slow_ema
        self.require_both = require_both
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        results = []
        
        for ticker, df in price_data.items():
            if df is None or len(df) < self.slow + 10:
                continue
            
            try:
                close = df['close']
                
                # Calculate EMAs
                ema_fast = close.ewm(span=self.fast, adjust=False).mean()
                ema_slow = close.ewm(span=self.slow, adjust=False).mean()
                
                current_close = close.iloc[-1]
                current_ema_fast = ema_fast.iloc[-1]
                current_ema_slow = ema_slow.iloc[-1]
                
                # Check conditions
                above_fast = current_close > current_ema_fast
                above_slow = current_close > current_ema_slow
                fast_above_slow = current_ema_fast > current_ema_slow
                
                # EMA spread (trend strength)
                spread = (current_ema_fast / current_ema_slow - 1) * 100
                spread_5d_ago = (ema_fast.iloc[-6] / ema_slow.iloc[-6] - 1) * 100
                spread_expanding = spread > spread_5d_ago
                
                # Distance from EMAs
                dist_from_fast = (current_close / current_ema_fast - 1) * 100
                dist_from_slow = (current_close / current_ema_slow - 1) * 100
                
                # EMA slopes
                fast_slope = (ema_fast.iloc[-1] / ema_fast.iloc[-5] - 1) * 100
                slow_slope = (ema_slow.iloc[-1] / ema_slow.iloc[-5] - 1) * 100
                
                # Determine signal and score
                if above_fast and above_slow and fast_above_slow:
                    signal_type = "BUY"
                    score = 70
                    score += min(15, spread * 5)  # Bonus for wider spread
                    score += 10 if spread_expanding else 0  # Bonus for expanding
                    score += 5 if fast_slope > 0 and slow_slope > 0 else 0  # Both rising
                    
                elif not above_fast and not above_slow and not fast_above_slow:
                    signal_type = "SELL"
                    score = 70
                    score += min(15, abs(spread) * 5)
                    
                elif above_slow and not above_fast:
                    # Pullback in uptrend
                    signal_type = "HOLD"
                    score = 55 if fast_above_slow else 45
                    
                elif above_fast and not above_slow:
                    # Potential trend change
                    signal_type = "HOLD"
                    score = 50
                    
                else:
                    signal_type = "HOLD"
                    score = 50
                
                score = min(100, max(0, score))
                
                results.append({
                    "ticker": ticker,
                    "score": score,
                    "signal_type": signal_type,
                    "price": round(current_close, 2),
                    "ema_fast": round(current_ema_fast, 2),
                    "ema_slow": round(current_ema_slow, 2),
                    "above_both": above_fast and above_slow,
                    "ema_structure": "Bullish" if fast_above_slow else "Bearish",
                    "spread_pct": round(spread, 2),
                    "spread_expanding": spread_expanding,
                    "dist_from_ema15": round(dist_from_fast, 2),
                    "dist_from_ema50": round(dist_from_slow, 2)
                })
                
            except Exception as e:
                continue
        
        return pd.DataFrame(results)
