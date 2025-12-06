"""
Nicolas Darvas Box Model
Buy breakouts from consolidation boxes
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Tuple
from app.models.base import TechnicalModel, SignalType
from app.data.fetcher import get_fetcher


class DarvasBoxModel(TechnicalModel):
    """
    Nicolas Darvas Box Theory
    
    1. Stock makes a new 52-week high
    2. Then consolidates in a "box" (trading range)
    3. Buy when price breaks above the box on high volume
    4. Stop loss at bottom of box
    
    The box is defined by:
    - Top: Recent high that hasn't been exceeded in 3+ days
    - Bottom: Lowest low since the top was established
    """
    
    def __init__(
        self,
        box_days: int = 20,
        volume_multiplier: float = 1.5,
        require_52w_high: bool = True
    ):
        super().__init__(
            name="Darvas Box",
            description="Buy breakouts from Darvas consolidation boxes",
            parameters={
                "box_days": box_days,
                "volume_multiplier": volume_multiplier,
                "require_52w_high": require_52w_high
            }
        )
        self.box_days = box_days
        self.volume_multiplier = volume_multiplier
        self.require_52w_high = require_52w_high
    
    def _find_darvas_box(self, df: pd.DataFrame) -> Optional[Tuple[float, float, int]]:
        """
        Find the current Darvas box
        Returns: (box_top, box_bottom, days_in_box) or None
        """
        if len(df) < self.box_days + 5:
            return None
        
        recent = df.iloc[-self.box_days:]
        
        # Find potential box top (high that wasn't exceeded for 3+ days)
        box_top = None
        box_top_idx = None
        
        for i in range(len(recent) - 4, -1, -1):
            high = recent['high'].iloc[i]
            # Check if this high wasn't exceeded in next 3 days
            subsequent_highs = recent['high'].iloc[i+1:i+4] if i+4 <= len(recent) else recent['high'].iloc[i+1:]
            
            if len(subsequent_highs) >= 3 and all(subsequent_highs < high):
                box_top = high
                box_top_idx = i
                break
        
        if box_top is None:
            return None
        
        # Box bottom is lowest low since box top was established
        box_bottom = recent['low'].iloc[box_top_idx:].min()
        days_in_box = len(recent) - box_top_idx
        
        return (box_top, box_bottom, days_in_box)
    
    def calculate_scores(
        self,
        price_data: Dict[str, pd.DataFrame],
        fundamental_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        fetcher = get_fetcher()
        results = []
        
        for ticker, df in price_data.items():
            if df is None or len(df) < 252:
                continue
            
            try:
                df = fetcher.calculate_technicals(df)
                
                close = df['close'].iloc[-1]
                high = df['high'].iloc[-1]
                volume = df['volume'].iloc[-1]
                avg_volume = df['volume'].rolling(20).mean().iloc[-1]
                
                # Check for 52-week high requirement
                high_52w = df['high'].rolling(252).max().iloc[-1]
                near_52w_high = (close / high_52w) > 0.90  # Within 10% of 52w high
                
                if self.require_52w_high and not near_52w_high:
                    continue
                
                # Find Darvas box
                box_result = self._find_darvas_box(df)
                
                if box_result is None:
                    continue
                
                box_top, box_bottom, days_in_box = box_result
                box_height_pct = (box_top / box_bottom - 1) * 100
                
                # Check for breakout
                is_breakout = close > box_top
                high_volume = volume > avg_volume * self.volume_multiplier
                
                if is_breakout and high_volume:
                    signal_type = "BUY"
                    # Score based on volume strength and box quality
                    volume_score = min(30, (volume / avg_volume - 1) * 20)
                    box_score = min(30, days_in_box * 2)  # Longer consolidation = better
                    breakout_score = min(40, (close / box_top - 1) * 200)  # Breakout strength
                    score = 50 + volume_score + box_score + breakout_score
                elif close < box_bottom:
                    signal_type = "SELL"
                    score = 70
                else:
                    signal_type = "HOLD"
                    score = 50
                
                score = min(100, max(0, score))
                
                results.append({
                    "ticker": ticker,
                    "score": score,
                    "signal_type": signal_type,
                    "box_top": round(box_top, 2),
                    "box_bottom": round(box_bottom, 2),
                    "box_height_pct": round(box_height_pct, 1),
                    "days_in_box": days_in_box,
                    "volume_ratio": round(volume / avg_volume, 2),
                    "is_breakout": is_breakout,
                    "near_52w_high": near_52w_high
                })
                
            except Exception as e:
                continue
        
        return pd.DataFrame(results)
